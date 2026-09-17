# SWC `instanceof` execution receipt — 2026-08-09

## In simple words

The first target-native execution pass reproduced the narrowed `instanceof` defect in all three SWC layers that the campaign fenced: the shared utility contract, the expression-simplifier consumer, and the minifier literal-member consumer.

All three base tests reached Rust test assertions and failed for the intended semantic reason. That upgrades those defect claims from `target-test-prepared` to `target-executed` RED evidence.

The same carrier was also supposed to apply the two-branch candidate inside the runner and prove GREEN. That part did not execute: the runner-only Python edit used a brittle exact text match and stopped with `classification patch context did not match exactly once`. This is a harness defect, not evidence against the candidate.

The correct state after this run is therefore:

- `instanceof` defect reproduction: **target-executed RED** in all three lanes;
- candidate repair: **prepared, GREEN pending**;
- carrier patch application: **harness failure after successful RED evidence**;
- full SWC gate: **not run**.

No third-party upstream mutation occurred.

## Execution identity

- Execution carrier: `teamleaderleo/fieldwork#756`
- Carrier branch: `fieldwork/execution/swc-instanceof-red-green`
- Carrier head: `3fc2cd9ed32eadd9509aae970f7f43e889530e86`
- Workflow: `Fieldwork integrity`
- Workflow run: `31290088187`
- Runner: GitHub-hosted `ubuntu-latest`
- Rust toolchain installed by carrier: `nightly-2026-04-10`
- Pinned SWC base: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`

The three source heads below are canonical owned-fork research branches. The execution carrier is supporting evidence only.

## Lane 1 — shared utility contract

Canonical source:

- PR: `teamleaderleo/swc#2`
- Head: `7f02482bdcecafdbf2b7c8d5d3667e2f9db6211b`
- Job: `93185657782`
- Command: `cargo test -p swc_ecma_utils --test operator_effects -- --nocapture`

Observed base result:

```text
test instanceof_operator_is_effectful ... FAILED
test extracting_effects_preserves_instanceof_operator ... FAILED
test primitive_controls_remain_pure ... ok

test result: FAILED. 1 passed; 2 failed
```

The classifier failure was the intended assertion:

```text
assertion failed: parse_expr("value instanceof Constructor").may_have_side_effects(expr_ctx())
```

The extractor failure reported an empty retained-effect set where the contract expected one whole binary expression.

Interpretation:

- current `may_have_side_effects` does not count the `instanceof` operator step as observable when its operands themselves look inert;
- current `extract_side_effects_to` can erase the entire `instanceof` operation when its operands contribute no retained effects;
- the primitive negative control remained green.

Evidence class: `target-executed` RED.

Candidate status: not executed. After the RED receipt, the runner-only source edit failed its exact-text matcher before formatting or GREEN tests ran.

## Lane 2 — expression-simplifier consumer

Canonical source:

- PR: `teamleaderleo/swc#4`
- Head: `1bfc544804d8c5f675a064f6670511973fc30f52`
- Job: `93185657793`
- Command: `cargo test -p swc_ecma_transforms_optimization --test operator_effects -- --nocapture`

Observed base result:

```text
test selected_array_member_preserves_invalid_instanceof ... FAILED
test selected_array_member_preserves_instanceof_callback ... FAILED
test selected_array_member_can_drop_strict_equality_control ... ok

test result: FAILED. 1 passed; 2 failed
```

The concrete output differences were the intended discriminator:

```text
input:    [1 instanceof 2, 42][1];
actual:   42;
expected: 1 instanceof 2, 42;
```

and:

```text
input:    [value instanceof Constructor, 42][1];
actual:   value, Constructor, 42;
expected: value instanceof Constructor, 42;
```

The first case drops an operator-thrown `TypeError`. The second decomposes the operator into operand evaluation and therefore drops `Symbol.hasInstance` behavior. The strict-equality removal control stayed green.

Evidence class: `target-executed` RED.

Candidate status: not executed because the same runner-only text patch failed after the RED receipt.

## Lane 3 — minifier literal-member consumer

Canonical source:

- PR: `teamleaderleo/swc#7`
- Head: `ea9d75c2bf1effd3fb8a191c030380961a1eaa15`
- Job: `93185657800`
- Command: `cargo test -p swc_ecma_minifier --test compress -- instanceof_member_extraction --nocapture`

The SWC fixture harness built successfully and reached the intended fixture assertions. The base fixture failed because the literal-member optimization removed/decomposed the discarded `instanceof` elements rather than retaining the operator step. The callback-capable case therefore lost `Symbol.hasInstance` behavior, and the invalid-right-operand case lost its `TypeError`; the strict-equality case remained the removable control.

Evidence class: `target-executed` RED.

Candidate status: not executed. The runner then stopped at the same brittle source matcher:

```text
classification patch context did not match exactly once
```

## Harness finding

The execution carrier tried to perform a runner-only production edit by replacing a larger exact text block in `swc_ecma_utils/src/lib.rs`. The source does contain the generic binary classification arm and the generic extraction arm identified by the campaign, but the carrier matcher expected a text context that did not match exactly once on these heads.

This failure happened **after** each focused base test had already compiled and produced the intended assertion RED. It therefore does not invalidate the target reproduction.

The next carrier revision should avoid large exact-string replacement. Acceptable bounded options are:

1. apply a checked patch generated directly from the pinned file context;
2. make two narrowly anchored edits around the `Expr::Bin` arms;
3. put the candidate on a separate owned-fork branch and have the execution carrier check out that exact candidate head.

Option 3 gives the cleanest exact-head GREEN receipt because the tested candidate becomes a canonical source revision rather than an ephemeral runner edit.

## Disposition

**RED accepted; GREEN pending.**

The target premise survived execution in the utility layer and both known external extraction consumers. The next transition is to repair the execution method, run the same three focused contracts against an exact owned-fork candidate head, require GREEN plus SWC-required formatting/clippy, then review the candidate diff and any compression consequence.

`in` remains a separate policy question and is not promoted by this receipt.
