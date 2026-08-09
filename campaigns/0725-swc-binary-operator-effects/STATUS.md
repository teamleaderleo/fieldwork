# SWC Binary Operator Effects

## In simple words

Campaign #725 now has three confirmed `instanceof` correctness owners.

JavaScript evaluates `instanceof` after both operands: the operator can call `Symbol.hasInstance` or throw `TypeError` for an invalid RHS. SWC's documented minifier assumptions do not grant permission to erase those behaviors.

Target-native execution has now proved two owners GREEN under the deterministic candidate: shared effect classification/extraction and expression-simplifier folding. A third owner was isolated in the minifier's main `Optimizer::ignore_return_value`: its generic binary fallback drops the operator and keeps only child effects. The three-owner candidate preserves all six direct/extracted minifier `instanceof` cases in target execution; the last run stopped on expected-fixture blank-line formatting before clippy. The owned fixture has been normalized and a clean rerun is active.

- Campaign issue: #725
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Pinned target revision: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- current upstream main rechecked 2026-08-10: all three relevant behaviors still present
- utility contract: `teamleaderleo/swc#2` at `520d841148305d135db78912e6e176a67617b6d3`
- transform/extraction contract: `teamleaderleo/swc#4` at `2afcd4202303c373593aa319b8533fb5bdd3204b`
- minifier contract: `teamleaderleo/swc#7` at `942c1871c1c186d7a3c03c84e86b0e10b374348d`
- independent folding discriminator: `teamleaderleo/swc#9` at `8bdbf2119bc93d3e6e20d0c97d61b7c0d43f1530`
- separate `in` policy discriminator: `teamleaderleo/swc#6`
- retired assumption-bound arithmetic/coercion discriminator: `teamleaderleo/swc#5`
- active execution carrier: `teamleaderleo/fieldwork#771`, latest carrier head `521b4d4f9f70634508c4bea912956d20962d2db5`
- deterministic candidate patcher: `apply-instanceof-candidate.py` at `62e7d9cbc6aaeba41e3b7321dad9b7af134e227b`
- Evidence: `source-read`, `model-executed`, `target-executed`; clean integrated minifier receipt pending
- Upstream contact: prohibited for automated workers

## Assumption boundary

The earlier arithmetic/coercion branch remains a negative result. SWC explicitly permits primitive coercion helpers and arithmetic runtime exceptions to be treated as side-effect-free during minification.

`instanceof` has no matching documented assumption. Its operator step can:

1. call `Constructor[Symbol.hasInstance](value)`;
2. throw when the RHS is not a valid `instanceof` target.

SWC's ES2015 `instanceof` transform also explicitly preserves `Symbol.hasInstance` semantics, giving internal precedent for treating the operator step as observable.

## Owner 1 — shared effect classification and extraction

At the pinned revision, `swc_ecma_utils::may_have_side_effects` asks only about `left` and `right` for ordinary binaries. `ExprCtx::extract_side_effects_to` retains short-circuit binaries whole but otherwise extracts only child effects.

Candidate:

- classify `instanceof` as operator-effectful;
- retain the complete `instanceof` expression during effect extraction.

Exact-head target evidence:

- unmodified target: `instanceof_operator_is_effectful` RED;
- unmodified target: `extracting_effects_preserves_instanceof_operator` RED;
- primitive negative control GREEN;
- candidate: all 3 utility tests GREEN;
- `cargo fmt --all -- --check` GREEN;
- `cargo clippy -p swc_ecma_utils --all-targets -- -D warnings` GREEN after a narrow test-only `clippy::vec_box` allowance for the library-required return type.

Latest clean integrated receipt: Fieldwork run `31330277348`, job `93287319911`, exact source head `520d841148305d135db78912e6e176a67617b6d3`.

Evidence class: `target-executed`.

## Owner 2 — expression simplifier `instanceof` folding

`crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs::optimize_bin_expr` has an independent `instanceof` arm that:

- treats a statically non-object LHS as proof of `false`;
- treats a known object-like LHS against global `Object` as proof of `true`.

Neither proof is sufficient under ordinary JavaScript semantics:

- `1 instanceof 2` throws instead of yielding `false`;
- an unknown constructor can install `Symbol.hasInstance` and accept primitives;
- `Object[Symbol.hasInstance]` can be replaced at runtime, so `({}) instanceof Object` is not intrinsically `true`.

SWC previously corrected an earlier `x instanceof Object` folding defect in PR #1630 / commit `b6ff4d6f717dfb4bd41c62c7085e15ace868f296`, but the surviving folds above remain unsafe.

Candidate: remove the unconditional `instanceof` fold unless a future proof can establish ordinary RHS semantics.

Exact-head target evidence on PR #9:

- base `1 instanceof 2` folded to `false`;
- base `({}) instanceof Object` folded to `true`;
- strict-equality optimization control passed;
- candidate disabling the unconditional `instanceof` arm made all 3 tests GREEN.

The broader PR #4 transform contract then passed all 5 tests under the combined shared-helper + folding candidate, including array-sibling callback/exception preservation and the two independent fold cases. `cargo fmt`, package clippy with `-D warnings`, and `git diff --check` passed in run `31330277348`, job `93287319873`, exact head `2afcd4202303c373593aa319b8533fb5bdd3204b`.

Evidence class: `target-executed`.

## Owner 3 — minifier Optimizer ignored-result reduction

Target execution proved that direct discarded expressions disappear too:

```js
value instanceof Constructor;
value instanceof 2;
```

so literal-member extraction is not the sole owner.

The compressor runs `pure_optimizer` and then a separate main `optimizer` every iteration. A first candidate fenced the Pure pass's ignored-result helper; target execution showed that was insufficient. That negative result narrowed the owner correctly.

The confirmed owner is `crates/swc_ecma_minifier/src/compress/optimize/mod.rs::Optimizer::ignore_return_value`.

That method first has an explicit allowlist described as operations that are side-effect-free; `in` and `instanceof` are absent. Later, a generic `Expr::Bin` fallback still recursively reduces every remaining binary expression to left/right effects and discards the operator step. This is the path that removes `instanceof`.

The maintainer-triggered January 2026 experiment for upstream issue #11246 independently targeted this same optimizer ignored-result seam for `in`, guarded by `pure_getters`. That is strong local precedent for preserving an operator here when its operator step remains observable.

Candidate: insert a narrow `instanceof` arm before the generic binary fallback and return the whole expression unchanged. `in` remains outside this repair.

Expanded PR #7 fixture covers:

- two `instanceof` operations produced through literal-member extraction;
- two direct discarded `instanceof` statements;
- the same direct callback/invalid-RHS forms followed by `return` to distinguish tail placement;
- strict equality as removable control.

Target run `31330277284`, job `93287319517`, with the three-owner candidate produced exactly the desired semantic output: all six `instanceof` operations were retained and strict equality was removed. The job stopped only because the expected fixture contained blank lines between functions while the minifier emitted compact formatting, so clippy did not run.

PR #7 expected output is now normalized at head `942c1871c1c186d7a3c03c84e86b0e10b374348d`. Clean minifier and integrated reruns are active on carrier head `521b4d4f9f70634508c4bea912956d20962d2db5`.

Evidence class: `target-executed` semantic observation; clean GREEN receipt pending.

## Existing regression-data inconsistency

SWC already has a minifier fixture named `dont_change_in_or_instanceof_expressions` whose input contains invalid `1 instanceof 1` and `null instanceof null` expressions. Its pinned expected output preserves the invalid `in` expressions but deletes both invalid `instanceof` expressions.

That expected output is inconsistent with the fixture name and with JavaScript's invalid-RHS `TypeError` behavior. A production candidate should update this existing regression expectation rather than treating its current snapshot as a reason to preserve the bug.

Existing expression-simplifier unit tests likewise encode the old primitive-LHS / global-`Object` folds and will need intentional expectation updates in a full candidate.

## Current upstream check

The relevant current upstream `main` source was re-read on 2026-08-10. The unsafe expression-simplifier `instanceof` arm and the main Optimizer's generic binary ignored-result fallback are still present; no independent fix was found in recent `instanceof` commits.

Duplicate search found no public SWC report specifically describing this `Symbol.hasInstance` / discarded-result `instanceof` family. This is a search result, not proof of absence.

## Optimization consequence

The current repair is deliberately conservative: without a proof that the RHS uses ordinary built-in `instanceof` semantics, `instanceof` remains observable.

This will retain expressions that SWC currently removes or folds. That output growth is attached to cases where current optimization can change callback/exception semantics. A later optimization could recover safe cases only with a stronger proof about the RHS and `Symbol.hasInstance`; the current `ExprCtx` has no such proof.

## `in` remains separate

Owned-fork PR #6 keeps `in` on its own policy lane because existing maintainer discussion explicitly connects `in` preservation to `pure_getters`. The `instanceof` repair does not inherit that policy automatically.

## Current disposition

**THREE OWNERS CONFIRMED; TWO CLEAN GREEN; MINIFIER SEMANTIC GREEN / CLEAN RECEIPT RUNNING.**

Next transitions:

1. accept the normalized PR #7 minifier receipt only if focused test, formatting, package clippy, and diff-check all pass on exact head `942c1871c1c186d7a3c03c84e86b0e10b374348d`;
2. rerun the integrated four-lane candidate on current exact heads;
3. prepare a canonical owned-fork candidate or retained patch with the three source owners plus intentional updates to old tests that encode the unsafe behavior;
4. run broader `swc_ecma_transforms_optimization` and `swc_ecma_minifier` gates;
5. measure output impact on representative safe/unsafe `instanceof` inputs;
6. keep `in` separate;
7. retire temporary execution workflows after receipts are transferred.

No third-party upstream mutation occurred.
