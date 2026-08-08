# SWC Binary Operator Effects

## In simple words

Campaign #725 is investigating a shared SWC effect-analysis boundary. Source reading now shows that binary operator behavior can be lost twice: first when `may_have_side_effects` ignores the operator, and again when `extract_side_effects_to` replaces a non-short-circuit binary expression with effects extracted only from its operands.

The owned fork has a utility-level contract test in draft PR `teamleaderleo/swc#2`. JavaScript callback/coercion and exception mechanisms have been executed with Node, while the Rust discriminator still needs target-native execution.

- Campaign issue: #725
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Public source pin: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Owned contract draft: `teamleaderleo/swc#2`
- Owned contract head: `9ad27ab47b7f9a6c77bdcc67fac173efff2f78c8`
- Evidence: `source-read`, `model-executed`, `target-test-prepared`
- Upstream contact: prohibited for automated workers

## Current invariant

```text
operand evaluation
      ↓
binary operator step ── callback / coercion / throw
      ↓
result

If the result is discarded, the operator step still has to happen whenever
JavaScript semantics make that step observable.
```

Both classification and extraction must preserve that invariant.

## Source findings

### Shared classification

`swc_ecma_utils::may_have_side_effects` handles every `Expr::Bin` by checking only `left` and `right`. The operator is absent from the decision.

### Shared extraction

`ExprCtx::extract_side_effects_to` retains short-circuit binary expressions whole, but every other binary expression is recursively reduced to effects from `left` and `right`. This can erase `in` / `instanceof` hooks, object-to-primitive conversion, and operator-thrown exceptions.

### Minifier value-discarding path

`swc_ecma_minifier::compress::pure::misc::ignore_return_value` has its own reducible operator allowlist. It includes arithmetic, exponentiation, bitwise/shift, loose/strict equality, and relational operators. This creates a second consequential consumer to inspect independently of the shared utility helper.

Strict equality is a useful negative control because it compares without object-to-primitive conversion. Primitive arithmetic is another useful control when operand types make the operation incapable of callback or type-mixing failure.

## Executed mechanism evidence

Node v22.16.0 executed user code through Proxy `has`, `Symbol.hasInstance`, and object `valueOf` during binary operator evaluation. It also produced `TypeError` for invalid `in`, invalid `instanceof`, Symbol arithmetic, and BigInt/Number arithmetic.

The model evidence establishes JavaScript behavior. It does not by itself establish which exact SWC optimization path transforms every case.

## Next target test revision

Extend `teamleaderleo/swc#2` so the same fixture packet checks:

1. whole-expression classification;
2. `ExprCtx::extract_side_effects_to` preservation;
3. primitive negative controls;
4. operator-thrown exceptions with pure literal operands where feasible.

Then obtain a base failure and candidate pass on the exact target head before selecting implementation.

## Current disposition

**EXECUTE** the utility contract first. Implementation remains open because a global conservative classifier could reduce compression. The next decision depends on the operator matrix, consumer map, and target-native RED evidence.
