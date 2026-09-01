# cmux Cloud snapshot-materialization identity cloning scout

Date: 2026-09-01  
Programme: high-leverage-open-source (#114)  
Fieldwork issue: #934  
Target: `manaflow-ai/cmux`  
Pinned execution baseline: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Current upstream recheck: `6044a8b3f43152d2e6fc17f771fd4b277b393118`  
Worker: `chatgpt:gpt-5.6-sol`  
State: `complete`  
Claim scope: mechanism / interface / recovery / identity  
Upstream contact authorized: `false`

## Result

**Retain the finding.** CMUX's current Cloud snapshot-materialization path can carry machine-scoped identity and authority from one logical machine into a separately tracked machine. Three independent target-native discriminators now execute the consequence at the client-trust, daemon-authorization, and durable-resource-identity layers.

The core invariant is:

> **Materializing a snapshot as a new independently managed machine must establish a new machine-scoped identity before network attach.**

A pause/resume, process restart, or compute resurrection of the *same* logical machine may preserve daemon and machine identity. A fork or restore that creates a separately addressable tracked machine needs an explicit new-machine identity transition.

No cross-account access claim is made. This is an identity/isolation and recovery finding inside authorized Cloud state.

## In simple words

CMUX deliberately persists the things that make a Cloud daemon feel like the same machine after a restart:

- the cmux-remote Noise/static daemon key;
- the enrolled-device authorization database;
- the root-level CMUX `machine-id`;
- durable session/registry state.

That persistence is correct for resurrection. The Cloud product also uses snapshots to create a **new tracked machine**. `cmux vm fork` is documented as a clone for a parallel experiment; `cmux vm restore <snapshot-id>` is documented as `snapshot -> new tracked machine`.

For the modern E2B and Daytona paths inspected here, the copied machine starts/ensures cmux-tui from snapshotted state without a visible new-machine rekey step. The result is that one persisted identity can represent two independently managed machines.

The consequences are now executable:

1. the Mac's shared known-daemon store can be re-pinned from source A's route to copied machine B's route, leaving A undiscoverable on ordinary reconnect when another daemon is also known;
2. copied authorization databases can diverge after the copy, so source A can revoke a device while B still authorizes it under the **same daemon fingerprint**;
3. a copied workspace state root preserves the same `MachinePublicId` and `SessionPublicId`, while a fresh root receives independent identities.

## Product contract and lifecycle boundary

`skills/cmux-cloud-vm/references/commands.md` describes:

- `cmux vm fork <id>` as a clone for a parallel experiment;
- `cmux vm restore <snapshot-id>` as `snapshot -> new tracked machine`.

The intended lifecycle distinction is therefore explicit. These operations are not merely resume operations on the source VM.

The current source already has the resurrection half of the contract:

- remote daemon identity and enrolled devices are intentionally persisted so they survive compute resurrection;
- `WorkspaceRegistry` has an upstream test named `machine_identity_is_state_root_global_and_survives_restart`;
- the native frontend contract treats `(machine_id, session_id, resource_id)` as the durable resource address while transport route is mutable resolution data.

The missing transition is **copied state -> new machine**.

## Source map

### Generic fork and restore

`web/services/vms/workflows.ts`

For providers without a native fork path, `forkVm` snapshots the source and calls `createVm` using the snapshot as the image, recording a separate VM. `restoreVm` likewise creates a new tracked VM from an owned snapshot.

The relevant workflow and identity-owner files did not change between the pinned execution baseline and current upstream `6044a8b3...`; current main is four commits ahead of the execution baseline and those commits do not touch the mechanisms exercised below.

### E2B

`web/services/vms/drivers/e2b.ts`

E2B materializes a new sandbox with `Sandbox.create(image, ...)`, including when the image is a snapshot id, then bootstraps/ensures cmux-tui. The daemon runs with persistent root state. No fork/restore-specific daemon rekey or CMUX machine-id rotation is visible before the copied daemon becomes available.

Upstream PR #11370 independently dogfooded the live E2B product path on staging and recorded `capabilities.snapshot/fork = true`; its parity loop successfully ran `vm snapshot` and `vm fork`, observed the new E2B machine, and removed it afterwards. That is useful operational confirmation that the E2B snapshot/fork lifecycle is active, although that PR did not compare source/fork identities.

### Daytona

`web/services/vms/drivers/daytona.ts`

Daytona uses the same modern cmux-remote daemon model, snapshots provider state, creates a new sandbox from a snapshot, and starts/ensures cmux-tui without a visible new-machine rekey step. The generic snapshot -> create fork workflow therefore presents the same identity boundary.

### Freestyle boundary

Freestyle has different native/beta lifecycle behavior, so this report does not generalize the strongest claim to every provider. The retained provider claim is E2B + Daytona on the modern remote stack.

### Existing clean-checkpoint precedent

Upstream PR #9618, `Add credential-free Sprite base builder`, was closed without merge on 2026-09-01, but its implementation note is a strong design precedent: the reusable Sprite checkpoint builder deliberately kept **provider credentials, daemon identities, and enrollment secrets out of checkpoints**, and its real checkpoint verification reported daemon state absent.

That is the same lifecycle distinction this finding needs: reusable/new-machine materialization should not inherit machine authority merely because resurrection state normally does.

## Shared Mac trust state

`Sources/Cloud/CloudTuiClientPaths.swift`, `CloudMachineLink.swift`, and `CloudMachineLinkManager.swift`

The ordinary macOS Cloud path uses one client identity directory and known-daemons store shared across every Cloud Machine Link. Each awake machine runs a headless `cmux-tui remote connect --headless` link through that shared store. Per-control-plane-machine fingerprint mappings are separate.

A new copied machine has a new control-plane VM id, so the Mac initially has no per-machine fingerprint mapping for it. Its invitation can therefore successfully pin the copied daemon fingerprint at the new route even while the copied daemon database already knows the same Mac device key.

`cmux-tui/crates/cmux-remote/src/identity.rs` keys known daemons by daemon fingerprint and replaces route hints when an enrolled fingerprint is re-pinned. WSS hints are canonicalized to credential-free origins.

`cmux-tui/crates/cmux-tui/src/remote_cli.rs` selects explicit routes as follows:

- route match -> select the daemon;
- no match with exactly one known daemon -> sole-daemon fallback;
- no match with multiple known daemons -> `no known daemon matches this route; connect with an invitation`.

That final branch is the concrete reconnect consequence exercised by D1.

## D1 — source route becomes undiscoverable

Owned execution PR: `teamleaderleo/cmux#19`  
Canonical test artifact: `teamleaderleo/cmux#9`  
Exact head: `f4c6dc6b030b929eb89212c4db19c2f373e2f8ae`  
Actions run: `33552460852`  
Job: `100004976839`

Focused result: **3 passed; 0 failed**.

Passing cases:

- `cloned_daemon_repin_orphans_source_route_when_another_daemon_is_known`;
- `sole_shared_daemon_uses_the_existing_single_daemon_fallback`;
- `distinct_fork_daemon_identity_preserves_source_route_selection`.

The candidate sequence is:

1. source A is known as fingerprint D at route A;
2. unrelated daemon C is also known;
3. copied machine B presents D and is successfully attached/enrolled at route B;
4. the shared client store re-pins D to B's route, replacing A's route hint;
5. A still regards the Mac device as enrolled and can legitimately omit a new invitation;
6. explicit route A now has no known-daemon match while multiple daemons exist;
7. selection fails locally with the invitation-required error before connection.

The distinct-fingerprint control preserves A's route. The sole-daemon control explains why a simpler smoke test can miss the failure.

An earlier D1 run stopped on a harness expectation that retained `/v1/link`; CMUX correctly canonicalizes WSS route hints to the origin. The corrected test uses the product's canonical route and is the retained receipt.

## D2 — one daemon fingerprint, two revocation histories

Owned execution PR: `teamleaderleo/cmux#21`  
Exact head: `cd0dfde9d63d407df29552789efead7b18ee35d0`  
Actions run: `33552781912`  
Job: `100006092106`

Focused test:

`copied_auth_database_creates_split_brain_revocation_under_one_daemon_fingerprint`

Result: **1 passed; 0 failed** in 0.06 s.

The test uses the real `AuthDatabase` / server authenticator path:

1. create a daemon and enroll a generated client device through invitation + approval;
2. close the database owner cleanly;
3. copy only `identity.json` and `devices.json` into another state root;
4. reopen source and copy;
5. confirm both present the same daemon fingerprint and initially authorize the same device;
6. revoke that device on source A;
7. confirm A rejects enrolled auth;
8. confirm copied B still authorizes the same device under the same daemon fingerprint.

This is the deeper authority result: after copying state, one cryptographic daemon identity can represent two independently diverging authorization histories.

It also tightens the repair policy. Rotating only `identity.json` while retaining copied `devices.json` would give B a new daemon fingerprint while still inheriting every source enrollment. Whether that is desirable must be an explicit product decision; fresh enrollment is the safer default for a new independently managed machine.

## D3 — copied durable CMUX machine/session namespace

Owned execution PR: `teamleaderleo/cmux#22`  
Exact green head: `fb172dc2689d0cff1c0a5af58608549afe47a85b`  
Actions run: `33554899740`  
Job: `100013202491`

Focused test:

`copied_workspace_state_root_preserves_machine_and_session_identity`

Result: **1 passed; 0 failed** in 0.04 s.

The test exercises public `WorkspaceRegistry` behavior:

1. open source state and record `MachinePublicId` + `SessionPublicId`;
2. same-root restart preserves both — resurrection control;
3. copy the closed state root into a separate root and reopen the same session;
4. copied root preserves the same machine and session IDs;
5. a fresh root receives independent machine and session IDs — negative control.

The first D3 run did not reach product assertions: the test failed to compile because the fresh-root control passed a `PathBuf` where `&Path` was required. The one-character borrow fix produced the green result above.

The persistence layout gives a useful repair seam. `WorkspaceRegistry::open(root, session)` loads the root-level `machine-id` separately from the session SQLite database. A new-machine transition can therefore rotate the machine namespace while intentionally preserving copied session IDs, resource IDs, journals, and history.

## Evidence boundary

### Established

- Fork and restore are product-level new-machine operations.
- E2B and Daytona materialize new machines from copied snapshot state and start/ensure cmux-tui without a visible new-machine rekey phase.
- CMUX deliberately persists daemon authority and durable machine/session identity in the copied state.
- Ordinary Mac Cloud links share one known-daemon store.
- D1 executes the client route-repin/source-reconnect failure with controls.
- D2 executes split-brain device revocation under one daemon fingerprint.
- D3 executes duplicate durable machine/session identity under a copied state root, with restart and fresh-root controls.
- Current upstream main has not changed the mechanisms under test.
- No matching upstream issue or PR was found for this exact snapshot-materialization identity collision at completion time.

### Still unexecuted

- a live E2B or Daytona source -> snapshot/fork/restore -> direct fingerprint and machine-id comparison;
- the full human-visible source-A / copied-B reconnect sequence in a tagged macOS app;
- production frequency and how commonly users have the multi-daemon known-store condition that exposes D1.

Those checks would improve operational frequency evidence. They are no longer required to establish the local identity model or the consequences of copied state. The scout stop condition is satisfied with bounded hosted uncertainty.

## Repair boundary

A client-only accommodation such as keeping multiple Cloud routes under one daemon fingerprint would make D1 harder to trigger while preserving the D2 authority collision. The first repair owner should be the **new-machine snapshot materialization transition**.

A narrow product repair can preserve the useful copied workspace while separating machine authority:

1. before the copied daemon accepts network connections, rotate/regenerate the remote daemon static identity;
2. rotate the root-level CMUX `machine-id`;
3. explicitly choose the enrollment policy — safest default: clear copied enrolled-device authority and require fresh enrollment for the new machine;
4. retain session/resource IDs and copied journals when desired, because the new `machine_id` already creates a distinct durable address namespace;
5. make the transition idempotent against the new control-plane machine id so provider retries cannot rotate identity repeatedly;
6. perform the transition through CMUX-owned APIs that respect the auth DB lease, file locks, permissions, and atomic-write rules instead of provider shell code deleting private files.

An idempotent marker provides a clean model: copied state records source machine A; materializing B sees a different control-plane identity, performs the offline rekey, and commits marker B last. Retrying B is a no-op. Materializing C from B's snapshot rekeys again.

Existing `session reset-state` is intentionally not this operation: it removes one session's saved state/terminal-host state while the root machine identity survives. A clone-rekey operation should do the inverse kind of ownership work — rotate root machine authority while preserving session history.

The root-level resource-effect pepper was inspected and is not included in this finding. Copied mutation/idempotency history may be legitimate clone lineage; rotating the machine namespace is enough to separate durable addresses. Keep that decision separate unless a concrete receipt collision is demonstrated.

## Why this is a strong fieldwork target

This has the consequence/provability combination the programme is looking for:

- **consequence:** source reconnect failure, duplicated machine trust identity, split revocation authority, and duplicate durable machine namespace across independently managed Cloud machines;
- **provability:** three small target-native tests with controls, exact commit/run receipts, current-main freshness check, and provider lifecycle source that composes directly with those semantics;
- **repair ownership:** one explicit lifecycle boundary knows whether copied storage means resurrection or a new machine;
- **scope discipline:** no cross-account claim, no frequency claim, no claim that a hosted identity comparison has already run.

## Stop condition

Satisfied. The snapshot-identity premise survives source review; all three local discriminators execute the predicted consequences with negative controls; current main remains materially unchanged; hosted product-path identity comparison is retained as an operational follow-up, not a prerequisite to the finding.

Third-party upstream remains read-only.