# Codex upstream drift and overlap ledger

Owner: lane J, Fieldwork #239  
Evidence class: source-read plus owned workflow states named below  
Retrieval date: 2026-07-31  
Current read-only upstream pin: `a01a2d91461a57809e944de7758477b92617ab01`  
Upstream contact authorized: `false`

## In simple words

Codex changes quickly. A candidate that fit last night's code may collide with today's files, may already be implemented upstream, or may still solve a missing rule at a new location.

This ledger compares exact upstream revisions with each Fieldwork source candidate. The classification answers two separate questions:

1. **Mechanical relation** — will the old patch apply cleanly?
2. **Semantic relation** — does current Codex already enforce the intended behavior?

A patch can conflict mechanically while remaining useful in meaning. Terminal retention currently has that classification.

## Pin history

| Pin | Relevant change | Convergence consequence |
| --- | --- | --- |
| `b545c94041017d000e2c8b2f6272705d21b85dfb` | Earlier execution base for deferred loader, MCP, terminal, and append candidates | Historical exact receipts remain valid at this pin |
| `acd540f1581bf30f963fccbcce43ac494102242c` | Precomputed app-server protocol exports | Expired current-source claims and triggered the first reset review |
| `97576b1794872e342450ebd577123e052ab57626` | Code Mode moved exclusively through the standalone host | Direct overlap with deferred discovery and request-authority placement |
| `e6cfd40c3f444aadd6017c9eeab01db70f48961a` | Connector candidates exposed during external-agent detection | Adds capability-discovery context; active source fences remain unchanged |
| `745603a5a1eb48b6f343633d622eeb72dd549d7b` | Passthrough metadata ignored during rollout-item reconciliation | Enters history/replay review; append acknowledgement and typed persistence outcome remain open |
| `a01a2d91461a57809e944de7758477b92617ab01` | Executor paths preserved in read-command actions | Adds adjacent execution-provenance context; declared active candidate source fences remain unchanged |

## Important upstream prior changes in the current ancestry

### Streaming output deque conversion

Commit `789c72dcf62d7439863d4d2846454f05b3d51db6` changes unified-exec output buffering from `Vec` to `VecDeque`, consumes valid UTF-8 prefixes through error offsets, and adds invalid-byte progress controls.

Overlap:

- same files as the historical terminal-retention candidate;
- real mechanical conflict;
- useful current behavior that every restack must preserve;
- no producer-owned completion retention before best-effort broadcast.

Classification: **mechanically conflicting, semantically complementary**.

### Logical websocket trace after prewarm

Commit `20fedafff83f5c681fc62f73b0ca3227e42e3f8b` records the logical request when a generated websocket call reuses an untraced warmup response.

Overlap:

- same startup-prewarm neighborhood as the Responses Lite investigation;
- solves rollout-trace replay of the logical request;
- leaves capability-manifest retransmission and executable authority as separate questions.

Classification: **partial adjacent absorption; source residue remains**.

### Responses Lite input-item tools

Commit `33cc928d339307795d4f5987337c7c4607f70338` places Responses Lite tools in `additional_tools` input items and a developer item.

Overlap:

- defines the capability prefix whose first generated transmission is under study;
- strengthens the need to distinguish prewarm connection reuse from model-visible capability delivery;
- does not answer Code Mode host authority or loader execution.

Classification: **upstream prerequisite and contract context**.

### Standalone Code Mode host

Commit `97576b1794872e342450ebd577123e052ab57626` moves Code Mode execution exclusively through its standalone host.

Overlap:

- changes the owning boundary for deferred discovery and executable loader policy;
- invalidates a source-placement-only restack of the older candidate;
- does not establish that every direct tool has an executable path or that deferred metadata matches host capability.

Classification: **mechanically and architecturally changed; semantic residue remains**.

### Rollout passthrough-metadata normalization

Commit `745603a5a1eb48b6f343633d622eeb72dd549d7b` ignores passthrough metadata during rollout-item reconciliation and adds focused reducer tests.

Overlap:

- enters logical item equality and replay normalization;
- can reduce false divergence caused by transport metadata;
- does not report whether a live append persisted;
- does not classify prewrite failure versus commit-then-error acknowledgement loss;
- does not establish retry or compaction authority for an ambiguous result.

Classification: **adjacent history absorption; append-outcome residue remains**.

### Executor paths in read-command actions

Commit `a01a2d91461a57809e944de7758477b92617ab01` preserves executor paths in app-server command-action records and updates protocol schemas, item builders, path-URI handling, and focused tests.

Overlap:

- adds adjacent provenance for environment-backed read actions;
- touches none of the declared append, terminal, MCP runtime, request-construction, or Code Mode host source fences;
- does not settle operation effect, result persistence, runtime-generation binding, or transcript retention.

Classification: **adjacent execution-provenance context; active candidate classifications unchanged**.

## Candidate ledger

| Candidate | Historical source head | Current class | Strongest current conclusion | Exact next action |
| --- | --- | --- | --- | --- |
| Deferred executable loader, owned Codex #45 | `e8d14cd1e4e26f3963f318ceb9f7f7493df32eba` | architectural conflict; semantic residue | Direct exposure still needs an executable authority path; Code Mode host migration changes placement | Redesign against standalone host and current request construction before restack |
| Host MCP reconnect, owned Codex #46 | `eb39c46b4bd0e115aa3e0acece50a19e803a37a4` | semantically complementary; current-source review pending | Explicit host refresh freshness remains distinct from ordinary runtime-config reuse | Re-read current manager call path and compare exact behavior with current upstream explicit-refresh reconnect |
| MCP generation publication, owned Codex #48 | `af8d348408e4ab7a00f2423503f9862359063357` | semantically complementary; current-source review pending | Current drift does not establish newest-generation-only publication or result identity | Restack the generation gate after current runtime ownership review |
| Terminal producer-owned retention, owned Codex #49 | `7db66fe3f235df77c36a9db521677e23379bcac5` | mechanically conflicting, semantically complementary | Upstream deque work improves decoding while retained completion still depends on the producer boundary | Execute and review carrier #53, preserving the deque behavior |
| Append acknowledgement prerequisite, owned Codex #51 | `30a0a9b50da5fd2f7d58ee81315e0311e84e221e` | clean semantic residue; current execution pending | Current session code still logs append failure without returning an outcome | Execute and review carrier #52, then branch typed persistence state separately |
| Responses Lite first generated capability prefix, historical owned Codex #23 work | carrier-only historical work | policy plausible; production source held | Trace repair and manifest delivery are different questions; full Code Mode test hits default worker stack limits | Build a lower-level exact-prefix and retry fixture before production candidate |
| MCP timeout outcome separation, Fieldwork #134/#162 | experiment and report set | complementary to current source | Caller timeout, cancellation delivery, transport state, and remote effect require separate facts | Design manager-owned generation-checked retirement without mutation replay |

## Current execution carriers

### Append outcome carrier #52

- branch: `fieldwork/83-direct-append-carrier-20260731`;
- head: `324ddccba14b2b0934e2c56cc0cda7ca04a56e6d`;
- intended source branch: `fieldwork/83-append-outcome-upstream-97576b`;
- authoritative workflow: `30582576317`;
- state at retrieval: `queued`;
- base: `97576b1794872e342450ebd577123e052ab57626`.

Current upstream is three commits ahead. The external-agent connector and executor-path changes leave the three-file source fence untouched. The rollout reconciliation change is adjacent and requires post-publication review; it does not replace the append outcome.

### Terminal retention carrier #53

- branch: `fieldwork/23-terminal-acd540-restack-carrier`;
- head: `d5028fc9771407aa7a9bafbceb7eba051b91de36`;
- intended source branch: `fieldwork/23-terminal-97576-source`;
- authoritative workflow: `30582012412`;
- state at retrieval: `queued`;
- base: `97576b1794872e342450ebd577123e052ab57626`.

The three newer upstream commits leave the terminal four-file fence unchanged. A successful source publication can therefore be compared directly to current head for an exact no-overlap confirmation, followed by independent complete-diff review.

## Classification vocabulary

- **absorbed** — current upstream enforces the intended invariant with adequate evidence;
- **cleanly portable** — the bounded source applies without material ownership change;
- **mechanically conflicting** — overlapping code prevents direct application;
- **semantically conflicting** — current architecture or contract rejects the proposed invariant;
- **complementary** — current upstream changed adjacent behavior while leaving the invariant open;
- **obsolete** — the premise, target boundary, or delivery value expired;
- **historical evidence only** — exact past execution remains useful while current-source claims have expired.

## Current conclusion

No active bounded candidate in this ledger is fully absorbed by current upstream.

Two candidates are in exact execution-carrier validation. Two MCP candidates remain semantically complementary and need current-source comparison or restacks. Deferred discovery requires redesign at the standalone host boundary. The Responses Lite source idea needs a smaller production-representative fixture before a source candidate. Timeout outcome work remains a separate operation-lifecycle proposal.

Every `current`, `portable`, or `proposal-ready` claim must use `a01a2d91461a57809e944de7758477b92617ab01` or a newer explicitly recorded head.