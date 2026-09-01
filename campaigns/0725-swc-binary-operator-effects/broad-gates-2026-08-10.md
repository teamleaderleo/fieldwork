# SWC `instanceof` broad-gate receipt — 2026-08-10

Campaign: #725

Pinned SWC target: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`

Deterministic candidate: `apply-instanceof-candidate.py` at Fieldwork commit `e8ec2506db64a2bdeca01ad221ce3a38d74a41c5`

Broad diagnostic run: `31331894271`

## Result in simple words

The four-owner candidate passes the minifier runtime execution suite. The broader transform/minifier snapshot gates expose exactly three old expectations that encode the behavior being corrected; no unrelated failure surfaced in these broad diagnostics.

The three mismatches are:

1. transform unit `simplify::expr::tests::test_fold_instance_of` expects `64 instanceof Object` and related primitive/object cases to constant-fold;
2. minifier fixture `comparing/dont_change_in_or_instanceof_expressions` expects invalid `instanceof` operations to disappear;
3. minifier fixture `pure_funcs/relational` expects `foo() instanceof bar()` to collapse to `bar()` when `foo` is declared pure, even though the left value remains semantically relevant to the `instanceof` operator and a RHS `Symbol.hasInstance` hook can observe it.

These are expectation updates required by the correctness repair, not candidate regressions.

## Minifier execution gate

Job: `93291358233`

Command: `crates/swc_ecma_minifier/scripts/exec.sh`

Results:

- suite 1: 484 passed, 0 failed, 13 ignored;
- suite 2: 2128 passed, 0 failed, 1 ignored;
- total passed: 2612;
- total failed: 0;
- diagnostic status: `0`.

This is the strongest broad semantic signal in the run because it executes generated JavaScript rather than comparing only compressor snapshots.

## Full optimization-package diagnostic

Job: `93291358274`

Command: `cargo test -p swc_ecma_transforms_optimization --no-fail-fast`

The only failing target was the library unit test `simplify::expr::tests::test_fold_instance_of`.

Observed mismatch:

```text
actual:   64 instanceof Object;
expected: false;
```

The rest of the package targets shown in the job completed successfully. The wrapper intentionally returned success after recording `BROAD_DIAGNOSTIC_STATUS=101` so the log could be retained for triage.

The source test contains a comment claiming non-object values are never instances of anything and encodes thirteen primitive-LHS folds plus object/global-`Object` folds. That premise is incomplete under modern JavaScript because `Symbol.hasInstance` participates in the operator and can be installed as an own property on a constructor such as `Object`.

## Full minifier compress-fixture diagnostic

Job: `93291358266`

Command: `cargo test -p swc_ecma_minifier --no-fail-fast --test compress --features concurrent`

Result:

- 2898 passed;
- 2 failed;
- 27 ignored;
- diagnostic status: `101`.

Only these fixtures failed:

### `comparing/dont_change_in_or_instanceof_expressions`

Input includes:

```js
1 in 1;
null in null;
1 instanceof 1;
null instanceof null;
```

Pinned expected output retains the `in` operations but deletes both `instanceof` operations. The candidate retains all four. The two `instanceof` expressions have observable invalid-RHS `TypeError` behavior and therefore belong in the corrected output.

### `pure_funcs/relational`

Input includes:

```js
foo() instanceof bar();
```

with `foo` listed in `pure_funcs` and `side_effects: true`.

Pinned expected output reduces this line to:

```js
bar();
```

The candidate keeps:

```js
foo() instanceof bar();
```

`pure_funcs` can establish that evaluating `foo()` has no side effects, but its return value is still an input to the `instanceof` operator. The RHS may return an object with a custom `Symbol.hasInstance` implementation that observes that value or performs user-visible work. Removing the left call changes the operator's input and deleting the operator removes the hook/throw step.

All large project/benchmark fixtures visible later in this same compress run completed successfully; the broad output drift was confined to the two explicit relational/`instanceof` expectations above.

## Sibling Terser precedent

Terser PR #1546, merged in 2024, explicitly declined compile-time `instanceof` evaluation because `Symbol.hasInstance` can override the result. This independently supports removing SWC's unconditional value fold.

Current Terser source nevertheless still treats generic binary expressions as operand-only in both `has_side_effects` and `drop_side_effect_free`. That is mixed precedent: Terser's value-fold policy supports the SWC repair, while its current discarded-result logic appears to retain the same operator-observability gap. Do not use that current operand-only behavior as a correctness oracle for SWC.

No Terser or SWC upstream mutation was performed.

## Disposition

Evidence class remains `target-executed`.

Broad-gate conclusion: **candidate behavior is semantically supported; three existing expectations need intentional updates; no unrelated broad semantic failure was found in this diagnostic.**

Next useful work:

1. include intentional expectation updates in a canonical owned-fork candidate;
2. rerun transform package and minifier compress gates as hard GREEN rather than diagnostic wrappers;
3. keep the minifier execution gate as a required hard GREEN;
4. quantify compression/output impact, especially cases where `instanceof` is provably safe to optimize under a stronger RHS proof;
5. compare four local guards with a shared context-aware operator-observability helper;
6. keep `in` and `pure_getters` policy separate.
