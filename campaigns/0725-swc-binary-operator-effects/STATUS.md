# SWC Binary Operator Effects

## In simple words

Campaign #725 is investigating a shared SWC effect-analysis boundary. Source reading now shows three places where binary operator behavior can disappear: `may_have_side_effects` ignores the operator, `extract_side_effects_to` reduces most binary expressions to operand effects, and the minifier's `ignore_return_value` independently decomposes a broad allowlist when an expression result is unused.

The campaign now has three owned-fork discriminators: `teamleaderleo/swc#2` for the shared utility contract, `teamleaderleo/swc#4` for expression-simplifier array-member folding, and `teamleaderleo/swc#5` for ordinary minifier expression statements. PR #5 includes a runtime oracle that expects discarded `+` and loose `==` coercions to execute and mixed BigInt/Number `+` to throw, while strict equality remains a negative control.

Rust execution remains pending because the connected GitHub interface reports no workflow runs for the current research heads.

- Campaign issue: #725
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Public source pin: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Utility contract: `teamleaderleo/swc#2` at `b5c1ef85cc8e7064fbc747c114b515df37a31a44`
- Expression-simplifier contract: `teamleaderleo/swc#4` at `f37dc8580458869eed38fc398b96d82976963745`
- Minifier discarded-result contract: `teamleaderleo/swc#5` at `7af17fada62c66d66dc96d981f4c2ef1dba43765`
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

Classification, extraction, and value-discarding optimization all need to preserve that invariant.

## Source findings

### Shared classification

`swc_ecma_utils::may_have_side_effects` handles every `Expr::Bin` by checking only `left` and `right`. The operator is absent from the decision.

### Shared extraction

`ExprCtx::extract_side_effects_to` retains short-circuit binary expressions whole, but every other binary expression is recursively reduced to effects from `left` and `right`. This can erase `in` / `instanceof` hooks, object-to-primitive conversion, and operator-thrown exceptions.

### Minifier value-discarding path

`swc_ecma_minifier::compress::pure::misc::ignore_return_value` has its own reducible operator allowlist covering arithmetic, exponentiation, bitwise/shift, loose and strict equality, and relational operators. It recursively ignores the left and right values and can drop the whole expression when both children disappear.

`Pure::visit_mut_expr_stmt` sends ordinary expression statements through `ignore_return_value`, so the consequence reaches normal minification directly. A discarded expression such as an object-coercing `+`, loose `==`, or `1n + 1` can lose behavior even without the expression-simplifier array-folding path.

### Expression-simplifier consumer

`swc_ecma_transforms_optimization::simplify::expr` uses `ExprCtx::extract_side_effects_to` when replacing a statically selected array element. Effects from elements before and after the chosen element are extracted, then the selected value is substituted.

That produces a concrete candidate reproduction:

```js
[
  ({ [Symbol.toPrimitive]() { log(); return 1; } }) + 1,
  42,
][1]
```

The original executes the conversion before yielding `42`. Extracting only the binary operands can erase the conversion step and leave `42` alone.

## Executed JavaScript evidence

Node v22.16.0 probes established operator-originated behavior across the main non-short-circuit families. Object conversion occurs for arithmetic, exponentiation, bitwise/shift, relational comparison, and loose equality; `in` performs property-key conversion and can invoke Proxy `has`; `instanceof` can invoke `Symbol.hasInstance`; strict equality performs no object-to-primitive conversion.

Pure-literal exception controls established mixed BigInt/Number `TypeError`s, BigInt division/remainder-by-zero and negative-exponent `RangeError`s, BigInt unsigned-shift `TypeError`, and invalid-right-operand `TypeError`s for `in` and `instanceof`.

A direct discarded-result probe re-confirmed the minifier contract independently of SWC: discarded object `+` and loose `==` expressions still called `Symbol.toPrimitive`, and discarded `1n + 1` still threw `TypeError`.

Evidence class: `model-executed`.

## Negative controls

Strict equality is the strongest operator-level negative control because it compares without object-to-primitive conversion. Primitive arithmetic is also safe when operand types and values rule out conversion hooks and numeric-domain exceptions.

Short-circuit logical operators already have a distinct extractor branch that preserves the whole expression, so they remain separate from this non-short-circuit repair.

## Prepared target contracts

### Utility layer — `teamleaderleo/swc#2`

Pins whole-expression side-effect classification and extraction for `in`, `instanceof`, object coercion, operator exceptions, and primitive negative controls.

### Expression simplifier — `teamleaderleo/swc#4`

Pins discarded array-sibling `+`, loose `==`, and mixed BigInt/Number exception behavior through `ExprCtx::extract_side_effects_to`, with strict equality as the drop control.

### Minifier statement discard — `teamleaderleo/swc#5`

Adds a `side_effects`-only minifier fixture. The input records `valueOf` callbacks for discarded `+` and loose `==`, catches the `1n + 1` exception into state, includes a strict-equality negative control, and prints the result. The runtime oracle expects:

```text
plus,eq true
```

The expected optimized output retains the two coercing expressions and the throwing BigInt expression while dropping the inert strict-equality expression.

All three branches are `target-test-prepared`; no target-native RED receipt is claimed yet.

## Upstream context

Upstream issue `swc-project/swc#11246` remains open for `in` removal. A maintainer-triggered automation branch in January 2026 prepared a narrow `in` / `pure_getters` correction, but the campaign evidence shows the underlying effect contract spans more operators and multiple consumers.

## Current repair decision

A one-line `in` special case is insufficient. The repair needs a shared answer to two questions:

1. can this particular operator evaluation itself be observable after child evaluation?
2. if yes, must classification, extraction, or result-discarding keep the whole operation?

A shared operator-aware predicate remains the leading direction. It should begin conservatively and use established type/value proofs only where they rule out callbacks and exceptions. The minifier's independent `ignore_return_value` path needs to consume the same semantic answer or be fenced equivalently.

## Execution status

The inherited SWC `CI.yml` listens to pull-request opened/reopened/synchronize events. The connected GitHub interface reports no workflow runs for PRs #2, #4, or #5, including the new PR #5 head. No `target-executed` or `full-gate` claim is made.

## Current disposition

**EXECUTE** the three prepared contracts on the pinned target revision. Require base RED evidence for the utility, expression-simplifier, and ordinary minifier paths before production implementation. Then apply a bounded operator-aware repair, obtain GREEN receipts, and measure compression loss from any conservative retention before promotion.
