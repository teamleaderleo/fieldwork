# Review — Unit 11: stabilize lifecycle fanout targets

## In simple words

The complete six-file OpenTelemetry candidate has been reviewed and the branch has been repaired into one commit. The implementation is technically coherent within its stated boundary. The repository owner is the final arbiter; no named outside reviewer is being treated as a gate.

## Subject

- target: `open-telemetry/opentelemetry-js`;
- base/current-main snapshot: `2c931bf4eec18a234a28706567c6977f08139abd`;
- branch: `upstream/unit-11-lifecycle-fanout-v2`;
- exact source head: `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`;
- reviewed pre-squash tree source: `987a2bde097fe2e44531830e38c7c15a59c35c23`;
- validation carrier: PR #19;
- relation: one commit ahead, zero behind;
- boundary: three production files and three tests;
- public upstream authority: none.

The clean commit was built from the exact six blobs reviewed at `987a2bde...`; the squash changed history only.

## Technical conclusion

`ACCEPT FOR OWNER DECISION — source repair complete; exact-head execution queued`

Metrics is correctly excluded. The public trace-provider path is included separately from the aggregate path. No further product defect was found in the complete six-file review.

## Complete-diff findings

### `MultiSpanProcessor`

Accepted:

- snapshots the opening processor set;
- retains eager invocation order;
- converts direct synchronous throws into rejected promises;
- preserves shutdown rejection and force-flush global-error-handler/resolve behavior;
- tests cover synchronous throw and opening-set removal for both lifecycle methods.

### `TracerProvider.forceFlush()`

Accepted:

- separately snapshots the provider’s direct fanout targets;
- converts synchronous throws into rejected promises that reach the existing cleanup path;
- clears the per-processor timeout on synchronous failure;
- retains the collected error-array rejection contract;
- tests cover later invocation, stable opening membership, exact error shape, zero remaining timers, and genuine timeout rejection.

### `MultiLogRecordProcessor`

Accepted:

- snapshots the public retained processor array;
- protects direct calls without deferring invocation;
- leaves timeout wrapping and rejection behavior in place;
- tests cover synchronous throw and opening-set removal for shutdown and force flush.

### Metrics exclusion

Accepted:

- the provider constructs an internal collector list instead of retaining the readers array;
- the earlier mutation tests spliced private state;
- collector lifecycle methods are async;
- no metrics source or test file belongs in this contribution.

### Test isolation

Accepted: aggregate trace cleanup installs `loggingErrorHandler()` rather than the factory function itself.

## Source cleanliness

- [x] one commit directly on the pinned public base;
- [x] six target-native source/test files only;
- [x] no metrics/private-state controls;
- [x] no workflows, publishers, lock/dependency files, generated output, or research vocabulary;
- [x] public provider force-flush path included;
- [x] genuine-timeout negative control included;
- [x] complete current diff reviewed;
- [x] owned source PR synchronized to the canonical head;
- [ ] exact-head workflow matrix has executed;
- [ ] required changelog entries added with the real authorized upstream PR number.

## Exact-head workflows

Queued on `db3d9e5e43d5abc6622784acf0ef87f3b038ac91`:

- Unit Tests `30756036668`;
- Lint `30756036660`;
- W3C Trace Context Integration `30756036656`;
- Bundler tests `30756036678`;
- Ensure API Peer Dependency `30756036662`;
- CodeQL Analysis `30756036671`;
- E2E Tests `30756036639`;
- Zizmor GitHub Actions Security Analysis `30756036691`.

Queued execution is an evidence gap, not an uncorrected source defect.

## Compatibility review

- API and types unchanged;
- eager fanout retained;
- aggregate trace shutdown rejects;
- aggregate trace force flush reports globally and resolves;
- provider trace force flush retains error-array rejection;
- logs retain rejection and timeout behavior;
- future mutation remains visible;
- provider cleanup changes only a timer with no useful owner after synchronous failure;
- one shallow copy per affected operation.

## Owner decision surface

The repository owner can now decide whether to advance this candidate. Before public filing, refresh current main, duplicate/overlap, contribution policy, and disclosure requirements, add both changelog entries with the real PR number, and explicitly authorize the upstream interaction.

## Reviewer role

Technical complete-diff review and source repair were performed here. Final project and public-submission authority remains with the repository owner.
