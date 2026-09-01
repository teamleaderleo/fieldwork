# cmux Cloud snapshot-materialization identity cloning scout

Date: 2026-09-01  
Programme: high-leverage-open-source (#114)  
Fieldwork issue: #934  
Target: `manaflow-ai/cmux`  
Pinned execution baseline: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Current upstream recheck: `6044a8b3f43152d2e6fc17f771fd4b277b393118`  
Worker: `chatgpt:gpt-5.6-sol`  
State: `claimed`  
Claim scope: mechanism / interface / recovery / identity  
Upstream contact authorized: `false`

## In simple words

cmux deliberately persists the identities that make a Cloud daemon feel like the *same machine* after pause, restart, or compute resurrection: the daemon Noise key, enrolled-device records, a cmux machine public id, and the durable session/registry state.

That is correct for resurrection of one logical machine. The Cloud snapshot paths also use the copied state to materialize a **new tracked machine**. `cmux vm fork` is documented as a clone for a parallel experiment, while `cmux vm restore <snapshot-id>` is explicitly documented as `snapshot -> new tracked machine`.

For the modern E2B and Daytona providers, the new machine boots from snapshot state and starts cmux-tui without an identity-reset step. This makes the same persisted identity serve two different control-plane machines.

One concrete consequence is now target-native and executed: if the source and copy share one daemon fingerprint, enrolling/attaching the copy re-pins that fingerprint at the copy's route. With any unrelated daemon also in the Mac's shared known-daemon store, the source route becomes unresolvable and ordinary source reconnect fails with `no known daemon matches this route; connect with an invitation`. Distinct source/fork daemon identities preserve the source route; the existing one-daemon fallback masks the bug when no other daemon is known.

This is broader than the full `cmux vm tui` client. The normal macOS Cloud path intentionally uses **one client identity directory and known-daemons store shared across every Cloud Machine Link**, and each awake machine owns a headless `cmux-tui remote connect --headless` link through that store.

Two additional target-native discriminators are running: one for copied authorization databases diverging under a single daemon fingerprint, and one for copied workspace roots preserving the same `MachinePublicId` and `SessionPublicId`.

No cross-account access claim is made. The current finding is a lifecycle/identity collision within authorized Cloud state, with an executed reconnect consequence.

## Core invariant

**Materializing a snapshot as a new independently managed machine must establish a new machine-scoped identity before network attach.**

A pause/resume, process restart, or compute resurrection of the *same* logical machine may preserve daemon and machine identity. A fork or restore that creates a separately addressable tracked machine must not leave source and copy cryptographically or durably indistinguishable.

## Why this is a lifecycle-category error

cmux already has the resurrection half of this rule in source and tests:

- remote daemon identity and enrolled devices intentionally live on persistent Cloud storage so they survive sandbox resurrection;
- `WorkspaceRegistry` has an upstream test named `machine_identity_is_state_root_global_and_survives_restart`;
- the native frontend contract says a durable resource address is `(machine_id, session_id, resource_id)` while hostname, socket, relay, and mount route are mutable resolution data.

The missing transition is **copy -> new machine**. Current provider bootstrap treats the copied state as though it were merely the same machine restarting.

## Source map

### Generic fork and restore workflows

`web/services/vms/workflows.ts`

For non-Freestyle providers, `forkVm` performs:

1. `snapshotVm(source)`;
2. `createVm({ provider: source.provider, image: snapshot.id, ... })`;
3. records the result as a separate fork VM.

`restoreVm` checks snapshot ownership and then calls `createVm` for a new tracked VM from the snapshot.

The relevant `workflows.ts` blob is unchanged between the pinned execution baseline and the current upstream recheck.

### Product contract

`skills/cmux-cloud-vm/references/commands.md`

- `cmux vm fork <id>`: clone for a parallel experiment;
- `cmux vm restore <snapshot-id>`: snapshot -> new tracked machine.

This makes the intended lifecycle distinction explicit: these are not merely resume operations on the source VM.

### E2B snapshot materialization

`web/services/vms/drivers/e2b.ts`

- `snapshot` calls E2B `createSnapshot()`;
- `restore` calls `Sandbox.create(snapshotId, ...)`;
- restore then `ensureCmuxTuiRunning` on the copied filesystem;
- no fork/restore rekey or machine-id rotation is visible before the copied daemon starts;
- E2B uses `cmux-remote` as its only session transport;
- public ingress relies on cmux Noise device enrollment as the session gate.

The E2B driver blob is also unchanged at current upstream `6044a8b3...`.

E2B's own current material describes snapshots as reusable state: new sandboxes can be started from snapshots containing the configured workspace/filesystem state. This matches the CMUX driver's use of a snapshot id as a `Sandbox.create` image.

### Daytona snapshot materialization

`web/services/vms/drivers/daytona.ts`

Daytona uses the same modern `cmux-remote` model. Its source explicitly treats daemon identity under `/root` as persistent state, implements snapshot creation, creates a new sandbox from a snapshot, and then starts/ensures the copied cmux-tui daemon without a visible identity-reset step.

Because Daytona has no native `fork()` implementation in the inspected provider class, the generic snapshot -> `createVm` fork path applies.

This makes the mechanism multi-provider on the current modern remote stack: **E2B + Daytona**.

### Freestyle boundary

Freestyle is different. Its backend has a native fork path for the legacy platform, while the beta cmux-tui platform's `fork` currently refuses and points callers at snapshot/restore semantics. The strongest current claim therefore stays on E2B and Daytona rather than generalizing to every provider.

### Persistent daemon authority

`docs/cloud-cmux-tui-daemon.md`

The Cloud design explicitly requires remote daemon state to live on persistent `/root` storage so daemon identity and enrolled devices survive sandbox resurrection. Session state is persistent there as well.

`web/services/vms/drivers/cmuxTuiDaemon.ts`

Container providers start cmux-tui with `HOME=/root`. There is no current fork/restore-specific rekey argument or scrub phase.

`cmux-tui/crates/cmux-remote/src/identity.rs`

The remote identity layer persists the stable static identity and device authorization database as files including `identity.json` and `devices.json` under the daemon state root.

### Persistent cmux machine/session identity

`cmux-tui/crates/cmux-tui-core/src/workspace_registry.rs`

`WorkspaceRegistry` carries:

- `machine_id: MachinePublicId`;
- `session_id: SessionPublicId`;
- durable registry/session state in SQLite;
- a process/runtime generation that is separately refreshed.

The state root contains a persisted `machine-id` file. Upstream tests explicitly prove that machine identity is state-root-global and survives restart, while reopening the same named session preserves its session id.

### Durable resource-address contract

`cmux-tui/spec/native-frontend.md`

The persistent daemon's identity contract states:

- durable resource address: `(machine_id, session_id, resource_id)`;
- hostname/socket/relay/mount route: mutable resolution data.

A copied state root therefore carries the namespace intended to identify durable resources independently of route changes. A separately managed fork needs a new machine namespace even if copied session/resource lineage is intentionally preserved.

### Remote authorization contract

`cmux-tui/spec/remote-daemon.md`

- one daemon represents one OS-user authority;
- it owns one stable Noise static key;
- enrolled devices have independent application keys and revocation records;
- route hints are not daemon authorization;
- enrolled reconnects use the stable daemon identity.

If two independent VMs copy one daemon private key and later mutate their copied device databases independently, one cryptographic daemon identity can represent two diverging authorization authorities. A separate target-native discriminator is running for this branch.

### Shared Mac known-daemon state

`Sources/Cloud/CloudTuiClientPaths.swift`

The normal macOS Cloud implementation intentionally uses one state directory, `~/.cmuxterm/cmux-tui-client`, with **one device key + known-daemons store shared across every Cloud Machine Link**. Per-control-plane-VM fingerprints are kept separately in `vm-tui-devices.json`.

`Sources/Cloud/CloudMachineLink.swift` and `CloudMachineLinkManager.swift`

Each awake machine starts a headless remote link using that shared `stateDir`. The manager asks the provider for the endpoint using the per-VM saved fingerprint. A new fork/restore has a new control-plane VM id, so it initially has no per-VM fingerprint mapping and can receive an invitation even if the copied daemon database already contains the same Mac device key.

After approval the new VM gets its saved mapping, while the shared remote client store pins the daemon by fingerprint.

### Known-daemon route ownership

`cmux-tui/crates/cmux-remote/src/identity.rs`

Known daemons are keyed by daemon fingerprint. Re-pinning an already enrolled daemon replaces its route-hint list with the newly verified route list.

WSS route hints are intentionally normalized to a credential-free origin, e.g. `wss://127.0.0.1:10/v1/link` becomes `wss://127.0.0.1:10/`.

`cmux-tui/crates/cmux-tui/src/remote_cli.rs`

`select_known_daemon` behaves as follows:

- one route match -> select that daemon;
- no match and exactly one known daemon -> existing sole-daemon fallback;
- no match, explicit route, multiple known daemons -> `no known daemon matches this route; connect with an invitation`.

That multi-daemon branch is the executed consequence below.

## Proven failure sequence: source reconnect becomes undiscoverable

Let:

- source Cloud machine A have daemon fingerprint `D` and route `R_A`;
- unrelated daemon C have fingerprint `D_C` and route `R_C`;
- Mac client device M be enrolled on A;
- new machine B be materialized from A's snapshotted state.

Sequence:

1. shared Mac known-daemon store contains `D -> [R_A]` and `D_C -> [R_C]`;
2. copied machine B presents the same daemon key `D`;
3. B has a new control-plane VM id, so the Mac has no saved per-B fingerprint mapping and receives an invitation;
4. B's invitation flow connects/approves the existing device key and the client pins `D` at `R_B`;
5. because `D` is already an enrolled known-daemon record, its route list becomes `[R_B]`, displacing `R_A`;
6. source A still regards M as enrolled, so a later ordinary A endpoint may omit an invitation;
7. the shared headless client receives explicit `R_A`, finds no matching known daemon and sees multiple known daemons;
8. it rejects before network connection with `no known daemon matches this route; connect with an invitation`.

The reconnect failure is self-created by successfully attaching the copied machine.

## D1 — executed target-native route discriminator

Owned CMUX PR: `teamleaderleo/cmux#19`  
Canonical test-only artifact: `teamleaderleo/cmux#9`  
Exact test head: `f4c6dc6b030b929eb89212c4db19c2f373e2f8ae`  
Execution baseline production tree: upstream `8ef183f1e5de765b183aec9d1799f17a0848ae84` plus the test file only  
Actions run: `33552460852`  
Job: `100004976839`

The focused Rust job passed **3/3**:

- `cloned_daemon_repin_orphans_source_route_when_another_daemon_is_known` — PASS;
- `sole_shared_daemon_uses_the_existing_single_daemon_fallback` — PASS;
- `distinct_fork_daemon_identity_preserves_source_route_selection` — PASS.

The final test result was `3 passed; 0 failed`.

An earlier run stopped on a harness assertion because the test expected the full WSS `/v1/link` URL while CMUX correctly canonicalizes route hints to the origin. That run was useful evidence of the route rewrite itself, but it did not reach the route-selection assertion. The corrected run uses the product's canonical route representation and is the retained receipt.

### What D1 proves

D1 proves the local product mechanism, including the negative controls:

- one daemon fingerprint re-pinned from source route to copied-machine route displaces source ownership;
- the source route then hits the exact multi-daemon invitation-required error;
- a distinct fork daemon key prevents the failure;
- the one-daemon fallback explains why a simple two-machine smoke test can miss it.

D1 does **not** by itself prove a hosted E2B/Daytona snapshot physically copied the daemon file. That premise is supported separately by provider snapshot semantics plus the current file/state placement.

## D2 — copied authorization split-brain discriminator

Owned CMUX PR: `teamleaderleo/cmux#21`

The test uses real `AuthDatabase` and `ServerAuthenticator` APIs:

1. create a daemon and enroll a real generated client key through invitation + approval;
2. stop the database owner;
3. copy only `identity.json` and `devices.json` into a second state root;
4. reopen source and copy;
5. confirm the same daemon fingerprint and initially active device on both;
6. revoke the device on source;
7. require source enrolled auth to fail;
8. ask the copy to authorize the same enrolled device under the same daemon fingerprint.

Status: **running** at this report revision. No result claimed yet.

## D3 — copied durable machine/session identity discriminator

Owned CMUX PR: `teamleaderleo/cmux#22`

The test uses public `WorkspaceRegistry` behavior:

1. open source state root and record `MachinePublicId` + `SessionPublicId`;
2. same-root restart control must preserve both;
3. recursively copy the closed state root into a new root and reopen the same session;
4. compare machine/session identities;
5. fresh-root negative control must receive independent identities.

Status: **running** at this report revision. No result claimed yet.

## Provider/product evidence boundary

### Established

- `vm fork` is a new-machine operation; generic non-Freestyle fork is snapshot -> `createVm`.
- `vm restore` is documented as snapshot -> new tracked machine and also creates a new VM from the owned snapshot.
- E2B and Daytona materialize new sandboxes from snapshot state and start/ensure cmux-tui with no visible new-machine rekey step.
- daemon identity/device state and cmux machine/session state are deliberately persisted in the copied user/root state.
- current upstream still has the E2B no-rekey restore path; the relevant E2B and generic workflow blobs are unchanged from the pinned execution baseline.
- the Mac uses one known-daemon state store across ordinary Cloud machine links.
- the route-repin reconnect consequence is target-native and executed with controls.

### Still unexecuted

- a live product-path E2B or Daytona source -> snapshot materialization -> compare daemon fingerprint/machine id run;
- live source/fork UI sequence after the copied machine's first attach;
- current production frequency / how many users have >1 unrelated known daemon when using E2B/Daytona.

These hosted checks would strengthen operational evidence, but the local mechanism no longer depends on speculation about client behavior.

## Adjacent capability mismatch

Provider capability reporting currently defines `fork` from a provider's native `fork()` method, so E2B/Daytona can advertise `fork: false` even though the backend generic fork workflow can snapshot and create them.

The current CLI/socket path can send `vm.fork` directly, and the REST fork endpoint runs the generic workflow. This means GUI capability hiding and CLI/backend behavior can disagree. Keep this as a separate adjacent bug; it is not needed for the identity finding.

## Repair boundary

A client-only accommodation such as keeping multiple route hints under one fingerprint would make D1 disappear while preserving the deeper identity collision. That is the wrong first owner.

The clean transition owner is **snapshot materialization into a new tracked machine**, because this layer uniquely knows the difference between:

- resurrection/resume of the same logical machine — preserve identity;
- fork/restore into a new logical machine — establish new machine-scoped identity.

The minimal policy to evaluate after D2/D3 settles is:

1. rotate/regenerate the remote daemon static identity before the copied daemon accepts network connections;
2. establish a new cmux `machine-id` namespace before opening the copied registry;
3. decide explicitly whether copied enrolled-device records should be retained under the new daemon key or require fresh enrollment;
4. preserve session/resource IDs when useful for copied history because a new `machine_id` already gives them an independent durable address namespace;
5. expose this as a purpose-built clone/rekey transition rather than provider code deleting implementation-private files by hand.

This avoids throwing away the useful part of a fork—files, terminals/history/checkpoints—while separating machine authority and durable machine identity.

## Competing explanations ruled out or bounded

- **"The outer control-plane VM id already namespaces everything."** It protects several Mac catalog/UI paths, but the remote client known-daemon store is explicitly shared and keyed by daemon fingerprint; D1 executes the resulting collision. CMUX's own durable resource contract also defines an inner machine identity independent of route.
- **"The copied machine will just reuse the old per-VM fingerprint mapping."** It cannot: B has a new control-plane VM id. The mapping is per VM id, so first B attach can mint an invitation and re-pin the shared daemon fingerprint.
- **"One daemon fallback prevents the bug."** Only when the shared store contains exactly one known daemon. D1 retains that as a negative control and proves the failure appears once another known daemon exists.
- **"This is E2B-only."** Daytona has the same modern cmux-remote + snapshot materialization pattern. Freestyle is separately bounded above; Blaxel remains the default and does not currently expose this snapshot/fork path.
- **"Snapshot restore is merely resurrection."** CMUX's own command contract calls restore a new tracked machine, and fork is a parallel clone. Same-machine resume is a separate provider operation.

## Current assessment

**Consequence:** high for affected snapshot-materialization paths. A successful new-machine attach can strand the source's ordinary Cloud link in a shared trust store; copied machine authority also has a plausible split-revocation branch under active test.

**Provability:** high. The reconnect mechanism is target-native with explicit positive/negative controls; snapshot state copying and persisted identity placement are direct provider/source contracts. Two independent identity tests are running.

**Reach:** narrower than default Blaxel Cloud usage, but not singular: modern E2B and Daytona paths plus both fork and restore materialization.

**Repair scope:** bounded conceptually. The key design decision is a purpose-built new-machine rekey transition before daemon attach, with copied workspace history kept separately from machine authority.

## Stop condition

Promote to ready-for-synthesis when D2 and D3 either:

- execute as predicted, giving independent authorization and durable-identity evidence; or
- reveal a product fence that materially weakens the clone premise.

A hosted E2B/Daytona run remains desirable for operational proof but is not required to retain D1 as an executed product-mechanism finding.
