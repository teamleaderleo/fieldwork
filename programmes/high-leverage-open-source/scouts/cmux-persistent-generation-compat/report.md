# cmux persistent-generation compatibility scout

Date: 2026-09-01  
State: `investigating`  
Worker: `chatgpt:gpt-5.6-sol`  
Programme: `high-leverage-open-source` / Fieldwork issue #114  
Assignment: Fieldwork issue #927  
Target: `manaflow-ai/cmux`  
Target hub: none registered in `targets/hubs.yml` at claim time  
Fieldwork base revision: `ad3745069e186190a65f032bbccae7f91ac2f2f4`  
Initial target source revision: `8ef183f1e5de765b183aec9d1799f17a0848ae84`  
Current tested target revision: `eaa899cb20bd411019744fbd2bdedeb397f3070b` (`main`, resolved 2026-09-01 17:27:07Z)  
Owned output path: `programmes/high-leverage-open-source/scouts/cmux-persistent-generation-compat/`  
Owned branch: `scout/cmux-persistent-generation-compat-20260901`  
Claim scope: compatibility, recovery, persistent-state lifecycle  
Upstream contact authorized: `false`

## In simple words

I tested one of the hardest replacement boundaries in current cmux-tui: the daemon dies while a terminal host survives independently and a durably receipted terminal operation sits between “started” and “finished.”

Terminal creation handles this well. A replacement daemon can adopt the same surviving host and shell and converge the same creation correlation to one terminal.

Generic terminal input has a different contract. If `terminal.input.write` reaches durable `executing` and the daemon dies before completion is recorded, restart changes that receipt to `indeterminate` and permanently rejects exact replay under the same key. I can deterministically produce two different external realities behind that identical recovered state:

```text
same durable pre-crash state
  resource_effect_receipt = executing
  input success journal = absent

         ┌── host never consumed input ──> restart: indeterminate
crash ───┤
         └── host consumed input once ──> restart: indeterminate
```

That is an explicit fail-closed resource-API policy, so I am not calling the existence of `indeterminate` itself a compatibility defect. The decision-relevant gap is narrower: after daemon replacement, cmux has no owner-side witness tying one logical input receipt to PTY delivery, so its documented “inspect state, then retry with a new key” recovery cannot generally establish whether a new key will duplicate an outside-world action.

This is a real persistent-generation/recovery boundary. It does not yet justify a registry-only patch. The smallest owner capable of adding stronger evidence is the independently surviving terminal host / PTY-input boundary.

## Exact source and binary evidence

Pinned current upstream `main` before the dynamic pass:

`manaflow-ai/cmux@eaa899cb20bd411019744fbd2bdedeb397f3070b`

Commit message: `fix(cmux-tui): harden socket start lock files (#11396)`.

Dynamic tests used the unmodified x86_64 Linux `cmux-tui` GitHub Actions artifact produced for that exact SHA. Published artifact ZIP digest:

`sha256:5777f0684b90fee55bf4b4ea7d142ec3c3aee9d33d0275076e8c29cc63ba0ab4`

Runtime `identify` reported the same build commit. No target source was modified for these tests.

Relevant source owners at the tested SHA:

- `cmux-tui/crates/cmux-tui-core/src/workspace_registry/effect_store.rs`
  - durable effect and creation receipts;
  - startup recovery converts uncorrelated `executing` effects to `indeterminate`;
  - committed transient-input receipts receive bounded completion ordering.
- `cmux-tui/crates/cmux-tui-core/src/resource_router/content.rs`
  - `terminal.input.write` executes `surface.write_bytes(...)` and only then commits success without resource changes.
- `cmux-tui/crates/cmux-tui-core/src/terminal_host_protocol.rs`
  - persistent terminal-host data plane;
  - targeted acknowledgements exist for resize, clear-history, cell size, terminate and detach;
  - ordinary `Input` is a separate message kind with no corresponding receipt identity or durable delivery acknowledgement.
- `cmux-tui/crates/cmux-tui-core/src/mux/resource_topology.rs`
  - correlated terminal creation recovery and survivor settlement.
- `cmux-tui/spec/resource-api-v2.md`
  - interrupted external effects deliberately fail closed as `mutation.indeterminate`;
  - recovery tells the caller to inspect state and retry with a new key.
- `cmux-tui/spec/terminal-host.md`
  - terminal host, incarnation, discovery and launch/adoption contract;
  - protocol-v4 launch activation barrier;
  - exit sidecar and replacement-daemon adoption.

## Persisted-state / owner map

| State or effect | Durable owner | Survives daemon death? | Replacement evidence |
| --- | --- | --- | --- |
| workspace/resource topology | SQLite workspace registry | yes | generation + revision + resource rows |
| resource effect identity | `resource_effect_receipts` | yes | key, operation, fingerprint, intent, state |
| correlated creation identity | `resource_creation_receipts` | yes | correlation, attempt, execution generation, created path |
| resource-effect journal outcome | session journal | yes | succeeded / failed / indeterminate record |
| terminal host process | terminal-host process | yes in tested local path | discovery record + PID + terminal incarnation + owner token |
| PTY child | terminal host | yes while host survives | host snapshot / process identity |
| terminal exit | host sidecar + registry settlement | yes | terminal + incarnation + exit outcome |
| one logical terminal input delivery | terminal host / PTY boundary | external effect survives | no per-input durable witness observed |

## Strongest tested invariant

For one exact `terminal.input.write` identity, daemon replacement should be able to distinguish enough external reality to avoid both duplicate delivery and permanent poisoning when the owner can prove the effect did not happen.

The tested implementation preserves safety against automatic duplicate replay by making interrupted generic effects indeterminate. It does not preserve the stronger liveness/reconciliation half for terminal input because the replacement daemon cannot determine whether the surviving host delivered that particular logical input.

## Deterministic discriminator

The fault injection uses only process signals, an external SQLite writer lock, and test child behavior. No target patch or timing lottery is required.

1. Start exact upstream binary against a fresh state root.
2. Create a workspace and a terminal whose child enters raw mode and records an external marker only after it consumes its first byte.
3. `SIGSTOP` the independently surviving terminal-host process.
4. Submit a large receipted `terminal.input.write` under `idempotency_key=input-key`; the host stop creates deterministic socket backpressure while the registry can durably enter `executing`.
5. Independently inspect SQLite until the effect row is `executing`. Confirm no input success journal record exists.
6. Branch the experiment at the owner boundary:
   - **pre-effect:** kill the daemon while the host remains stopped;
   - **post-effect:** hold SQLite with `BEGIN IMMEDIATE`, resume the host, wait for the child’s external marker, freeze and kill the daemon before completion can commit.
7. Restart the exact same cmux binary against the same state root.
8. Replay the exact same input key, operation, selectors and payload.

The two branches recover to the same durable state and same replay error even though external reality differs.

## Raw outcome matrix

| Phase / case | Registry at crash | External reality | Restart | Exact replay |
| --- | --- | --- | --- | --- |
| before effect | `executing` | child consumed zero bytes | `indeterminate` | permanent `mutation.indeterminate` |
| after effect, before completion | `executing` | child consumed `X` exactly once | `indeterminate` | same permanent error |
| after durable completion | `committed` | child consumed `X` exactly once | remains committed | `replayed:true`, no second byte |
| interrupted correlated terminal creation | creation + effect `executing` | host and shell alive | replacement adopts same host | original creation replays, one shell |

Representative pre-effect evidence:

```text
before-effect PREPARED
effect_receipt ('executing', None, None)
journal_count 0
effect_file False

post-kill:
host_alive True
child_alive True
effect_file False
```

Representative post-effect evidence before daemon death:

```text
effect_receipt ('executing', None, None)
journal_count 0
EXTERNAL_EFFECT_OBSERVED b'X'
```

Both restarts return:

```text
code: mutation.indeterminate
idempotency_key: input-key
operation: terminal.input.write
recovery: inspect_state_then_retry_with_new_key
retryable: false
```

The recovered journal contains the indeterminate recovery record rather than a success record.

## Short-lived child cross-check

A second child consumes `X` and exits immediately with status 0. Before daemon death:

```text
external marker = b'X'
effect receipt = executing
input success journal count = 0
child alive = false
terminal-host .exit sidecar = present
```

After restart, cmux correctly reconciles the terminal lifecycle to `exited` with exit code 0 and preserves its terminal incarnation. The input receipt nevertheless remains `indeterminate`, and same-key replay remains rejected.

This narrows the missing fact: the replacement knows the terminal incarnation’s final lifecycle, but no durable evidence binds that lifecycle to the specific input receipt.

## Positive control: correlated terminal creation

Terminal creation is the important counterexample. I killed the daemon after the terminal-host process and shell existed while both creation/effect receipts were still `executing` and the `workspace.run` success journal record was absent.

Replacement behavior:

- same terminal-host PID survived;
- same terminal incarnation survived;
- same shell survived;
- replacement daemon adopted that host;
- correlation settled to one `created` result;
- exact replay returned the original result with `replayed:true`;
- exactly one live shell remained.

Outcome: **A — survivor adoption converges to one logical result.**

This shows current cmux already uses an owner-side recovery witness where the lifecycle justifies it.

## Completed-input control

When the original daemon reaches durable completion before death:

- effect receipt is `committed`;
- transient-input completion row exists;
- one success journal record exists;
- child marker is one byte;
- terminal host PID and incarnation survive daemon replacement;
- exact replay returns `replayed:true`;
- child marker remains one byte.

This rules out replay machinery itself as the cause.

## Hook external-delivery contrast

Journal hooks deliberately use a different contract. I killed the daemon after hook attempt 1 produced an external file effect while the hook child survived. Replacement started attempt 2 for the same source event, so a deliberately non-idempotent external sink observed two writes.

That is **B at process/external-file level**, but it matches the documented hook contract: exactly-once scheduling plus at-least-once process execution. Both attempts receive the same stable hook/event/correlation identity so a conforming downstream can deduplicate.

This contrast is useful because it distinguishes delegated downstream idempotency from cmux-owned terminal input delivery. The terminal host is cmux’s own independently surviving effect owner.

## Browser/provider boundary checked

`tab.create_browser` in a headless cmux-tui daemon creates durable browser topology but does not itself launch a Chromium owner. The browser projection remains `starting` / external until a browser provider appears. Browser-provider target leases are intentionally process-scoped and non-durable to avoid reconnecting a durable tab to an unrelated future target.

I therefore did not treat headless browser creation as a comparable independent-survivor effect. Browser input/navigation and sidebar effects still share the generic effect receipt machinery in source, but I did not dynamically upgrade the terminal-input result to those owners.

## Competing explanation and contract check

Current behavior is deliberate at the resource-API layer: an interrupted external effect returns non-retryable `mutation.indeterminate`, and callers are instructed to inspect state and use a new key.

That contract protects against blind duplicate execution. Therefore these experiments do **not** establish that recovery should automatically retry `terminal.input.write`.

The remaining problem under the stronger invariant is that generic state inspection cannot always determine whether PTY input already triggered an independent action. Retrying with a new key can duplicate it; refusing forever under the old key can strand an operation that definitely never reached the PTY.

## Consequence

The same ambiguity applies to tiny terminal writes; the multi-megabyte payload exists only to make the phase deterministic.

A receipted input can contain a shell command, approval, REPL mutation or agent instruction whose downstream consequence lives outside cmux. After daemon death in the demonstrated window, cmux preserves enough state to avoid automatic duplication but not enough to tell an orchestrator whether a fresh-key retry is safe.

The practical failure is therefore a liveness-versus-duplication fork at the daemon/terminal-host ownership boundary.

## Smallest repair owner

For the semantic claim “these bytes were delivered once to this terminal incarnation,” the smallest owner that can establish the missing fact is the persistent terminal host / PTY-input boundary.

The SQLite registry sits before and after that boundary. A registry-only policy cannot distinguish the two demonstrated worlds:

```text
world C: executing + effect absent
world E: executing + effect present
```

Blind retry converts C into progress while risking duplicate E. Blind commit preserves E while dropping C. Stronger reconciliation would need owner evidence capable of distinguishing them.

For semantic effects beyond PTY delivery, such as whether a shell command committed an API mutation, the downstream application remains the authoritative owner.

## Transition interpretation for this scout

This is a same-binary daemon-generation replacement result, not a binary-upgrade schema migration result.

| Transition | Result |
| --- | --- |
| same binary, clean reopen | compatible in tested controls |
| same binary, live terminal host adoption | compatible for correlated creation |
| same binary, committed terminal input | compatible and replay-safe |
| same binary, interrupted terminal input | explicit fail-closed indeterminacy; external reality unreconciled |
| same binary, short-lived child + durable exit | terminal lifecycle reconciles; input identity remains indeterminate |
| older/newer binary schema pairs | unexecuted in this update |
| rollback against copied newer state | unexecuted in this update |
| cloud compute destruction/resurrection | unexecuted in this update |

## Evidence labels

- exact current target source and contracts: `source-read`;
- exact published Linux binary: `target artifact`;
- daemon/host/PTY fault sequences: `target-executed` against exact upstream artifact;
- SQLite rows, host PID/incarnation, process/file markers and journal rows: `observed` independent oracles;
- cross-owner interpretation for browser/sidebar/remote paths: `source-read` or `Unknown` as stated;
- proposed owner boundary: `inferred` from the proven indistinguishable states and owner capabilities.

## Evidence boundary

Executed dynamically:

- Linux x86_64;
- exact current upstream artifact at `eaa899cb...`;
- local persistent terminal hosts;
- long-lived and immediately exiting PTY children;
- crash before delivery, after observed delivery and after durable completion;
- exact same-key replay;
- daemon generation replacement;
- correlated terminal creation recovery;
- one journal-hook at-least-once contrast.

Not executed:

- macOS;
- real remote/cloud provider transitions;
- binary A -> B schema migration;
- B -> A rollback;
- remote PTY over relay/provider paths;
- real browser/CDP owner recovery;
- simultaneous terminal-host death.

## Current disposition

Retain this as a consequential recovery finding inside #927. It establishes one daemon-generation transition where the system safely fails closed yet cannot reconcile external reality strongly enough to satisfy an exactly-once-plus-progress invariant for terminal input.

A registry-only implementation is unsupported by the evidence. A target-native terminal-host protocol experiment is justified if the programme chooses to promote this branch: add an owner-side discriminator for one logical input identity, then prove before-effect, after-effect, completed replay and replacement-incarnation behavior without widening the claim to downstream shell semantics.

The broader binary-upgrade / rollback matrix remains open if #927 is intended to answer compatibility beyond this proven daemon-generation boundary.

Third-party upstream remained read-only. No upstream issue, pull request, comment, review, reaction or other mutation was made.
