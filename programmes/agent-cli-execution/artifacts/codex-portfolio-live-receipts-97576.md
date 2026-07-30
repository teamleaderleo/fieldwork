# Codex portfolio live receipts from `97576b1794872e342450ebd577123e052ab57626`

Authority: this file supersedes carrier-head, live-run, and current-upstream fields in `codex-portfolio-convergence-97576.md`. The larger dossier remains the portfolio analysis and proposal packet. This ledger owns changed-head receipts, current drift, and final disposition.

Fieldwork command: #239  
Proposal owner: #260  
Dossier PR: #258  
Public upstream interaction authorized: `false`

## Current public head

The portfolio execution pin remains:

```text
97576b1794872e342450ebd577123e052ab57626
```

The latest public Codex head inspected during this pass is:

```text
a01a2d91461a57809e944de7758477b92617ab01
```

Exact relation:

```text
97576b1794872e342450ebd577123e052ab57626..a01a2d91461a57809e944de7758477b92617ab01
status: ahead
commits: 3
merge base: 97576b1794872e342450ebd577123e052ab57626
changed files: 39
```

The three commits are:

1. `e6cfd40c3f444aadd6017c9eeab01db70f48961a` — external-agent connector detection protocol;
2. `745603a5a1eb48b6f343633d622eeb72dd549d7b` — rollout-trace normalization of top-level passthrough metadata;
3. `a01a2d91461a57809e944de7758477b92617ab01` — executor-native read-action path preservation.

The delta has no direct file overlap with the deferred-discovery, MCP publication/reconnect, append-acknowledgement, terminal-retention, Responses Lite, receipt-foundation, or typed-identity source fences. It is semantically adjacent to:

- receipt identity and Responses Lite through rollout replay normalization;
- terminal delivery through app-server command-action notifications;
- MCP work through external-agent connector protocol.

Every proposal-ready/current claim at `97576b...` therefore expires. Successful `97576b...` receipts remain immutable execution evidence and require a fresh `a01a2d...` relation plus the lane-specific current-head gate before promotion.

## Complete-diff review of PR #258

PR #258 changes documentation only. The initial convergence table captured carrier heads that later moved during concurrent repairs. This ledger records the authoritative replacements.

No source or proposal contract contradiction was found in the complete documentation diff. The stale fields are historical snapshots only.

## Deferred discovery

Reviewed source #54:

```text
head: 2b9fd0fc597965341a1a9c61559b67135ed0a49d
parent: 97576b1794872e342450ebd577123e052ab57626
files: codex-rs/core/src/tools/spec_plan.rs
       codex-rs/core/src/tools/spec_plan_tests.rs
```

Completed receipt #55:

```text
carrier head: f27b14dddbb0a24ee4eab17b59f76bf8dd26e6b0
run: 30580836079
job: 91000366783
source fence: passed
format: passed
planner exact controls: 4/4 passed
FIELDWORK_DEFERRED_EXACT=4/4
FIELDWORK_CODE_MODE_FALLBACK=default:101;large:0
```

The exact fallback control was:

```text
suite::code_mode::missing_process_host_falls_back_to_direct_tools_and_warns_once
```

Default execution reached the shared worker-stack overflow. The unchanged test passed 1/1 at `RUST_MIN_STACK=16777216`. Stack enlargement remains diagnostic evidence.

Mixed-catalogue successor carrier #64:

```text
head: cf7e32ed4b0e8841680001a39a364c9b8396f3b9
run: 30582147570
status at ledger revision: queued
source target: fieldwork/239-deferred-loader-97576-v2
```

#64 adds one same-request catalogue containing a searchable deferred extension runtime and a deferred core runtime without search metadata. It resolves five unique exact planner controls, reruns fallback classification, runs the focused spec-plan gate, and publishes a two-file source-only successor after success.

Current classification: `cleanly portable from 97576b to a01a2d; exact-current execution pending`.

## Append acknowledgement

Historical reviewed source #51:

```text
30a0a9b50da5fd2f7d58ee81315e0311e84e221e
```

Authoritative carrier #52:

```text
head: 324ddccba14b2b0934e2c56cc0cda7ca04a56e6d
run: 30582576317
status at ledger revision: queued
source target: fieldwork/83-append-outcome-upstream-97576b
```

The carrier checks out the triggering event head, applies the reviewed three-file patch, resolves exactly one full name for each append-outcome control, runs four controls with `--exact`, runs complete `codex-thread-store`, verifies the source fence, and publishes only after success.

Earlier run `30560746088` / job `90932794178` failed during stale source transformation and executed zero source controls.

Current classification: `file-disjoint from a01a2d drift; mechanically portable; exact-current execution pending`.

## Receipt foundation

Authoritative carrier #56:

```text
head: f776a6483fe9fed2dd216c0ca6d00c7740e7f049
run: 30582540059
status at ledger revision: queued
source target: fieldwork/83-receipt-foundation-upstream-97576b
source fence: 19 files
```

The repaired carrier checks out the triggering event head, lists immutable library tests, resolves every full name in five owned groups, rejects duplicate package/name execution, runs each with `--exact`, and emits per-group plus total counts.

Current classification: `file-disjoint, semantically adjacent to rollout-trace replay normalization; fresh current-head receipt review required`.

## Typed operation identity

Authoritative carrier #61:

```text
head: d44040ef24ac972713c4e0b1922586dfb1b4dcc1
run: 30582772729
status at ledger revision: queued
source target: fieldwork/83-typed-identity-upstream-97576b
source fence: 20 files
```

The repaired carrier checks out the triggering event head, applies the receipt foundation and reviewed typed-identity generator, adapts current `DirectPlaintextMessage`, resolves full names for receipt-state, Code Mode identity, lifecycle, and direct-persistence groups, rejects duplicate execution, and runs every selected control with `--exact`.

Current classification: `file-disjoint, semantically adjacent to rollout-trace replay normalization; exact-current identity review required`.

## Terminal retention

Historical reviewed source #49:

```text
7db66fe3f235df77c36a9db521677e23379bcac5
```

Authoritative carrier #53:

```text
head: d5028fc9771407aa7a9bafbceb7eba051b91de36
run: 30582012412
status at ledger revision: queued
source target: fieldwork/23-terminal-97576-source
```

The workflow reconstructs the reviewed source, resolves the two known conflicts, preserves current VecDeque and invalid-UTF-8 behavior, verifies the exact four-file source fence, runs nine unique nextest names through the repository test entrypoint, runs focused `codex-core`, and publishes only after success.

Historical phase receipts:

- `30579629635` / `90996353540`: conflict before tests; zero tests;
- `30579942527` / `90997384432`: reconstruction and four-file fence passed; execution stopped because `just` was absent.

Current classification: `file-disjoint from a01a2d drift, with adjacent app-server command-action work; fresh current-head terminal review required`.

## Responses Lite

Execution-and-publication carrier #58:

```text
head: b3727359801f033f247d5b04561c022608d5cba9
run: 30581975601
status at ledger revision: queued
source target: fieldwork/239-lite-source-97576
source fence: client.rs, agent_websocket.rs, client_websockets.rs
```

The carrier proves full first generated request after untraced startup prewarm, ordinary generated-response continuation reuse, and full retry after failed first generation. The full agent control remains classified on default and 16 MiB stacks.

Current classification: `file-disjoint, semantically adjacent to rollout-trace replay normalization; published source requires independent a01a2d review`.

## MCP publication and reconnect

Current-pin source #59:

```text
head: 84b191c66d00ee95a840fb389df0b06f3558f615
file: codex-rs/codex-mcp/src/runtime.rs
v8 run: 30580767150 success
blocking run: 30580767387 in progress at ledger revision
```

Complete-diff disposition: `EXECUTE TARGET TEST`. Required residue includes slow-A/fast-B publication, superseded fresh-result identity, cancellation/progress behavior, and composition with reconnect freshness.

Current-pin source #63:

```text
head: bd6fc6634f03efffb7590b6c1954acb198cf900c
files: codex-rs/core/src/codex_thread.rs
       codex-rs/core/tests/suite/mcp_tool_exposure.rs
runs: 30581303040 and 30581303301 queued at ledger revision
```

Complete-diff disposition: `EXECUTE TARGET TEST`. Required residue is a real app-server `mcpServer/refresh` request-path control proving healthy-thread reconnect completion and strict planning failure with zero reconnect attempts.

The public drift is file-disjoint from both source fences and adds adjacent external-agent connector protocol. Both packets require refreshed prior-art and current-head execution before promotion.

## Retirement ledger

Retired in this convergence pass:

- #5, #6, #33, #34: superseded source lineages;
- #43: completed boxed-future diagnostic;
- #44: superseded append execution predecessor;
- #47: completed deferred exact-review carrier;
- #55: completed deferred receipt carrier after transfer.

Keep open until replacement source and receipts transfer:

- #45 historical deferred source;
- #46 historical reconnect source;
- #48 historical publication source;
- #49 historical terminal source;
- #51 historical append source;
- #52, #53, #56, #58, #61, #64 active execution carriers;
- #54, #59, #63 current-pin source candidates;
- #23 and #32 historical mixed evidence until clean successors absorb residue.

Refresh every PR head immediately before any closure. Execution carriers remain outside promotion and Delivery Desk D0.

## Blocked exact-head handoff fields

At this ledger revision, source publication and exact execution are blocked on the shared GitHub Actions queue. The exact blockers are queued or executing run IDs recorded above, plus public head movement from `97576b...` to `a01a2d...`.

For every completed or blocked lane, the final command handoff must record:

1. latest public upstream head inspected;
2. source branch, exact head, parent, and complete file list;
3. carrier head, workflow run, and job;
4. exact test names and count;
5. focused package gate outcome;
6. publication outcome and source branch;
7. absorption/conflict classification against `a01a2d...` or a later freshly inspected head;
8. retired carrier list;
9. proposal packet disposition;
10. public upstream interaction performed: `false`.
