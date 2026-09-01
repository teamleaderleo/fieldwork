# Working upstream PR draft

Status: **draft — not submitted upstream**

Prospective title: **fix(es): preserve observable `instanceof` semantics during optimization**

Prospective implementation branch: https://github.com/teamleaderleo/swc/tree/fix/instanceof-observable-effects

Prospective diff: https://github.com/teamleaderleo/swc/compare/main...fix/instanceof-observable-effects

Exact candidate commit: `3724575f1b20df8b79a742e118f2424f8ca932a6`

Exact-candidate validation: https://github.com/teamleaderleo/fieldwork/actions/runs/31386704989

---

## Description

Preserve `instanceof` operations when optimization discards their boolean result, and stop constant-folding `instanceof` solely from operand shape.

Executing `instanceof` can itself be observable: the RHS may provide `Symbol.hasInstance`, and invalid right operands throw `TypeError`. Several optimization paths currently preserve only the effects of the left and right operands and can therefore drop the operator step.

This patch keeps the repair deliberately narrow.

## Changes

- Treat `instanceof` as potentially effectful in shared expression effect classification.
- Preserve the complete `instanceof` expression during shared side-effect extraction.
- Remove the unconditional expression-simplifier `instanceof` fold.
- Preserve `instanceof` in `Optimizer::ignore_return_value` before the generic binary-expression fallback.
- Preserve `instanceof` in dead-branch `ignore_result` before its generic non-short-circuit binary fallback.
- Update the existing expression-simplifier unit test so `instanceof` is not folded without a complete semantic proof.
- Update existing minifier expectations that encoded the previous behavior.
- Add an SWC-owned regression covering discarded `instanceof`, invalid RHS behavior, `pure_funcs`, and an ordinary `===` control.
- Add the required patch changeset for `swc_core`, `swc_ecma_minifier`, `swc_ecma_transforms_optimization`, and `swc_ecma_utils`.

## Why remove the existing folds?

Facts such as:

```js
1 instanceof Constructor
({}) instanceof Object
```

do not by themselves prove the complete `instanceof` result.

The RHS may expose custom `Symbol.hasInstance` behavior, and invalid RHS values may throw.

There are narrower `instanceof` cases that could theoretically be proven safe, but recovering those optimizations requires reasoning about the identity/provenance of the exact RHS value and its `@@hasInstance` behavior rather than only operand types. That precision work is intentionally left for a separate change.

## Scope

This change does not alter:

- `in` handling or `pure_getters`;
- SWC's documented arithmetic/coercion assumptions;
- ordinary binary-expression removal where the operator itself has no relevant observable behavior;
- the common used-result `value instanceof Constructor` case except where an existing unsafe constant fold would otherwise apply.

The patch does not introduce a new generalized binary-operator effect abstraction. The four local guards correspond to four independently confirmed consumers, while value folding remains a separate proof question.

## Regression coverage

The new SWC-owned minifier fixture uses:

```json
{
    "defaults": false,
    "pure_funcs": ["foo"],
    "side_effects": true
}
```

with input equivalent to:

```js
function callback() {
    foo() instanceof bar();
}

function invalid() {
    foo() instanceof 2;
}

function control() {
    foo() === bar();
}
```

Expected behavior preserves both `instanceof` operations while still reducing the strict-equality control to `bar();`.

This verifies that the patch does not globally disable ignored-result binary optimization.

## Related history

- #1630 previously narrowed an unsafe `instanceof Object` optimization.
- #2836 / #3728 fixed `Symbol.hasInstance` handling in SWC's `_instanceof` compatibility helper.
- #11246 covers related `in` / Proxy semantics but has separate minifier-policy considerations.

## Validation

The proposed branch is one source-only commit on SWC base:

```text
5bf27fd72e4667bac6cc86888b8facb8b91f8077
```

Exact prospective commit:

```text
3724575f1b20df8b79a742e118f2424f8ca932a6
```

Fieldwork run `31386704989` checked out that literal commit directly; no patch applicator or reconstructed candidate was used.

The exact commit passed:

```text
cargo fmt --all -- --check
git diff --check
cargo test -p swc_ecma_transforms_optimization --no-fail-fast
cargo test -p swc_ecma_minifier --no-fail-fast --test compress --features concurrent
./scripts/exec.sh
```

Observed results:

- optimization package test binaries: **515 passed, 0 failed, 106 ignored** in aggregate;
- minifier compress: **2901 passed, 0 failed, 27 ignored**;
- minifier JavaScript execution: **2612 passed, 0 failed** across the two execution groups;
- final `git diff --check`: passed.

The native `simplify::expr::tests::test_fold_instance_of` and the new SWC-owned `instanceof_pure_func_value` fixture both pass on the literal prospective commit.

## Review links

- branch: https://github.com/teamleaderleo/swc/tree/fix/instanceof-observable-effects
- diff: https://github.com/teamleaderleo/swc/compare/main...fix/instanceof-observable-effects
- exact commit: https://github.com/teamleaderleo/swc/commit/3724575f1b20df8b79a742e118f2424f8ca932a6
- exact-green run: https://github.com/teamleaderleo/fieldwork/actions/runs/31386704989

No upstream PR has been opened from this draft yet.
