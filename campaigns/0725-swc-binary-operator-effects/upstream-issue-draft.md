# Working upstream issue draft

Status: **draft — not submitted upstream**

Prospective title: **Optimizer can discard observable `instanceof` operations**

Prospective implementation branch: https://github.com/teamleaderleo/swc/tree/fix/instanceof-observable-effects

Prospective diff: https://github.com/teamleaderleo/swc/compare/main...fix/instanceof-observable-effects

Exact candidate commit: `3724575f1b20df8b79a742e118f2424f8ca932a6`

Exact-candidate validation: https://github.com/teamleaderleo/fieldwork/actions/runs/31386704989

---

## Describe the bug

SWC can remove or constant-fold `instanceof` expressions in cases where evaluating the `instanceof` operation itself is observable.

This does **not** mean ordinary used-result code such as `if (value instanceof Constructor) { ... }` is generally removed. The problem appears when optimization determines that the boolean result is unused, or when the expression simplifier attempts to infer the result from operand shape alone.

For example, `instanceof` may invoke a user-defined `Symbol.hasInstance` method:

```js
const Matcher = {
    [Symbol.hasInstance](value) {
        console.log("checked", value);
        return false;
    }
};

value instanceof Matcher;
```

Even though the boolean result is unused, the `Symbol.hasInstance` call must still occur.

Likewise:

```js
1 instanceof 2;
```

must throw a `TypeError`. Removing the expression changes observable control flow.

## Affected optimization paths

I found four independent places that can lose these semantics:

1. `swc_ecma_utils` binary-expression side-effect classification and extraction inspect the operands of ordinary binary expressions but do not represent effects caused by executing the operator itself.
2. The expression simplifier has a dedicated `instanceof` fold that treats primitive LHS values as `false` and known object-like values against global `Object` as `true`.
3. `swc_ecma_minifier::Optimizer::ignore_return_value` has a generic binary fallback that preserves operand effects while dropping the binary operation.
4. The dead-branch simplifier's local `ignore_result` performs a similar decomposition for non-short-circuit binary expressions.

DCE is also affected downstream because it relies on the shared side-effect classifier.

Examples that exercise these paths include unused expression statements, unused variable initializers, empty branches, and expressions whose value becomes irrelevant after another simplification.

## Why this is observable

ECMAScript's `InstanceofOperator` does more than compare the two operands. It can retrieve and call the RHS `@@hasInstance` method and can throw when the RHS is invalid.

SWC already recognizes this semantic requirement in its ES2015 `instanceof` transform, which uses an `_instanceof` helper specifically to preserve `Symbol.hasInstance` behavior.

## Related SWC history

This appears to extend several earlier `instanceof` correctness fixes rather than duplicate them:

- #1630 fixed an overly broad `x instanceof Object` simplification in 2021, but retained narrower type-based `instanceof` folds.
- #2836 / #3728 fixed `Symbol.hasInstance` result handling in the ES5 `_instanceof` helper.
- #11246 concerns the analogous possibility of dropping an `in` operation that invokes a Proxy `has` trap. That issue has separate `pure_getters` policy considerations and is not part of this proposed repair.

I did not find an existing issue specifically covering discarded-result `instanceof` semantics across the optimizer paths above. That is a search result, not proof that no duplicate exists.

## Proposed behavior

Treat ordinary `instanceof` evaluation as observable when its result is discarded, and avoid unconditional type-only `instanceof` constant folding unless the optimizer has a proof covering the complete RHS `@@hasInstance` semantics.

This should not disable ordinary binary-expression cleanup or change `in` / `pure_getters` policy.

## Reproduction / candidate

A source-only candidate is available here:

- branch: https://github.com/teamleaderleo/swc/tree/fix/instanceof-observable-effects
- diff: https://github.com/teamleaderleo/swc/compare/main...fix/instanceof-observable-effects
- exact commit: https://github.com/teamleaderleo/swc/commit/3724575f1b20df8b79a742e118f2424f8ca932a6

The exact commit has passed formatting/diff checks, the full `swc_ecma_transforms_optimization` package, the complete minifier compress suite, and the minifier JavaScript execution suite in Fieldwork run `31386704989`.

No upstream issue has been opened from this draft yet.
