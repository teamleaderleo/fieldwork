# SWC `instanceof` design review — 2026-08-10

Campaign: #725

Pinned SWC target: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`

## Decision in simple words

Keep the current narrow `instanceof` guards for the correctness repair. Do not recover the old global-constructor folds, and do not introduce a new shared public operator-policy abstraction in this patch.

The repair has one semantic rule today: ordinary `instanceof` evaluation is observable even when both operand evaluations look pure. Four destructive consumers need to preserve that operator step, while the expression simplifier must stop claiming a result unless it proves the complete `instanceof` semantics.

## Why the old folds stay removed

ECMAScript `InstanceofOperator` first requires an object RHS, then gets `@@hasInstance`, and calls that method when present. Only after that does it fall back to callable/default `OrdinaryHasInstance` behavior.

Therefore these are not sufficient proofs:

- primitive LHS => `false`;
- array/object/function literal LHS plus global `Object` RHS => `true`;
- a global constructor name such as `Object` or `Number` => standard built-in behavior.

The RHS object can expose its own `Symbol.hasInstance`, and global constructor objects are mutable values. The existing unconditional folds can therefore remove a callback, change its input, or suppress a `TypeError`.

## Small safe subset exists, but is not worth recovering here

There is a much narrower proof that could support a future optimization. A directly evaluated fresh ordinary function expression inherits the standard `Function.prototype[Symbol.hasInstance]`; that inherited method is non-writable and non-configurable. Under the default `OrdinaryHasInstance` algorithm, a non-object LHS returns `false` before the constructor `prototype` lookup.

So a compiler could in principle prove cases such as a primitive LHS against a syntactically fresh ordinary function RHS. Similar fresh-identity proofs may establish more cases.

Do not add that optimization to this repair. SWC's current fold was type-shaped, not identity/provenance-shaped, and there is no existing proof object here that establishes a fresh RHS, standard inherited `@@hasInstance`, and the required evaluation ordering. The expected size win is tiny compared with the proof surface.

A future precision patch should be separate and begin with RED/GREEN tests for the exact fresh-RHS subset it claims.

## Shared-helper decision

Earlier notes considered a context-aware operator-observability predicate near `ExprCtx`. Source review makes that a poor fit for this patch:

- `ExprCtx` currently carries unresolved-reference context, unresolved-reference safety, strict-mode state, and recursion depth;
- it does not carry minifier `pure_getters` policy;
- owner 2 (value folding) asks a different question from the four ignored-result/effect-preservation sites;
- adding a public cross-crate helper for one unconditional operator would create API/policy coupling without removing the need for owner-specific control flow.

Decision: keep the explicit `instanceof` guards in the four confirmed owners. Revisit centralization only if another operator needs the same unconditional preservation rule. If `in` joins later, pass its policy explicitly rather than smuggling `pure_getters` into general expression context.

## Fixture strategy

SWC's minifier-local instructions explicitly say new regression coverage should not be added under `tests/terser`; use SWC-owned fixture roots instead. Imported Terser fixture outputs are still part of the broad compatibility suite and must be updated when they encode the old SWC behavior, but they should not be the sole semantic contract.

The broad diagnostic exposed a `pure_funcs` relational case where `foo()` is declared pure and old output reduces `foo() instanceof bar()` to `bar()`. Declaring the call pure does not make its return value irrelevant to `instanceof`.

Fieldwork commit `89eaad96d0c206d28eec302ef214f40967fd1300` adds `add-instanceof-owned-regressions.py`, which creates an SWC-owned fixture under:

`crates/swc_ecma_minifier/tests/fixture/operator-effects/instanceof-pure-func-value/`

The fixture requires callback-capable and invalid-RHS `instanceof` operations to survive even when the LHS call is listed in `pure_funcs`, while a strict-equality control still reduces to the remaining RHS call.

## Output-impact result

The broad diagnostic showed tightly bounded drift:

- one transform unit expectation surface (`test_fold_instance_of`);
- two minifier golden fixtures (`comparing/dont_change_in_or_instanceof_expressions` and `pure_funcs/relational`);
- no unrelated minifier runtime failure across 2,612 executed cases.

After intentional expectation updates, the first hard-gate candidate passed the full optimization package, complete minifier compress fixtures, and minifier execution suite. The complete compress run reported 2,900 passed, 0 failed, 27 ignored. This means the existing fixture corpus changed output only where the investigation had already identified stale `instanceof` expectations.

## Canonical repair boundary

Include:

1. shared effect classification/extraction preservation;
2. removal of the unconditional expression-simplifier `instanceof` fold;
3. main minifier Optimizer ignored-result preservation;
4. dead-branch ignored-result preservation;
5. intentional updates to stale broad expectations;
6. SWC-owned focused regression coverage, including the `pure_funcs` value-preservation case.

Exclude:

- `in` / `pure_getters` policy;
- arithmetic/coercion assumptions;
- speculative fresh-function `instanceof` folding;
- a new shared operator-policy API.

No third-party upstream mutation is authorized or performed.
