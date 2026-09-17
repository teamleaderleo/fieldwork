# SWC mapped `arguments` explicit-ownership candidate receipt

## In simple words

A per-binding ownership candidate fixes the mapped-`arguments` bug family across ordinary nested writes, declaring-function strictness, and real inline remapping.

The candidate adds a `VarUsageInfo` flag for parameters of ordinary functions whose lexical `arguments` binding is used. That fact is established by the usage analyzer after the declaring function body is analyzed, follows cloned/remapped bindings through the existing `VarUsageInfo::clone` path, and replaces writer-scope queries in `drop_unused_assignments`.

Three semantic suites are GREEN on the exact test head, including the two cases that disproved the one-line `i.id.ctxt` repair. The deterministic source-pinned patcher also passes SWC formatting and package clippy.

The candidate is intentionally conservative: it can retain a dead parameter assignment in strict or non-simple-parameter functions that use `arguments`. That is a compression-precision cost to measure/refine before promotion, not a semantic failure.

Evidence class: `target-executed` focused GREEN plus package formatting/clippy. No third-party upstream mutation occurred.

## Exact identities

- pinned upstream ancestor: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- owned SWC discriminator: `teamleaderleo/swc#8`
- exact SWC test head: `e9306342b4217ac259a5ad6840a7f7c1290e474c`
- execution carrier: `teamleaderleo/fieldwork#770`
- semantic candidate run/job: `31294224774` / `93196547013`
- package candidate run/job: `31294497411` / `93197236450`
- Rust toolchain: nightly `2026-04-10`, rustc `1.96.0-nightly (f5eca4fcf 2026-04-09)`
- deterministic patcher: `apply-explicit-ownership.py`
- human-readable candidate sketch: `candidate-explicit-ownership.patch`

## Candidate model

The current guard asks mapped-arguments questions using the scope where an assignment is visited:

```rust
(!var.flags.contains(VarUsageInfoFlags::DECLARED_AS_FN_PARAM)
    || !self.data.used_arguments(self.ctx.scope)
    || self.ctx.expr_ctx.in_strict)
```

That fails in two independent ways:

1. a nested writer has a different scope from the function that declared the captured parameter;
2. an inline clone can give the parameter a fresh binding `SyntaxContext` with no function `ScopeData`.

The candidate carries the declaring-function relationship on per-binding metadata instead.

Conceptually:

```rust
const FN_PARAM_OF_ARGUMENTS_FN = 1 << 26;
```

After an ordinary function's parameters and body are analyzed:

```rust
if child.scope.used_arguments() {
    for param in &n.params {
        for id in find_pat_ids::<_, Id>(&param.pat) {
            child
                .data
                .var_or_default(id)
                .mark_fn_param_of_arguments_fn();
        }
    }
}
```

Then the unused-assignment guard becomes:

```rust
(!var.flags.contains(VarUsageInfoFlags::DECLARED_AS_FN_PARAM)
    || !var
        .flags
        .contains(VarUsageInfoFlags::FN_PARAM_OF_ARGUMENTS_FN))
```

The flag is merged with other `VarUsageInfoFlags`, and the inliner already clones the complete `VarUsageInfo` when it remaps a binding.

## Semantic GREEN — run 31294224774

The runner applied the candidate to exact SWC head `e9306342b4217ac259a5ad6840a7f7c1290e474c` and ran three focused suites.

### Existing seven-case matrix

Oracle:

```text
2 2 2 1 7 5 1
```

Coverage includes:

- direct sloppy parameter write;
- nested arrow write;
- nested ordinary-function write;
- strict declaring function control;
- no-`arguments` observation;
- unrelated local assignment;
- default-parameter control.

Result: GREEN.

### Declaring-owner strictness

This is the target RED discovered during this continuation:

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

Oracle:

```text
2 1
```

Pinned base produced `1 1`. The explicit-ownership candidate produced `2 1` and the focused fixture passed.

Result: GREEN.

### Real inline remapping

The discriminator forces SWC to clone the same mapped-arguments function twice:

```js
function mapped(b, c, d, e, f, g, h, i, j, k, l, m) {
    return (b = 2, arguments[0]);
}

console.log(mapped(1), mapped(1));
```

Oracle:

```text
2 2
```

The rejected one-line `i.id.ctxt` repair produced `1 1` after real cloning. The explicit-ownership candidate retained both `b = 2` assignments in the cloned bodies and produced `2 2`.

Result: GREEN.

## Package gate — run 31294497411

The first semantic carrier inserted one flag-propagation line with runner formatting that `rustfmt` wanted collapsed. Semantic tests had already passed; package clippy was skipped after the formatting failure.

Fieldwork then created `apply-explicit-ownership.py`, a deterministic patcher pinned to the exact SWC source text. Every replacement requires exactly one source match and fails closed on drift.

The package run checked out the exact SWC discriminator head, applied that durable patcher successfully, then ran:

```text
cargo fmt --all -- --check
cargo clippy -p swc_ecma_minifier --all-targets -- -D warnings
git diff --check
```

All passed.

Evidence class: package formatting/clippy at the exact candidate source produced by the durable patcher.

## Precision boundary

The candidate flag currently means:

> parameter of an ordinary function whose lexical function scope uses `arguments`

It does not yet encode whether that declaring function actually has a mapped parameter object under ECMAScript semantics.

Consequently, examples such as a strict declaring function or a non-simple parameter list can retain an assignment that could safely be removed. The semantic matrix demonstrates this conservative behavior: strict/default-parameter controls remain correct, but some assignment text stays in optimized output.

The usage analyzer currently has no strict-mode field in its analysis context, so making this flag exact would require more state than the correctness repair itself. SWC's dedicated `arguments` optimizer provides useful precision precedent by limiting transformations to plain identifier parameters and rejecting duplicate/shadowing cases.

## Disposition

**CANDIDATE GREEN / REVIEW HOLD FOR PRECISION AND ACTIVE-UPSTREAM COORDINATION.**

The one-line `i.id.ctxt` repair is rejected. The explicit per-binding ownership candidate is the first implementation direction in this campaign that passes:

- the original nested-write semantics;
- the declaring-owner strictness case;
- real inline remapping;
- formatting and package clippy.

Before any promotion language, compare the compression consequence of the conservative flag and decide whether strict/non-simple declaring-function precision belongs in the same repair or a bounded follow-up. Active upstream PR `swc-project/swc#12037` remains the implementation owner; Fieldwork should continue to review/verify rather than automate upstream contact.
