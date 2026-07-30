# Jotai JSON cache retention selection review

## In simple words

Jotai keeps a parsed JSON value so repeated reads of unchanged storage can return the same object. The repaired candidate keeps one remembered value per storage key. This review compares how long those per-key values should remain and selects adapter-lifetime retention for the narrow repair.

## Reviewed inputs

- Fieldwork issue #235 body as read on 2026-07-31;
- canonical finding proposal in PR #272 at `1af4c49a204f2057bdf0111f1bba59481d5534c0`;
- candidate carrier PR #252 at `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`;
- exact Jotai source `56a9cc51de8a5dd762b95a145820f12589cc47c9`;
- original same-key identity repair commit `9e336c6bd2bebf257ffca957b0af18f97444323c`;
- Jotai `CONTRIBUTING.md` and `src/vanilla/utils/atomWithStorage.ts` at the exact source revision;
- Fieldwork `FINDINGS.md`, `DECISIONS.md`, and `REVIEWING.md` from canonical-finding pilot PR #264.

## Governing invariant

For one JSON storage adapter, unchanged serialized data for the same key must preserve parsed identity across unrelated-key activity, while different keys must never share mutable parsed identity merely because their bytes match.

## Decision criteria

1. Preserve the historical same-key identity behavior that protects mount/subscription consistency.
2. Remove cross-key aliasing without introducing a second lifecycle owner.
3. Keep the public storage adapter API unchanged for the narrow bug fix.
4. Keep invalidation deterministic on observed missing, malformed, or terminal removal outcomes.
5. Avoid weakening compatibility to solve an unmeasured retention risk.
6. Leave a precise reopening path for measured dynamic-key churn.

## Alternatives

### A — Adapter-lifetime per-key map

The existing candidate. It preserves same-key identity across arbitrary interleaving, isolates keys, and requires no public API. Retention lasts until key invalidation or adapter collection.

### B — Bounded or LRU cache

Paper-only. Any finite bound makes same-key identity depend on unrelated-key access order. A capacity chosen without usage evidence would replace a confirmed compatibility property with an arbitrary eviction policy.

### C — Explicit dispose or key-release authority

Paper-only. Deterministic cleanup could be useful, but it widens the public lifecycle contract and needs shared-adapter, subscription, and caller-ownership evidence. That is a separate feature/design investigation.

## Discriminating evidence

- The historical fix deliberately added unchanged-string identity reuse for one key.
- The candidate proves that per-key retention preserves that behavior across interleaved reads while eliminating cross-key aliases.
- Option B necessarily fails the historical identity criterion after sufficient unrelated-key activity.
- Option C can preserve identity, but adds public authority and complexity absent from the bug’s required repair boundary.
- No retained measurement establishes dynamic-key churn large enough to justify weakening current identity behavior.

## Independent criticism

### Retention can grow with every observed key

Accepted. The risk is real and source-visible. Its practical frequency and retained size are unmeasured. The narrow repair therefore records a bounded-key adapter expectation and a reopening trigger: representative evidence of material dynamic-key retention.

### Weak references could clean values automatically

They cannot provide deterministic identity continuity, depend on garbage-collection timing, and cannot hold primitive parsed values. They do not satisfy the contract.

### Async reads can finish out of order

That is a separate pre-existing generation-order question. The retention selection neither causes nor repairs it. It should receive its own finding when a direct source candidate exists.

## Disposition

**ACCEPT option A as the autonomous technical selection.**

Move the canonical finding from `design-decision-ready` to `delivery-gate-ready`, remove the D3 human-choice routing, and route the patch carrier through Delivery Desk D2 until it becomes a clean direct owned Jotai source branch. Then run the repository’s declared format, build, test, type, and compatibility gates and obtain independent complete-diff review.

Non-delegable human decision: none.

Reopening trigger: representative evidence that adapter instances routinely observe an unbounded or materially large dynamic key set, or a concrete caller need for explicit release authority.

Upstream contact authorized: no.
