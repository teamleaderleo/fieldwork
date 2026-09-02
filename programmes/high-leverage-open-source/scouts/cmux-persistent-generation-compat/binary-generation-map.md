# cmux binary-generation and persistent-state compatibility map

Date: 2026-09-01  
Programme: `high-leverage-open-source` / #114  
Scout: #927  
Owned branch: `scout/cmux-persistent-generation-compat-20260901`  
Upstream: `manaflow-ai/cmux` read-only  
Disposition: source map complete; one same-binary daemon-generation failure boundary is target-executed; exact cross-binary carrier is prepared and queued without an execution receipt

## Executive result

The highest-consequence current cmux persistent formats mostly carry explicit compatibility boundaries:

- the cmux-tui workspace registry is a forward-migrated SQLite database with a read-only newer-schema preflight and transactional schema-version advancement;
- remote authorization has a dedicated on-disk authorization version and explicit rollback fencing;
- remembered remote daemons are keyed by daemon public-key fingerprint, and reconnect refuses a changed daemon key;
- the app/daemon remote protocol requires an exact supported protocol match before connect;
- macOS session restore has an exact snapshot schema fence plus a retained previous snapshot;
- cloud providers keep the daemon binary, daemon identity, enrolled devices, workspace registry, and user home on persistent home storage while compute is disposable, so resurrection is an ordinary binary-replacement boundary;
- durable terminal hosts survive mux-daemon death and therefore create a second generation axis independent from the registry schema.

No cross-binary corruption is proven in this pass. The exact-binary A/B carrier is admitted to the owned fork workflow and remains queued, so its evidence class stays `target-test-prepared`.

One consequential daemon-generation failure is already proven and retained in `report.md` plus the `input-*` artifacts: interrupted `terminal.input.write` converges to the same durable `indeterminate` state whether the surviving terminal host consumed the bytes or consumed zero bytes. That policy prevents automatic duplicate replay, yet it cannot tell an orchestrator whether a fresh-key retry duplicates an outside-world action. Correlated terminal creation is the positive control: replacement adopts the same host and converges to one logical creation.

## Exact revision set

| Role | Revision | Why it is here |
| --- | --- | --- |
| assignment-time current main | `8ef183f1e5de765b183aec9d1799f17a0848ae84` | resolved and pinned before this binary-generation investigation |
| exact dynamically executed artifact | `eaa899cb20bd411019744fbd2bdedeb397f3070b` | target-executed daemon/host/input crash campaign retained in `report.md`; ancestor of the assignment pin by six commits |
| latest release | `v0.64.22` = `ddd4a01bc5d8ebac19643930f5fd7d40e85f1534` | released-build A for prepared schema rollback probe |
| prior release | `v0.64.21` = `33ac210ab4cc36642749701cbc3d3fec30af0934` | confirms current authorization schema v2 is already present in adjacent release |
| earlier release | `v0.64.20` = `14e3400b95daedd652d0b6f395d0777c41e39eef` | predates the current `cmux-remote` persisted-auth owner in the inspected tree |
| terminal-host A | `ae830c381bb846609230fc155a7fcdcd5e06b4d0` | workspace schema 13, terminal-host protocol 3, host-record version 2 |
| terminal-host B | `a23c328f58738e58f692ef7e0e23ec5c194cf383` | direct child boundary: workspace schema 13, terminal-host protocol 4, host-record version 2 |
| additive-column A | `c4d7ee75205b01ddac887e5cd0c80bda83972281` | old terminal-host registry writer |
| additive-column B | `c5e2c64b704ae4ed0ebdc5140a4a4e003da8bcff` | adds `terminal_hosts.on_exit` without bumping outer workspace schema |

`eaa899cb...` -> `8ef183f1...` is six commits. The inspected diff between those exact coordinates touches cmux-tui app/UI files, while the persistent owners used by the executed input discriminator stay outside that delta. Execution remains attributed only to `eaa899cb...`.

## Persisted-state map

| Durable state | Physical owner / format | Generation owner | Primary version fence | Recovery / identity key |
| --- | --- | --- | --- | --- |
| workspace and resource topology | `workspace-registry.sqlite3` | cmux-tui mux | `SCHEMA_VERSION=14` at assignment pin; `8` in v0.64.22 | registry id, generation, revisions, resource ids |
| session journal / resource effects | registry tables + per-record schemas | cmux-tui resource API | outer registry schema + journal/effect schema fields | event/correlation/idempotency identity; required-vs-observation replay policy |
| resource-effect receipt pepper | sibling `resource-effect-pepper` plus registry meta | cmux-tui resource API | pepper schema 7 + `resource_effect_pepper_id` + cleanup-pending marker | DB meta ties sidecar to the registry generation |
| terminal-host discovery | persistent terminal-host JSON records | independent terminal-host process | host-record version 4 current; older inspected pair version 2 | terminal id + incarnation + endpoint + owner token + PID/start identity |
| terminal exit | `.exit` sidecar + registry settlement | terminal host then mux | exit sidecar version + terminal incarnation | deletion acts as acknowledgement after equivalent durable settlement |
| live PTY/parser/replay | terminal-host process memory + child process | independent host process | terminal-host wire protocol | terminal id + incarnation + negotiated protocol |
| daemon static identity | remote state `identity.json` | cmux-remote daemon | identity `STATE_VERSION=1` | public-key fingerprint |
| enrolled/revoked devices | remote auth state `devices.json` | cmux-remote daemon | `AUTH_STATE_VERSION=2` | device id/fingerprint + auth revision/lifecycle fences |
| client static identity | `client-identity.json` | cmux-remote client | `STATE_VERSION=1` | client public-key fingerprint |
| remembered daemons/routes | `known-daemons.json` | cmux-remote client | `STATE_VERSION=1` | daemon public-key fingerprint; route hints are attached to that pin |
| local per-cloud-VM enrollment memory | `~/.cmuxterm/vm-tui-devices.json` | macOS app/CLI | JSON model, atomic 0600 save | provider + VM id -> device fingerprint |
| macOS session restore | Application Support session snapshot + `-previous` | app | `SessionSnapshotSchema.currentVersion=1` | window/workspace/pane ids + optional remote projection records |
| remote projection restore | persisted `SurfaceProjectionRecord` | app surface catalog | snapshot schema + exact resource identity | cloud machine id + resource kind + provider key |
| cloud persistent machine state | provider persistent `/root` home for Blaxel | provider + cmux bootstrap | binary manifest commit/SHA + all format fences above | logical VM id + persistent volume contents |

## Version / generation owners

### Workspace registry

At `8ef183f1...`, the registry owns schema 14. The history comments record meaningful version boundaries, including independently shipped schema-9 journal/multiview variants and a schema-11 normalization that probes the actual tables/indexes instead of trusting the outer number alone. This is the right response to a generation number that once represented more than one physical layout.

Existing databases receive a read-only unsupported-schema preflight before writable open. Newer-schema refusal therefore has an explicit chance to occur before migration writes. The current migration path performs data migration and the `schema_version` update inside the same SQLite transaction. A process interruption between migration statements and commit rolls the transaction back as one unit.

The registry is one logical generation with one important sidecar exception: the resource-effect pepper. Current code stores a pepper id and a cleanup-pending marker in SQLite. Sensitive-receipt cleanup is marked pending before the external cleanup phase; the marker is cleared only after the cleanup/checkpoint path succeeds. That is a multi-file recovery protocol instead of an unmarked half-generation.

### Remote identity / enrollment

Current and v0.64.21/v0.64.22 source own authorization schema 2. The code comment states that v2 fences binaries that understand only original v1 state. Current loading distinguishes missing, legacy, current, and unsupported authorization schemas. Legacy migration is explicit. Current-only startup refuses unsupported state.

The August 1 remote hardening lineage contains dedicated rollback-fence and preflight-before-mutation work for authorization/lifecycle state. The current owner also serializes atomic JSON persistence and drains queued authorization persistence during shutdown.

Daemon identity and authorization are separate durable files but one trust generation in practice: a client remembers the daemon public key, while the daemon remembers authorized device keys. A replacement that preserves both keeps enrollment. Loss or replacement of daemon identity creates a new public-key fingerprint; a remembered client rejects the key change. Loss of `devices.json` while daemon identity survives causes the provider control plane to see the client fingerprint as unenrolled and mint a fresh invitation.

### Client / daemon remote protocol

The inspected current and v0.64.22 remote protocol version is 5. macOS cmux-tui integration probes the client and daemon before connect and requires matching remote-protocol compatibility, reporting stale-client / stale-daemon errors instead of entering an incompatible session.

The remote daemon specification also distinguishes installation modes: release/nightly bootstrap can install an exact verified daemon build; source/raw/PyPI paths require a matching preinstalled remote binary. Embedded or mux-owned daemons have bounded upgrade rules. Silent substitution is outside the stated contract.

### Terminal-host protocol

The terminal host is a durable local binary data-plane owner separate from the JSON mux control plane. Current protocol is v4 and current host-record version is 4. The host owns the PTY, child, parser and replay state; mux daemons can die and be replaced while the host remains alive.

The cleanest historical cross-generation discriminator is `ae830c381...` -> `a23c328f...`: both use workspace schema 13 and host-record version 2, while the terminal-host protocol changes 3 -> 4. B adds launch-activation semantics. Because the outer database schema is constant, any rollback failure in this pair points at the live-host generation boundary instead of the registry migration fence.

### macOS local restore

The app session snapshot uses schema version 1. A snapshot whose version differs from current is treated as unusable. The repository keeps a previous snapshot; an unusable primary does not overwrite that recovery copy. Remote surface projections are restored by exact machine/resource identity and remain pending until the matching remote resource reappears. This favors stale/pending state over rebinding a pane to a fresh unrelated remote resource.

## Support / compatibility contract

1. **Supported forward registry upgrade:** migrate in SQLite transactions. If the target generation cannot interpret the database, refuse before writable migration where the newer-schema preflight applies.
2. **Released-build rollback after a registry bump:** an older schema owner may deliberately refuse the newer database. That refusal is a valid rollback contract when retained bytes stay untouched and a pre-upgrade copy or newer binary remains available.
3. **Authorization rollback:** schema v2 is an explicit fence against v1-only binaries; unsupported authorization state is a refusal boundary.
4. **Remote reconnect:** daemon identity is cryptographically pinned. A changed daemon key under the same route/logical machine is an identity change and connection fails until explicit re-enrollment/re-pinning.
5. **Remote client/daemon binary skew:** protocol compatibility is checked before session use. A stale generation is surfaced as an incompatibility instead of a fresh hidden session.
6. **Terminal-host replacement:** a surviving host is a peer generation with its own protocol. Adoption must either negotiate/validate the same host incarnation or leave it recoverable. Reaping/recreating the terminal as a silent fallback would violate the scout invariant.
7. **Session restore:** exact snapshot schema + retained previous snapshot; restored remote projections wait for the same resource identity.
8. **Generic external effects:** interrupted `executing` effects recover as explicit `indeterminate`; automatic same-key replay is refused. The executed terminal-input result shows the limit of this generic contract when the independently surviving owner lacks a per-effect witness.

## What survives each replacement boundary

Legend: `yes` = durable by design/source or executed control; `conditional` = survives when the stated owner persists and version fence accepts it; `process lost` = files may survive but live process state ends; `external` = lives outside the replaced process.

| State | app restart | daemon restart | binary upgrade | binary downgrade | cloud compute destruction / resurrection | rollback to prior release |
| --- | --- | --- | --- | --- | --- | --- |
| macOS session snapshot | yes | yes | conditional on snapshot schema | conditional on snapshot schema / previous copy | local state unaffected | conditional on schema |
| remote projection ids | yes | yes | yes if resource identity survives | yes if resource identity survives | conditional on same VM/resource ids | conditional on same remote resource ids |
| client identity + known daemons | yes | yes | conditional on state version | conditional on state version | local state unaffected | conditional on state version |
| local VM -> device fingerprint map | yes | yes | yes in inspected format | yes in inspected format | yes; daemon may require a fresh invitation | yes |
| daemon identity | yes | yes | conditional on identity format | conditional on identity format | yes on persistent `/root` | yes if release accepts identity format |
| enrolled devices / auth | yes | yes | conditional on auth fence | explicit fence when unsupported | yes on persistent `/root` | v0.64.21/22/current share auth v2 |
| workspace registry | yes | yes | forward migration | older schema may refuse | yes on persistent `/root` | prior release accepts only its supported schema |
| pepper sidecar + cleanup marker | yes | yes | recovery protocol spans DB + sidecar | conditional on older understanding | yes on persistent `/root` | conditional on schema generation |
| terminal-host records / exit sidecars | yes | yes | conditional on host-record/protocol readers | conditional | files survive persistent home; liveness resolves dead after compute loss | conditional |
| live terminal host / PTY child | remote app restart: yes | **yes, target-executed** for same-binary mux death | conditional on replacing mux's host protocol compatibility | conditional on rollback protocol compatibility | **process lost** | conditional if old mux can adopt newer surviving host |
| remote workspace/resource journal | yes | yes | conditional on registry/journal schemas | fail/refuse when required schemas unsupported | yes on persistent `/root` | conditional on supported schema |
| outside-world side effects already caused by terminal input | external | external | external | external | external | external |

## Transition matrix

| Sequence | Evidence | Result / current classification |
| --- | --- | --- |
| exact artifact A -> A clean reopen | target-executed controls in `report.md` | compatible for tested local state |
| same binary, mux death with correlated terminal creation executing | target-executed | replacement adopts same host/incarnation and replay converges to one creation |
| same binary, completed receipted terminal input | target-executed | committed receipt replays without second delivery |
| same binary, interrupted input before host consumption | target-executed | restart converts `executing` to `indeterminate`; same key refuses |
| same binary, interrupted input after host consumption before completion commit | target-executed | same durable recovered state and same refusal; external world differs |
| c4d7 old writer -> c5e2 additive `on_exit` -> c4d7 writer | model-executed exact SQL | clean compatibility: B `keep` survives old update; old insert receives `close` default |
| v0.64.22 schema 8 -> pinned main schema 14 | source-read + target-test-prepared | supported forward migration expected; exact binary receipt queued |
| pinned main schema 14 -> v0.64.22 on disposable copy | source-read + target-test-prepared | deliberate newer-schema refusal expected; mutation-before-refusal is the defect discriminator |
| protocol-3 mux A -> protocol-4 host/mux B -> kill B mux -> restore A | source-read + target-test-prepared | highest-value live-host rollback test; exact execution queued |
| protocol-4 host state after A touch -> restore B | target-test-prepared | must recover same terminal or surface explicit recoverable incompatibility |
| remembered client -> same logical cloud VM after compute resurrection | source-read | daemon identity/devices survive persistent home; client reconnect keeps same pin when volume is intact |
| remembered client -> same logical VM with replaced daemon identity | source-read | client rejects changed daemon key; explicit enrollment/re-pin is recovery |
| older bundled client -> newer daemon protocol mismatch | source-read | compatibility check surfaces stale-client / stale-daemon before session use |
| app local restore -> remote resource reappears | source-read | projection waits for exact machine/resource id instead of binding an unrelated resource |

## Migration interruption analysis

### SQLite registry

The outer schema number is updated in the same SQLite transaction as the migrations that justify it. That closes the classic `version advanced / data half-migrated` window for database-local changes.

Schema history also contains an explicit lesson from a previous version collision: code probes table/index reality when a single version number had represented independently shipped variants. This reduces reliance on a misleading number alone.

### Registry + pepper sidecar

The pepper migration crosses SQLite and a sibling file. Current code records the pepper id and a cleanup-pending state in SQLite, performs cleanup/checkpoint work, then clears the marker. Interruption therefore leaves durable evidence that cleanup remains owed.

### Remote identity + authorization + lifecycle

The current code has separate daemon identity and authorization files plus lifecycle evidence. The hardening lineage explicitly added rollback fencing and recovery preflight before authorization mutation. This is the format family where several files collectively represent one trust generation; current code treats rollback recovery as an owned protocol instead of silently recreating state.

### Terminal host + registry

Registry rows and host JSON/exit sidecars collectively represent one live terminal generation. A surviving host can outlive mux death. The executed creation control proves the replacement can reconcile one such split generation. Generic terminal input lacks the same per-operation owner witness, producing the proven indeterminate boundary in `report.md`.

## Strongest distinguishing sequences

### Proven: same-binary daemon generation, input effect boundary

Retained dynamic sequence:

```text
A daemon writes durable effect receipt = executing
-> independent terminal host remains alive
-> branch C: host consumes zero bytes
-> branch E: host consumes bytes once
-> A daemon dies before completion record
-> same binary starts as replacement generation
-> both branches recover to the same indeterminate receipt
-> exact same-key replay refuses in both branches
```

The durable cmux state is identical across two different external realities. This proves the replacement generation lacks an owner witness for one logical terminal-input delivery. The system chooses duplicate-prevention via fail-closed indeterminacy; progress may require a fresh key whose safety cannot be inferred from cmux state alone.

### Prepared: protocol-only rollback across a surviving terminal host

```text
A = protocol 3 / registry schema 13
B = protocol 4 / registry schema 13
B creates durable terminal + live host
-> kill only B mux
-> host process and PTY remain alive
-> restore A against same state
-> inspect same terminal id, host record, registry bytes and host liveness
-> kill A
-> restore B against A-touched state
```

Distinguishing outcomes:

- clean compatibility: A adopts the same host safely;
- explicit incompatibility: A refuses before mutating host/registry state and B can recover;
- failure: A rewrites/removes host metadata, terminates/replaces the host, creates a fresh terminal that hides the old one, or leaves B unable to recover the original terminal.

This pair is especially strong because both sides own workspace schema 13. The protocol generation is the main changed compatibility coordinate.

### Prepared: released-build registry rollback

```text
v0.64.22 creates schema-8 state
-> pinned main opens and migrates to schema 14
-> copy migrated state
-> v0.64.22 attempts open on copy
-> compare every file/hash/meta row before and after refusal
-> pinned main reopens the refused copy
```

A clean old-binary refusal is expected and acceptable. Mutation before refusal, fresh-state fallback, partial migration, or failure of B to recover the refused copy would be the consequential defect.

## Negative controls

- same exact binary reopen and committed replay controls from the retained target-executed input campaign;
- correlated terminal creation: same surviving host/incarnation converges to one logical creation after daemon death;
- completed terminal input: one external byte remains one byte after exact replay;
- additive `terminal_hosts.on_exit` old-writer model: B-only `keep` value survives A update; A insert receives B's declared default; SQLite integrity is `ok`;
- current source regression for newer workspace schema refusal;
- fresh-B registry state and A->A / A->B / B->A byte comparison are encoded in the queued owned-fork carrier.

## Cloud resurrection analysis

Blaxel explicitly treats the root filesystem as disposable while `/root` is the persistent machine home. The daemon binary lives under that persistent home, and daemon identity/enrolled-device state also lives there. Workspace state and user files therefore survive compute destruction when the persistent volume survives.

Resurrection can still become a generation change. Bootstrap resolves a daemon manifest, verifies the persistent binary hash, downloads a replacement to a temporary path when needed, verifies SHA, and atomically installs it before daemon start. The logical cloud VM can remain the same while the daemon binary generation changes against older durable state.

Live terminal-host processes and PTYs die with compute. Their records remain on the volume and must be reconciled as dead/stale by the resurrected daemon. Client trust remains tied to the persisted daemon key. If the volume instead loses daemon identity, the old client pin detects the new key and refuses; provider enrollment is the explicit recovery path.

This makes a provider resurrection experiment one of the highest-value next branches: pin two exact daemon manifests, retain one persistent home, destroy/recreate compute between them, and inspect `identity.json`, `devices.json`, workspace-registry metadata, terminal-host records and client pins before/after.

## Practical consequence

The current design prevents several dangerous silent-fresh-state paths:

- newer workspace schemas have an explicit refusal owner;
- changed daemon identity trips the client key pin;
- remote protocol skew is surfaced before session use;
- restored remote projections wait for exact resource identity;
- generic interrupted effects are retained as indeterminate instead of being blindly replayed.

The proven weak point is narrower and consequential: a daemon generation can inherit a surviving terminal whose external PTY input reality cannot be reconstructed from the durable idempotency receipt. The replacement therefore faces a progress-versus-duplicate decision after interruption.

The main unresolved cross-binary risk is the independently versioned live terminal host. A rollback can keep the same workspace schema while changing the only mux protocol that can adopt an already-running PTY owner.

## Repair boundary

No upstream patch is justified from the queued binary-transition carrier alone.

For the proven terminal-input ambiguity, the smallest owner capable of distinguishing `delivered` from `never delivered` is the persistent terminal-host / PTY-input boundary. A registry-only change sees the same `executing` receipt in both demonstrated worlds.

For a future cross-binary host rollback failure, the repair owner depends on the observed outcome:

- mutation before protocol refusal -> adoption/startup preflight owner;
- stale host record rewritten or removed -> terminal-host record/reconciliation owner;
- old mux binds a fresh terminal while old host survives -> terminal identity/projection owner;
- protocol mismatch with untouched bytes and B recovery -> deliberate rollback contract, no defect;
- provider resurrection loses daemon identity despite intact persistent home -> bootstrap/state-root owner;
- client accepts a changed daemon key under same logical VM -> client trust/pinning owner.

## Evidence limits

### Target-executed

- exact upstream Linux x86_64 artifact `eaa899cb20bd411019744fbd2bdedeb397f3070b`;
- mux kill with live terminal-host survivor;
- interrupted generic terminal input before delivery and after observed delivery;
- committed-input replay control;
- correlated terminal-creation recovery control;
- short-lived child/exit reconciliation;
- journal-hook contrast.

### Model-executed

- exact SQLite additive-column old-writer compatibility for `c4d7ee...` -> `c5e2c64...` -> old writer.

### Source-read

- assignment pin `8ef183f1...` registry/auth/remote/terminal-host/cloud/session-restore owners;
- v0.64.22/v0.64.21 released schemas;
- remote protocol and key-pinning contract;
- Blaxel persistent-home and bootstrap replacement path;
- macOS snapshot backup/version fence and remote projection identity.

### Target-test-prepared only

Owned-fork workflow run `33544120861`, head `40013d90654d86f9561ad3bf00272655525f467b`:

- v0.64.22 schema-8 -> pinned-main schema-14 upgrade and copied rollback;
- protocol-3 mux -> protocol-4 surviving host -> protocol-3 rollback -> protocol-4 recovery.

Latest retained observation: both intended jobs are queued. Workflow admission proves platform state only; no target execution claim is drawn from it.

### Unexecuted

- macOS binary A/B restore;
- real cloud provider destroy/resurrect on one retained volume;
- released binary downgrade after a completed schema-14 migration;
- remote client A / daemon B mismatch using real independently installed binaries;
- interruption during the SQLite+pepper cleanup phase;
- downgrade from current auth state to a genuinely v1-only remote daemon generation;
- provider volume loss / daemon-key replacement recovery end-to-end.

## Ranked next branches

1. **Execute the protocol-3/protocol-4 live-host rollback carrier.** Same DB schema removes the largest confounder and directly tests silent terminal replacement, record mutation, and B recoverability.
2. **Execute v0.64.22 -> pinned-main -> v0.64.22 copied registry rollback.** Require a byte-identical old-binary refusal and successful B reopen.
3. **Cloud persistent-home resurrection with two pinned daemon manifests.** Preserve VM/home identity, replace compute and binary generation, inspect daemon key/devices/registry/host records/client pin.
4. **Auth-v1 boundary archaeology and executable pair.** Find the last exact v1-only daemon revision, create v1 auth/enrollment state, upgrade to v2, interrupt at each durable fence, then restore v1 on a copy.
5. **Pepper cleanup interruption.** Kill between cleanup-pending commit, sidecar cleanup/checkpoint, and marker clear; reopen old/new generations on copies and inspect receipts/pepper id.
6. **Old bundled client against newer independently installed daemon.** Exercise protocol mismatch, daemon key persistence, and enrollment preservation with exact binary revisions.
7. **macOS session snapshot rollback.** Create remote projection state with one app generation, restore with another, verify `-previous` fallback and exact remote resource identity after remote daemon replacement.

## Retained artifacts

- `report.md` — target-executed daemon-generation finding and controls.
- `artifacts/input-boundary-evidence.txt` — raw terminal-input boundary evidence.
- `artifacts/input-controls-evidence.txt` — raw positive/negative controls.
- `artifacts/test_input_effect_boundary.py` — retained execution harness.
- `artifacts/test_input_controls.py` — retained control harness.
- `artifacts/on-exit-old-writer-model.txt` — exact SQL additive-column compatibility control.
- `artifacts/binary-transition-carrier.txt` — exact owned-fork carrier head/run/revisions and queued status.

Third-party upstream remained read-only. No upstream issue, pull request, branch, comment, review, reaction, or patch was created or changed.
