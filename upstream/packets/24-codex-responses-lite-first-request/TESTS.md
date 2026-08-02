# Tests and receipts — unit 24 Responses Lite first request after prewarm

## Exact source

- Public-source parent: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- Candidate head: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- Canonical branch: `teamleaderleo/codex:fix/responses-lite-first-request`
- Canonical draft PR: `teamleaderleo/codex#130`
- Compare: one commit, exactly three files, `+301/-1`

Expected source files:

```text
codex-rs/core/src/client.rs
codex-rs/core/tests/suite/agent_websocket.rs
codex-rs/core/tests/suite/client_websockets.rs
```

## Current exact-head receipt

- Execution PR: `teamleaderleo/fieldwork#459`
- Workflow run: `30691514386`
- Job: `91346961426`
- Source under test: `9fd4ba575de8dd77bc411362256591ce9e7d8c82`
- Job conclusion: `success`

GitHub recorded every source-specific step as successful:

1. `Check out exact Codex source`
2. `Verify immutable source fence`
3. target `setup-ci`
4. pinned Rust toolchain
5. `Check formatting`
6. `Resolve and run exact client controls`
7. `Run exact agent control and classify default stack`
8. `Verify clean source worktree`

This receipt covers the immutable source fence, repository formatting, both exact client controls, the exact full-agent request control with the retained stack discriminator, and clean-worktree/diff validation.

## Behavioral controls

### Full first generation, then generated-response continuation

```text
responses_lite_reuses_generated_response_after_full_first_turn
```

Checks:

- prewarm and first generation share one WebSocket connection;
- first generation has no `previous_response_id`;
- first generated input is complete;
- the following turn uses `previous_response_id = resp-1`;
- the following turn sends only the new suffix and no `additional_tools` item.

Current exact-head result: pass.

### Failed first generation retries the complete request

```text
responses_lite_retries_full_first_turn_after_failed_generation
```

Checks:

- first generation sends no warmup predecessor;
- the synthetic failure closes the first connection;
- retry opens a new connection;
- retry sends no `previous_response_id`;
- retry input and model match the failed complete request.

Current exact-head result: pass.

### Full-agent request identity after startup prewarm

```text
websocket_first_responses_lite_turn_sends_exact_current_request_after_startup_prewarm
```

Checks:

- warmup uses `generate=false`;
- warmup begins with a nonempty `additional_tools` manifest;
- first generated request omits `previous_response_id` and top-level `tools`;
- generated input starts with the exact warmup input and appends the submitted user message;
- model, reasoning, and parallel-tool settings match.

Current exact-head result: pass under the workflow’s default/16-MiB discriminator step.

## Historical receipt

- Base: `e6cfd40c3f444aadd6017c9eeab01db70f48961a`
- Head: `e520da008366cd720ef58fa0b489efc0a2867e97`
- Carrier: `40a56eefce26ea647a65779faeb783d65a84a49a`
- Run/job: `30584165709` / `91011486628`

```text
FIELDWORK_LITE_SOURCE_FENCE=3/3
FIELDWORK_LITE_CLIENT_EXACT=2/2
FIELDWORK_LITE_AGENT=default:101;large:0
```

The historical default Tokio worker stack overflow and raised-stack pass are retained as a harness/runtime discriminator. The current exact-head workflow repeated the corresponding classification step successfully.

## Ordinary repository CI

For current source head `9fd4ba...`:

- v8-canary runs `30690616645` and `30691678330`: success;
- rust formatting: success;
- cargo-deny: success;
- codespell: success;
- blob-size policy: success;
- changed-area detection: success;
- cargo-shear: success.

Repository-wide failures were classified as follows:

- manifest verification fails on a stale exception involving `codex-rs/code-mode/Cargo.toml`, outside the unit fence;
- SDK/Bazel/macOS/Windows jobs fail, cancel, or lack source-attributable step data and do not identify any of the three unit files;
- a separate raised-stack `just test -p codex-core` package job fails after the exact unit controls pass. The available receipt does not expose a source-specific failing test or assertion. It remains broad repository evidence rather than a fabricated unit diagnosis.

Supplementary sequential candidate/base package controls were created on execution branches during classification. They were execution-only and are excluded from the clean source and packet heads.

## Public-source drift control

Public `openai/codex:main` was refreshed through `3e3d82d674d8a263cf2c33684f6a04beb9dcf8d7`, six commits after `ee0247...`. None of those commits changes the three source/test files in this unit.

## Isolation controls

- `use_responses_lite` is required by the production predicate.
- The candidate is inactive during warmup itself.
- Generic non-Lite response chaining is unchanged.
- Later continuation uses the first generated response, not warmup.
- Failed first generation retries full on a new connection.
- Existing reconnect cleanup remains the response-chain reset owner.
- No workflow, manifest, lock, generated, snapshot, planner, or tool-registration file enters the canonical source diff.

## Cleanup state

- Canonical source contains no execution workflow: yes.
- Superseded execution PR `#133`: closed.
- Target execution PR `teamleaderleo/codex#135`: closed without merge.
- Target execution branch `fieldwork/435-unit-24-exec-9fd4ba5`: repointed to clean source head `9fd4ba575de8dd77bc411362256591ce9e7d8c82`.
- Cross-repo execution PR `teamleaderleo/fieldwork#459`: closed without merge.
- Cross-repo execution branch `p0/435-unit-24-crossrepo-exec`: repointed to final packet history.
- Fieldwork branch `tmp-do-not-use`: deletion is unavailable through the connector; it is repointed to final packet history and documented in the #435 handoff.

## Test judgment

`READY`

The exact current source passes the source-specific behavior, formatting, and worktree gates. Repository-wide failures are outside the three-file fence or provide no source-attributable diagnosis and are recorded without widening the unit.
