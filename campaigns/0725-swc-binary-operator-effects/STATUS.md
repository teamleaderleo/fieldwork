# SWC Binary Operator Effects

## In simple words

Campaign #725 is investigating a shared SWC effect-analysis boundary. Source reading now shows that binary operator behavior can be lost twice: first when `may_have_side_effects` ignores the operator, and again when `extract_side_effects_to` replaces a non-short-circuit binary expression with effects extracted only from its operands.

The operator matrix now covers callbacks, coercion, and exceptions across the main non-short-circuit families. A concrete expression-simplifier consumer also uses the shared extractor while folding array element access, giving the campaign an end-to-end path where an operator-originated effect can disappear.

The owned fork contract draft is `teamleaderleo/swc#2`. Its test packet now checks whole-expression classification, effect extraction, operator exceptions, and primitive controls. Rust execution remains pending.

- Campaign issue: #725
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Public source pin: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Owned contract draft: `teamleaderleo/swc#2`
- Owned contract head: `b5c1ef85cc8e7064fbc747c114b515df37a31a44`
- Evidence: `source-read`, `model-executed`, `target-test-prepared`
- Upstream contact: prohibited for automated workers

## Current invariant

```text
operand evaluation
      ↓
binary operator step ── callback / coercion / throw
      ↓
result

If the result is discarded, the operator step still has to happen whenever
JavaScript semantics make that step observable.
```

Both classification and extraction must preserve that invariant.

## Source findings

### Shared classification

`swc_ecma_utils::may_have_side_effects` handles every `Expr::Bin` by checking only `left` and `right`. The operator is absent from the decision.

### Shared extraction

`ExprCtx::extract_side_effects_to` retains short-circuit binary expressions whole, but every other binary expression is recursively reduced to effects from `left` and `right`. This can erase `in` / `instanceof` hooks, object-to-primitive conversion, and operator-thrown exceptions.

### Minifier value-discarding path

`swc_ecma_minifier::compress::pure::misc::ignore_return_value` has its own reducible operator allowlist. It includes arithmetic, exponentiation, bitwise/shift, loose/strict equality, and relational operators. It recursively ignores the left and right values and can drop the whole expression when both children disappear.

This is a separate consequential consumer from the shared extractor and needs its own regression fence.

### Expression-simplifier consumer

`swc_ecma_transforms_optimization::simplify::expr` uses `ExprCtx::extract_side_effects_to` when replacing a statically selected array element. Effects from elements before and after the chosen element are extracted, then the selected value is substituted.

That produces a concrete candidate reproduction:

```js
[
  ({ [Symbol.toPrimitive]() { log(); return 1; } }) + 1,
  42,
][1]
```

The original must execute the conversion before yielding `42`. Extracting only the binary operands can erase the conversion step and leave `42` alone.

## Executed operator matrix

A Node v22.16.0 probe used an object with `Symbol.toPrimitive` and recorded callback execution.

| Family | Operators probed | Operator callback observed |
| --- | --- | --- |
| addition | `+` | yes, `default` hint |
| numeric arithmetic | `- * / % **` | yes, `number` hint |
| bitwise and shifts | `& | ^ << >> >>>` | yes, `number` hint |
| relational | `< <= > >=` | yes, `number` hint |
| loose equality | `== !=` | yes, `default` hint |
| strict equality | `=== !==` | no |
| property presence | `in` | yes, property-key conversion; Proxy `has` is an additional hook |
| instance test | `instanceof` | yes with `Symbol.hasInstance` |

Pure-literal exception controls also established:

- mixed BigInt/Number arithmetic, exponentiation, bitwise, and signed-shift operations throw `TypeError`;
- BigInt unsigned right shift throws `TypeError`;
- BigInt division or remainder by zero throws `RangeError`;
- BigInt negative exponentiation throws `RangeError`;
- invalid right operands for `in` and `instanceof` throw `TypeError`.

A second model compared whole evaluation with child-only evaluation. `obj + 1` ran `valueOf` while evaluating `obj` then `1` did not; `1n + 1` threw while evaluating `1n` then `1` did not; `'x' in proxy` ran the Proxy `has` trap while evaluating the two operands separately did not.

Evidence class: `model-executed`.

## Negative controls

Strict equality is the strongest operator-level negative control because it compares without object-to-primitive conversion. Primitive arithmetic is also safe when the operand types and values rule out conversion hooks and numeric-domain exceptions.

Short-circuit logical operators already have a distinct extractor branch that preserves the whole expression, so they should remain separate from the non-short-circuit repair.

## Prepared target contract

`teamleaderleo/swc#2` now asks the utility layer to preserve:

- `in` and `instanceof` operator callbacks;
- object coercion through arithmetic, relational comparison, and loose equality;
- pure-literal operator exceptions such as `1 in 2`, `1 instanceof 2`, and `1n + 1`;
- the complete binary expression when `extract_side_effects_to` is asked to retain those effects.

Primitive `1 + 2` and `1 === 2` remain extraction controls.

## Current repair decision

A one-line `in` special case is insufficient. The repair needs a shared answer to two questions:

1. can this particular operator evaluation itself be observable after child evaluation?
2. if yes, must effect extraction retain the whole binary expression?

A type-aware shared helper is currently the leading direction because both classification and extraction need the same answer. The implementation should begin conservatively and use established type/value proofs only where they rule out callbacks and exceptions.

## Current disposition

**EXECUTE** the expanded utility contract and add an expression-simplifier end-to-end regression before promoting implementation. Measure any compression loss if the shared operator guard becomes more conservative.
