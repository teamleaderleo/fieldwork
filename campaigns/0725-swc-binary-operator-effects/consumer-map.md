# SWC `instanceof` Consumer and Owner Map

## In simple words

The `instanceof` campaign no longer has a two-helper repair. Target execution identified three independent places where SWC can erase observable operator behavior:

1. shared effect classification/extraction in `swc_ecma_utils`;
2. an `instanceof` constant-fold arm in the expression simplifier;
3. the minifier main Optimizer's ignored-result binary fallback.

The shared extractor still has only two external call sites at the pinned revision, and both have owned-fork regressions. The shared classifier is used much more widely, so its main review risk is conservative retention. The other two owners actively rewrite or delete the `instanceof` operation and need their own correction.

Pinned source: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`.

## Owner 1 — `ExprCtx::may_have_side_effects`

Current binary classification asks only whether the left or right operand has effects. The `instanceof` operator step is absent from the decision.

Candidate: classify `instanceof` as effectful.

Why: `Symbol.hasInstance` callbacks and invalid-RHS exceptions occur after operand evaluation.

This classifier is used broadly across minifier and optimization code, including DCE, boolean work, property transforms, inlining, sequences, member optimization, and other destructive decisions. The candidate is conservative: callers may retain an `instanceof` that was previously considered pure.

Owned regression: `teamleaderleo/swc#2` at `520d841148305d135db78912e6e176a67617b6d3`.

Status: target-executed GREEN under the deterministic candidate, including package clippy with `-D warnings`.

## Owner 1b — `ExprCtx::extract_side_effects_to`

Current extraction preserves short-circuit binary expressions whole, then decomposes other binaries into child effects. That loses the complete `instanceof` operation.

Candidate: preserve the whole `instanceof` expression.

External consumers found by repository search:

1. `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs`
   - Used when a statically selected array member discards sibling elements while retaining effects.
   - Covered by `teamleaderleo/swc#4` at `2afcd4202303c373593aa319b8533fb5bdd3204b`.

2. `crates/swc_ecma_minifier/src/compress/pure/member_expr.rs`
   - Used when literal array/object member access is simplified and discarded literal contents are reduced to effects.
   - Covered as one input path in `teamleaderleo/swc#7`, current head `942c1871c1c186d7a3c03c84e86b0e10b374348d`.

The remaining repository-search hit is the helper implementation itself.

## Owner 2 — expression-simplifier constant folding

File: `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs`.

`optimize_bin_expr` has a dedicated `instanceof` branch that currently:

- folds a statically non-object LHS to `false`, preserving only RHS evaluation;
- folds a known object-like LHS against global `Object` to `true`.

Those are not valid proofs of the operator result under ordinary JavaScript semantics. The RHS can be invalid or provide custom `Symbol.hasInstance`, and global `Object` can have its own `Symbol.hasInstance` replaced.

Candidate: remove the unconditional `instanceof` fold. A future optimized case should require a stronger RHS proof.

Owned regressions:

- `teamleaderleo/swc#9` at `8bdbf2119bc93d3e6e20d0c97d61b7c0d43f1530` isolates the fold;
- `teamleaderleo/swc#4` also carries the fold cases alongside extraction consumers.

Status: target-executed RED -> GREEN. PR #4 passed 5/5 focused tests plus package clippy under the combined owner-1/owner-2 candidate.

Historical precedent: upstream PR #1630 / commit `b6ff4d6f717dfb4bd41c62c7085e15ace868f296` previously narrowed an unsafe `x instanceof Object` fold, but the surviving cases remain unsafe.

## Owner 3 — minifier main Optimizer ignored-result fallback

File: `crates/swc_ecma_minifier/src/compress/optimize/mod.rs`.

The compressor runs a Pure visitor and then a separate main Optimizer visitor each iteration. Target experiments first guarded the Pure pass ignored-result helper; direct `instanceof` statements still disappeared. That was a useful negative result and ruled out the Pure helper as the complete owner.

The main `Optimizer::ignore_return_value` first lists binary operations considered side-effect-free. `in` and `instanceof` are absent from that allowlist. Later, however, a generic `Expr::Bin` fallback recursively keeps only left/right effects and discards the operator step for every remaining binary.

Candidate: before that fallback, preserve `instanceof` whole:

```rust
Expr::Bin(BinExpr {
    op: op!("instanceof"),
    ..
}) => {
    return Some(e.take());
}
```

This keeps the `in` policy separate.

Owned regression: `teamleaderleo/swc#7`, current head `942c1871c1c186d7a3c03c84e86b0e10b374348d`.

The expanded fixture covers:

- two `instanceof` operations produced through member extraction;
- two direct discarded `instanceof` statements;
- two direct forms followed by `return`, distinguishing tail placement;
- strict equality as removable control.

A target run with the three-owner candidate preserved all six `instanceof` operations and removed the strict-equality control. That run stopped on blank-line-only expected-output formatting before clippy. The expected fixture is normalized and the clean rerun is active.

Strong local precedent: the maintainer-triggered January 2026 experiment for upstream issue #11246 patched this same Optimizer ignored-result seam to preserve `in` unless `pure_getters` allowed removal.

## Existing tests that encode old behavior

A production candidate will intentionally change existing expectations, not merely add new regressions.

### Minifier fixture

`crates/swc_ecma_minifier/tests/terser/compress/comparing/dont_change_in_or_instanceof_expressions/`

Its input contains invalid `1 instanceof 1` and `null instanceof null`, but current expected output drops them while preserving invalid `in` operations. That is inconsistent with the fixture name and invalid-RHS `TypeError` semantics.

### Expression simplifier unit tests

Existing `test_fold_instance_of` cases encode primitive-LHS -> `false` and object-like-LHS/global-`Object` -> `true` folds. These expectations must be updated when the production candidate disables the unsafe fold.

## Current candidate fence

The deterministic patcher currently changes only the three confirmed semantic owners:

- shared classification: `instanceof` is effectful;
- shared extraction: preserve `instanceof` whole;
- expression simplifier: remove unconditional `instanceof` constant folding;
- main minifier Optimizer: preserve `instanceof` before generic ignored-result binary decomposition.

It does not change arithmetic/coercion assumptions, `pure_getters`, or `in`.

## Review and execution requirements

Before promotion:

- obtain a clean exact-head PR #7 minifier test + fmt + package-clippy receipt;
- rerun the integrated utility/transform/folding/minifier candidate on current exact research heads;
- update existing old-behavior tests intentionally in a canonical candidate;
- run broader `swc_ecma_transforms_optimization` and `swc_ecma_minifier` gates;
- inspect the complete candidate diff;
- compare representative output size/optimization changes;
- retain the separate `in` policy lane.
