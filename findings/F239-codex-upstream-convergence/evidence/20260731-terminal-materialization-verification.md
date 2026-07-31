# F239 terminal source materialization verification — 2026-07-31

## Result

The bounded terminal producer-retention source is present in owned Git and has an open source-review pull request.

- Source PR: `teamleaderleo/codex#91`.
- Live exact source head: `5216ca53ef949c285508e2a2b71d02462a87f6ec`.
- Exact parent: `97576b1794872e342450ebd577123e052ab57626`.
- Exact source tree: `563f90f55c0ebd9454171d24697d796cba1388d4`.
- Four-file source fence:
  - `codex-rs/core/src/unified_exec/async_watcher.rs`;
  - `codex-rs/core/src/unified_exec/async_watcher_tests.rs`;
  - `codex-rs/core/src/unified_exec/process.rs`;
  - `codex-rs/core/src/unified_exec/process_tests.rs`.
- Independent source review: `4824480012`.
- Review disposition: `ACCEPT` bounded normal-close producer retention; hold proposal packaging for direct-current-head source and compatibility review.

Upstream contact authorized: `no`.

## Authoritative behavior execution

- Fieldwork run: `30587866332`.
- Job: `91023382172`.
- Result: formatting, exact four-file fence, nine uniquely resolved exact controls through repository entrypoints, focused core library gate, integration compilation, source export, and artifact upload passed.
- Retained artifact: `8777460316`.
- Artifact digest: `sha256:9c6c4f6741ee2514e995849ca2bed9caf0f80b80fdbb3a9ea31565df3ebda2dd`.
- Retained source archive SHA-256: `dca7808534f03a576a3b1d11f312393a8861c7c5f268cea2b3d6ac442f1122f5`.

## Materialization-run classification

Disposable carrier `teamleaderleo/codex#86@4779b0f376b21bb0fa8ed0fbb0e42728e0ecf9c1` ran workflow `30590643470`, job `91032002837`.

Passed:

- archive decoding and digest verification;
- exact four-file inventory;
- exact source-base checkout;
- extraction and changed-file fence;
- `git diff --check`;
- exact `git write-tree` result `563f90f55c0ebd9454171d24697d796cba1388d4`;
- one-commit source creation directly parented by the exact base.

The run created local commit `39d1f750a02d4fb2b3654ddabdf9b52ebb65ef2e`. Its final push failed with a non-fast-forward rejection because the intended destination branch already contained independently published source commit `5216ca53ef949c285508e2a2b71d02462a87f6ec`.

Classification: publication race only. It supplies no negative source evidence.

## Byte-for-byte branch verification

The retained artifact and live source branch have the same Git blob IDs for all four files:

| File | Git blob |
| --- | --- |
| `async_watcher.rs` | `a0427969dec77d57f6bc3037108cd4be26125cd0` |
| `async_watcher_tests.rs` | `57002ea930169d2815aed51e42bbb37f27faedc8` |
| `process.rs` | `ca47e90159328921a3f469fd0dad72c91ef5f86a` |
| `process_tests.rs` | `b76c9151eb9b5a42e6e6cdfe4ef4b1c0c1686f58` |

The differing source commit SHA comes from commit metadata. The parent, tree, source files, and patch are equivalent.

## Bounded conclusion

The source establishes normal-close terminal transcript ownership:

- local output enters a bounded producer-owned completion transcript before best-effort broadcast;
- late or lagging listeners cannot erase retained completion bytes;
- the completion path replaces a partial listener-derived transcript with the authoritative bounded producer transcript at close;
- deque limits, invalid-UTF-8 progress, and close/drain ordering remain preserved.

Outside this finding:

- hard-kill trailing-byte recovery;
- Windows descendant containment and pipe-to-job race;
- remote executor process discovery or reattachment after a full Codex restart;
- durable tool-result persistence;
- unbounded output retention.

## Current public relation

Current read-only public Codex head: `4642370542739d5dd080b0c87a9de06a6435d3db`.

The public delta after source base has no file overlap with the four-file terminal fence. File disjointness preserves the bounded source conclusion. Direct-current-head packaging and semantic compatibility review remain.

## Coordination consequence

The F23 materialization gate is cleared. Remaining work moves from artifact publication to current-head packaging, source review reconciliation, carrier cleanup, and the independently owned termination/restart findings.

This note supersedes earlier F239 and PR #292 fields that described owned Git source as absent or materialization as still pending.

Public upstream interaction performed: none.