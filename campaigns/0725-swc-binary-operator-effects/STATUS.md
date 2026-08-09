# SWC Binary Operator Effects

## In simple words

Campaign #725 has narrowed to `instanceof` and now has **four independent correctness owners**.

JavaScript evaluates `instanceof` after both operands. The operator can call `Symbol.hasInstance`, and an invalid right operand throws `TypeError`. SWC's documented minifier assumptions do not authorize removing either behavior.

Three owners are already target-executed GREEN under the retained candidate: shared effect classification/extraction, expression-simplifier `instanceof` folding, and the minifier main Optimizer's ignored-result fallback. A fourth owner was found in the optimization dead-branch remover: its local `ignore_result` helper also decomposes every non-short-circuit binary expression to child effects. An exact-head discriminator for that fourth owner is running now.

A separate DCE discriminator is also running. DCE is an end-to-end consequence of owner 1 rather than a fifth source owner: unused initializers are removed based on `may_have_side_effects`.

- Campaign issue: #725
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Pinned target/current upstream head: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- utility contract: `teamleaderleo/swc#2` at `520d841148305d135db78912e6e176a67617b6d3`
- transform extraction/folding contract: `teamleaderleo/swc#4` at `2afcd4202303c373593aa319b8533fb5bdd3204b`
- minifier contract: `teamleaderleo/swc#7` at `942c1871c1c186d7a3c03c84e86b0e10b374348d`
- folding discriminator: `teamleaderleo/swc#9` at `8bdbf2119bc93d3e6e20d0c97d61b7c0d43f1530`
- DCE discriminator: `teamleaderleo/swc#10` at `ee4c7c3289d58cdf7a9f8a856c1c86622a95fee6`
- dead-branch discriminator: `teamleaderleo/swc#11` at `35e2010575cc5f4bd87335a6096302b106f518a2`
- separate `in` policy discriminator: `teamleaderleo/swc#6`
- retired arithmetic/coercion discriminator: `teamleaderleo/swc#5`
- deterministic four-owner candidate: `apply-instanceof-candidate.py` at `e8ec2506db64a2bdeca01ad221ce3a38d74a41c5`
- consolidated execution carrier: `teamleaderleo/fieldwork#771`, four-owner workflow head `5cc2b3192cfb54bf3228dcce3dab1c2adefe1105`
- Evidence: `source-read`, `model-executed`, `target-executed`; owner-4 and DCE exact-head receipts running
- Upstream contact: prohibited for automated workers

## Assumption boundary

The earlier arithmetic/coercion branch remains a negative result. SWC explicitly permits primitive coercion helpers and arithmetic runtime exceptions to be treated as side-effect-free during minification.

`instanceof` has no matching documented assumption. Its operator step can:

1. call `Constructor[Symbol.hasInstance](value)`;
2. throw when the RHS is not a valid `instanceof` target.

SWC's ES2015 `instanceof` transform explicitly preserves `Symbol.hasInstance` semantics, giving internal precedent for treating this operator step as observable.

## Owner 1 — shared effect classification and extraction

File: `crates/swc_ecma_utils/src/lib.rs`.

Current classification asks only whether `left` or `right` has effects. Current extraction retains short-circuit binaries whole but otherwise keeps only child effects.

Candidate:

- classify `instanceof` as operator-effectful;
- retain the complete `instanceof` expression during effect extraction.

Owned contract: PR #2.

Exact-head evidence:

- base `instanceof_operator_is_effectful`: RED;
- base `extracting_effects_preserves_instanceof_operator`: RED;
- primitive control: GREEN;
- candidate: all 3 focused tests GREEN;
- formatting, package clippy with `-D warnings`, and diff-check GREEN.

Clean receipt: Fieldwork run `31330277348`, job `93287319911`, exact source head `520d841148305d135db78912e6e176a67617b6d3`.

Evidence class: `target-executed`.

### DCE consequence of owner 1

`crates/swc_ecma_transforms_optimization/src/simplify/dce/mod.rs` uses `may_have_side_effects` to decide whether unused assignment RHS values and unused variable initializers can be removed.

That creates a direct consequence: an unused initializer such as `value instanceof Constructor` can lose `Symbol.hasInstance` behavior solely because owner 1 reports the expression pure.

Owned DCE discriminator: PR #10.

Its exact-head carrier lane requires:

- base RED for callback-capable and invalid-RHS unused initializers;
- strict-equality removal as control;
- candidate GREEN using the same owner-1 classifier repair;
- formatting and package clippy.

Execution is active on the consolidated carrier.

## Owner 2 — expression-simplifier `instanceof` folding

File: `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs`.

The dedicated `instanceof` arm currently:

- folds a statically non-object LHS to `false`, preserving only RHS evaluation;
- folds a known object-like LHS against global `Object` to `true`.

Those are unsafe proofs under ordinary JavaScript semantics:

- `1 instanceof 2` throws instead of yielding `false`;
- an unknown constructor can implement `Symbol.hasInstance` and accept primitives;
- `Object[Symbol.hasInstance]` can be replaced at runtime, so `({}) instanceof Object` is not intrinsically `true`.

Historical precedent: upstream PR #1630 / commit `b6ff4d6f717dfb4bd41c62c7085e15ace868f296` previously narrowed an unsafe `x instanceof Object` fold, but the surviving folds above remain unsafe.

Candidate: remove the unconditional `instanceof` fold until a stronger RHS proof exists.

Owned discriminators: PR #9 isolates the fold; PR #4 combines folding with the extraction consumer.

Exact-head evidence:

- PR #9 base: `1 instanceof 2` became `false`; `({}) instanceof Object` became `true`;
- PR #9 strict-equality control passed;
- disabling the unconditional fold made all 3 tests GREEN;
- PR #4 then passed all 5 extraction/folding tests under the combined owner-1/owner-2 candidate;
- formatting, package clippy with `-D warnings`, and diff-check GREEN.

Clean PR #4 receipt: Fieldwork run `31330277348`, job `93287319873`, exact head `2afcd4202303c373593aa319b8533fb5bdd3204b`.

Evidence class: `target-executed`.

## Owner 3 — minifier main Optimizer ignored-result reduction

File: `crates/swc_ecma_minifier/src/compress/optimize/mod.rs`.

The compressor runs a Pure visitor and then a separate main Optimizer visitor each iteration. A first candidate guarded only the Pure ignored-result helper; target execution showed direct `instanceof` expressions still disappeared. That negative result correctly narrowed the owner.

`Optimizer::ignore_return_value` has an explicit binary allowlist described as side-effect-free; `in` and `instanceof` are absent. A later generic `Expr::Bin` fallback nevertheless reduces every remaining binary expression to left/right effects and discards the operator step.

Candidate: preserve `instanceof` whole before that generic fallback. `in` remains outside this repair.

Maintainer precedent: the January 2026 experiment for upstream issue #11246 targeted this same main Optimizer ignored-result seam for `in`, guarded by `pure_getters`.

Owned contract: PR #7.

Expanded fixture covers:

- two `instanceof` expressions produced through literal-member extraction;
- two direct discarded `instanceof` statements;
- callback/invalid-RHS direct forms followed by `return`, distinguishing placement;
- strict equality as removable control.

Clean target receipt: Fieldwork run `31330595440`, job `93288105179`, exact PR #7 head `942c1871c1c186d7a3c03c84e86b0e10b374348d`, deterministic candidate `62e7d9cbc6aaeba41e3b7321dad9b7af134e227b`.

Result:

- focused fixture GREEN: 1 passed, 0 failed, 2927 filtered out;
- all six `instanceof` operations retained;
- strict-equality control removed;
- formatting GREEN;
- `cargo clippy -p swc_ecma_minifier --all-targets -- -D warnings` GREEN;
- diff-check GREEN.

Evidence class: `target-executed`.

## Owner 4 — dead-branch remover local `ignore_result`

File: `crates/swc_ecma_transforms_optimization/src/simplify/branch/mod.rs`.

The dead-branch remover uses a local `ignore_result` helper for empty `if` statements, loop init/update expressions, sequence elements, and other result-discarding cleanup.

Its non-short-circuit binary arm recursively calls `ignore_result` on `left` and `right`, then rebuilds only child effects. This independently erases the `instanceof` operator step even if shared classification/extraction is corrected.

Owned discriminator: PR #11.

Focused cases:

- `if (value instanceof Constructor) {}` must retain `value instanceof Constructor;`;
- `if (1 instanceof 2) {}` must retain the throwing operation;
- strict equality in the same empty-branch pattern remains removable.

Candidate: preserve `instanceof` whole before the generic non-short-circuit binary arm.

Target-native base RED / candidate GREEN is running in the consolidated carrier. Until that receipt completes, owner 4 is `source-read` + `target-test-prepared`, not yet accepted `target-executed`.

## Existing regression-data inconsistency

SWC already has a minifier fixture named `dont_change_in_or_instanceof_expressions`. Its input contains invalid `1 instanceof 1` and `null instanceof null`, but its current expected output drops both `instanceof` expressions while preserving invalid `in` operations.

That expected output conflicts with the fixture name and invalid-RHS `TypeError` semantics. A canonical candidate should intentionally update this old expectation.

Existing expression-simplifier unit tests also encode primitive-LHS -> `false` and object-like/global-`Object` -> `true` behavior and will require intentional updates.

## Current upstream check

On 2026-08-10, repository history and the relevant source paths were re-read. Upstream `main` is still exactly the pinned revision `5bf27fd72e4667bac6cc86888b8facb8b91f8077`. There is no source drift between the campaign pin and current upstream head.

No public SWC issue specifically describing this `Symbol.hasInstance` / discarded-result family was found in duplicate search. This remains a search result, not proof of absence.

## Candidate boundary

The current deterministic candidate changes four semantic owners:

1. shared `instanceof` effect classification/extraction;
2. unconditional expression-simplifier `instanceof` folding;
3. main minifier Optimizer ignored-result binary reduction;
4. optimization dead-branch local `ignore_result` binary reduction.

It does not change arithmetic/coercion assumptions, `pure_getters`, or `in`.

## Current disposition

**FOUR OWNERS IDENTIFIED; OWNERS 1–3 CLEAN TARGET GREEN; OWNER 4 AND DCE EXECUTING.**

Next transitions:

1. require exact-head base RED / four-owner candidate GREEN for PR #11;
2. require DCE base RED / candidate GREEN for PR #10;
3. require the consolidated six-lane four-owner carrier to pass formatting, focused tests, package clippy, and diff-check;
4. consolidate source edits and intentional old-test expectation updates into one canonical owned-fork candidate or retained patch;
5. run broader `swc_ecma_transforms_optimization` and `swc_ecma_minifier` gates;
6. measure output impact on representative `instanceof` inputs;
7. keep `in` separate;
8. retire temporary execution workflows after evidence transfer.

No third-party upstream mutation occurred.
