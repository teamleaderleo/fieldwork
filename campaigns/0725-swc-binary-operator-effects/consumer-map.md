# SWC `instanceof` Consumer and Owner Map

## In simple words

Target execution has identified **four independent source owners** where SWC can erase observable `instanceof` operator behavior:

1. shared effect classification/extraction in `swc_ecma_utils`;
2. unconditional `instanceof` folding in the expression simplifier;
3. the minifier main Optimizer's ignored-result binary fallback;
4. the optimization dead-branch remover's local ignored-result binary fallback.

A fifth research surface, DCE, is an end-to-end consequence of owner 1: it removes unused initializers according to `may_have_side_effects` and therefore needs no additional source correction once owner 1 is fixed.

Pinned source/current upstream head: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`.

## Owner 1 — shared classification and extraction

File: `crates/swc_ecma_utils/src/lib.rs`.

Current classification asks only about child effects for ordinary binary expressions. Current extraction preserves short-circuit binaries whole and decomposes the rest into child effects.

Candidate:

- classify `instanceof` as effectful;
- preserve the complete `instanceof` expression during effect extraction.

Owned utility regression: `teamleaderleo/swc#2` at `520d841148305d135db78912e6e176a67617b6d3`.

Status: exact-head RED -> GREEN, formatting GREEN, package clippy `-D warnings` GREEN, diff-check GREEN.

### External extractor consumers

Repository search found two external `extract_side_effects_to` consumers at the pinned revision:

1. `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs` — statically selected array member folding. Covered by PR #4.
2. `crates/swc_ecma_minifier/src/compress/pure/member_expr.rs` — literal member simplification. Covered as one path in PR #7.

### DCE consequence

`crates/swc_ecma_transforms_optimization/src/simplify/dce/mod.rs` uses `may_have_side_effects` to decide whether unused variable initializers and assignment RHS values can be dropped.

Owned DCE regression: `teamleaderleo/swc#10` at `5ef8472b24a836ded4035c619393ac0d4ac2384f`.

Consolidated run `31331416981`, job `93290155622`:

- base: callback and invalid-RHS unused initializers erased; strict-equality control passed; 1 passed, 2 failed;
- candidate: 3/3 GREEN;
- formatting, package clippy with `-D warnings`, and diff-check GREEN.

DCE therefore demonstrates a destructive owner-1 consequence without adding a new source owner.

## Owner 2 — expression-simplifier constant folding

File: `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs`.

The current `instanceof` arm folds:

- statically non-object LHS -> `false`;
- known object-like LHS against global `Object` -> `true`.

Those are not sufficient proofs under JavaScript semantics because the RHS can throw or implement `Symbol.hasInstance`, and `Object[Symbol.hasInstance]` can be replaced.

Candidate: remove the unconditional fold until a stronger RHS proof exists.

Owned regressions:

- PR #9 at `8bdbf2119bc93d3e6e20d0c97d61b7c0d43f1530` isolates folding;
- PR #4 at `2afcd4202303c373593aa319b8533fb5bdd3204b` combines folding with extraction consumers.

Status: target-executed RED -> GREEN. PR #4 passed all 5 focused tests plus formatting, package clippy `-D warnings`, and diff-check.

Historical precedent: upstream PR #1630 / commit `b6ff4d6f717dfb4bd41c62c7085e15ace868f296` previously narrowed another unsafe `x instanceof Object` fold.

## Owner 3 — minifier main Optimizer ignored-result fallback

File: `crates/swc_ecma_minifier/src/compress/optimize/mod.rs`.

The method's explicit side-effect-free binary allowlist excludes `in` and `instanceof`, but a later generic binary fallback still keeps only left/right effects for all remaining binaries.

Candidate:

```rust
Expr::Bin(BinExpr {
    op: op!("instanceof"),
    ..
}) => {
    return Some(e.take());
}
```

Owned regression: PR #7 at `942c1871c1c186d7a3c03c84e86b0e10b374348d`.

Clean receipt: run `31330595440`, job `93288105179` — all six direct/extracted callback/invalid-RHS cases retained, strict-equality control removed, focused fixture + fmt + package clippy + diff-check GREEN.

Strong local precedent: the maintainer-triggered January 2026 experiment for issue #11246 changed this same Optimizer seam for `in`, guarded by `pure_getters`.

## Owner 4 — dead-branch remover local `ignore_result`

File: `crates/swc_ecma_transforms_optimization/src/simplify/branch/mod.rs`.

The local `ignore_result` helper independently decomposes every non-short-circuit binary into child effects. It is reused by empty `if` cleanup, loops, sequence pruning, empty switches, selected switch cases, and related result-discarding branch transforms.

Candidate:

```rust
Expr::Bin(bin) if bin.op == op!("instanceof") => Some(bin.into()),
```

before the generic non-short-circuit binary arm.

Owned regression: PR #11 at `05df66c3e98a1124c6e58dd1a814467b0da7f8f5`.

Consolidated run `31331416981`, job `93290155640`:

- base RED confirmed;
- candidate 3/3 focused tests GREEN;
- callback and invalid-RHS `instanceof` retained;
- strict-equality control reduced to normal child effects;
- formatting, package clippy with `-D warnings`, and diff-check GREEN.

Status: `target-executed`.

## Existing tests that encode old behavior

A canonical implementation will intentionally update old expectations.

### Minifier fixture

`crates/swc_ecma_minifier/tests/terser/compress/comparing/dont_change_in_or_instanceof_expressions/`

Its input contains invalid `1 instanceof 1` and `null instanceof null`, but current expected output drops both while preserving invalid `in` operations. That conflicts with the fixture name and invalid-RHS `TypeError` semantics.

### Expression-simplifier tests

`test_fold_instance_of` currently encodes primitive-LHS -> `false` and object-like/global-`Object` -> `true` folds. These expectations must change with owner 2.

## Consolidated candidate fence

Deterministic patcher: `apply-instanceof-candidate.py` at `e8ec2506db64a2bdeca01ad221ce3a38d74a41c5`.

It changes only the four confirmed source owners:

- shared classification/extraction;
- expression-simplifier folding;
- minifier main Optimizer ignored-result fallback;
- dead-branch local ignored-result fallback.

It does not modify arithmetic/coercion assumptions, `pure_getters`, or `in`.

## Focused execution result

Fieldwork run `31331416981` applied that exact candidate across six owned-fork discriminator heads. All six jobs completed successfully. DCE and dead-branch required base RED before candidate application. Every candidate job required focused GREEN, `cargo fmt --all -- --check`, package clippy `--all-targets -- -D warnings`, and `git diff --check`.

## Design direction

The executed candidate uses narrow `instanceof` guards at each owner. A canonical implementation should evaluate whether a context-aware operator-observability predicate near `ExprCtx` can provide the shared semantic answer to classification, extraction, dead-branch result-discarding, and minifier ignored-result handling. Owner 2's value-fold proof remains separate.

A context-aware helper is preferable to encoding policy directly on AST `BinaryOp`, because future `in` behavior may depend on `pure_getters`.

## Next gates

- full `cargo test -p swc_ecma_transforms_optimization` under the candidate;
- minifier execution tests required by target-local instructions;
- broader minifier fixture tests;
- enumerate and intentionally update stale expectations;
- rerun broad gates;
- compare baseline/candidate output on representative `instanceof` inputs;
- keep `in` separate.
