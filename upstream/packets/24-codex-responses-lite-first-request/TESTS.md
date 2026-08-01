# Tests and receipts — unit 24 Responses Lite first request after prewarm

## Exact identities

### Current source

- Public-source parent: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- Candidate head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- Canonical branch: `teamleaderleo/codex:fix/responses-lite-first-request`
- Canonical draft PR: `teamleaderleo/codex#130`
- Compare: one commit, exactly three files, `+301/-1`

### Historical executed source

- Base: `e6cfd40c3f444aadd6017c9eeab01db70f48961a`
- Head: `e520da008366cd720ef58fa0b489efc0a2867e97`
- Execution carrier: `40a56eefce26ea647a65779faeb783d65a84a49a`
- Workflow run: `30584165709`
- Job: `91011486628`
- Date: `2026-07-30`

### Fresh current-head execution

- Execution-only PR: `teamleaderleo/codex#135`
- Carrier branch: `fieldwork/435-unit-24-exec-9fd4ba5`
- Carrier head: `fb77d59b2f5d07cebee889851a476ebab57c9e45`
- Workflow run: `30690825055`
- Job: `91345120846`
- Date: `2026-08-01`
- Status at this packet revision: queued for a hosted runner

## Changed-file fence

Expected source files:

```text
codex-rs/core/src/client.rs
codex-rs/core/tests/suite/agent_websocket.rs
codex-rs/core/tests/suite/client_websockets.rs
```

The current compare from `ee0247...` to `9fd4ba...` is one commit and exactly these three files. Public drift from the prior parent `670f694...` to `ee0247...` did not touch them.

## Behavioral controls

### 1. Full first generation, then generated-response continuation

Test suffix:

```text
responses_lite_reuses_generated_response_after_full_first_turn
```

Assertions:

- prewarm and first generation use one WebSocket connection;
- the first generated request has no `previous_response_id`;
- the first generated input equals the complete warmup input for the direct client fixture;
- the following turn uses `previous_response_id = resp-1`;
- the following turn sends only the new suffix and no `additional_tools` item.

Historical result: pass.

### 2. Failed first generation retries the complete request

Test suffix:

```text
responses_lite_retries_full_first_turn_after_failed_generation
```

Assertions:

- first generation sends no warmup predecessor;
- the synthetic first-generation failure closes the first connection;
- retry opens a new connection;
- retry sends no `previous_response_id`;
- retry input and model match the failed complete request.

Historical result: pass.

### 3. Full-agent request identity after startup prewarm

Test suffix:

```text
websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm
```

Assertions:

- warmup uses `generate=false`;
- warmup begins with a nonempty `additional_tools` manifest;
- first generated request omits `previous_response_id` and top-level `tools`;
- generated input starts with the exact warmup input and appends the submitted user message;
- model, reasoning, and parallel-tool settings match.

Historical result:

```text
FIELDWORK_LITE_AGENT=default:101;large:0
```

The default Tokio worker stack overflowed. The same assertion passed with `RUST_MIN_STACK=16777216`. This is retained as a runner/runtime discriminator and not presented as a product repair.

## Historical receipt

The authoritative historical workflow recorded:

```text
FIELDWORK_LITE_SOURCE_FENCE=3/3
FIELDWORK_LITE_CLIENT_EXACT=2/2
FIELDWORK_LITE_AGENT=default:101;large:0
```

Coverage limit: exact behavior was executed on source `e520da...`, not the current source head.

## Fresh exact-head workflow

Execution carrier `teamleaderleo/codex#135` is deliberately separate from the clean source PR. It runs these steps against immutable source head `9fd4ba...`:

1. verify the carrier parent equals the source head;
2. verify the source parent equals `ee0247...`;
3. verify the carrier changes one workflow file only;
4. verify the source changes the exact three-file fence;
5. run `cargo fmt --all -- --check`;
6. resolve each exact test name from `cargo test -- --list`;
7. run the two exact client controls;
8. run the full-agent control on default and 16-MiB stacks;
9. require the 16-MiB run to pass and require any default failure to contain a stack-overflow signature;
10. run `RUST_MIN_STACK=33554432 just test -p codex-core`;
11. run `just fix -p codex-core`;
12. require a clean worktree and `git diff --check`.

Expected markers:

```text
FIELDWORK_LITE_CURRENT_SOURCE_FENCE=3/3
FIELDWORK_LITE_CURRENT_FORMAT=PASS
FIELDWORK_LITE_CURRENT_CLIENT_EXACT=2/2
FIELDWORK_LITE_CURRENT_AGENT=default:<status>;large:0
FIELDWORK_LITE_CURRENT_CORE_RAISED_STACK=PASS
FIELDWORK_LITE_CURRENT_FIX=PASS
FIELDWORK_LITE_CURRENT_WORKTREE=CLEAN
```

Any failure is to be inspected and classified. Source-attributable failures require a source repair and a new exact run; setup or repository-baseline failures remain recorded with their limits and do not terminate the unit.

## Ordinary repository CI

### Previous clean-head attempt

On predecessor head `2c3f21d38056d2d77215cd9dce820a680d11cfe8`:

- v8-canary passed;
- format, cargo-deny, codespell, blob-size policy, changed-area detection, and cargo-shear checks passed;
- repository manifest verification failed on a stale exception for `codex-rs/code-mode/Cargo.toml`, outside the unit fence;
- additional Bazel, SDK, macOS, and Windows jobs were red, cancelled, or incomplete and were not used as a focused unit receipt.

The unit continued by rebasing to the newer public parent and creating an exact execution carrier rather than modifying unrelated manifest or platform files.

### Current source CI

Automatic runs were created for source head `9fd4ba...`:

- v8-canary run `30690616645`;
- blocking-ci run `30690616756`.

At this packet revision both were queued. Their results will be classified after completion. The exact execution workflow remains the authoritative focused receipt.

## Prior-art controls

- Generic warmup wire compression is intentional under merged `openai/codex#23581`; the unit predicate must remain Responses Lite-specific.
- Responses Lite input-item identity was introduced by merged `openai/codex#27946`; the first-generated full-input assertions test that contract.
- No equivalent public implementation was found in refreshed issue, PR, and code searches on `2026-08-01`.

## Reversing and isolation controls

- Non-Lite isolation: `use_responses_lite` is required by the production predicate.
- Warmup isolation: the candidate branch is inactive when `warmup` is true.
- Post-generation compatibility: later continuation uses `resp-1` and the suffix only.
- Failure recovery: failed first generation retries full on a new connection.
- Reconnect cleanup: existing connection replacement clears all response-chain state.
- Source isolation: no planner, tool-registration, manifest, workflow, generated, lock, or snapshot file in the source diff.

## Gaps outside the current claim

- live provider deployment and proxy behavior;
- production prevalence;
- long-running WebSocket soak and dedicated leak accounting;
- cancellation during the first generated Lite request;
- root cause of broad agent-test worker-stack pressure;
- full cross-platform repository acceptance where baseline jobs remain unhealthy.

## Cleanup state

- Canonical source contains no execution workflow: yes.
- Superseded execution PR `#133`: closed.
- Superseded execution branch `fieldwork/435-unit-24-exec-2c3f21d`: repointed to the clean current source head.
- Rebase materialization PR `#134`: merged internally.
- Temporary rebase destination branch `fix/responses-lite-first-request-ee0247`: repointed to the exact public-source parent.
- Current execution PR `#135`: open until receipt transfer, then close and repoint its branch to the clean source head.
- Fieldwork branch `tmp-do-not-use`: still cannot be deleted through the available connector; it points at retained packet history and remains an explicit cleanup item.

## Current test judgment

`REPAIR`

Reason: the source and review are coherent, and current exact execution is actively queued. The next disposition will be based on the completed run and failure classification, not on queue state or unrelated repository failures.
