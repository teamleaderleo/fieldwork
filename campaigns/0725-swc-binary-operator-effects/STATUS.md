# SWC `instanceof` optimization campaign

## In simple words

This campaign started from a broad code-reading question about binary-expression effects in SWC and eventually split into two different `instanceof` behaviors.

The first was discarded-result behavior. SWC can reduce an unused `instanceof` expression to operand evaluation. JavaScript evaluation of the operator can invoke `Symbol.hasInstance` or throw for an invalid right operand, so the first candidate treated the operator step itself as observable across shared effect analysis, DCE, dead-branch cleanup, and minifier result dropping.

The second was value folding. SWC also had dedicated folds that inferred an `instanceof` result from operand category alone. That produces a plain wrong answer for cases such as:

```js
({ __proto__: null }) instanceof Object
```

which evaluates to `false`.

The broad candidate originally repaired both families and passed its retained target-native gates. Public maintainer feedback then clarified that SWC intentionally keeps Terser-compatible assumptions for the discarded-result path. That feedback changed the target contract for this contribution. The campaign reconciled against it and narrowed the surviving implementation to the independent constant-folding defect.

The current owned-fork follow-up is `teamleaderleo/swc@a39678bd0226a394847605b6874b1eab7ad7f32c`, tree `d2f68ef13dbd238b0ea44b7b1c0c1fb39eeea24a`. A human advanced the public contribution branch to that commit on 2026-08-15. Automated upstream contact remains prohibited.

Campaign: #725  
State: `fold-only contribution active`  
Evidence retained: `source-read`, `model-executed`, `target-executed`  
Current repair boundary: incorrect `instanceof` constant folding only

## How the finding emerged

The useful discovery path was wider than the final patch.

The SWC scout was reading ordinary binary-expression effect handling in `swc_ecma_utils`. That code largely classified a binary expression from the effects of its children. This raised a direct operator-level question: are there binary operators whose evaluation can execute behavior beyond evaluating their operands?

`instanceof` was an immediate candidate because the operator can dispatch through `Symbol.hasInstance`. `in` raised a sibling question through Proxy `has` behavior and stayed separate because its optimizer policy can differ.

Following the `instanceof` path through consumers exposed several places where the complete operation could disappear when its result was unused. That led to the original multi-owner candidate and the DCE, dead-branch, effect-extraction, and minifier discriminators.

While tracing those paths, the investigation also reached SWC's dedicated `instanceof` simplification logic. That code had a different problem: it inferred the boolean result from the apparent type or syntax of the left operand and the right operand's identity. Testing the assumption with a null-prototype object produced a minimal wrong-value case:

```js
({ __proto__: null }) instanceof Object // false
```

The existing fold could turn that result into `true`.

That second finding survives independently of any policy about discarding unused operator evaluation. It became the durable implementation repair after maintainer feedback narrowed the contribution.

## Why the first candidate became too broad

The original candidate treated four implementation owners as one repair family:

1. shared effect classification and extraction;
2. expression-simplifier `instanceof` folding;
3. minifier ignored-result reduction;
4. dead-branch ignored-result cleanup.

Target-native execution established that this candidate behaved as intended. The broad evidence remains useful because it shows exactly where SWC changes or removes `instanceof` evaluation.

Public review then supplied a target-contract fact that execution alone could not establish: SWC intentionally accepts the existing discarded-result behavior under inherited Terser-compatible optimizer assumptions.

That divided the campaign cleanly.

### Discarded result

The shared utility, DCE, minifier ignored-result, and dead-branch changes would alter an accepted optimizer contract. They were removed from the contribution.

The earlier execution evidence remains a record of behavior and ownership. It no longer supports presenting those paths as implementation defects in this contribution.

### Used result and constant folding

The dedicated value folds can manufacture the wrong boolean. That problem does not depend on discarded-result policy. The fold-only candidate removes those operand-shape proofs and keeps focused regression coverage.

This is the patch that remains active.

## Current code boundary

The fold-only contribution is intentionally small.

Production changes remain in the value-simplification paths that previously considered `instanceof` foldable from operand shape:

- `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs`;
- `crates/swc_ecma_minifier/src/compress/pure/mod.rs`.

The regression coverage keeps the null-prototype used-value case and updates the existing fold expectations. A minifier used-value fixture protects the same value-producing boundary without changing discarded-result behavior.

The following broad-candidate changes were removed during reconciliation:

- global `instanceof` effect classification in `swc_ecma_utils`;
- complete-expression preservation in shared effect extraction;
- the main minifier ignored-result guard;
- dead-branch `ignore_result` preservation;
- DCE regressions whose assertion depended on retaining unused `instanceof` evaluation;
- expectation changes whose only purpose was to preserve discarded-result operator execution.

## Evidence history

The earlier campaign work established the source ownership and exercised a deterministic multi-owner candidate through focused and broad target gates. Those receipts remain valid evidence about the candidate that ran.

After maintainer feedback, Fieldwork reopened the target contract instead of treating language-level observability as sufficient proof that every optimizer transformation was unwanted. Carrier #838 then exercised the narrowed fold-only direction. The final owned-fork follow-up was prepared as a one-commit descendant of the public contribution head and was manually pushed by the human owner.

The important evidentiary distinction is now explicit:

- broad execution proved what the original candidate changed;
- maintainer feedback established which discarded-result behavior SWC intends to retain;
- the null-prototype case establishes a separate wrong-value fold;
- the current contribution repairs only that surviving implementation defect.

## Current disposition

**FOLD-ONLY CONTRIBUTION ACTIVE.**

The campaign has completed its reconciliation step. The broad operator-effects investigation remains the discovery trail, while the active patch is scoped to incorrect `instanceof` constant folding.

Further work on discarded-result semantics would be a separate optimizer-contract discussion. It should not be smuggled back into this patch through effect classification, DCE, dead-branch cleanup, or minifier result-discard changes.

`in` remains a separate policy question.

No automated worker performed a third-party upstream write. The 2026-08-15 public branch advance was performed manually by the human owner and is recorded here after the fact.
