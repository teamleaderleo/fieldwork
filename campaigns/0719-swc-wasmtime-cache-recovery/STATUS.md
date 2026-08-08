# SWC Wasmtime Cache Recovery

## In simple words

Campaign #719 now has two distinct Wasmtime filesystem-cache recovery discriminators. PR `teamleaderleo/swc#1` covers an abandoned legacy temporary file that blocks final publication. PR `teamleaderleo/swc#3` covers a rejected final cache artifact that Wasmtime leaves behind even though the Wasmer sibling explicitly deletes rejected cache files.

The publication candidate remains draft and target-test-prepared. The rejected-cache branch is test-only so the second defect stays independently reviewable until target-native execution is available.

- Campaign issue: #719
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Public source pin: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Stale-temp candidate: `teamleaderleo/swc#1` at `bce1d2e03f654d6aaaac77d76e2a818b3b743706`
- Rejected-cache discriminator: `teamleaderleo/swc#3` at `825e42ed44676001d6c6a52bc1d0807a91852137`
- Evidence: `source-read`, `model-executed`, `target-test-prepared`
- Upstream contact: prohibited for automated workers

## Recovery cases

### 1. Abandoned deterministic temporary file

Current Wasmtime publication derives one `.tmp` sibling, opens it with `create_new`, and treats `AlreadyExists` as success. A prior interrupted writer can therefore leave a stale temp file that causes a later store to report success while the final path remains absent.

PR #1 prepares a unique same-directory temporary path and final rename pattern modeled on the Wasmer sibling.

### 2. Rejected final cache artifact

Wasmtime reads the final file and returns `None` when `wasmtime::Module::deserialize` rejects it, but leaves the file in place.

Wasmer handles the same lifecycle explicitly: if module deserialization fails, it removes the cache file because it no longer trusts the artifact.

PR #3 pins the equivalent Wasmtime expectation as a test without bundling a production repair.

## Review finding on PR #1

During continuation work an attempted full-file edit accidentally duplicated part of `WasmtimeRuntime::init`. The branch was force-restored immediately to its prior exact head `bce1d2e03f654d6aaaac77d76e2a818b3b743706`; PR #1 currently contains none of that bad intermediate edit.

This is recorded because exact-head review is part of the campaign evidence boundary.

## Execution status

The fork's inherited `CI.yml` listens to `pull_request` events, including synchronize, but the connected GitHub interface has returned no workflow runs for the current research heads. No target-executed or full-gate claim is made.

## Current disposition

**HOLD** promotion of PR #1 until:

1. stale-temp base failure and candidate pass are target-executed;
2. rejected-cache behavior is target-executed;
3. the relationship between invalid-cache deletion and Windows destination handling is incorporated into the final candidate;
4. focused Wasmtime tests, formatting, clippy, and exact-head diff review pass.
