# SWC `instanceof` Consumer and Owner Map

## In simple words

Campaign #725 has **four independent source owners** where SWC can erase observable `instanceof` operator behavior:

1. shared effect classification/extraction in `swc_ecma_utils`;
2. unconditional `instanceof` folding in the expression simplifier;
3. the minifier main Optimizer's ignored-result binary fallback;
4. the optimization dead-branch remover's local ignored-result binary fallback.

DCE is an end-to-end consequence of owner 1, not a fifth source owner.

Pinned target/current upstream head: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`.

## Why the operator itself must survive

`instanceof` is not just evaluation of a left child and a right child. The operator can:

- reject a non-object/non-callable RHS with `TypeError`;
- retrieve and call RHS `Symbol.hasInstance`;
- pass the evaluated LHS value to that hook.

Therefore an optimizer cannot replace an unused `left instanceof right` with only the child effects unless it has separately proved the operator step unobservable.

SWC's documented arithmetic/coercion assumptions do not include such an `instanceof` assumption, and SWC's own ES2015 transform explicitly preserves `Symbol.hasInstance` semantics.

## Owner 1 — shared classification and extraction

File: `crates/swc_ecma_utils/src/lib.rs`.

Current classification asks only about child effects for ordinary binary expressions. Current extraction preserves short-circuit binaries whole and decomposes other binaries into child effects.

Repair:

- classify `instanceof` as operator-effectful;
- preserve the complete `instanceof` expression during effect extraction.

Owned utility regression: `teamleaderleo/swc#2` at `520d841148305d135db78912e6e176a67617b6d3`.

Target result: base RED -> candidate GREEN, formatting GREEN, package clippy `-D warnings` GREEN, diff-check GREEN.

### External extractor consumers

Repository search at the pinned revision found two external `extract_side_effects_to` consumers:

1. `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs` — statically selected array-member folding, covered by PR #4;
2. `crates/swc_ecma_minifier/src/compress/pure/member_expr.rs` — literal-member simplification, covered as one path in PR #7.

### DCE consequence

`crates/swc_ecma_transforms_optimization/src/simplify/dce/mod.rs` uses `may_have_side_effects` to decide whether unused initializers can be dropped.

Owned DCE regression: `teamleaderleo/swc#10` at `5ef8472b24a836ded4035c619393ac0d4ac2384f`.

Consolidated run `31331416981`, job `93290155622`:

- base erased callback-capable and invalid-RHS unused `instanceof` initializers;
- candidate passed 3/3 focused tests;
- formatting, package clippy `-D warnings`, and diff-check passed.

## Owner 2 — expression-simplifier constant folding

File: `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs`.

The old fold used two type-shaped rules:

- statically non-object LHS -> `false`;
- known object-like LHS against global `Object` -> `true`.

Those are insufficient proofs. The RHS can implement custom `Symbol.hasInstance`, can throw, and global constructor objects such as `Object` are mutable values.

Repair: remove the unconditional `instanceof` fold.

Owned regressions:

- PR #9 at `8bdbf2119bc93d3e6e20d0c97d61b7c0d43f1530` isolates folding;
- PR #4 at `2afcd4202303c373593aa319b8533fb5bdd3204b` combines folding with extraction consumers.

Historical precedent: upstream PR #1630 / commit `b6ff4d6f717dfb4bd41c62c7085e15ace868f296` previously narrowed another unsafe `x instanceof Object` fold.

### Precision decision

A small safe subset exists in principle. For example, a primitive LHS against a syntactically fresh ordinary function/arrow RHS with the standard inherited `@@hasInstance` path can be proven `false` without consulting a constructor prototype.

Do **not** recover that optimization in this correctness repair. SWC currently lacks the identity/provenance proof at this fold site, and broad regression testing shows the conservative repair has tightly bounded output drift. Any fresh-RHS optimization should be a separate patch with exact tests for the proof it claims.

## Owner 3 — minifier main Optimizer ignored-result fallback

File: `crates/swc_ecma_minifier/src/compress/optimize/mod.rs`.

The method has an explicit side-effect-free binary allowlist that excludes `in` and `instanceof`, but a later generic binary fallback still reduces remaining binaries to left/right effects.

Repair: preserve `instanceof` whole before that fallback.

Owned regression: PR #7 at `942c1871c1c186d7a3c03c84e86b0e10b374348d`.

Clean focused receipt: run `31330595440`, job `93288105179` — all six direct/extracted callback/invalid-RHS cases retained, strict-equality control removed, focused fixture + fmt + package clippy + diff-check GREEN.

Maintainer precedent: a January 2026 experiment for issue #11246 changed this same seam for `in`, guarded by `pure_getters`. That policy remains separate.

## Owner 4 — dead-branch remover local `ignore_result`

File: `crates/swc_ecma_transforms_optimization/src/simplify/branch/mod.rs`.

Its local `ignore_result` independently decomposes every non-short-circuit binary into child effects. It is reused by empty `if` cleanup, loops, sequence pruning, empty switches, and related branch transforms.

Repair: preserve `instanceof` whole before the generic binary arm.

Owned regression: PR #11 at `05df66c3e98a1124c6e58dd1a814467b0da7f8f5`.

Consolidated run `31331416981`, job `93290155640`: base RED -> candidate 3/3 GREEN, with formatting, package clippy `-D warnings`, and diff-check GREEN.

## Broad expectation drift

Diagnostic run `31331894271` exposed exactly three old expectations and no unrelated semantic failures:

1. transform `test_fold_instance_of` encoded the unsafe constant folds;
2. Terser-named `comparing/dont_change_in_or_instanceof_expressions` deleted invalid `instanceof` operations;
3. Terser-named `pure_funcs/relational` reduced `foo() instanceof bar()` to `bar()` when `foo` was declared pure.

Declaring `foo()` pure only says evaluating that call is side-effect-free; its return value is still an operand supplied to `instanceof` and can be observed by RHS `Symbol.hasInstance`.

The minifier runtime diagnostic passed 2,612 executed cases with zero failures. After intentional expectation updates, the first broad hard-GREEN candidate passed the full optimization package, complete minifier compress fixtures, and execution suite. The complete compress run reported 2,900 passed, 0 failed, 27 ignored.

## SWC-owned regression strategy

SWC's minifier-local instructions say new regressions belong in SWC-owned fixture roots rather than `tests/terser`.

Fieldwork candidate commit `89eaad96d0c206d28eec302ef214f40967fd1300` therefore adds `add-instanceof-owned-regressions.py`, creating:

`crates/swc_ecma_minifier/tests/fixture/operator-effects/instanceof-pure-func-value/`

This pins the `pure_funcs` value-preservation case independently of imported Terser snapshots:

- callback-capable `foo() instanceof bar()` survives;
- invalid-RHS `foo() instanceof 2` survives;
- strict-equality control can still reduce to the remaining RHS effect.

## Shared-helper decision

The executed repair intentionally keeps narrow `instanceof` guards at the four owners.

Do **not** introduce a new shared public operator-policy helper in this patch:

- `ExprCtx` does not carry minifier `pure_getters` policy;
- owner 2 asks a value-proof question, while owners 1/3/4 ask effect/result-discard questions;
- one unconditional operator rule does not justify new cross-crate policy API surface;
- forcing future `in` policy into general expression context would widen this correctness repair unnecessarily.

Revisit centralization only if a second operator needs the same unconditional preservation rule. Keep `in`/`pure_getters` explicit and separate.

## Canonical repair boundary

Deterministic source/expectation patcher: `apply-instanceof-candidate.py`.

Current exact candidate bundle: Fieldwork `89eaad96d0c206d28eec302ef214f40967fd1300`, containing that patcher plus the SWC-owned `pure_funcs` regression generator.

Include:

1. owner 1 classification/extraction preservation;
2. owner 2 removal of unsafe unconditional folding;
3. owner 3 main Optimizer ignored-result preservation;
4. owner 4 dead-branch ignored-result preservation;
5. intentional updates to the three stale broad expectations;
6. SWC-owned focused regressions.

Exclude:

- `in` / `pure_getters` policy;
- arithmetic/coercion assumptions;
- speculative fresh-function folding;
- a new shared operator-policy API.

## Execution state

Focused six-lane matrix: run `31331416981`, all six lanes GREEN.

Broad diagnostic: run `31331894271`, only three stale expectations surfaced.

First broad hard-GREEN run: `31344353719`, all three hard gates GREEN.

Final bundle hard gate with the new SWC-owned `pure_funcs` fixture: run `31345496191`. The full `swc_ecma_transforms_optimization` package is already GREEN on exact candidate `89eaad96d0c206d28eec302ef214f40967fd1300`; minifier compress and execution gates are completing on the same bundle.

Temporary carrier #771 is retired. Clean one-workflow fallback carrier #775 exists only if another receipt is needed.

No third-party upstream mutation occurred.
