# SWC Mapped `arguments` Aliasing Across Nested Writes

## In simple words

Campaign #766 now has two target-reproduced ownership defects, a rejected one-line repair, and a stronger explicit per-binding candidate that is GREEN across the hard semantic cases plus SWC formatting/package clippy.

Pinned SWC's `unused` pass can delete writes to a parameter based on the scope currently visiting the assignment. That is wrong when the parameter belongs to another function. It fails for an ordinary nested writer, fails when a strict nested function writes a sloppy outer mapped parameter, and the obvious `i.id.ctxt` repair fails after SWC gives an inline clone a fresh binding context.

The successful candidate records on `VarUsageInfo` that a parameter belongs to an ordinary function whose lexical `arguments` binding is used. `VarUsageInfo` already follows remapped inline clones, so the ownership fact survives code motion instead of being reconstructed from the current writer scope or current binding context.

The candidate is conservative: strict or non-simple declaring functions that use `arguments` may retain a dead parameter assignment. That is a compression-precision question remaining before promotion.

- Campaign issue: #766
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Pinned/current SWC: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Initial RED carrier: `teamleaderleo/fieldwork#765`, retired
- Option bisection carrier: `teamleaderleo/fieldwork#767`, retired
- Ordinary-path one-line carrier: `teamleaderleo/fieldwork#768`, retired
- Inline-remap carrier: `teamleaderleo/fieldwork#769`, retired
- Explicit-ownership carrier: `teamleaderleo/fieldwork#770`
- SWC discriminator: `teamleaderleo/swc#8` at `e9306342b4217ac259a5ad6840a7f7c1290e474c`
- Inline-remap run/job: `31293367121` / `93194367502`
- Owner-strictness RED run/job: `31294069767` / `93196148731`
- Explicit-owner semantic run/job: `31294224774` / `93196547013`
- Explicit-owner package run/job: `31294497411` / `93197236450`
- Active upstream implementation: `swc-project/swc#12037`
- Ordinary-path receipt: `candidate-local-green-2026-08-09.md`
- Inline-remap receipt: `inline-remap-2026-08-09.md`
- Owner-strictness receipt: `owner-strictness-red-2026-08-09.md`
- Explicit-owner receipt: `explicit-ownership-candidate-2026-08-09.md`
- Deterministic candidate patcher: `apply-explicit-ownership.py`
- Upstream review note: `upstream-pr-12037-review.md`
- Upstream contact: prohibited for automated workers

## Language invariant

For a sloppy ordinary function with a simple parameter list:

```text
parameter b  <──────── mapped ────────>  arguments[0]
```

A write to `b` remains observable through that declaring function's `arguments[0]`, even when the write executes inside a nested function. The nested writer's own strictness does not alter the outer mapping.

Strict declaring functions and non-simple parameter lists do not have the same mapping.

## Original target RED and option bisection

Carrier #765 reproduced expected `2 1` versus optimized `1 1` for a sloppy/strict pair. Evidence: `target-executed` RED.

Carrier #767 started from `defaults: false` and showed `unused` alone is sufficient among the tested compressor options:

| configuration | runtime | result |
| --- | --- | --- |
| `unused` | `1 1` | RED |
| `reduce_vars` | `2 1` | correct |
| `collapse_vars` | `2 1` | correct |
| `side_effects` | `2 1` | correct |
| `inline` | `2 1` | correct |
| `unused + reduce_vars` | `1 1` | RED |
| `unused + collapse_vars` | `1 1` | RED |
| `reduce_vars + collapse_vars` | `2 1` | correct |

## Exact source owner

`drop_unused_assignments` guards removal with:

```rust
(!var.flags.contains(VarUsageInfoFlags::DECLARED_AS_FN_PARAM)
    || !self.data.used_arguments(self.ctx.scope)
    || self.ctx.expr_ctx.in_strict)
```

For a captured parameter, both `self.ctx.scope` and `self.ctx.expr_ctx.in_strict` can describe the nested writer rather than the function that declared the parameter.

## One-line candidate — ordinary GREEN, remap RED

Fieldwork and active upstream PR #12037 independently arrived at:

```diff
- || !self.data.used_arguments(self.ctx.scope)
+ || !self.data.used_arguments(i.id.ctxt)
```

Carrier #768 passed a seven-case ordinary-path matrix with oracle:

```text
2 2 2 1 7 5 1
```

But carrier #769 forced real SWC multi-use cloning. Base SWC cloned the function twice, retained both `b = 2` assignments, and ran `2 2`. Applying only the one-line candidate removed both assignments and ran `1 1`; the target fixture failed its `2 2` oracle.

Evidence: `target-executed` base GREEN plus candidate RED.

Reason: the inliner gives cloned bindings a fresh `SyntaxContext` and copies `VarUsageInfo` to the remapped `Id`, while `ScopeData::USED_ARGUMENTS` remains owned by the lexical function scope. The fresh binding context is not a function-scope key.

Disposition for the one-line repair: **REJECT**.

## Second target RED — declaring-function strictness

PR #8 adds:

```js
function sloppyOuterStrictChild(b) {
    run(function () {
        "use strict";
        b = 2;
    });
    return arguments[0];
}

function strictOuterSloppyChild(b) {
    "use strict";
    run(function () {
        b = 2;
    });
    return arguments[0];
}
```

Direct JavaScript result:

```text
2 1
```

Pinned SWC removed both nested assignments and produced `1 1`. The focused fixture failed with an actual semantic assertion.

Evidence: `target-executed` RED. Exact receipt: `owner-strictness-red-2026-08-09.md`.

This proves writer-scope strictness is also the wrong owner for the mapped-arguments decision.

## Explicit per-binding ownership candidate

The candidate introduces a `VarUsageInfo` flag:

```rust
FN_PARAM_OF_ARGUMENTS_FN
```

After an ordinary function's parameters and body are analyzed, parameters are marked when that function's lexical scope uses `arguments`. The unused pass then decides against dropping a parameter write based on this stable per-binding fact rather than current writer scope/context.

This is a natural fit for SWC's data model because the inliner already clones full `VarUsageInfo` records onto fresh remapped IDs, and `ProgramData` is re-analyzed from the current AST at the start of compressor passes.

Deterministic implementation artifact: `apply-explicit-ownership.py`. Every source replacement must match exactly once and fails closed on target drift.

## Explicit candidate semantic GREEN

Carrier #770 semantic run `31294224774`, job `93196547013`, applied the candidate to exact SWC test head `e9306342b4217ac259a5ad6840a7f7c1290e474c`.

All three suites passed:

1. seven-case ordinary-path matrix — `2 2 2 1 7 5 1`;
2. declaring-owner strictness — `2 1`;
3. real inline-remap cloning — `2 2`.

The inline output retained both `b = 2` assignments after cloning.

Evidence: focused `target-executed` GREEN.

## Formatting and package clippy GREEN

The first semantic runner had a mechanical rustfmt mismatch in the runner-generated source after all semantic tests had passed.

Fieldwork replaced that ephemeral edit path with deterministic patcher `apply-explicit-ownership.py`. Package run `31294497411`, job `93197236450`, successfully:

1. checked out exact SWC head `e9306342b4217ac259a5ad6840a7f7c1290e474c`;
2. applied the deterministic candidate;
3. passed `git diff --check`;
4. passed `cargo fmt --all -- --check`;
5. passed `cargo clippy -p swc_ecma_minifier --all-targets -- -D warnings`.

Evidence: exact-candidate package validation.

## Precision boundary

The candidate currently records:

> parameter of an ordinary function whose lexical scope uses `arguments`

It does not yet encode whether that declaring function actually has mapped parameters under ECMAScript rules. Strict functions and non-simple parameter lists can therefore keep an assignment that could be removed safely.

This is correctness-conservative. It is visible in optimized output for controls and should be measured before promotion.

The usage analyzer currently has no strict-mode field, so exact strictness precision would widen analyzer state. SWC's dedicated `arguments` optimizer offers useful precedent for parameter precision by operating only on plain identifier parameters and rejecting duplicate/shadowing cases.

## Active upstream ownership

Upstream PR #12037 remains open on the one-line `i.id.ctxt` implementation. Fieldwork now has target evidence that this current approach regresses real inline-remapped code plus a locally GREEN alternative ownership model.

Fieldwork should continue review/verification and avoid automated upstream interaction.

## Current disposition

**EXPLICIT-OWNERSHIP CANDIDATE GREEN / REVIEW HOLD FOR PRECISION AND ACTIVE-UPSTREAM COORDINATION.**

Next research transitions:

1. measure the compression consequence of conservative retention in strict/non-simple controls;
2. decide whether declaring-function strict/simple-parameter precision belongs in the same repair or a bounded follow-up;
3. review any new upstream #12037 revision against the inline-remap and owner-strictness discriminators;
4. retire carrier #770 after this receipt is synchronized.

No third-party upstream mutation occurred.
