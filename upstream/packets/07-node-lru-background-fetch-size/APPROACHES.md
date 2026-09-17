# Approaches — unit 07 backgroundFetchSize snapshot

## In simple words

The selected direction validates `backgroundFetchSize` and binds each pending missing-key fetch to a captured size receipt before user `fetchMethod` code can mutate the public field. Earlier approaches either validated too early, re-read mutable state after user code, widened the source surface, or over-tested deliberately corrupted private state.

The owner submitted the final direction as [isaacs/node-lru-cache#410](https://redirect.github.com/isaacs/node-lru-cache/pull/410).

## Decision criteria

1. Pending accounting receives a primitive finite nonnegative integer without coercion.
2. Zero, stale refresh, same-key coalescing, and no-size behavior remain compatible.
3. Synchronous user callback mutation cannot change the already-dispatched operation.
4. The upstream diff stays limited to product source and target-native tests.
5. Regression tests cover supported behavior rather than manufactured private-state corruption.

## Selected approach

### Pre-dispatch validation plus per-operation receipt

- Design: validate construction; for missing-key size-tracked fetches, capture the current value before Promise construction, assign it to `BackgroundFetch.__size`, and consume that receipt in `#requireSize()`.
- Owning boundary: `#backgroundFetch()` owns dispatch-time capture; `#requireSize()` owns accounting-time consumption.
- Submitted source: `364a8c1c07c9f6281fbe19943eacd261bd410fc4` over base `16b3a916662ab449d496b7b4b4f04132565d1d28`.
- Advantages: closes the demonstrated synchronous mutation window, avoids coercion, preserves later mutability, and leaves stale/no-size paths unchanged.
- Costs and risks: one internal optional receipt and validation branches; invalid constructor values now fail fast.

## Viable alternatives

### Make backgroundFetchSize immutable after construction

- Why plausible: removes later mutation ambiguity entirely.
- Why not selected: widens the public API compatibility change and conflicts with the class's general mutable-option model.
- Reopening trigger: upstream maintainer explicitly prefers immutable configuration.

### Validate only when consumed

- Why plausible: a no-size cache never needs the option.
- Why not selected: configuration validity would depend on a later operation rather than fail at construction, unlike other numeric option guards.
- Reopening trigger: upstream maintainer prefers lazy validation for unused options.

## Executed losing approaches

### Constructor-only validation

- Result: invalid construction was blocked, but synchronous `fetchMethod` mutation could still change the value before provisional accounting.
- Why it lost: time-of-check/time-of-use remained open.

### Pre-dispatch check with later public-field re-read

- Result: validation happened before dispatch, but insertion still re-read the mutable property.
- Why it lost: the current fetch had no stable accounting identity.

### Patch carrier / dependency repair variants

- Historical carriers proved behavior but introduced packaging, workflow, or `@tapjs/clock` dependency/lockfile noise.
- Why they lost: the final upstream contribution can remain a clean two-file source/test diff.

### Required exported `__size` field

- Result: runtime design was coherent, but making the field required could break external TypeScript mocks or adapters.
- Why it lost: an optional exported field plus runtime construction preserves compatibility.

### Exhaustive invalid-type and corrupted-internal tests

- Result: earlier tests enumerated many redundant runtime types and later deliberately changed an internal receipt through `unsafeExposeInternals()`.
- Why they lost: the extra cases did not establish distinct supported behaviors, and upstream explicitly warns that mutating exposed internals can cause strange breakage.
- Retained coverage: representative numeric/non-number validation, hostile non-coercion, pre-dispatch mutation, the snapshot race, zero/coalescing, and stale/no-size boundaries.

## Rejected easy answers

### Reuse `isPosInt()` directly

Zero is established compatible behavior, so the provisional size needs a nonnegative rather than strictly positive predicate.

### Coerce with `Number()`, `Math.floor()`, or global `isFinite()`

Runtime strings, symbols, and hostile objects should be rejected rather than converted into accounting values.

### Validate every refresh path

Stale refresh uses the existing entry size, and caches without size tracking do not consume the provisional option. Rejecting the field there would widen behavior without fixing the demonstrated defect.

### Read the public field again during insertion

Promise construction invokes `fetchMethod` synchronously, so re-reading afterward reopens the mutation race.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [`4708153206...`](https://redirect.github.com/isaacs/node-lru-cache/commit/4708153206daf822a3ad440ce47248b9cfbdb973) | introduce `backgroundFetchSize` and provisional accounting | merged | original feature and semantic baseline |
| [`0b0a77e992...`](https://redirect.github.com/isaacs/node-lru-cache/commit/0b0a77e99245e12c53ec0cf05e200c66e6749ba9) | reschedule an autopurge timer that fires before revised expiry | merged | adjacent repository behavior, not part of the submitted source change |
| upstream issue/PR search immediately before submission | matching repair | none found | independent candidate |

## Deferred adjacent work

- broader mutable-option snapshot policy;
- redesign of the internal `BackgroundFetch` representation;
- general hardening against deliberately corrupted internals;
- fetch cancellation ownership;
- performance interpretation beyond repository benchmark pass/fail.

## Final decision

`SUBMITTED` as upstream PR #410 by the owner. No additional upstream interaction is authorized from Fieldwork without explicit owner direction.
