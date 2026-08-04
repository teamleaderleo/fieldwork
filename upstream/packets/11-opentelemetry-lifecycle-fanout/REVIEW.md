# Review — Unit 11: stabilize lifecycle fanout targets

## Current disposition

`SOURCE REVIEW ACCEPTED — EXACT-HEAD EXECUTION PENDING`

The current-main rebase remains one clean six-file commit. A fresh complete-diff source review found no blocking defect in the rebased mechanism, including its integration with the newly merged per-call trace force-flush timeout. Fresh repository workflows are still running, so this is not yet a final filing-ready disposition.

## Subject

- target: `open-telemetry/opentelemetry-js`;
- refreshed base: `f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`;
- branch: `upstream/unit-11-lifecycle-fanout-v2`;
- exact source head: `f4cb44bcccffbc0eb39e774284655e0f965cfce1`;
- source PR: `teamleaderleo/opentelemetry-js#19`;
- relation: one commit ahead, zero behind;
- boundary: three production files and three tests;
- public upstream authority: none.

## Fresh rebase findings

### Current-main overlap

Public `main` advanced by three commits from the earlier base. The only source overlap is upstream PR #6929, which adds `ForceFlushOptions` and a per-call timeout to `TracerProvider.forceFlush()`.

The rebased candidate preserves:

- the `ForceFlushOptions` import and public signature;
- per-call timeout precedence over the deprecated constructor setting;
- upstream's existing timeout tests;
- the unrelated `MultiSpanProcessor.onEnding()` forwarder added on current main.

No current issue or pull request was found that duplicates the synchronous-throw/opening-set repair.

### `MultiSpanProcessor`

- snapshots the opening processor set before any child invocation;
- invokes children eagerly through a local `try`/`catch` helper;
- converts only direct synchronous throws into rejected promises;
- preserves shutdown rejection and force-flush global-error-handler/resolve behavior;
- leaves normal `onStart`, `onEnding`, and `onEnd` hot paths unchanged.

### `TracerProvider.forceFlush()`

- separately snapshots its direct fanout targets;
- resolves the current timeout from the per-call option before fanout as upstream now requires;
- creates each timeout before invocation as before;
- routes synchronous throws through the existing catch path;
- clears the timeout and preserves the existing collected error-array rejection;
- retains genuine timeout rejection for non-settling processors.

### `MultiLogRecordProcessor`

- snapshots the retained public processor array;
- protects direct calls without microtask deferral;
- preserves the current per-call timeout option, timeout wrapper, and rejection behavior.

### Metrics exclusion

- provider collector membership is internally constructed;
- prior mutation controls required private-state access;
- metric collector lifecycle methods are async;
- symmetry alone does not justify widening the patch.

## Regression coverage

Eleven focused assertions cover direct throws, opening-set mutation, provider error-array shape, timeout cleanup, and genuine timeout behavior. The rebased provider tests use the new per-call timeout option rather than the deprecated constructor option.

## Compatibility boundary

- no new public API or type change;
- upstream's new per-call timeout API is retained;
- eager fanout and existing order are retained;
- existing trace aggregate, provider, and logs settlement policies are retained;
- future mutations remain visible to future operations;
- one shallow copy per affected lifecycle operation;
- no settle-all aggregation, retries, cancellation, idempotence, or metrics change.

## Remaining evidence gate

The fresh exact-head workflow matrix for `f4cb44bcccffbc0eb39e774284655e0f965cfce1` must complete and be classified. The earlier green matrix and acceptance on `db3d9e5e43d5abc6622784acf0ef87f3b038ac91` are historical evidence only.

## Recommendation

Keep the source preview and packet in draft until the fresh matrix is green or any candidate-relevant failure is repaired. Once that gate closes, present the prepared upstream wording and explicit public-contact decision to the repository owner.
