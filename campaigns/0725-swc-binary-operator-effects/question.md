# Campaign 0725: SWC Binary Operator Effects

State: `claimed`

Campaign issue: #725

Programme: #15

Parent scout: #718

Primary target: #717

Owned fork contract draft: `teamleaderleo/swc#2`

Pinned target revision: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`

Upstream contact authorized: `false`

## In simple words

SWC has shared helpers that decide whether evaluating an expression can do observable work and, separately, which pieces of an expression must be kept when its value is discarded.

For ordinary binary expressions, both helpers currently look through the operator. `may_have_side_effects` checks only the operands, while `extract_side_effects_to` keeps only operand effects for every non-short-circuit binary operator. JavaScript operators can themselves invoke user code, coerce values, or throw. That means a later optimization can erase behavior even when evaluating the operand expressions alone looks harmless.

The campaign will make one invariant explicit: **operator-originated behavior must survive both effect classification and effect extraction.** Primitive operations that are proven effect-free should remain optimizable.

## Exact question

Which SWC binary operators can perform observable work after their operands are evaluated, which consumers depend on the current whole-expression effect contract, and what is the smallest correction that preserves callbacks, coercion, and exceptions while retaining safe primitive optimizations?

## Current behaviour

At the pinned revision, `crates/swc_ecma_utils/src/lib.rs` contains two independent binary-expression paths:

```rust
// Effect classification
Expr::Bin(BinExpr { left, right, .. }) => {
    left.may_have_side_effects(ctx) || right.may_have_side_effects(ctx)
}

// Effect extraction
Expr::Bin(BinExpr { op, .. }) if op.may_short_circuit() => {
    to.push(Box::new(expr));
}
Expr::Bin(BinExpr { left, right, .. }) => {
    self.extract_side_effects_to(to, *left);
    self.extract_side_effects_to(to, *right);
}
```

The minifier also has a value-discarding path in `crates/swc_ecma_minifier/src/compress/pure/misc.rs` that recursively reduces `+`, `-`, `*`, `%`, `**`, bitwise and shift operators, loose and strict equality, and relational comparisons to their operands when the result is unused.

## Executed mechanism evidence

A Node v22.16.0 probe demonstrated operator-originated callbacks for:

- Proxy `has` through `in`;
- `Symbol.hasInstance` through `instanceof`;
- object-to-primitive conversion through arithmetic, relational comparison, and loose equality.

Separate controls demonstrated operator-originated `TypeError` for:

- `1 in 2`;
- `1 instanceof 2`;
- `Symbol() + 1`;
- `1n + 1`.

Evidence class: `model-executed`.

The existing public `in` report is recorded in the campaign issue through a quiet redirect reference. No additional upstream interaction is required for this campaign.

## Prepared target discriminator

Owned fork draft `teamleaderleo/swc#2` adds `crates/swc_ecma_utils/tests/operator_effects.rs` at head `9ad27ab47b7f9a6c77bdcc67fac173efff2f78c8`.

It asks the shared classifier to retain callback/coercion-capable operations and keeps primitive controls such as `1 + 2`, strict equality, and boolean short-circuit expressions as negative controls.

The next test revision should also call `ExprCtx::extract_side_effects_to` directly so classification and extraction are protected by the same regression packet.

Evidence class: `target-test-prepared`.

## Competing repair directions

1. **Shared operator-aware effect analysis.** Classify the whole binary operation using operator semantics plus available type proofs, then make extraction preserve the complete expression whenever the operator itself can have an effect.
2. **Split contracts.** Introduce an explicit distinction between child-evaluation purity and whole-expression purity so callers state which question they need.
3. **Consumer protection.** Leave the shared helper broad and guard only consequential optimization paths. This is smaller locally but risks retaining inconsistent assumptions across consumers.

The campaign will choose after the operator matrix and consumer map show the review and optimization cost of each direction.

## Required evidence before implementation is promoted

- operator matrix covering callback, coercion, exception, short-circuit, and primitive-control cases;
- direct target-native RED evidence for classification and extraction;
- map of consequential consumers that discard, move, duplicate, or simplify expressions;
- candidate repair with primitive negative controls;
- focused target execution and exact-head review;
- a small output-size or optimization comparison if the shared classifier becomes more conservative.

## Stop condition

Stop when one bounded repair can preserve whole-expression effects through classification and extraction with explicit primitive controls, or when source/test evidence shows the shared correction would be unsound and a narrower consumer boundary is required.
