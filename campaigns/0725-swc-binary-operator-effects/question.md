# Campaign 0725: SWC Binary Operator Effects

State: `claimed`

Campaign issue: #725

Programme: #15

Parent scout: #718

Primary target: #717

Pinned target revision: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`

Upstream contact authorized: `false`

## In simple words

SWC's shared expression helpers currently look through every ordinary binary operator when deciding whether an expression can do observable work and when extracting effects from a discarded value.

The first broad probe included arithmetic coercion and BigInt exceptions. Target-local instructions and the public minification guide establish that those behaviors are inside SWC's documented minifier assumptions: primitive coercion helpers may be treated as side-effect-free, and arithmetic exceptions such as mixed BigInt/Number operations may be discarded. Those cases are therefore retained only as research context, not as repair requirements.

The clean unresolved case is `instanceof`. Its operator step can call `Symbol.hasInstance` or throw `TypeError` for an invalid right operand. Neither behavior is covered by the documented assumption set. A separate `in` branch remains open because the existing upstream discussion connects that operator to `pure_getters` policy.

## Exact question

Can SWC preserve `instanceof` operator behavior in shared side-effect classification and effect extraction with a two-branch special case, while leaving documented arithmetic/coercion assumptions and unrelated minifier behavior unchanged?

## Current behaviour

At the pinned revision, `crates/swc_ecma_utils/src/lib.rs` has two relevant paths:

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

For `instanceof`, both paths can erase the operator step. The ordinary minifier `ignore_return_value` allowlist does not include `instanceof`, so the first repair slice does not require a minifier-specific discard change.

Other minifier code already treats `in` and `instanceof` as distinct operators in negation and boolean-cost logic, which supports a narrow shared-helper special case rather than a general operator matrix.

## Executed mechanism evidence

Node v22.16.0 established the exact `instanceof` distinction:

- whole evaluation of `value instanceof Constructor` invoked `Constructor[Symbol.hasInstance]`;
- evaluating only `value` and `Constructor` invoked no callback;
- whole evaluation of `value instanceof 2` threw `TypeError`;
- evaluating only the operands did not throw.

Evidence class: `model-executed`.

## Prepared target discriminators

### `instanceof` utility contract — `teamleaderleo/swc#2`

Head: `7f02482bdcecafdbf2b7c8d5d3667e2f9db6211b`.

Checks `may_have_side_effects` and `ExprCtx::extract_side_effects_to` for callback-capable and invalid-right-operand `instanceof`, with primitive arithmetic and strict equality as controls.

### `instanceof` expression-simplifier contract — `teamleaderleo/swc#4`

Head: `1bfc544804d8c5f675a064f6670511973fc30f52`.

Checks the concrete array-member folding consumer that extracts effects from discarded siblings. It requires both callback-capable and invalid-right-operand `instanceof` expressions to survive.

### `in` policy discriminator — `teamleaderleo/swc#6`

Head: `1ff10db31595acd540ecc769f1fd4b672dab9746`.

Keeps the `in` question separate because upstream issue 11246 remains open and a prior maintainer-triggered experiment reportedly tied preservation to `pure_getters`.

### Retired assumption-bound discriminator — `teamleaderleo/swc#5`

Closed as a negative result. Its `valueOf` and mixed BigInt/Number expectations conflict with SWC's documented minifier assumptions and therefore should not drive a repair.

## Candidate repair

The leading `instanceof` repair is intentionally tiny:

1. classify `Expr::Bin` with `instanceof` as effectful at the operator step;
2. retain the complete `instanceof` expression in `extract_side_effects_to` instead of recursively extracting only its operands;
3. leave all other binary operators unchanged in this first slice.

Prepared patch: `campaigns/0725-swc-binary-operator-effects/candidate-instanceof.patch`.

## Required evidence before implementation is promoted

- target-native RED for owned-fork PR #2;
- target-native RED for owned-fork PR #4;
- application of the two-branch candidate patch;
- GREEN receipts for both discriminators and focused affected-crate tests;
- formatting/clippy where required by the target;
- exact-head review and confirmation that no unrelated binary-operator behavior changed.

## Stop condition

Stop the first repair slice when `instanceof` classification and extraction are target-executed RED/GREEN with the minimal shared-helper patch, or when target execution shows another consumer or policy boundary is required. Keep `in` separate until its `pure_getters` contract is resolved.
