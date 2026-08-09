# SWC Binary Operator Effects

## In simple words

Campaign #725 has narrowed to `instanceof` and now has **four independent correctness owners**. The same deterministic four-owner candidate has passed a consolidated six-lane exact-head matrix covering the shared utility contract, a DCE consequence, expression-simplifier extraction/folding, standalone folding, dead-branch cleanup, and minifier result-discarding.

JavaScript evaluates `instanceof` after both operands. The operator can call `Symbol.hasInstance`, and an invalid right operand throws `TypeError`. SWC's documented minifier assumptions do not authorize removing either behavior.

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
- DCE discriminator: `teamleaderleo/swc#10` at `5ef8472b24a836ded4035c619393ac0d4ac2384f`
- dead-branch discriminator: `teamleaderleo/swc#11` at `05df66c3e98a1124c6e58dd1a814467b0da7f8f5`
- separate `in` policy discriminator: `teamleaderleo/swc#6`
- retired arithmetic/coercion discriminator: `teamleaderleo/swc#5`
- deterministic four-owner candidate: `apply-instanceof-candidate.py` at `e8ec2506db64a2bdeca01ad221ce3a38d74a41c5`
- consolidated carrier: `teamleaderleo/fieldwork#771`
- focused matrix run: `31331416981`
- Evidence: `source-read`, `model-executed`, `target-executed`
- Upstream contact: prohibited for automated workers

## Assumption boundary

The arithmetic/coercion branch remains a negative result because SWC explicitly permits primitive coercion helpers and arithmetic runtime exceptions to be treated as side-effect-free during minification.

`instanceof` has no corresponding documented assumption. SWC's ES2015 `instanceof` transform also explicitly preserves `Symbol.hasInstance` semantics, providing internal precedent for treating this operator step as observable.

## Owner 1 — shared effect classification and extraction

File: `crates/swc_ecma_utils/src/lib.rs`.

Current classification checks only child effects for ordinary binary expressions. Current extraction retains short-circuit binaries whole but otherwise keeps only child effects.

Candidate:

- classify `instanceof` as operator-effectful;
- retain the complete `instanceof` expression during effect extraction.

PR #2 target evidence: exact-head base RED for classification/extraction, primitive control GREEN, candidate 3/3 GREEN, formatting GREEN, package clippy with `-D warnings` GREEN, diff-check GREEN.

Clean receipt: Fieldwork run `31330277348`, job `93287319911`.

### DCE consequence of owner 1

`crates/swc_ecma_transforms_optimization/src/simplify/dce/mod.rs` removes unused initializers when `may_have_side_effects` reports them pure.

PR #10 exact-head receipt: Fieldwork run `31331416981`, job `93290155622`.

Base RED:

- callback-capable unused `instanceof` initializer was erased;
- invalid-RHS unused initializer was erased;
- strict-equality control passed;
- 1 passed, 2 failed.

Four-owner candidate GREEN:

- 3/3 focused DCE tests passed;
- formatting, package clippy with `-D warnings`, and diff-check passed.

This is an end-to-end consequence of owner 1, not another source owner.

## Owner 2 — expression-simplifier `instanceof` folding

File: `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs`.

The dedicated `instanceof` arm folds a statically non-object LHS to `false` and known object-like values against global `Object` to `true`. Those proofs are unsafe because the RHS may throw or implement custom `Symbol.hasInstance`, and global `Object[Symbol.hasInstance]` can be replaced.

Historical precedent: upstream PR #1630 / commit `b6ff4d6f717dfb4bd41c62c7085e15ace868f296` previously narrowed another unsafe `x instanceof Object` fold.

Candidate: remove the unconditional `instanceof` fold until a stronger RHS proof exists.

PR #9 proved base RED -> candidate GREEN for the standalone fold. PR #4 then passed all 5 extraction/folding tests under the combined candidate, plus formatting, package clippy with `-D warnings`, and diff-check. Clean PR #4 receipt: run `31330277348`, job `93287319873`.

## Owner 3 — minifier main Optimizer ignored-result reduction

File: `crates/swc_ecma_minifier/src/compress/optimize/mod.rs`.

The main `Optimizer::ignore_return_value` has a generic binary fallback that reduces remaining binary operations to left/right effects. A prior candidate guarded only the Pure pass and failed; that negative result isolated this later Optimizer owner.

Candidate: preserve `instanceof` whole before the generic Optimizer binary fallback. `in` remains outside this repair.

PR #7 clean exact-head receipt: run `31330595440`, job `93288105179`.

- six direct/extracted callback/invalid-RHS `instanceof` cases retained;
- strict-equality control removed;
- focused fixture GREEN;
- formatting, package clippy with `-D warnings`, and diff-check GREEN.

Maintainer precedent: the January 2026 experiment for upstream issue #11246 patched this same Optimizer seam for `in`, guarded by `pure_getters`.

## Owner 4 — dead-branch remover local `ignore_result`

File: `crates/swc_ecma_transforms_optimization/src/simplify/branch/mod.rs`.

Its local `ignore_result` helper decomposes every non-short-circuit binary into child effects. The helper is reused by empty `if` cleanup, loop init/update cleanup, sequence pruning, empty switch handling, and related branch simplification.

Candidate: preserve `instanceof` whole before that generic non-short-circuit binary arm.

PR #11 exact-head receipt: run `31331416981`, job `93290155640`.

- base RED confirmed;
- candidate 3/3 focused dead-branch tests GREEN;
- callback and invalid-RHS `instanceof` operations retained;
- strict-equality control reduced to its normal declared-identifier child effect;
- formatting, package clippy with `-D warnings`, and diff-check GREEN.

Evidence class: `target-executed`.

## Consolidated focused matrix

Fieldwork run `31331416981` applied the same candidate `e8ec2506db64a2bdeca01ad221ce3a38d74a41c5` to six exact owned-fork research heads.

All six jobs completed successfully:

1. utility — GREEN;
2. DCE — base RED then candidate GREEN;
3. transform extraction/folding — GREEN;
4. standalone folding — GREEN;
5. dead-branch — base RED then candidate GREEN;
6. minifier — GREEN.

Every candidate lane required `git diff --check`, `cargo fmt --all -- --check`, its focused test, package clippy `--all-targets -- -D warnings`, and final diff-check.

## Existing regression expectations that encode the defect

A canonical implementation will need intentional expectation updates.

- Minifier fixture `dont_change_in_or_instanceof_expressions` contains invalid `1 instanceof 1` and `null instanceof null`, but current expected output deletes those operations while retaining invalid `in` expressions.
- Expression-simplifier `test_fold_instance_of` currently expects primitive-LHS expressions to become `false` and object-like/global-`Object` expressions to become `true`.

These snapshots should be treated as stale behavior to update, not compatibility evidence for preserving the defect.

## Current upstream check

Upstream `main` is still exactly `5bf27fd72e4667bac6cc86888b8facb8b91f8077`; the campaign pin is current and the four owner sites remain present.

Duplicate search found no public SWC report specifically describing this `Symbol.hasInstance` / discarded-result family. This is a search result, not proof of absence.

## Design direction

The behavioral candidate currently uses narrow `instanceof` guards at each owner. A cleaner canonical implementation may centralize a context-aware operator-observability predicate near `ExprCtx`, then reuse it in shared classification/extraction, dead-branch result-discarding, and minifier ignored-result handling. Owner 2's value-fold proof remains a separate concern.

This is preferable to putting policy directly on `BinaryOp`: future `in` behavior may depend on `pure_getters`, while `instanceof` currently has no comparable documented assumption.

## Current disposition

**FOUR OWNERS TARGET-PROVEN; CONSOLIDATED SIX-LANE FOCUSED MATRIX GREEN.**

Next transitions:

1. run the full `cargo test -p swc_ecma_transforms_optimization` gate under the four-owner candidate and enumerate intentional stale-expectation failures;
2. run minifier execution tests required by target-local instructions, then broader minifier fixture tests;
3. update old expectations intentionally in a canonical owned-fork candidate or exact retained patch;
4. rerun broad gates;
5. measure baseline-vs-candidate output impact on representative safe/observable `instanceof` cases;
6. compare the current four-guard implementation with a centralized operator-observability helper;
7. keep `in` separate;
8. retire temporary execution workflows after evidence transfer.

No third-party upstream mutation occurred.
