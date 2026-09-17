# SWC mapped `arguments` declaring-owner strictness RED

## In simple words

Current SWC asks strictness at the scope where a parameter assignment is visited, but mapped-`arguments` semantics belong to the function that declared the parameter.

A strict nested function writing a parameter of a sloppy outer function still changes the outer mapped `arguments[0]`. Pinned SWC deletes that write under the `unused` pass and changes runtime output from `2 1` to `1 1`.

This is a second ownership defect in the same `drop_unused_assignments` guard as campaign #766's original nested-scope bug. It is independent of inline remapping.

Evidence class: `target-executed` RED.

No third-party upstream mutation occurred.

## Exact target

- SWC test-only branch: `teamleaderleo/swc#8`
- exact SWC head: `e9306342b4217ac259a5ad6840a7f7c1290e474c`
- pinned source ancestor: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Fieldwork execution carrier: `teamleaderleo/fieldwork#770`
- retained base run/job: `31294069767` / `93196148731`
- runner: Ubuntu 24.04, GitHub-hosted, Azure centralus
- Rust toolchain: nightly `2026-04-10`, rustc `1.96.0-nightly (f5eca4fcf 2026-04-09)`

## Discriminator

```js
function run(f) {
    f();
}

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

console.log(sloppyOuterStrictChild(1), strictOuterSloppyChild(1));
```

Configuration:

```json
{
  "defaults": false,
  "unused": true
}
```

Direct Node runtime:

```text
2 1
```

The first result is `2` because `b` belongs to a sloppy ordinary function with a simple parameter list and remains mapped to that outer function's `arguments[0]`. Strictness inside the nested writer does not sever the outer mapping.

The second result is `1` because the function that declares `b` is strict, so its parameter and `arguments[0]` are not mapped.

## Pinned SWC output

The focused target run printed this transformed program:

```js
function run(f) {
    f();
}
function sloppyOuterStrictChild(b) {
    run(function() {});
    return arguments[0];
}
function strictOuterSloppyChild(b) {
    "use strict";
    run(function() {});
    return arguments[0];
}
console.log(sloppyOuterStrictChild(1), strictOuterSloppyChild(1));
```

Both `b = 2` writes were removed.

The fixture runtime assertion failed with:

```text
<1 1
>2 1

test result: FAILED. 0 passed; 1 failed; 2928 filtered out
```

The workflow subsequently attempted to read `output.js`, which the fixture harness does not materialize after a stdout assertion failure. That post-failure file lookup is a harness issue and does not weaken the already-completed semantic RED above.

## Source explanation

The relevant condition in `drop_unused_assignments` combines three facts:

```rust
(!var.flags.contains(VarUsageInfoFlags::DECLARED_AS_FN_PARAM)
    || !self.data.used_arguments(self.ctx.scope)
    || self.ctx.expr_ctx.in_strict)
```

Both `used_arguments(self.ctx.scope)` and `self.ctx.expr_ctx.in_strict` describe the currently visited writer scope.

For a captured parameter, the semantic owner is the declaring function:

```text
sloppy outer function
  parameter b  <---- mapped ----> outer arguments[0]
      ^
      |
strict nested writer executes b = 2
```

The nested writer's strictness does not change the outer parameter mapping.

## Repair consequence

A durable repair cannot use the current writer's strictness to decide whether an outer function parameter is mapped.

This strengthens the explicit-ownership direction already motivated by the inline-remap RED. The unused pass needs a stable per-binding fact or owner describing the parameter's declaring function, rather than reconstructing mapped-arguments semantics from whichever scope currently visits the assignment.

## Disposition

**TARGET RED / DECLARING-FUNCTION OWNERSHIP REQUIRED.**

The next candidate must pass this fixture together with:

- the original ordinary nested-write matrix;
- the inline-remap `2 2` discriminator;
- strict and non-simple parameter controls.

Automated third-party upstream contact remains prohibited.
