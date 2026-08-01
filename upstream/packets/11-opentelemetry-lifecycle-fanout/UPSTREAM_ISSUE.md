# Upstream issue draft — lifecycle fanout can skip opening children after mutation or direct synchronous failure

Draft status: `not applicable — direct PR preferred after repair`  
Public interaction authorized: `no`

A direct pull request remains preferable once the owned candidate is repaired. This fallback draft deliberately distinguishes the trace/logs synchronous-invocation defect from the metrics snapshot-only defect.

---

## Summary

Trace, logs, and metrics lifecycle fanout iterates mutable arrays. An earlier child can remove a later indexed child during shutdown or force flush, causing the current operation to skip a child that belonged to its opening set.

Trace and logs additionally invoke processor lifecycle methods directly while constructing promise inputs. A synchronous processor throw can stop construction before later opening processors are invoked.

Metrics already calls async `MetricCollector` lifecycle methods, so synchronous reader throws already become rejected promises. Metrics needs stable opening membership, not an extra synchronous safe-call layer.

## Reproduction

1. Configure two processors or readers.
2. Make the first remove the second from the backing collection during shutdown or force flush.
3. Invoke the aggregate lifecycle method.
4. Observe that live indexed iteration can skip the removed opening child.

For trace and logs, a second control makes the first processor throw synchronously and verifies whether the later opening processor is invoked.

## Expected behavior

A lifecycle aggregate should attempt every child present when the operation begins. Mutation during the call should affect future operations while leaving current opening membership stable. Existing package-specific error behavior should remain unchanged.

## Candidate direction

- Trace and logs: copy the opening processor array and convert direct synchronous throws into rejected promises before applying the existing `Promise.all` policy.
- Metrics: copy the opening collector array and continue calling the existing async collector lifecycle methods directly.

## Compatibility and limits

- Public APIs and method signatures remain unchanged.
- Future operations continue to observe mutations to the original collections.
- Existing eager concurrency and first-rejection behavior remain.
- The proposal does not aggregate every asynchronous child error.
- Production frequency and ecosystem prevalence are unmeasured.
- Delayed recursion, one-shot shutdown state, final metrics collection, and retry semantics remain separate.

## Versions and evidence

- Reviewed project commit: `2c931bf4eec18a234a28706567c6977f08139abd`;
- Owned candidate head reviewed: `641528c9786f7d027fef4f4a76ae685f7107d394`;
- Repository workflow matrix: all named groups passed on the owned candidate;
- Complete-diff result: candidate requires metrics narrowing before filing.

---

## Filing checklist

- [ ] Metrics source repaired to snapshot-only and every claim synchronized.
- [ ] Repaired exact head passes the complete required workflow set.
- [ ] Eligible independent complete-diff review accepts the repaired head.
- [ ] Current upstream issue and PR search repeated immediately before filing.
- [ ] Changelog packaging completed using a real PR number.
- [ ] Target contribution and AI-disclosure policies rechecked.
- [ ] Exact user authorization to file recorded.
