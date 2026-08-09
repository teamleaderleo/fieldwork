# SWC Binary Operator Effects

## In simple words

Campaign #725 now has a stronger owner map than the original shared-helper theory.

`instanceof` operator evaluation can invoke `Symbol.hasInstance` or throw `TypeError` after both operands have been evaluated. Those behaviors are outside SWC's documented minifier assumptions. Target execution first proved that SWC's shared effect classifier/extractor loses the operator. A deterministic shared-helper candidate then made the direct utility contract GREEN.

That same run also proved the shared helper is only one owner. The expression simplifier has an independent `instanceof` constant-fold branch that still erases invalid-right-operand behavior, and the minifier still removes preserved `instanceof` operations after literal-member extraction. The next repair must therefore cover each independent semantic owner rather than treating extraction as the whole defect.

- Campaign issue: #725
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Pinned/current SWC: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- utility contract: `teamleaderleo/swc#2`, current head `520d841148305d135db78912e6e176a67617b6d3`
- expression-simplifier contract: `teamleaderleo/swc#4` at `1bfc544804d8c5f675a064f6670511973fc30f52`
- minifier-member contract: `teamleaderleo/swc#7` at `ea9d75c2bf1effd3fb8a191c030380961a1eaa15`
- separate `in` policy discriminator: `teamleaderleo/swc#6`
- retired assumption-bound discriminator: `teamleaderleo/swc#5`
- initial RED carrier: `teamleaderleo/fieldwork#756`, retired
- shared-candidate carrier: `teamleaderleo/fieldwork#771`
- deterministic shared patcher: `apply-instanceof-candidate.py`
- Evidence: `source-read`, `model-executed`, target RED, direct-utility candidate GREEN, downstream candidate RED
- Upstream contact: prohibited for automated workers

## Assumption boundary

The earlier arithmetic/coercion branch remains retired. SWC explicitly permits primitive coercion helpers and arithmetic runtime exceptions to be treated as side-effect-free during minification.

`instanceof` is different. Its post-operand operator step can:

1. call `Constructor[Symbol.hasInstance](value)`;
2. throw when the RHS is not a valid `instanceof` target.

Node modeling already distinguished whole execution from operand-only execution for both cases.

## Owner 1 — shared effect classification and extraction

At the pinned source revision, `swc_ecma_utils::may_have_side_effects` handles ordinary binaries by asking only about `left` and `right`. `ExprCtx::extract_side_effects_to` retains short-circuit binaries whole but otherwise extracts only child effects.

Initial carrier #756 produced direct target REDs for both behaviors.

Carrier #771 then applied the deterministic two-branch shared candidate:

- classify `instanceof` as operator-effectful;
- retain the whole `instanceof` expression during effect extraction.

The utility contract itself passed all three semantic tests:

```text
instanceof_operator_is_effectful ... ok
extracting_effects_preserves_instanceof_operator ... ok
primitive_controls_remain_pure ... ok
```

The utility job later failed only because the owned research helper returning the library-required `Vec<Box<Expr>>` triggered `clippy::vec-box` under `-D warnings`. PR #2 now carries a narrow test-only `#[allow(clippy::vec_box)]`; production candidate semantics were GREEN.

Evidence: direct utility `target-executed` candidate GREEN.

## Owner 2 — expression simplifier constant folding

The expression-simplifier candidate lane showed a second independent defect.

With the shared helper candidate applied:

- the callback-capable `value instanceof Constructor` array-sibling case passed;
- the literal invalid-RHS case still failed: `[1 instanceof 2, 42][1]` became `42;` instead of retaining the throwing operation.

Source reading identifies the owner in `crates/swc_ecma_transforms_optimization/src/simplify/expr/mod.rs::optimize_bin_expr`.

Its `instanceof` arm currently treats a primitive left operand as sufficient proof of `false`:

```rust
if is_non_obj(left) {
    *changed = true;
    *expr = *make_bool_expr(expr_ctx, *span, false, iter::once(right.take()));
    return;
}
```

That is not a valid `instanceof` proof by itself. The RHS operator step still runs first: an invalid RHS throws, and a custom `Symbol.hasInstance` can execute user code even when the LHS is primitive.

The same arm also folds `objectLike instanceof Object` to `true`; that branch needs its own semantic proof before it is retained because `instanceof` consults RHS behavior.

Evidence: target candidate RED plus source owner identified.

Leading bounded direction: remove or conservatively gate these `instanceof` folds unless SWC can prove the RHS uses ordinary built-in `instanceof` semantics.

## Owner 3 — minifier discarded-result lifecycle

The minifier literal-member lane also remained RED after the shared helper candidate.

Input contracts:

```js
[value instanceof Constructor][1];
[value instanceof 2][1];
```

Expected extraction preserves each `instanceof` expression. Actual candidate output reduced both containing functions to empty bodies.

This is independent of the known arithmetic/equality binary decomposition list. `ignore_return_value` decomposes arithmetic, bitwise/shift, equality, and relational binaries; `instanceof` is absent from that allowlist.

The minifier does, however, run a broader multi-pass compressor/pure-optimizer lifecycle around the literal-member rewrite. The exact third deletion phase is still being isolated.

Next discriminator: compare a direct discarded expression statement

```js
value instanceof Constructor;
```

against the same operation produced by out-of-bounds literal-member extraction. If the direct statement survives under `side_effects` while the extracted one disappears, the owner is in the member-rewrite lifecycle. If both disappear, trace the generic expression-statement/pure phase.

Evidence: target candidate RED; exact phase still under investigation.

## Classification blast radius

Making `instanceof` always effectful in `may_have_side_effects` is correctness-conservative but affects many destructive consumers beyond the two extractor call sites, including DCE and minifier decisions that consult whole-expression effects.

That means a final repair needs both semantic GREEN and a small optimization/output comparison. The campaign should not promote a broad shared classification change solely because the three focused regressions pass.

## `in` remains separate

Owned-fork PR #6 keeps the `in` operator on its own policy lane because existing upstream discussion ties `in` behavior to `pure_getters`. It should not broaden this `instanceof` repair.

## Current disposition

**SHARED OWNER GREEN; DOWNSTREAM OWNERS STILL RED; BROADEN REPAIR MAP.**

Next transitions:

1. isolate the exact minifier phase that removes preserved `instanceof`;
2. prepare a broadened candidate covering the shared helper plus the expression-simplifier fold and the confirmed minifier owner;
3. rerun the utility, transform, and minifier contracts on exact owned-fork heads;
4. require formatting/package clippy and exact-head diff review;
5. measure the optimization consequence of always-effectful `instanceof` classification;
6. keep `in` separate.

No third-party upstream mutation occurred.
