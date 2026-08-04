# Approaches — unit 07 backgroundFetchSize snapshot

## In simple words

The selected direction validates the option and binds each pending missing-key fetch to a captured size receipt. Earlier approaches either validated too early, re-read mutable state after user code, transported the change as a patch, introduced an exported-type compatibility break, added an unnecessary clock dependency, or stopped one review pass before the hostile/`undefined`/stale controls. Their evidence remains useful; their packaging or test completeness lost.

## Decision criteria

1. Pending accounting always receives a primitive finite nonnegative integer without coercion.
2. Zero, omitted/default `undefined`, stale refresh, same-key coalescing, and no-size behavior remain compatible.
3. Synchronous user callback mutation cannot change the already-dispatched operation.
4. The upstream diff stays limited to product source and target-native tests.
5. Exported TypeScript types and cross-platform tests avoid avoidable compatibility costs.

## Selected approach

### Pre-dispatch validation plus per-operation receipt

- Design: validate construction; for missing-key size-tracked fetches, capture the current value before Promise construction, assign it to `BackgroundFetch.__size`, and consume that receipt in `#requireSize()`.
- Owning boundary: `#backgroundFetch()` owns dispatch-time capture; `#requireSize()` owns accounting-time enforcement.
- Evidence: source review, released probe, hostile object control, explicit constructor/mutated `undefined`, callback mutation tests, zero/no-size/stale controls, internal-receipt control, and earlier native executions.
- Advantages: closes the demonstrated re-entry window; avoids coercion; preserves later mutability; keeps unrelated paths unchanged.
- Costs and risks: one internal property and validation branch; constructor behavior becomes stricter for invalid runtime values.
- Remaining controls: exact-head CI, benchmarks, focused build/lint/format, and independent final review.

## Viable alternatives

### Make backgroundFetchSize immutable after construction

- Design: expose a read-only field or private backing value.
- Why it remains plausible: removes all later mutation ambiguity.
- What it would improve: simpler lifetime contract.
- What it would widen or complicate: public API compatibility and the existing mutable-option pattern.
- Exact discriminator: maintainer preference for immutable configuration.
- Reopening trigger: maintainers reject per-operation mutation semantics.

### Validate only at consumption

- Design: accept any constructor value, then validate whenever missing-key provisional accounting uses it.
- Why it remains plausible: no-size caches could carry irrelevant values indefinitely.
- What it would improve: narrower runtime rejection surface.
- What it would widen or complicate: configuration validity depends on later operations and cache mode.
- Exact discriminator: documented option-validation policy for unused options.
- Reopening trigger: maintainers prefer lazy validation consistently across numeric options.

## Executed losing approaches

### Constructor-only validation

- Exact branch, patch, or commit: early iterations on owned PR #1 and Fieldwork PR #135.
- What ran: released probes and focused constructor controls.
- Result: invalid construction was blocked, but source review found synchronous `fetchMethod` mutation between check and accounting.
- Why it lost: it left the demonstrated time-of-check/time-of-use window open.
- Useful evidence retained: primitive type guard and zero compatibility.

### Pre-dispatch check with later public-field re-read

- Exact branch, patch, or commit: intermediate candidate before receipt attachment.
- What ran: focused mutation review and source trace.
- Result: user callback could still replace the value before `#requireSize()`.
- Why it lost: the current operation had no immutable accounting identity.
- Useful evidence retained: validation belongs before provider dispatch.

### Patch carrier

- Exact branch, patch, or commit: `teamleaderleo/node-lru-cache#1`, branch `fieldwork/background-fetch-size-validation`; Fieldwork PR #135.
- What ran: `git apply --check`, build/declarations, 70 focused assertions on Node 22/24/26, OXLint, and Prettier.
- Result: behavior and formatting passed on the final historical carrier revision.
- Why it lost: `src/index.ts` remained an applied patch artifact, so the branch was an execution surface rather than an upstream-ready diff.
- Useful evidence retained: baseline probe, candidate contract, focused matrix, issue draft, and review requests for hostile values, `undefined`, and stale usage-bound behavior.

### Required exported __size field

- Exact branch, patch, or commit: target PR #2 at `f9dcd66cda9fffbe9612e6053634853dfde30e25`; review `4824064389`.
- What ran: complete source/test review and earlier native checks.
- Result: runtime design was coherent; exported `BackgroundFetch` consumers could face a TypeScript source break.
- Why it lost: internal invariant enforcement did not require a new mandatory public member.
- Useful evidence retained: `__size?: number` plus runtime validation.

### t.clock dependency repair

- Exact branch, patch, or commit: target PR #2 at `fef8328c9431b656c0ee48547250e37d6caeabef`.
- What ran: workflows ended `action_required` before jobs.
- Result: added `@tapjs/clock`, `package.json`, and lockfile churn despite a dependency-free test route.
- Why it lost: widened the diff and contradicted source cleanliness.
- Useful evidence retained: the optional exported field change.

### First clean two-file generation

- Exact branch, patch, or commit: target head `0f4a357a9bc0b09ad413e99fa566317bf4ce283c`.
- What ran: native CI `30674355332` and Benchmarks `30674355680` were queued before the head moved.
- Result: source and main test logic were clean, but complete historical review exposed three untransferred controls.
- Why it lost: no hostile conversion object, no post-construction `undefined` control, and no invalid-field stale refresh control.
- Useful evidence retained: identical product source and dependency-free timing repairs.

### Fixed-sleep autopurge control

- Exact branch, patch, or commit: earlier target PR #2 heads before `f9dcd66...`.
- What ran: platform matrices exposed timing and coverage variability.
- Result: a fixed scheduler window was brittle, and one approach replaced the timer before the intended branch could execute.
- Why it lost: it failed to observe the exact reschedule transition deterministically enough.
- Useful evidence retained: current bounded condition poll and direct internal start-receipt adjustment.

## Rejected easy answers

### Reuse isPosInt directly

- Temptation: treat positive integer validation as sufficient.
- Why it is incomplete: zero is established compatible behavior and must remain accepted.
- Negative control or source fact: released zero-size fetches remain cached and coalesced.

### Coerce with Number(), Math.floor(), or global isFinite()

- Temptation: normalize dynamic values.
- Why it is incomplete: strings, booleans, objects, symbols, and hostile conversion hooks should never enter accounting through coercion.
- Negative control or source fact: runtime string `'2'` causes demonstrated state corruption; the final hostile object throws from every conversion hook.

### Treat constructor undefined as invalid

- Temptation: apply the runtime domain check before option defaults.
- Why it is incomplete: an optional property explicitly set to `undefined` has the same constructor semantics as omission in the current destructuring path.
- Negative control or source fact: final native control accepts constructor `undefined` while rejecting later mutated `undefined` when missing-key accounting consumes it.

### Validate every refresh path

- Temptation: reject the public field on any `fetch()` call.
- Why it is incomplete: stale refresh reuses an existing entry size and no-size caches have no provisional size accounting.
- Negative control or source fact: final controls prove invalid values remain irrelevant in those paths.

### Read the public field again during insertion

- Temptation: avoid adding an internal receipt.
- Why it is incomplete: synchronous callback re-entry can mutate the value before insertion.
- Negative control or source fact: Promise executors invoke `fetchMethod` synchronously.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [`4708153206...`](https://github.com/isaacs/node-lru-cache/commit/4708153206daf822a3ad440ce47248b9cfbdb973) | introduce `backgroundFetchSize` and provisional accounting | merged | original feature and semantic baseline |
| [`0b0a77e992...`](https://github.com/isaacs/node-lru-cache/commit/0b0a77e99245e12c53ec0cf05e200c66e6749ba9) | reschedule an autopurge timer that fires before revised expiry | merged | adjacent line covered by current native test |
| upstream issue/PR search on 2026-08-01 | matching repair | none found | independent candidate |

## Deferred adjacent work

- broader mutable-option snapshots — separate API audit
- general cache index hardening against corrupted internals — separate invariant family
- fetch cancellation ownership — separate lifecycle behavior
- benchmark interpretation beyond pass/fail — separate performance study

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-29 | released `11.5.2`, probe `30491292307` | confirm defect | invalid values reached live arithmetic | public source changes |
| 2026-07-30 | owned PR #1 and Fieldwork PR #135 | select validation plus snapshot | constructor-only validation missed callback re-entry | maintainer contract differs |
| 2026-07-30 | target PR #2 review `4824064389` | repair exported type | required field risked TS compatibility | type no longer exported |
| 2026-07-31 | target head `fef8328...` | reject dependency/lock churn | test can use injected time and real timers | target explicitly requires plugin |
| 2026-08-01 | base `16b3...`, target head `0f4a357a...` | publish first clean two-file generation | removed all dependency and lock churn | complete prior-art review |
| 2026-08-01 | PR #1 reviews plus first clean diff | supersede with `70a9e62b0555e6bb68763fb9d32458fa82fd2a70` | add hostile, `undefined`, and stale usage-bound controls | exact-head execution or review reverses result |
