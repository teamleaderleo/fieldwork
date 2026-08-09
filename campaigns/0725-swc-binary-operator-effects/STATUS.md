# SWC Binary Operator Effects

## In simple words

Campaign #725 has now reproduced the narrowed `instanceof` defect with SWC's real Rust tests at three layers: the shared utility contract, the expression-simplifier consumer, and the minifier literal-member consumer.

The broad arithmetic/coercion theory remains retired. SWC explicitly permits its minifier to ignore primitive coercion-helper side effects and arithmetic exceptions such as mixed BigInt/Number operations, so owned-fork PR #5 is a negative result rather than a correctness repair.

`instanceof` sits outside those documented assumptions. Its operator step can invoke `Symbol.hasInstance` or throw `TypeError` after both operands are evaluated. SWC's shared effect classifier currently asks only whether the operands are effectful, while the shared extractor can reduce an ordinary binary expression to operand effects. Target execution now confirms that those helpers erase real `instanceof` behavior in both known extraction consumers.

The first RED/GREEN carrier produced three valid RED receipts and then hit a carrier-only text-patching failure before the candidate could run. The defect is therefore `target-executed`; candidate GREEN remains pending.

- Campaign issue: #725
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Public source pin/current upstream main: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- `instanceof` utility contract: `teamleaderleo/swc#2` at `7f02482bdcecafdbf2b7c8d5d3667e2f9db6211b`
- `instanceof` expression-simplifier contract: `teamleaderleo/swc#4` at `1bfc544804d8c5f675a064f6670511973fc30f52`
- `instanceof` minifier-member contract: `teamleaderleo/swc#7` at `ea9d75c2bf1effd3fb8a191c030380961a1eaa15`
- `in` policy discriminator: `teamleaderleo/swc#6` at `1ff10db31595acd540ecc769f1fd4b672dab9746`
- retired assumption-bound discriminator: `teamleaderleo/swc#5`
- execution carrier: `teamleaderleo/fieldwork#756` at `3fc2cd9ed32eadd9509aae970f7f43e889530e86`
- execution receipt: `execution-2026-08-09.md`
- Evidence: `source-read`, `model-executed`, `target-test-prepared`, `target-executed` RED
- Upstream contact: prohibited for automated workers

## Assumption correction

`crates/swc_ecma_minifier/AGENTS.md` and the public SWC minification guide explicitly allow primitive coercion helpers such as `.valueOf()` to be treated as side-effect-free and arithmetic runtime exceptions such as mixed BigInt/Number operations to be ignored during minification.

That evidence invalidated the earlier plan to require preservation of discarded object coercion and arithmetic exceptions. PR #5 is retained only as a negative result.

## Current source boundary

At the pinned revision:

- `swc_ecma_utils::may_have_side_effects` handles ordinary binary expressions by checking only `left` and `right`;
- `ExprCtx::extract_side_effects_to` retains short-circuit binaries whole but recursively extracts only `left` and `right` for other binary expressions;
- the ordinary minifier `ignore_return_value` allowlist excludes `instanceof`, so no separate ordinary-expression discard repair is required for this slice;
- repository search found two external `extract_side_effects_to` consumers: the expression simplifier and the minifier literal-member optimizer;
- other minifier code already treats `in` and `instanceof` specially in negation and boolean-cost logic.

The two known external extraction consumers are fenced by PRs #4 and #7.

## Executed JavaScript model

Node v22.16.0 distinguished whole `instanceof` execution from evaluating the operands alone:

```json
{
  "wholeCallback": ["hasInstance"],
  "childrenOnlyCallback": [],
  "wholeInvalid": "TypeError",
  "childrenOnlyInvalid": "no-throw"
}
```

Evidence class: `model-executed`.

## Target-native RED receipts

Execution carrier #756, workflow run `31290088187`, used SWC's nightly `2026-04-10` toolchain and the exact owned-fork research heads.

### Shared utility — PR #2

Command:

```text
cargo test -p swc_ecma_utils --test operator_effects -- --nocapture
```

Result:

```text
test result: FAILED. 1 passed; 2 failed
```

`instanceof_operator_is_effectful` failed because `may_have_side_effects` returned false. `extracting_effects_preserves_instanceof_operator` failed because extraction retained no whole operator expression. The primitive control passed.

Evidence class: `target-executed` RED.

### Expression simplifier — PR #4

Command:

```text
cargo test -p swc_ecma_transforms_optimization --test operator_effects -- --nocapture
```

Result:

```text
test result: FAILED. 1 passed; 2 failed
```

The selected-array transform reduced `[1 instanceof 2, 42][1]` to `42;`, losing the `TypeError`, and reduced `[value instanceof Constructor, 42][1]` to `value, Constructor, 42;`, losing `Symbol.hasInstance`. The strict-equality control passed.

Evidence class: `target-executed` RED.

### Minifier literal-member consumer — PR #7

Command:

```text
cargo test -p swc_ecma_minifier --test compress -- instanceof_member_extraction --nocapture
```

The SWC fixture harness built and reached the intended assertions. The base fixture failed because literal-member extraction erased/decomposed the discarded `instanceof` operation, losing both callback-capable and invalid-RHS behavior while retaining the strict-equality removal control.

Evidence class: `target-executed` RED.

The exact execution record is preserved in `execution-2026-08-09.md`.

## Harness finding after RED

The carrier attempted to apply the candidate only inside the runner using a large exact-string replacement. On all three jobs it stopped after the RED receipt with:

```text
classification patch context did not match exactly once
```

This is a carrier-script defect. The target tests had already compiled and failed at their intended semantic assertions, so the RED evidence remains valid. Formatting, candidate GREEN tests, and clippy did not run after that failure.

## Candidate repair

`candidate-instanceof.patch` expresses the intended two-branch change in `swc_ecma_utils/src/lib.rs`:

- classify `instanceof` as operator-effectful;
- retain `instanceof` whole during effect extraction;
- leave every other binary operator unchanged.

The next execution should put that candidate on an exact owned-fork source head rather than relying on an ephemeral large-string edit in the runner. That will make the GREEN receipt independently reviewable.

## `in` remains separate

Owned-fork PR #6 retains the `in` operator question. Upstream issue #11246 and prior maintainer discussion connect `in` preservation to `pure_getters`, so that policy should not block or contaminate the cleaner `instanceof` repair.

## Current disposition

**RED ACCEPTED; GREEN PENDING.**

The `instanceof` defect is now reproduced target-natively in the shared utility layer and both known external extraction consumers. The next accepted transition is:

1. prepare an exact owned-fork candidate head containing only the two shared-helper changes;
2. run PRs #2, #4, and #7 against that candidate and require GREEN;
3. run SWC-required formatting and package clippy on the candidate;
4. inspect the exact candidate diff and measure any optimization/compression consequence;
5. keep `in` on its separate policy lane.

No third-party upstream mutation occurred.
