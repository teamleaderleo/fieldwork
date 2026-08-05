# Codex upstream drift and overlap ledger

Owner: lane J/I, Fieldwork #239  
Parent canonical finding: [`F239`](../../../findings/F239-codex-upstream-convergence/finding.md)  
Evidence class: source-read plus exact owned workflow state  
Retrieval date: 2026-07-31  
Current read-only upstream pin: `3016671bb077c43448b8fa88f3edfa9772e17058`  
Upstream contact authorized: `no`

## In simple words

Codex changes quickly. A candidate that fit an older source tree may conflict with current files, may have been absorbed upstream, or may still solve a missing rule at a new owner.

This ledger separates:

1. **mechanical relation** — whether historical source applies cleanly;
2. **semantic relation** — whether current Codex already enforces the intended invariant;
3. **evidence relation** — whether the current exact carrier has executed and produced a reviewable source successor.

A candidate can conflict mechanically and remain useful semantically. Historical green tests remain historical evidence; they do not make a candidate current.

## Pin history

| Pin | Relevant change | Convergence consequence |
| --- | --- | --- |
| `b545c94041017d000e2c8b2f6272705d21b85dfb` | Earlier execution base for deferred loader, MCP, terminal, and append candidates | Historical exact receipts remain valid only at this pin |
| `97576b1794872e342450ebd577123e052ab57626` | Code Mode moved exclusively through the standalone host | Historical deferred-authority source placement became obsolete |
| `745603a5a1eb48b6f343633d622eeb72dd549d7b` | Rollout reconciliation ignores passthrough metadata | Adjacent history/replay improvement; append acknowledgement remains open |
| `a01a2d91461a57809e944de7758477b92617ab01` | Read-command actions preserve executor paths | Adjacent execution-provenance context |
| `3016671bb077c43448b8fa88f3edfa9772e17058` | Enterprise automation account-plan support | Current head; one-commit delta from `a01a2d...` does not overlap declared active source fences |

## Current-head delta

The complete `a01a2d... → 3016671...` compare changes:

- account plan and authentication types;
- rate-limit payloads and app-server schemas;
- backend-client behavior;
- login, cloud-config, protocol, and status tests;
- TUI status presentation.

It does not touch the declared current fences for:

- session append acknowledgement;
- ThreadStore in-memory controls;
- unified-exec process and async watcher retention;
- MCP runtime manager and reconnect paths;
- request construction or standalone Code Mode host authority.

Classification: **no active-fence overlap; prior candidate classifications carry forward to `3016671...` for those paths**.

## Important prior changes in the current ancestry

### Streaming output deque conversion

Commit `789c72dcf62d7439863d4d2846454f05b3d51db6` replaces repeated front-shifting with `VecDeque`, advances through invalid UTF-8, and adds focused controls.

Classification: **mechanically conflicting, semantically complementary** to producer-owned completion retention. Every terminal restack must preserve this behavior.

### Responses Lite logical trace and capability prefix

Commit `20fedafff83f5c681fc62f73b0ca3227e42e3f8b` repairs logical websocket tracing after untraced prewarm. Commit `33cc928d339307795d4f5987337c7c4607f70338` carries Responses Lite tools in input items.

Classification: **trace repair and capability-delivery prerequisite**. Neither proves the first generated request transmitted the complete capability prefix or that executable host authority matched it.

### Standalone Code Mode host

Commit `97576b1794872e342450ebd577123e052ab57626` moves execution exclusively to the standalone host.

Classification: **architectural conflict with historical placement; semantic executable-authority invariant remains**.

### Rollout passthrough-metadata normalization

Commit `745603a5a1eb48b6f343633d622eeb72dd549d7b` reduces false history divergence caused by passthrough metadata.

Classification: **adjacent history absorption**. It does not report original append acknowledgement or distinguish prewrite failure from commit-then-error ambiguity.

### Executor path preservation

Commit `a01a2d91461a57809e944de7758477b92617ab01` preserves executor paths in public read-command actions.

Classification: **adjacent provenance precedent**. It does not settle runtime generation, remote effects, result persistence, or terminal retention.

## Candidate ledger

| Candidate | Historical source identity | Current classification | Strongest current conclusion | Exact next action |
| --- | --- | --- | --- | --- |
| Deferred executable authority, owned #45 | `e8d14cd1e4e26f3963f318ceb9f7f7493df32eba` | architectural conflict; semantic residue | Every model-visible direct/deferred tool still needs matching executable authority, but standalone host owns the current boundary | Map host declaration, loader, dispatch, collision identity, and request prefix before new source |
| Host MCP reconnect, owned #46 | `eb39c46b4bd0e115aa3e0acece50a19e803a37a4` | partial overlap; current comparison pending | Explicit freshness remains distinct from ordinary unchanged reuse | Compare exact manager call paths and tests with upstream #34952/#35151 |
| MCP generation publication, owned #48 | `af8d348408e4ab7a00f2423503f9862359063357` | complementary; current comparison pending | Current source does not yet prove newest-eligible-generation publication or accepted-result identity | Restack only after manager ownership map |
| Terminal producer retention, owned #49/#53 | historical source `7db66fe3f235df77c36a9db521677e23379bcac5`; carrier `#53@c4e0de2e54d804d1054afb90c30b7150a774151c` | mechanically conflicting, semantically complementary, executing | Current deque and lifecycle ordering remain valuable; producer-owned retained completion still has bounded residue | Inspect run `30585540688`, then review four-file source successor |
| Append acknowledgement, owned #51/#80 | reviewed source `30a0a9b50da5fd2f7d58ee81315e0311e84e221e`; carrier `#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc` | clean semantic residue, current-pin execution pending | Session still needs caller-visible canonical append acknowledgement | Inspect run `30583967538`, review source-only successor, then split typed ambiguity state |
| Responses Lite first generated capability prefix | historical carrier-only work | plausible contract; production source held | Trace reconstruction and capability transmission are separate; default-stack failure requires smaller fixture | Build lower-level exact-prefix and failed-first-generated retry controls |
| MCP timeout outcome separation, #134/#162 | executed experiment/report set | complementary operation model | Caller deadline, cancellation delivery, transport, and remote effect are separate facts | Design manager-owned generation-checked retirement; prohibit mutation replay while unknown |

## Current execution carriers

### Current-pin append carrier #80

- branch: `fieldwork/83-append-outcome-carrier-a01a2d`;
- exact head: `401c2e5e6a37730aae3e8da95591cc6f56655cfc`;
- base: `a01a2d91461a57809e944de7758477b92617ab01`;
- intended source branch: `fieldwork/83-append-outcome-a01a2d`;
- authoritative workflow: `30583967538`;
- state at this retrieval: `queued`;
- source fence: `codex-rs/core/src/session/mod.rs`, `codex-rs/core/src/session/turn_tests.rs`, `codex-rs/thread-store/src/in_memory.rs`.

Historical carrier #52 remains a retained exact-pin record. It is superseded by #80 for current-source promotion and should retire only after #80 supplies a valid successor or retained failure.

### Terminal retention carrier #53

- branch: `fieldwork/23-terminal-acd540-restack-carrier`;
- exact head: `c4e0de2e54d804d1054afb90c30b7150a774151c`;
- base: `97576b1794872e342450ebd577123e052ab57626`;
- intended source branch: `fieldwork/23-terminal-97576-source`;
- authoritative workflow: `30585540688`;
- state at this retrieval: `pending`;
- source fence: `process.rs`, `process_tests.rs`, `async_watcher.rs`, `async_watcher_tests.rs` under unified execution.

The public delta from the carrier base through `3016671...` leaves the four-file terminal fence unchanged. A published source successor still requires direct current-head compare and complete-diff review.

## Classification vocabulary

- **absorbed** — current source enforces the intended invariant with adequate evidence;
- **cleanly portable** — bounded source applies without material ownership change;
- **mechanically conflicting** — overlapping source prevents direct application;
- **semantically conflicting** — current architecture rejects the proposed invariant;
- **complementary** — current source changed adjacent behavior while leaving the invariant open;
- **obsolete** — premise, owner, or delivery value expired;
- **historical evidence only** — exact past execution remains useful while present-tense claims expired.

## Current conclusion

No active bounded candidate in this ledger is fully absorbed by current Codex.

Append acknowledgement and terminal retention are in exact carrier execution. MCP reconnect and generation publication need current manager comparison. Deferred executable authority needs a new standalone-host source map. Responses Lite needs a smaller capability-prefix fixture. Timeout outcome work remains a separate operation-lifecycle finding.

Every `current`, `portable`, `conflict-free`, or `proposal-ready` claim must use `3016671bb077c43448b8fa88f3edfa9772e17058` or a newer explicitly reviewed head.
