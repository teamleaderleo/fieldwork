# CMUX Blaxel create response-loss implementation checkpoint

Date: 2026-09-02  
Programme: high-leverage-open-source  
Fieldwork issue: #928  
Worker: `chatgpt:gpt-5.6-sol`  
Upstream contact authorized: `false`

## Current source boundary

Re-fetched upstream `manaflow-ai/cmux` main before implementation claims.

Current upstream revision used by the implementation lane:

`9e2dd50957936153ca0da61d2f079937674f9375`

The Cloud VM create owners examined remain:

- `web/services/vms/repository.ts`
- `web/services/vms/workflows.ts`
- `web/services/vms/providerGateway.ts`
- `web/services/vms/drivers/blaxel.ts`
- `web/services/vms/billingGateway.ts`
- relevant VM workflow and Blaxel tests

Upstream remained read-only. All branches, tests, workflows, and commits were created in `teamleaderleo/cmux` or this owned Fieldwork branch.

## Invariant

One logical VM create may own at most one live Blaxel sandbox attempt at a time.

Before the external sandbox create starts, CMUX needs a durable external-attempt identity. After an ambiguous result or process restart, replay must address that same attempt identity. A second sandbox identity may begin only after the first attempt is authoritatively absent or fully retired.

## Identity owners

At the current repair boundary:

| Identity | Owner | Durable before provider call? |
| --- | --- | --- |
| logical request / API idempotency key | CMUX caller + `cloud_vms.idempotency_key` | yes |
| DB VM row / generation | `cloud_vms.id` | yes |
| Blaxel external create attempt | `provider_metadata.createIdentity` | candidate B: yes at row insert; candidate C direction: yes immediately before provider start |
| deterministic Blaxel sandbox name | Blaxel adapter, derived from `createIdentity` | reproducible |
| provider VM ID | Blaxel sandbox name returned/adopted into `provider_vm_id` | after create/adoption |
| retry generation | current `cloud_vms` row transitions | yes |
| visible VM | running row with `provider_vm_id` | after finalization |

## Candidate A: failed-row identity handoff

Earlier candidate retained one Blaxel create identity across the immediate failed-row to successor-row retry and made the sandbox name deterministic.

It fixed the already-proven response-loss retry case, but it had a restart hole: a process crash could leave the original row in `provisioning` with no `provider_vm_id`. Current same-key behavior returns `VmCreateInProgressError`, so the failed-row successor handoff never runs.

Disposition: useful negative result. The durable attempt must be resumable from the original row itself; successor-row inheritance alone is insufficient.

## Candidate B: resumable same-attempt provider protocol

Owned branch:

`fieldwork/blaxel-create-response-loss-resume-20260901`

Product commit:

`f11eda12dbf85edc1f961ebe5c9db9adba36e767`

Execution carrier run:

`33577608651`

Result: success.

### Candidate B repair boundary

1. Keep a durable Blaxel `createIdentity` on the VM row.
2. Derive a deterministic sandbox name from that identity.
3. Use Blaxel `POST /sandboxes?createIfNotExist=true` for identified attempts, so replay of the same name returns/reuses the same sandbox.
4. Preserve read-after-ambiguity behavior for transport failures.
5. Permit one stale `provisioning` row to be atomically claimed after the request timeout window.
6. Resume provider create with the same row metadata and the same `createIdentity`.
7. Finalize the same row with the adopted provider ID.
8. If provider identity finalization fails after a handle exists, compensate using the exact provider ID.

### Candidate B executed receipts

The successful carrier proved:

- stale durable intent is RED before the restart repair (`VmCreateInProgressError`);
- stale intent before any provider effect resumes and creates one provider VM;
- provider A already committed while CMUX lacks `provider_vm_id` is adopted by replaying the same external identity;
- same logical key after identity commit returns the running row without a second provider create;
- independent provider state remains a singleton during recovery;
- destroy after ambiguous recovery removes the recovered provider VM;
- a genuinely new logical request receives a genuinely new external identity;
- the earlier ambiguous response-loss repair remains GREEN;
- Blaxel provider controls remain GREEN;
- the existing transient provider-create retry control remains GREEN;
- the canonical definite pre-effect failure negative control remains GREEN.

The original canonical response-loss fake remains RED on repaired source because that fake intentionally ignores the new provider-attempt identity contract and invents a fresh provider ID on every gateway create. This is an oracle limitation: it remains valuable as proof of the original bug and negative control, while provider-native GREEN tests exercise the repaired contract.

## New adjacent finding: billing reservation ambiguity

The create workflow performs `reserveCreate` after the durable VM row is inserted and before provider create.

`VmBillingGateway.reserveCreate` accepts the logical idempotency key, but the live Stack adapter drops it and calls the Stack item API as `tryDecreaseQuantity(amount)`.

Pinned dependency during this investigation: `@stackframe/stack 2.8.108`.

The public server-item mutation contract exposes an atomic decrement amount but no create-attempt/idempotency token. Therefore a process crash or response loss around the credit decrement can leave CMUX unable to prove whether billing committed.

Candidate B resumes an identified provider attempt without reserving credit again. That prevents double-debit when the first reservation committed, but a row whose process died before the billing call can also carry a `createIdentity` under candidate B and later resume provider create without ever reserving credit.

This does not reopen the orphaned-compute bug, but it weakens the full crash protocol. A stronger phase boundary is warranted.

## Candidate C: durable provider-start fence

Owned test branch:

`fieldwork/blaxel-create-response-loss-billing-fence-20260901`

Test head:

`eaedff9451d3927d38788d1e89c5fad772e99a4d`

Carrier branch:

`fieldwork/blaxel-create-response-loss-billing-fence-carrier-20260901`

Carrier run:

`33578507039`

Current result: carrier failure during patch materialization; production candidate C has not been committed.

### Candidate C intended protocol

Introduce a durable provider-start phase marker in `provider_metadata`, alongside the external attempt identity.

Conceptually:

```text
R inserted
  providerCreateReady absent
        |
        v
billing.reserveCreate()
        |
        v
persist providerCreateReady + createIdentity
        |
        v
Blaxel create/replay exact identity
```

Restart behavior:

- stale row missing `providerCreateReady` -> fail closed; zero provider create and zero billing replay;
- stale row with `providerCreateReady` and `createIdentity` -> resume the exact Blaxel attempt;
- running row with committed provider ID -> ordinary idempotent replay returns the row.

This isolates the unresolvable Stack debit ambiguity from the compute side. A billing-ambiguous row may require manual or provider-specific billing reconciliation, but it cannot start compute after restart until CMUX has durably crossed the billing phase.

### Candidate C RED receipt

The pre-fence discriminator ran successfully before repair. On candidate B, a stale row carrying `createIdentity` but no provider-start fence was resumed and reached the provider. The test expected fail-closed behavior, so the intended RED was observed.

### Candidate C carrier failure classification

The run stopped in `Materialize durable provider-start fence` before GREEN tests.

Failure text:

`fresh provider metadata source: expected one match, found 2`

This is a patcher/source-match defect in the execution carrier, not a product-test failure. The RED discriminator completed first and established the unsafe candidate-B phase behavior. Candidate C still needs the patch script repaired and the full test matrix rerun.

## Remaining experiments for candidate C

After fixing the carrier patcher, execute:

- stale row before provider-start fence -> zero provider calls, zero billing replay;
- ordinary fresh create -> one billing reservation, provider receives durable ready identity;
- crash after durable provider-start fence and before provider call -> resume exact identity;
- crash after provider success and before provider identity commit -> adopt exact identity;
- crash after provider identity commit and before user-visible success -> return running row, zero second create;
- provider success + response loss -> singleton provider state;
- provider timeout with unknown external fate -> preserve exact attempt identity and block blind new identity;
- repeated same logical idempotency key -> converges on one external attempt;
- genuinely new logical request -> new external identity;
- cleanup/destroy after ambiguous recovery -> provider singleton removed;
- definite pre-effect provider failure -> retry may create one VM;
- existing Blaxel provider and workflow controls.

## Current decision

Candidate B is the last fully executed GREEN repair. It closes the proven orphan-on-response-loss bug and the stale-provisioning restart gap on the provider side.

Candidate C is preferred for a final repair PR because it adds a durable phase fence between the non-idempotent billing decrement and provider start. Its first RED succeeded; its patch carrier needs repair before the candidate can be promoted.

No fork repair PR has been promoted from candidate C yet.

## Remaining uncertainty

1. Stack's ordinary server-item mutation API has no per-operation idempotency token in the inspected pinned contract. Billing ambiguity before the provider-start fence therefore fails closed and may require a separate accounting reconciliation path.
2. The stale-claim threshold is currently tied to the API create timeout window. Review should confirm that no legitimate create request can remain active beyond the chosen claim age.
3. The real Blaxel `createIfNotExist=true` semantics were established from the provider API contract used by the adapter; live production fault injection was not performed.
4. Other providers have separate identity/idempotency contracts and remain outside this Blaxel repair lane.

## Next decision

Repair candidate C's materialization carrier, rerun the full matrix, then compare the resulting diff against candidate B. Promote C if its provider-start fence remains bounded and all existing controls stay green. If C exposes a deeper billing dependency, retain B as the provider-side repair and record billing crash recovery as a separate blocker/lead.

Upstream `manaflow-ai/cmux` remained read-only throughout this implementation work.