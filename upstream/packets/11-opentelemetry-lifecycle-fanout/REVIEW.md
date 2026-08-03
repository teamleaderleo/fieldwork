# Review — Unit 11: stabilize lifecycle fanout targets

## In simple words

The complete six-file OpenTelemetry candidate is one clean commit, passed all eight exact-head workflows, and received an independent exact-head technical acceptance. No blocking product defect remains within the stated trace/log lifecycle boundary. The repository owner is the final arbiter.

## Subject

- target: `open-telemetry/opentelemetry-js`;
- base/current-main snapshot: `2c931bf4eec18a234a28706567c6977f08139abd`;
- branch: `upstream/unit-11-lifecycle-fanout-v2`;
- exact source head: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`;
- source PR: `teamleaderleo/opentelemetry-js#19`;
- relation: one commit ahead, zero behind;
- boundary: three production files and three tests;
- public upstream authority: none.

## Disposition

`ACCEPT / TECHNICALLY READY — OWNER DECISION REQUESTED`

## Why the repair is correct

### `MultiSpanProcessor`

- snapshots the opening processor set before any child invocation;
- invokes children eagerly through a local try/catch helper;
- converts only direct synchronous throws into rejected promises;
- preserves shutdown rejection and force-flush global-error-handler/resolve behavior.

### `TracerProvider.forceFlush()`

- separately snapshots its direct fanout targets;
- creates the timeout before invocation as before;
- routes synchronous throws through the existing catch path;
- clears the timeout and preserves the existing collected error-array rejection;
- retains genuine timeout rejection for non-settling processors.

### `MultiLogRecordProcessor`

- snapshots the retained public processor array;
- protects direct calls without microtask deferral;
- preserves timeout wrapping and rejection behavior.

### Metrics exclusion

- provider collector membership is internally constructed;
- prior mutation controls required private-state access;
- metric collector lifecycle methods are async;
- symmetry alone does not justify widening the patch.

## Evidence

All eight workflows passed at the exact source head:

- Unit Tests `30756036668`;
- Lint `30756036660`;
- W3C `30756036656`;
- Bundler `30756036678`;
- API peer dependency `30756036662`;
- CodeQL `30756036671`;
- E2E `30756036639`;
- Zizmor `30756036691`.

Independent exact-head review of the complete six-file fence found no blocking source defect and accepted the candidate as technically ready.

## Compatibility boundary

- no public API or type change;
- eager fanout retained;
- existing trace aggregate, provider, and logs settlement policies retained;
- future mutations remain visible to future operations;
- one shallow copy per affected operation;
- no settle-all aggregation, retries, cancellation, idempotence, or metrics change.

## Recommendation to the owner

Advance this candidate toward authorized upstream preparation. Before filing, refresh current public main and duplicate/overlap, confirm current contribution and disclosure policy, add root and experimental changelog entries with the real upstream PR number, and explicitly authorize the public interaction.
