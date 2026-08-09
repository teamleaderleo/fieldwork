# SWC `instanceof` Effect Consumer Map

## In simple words

The proposed `instanceof` repair changes one shared classifier and one shared effect extractor. The extractor has only two external call sites at the pinned revision, and both now have owned-fork regressions. The classifier is used more widely across minifier and optimization passes, so its main review risk is conservative retention or reduced compression rather than a new semantic transformation.

Pinned source: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`.

## `ExprCtx::extract_side_effects_to`

External consumers found by repository search:

1. `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs`
   - Used when a statically selected array member discards sibling elements while retaining their effects.
   - Covered by owned-fork PR `teamleaderleo/swc#4` at `1bfc544804d8c5f675a064f6670511973fc30f52`.

2. `crates/swc_ecma_minifier/src/compress/pure/member_expr.rs`
   - Used when literal array/object member access is simplified and discarded literal contents are reduced to their effects.
   - Covered by owned-fork PR `teamleaderleo/swc#7` at `ea9d75c2bf1effd3fb8a191c030380961a1eaa15`.

The remaining search hit is the helper's own implementation in `swc_ecma_utils/src/lib.rs`.

## `may_have_side_effects`

This classifier is used broadly across minifier and optimization code, including boolean simplification, dead-code decisions, property transforms, inlining, sequence work, literal-member optimization, unsafe transforms, and DCE.

Changing `instanceof` from operand-only purity to operator-effectful therefore has a wider optimization blast radius than the extractor change. The direction is conservative: callers that previously treated a pure-operand `instanceof` as removable or freely movable may retain it instead.

Review should specifically look for:

- output-size changes where unused `instanceof` expressions become retained;
- optimizations guarded by `may_have_side_effects` that now stop earlier;
- any caller that already has an explicit `instanceof` policy and would become redundant or contradictory.

Current source evidence already shows explicit `in` / `instanceof` handling in minifier negation and negation-cost logic, which is consistent with treating these operators as semantically distinct.

## Candidate boundary

The first repair patch changes only:

- `may_have_side_effects`: `instanceof` => effectful;
- `extract_side_effects_to`: retain `instanceof` whole.

It does not change arithmetic/coercion assumptions, `ignore_return_value`, `pure_getters`, or the separate `in` policy branch.

## Execution requirement

Before promotion, run the PR #2, #4, and #7 regressions on the pinned target, then compare affected minifier fixture output/size to quantify any conservative retention caused by the classifier change.
