# Tests and receipts — Unit 24 Responses Lite first request after prewarm

## Exact current source

- Public-source parent: `e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`
- Candidate head: `abf61e5fb8505181e071674ce224faff17e79d77`
- Canonical branch: `teamleaderleo/codex:fix/responses-lite-first-request-e4e0c70`
- Owned-fork draft PR: `teamleaderleo/codex#143`
- Compare: one commit, exactly three files, `+301/-1`

Expected source files:

```text
codex-rs/core/src/client.rs
codex-rs/core/tests/suite/agent_websocket.rs
codex-rs/core/tests/suite/client_websockets.rs
```

## Current execution status

Corrected immutable-current-head execution is queued on lightweight carrier `teamleaderleo/smolrunner#286`:

- run: `30849910237`
- exact-source job: `91807127950`
- source under test: `abf61e5fb8505181e071674ce224faff17e79d77`
- exact parent asserted: `e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`

The job will require:

1. exact immutable source and parent;
2. exact three-file fence;
3. `cargo fmt --all -- --check` from `codex-rs/`;
4. both exact client controls;
5. the exact full-agent request-shape control;
6. `just fix -p codex-core`;
7. clean worktree and `git diff --check`.

Two redundant current-source carriers were closed without merge after the lightweight lane was established:

- `teamleaderleo/codex#142`;
- `teamleaderleo/fieldwork#596`.

## Harness correction

The first attempted current-head carrier run `30848390794` stopped at formatting before any test ran because the workflow invoked Cargo from the repository root. Codex's Rust workspace is under `codex-rs/`.

The log reports:

```text
could not find Cargo.toml in /home/runner/work/codex/codex or any parent directory
```

This is an execution-harness error, not a source failure or a failed target assertion. Every corrected lane runs Rust and `just` commands from `codex-rs/`.

## Behavioral controls

### Complete first generation, then generated-response continuation

```text
responses_lite_reuses_generated_response_after_full_first_turn
```

Checks:

- prewarm and first generation share one WebSocket connection;
- first generation has no `previous_response_id`;
- first generated input is complete;
- the following turn uses `previous_response_id = resp-1`;
- the following turn sends only the new suffix and no `additional_tools` item.

### Failed first generation retries complete

```text
responses_lite_retries_full_first_turn_after_failed_generation
```

Checks:

- first generation sends no prewarm predecessor;
- synthetic failure closes the first connection;
- retry opens a new connection;
- retry sends no `previous_response_id`;
- retry input and model match the failed complete request.

### Full-agent request identity after startup prewarm

```text
websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm
```

Checks:

- prewarm uses `generate=false`;
- prewarm carries a nonempty Lite tool manifest;
- first generated request omits `previous_response_id` and top-level `tools`;
- generated input starts with the exact prewarm input and appends the user message;
- model, reasoning, and parallel-tool settings match.

## Historical exact receipt for the same patch

The predecessor source `9fd4ba575de8dd77bc411362256591ce9e7d8c82` passed immutable exact execution in Fieldwork run `30691514386`, job `91346961426`:

```text
FIELDWORK_LITE_SOURCE_FENCE=3/3
FIELDWORK_LITE_CLIENT_EXACT=2/2
```

The job also passed formatting, the full-agent request-shape discriminator, and clean-worktree validation.

The current source is a patch-equivalent one-commit restack. The advance from the historical base to `e4e0c707...` did not modify any of the three unit files. This historical receipt is strong predecessor evidence, but the packet does not mislabel it as the current-head receipt.

## Current ordinary CI

Normal CI on source `abf61e5...` is queued:

- blocking CI run `30849647092`;
- v8-canary run `30849647356`.

These are supplemental to the focused immutable-source lane. Broad repository results will be recorded without widening the three-file source claim.

## Isolation controls

- `use_responses_lite` is required by the production predicate.
- The candidate is inactive during warmup itself.
- Generic non-Lite response chaining is unchanged.
- Later continuation uses the first generated response, not prewarm.
- Failed first generation retries complete.
- Existing reconnect cleanup remains the response-chain reset owner.
- No workflow, manifest, lock, generated, snapshot, planner, or tool-registration file enters the source diff.

## Current test judgment

`PENDING CURRENT EXACT RECEIPT`

The source has a patch-equivalent historical green receipt and a current complete-diff review. One corrected immutable-current-head green run remains before the filing package is marked fully refreshed.
