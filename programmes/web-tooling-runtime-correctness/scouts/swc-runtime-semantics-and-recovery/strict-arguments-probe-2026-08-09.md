# SWC function-local strict `arguments` probe — 2026-08-09

## In simple words

Open upstream issue `swc-project/swc#9238` reports that SWC can remove a function-local `"use strict"` directive and thereby change the mapping between a simple parameter and `arguments[0]`.

A current pinned-target probe does **not** reproduce that behavior in the isolated `directives` compressor pass. SWC retained the function-local directive, the generated output preserved the sloppy/strict distinction, and the fixture's runtime oracle passed before and after snapshot generation.

This is a useful negative result, not proof that every historical playground configuration is fixed. It establishes that current `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077` does not exhibit the reported failure under the smallest source-grounded `directives: true` configuration.

No third-party upstream mutation occurred.

## Execution identity

- Work class: execution-only discriminator
- Fieldwork carrier: `teamleaderleo/fieldwork#764`
- Carrier branch: `fieldwork/execution/swc-strict-arguments-probe`
- Carrier head: `a5ec3b004c68eceed10cf5cf272a875131a1928b`
- Workflow: `Fieldwork integrity`
- Workflow run: `31291282856`
- Job: `93188782308` (`swc-strict-arguments-probe`)
- Runner: GitHub-hosted Ubuntu 24.04
- SWC source: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Rust toolchain: `nightly-2026-04-10`

## Probe

The carrier created a temporary SWC-owned-style minifier fixture with:

```json
{
  "defaults": false,
  "directives": true
}
```

Input:

```js
function sloppy(o) {
    o = 1;
    return [o, arguments[0]];
}

function strict(o) {
    "use strict";
    o = 1;
    return [o, arguments[0]];
}

console.log(sloppy(0).join(","));
console.log(strict(0).join(","));
```

Runtime oracle:

```text
1,1
1,0
```

Commands:

```text
UPDATE=1 cargo test -p swc_ecma_minifier --test compress -- strict_arguments_probe --nocapture
cargo test -p swc_ecma_minifier --test compress -- strict_arguments_probe --nocapture
```

Both passed.

## Generated output

The generated `output.js` retained the local directive:

```js
function strict(o) {
    "use strict";
    o = 1;
    return [
        o,
        arguments[0]
    ];
}
```

The carrier's explicit grep found:

```text
9:    "use strict";
```

The fixture harness executed the optimized program and matched the expected stdout.

Evidence class: `target-executed` negative discriminator.

## Source interpretation

Current `compress/optimize/mod.rs` already separates two concepts:

1. the directive statement itself is visited with the pre-directive context;
2. statements after `"use strict"` are optimized with `ExprCtx.in_strict = true`.

`ExprCtx` documents this field as strict for statements **after** the directive. Ordinary function visitors inherit their surrounding expression context rather than unconditionally forcing strict mode.

Terser's current compressor uses a more explicit directive-provenance test: a `"use strict"` directive is removable only when another directive/inherited directive already supplies the same mode. That remains useful review precedent if a broader SWC configuration reproduces the historical issue later.

## Boundary

This probe intentionally isolated only the `directives` pass. It does not establish that the exact historical 2024 playground configuration, a multi-pass default compressor configuration, or another transform pipeline can never erase a necessary function-local directive.

No broader reproduction is justified yet because the minimal present-revision path is correct.

## Disposition

**NEGATIVE / RETIRE THIS PROBE.**

Do not promote #9238 into a new Fieldwork campaign from this evidence. Revisit only if a current configuration produces a runtime mismatch or source analysis identifies a separate pipeline that removes the directive after the isolated directives pass.
