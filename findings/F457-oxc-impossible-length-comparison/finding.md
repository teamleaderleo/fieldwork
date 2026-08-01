# F457 — Oxc `unicorn/no-impossible-length-comparison`

## Current disposition

`SOURCE-READY RESEARCH`

The rule is still unimplemented in Oxc at exact target revision `067da8c4e7de2ea11cc55d3e38cbda522067dc89`, and the current pull-request search found no exact competing implementation. The semantic boundary is narrow enough for a syntax-and-constant-evaluation Oxlint rule. No writable owned `teamleaderleo/oxc` repository is installed, so this record stops before creating target-source commits.

Public upstream interaction: `none`.

## Exact revisions and records

- Fieldwork intake: `teamleaderleo/fieldwork#457`
- Intake branch/head used as research base: `p0/457-hot-rust-typescript-intake@a97c50dd14c1539fe5a0c58821fe6db010a0bf86`
- Owned research branch: `research/457-d-oxc-impossible-length-comparison`
- Public Oxc target: `oxc-project/oxc@067da8c4e7de2ea11cc55d3e38cbda522067dc89`
- Oxc tracker: `oxc-project/oxc#684`
- Reference implementation: `sindresorhus/eslint-plugin-unicorn@v72.0.0`
- Reference rule: `rules/no-impossible-length-comparison.js`
- Reference tests: `test/no-impossible-length-comparison.js`
- Reference shared semantics: `rules/utils/length-or-size.js`

## Duplicate result

The Oxc tracker entry for `unicorn/no-impossible-length-comparison` has no implemented, rejected, or pending marker at the inspected revision. Exact-rule pull-request search returned no implementation; adjacent results concerned other length rules or lint infrastructure.

Refresh this search before materializing source because the target is active.

## Rule contract recovered from Unicorn v72

The subject is a non-computed, non-optional member access named `.length` or `.size` on either side of a binary comparison. The other operand must resolve to a finite numeric constant.

Normalize reversed operands by flipping relational operators:

| Original relation | Normalized relation |
| --- | --- |
| `value < subject` | `subject > value` |
| `value <= subject` | `subject >= value` |
| `value > subject` | `subject < value` |
| `value >= subject` | `subject <= value` |
| equality/inequality | unchanged |

For cardinality `n >= 0`, report only these proofs:

| Normalized expression | Reported constant result |
| --- | --- |
| `n < value`, `value <= 0` | `false` |
| `n <= value`, `value < 0` | `false` |
| `n > value`, `value < 0` | `true` |
| `n >= value`, `value <= 0` | `true` |
| `n === value` or `n == value`, `value < 0` | `false` |
| `n !== value` or `n != value`, `value < 0` | `true` |

All other operators or bounds are ignored.

### Required exclusions

The reference implementation intentionally suppresses diagnostics for:

1. optional-chain receivers at any depth, including parenthesized or TypeScript-wrapped receivers;
2. `this.length`, `this.size`, `super.length`, and `super.size`;
3. a statically known member value that is not a non-negative safe integer, because this proves a custom object property rather than collection cardinality;
4. same-object shape guards under a logical-AND root, where another operand reads `.width`, `.height`, or `.depth` from the same receiver;
5. computed properties such as `value["length"]`;
6. non-finite or non-numeric comparison values.

These exclusions are correctness requirements, not optional polish.

## Oxc source map

### Existing rule patterns

- `crates/oxc_linter/src/rules/unicorn/explicit_length_check.rs`
  - already recognizes static `.length` and `.size` members;
  - already rejects optional members, optional chains inside the receiver, and `this`;
  - uses `Expression::get_inner_expression()` for TypeScript wrappers;
  - provides the closest local AST pattern.
- `crates/oxc_linter/src/utils/unicorn.rs`
  - already exposes `is_same_expression` / member-expression identity logic suitable for matching shape guards to the cardinality receiver.
- `crates/oxc_ecmascript/src/constant_evaluation/mod.rs`
  - exposes `ConstantEvaluation::evaluate_value_to_number` and side-effect-aware numeric evaluation;
  - resolves numeric literals, unary/binary expressions, supported globals, and constant references through a context;
  - is already a dependency of `oxc_linter`.
- `crates/oxc_linter/src/rules/unicorn/no_useless_length_check.rs`
  - is a distinct rule about redundant `some`/`every` guards and does not own these diagnostics.

### Proposed target file fence

Direct source work should initially touch only:

- `crates/oxc_linter/src/rules/unicorn/no_impossible_length_comparison.rs`
- generator-owned registration/snapshot files emitted by `just new-unicorn-rule no-impossible-length-comparison`, `cargo lintgen`, tests, and `cargo lint-timings`

Do not edit generated registration files manually.

## Selected implementation approach

1. Generate the new Unicorn rule through the repository command.
2. Visit `AstKind::BinaryExpression` only.
3. Accept the eight comparison operators used by the reference rule.
4. Extract a static `.length`/`.size` member from either operand and normalize reversed operators.
5. Reuse the optional-chain traversal pattern from `explicit_length_check` and reject `this`/`super` receivers.
6. Add a rule-local constant-evaluation context around `LintContext`; evaluate the comparison operand to a finite `f64` without side effects.
7. Evaluate the member expression itself only for the custom-value exclusion. Suppress when its known value is negative, non-integral, non-finite, or outside the safe-integer range.
8. Flatten the enclosing same-operator `&&` root and suppress when a sibling reads `.width`, `.height`, or `.depth` from the same receiver using `utils::unicorn::is_same_expression`.
9. Emit one diagnostic on the complete binary expression, naming the property and whether the expression is always `true` or `false`.
10. Keep all new helpers rule-local until another Oxc rule needs the exact same contract.

## Why this approach

- It preserves upstream parity without requiring type information.
- It reuses Oxc's existing AST ownership and semantic constant machinery.
- It avoids widening shared utilities before the behavior has native tests.
- It keeps runtime work bounded to binary comparisons and early exits.

## Rejected approaches

### Property-name-only check

Reporting every negative comparison against a property named `length` or `size` creates known false positives for custom object models, optional chains, `this`/`super`, and shape objects.

### Literal-only comparison values

This misses reference behavior for constant bindings and expressions such as `const negativeOne = -1` and `-Number.EPSILON`.

### Type-driven collection proof

The reference rule is deliberately syntax/static-value based and works without type information. Requiring TypeScript types would narrow JavaScript coverage and add unnecessary infrastructure.

### Shared helper extraction before tests

Oxc has nearby but not identical logic. Prematurely merging optional-chain, member, and constant helpers would enlarge the change and complicate review.

## Native test requirements

Port the reference cases first, then add Oxc-specific regression coverage. The companion `parity-matrix.md` is the executable checklist.

Minimum focused command after source materialization:

```text
cargo test -p oxc_linter unicorn::no_impossible_length_comparison
```

Repository gates required by `AGENTS.md`:

```text
just fmt
cargo lintgen
cargo lint-timings
just test
just ready
```

The exact focused command may need adjustment to Oxc's generated test filter; preserve the final command and output rather than assuming it.

## Current blockers

1. No writable owned `teamleaderleo/oxc` repository is installed, so no clean target branch can be created through current access.
2. No exact source implementation has been compiled or executed.
3. Constant-evaluation context plumbing must be confirmed against the current Oxc APIs during implementation.
4. Current duplicate search must be refreshed immediately before source materialization.

## Continuation-ready action

Create or identify a writable owned Oxc fork, branch from exact target `067da8c4e7de2ea11cc55d3e38cbda522067dc89`, apply the selected one-rule design, port the complete parity matrix, and preserve exact test receipts and generated-file fence in this finding.

Upstream contact authorization: `false`.
