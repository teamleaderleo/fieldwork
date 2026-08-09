# SWC Binary Operator Effects

## In simple words

Campaign #725 has narrowed substantially after reading SWC's target-local minifier instructions and public minification assumptions.

The broad arithmetic/coercion probe found real JavaScript behavior, but SWC explicitly permits the minifier to ignore primitive coercion-helper side effects and arithmetic exceptions such as mixed BigInt/Number operations. Those cases no longer justify a repair. Owned-fork PR #5 has been closed as a negative result.

The strongest repair slice is now `instanceof`. SWC's shared effect classifier checks only the operands, and its shared extractor reduces ordinary binary expressions to operand effects. `instanceof` can still invoke `Symbol.hasInstance` or throw `TypeError` after both operands have been evaluated. Those behaviors are outside the documented assumption set. Owned-fork PR #2 pins the shared utility contract; PR #4 pins a concrete expression-simplifier consumer.

`in` remains a separate policy branch on owned-fork PR #6 because upstream issue 11246 is still open and a prior maintainer-triggered experiment reportedly tied that operator to `pure_getters`.

- Campaign issue: #725
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Public source pin/current upstream main: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- `instanceof` utility contract: `teamleaderleo/swc#2` at `7f02482bdcecafdbf2b7c8d5d3667e2f9db6211b`
- `instanceof` expression-simplifier contract: `teamleaderleo/swc#4` at `1bfc544804d8c5f675a064f6670511973fc30f52`
- `in` policy discriminator: `teamleaderleo/swc#6` at `1ff10db31595acd540ecc769f1fd4b672dab9746`
- retired assumption-bound discriminator: `teamleaderleo/swc#5` at `c75fca0578457d1891833c9d7de30598fb1ed00d`
- Evidence: `source-read`, `model-executed`, `target-test-prepared`
- Upstream contact: prohibited for automated workers

## Assumption correction

`crates/swc_ecma_minifier/AGENTS.md` states that the minifier may rely on the public assumptions, including side-effect-free primitive coercion helpers and side-effect-free arithmetic expressions including runtime exceptions from mixing BigInt and Number.

The public SWC minification guide says `.toString()` and `.valueOf()` are assumed side-effect-free and explicitly says arithmetic expressions may be treated as side-effect-free, including BigInt/Number exceptions.

That evidence invalidated the earlier plan to require preservation of discarded `valueOf` callbacks and `1n + 1` exceptions. PR #5 is retained only as a documented negative result.

## Current source finding

At the pinned revision, `swc_ecma_utils::may_have_side_effects` handles ordinary binary expressions by checking only `left` and `right`.

`ExprCtx::extract_side_effects_to` retains short-circuit binary expressions whole, but recursively extracts only `left` and `right` for other binary expressions.

For `instanceof`, this loses two operator-originated behaviors:

1. `Constructor[Symbol.hasInstance](value)` may execute user code;
2. an invalid right operand throws `TypeError`.

The ordinary minifier `ignore_return_value` reducible allowlist excludes `instanceof`, so the first repair slice belongs in the shared utility layer rather than in minifier statement-discard code.

Other minifier code already treats `in` and `instanceof` specially in negation and boolean-cost logic. That makes a narrow shared-helper special case consistent with existing source conventions.

## Executed `instanceof` model

Node v22.16.0 produced:

```json
{
  "wholeCallback": ["hasInstance"],
  "childrenOnlyCallback": [],
  "wholeInvalid": "TypeError",
  "childrenOnlyInvalid": "no-throw"
}
```

This directly models the shared extractor's current whole-expression-versus-operand-only choice.

Evidence class: `model-executed`.

## Prepared target contracts

### PR #2 — shared utility contract

Requires `may_have_side_effects` to classify callback-capable and invalid-right-operand `instanceof` expressions as effectful and requires `extract_side_effects_to` to retain the complete binary expression. Primitive arithmetic and strict equality remain controls.

### PR #4 — expression-simplifier consumer

Exercises the array-member folding path that extracts effects from discarded siblings. A discarded `value instanceof Constructor` and `1 instanceof 2` must remain in the transformed output; strict equality remains removable.

### PR #6 — `in` policy branch

Keeps Proxy `has` and invalid-right-operand behavior isolated from the `instanceof` repair. Existing upstream discussion around `pure_getters` means this branch needs an explicit policy decision before production implementation.

### PR #5 — negative result

Closed. The fixture required preservation of behavior SWC's documented assumptions allow the minifier to discard.

## Candidate repair

`campaigns/0725-swc-binary-operator-effects/candidate-instanceof.patch` prepares a two-branch change in `swc_ecma_utils/src/lib.rs`:

- classify `instanceof` as operator-effectful;
- retain `instanceof` whole during effect extraction;
- leave every other binary operator unchanged.

No minifier-specific `ignore_return_value` change is proposed for this slice.

## Execution boundary

The local runtime has Node v22.16.0 but no Rust toolchain and no outbound GitHub DNS. The owned SWC fork's inherited pull-request workflow still exposes no runs for the research heads, including after a synchronize event. Target-native RED/GREEN therefore remains unavailable in this session.

No `target-executed` or `full-gate` claim is made.

## Current disposition

**HOLD implementation promotion, PREPARE the minimal `instanceof` repair.**

Next accepted transition requires target-native RED for PRs #2 and #4, application of the candidate patch, GREEN focused tests, formatting/clippy as required by SWC, and exact-head review. `in` stays separate until its `pure_getters` policy is resolved.
