# Codex portfolio convergence at `97576b1794872e342450ebd577123e052ab57626`

Status: active convergence packet  
Owner: Fieldwork #239 lane O  
Fieldwork base: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`  
Owned Codex main observed: `f7265553ea1510304f3091833dcbce65ef21f10c`  
Public Codex head reviewed: `97576b1794872e342450ebd577123e052ab57626`  
Reset pin: `acd540f1581bf30f963fccbcce43ac494102242c`  
Shared source-set merge base: `b545c94041017d000e2c8b2f6272705d21b85dfb`  
Public upstream interaction authorized: `false`

## Purpose

This packet treats the owned Codex work as one portfolio. It records the current authority carrier, exact source relation, complete-diff boundary, execution receipt, upstream overlap, remaining residue, proposal text, and retirement decision for every source or diagnostic lineage opened through owned Codex PR #55.

The authority order used here is:

1. exact current-upstream source-only head with an exact-head receipt;
2. exact current-upstream source-only head awaiting execution;
3. historical source-only head with valid historical execution and an explicit current restack plan;
4. completed diagnostic or execution receipt;
5. superseded, polluted, failed, or mixed carrier retained only as history.

A workflow carrier never outranks the source head it applies or publishes. A larger-stack pass is diagnostic evidence. It never becomes the production contract.

## Upstream movement and overlap

`b545c94041017d000e2c8b2f6272705d21b85dfb..97576b1794872e342450ebd577123e052ab57626` is an exact 16-commit ancestor chain. `97576b...` is one commit after reset pin `acd540...`.

The 16-commit delta changes these portfolio seams:

- `codex-rs/core/src/codex_thread.rs`;
- `codex-rs/core/src/session/mod.rs` and `session/turn.rs`;
- unified-exec watcher, process, and tests;
- Code Mode host selection and fallback;
- tool registry and MCP handler paths;
- thread-history paths.

The delta leaves these reviewed candidate files untouched:

- `codex-rs/core/src/tools/spec_plan.rs` and `spec_plan_tests.rs`;
- `codex-rs/codex-mcp/src/runtime.rs`;
- `codex-rs/thread-store/src/in_memory.rs` in the relevant candidate comparison.

File disjointness supports mechanical portability. It never replaces current-head execution when semantics moved nearby.

## Current convergence table

| Lane | Authority class | Owned PR / exact head | Complete diff | Exact validation | Upstream relation | Residue and disposition |
| --- | --- | --- | --- | --- | --- | --- |
| Deferred discovery | current source | #54 `2b9fd0fc597965341a1a9c61559b67135ed0a49d` | exactly `spec_plan.rs`, `spec_plan_tests.rs` | #55 `0f50a5612a2b4d471de2be35512540222d6673b3`; exact run active at packet creation | parent is exact `97576b...`; clean restack of #45 | best current source; proposal eligible only after #55 completes and receipt transfers |
| Deferred discovery history | historical source | #45 `e8d14cd1e4e26f3963f318ceb9f7f7493df32eba` | same two files | #47 run `30560341515`, job `90931415852`, `FIELDWORK_DEFERRED_EXACT=4/4` | one candidate commit, 16 commits behind current; file-disjoint but Code Mode semantics moved | retire after #54/#55 replacement receipt is complete |
| MCP explicit reconnect | historical source | #46 `eb39c46b4bd0e115aa3e0acece50a19e803a37a4` | `codex_thread.rs`, `mcp_tool_exposure.rs` | historical exact reconnect/reuse `2/2` at 16 MiB; default integration worker overflows | upstream also changed `codex_thread.rs` | hand-restack on exact current head; retain captured reconnect/reuse contract; proposal blocked on current exact source and execution |
| MCP publication | historical source | #48 `af8d348408e4ab7a00f2423503f9862359063357` | `codex-mcp/src/runtime.rs` only | historical exact publication controls `5/5` | file-disjoint from 16-commit delta | cleanly portable; rerun on exact current source and add slow-A/fast-B fixture before proposal-ready |
| Append acknowledgement | historical source plus active execution | #51 `30a0a9b50da5fd2f7d58ee81315e0311e84e221e`; #52 carrier `ec78830e3d6f67454b56900427c683a2da7bc29b` | `session/mod.rs`, `session/turn_tests.rs`, `thread-store/in_memory.rs` | historical `FIELDWORK_APPEND_OUTCOME_EXACT=4/4`; thread-store `158/158`; current run active | upstream changed `session/mod.rs`; old transformer failed on a stale `session/turn.rs` anchor | #52 now applies the reviewed three-file patch with `git apply --3way`; current source publication and exact receipt required |
| Terminal retention | historical source plus active execution | #49 `7db66fe3f235df77c36a9db521677e23379bcac5`; #53 carrier `600bba1f556d63a75f4fdecd6217c2bab9f458ec` | `unified_exec/process.rs`, `process_tests.rs`, `async_watcher.rs`, `async_watcher_tests.rs` | historical exact `3/3`; repaired current carrier active | explicit conflicts in `async_watcher.rs` and `process_tests.rs`; semantics complementary to upstream VecDeque and invalid-UTF-8 work | repaired carrier resolves exact conflicts, preserves upstream controls, removes test-only visibility widening, runs nine exact controls plus focused `codex-core`; current source publication required |
| Responses Lite | diagnostic only | #23 `d1045ae0001444549a4905715e7962e14c2ae163` | mixed branch, 58 commits ahead and 154 behind current, with temporary workflows and unrelated receipt files | lower-level controls passed; full exact regression exits 101 on default worker and passes at 16 MiB | ancient merge base `20dafe201d91d4405eef05ecd1db0257f13a9ac8`; no source-only head | no proposal carrier; split transport source from shared stack defect, add failed-first-request retry control, then publish a clean head |
| Direct result persistence history | historical mixed source | #32 `a0ab863c8d9f90fd9bd284cc6b31049e2579da51` | three Rust files across a ten-commit owned-main lineage | historical focused `7/7` and in-memory `3/3` | based on owned fork main, predates #51 and current public head | keep only as receipt-semantics evidence; rebuild the typed persistence slice on the current append-acknowledgement source |
| Authority fallback / admission | cross-review repair | Fieldwork #251 `17d4fc3dd17e0f7a37516aa38a8767eca9ade591` | five Fieldwork files | three exact workflows passed | owned integration, not public Codex source | complete-diff review found incomplete authority inputs can admit a mutation fallback; disposition REPAIR |

## Exact execution receipts and failures

### Deferred discovery

Historical source #45 passed four exact controls:

- `deferred_extension_is_direct_when_search_is_unavailable`;
- `deferred_runtime_without_search_metadata_is_direct`;
- `code_mode_keeps_unsearchable_deferred_runtime_registered`;
- `mcp_and_tool_search_follow_direct_and_deferred_tool_exposure`.

Run `30560341515`, job `90931415852`, marker `FIELDWORK_DEFERRED_EXACT=4/4`. The new #54 source is directly parented by current upstream and #55 verifies the two-file fence, formatting, the same four exact controls, and the current standalone-host optional-Code-Mode fallback.

### Append acknowledgement

Historical #51 passed four exact append-outcome controls and all 158 thread-store tests. The first #52 attempt, run `30560746088` / job `90932794178`, failed before tests with:

```text
codex-rs/core/src/session/turn.rs: expected one anchor, found 0
```

The repaired #52 head uses the reviewed three-file patch and exact current upstream. A prior in-progress run was cancelled while installing test runners; a newer run owns the current receipt.

### Terminal retention

The first #53 run failed during cherry-pick before tests. The second repaired run resolved the exact two conflicts and produced the exact four-file source fence, then failed because `just` was unavailable. The current #53 head adds the repository CI setup action and owns the next run.

The intended exact terminal/deque controls are:

- `local_output_task_retains_stdout_before_best_effort_broadcast`;
- `local_output_task_retains_invalid_utf8_when_broadcast_lags`;
- `completed_item_includes_output_emitted_before_subscription`;
- `reconcile_transcript_replaces_partial_stream_with_authoritative_output`;
- `split_valid_utf8_prefix_respects_max_bytes_for_ascii`;
- `split_valid_utf8_prefix_avoids_splitting_utf8_codepoints`;
- `split_valid_utf8_prefix_makes_progress_on_invalid_utf8`;
- `split_valid_utf8_prefix_consumes_all_valid_bytes_before_invalid_utf8`;
- `split_invalid_utf8_advances_without_shifting_remaining_bytes`.

### Responses Lite stack probe

Run `30560549409`, job `90932120547`, exact test:

```text
suite::agent_websocket::websocket_first_responses_lite_turn_sends_full_manifest_after_startup_prewarm
```

The boxed `new_turn_with_sub_id` future entered and still overflowed the default stack. The identical test passed at 16 MiB. Marker:

```text
FIELDWORK_BOXED_NEW_TURN=default:101;large:0
```

This rejects the await-boundary boxing hypothesis and leaves the source candidate unresolved.

## Proposal packets

These are owned draft packets only. They authorize no public upstream contact.

### Packet A — deferred discovery

**Proposed title**

```text
core: expose deferred tools when no executable loader exists
```

**Problem**

A runtime marked deferred becomes unreachable when the effective request mode has no executable loader for that runtime. Current upstream contains lazy tool-search registration, including public PR #25211, but that machinery is dormant until a loader exists.

**Change**

At final tool exposure normalization, promote a deferred runtime to direct when the effective mode is Direct and either request search is unavailable or the runtime has no searchable metadata. Keep searchable deferred runtimes deferred. Keep available Code Mode and Code Mode Only runtimes registered for their catalogue.

**Evidence required**

- exact source #54 at `2b9fd0fc597965341a1a9c61559b67135ed0a49d`;
- exact two-file complete diff;
- four exact planner controls;
- current standalone-host optional-Code-Mode fallback control;
- formatting and patch hygiene;
- no exposure changes outside final normalization.

**Tradeoff**

The direct surface grows only for tools that would otherwise lack an executable route. Searchable deferred tools preserve deferred discovery. Code Mode keeps catalogue ownership when its host is available.

**Best carrier**

#54 after #55 receipt transfer. Retire #45 and #55 after the source receipt is durable.

### Packet B — explicit MCP reconnect

**Proposed title**

```text
core: reconnect MCP clients on explicit host config reload
```

**Problem**

A host-requested MCP config refresh is a freshness boundary, while ordinary unchanged runtime reconciliation should reuse a healthy client.

**Change**

Mark the ready MCP runtime for reconnection before applying host-refreshed MCP config. Keep ordinary unchanged runtime refresh on the reuse path.

**Evidence required**

- exact current-upstream source-only restack of #46;
- complete two-file diff and explicit resolution of current `codex_thread.rs` overlap;
- exact reconnect and unchanged-config reuse controls;
- default-stack classification kept separate from behavior;
- no claim of newest-generation publication or authority continuity.

**Tradeoff**

This adds a bounded freshness primitive. It does not arbitrate overlapping publication and should stay separate from Packet C.

**Best carrier**

A new source-only successor to #46 on exact current upstream. Retire #46 after replacement receipt transfer.

### Packet C — newest MCP publication

**Proposed title**

```text
mcp: publish only the newest accepted refresh generation
```

**Problem**

Overlapping refreshes can finish out of order. An older candidate can otherwise publish after a newer request, and a fresh caller can receive a catalogue from a candidate that lost publication.

**Change**

Give each refresh a monotonic generation and freshness epoch. Permit only the newest requested generation at the current epoch to store its snapshot and open its publication gate. Carry unresolved freshness across overlapping candidates until an accepted fresh publication settles it. Report superseded fresh replacement instead of returning an unaccepted catalogue.

**Evidence required**

- exact current-upstream one-file source head;
- existing five exact state/gate controls;
- end-to-end slow-A/fast-B server fixture;
- accepted fresh-result identity control;
- complete one-file diff and formatting.

**Tradeoff**

Prepared and active calls retain their captured runtime. This packet governs future publication only and leaves authority fingerprint comparison and typed timeout outcomes to Campaign #84/#134/#162.

**Best carrier**

Current-head successor to #48. Retire #48 after replacement receipt transfer.

### Packet D — rollout append acknowledgement

**Proposed title**

```text
core: propagate rollout append outcomes
```

**Problem**

Conversation recording discarded the result of rollout append attempts. The session caller could not distinguish success, pre-write failure, or commit-then-error acknowledgement loss.

**Change**

Propagate append success or failure through the live session boundary and add deterministic in-memory controls for pre-write failure and commit-then-error acknowledgement loss.

**Evidence required**

- clean current source published by #52;
- exact three-file complete diff;
- four exact append-outcome controls;
- complete thread-store package;
- formatting, patch hygiene, and ordinary in-memory behavior;
- explicit boundary: acknowledgement only, with no retry authorization or typed persistence settlement.

**Tradeoff**

The caller gains authoritative append acknowledgement while durable effect can remain ambiguous after commit-then-error. That ambiguity is the required input for later receipt policy.

**Best carrier**

The source-only branch published by repaired #52. Retire #51 and #52 after independent review and receipt transfer.

### Packet E — terminal transcript retention

**Proposed title**

```text
core: retain terminal output before best-effort delivery
```

**Problem**

Terminal completion depended on a later best-effort subscriber. Output emitted before subscription or skipped by a lagging subscriber could disappear from the completed command item.

**Change**

Keep a producer-owned completion buffer, record local output before best-effort broadcast, retain exec-server gap-recovered output before downstream delivery, and reconcile the authoritative retained transcript into terminal completion after output closes.

**Evidence required**

- clean current source published by repaired #53;
- exact four-file complete diff;
- all nine exact terminal/deque controls;
- focused `codex-core` target gate;
- preservation of upstream VecDeque and invalid-UTF-8 behavior;
- no test-only visibility widening;
- explicit retained-window boundary, with no remote-settlement claim.

**Tradeoff**

Completion becomes independent of a loss-prone live subscriber within each transport's retained window. Live deltas remain best-effort. Memory remains bounded by the existing head/tail buffer contract.

**Best carrier**

The source-only branch published by repaired #53. Retire #49 and #53 after independent review and receipt transfer.

## Prior-art and duplicate search

Read-only public Codex PR search found:

- #25211, lazy tool-search registration, directly adjacent to Packet A. It supplies loader-driven lazy registration and remains dormant without a loader. Packet A covers the unreachable deferred-runtime case when the effective mode has no executable loader.
- #25018, thread deletion, and #11227, extended history persistence, adjacent to durable history but outside Packet D's append-acknowledgement boundary.

Searches for the exact MCP generation/publication terms, unified-exec broadcast-retention terms, and Responses Lite prewarm terms returned no matching PR. Search absence is a search result, never proof that no related work exists. A public proposal would require one final current search and maintainer-facing overlap statement.

## Cross-lane meta-analysis

### Campaign #83 — mutation identity and persistence

The append-outcome prerequisite is the correct first current slice. Typed `Persisted/Ambiguous` receipt state must build on that exact source. Automatic retry remains unauthorized. Commit-then-error is durable-effect ambiguity, not a failed mutation fact.

### Campaign #84 — MCP lifecycle

Reconnect and publication remain separate primitives. A complete lifecycle proposal needs newest-generation publication, captured-call runtime identity, authority fingerprint comparison before cached-A/live-B execution, typed cancellation and timeout outcomes, and resume/fork reconstruction. Current #46/#48 are bounded components, not a complete repair.

### Campaign #85 — request exposure and Responses Lite

Deferred discovery has a viable current source in #54. Responses Lite has no source carrier. The boxed-future probe rejects one mitigation and confirms a shared stack-pressure defect downstream of entering `new_turn_with_sub_id`. Transport behavior and the stack defect need separate source heads.

### Campaign #86 — authority fallback

Fallback selection must consume typed absence and execution-certainty facts from #83/#84/#85. Fieldwork #251 currently allows incomplete authority evidence to classify as equal or narrower. The admission boundary must require complete binding generations, strict reversibility where applicable, and a trusted complete authority comparison.

### MCP timeout lanes #134 and #162

Cancellation delivery and remote terminal certainty remain separate. `LocalTimeoutOutcomeUnknown` and related typed facts should cross the generic tool-output boundary into the receipt owner before any fallback or replay decision. Packet B/C must preserve operation lineage for calls captured under an older runtime generation.

### Tool/process lane #23

Packet E improves transcript retention only. Process-tree shutdown, sandbox partial-output behavior, remote settlement, cancellation, and replay safety remain distinct work.

## Retirement ledger through owned Codex #55

### Retired-authoritative merged foundation

Owned Codex #2, #3, #9, #12, #16, #18, #19, #20, and #21 are merged foundation on owned main. Their behavior may supply experiments and prerequisites, while their individual PRs no longer compete as proposal carriers.

### Retired historical or failed carriers

Owned Codex #1, #4, #7, #8, #10, #11, #13, #14, #15, #17, #22, #24, #25, #26, #27, #28, #29, #30, #31, #35, #36, #37, #38, #39, #40, #41, #42, and #50 are closed historical, failed, or diagnostic carriers with evidence transferred to campaign records.

### Retired in this convergence pass

- #5: superseded by #46;
- #6: superseded by #49 and current carrier #53;
- #33: superseded by #46;
- #34: superseded by #48;
- #43: completed boxed-future diagnostic;
- #44: superseded append execution predecessor;
- #47: completed exact-review carrier for #45.

### Open with current authority or residue

- #23: mixed Responses Lite diagnostic; no source authority;
- #32: historical direct-result-persistence evidence; rebuild after current append acknowledgement;
- #45: historical deferred source, superseded when #54/#55 receipt is complete;
- #46: historical reconnect source requiring current restack;
- #48: historical publication source requiring current execution and fixture;
- #49: historical terminal source retained until #53 publishes a reviewed successor;
- #51: historical append source retained until #52 publishes a reviewed successor;
- #52: active current append execution carrier;
- #53: active current terminal execution carrier;
- #54: exact current deferred-discovery source;
- #55: active exact-current receipt carrier for #54.

## Coordination receipt

During this pass, #52 was closed from a stale snapshot that referenced its failed earlier head. The mutation response exposed a newer repaired head and body. #52 was immediately reopened before any source authority was lost. The current exact head and active run now govern its disposition. This incident reinforces the exact-head rule: refresh the PR head immediately before every retirement mutation.

## Final gate

No candidate is public-proposal-ready until all of these hold on a freshly inspected public head:

1. exact source head and parent recorded;
2. complete diff reviewed;
3. intended exact tests resolve uniquely and execute;
4. broader focused target gate has a stated outcome;
5. upstream overlap and nearby semantic movement classified;
6. prior-art search refreshed;
7. proposal text names its bounded contract and exclusions;
8. stale source and execution carriers are retired after receipt transfer;
9. public upstream interaction remains separately authorized.
