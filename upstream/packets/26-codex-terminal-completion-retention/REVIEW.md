# Review record

## Review state

- Review type: packet-owner self-review
- Independent review: pending
- Current disposition: **REPAIR**
- Public-upstream contact: false

Self-review checks packet completeness and source isolation. It does not satisfy the independent-review gate.

## Exact source under review

- Repository: `teamleaderleo/codex`
- Branch: `fieldwork/26-terminal-completion-retention-source`
- Base: `670f69416bf91c5dfd8b58669e78050b584ff053`
- Head: `a020d7bd3e7f6886c3fbc21d75b3110586df08f5`
- Tree: `9a067c244d464e863a7b50978826ac9930df680b`
- Compare: https://github.com/teamleaderleo/codex/compare/670f69416bf91c5dfd8b58669e78050b584ff053...a020d7bd3e7f6886c3fbc21d75b3110586df08f5

The branch contains one commit and exactly four changed files. No workflow or unrelated unit file is present.

## Source provenance review

The current source uses exact blobs from Codex PR #125 live head `ee605985012dc1b768f03f6b450db16dd5c0467e`:

| File | Blob | Review result |
|---|---|---|
| `codex-rs/core/src/unified_exec/async_watcher.rs` | `a0427969dec77d57f6bc3037108cd4be26125cd0` | provenance confirmed |
| `codex-rs/core/src/unified_exec/async_watcher_tests.rs` | `57002ea930169d2815aed51e42bbb37f27faedc8` | provenance confirmed |
| `codex-rs/core/src/unified_exec/process.rs` | `ca47e90159328921a3f469fd0dad72c91ef5f86a` | provenance confirmed |
| `codex-rs/core/src/unified_exec/process_tests.rs` | `b76c9151eb9b5a42e6e6cdfe4ef4b1c0c1686f58` | provenance confirmed |

The earlier claim comment on Fieldwork issue #435 named stale source/base hashes. Live PR metadata and the newly created source branch supersede those values. The completion handoff must use the exact revisions above.

## Scope review

### Included

- producer-owned bounded stdout/stderr retention;
- retention before broadcast;
- completion reconciliation;
- invalid UTF-8 handling;
- normal EOF behavior;
- hard-termination behavior;
- focused tests in the two touched test files.

### Excluded

- skills async unified-exec contract work from Codex PR #46;
- permission matcher work from Codex PR #48;
- unrelated NVIDIA issue #197;
- unrelated Workers cleanup issue #41;
- public-upstream submission;
- carrier workflow changes in the clean source branch.

## Diff review

### `async_watcher.rs`

Review focus:

- retained bytes are appended before best-effort broadcast;
- deque truncation removes oldest bytes and respects the configured bound;
- read-loop errors and EOF propagate consistently;
- invalid UTF-8 cannot stall the loop;
- hard termination avoids waiting indefinitely for the output task.

Self-review result: design intent is visible and matches the historical test record. Independent concurrency review remains required.

### `async_watcher_tests.rs`

Review focus:

- output produced before subscription reaches final completion;
- lag and closed-receiver cases preserve retained bytes;
- invalid UTF-8 advances and remains representable;
- bounded retention is observable;
- hard termination completes promptly.

Self-review result: focused cases cover the primary failure modes. The carrier-defined nine-test list should be pinned verbatim in the next execution receipt.

### `process.rs`

Review focus:

- streamed output and retained completion output reconcile through suffix/prefix overlap;
- shared bytes appear once;
- useful streamed prefix survives retention-window eviction;
- empty and complete-overlap cases behave predictably.

Self-review result: selected algorithm matches the stated contract. Independent review should stress repeated byte patterns where several overlap lengths are possible.

### `process_tests.rs`

Review focus:

- pre-subscription completion regression;
- replacement/reconciliation of a partial streamed transcript;
- output ordering and exact equality.

Self-review result: tests directly cover the original completion-level symptom.

## Evidence review

### Accepted

- Fieldwork run `30587866332`: nine exact controls pass, full `codex-core` library gate pass, integration-target compile pass.
- Codex run `30651607704`: source guard, baseline build, and nine exact controls pass for source `ee605985...`.
- Exact four-blob restack over current public main.

### Limited

- Codex PR #6 broad run: 95/99 pass with four sandbox/network SIGABRT cases; useful prototype evidence, not a clean full gate.
- PR #125 local formatting receipt: useful formatting evidence, not target execution.

### Rejected as product evidence

- PR #53 setup failures.
- PR #94 source-consistency guard failure.
- shared-carrier setup failures before target execution.

## Risk map

| Risk | Severity | Evidence | Required follow-up |
|---|---:|---|---|
| Completion duplicates bytes at overlap boundary | high | reconciliation tests; historical focused passes | independent algorithm review; repeated-pattern cases |
| Completion truncates useful early streamed output | high | bounded-retention design and partial-stream test | current-head full tests; cap-boundary cases |
| Retention increases memory use | medium | explicit bounded deque | review cap value and per-process impact |
| Invalid UTF-8 stalls or shifts bytes | medium | helper tests and lag case | current-head exact controls |
| Normal EOF waits incorrectly | high | historical exact controls | current-head full library gate |
| Hard termination hangs after receiver closure | high | dedicated promptness case | current-head exact control and timeout receipt |
| Adjacent current-main unified-exec integration drift | medium | one adjacent integration file changed after prior base | integration-target compile on current base |
| Carrier masks a baseline failure | medium | latest broad gate failed after focused pass | paired baseline/source rerun with complete logs |
| Public submission precedes invitation | high process risk | target policy invitation-only | keep drafts private |

## Disposition rationale

**REPAIR** is the current defensible disposition.

The source has strong historical execution and a clean current-main restack. Readiness still depends on a current-head carrier run, classification of the broader gate, and independent review.

## Required independent review request

Review the exact compare `670f694...a020d7b` with emphasis on:

1. producer retention ordering relative to broadcast;
2. deque-cap semantics;
3. overlap reconciliation under repeated byte sequences;
4. invalid UTF-8 boundaries;
5. normal EOF versus hard termination;
6. whether the nine exact controls and full library/integration gates cover the modified contracts.

Record the reviewer, reviewed SHA, findings, and verdict in this file or a linked GitHub review. A review of an earlier source head does not automatically cover the current head unless blob identity and base-drift analysis are explicit.

## Handoff verdict

Continue from the current unit-owned source head. Build a separate carrier, execute paired baseline/source gates, preserve full logs and artifacts, obtain independent review, and then reassess REPAIR versus READY or HOLD.
