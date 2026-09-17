# cmux Blaxel create response-loss reconciliation scout

Date: 2026-09-01  
Programme: high-leverage-open-source (#114)  
Assignment: Fieldwork #928  
Worker: `chatgpt:gpt-5.6-sol`  
Upstream contact authorized: `false`

## In simple words

I'm testing one recovery invariant: after a Cloud VM create settles, cmux and the cloud provider should agree about whether a machine exists and which logical create owns it.

At pinned cmux `eaa899cb20bd411019744fbd2bdedeb397f3070b`, the Blaxel path has a narrow response-loss gap. The sandbox create is a non-idempotent `POST`, and cmux deliberately refuses to replay that HTTP request because the provider may already have performed the operation before a network failure becomes visible locally. But the generated Blaxel machine name is held only inside the provider call until a successful `VMHandle` returns. If Blaxel commits sandbox A and the response disappears, the workflow records the database row as a retryable provider-create failure with no `provider_vm_id`.

That leaves no current automatic path that can ask Blaxel whether A exists. A retry with the same cmux idempotency key is intentionally allowed to call the provider again immediately; Blaxel generates a fresh name B and can create a second sandbox. cmux then lists B while A remains outside its registry.

```text
logical create K
    |
    v
Blaxel POST create A ---- remote commit ----X---- success response
    |                                      response lost
    |                                          |
    |                                          v
    |                              cloud_vms: failed, provider_vm_id=NULL
    |                                          |
    |                                  same-key retry allowed
    |                                          v
    +------------------------------------ Blaxel POST create B
                                               |
                                               v
                                  cloud_vms: running, provider_vm_id=B

provider view: A + B
cmux view:     B
```

This report establishes the source-level recovery gap and the consequence-producing retry from current implementation and tests. It does **not** claim a live Blaxel fault-injection execution: the remaining discriminator is to make a provider test simulate “remote create committed, response lost” and retain the execution receipt.

## Exact source state

Repository: `manaflow-ai/cmux`  
Pinned `main`: `eaa899cb20bd411019744fbd2bdedeb397f3070b`  
Commit time: 2026-09-01T17:27:07Z  
Commit: https://github.com/manaflow-ai/cmux/commit/eaa899cb20bd411019744fbd2bdedeb397f3070b

Fieldwork base for this scout: `37ac7063c980568f8128508a79a12dc30a35a311`.

Primary source owners at the pinned revision:

- `web/services/vms/drivers/blaxel.ts`
- `web/services/vms/workflows.ts`
- `web/services/vms/repository.ts`
- `web/services/vms/providerGateway.ts`
- `web/services/vms/reaper.ts`
- `web/tests/vm-blaxel-fetch-retry.test.ts`
- `web/tests/vm-workflows.test.ts`

## Core invariant

After recovery settles, every authoritative representation of the same remote create should agree on:

1. whether a machine exists;
2. which provider identity represents the logical create;
3. whether that create succeeded, failed, or remains indeterminate;
4. whether retrying the logical create may create another machine.

The useful property is stronger than “don't crash.” A failed local response may be legitimate while the remote outcome is unknown. The recovery path must preserve enough identity to resolve that uncertainty before starting a second effect.

## Fact being reconciled

**Fact:** Which remote machine, if any, represents one logical Cloud VM create identified by cmux idempotency key K?

The fact is represented independently in several places.

| Representation | What it can say | Component that trusts it |
| --- | --- | --- |
| Blaxel sandbox control plane | sandbox A exists / is absent / has lifecycle state | Blaxel driver and direct provider status operations |
| Generated Blaxel machine name | identity used in `metadata.name` for the create POST | `BlaxelProvider.create` during one invocation |
| Returned `VMHandle` | provider id plus provider metadata after successful create response | `VmProviderGateway` and `createVm` finalization |
| `cloud_vms.provider_vm_id` | durable provider identity owned by the logical row | list/status/attach/destroy/reconciliation workflows |
| `cloud_vms.status` and failure fields | provisioning/running/failed/destroyed interpretation | create retry policy, UI/API, billing and telemetry |
| idempotency-key row ownership | whether K replays, waits, fails, or is allowed to create again | `VmRepository.beginCreate` |
| user VM list | rows with a provider id | callers and UI |
| provider-status reconciler | non-destroyed rows with non-null provider id | reconciliation cron / lazy status correction |
| VM reaper | old provisioning rows and provider **volume** inventory | observability only; report-only |
| billing reservation and usage events | create credit consumed/refunded and failure/success event | billing/accounting path |

The dangerous asymmetry is that Blaxel can know A while every cmux recovery path that can query a machine requires `provider_vm_id`, which never became durable.

## Current control flow

### 1. cmux creates the logical row first

`createVm` calls `beginCreateWithLazyProviderRefresh`, obtains a provisioning `cloud_vms` row, reserves create credit, and records create-requested events before entering `providers.create(...)`.

This ordering gives cmux a durable logical operation before the remote effect, which is the right starting point.

### 2. Blaxel chooses the provider identity inside the provider call

`BlaxelProvider.create` calls `friendlyVmName()` and stores the result in local variable `name`. A per-machine home-volume name, when used, derives from that generated name.

The sandbox request is then:

```text
POST /sandboxes
metadata.name = name
spec.runtime = image/memory/env/ports
optional volume = resolved from name
```

The cmux idempotency key and the durable `cloud_vms` row id are not carried into this provider identity or request as a provider-side create identity.

### 3. Blaxel POST failures are deliberately not replayed

`blaxelFetch` classifies GET/DELETE/PUT/HEAD as idempotent for its retry policy. POST is excluded. Its source comment explains the reason: a rate-limit or network failure does not prove the provider did no work, and process starts / sandbox creates are non-idempotent.

`web/tests/vm-blaxel-fetch-retry.test.ts` pins the behavior:

- POST 5xx -> one call, error propagated;
- POST 429 -> one call, error propagated;
- POST network failure -> one call, original transport error propagated;
- GET network/5xx -> bounded retry.

That is a good local policy. Replaying the same POST blindly would create exactly the duplicate effect this scout cares about.

### 4. The workflow can compensate only after a `VMHandle` exists

After `providers.create` returns a handle, `createVm` calls `repo.markCreateRunning` with `handle.providerVmId`. If database finalization fails at that point, `rollbackProviderCreate` has the exact provider identity and destroys the machine; it also deletes a machine-owned home volume when appropriate.

That is the important negative control:

```text
provider create A returns VMHandle(A)
    -> database finalization fails
    -> rollbackProviderCreate(A)
    -> provider effect is compensated
```

The response-loss window occurs earlier. If the provider created A but the successful response never reaches the caller, no `VMHandle(A)` exists locally, so the compensation function has no identity to use.

### 5. Provider-create failure is made immediately retryable

When `providers.create` fails, `createVm`:

- refunds the create credit;
- marks the row failed with `PROVIDER_CREATE_UNAVAILABLE_FAILURE_CODE` (`provider_create_unavailable`);
- records `vm.create.failed`.

The source comment says this failure code exists so a client retrying the **same stable idempotency key** reaches the provider again immediately instead of replaying a stored failure for the ordinary failed-create retry window.

`VmRepository.isRetryableFailedCreate` treats this code as immediately retryable. During `beginCreate`, a retryable failed row has its old `idempotency_key` cleared before a new row claims the same key.

`web/tests/vm-workflows.test.ts` pins the intended behavior: a transient provider create failure followed by the same stable key invokes provider create a second time and returns the second provider VM.

## Interruption sequence

Use one logical idempotency key K.

1. `beginCreate` commits provisioning row R1 for K.
2. The driver generates provider name A.
3. cmux sends Blaxel `POST /sandboxes` for A.
4. Blaxel commits sandbox A.
5. Interrupt the response path after remote commit and before the successful response is consumed locally. A realistic discriminator is a response-body/connection failure after the fake provider has recorded the create side effect.
6. `blaxelFetch` returns the network error and performs no POST replay.
7. No `VMHandle(A)` reaches `createVm`.
8. `createVm` marks R1 `failed` with `provider_create_unavailable`; `provider_vm_id` remains null; credit is refunded.

### First divergence

The first durable disagreement is step 8:

```text
Blaxel:   A exists
R1:       failed
R1 pid:   NULL
billing:  create credit refunded
```

Each local component is internally consistent. The wrong answer emerges across the ownership boundary: the remote effect exists, while the durable row says provider create failed without preserving the identity needed to resolve “failed” versus “committed but response lost.”

## Settlement check

A temporary disagreement during an in-flight create is expected. The settlement point here is after the failed `createVm` invocation has returned and its failure bookkeeping has completed.

At 100 ms / 1 s / 10 s after that point, absent additional user action:

- direct Blaxel lookup by A can still say **exists**;
- R1 remains **failed** with no provider id;
- `listUserVms` omits R1 because it filters to rows with `providerVmId`;
- normal provider-status reconciliation cannot query A because `reconciliationCandidates` requires a non-null `provider_vm_id`;
- the VM reaper does not discover orphan sandboxes. Its provider inventory is for volumes, while stuck provisioning reporting starts from database rows; the reaper is explicitly report-only and performs no lifecycle mutation.

### Expected convergence

One of these would satisfy the invariant:

- adopt A into R1 after an exact read-after-ambiguity lookup;
- prove A absent, then allow a retry;
- retain an indeterminate provisioning state with durable provider-create identity until a later reconciler resolves it;
- compensate A once its identity is recovered.

### Actual convergence

No current source path found during this scout performs one of those transitions for a sandbox whose create response was lost before `provider_vm_id` publication.

The ordinary status reconciler cannot help because its key is the missing provider id. The reaper cannot help because it does not inventory/adopt sandboxes and is report-only.

## Consequential second operation

Retry the same logical create using idempotency key K, exactly as the API's retryable provider failure invites the caller to do.

1. `beginCreate` sees R1's `provider_create_unavailable` code as retryable.
2. It clears K from R1.
3. It creates a new provisioning row R2 that owns K.
4. `BlaxelProvider.create` executes again and calls `friendlyVmName()` again, producing B.
5. Blaxel creates B and returns normally.
6. R2 becomes running with `provider_vm_id=B`.

Settled result:

```text
provider:
  A  live/unowned by cmux registry
  B  live/owned by R2

registry:
  R1 failed, provider_vm_id=NULL, K cleared
  R2 running, provider_vm_id=B, K current

user list:
  B
```

This converts stale/indeterminate local state into a second remote effect. The logical idempotency key protects concurrent/replayed database work, but it does not protect provider create across the response-loss boundary because provider identity is minted after that durable key stops being useful as a provider operation identity.

Practical consequences include duplicate compute allocation, hidden provider resources, storage/usage cost, and cleanup ownership that cannot be expressed through the normal cmux machine list.

## Negative controls

### Control A: database finalization fails after handle return

If create returns `VMHandle(A)` and only `markCreateRunning` fails, `rollbackProviderCreate` knows A and destroys it. This adjacent failure window is compensated.

That distinguishes this scout from a broad claim that “any create failure leaks a machine.”

### Control B: provider proves the POST failed before creating anything

A definite provider rejection such as a pre-effect validation failure can be recorded as failed and retried without adopting an existing sandbox. The dangerous state requires an **ambiguous** transport outcome where remote commit is possible.

### Control C: idempotent provider requests

GET and other retry-safe calls use bounded retry. The duplicate-create risk is specific to an effectful POST for which automatic replay is intentionally disabled.

### Control D: existing DB-owned machines

For rows that already have `provider_vm_id`, `reconcileVmProviderStatuses` can query provider status and repair drift. The missing-identity row is outside that repair set.

## Competing explanations checked

### "Blaxel POST failure proves no sandbox was created"

The implementation itself rejects that assumption. Its retry policy comments and tests treat POST network failure as execution-ambiguous and refuse automatic replay for that reason.

### "The same cmux idempotency key suppresses the retry"

Current repository policy deliberately does the opposite for `provider_create_unavailable`: it detaches the key from the failed row so the same stable key reaches the provider again immediately. The workflow regression asserts two provider calls across failure/retry.

### "The reaper eventually repairs the orphan"

Current reaper scope is old provisioning rows plus provider volume inventory, and its lifecycle is report-only. It has no sandbox adoption path and cannot infer A from R1.

### "The normal status reconciler will find it"

Its candidates require `provider_vm_id IS NOT NULL`. R1 never learned A.

## Repair owner

The clean repair boundary spans the durable create protocol and the Blaxel adapter, not the user list or a UI projection.

Preferred direction:

1. **Choose or persist the provider create identity before the POST.** The durable `cloud_vms` row id or the logical idempotency key can seed a stable operation-scoped provider name; alternatively persist the randomly generated A into a dedicated provider-create-intent field before effect execution.
2. Pass that identity through `CreateOptions` into `BlaxelProvider.create` instead of minting the only recoverable sandbox identity inside one provider-call stack frame.
3. On an ambiguous create transport failure, perform read-after-ambiguity by the exact persisted identity:
   - A exists with matching expected creation attributes -> adopt A and continue finalization;
   - A is authoritatively absent -> create/retry A;
   - outcome remains indeterminate -> retain a recoverable provisioning state that still names A.
4. Keep blind POST replay disabled.
5. Optionally add sandbox orphan reporting as defense in depth, but do not make a periodic reaper the primary transaction protocol.

The smallest invariant owner is the layer that knows both the durable logical mutation identity and the provider create identity before the external effect begins.

## Target-native discriminator to add

No upstream mutation was made. The next evidence step should live in the owned fork or an authorized execution surface.

A useful two-part regression would preserve current module boundaries:

### A. Blaxel driver ambiguity test

Extend `web/tests/vm-blaxel-fetch-retry.test.ts` or a provider test fixture with a fake control plane that:

1. receives `POST /sandboxes` for A;
2. records sandbox A in fake provider state;
3. throws a network/response-body error instead of returning the response;
4. asserts the driver does not replay the POST.

This turns the already-documented ambiguity into executable provider state: **remote effect present, local create call failed**.

### B. Workflow consequence test

In `web/tests/vm-workflows.test.ts`, use a provider double whose first `create` records A in an independent provider-state set then fails with `VmProviderOperationError`; the second same-key call records B and succeeds.

Assert after the first invocation:

```text
provider set = {A}
cloud_vms R1 = failed, provider_vm_id NULL
listUserVms = []
```

Then retry the same idempotency key and assert:

```text
provider set = {A, B}
cloud_vms visible running rows = {B}
```

Negative variant: return `VMHandle(A)` and fail `markCreateRunning`; assert rollback removes A.

A stronger integrated provider test can later bind both halves to the real Blaxel adapter with an injected name/randomness seam or a local fake HTTP control plane.

## Evidence labels

| Claim | Label | Evidence |
| --- | --- | --- |
| pinned cmux source revision and listed control flow | `source-read` | exact `eaa899cb...` source |
| POST network failures are never replayed | `source-read` + existing `target-executed-by-upstream-tests` source assertion | `vm-blaxel-fetch-retry.test.ts` test definitions; Fieldwork did not execute them in this scout |
| provider-create failure becomes immediately same-key retryable | `source-read` | `workflows.ts`, `repository.ts`, `vm-workflows.test.ts` |
| rows without provider id disappear from user list and status reconciliation | `source-read` | `workflows.ts`, `repository.ts` |
| reaper cannot adopt an orphan sandbox | `source-read` | `reaper.ts`, provider gateway inventory surface |
| Blaxel can commit the POST before the response is lost | `Inferred`, strongly supported by the code's explicit POST ambiguity model | provider-level interruption execution pending |
| final `{A,B}` duplicate provider state | `Inferred from source composition` | target-native consequence test prepared above, not executed |

No claim in this report is promoted to `target-executed`, `integration-executed`, or `full-gate` by this Fieldwork run.

## Evidence limit

This scout did not mutate `manaflow-ai/cmux`, contact upstream, create a Blaxel sandbox, use production credentials, or run a live provider fault injection.

The strongest established statement is therefore:

> **Under the remote-commit-before-response-loss outcome that cmux's own Blaxel retry policy treats as possible, current recovery loses the provider identity required to reconcile that effect, while the same logical idempotency key is intentionally allowed to start a fresh provider create. No automatic adoption path for the first sandbox is visible in the inspected source.**

A retained target-native test that models the remote commit and observes `{A,B}` after same-key retry would upgrade the practical duplicate-effect consequence from source composition to executed evidence.

## Recommendation

Retain this as a high-consequence recovery finding and promote it to a focused implementation campaign only after the two-part target-native discriminator runs on an owned fork or other permitted execution surface.

The likely implementation should make provider-create identity durable before the POST and resolve ambiguous outcomes by exact read-after-ambiguity. A UI cleanup or periodic reaper-only patch would leave the transaction invariant implicit.

Upstream remained read-only throughout this scout.
