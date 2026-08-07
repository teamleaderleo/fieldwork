# Unit 26 — Codex terminal completion retention

## Current disposition

`SUBMITTED — UPSTREAM ISSUE OPEN / MAINTAINER TRIAGE PENDING`

The owner filed [openai/codex#37207](https://redirect.github.com/openai/codex/issues/37207).

The report covers one concrete failure: unified exec can receive terminal bytes and still omit them from the completed command result when the completion listener subscribes late or falls behind.

As of the latest check, the issue is open with `bug`, `CLI`, and `tool-calls` labels and has no maintainer comments yet.

## Selected boundary

The process producer retains the completion transcript before broadcasting live deltas.

- producer-owned retention supplies the completed result;
- live delivery can still miss updates;
- late or lagged listeners cannot erase output already accepted by the process layer;
- invalid UTF-8 remains retained as bytes;
- existing head/tail limits remain in force;
- normal close replaces partial listener state with the retained transcript.

## Current implementation proof

- Owned source PR: `teamleaderleo/codex#144`
- Base: `ee0247f95a6fe2b094ba2253d82cae2a2b4c2dff`
- Current head: `d4ff73f50e30e96b6db4a08205c9d3600e15488e`
- Branch: `fieldwork/26-terminal-completion-retention-source`
- Shape: four Rust files

Files:

- `codex-rs/core/src/unified_exec/async_watcher.rs`
- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`
- `codex-rs/core/src/unified_exec/process.rs`
- `codex-rs/core/src/unified_exec/process_tests.rs`

The first fully executed implementation used separate mutexes for the polling and completion buffers. The current head places both `HeadTailBuffer` values in one shared `OutputState` mutex and exposes separate polling and completion views. Each producer updates both views under one lock before broadcasting the live chunk.

That removes the partial-update window between the two retained views and reduces producer-side lock acquisition from two to one.

## Current-head CI

- `v8-canary` run `31072774070`: passed;
- `blocking-ci` run `31072774224`: failed;
- formatting and Rust benchmark smoke: passed;
- cargo-shear: passed;
- blob-size policy, cargo-deny, and codespell: passed.

The first deterministic blocking-CI failure is outside the four-file patch: `verify_cargo_workspace_manifests.py` reports a stale `code-mode/Cargo.toml` feature-exception entry in the owned fork. Later SDK/Bazel/platform failures are broad repository-state signals and are not treated as validation of this patch.

The current single-mutex head therefore does not yet have an equivalent paired source-vs-baseline receipt.

## Earlier paired execution

Execution carrier `teamleaderleo/codex#137`, corrected run `30699322569`, covered the previous two-mutex source head `b2a704c708748462d7893fe82cf8971f00ca751e`:

- baseline `codex-core` library: `2,129/2,129` passed;
- source exact terminal-retention controls: `12/12` passed;
- source `codex-core` library: `2,133/2,133` passed;
- integration targets compiled;
- formatting and exact four-file fence passed;
- paired baseline/source artifacts and logs retained.

This remains strong evidence for the behavior, but it is not an exact-head receipt for the single-mutex revision.

## Latest public comparison

Latest public head checked: `b3278e96cb6df4b77b8dd93cf6c65d74990a033d`.

Public main has now changed the two production files in the source fence:

- `async_watcher.rs`: `5ffbfaaafd7ea1e74cbc80ff2b04f321519b1406`;
- `process.rs`: `e8ec6b98828ee896f96d50dbde995fb3435c2644`.

The two test files remain byte-identical to the implementation base:

- `async_watcher_tests.rs`: `66fd8dba1194a17d1a1b19b3d257750fd88eb56e`;
- `process_tests.rs`: `e7f99e38ee731241e1b2a1cb6f590d4a560a5ad1`.

The main overlapping public change is merged `openai/codex#37083`, which consolidates the existing output buffer, notifications, closed state, and cancellation token into `OutputHandles`.

That refactor does not fix issue #37207. On the latest checked head:

- `start_streaming_output` still continues after `RecvError::Lagged(_)` while its listener-owned transcript is being built;
- the local output collector still continues after `RecvError::Lagged(_)` before the missed chunks can be added to its retained output buffer.

A future public PR therefore needs a semantic restack onto the current `OutputHandles` shape rather than a mechanical replay of the owned branch.

## Historical intent of `Lagged`

Merged `openai/codex#4992` introduced the explicit `Lagged(_) => continue` handling so a receiver that falls behind would skip missed messages but keep the output task alive and continue streaming later output.

That supports the current issue framing: continuing after lag is a useful resilience behavior for live delivery. The problem is allowing that lossy observation path to define the completed command record as well.

## Submission receipt

- Upstream issue: [openai/codex#37207](https://redirect.github.com/openai/codex/issues/37207)
- State: open
- Labels: `bug`, `CLI`, `tool-calls`
- Maintainer comments at latest check: none
- Public implementation PR: none
- Owned implementation proof: `teamleaderleo/codex#144`

## Next state

Leave the public issue alone unless a maintainer engages.

If a public PR is later invited and authorized:

1. restack the single-state design onto then-current public main;
2. add sustained stdout/stderr plus concurrent-polling stress coverage;
3. add cancellation-boundary timing coverage;
4. run a fresh paired baseline/source gate on the exact proposed head;
5. review the final diff against any additional unified-exec changes.

No further public comment, reaction, pull request, review, or other upstream interaction is authorized.