# cmux Cloud fork identity cloning scout

Date: 2026-09-01  
Programme: high-leverage-open-source (#114)  
Fieldwork issue: #934  
Target: `manaflow-ai/cmux`  
Pinned target main: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Worker: `chatgpt:gpt-5.6-sol`  
State: `claimed`  
Claim scope: mechanism / interface / recovery / identity  
Upstream contact authorized: `false`

## In simple words

`cmux vm fork` is presented as a way to clone a Cloud machine for an independent parallel experiment. On E2B, the fallback fork path snapshots the source filesystem and starts a newly tracked machine from that snapshot. cmux deliberately stores the remote daemon's cryptographic identity, enrolled-device database, and durable cmux-tui machine/session state under root-owned persistent state paths so those facts survive resurrection of the same machine.

Those two contracts appear to collide: a fork can become a distinct control-plane VM while inheriting the source daemon key, enrollment state, machine public id, registry/session identity, and copied workspace history.

The first concrete consequence under investigation is local trust-route poisoning. The client stores known daemons by daemon fingerprint. Re-pinning an enrolled fingerprint replaces its route hints. If source A and fork B share a daemon key, B's first invitation can move the one known-daemon record from route A to route B. Once any unrelated daemon C is also known, a subsequent normal attach to A can fail with `no known daemon matches this route; connect with an invitation`, even though A still regards the Mac device as enrolled and therefore need not mint a new invitation.

This report does **not** yet claim a live E2B reproduction. The client-side consequence is being converted into a target-native regression first; hosted proof of cloned daemon and machine identity remains a separate gate.

## Invariant

Forking a Cloud VM into an independent machine must not clone machine-scoped authority or identity in a way that makes the source and fork cryptographically or logically indistinguishable.

Resurrection of the same physical/logical machine may preserve those identities. Forking into a separately addressable machine needs an explicit identity policy.

## Source map

### Fork workflow

`web/services/vms/workflows.ts`

For providers without a native fork primitive, `forkVm` calls `snapshotVm(...)` and then `createVm(...)` with `image: snapshot.id`. The result is recorded as a separate fork VM.

### E2B snapshot and restore

`web/services/vms/drivers/e2b.ts`

- `snapshot` calls E2B `createSnapshot()`.
- `restore` creates a new sandbox from the snapshot id.
- restore starts/ensures cmux-tui after the copied filesystem boots.
- no identity reset or state scrub is visible between snapshot creation and daemon startup.
- E2B's public ingress relies on the cmux-tui Noise enrollment as the session gate.

### Persistent daemon identity

`docs/cloud-cmux-tui-daemon.md`

The Cloud design explicitly places remote daemon state under `/root` so daemon identity and enrolled devices survive sandbox resurrection. Session state lives persistently there as well.

`web/services/vms/drivers/cmuxTuiDaemon.ts`

Every container provider starts the daemon with `HOME=/root`; no fork-specific rekey argument or scrub step is present.

`cmux-tui/crates/cmux-remote/src/identity.rs`

The Linux default remote state root is `$HOME/.local/state/cmux/remote`. Daemon identity and authorization/device state are stored beneath this root.

### Persistent cmux-tui machine/session identity

`cmux-tui/crates/cmux-tui-core/src/platform.rs`

Linux session/registry state is rooted in the user's persistent cmux-tui state directory.

`cmux-tui/crates/cmux-tui-core/src/workspace_registry.rs`

The registry loads or creates a persisted machine public id and loads durable registry/session metadata from SQLite. The runtime registry generation is newly generated on open, but the stored machine/registry/session identities survive.

### Client identity and route ownership

`cmux-tui/crates/cmux-remote/src/identity.rs`

Known daemons are keyed by daemon fingerprint. Re-pinning an existing enrolled daemon replaces its `route_hints` with the new route list.

`cmux-tui/crates/cmux-tui/src/remote_cli.rs`

`select_known_daemon` resolves an explicit route by matching it against stored route hints. If no route matches and exactly one daemon is known, it has a sole-daemon fallback. If no route matches and multiple daemons are known, it returns `no known daemon matches this route; connect with an invitation`.

The invitation path pins the invitation daemon key after a successful connection. The non-invitation Cloud path selects the expected daemon from the explicit route and known-daemon store.

### Control-plane enrollment behavior

`web/services/vms/drivers/e2b.ts`

`openCmuxRemote` checks whether the supplied client device fingerprint is enrolled on the machine. It only mints an invitation when that check is false.

This means a source machine whose copied auth database still contains the device can legitimately omit an invitation even after the local route binding has been displaced by the fork.

## Candidate failure sequence

Let:

- source Cloud machine A have daemon fingerprint `D` and route `R_A`;
- unrelated daemon C have fingerprint `D_C` and route `R_C`;
- Mac client device M be enrolled on A;
- fork B be created from A's E2B snapshot.

Candidate sequence:

1. client known-daemon store contains `D -> [R_A]` and `D_C -> [R_C]`;
2. fork B inherits A's daemon private key and enrollment database, so B also presents fingerprint `D`;
3. B has a new control-plane VM id, so its first app attach has no saved per-machine device mapping and receives an invitation;
4. the invitation connection succeeds and `pin_daemon(D, [R_B])` replaces A's stored route with B's route;
5. source A still has M in its enrollment database, so a later normal A attach can omit an invitation;
6. the client receives explicit `R_A`, but no stored daemon now claims that route and there is more than one known daemon;
7. `select_known_daemon` rejects the attach with `no known daemon matches this route; connect with an invitation`.

The failure is self-created: the fork's successful enrollment can make the source's ordinary enrolled reconnect undiscoverable locally.

## Discriminators

### D1 — target-native client-store red test

Use a temporary `ClientIdentityStore`:

1. pin key D at `wss://a.example/v1/link`;
2. pin unrelated key C at `wss://c.example/v1/link`;
3. pin key D again at `wss://b.example/v1/link`;
4. resolve explicit source route A with `select_known_daemon`.

Expected current result from source reading: error `no known daemon matches this route; connect with an invitation`.

### Negative controls

- only D is known: sole-daemon fallback should still resolve D for route A;
- D is re-pinned to the same route A: source resolution stays valid;
- B uses a distinct daemon key: A and B remain independently addressable;
- pause/resume or resurrection of A without forking should preserve D and A's normal identity.

### D2 — hosted fork identity check

On disposable E2B state:

1. create/enroll source A;
2. record daemon fingerprint and cmux machine public id;
3. fork A through `cmux vm fork`;
4. record fork B fingerprint and machine public id before any manual rekey;
5. compare A/B;
6. enroll/attach B, then retry A with an unrelated known daemon C present.

Hosted execution is not yet available in this scout.

## Evidence boundary

Established by current-source reading:

- fallback fork is snapshot -> fresh tracked VM;
- E2B starts the copied daemon without visible fork-specific identity rotation;
- machine-scoped cmux remote and registry identity is deliberately persisted under the snapshotted root home;
- known-daemon route replacement and multi-daemon no-match failure are explicit client behaviors.

Still to execute:

- target-native D1 regression;
- live or provider-faithful proof that an E2B snapshot preserves the exact daemon identity and cmux machine id under the product path;
- end-to-end source A attach failure after B enrollment.

No cross-account access claim is made. Snapshot restore is owner-scoped in current backend source. The current concern is failure of machine isolation/identity semantics within the authorized account and the resulting recovery/trust confusion.

## Candidate repair boundary

Do not erase all cmux-tui state reflexively: a fork may intentionally preserve workspace contents/history while still needing a new machine identity.

Candidate directions to compare only after the discriminator runs:

1. a fork/restore rekey operation that regenerates daemon private identity and clears/rebinds enrollment while preserving desired workspace state;
2. rotate the persisted cmux `machine-id` when a snapshot becomes a separately tracked machine;
3. explicitly define whether registry/session ids should be copied, namespaced, or regenerated;
4. teach the control plane/provider bootstrap to distinguish resurrection of the same machine from creation of a new machine from copied storage.

The clean owner is likely the Cloud fork/restore transition, because only that layer knows whether copied state is resurrection or a new machine.

## Stop condition

Stop with a negative result if the target-native discriminator or provider semantics disproves the identity collision. Otherwise retain the narrow finding once the client consequence is executable and keep hosted clone proof as an explicit next gate.
