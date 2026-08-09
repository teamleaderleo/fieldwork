# SWC Mapped `arguments` Aliasing Across Nested Writes

## In simple words

Campaign #766 tracks a target-executed SWC minifier defect in sloppy JavaScript parameter/`arguments` semantics.

In a sloppy function with a simple parameter list, the parameter `b` and `arguments[0]` are mapped. A write to `b` is therefore observable through `arguments[0]`. Current pinned SWC default compression deletes such a write when it occurs inside a nested arrow, even though the enclosing function later reads `arguments[0]`.

A strict-mode control using otherwise identical code is allowed to delete the write because strict functions do not map simple parameters to `arguments`. Current SWC produces `1` for that control, which is correct. The defect is the sloppy function also becoming `1` instead of `2`.

- Campaign issue: #766
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Pinned/current SWC: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Execution carrier: `teamleaderleo/fieldwork#765`
- Carrier head: `2581d9c1627ecea8af0cca1ff0d7ec14ef7446f4`
- Workflow run: `31291592350`
- Job: `93189631053`
- Evidence: `model-executed`, `target-executed` RED
- Upstream context: open `swc-project/swc#12032`
- Upstream contact: prohibited for automated workers

## Language invariant

For an ordinary sloppy function with a simple parameter list:

```text
parameter b  <──────── mapped ────────>  arguments[0]
     │
     └── assignment to b must remain observable through arguments[0]
```

For a strict function, or other cases where the arguments object is unmapped, that alias does not exist.

The optimizer therefore cannot decide whether `b = value` is dead from ordinary lexical uses of `b` alone. It also needs the function's arguments-mapping mode and whether the corresponding arguments entry can be observed.

## Model evidence

A dependency-free Node probe established the mode distinction:

```text
sloppy script: b = 2, arguments[0] = 2
module/strict: b = 2, arguments[0] = 1
```

Evidence class: `model-executed`.

This also corrected the interpretation of upstream issue #12032: its published `isModule: true` configuration is strict, so its stated expected value `2` does not by itself isolate a bug. The Fieldwork target probe uses a sloppy function and strict control in the same script to remove that ambiguity.

## Target-native RED

Fixture config:

```json
{
  "defaults": true
}
```

Input:

```js
function run(f) {
    f();
}

function sloppy(b) {
    run(() => {
        b = 2;
    });
    return arguments[0];
}

function strict(b) {
    "use strict";
    run(() => {
        b = 2;
    });
    return arguments[0];
}

console.log(sloppy(1), strict(1));
```

Expected runtime:

```text
2 1
```

SWC output:

```js
function run(f) {
    f();
}
function sloppy(b) {
    return run(()=>{}), arguments[0];
}
function strict(b) {
    return run(()=>{}), arguments[0];
}
console.log(sloppy(1), strict(1));
```

Actual runtime:

```text
1 1
```

The fixture harness failed with:

```text
< 1 1
> 2 1
```

and:

```text
test result: FAILED. 0 passed; 1 failed
```

Evidence class: `target-executed` RED.

## Source map so far

The failure is present under default compression.

`compress/optimize/arguments.rs` is a specialized rewrite behind the separate `arguments` option. It should not be assumed to own this default-compression failure.

The general usage analyzer sees the nested assignment to the outer parameter. It also treats an identifier named `arguments` specially by marking the function scope as using arguments.

What is not yet visible in the mapped source is an explicit relation connecting an indexed `arguments` read to the corresponding simple parameters when the function is sloppy. That missing implicit alias is the leading dataflow hypothesis.

The final deletion appears in ordinary default optimization: the arrow body becomes empty while both function parameters remain present. The exact option/pass that removes the assignment has not yet been isolated.

## Competing repair locations

1. **Usage-analysis aliasing.** When a sloppy simple-parameter function uses `arguments`, mark the relevant parameters or mutations as observable through the mapped arguments object.
2. **Assignment-removal fence.** At the consumer that removes writes to parameters, preserve them when the owning function can expose a mapped arguments object.
3. **Function-level conservative mode.** Disable selected parameter-write reductions in any function that both has mapped arguments semantics and observes `arguments`.

The first direction is semantically central but can have a wider optimization consequence. The second may be smaller but risks missing other consumers of the same implicit alias. The third is easiest to reason about but may unnecessarily reduce compression.

No repair should be chosen until the minimal responsible option/pass is identified.

## Required next probes

### Compressor option bisection

Starting from `defaults: false`, enable likely default passes individually or in small combinations until the runtime flips from `2 1` to `1 1`.

Priority options:

- `unused`;
- `reduce_vars`;
- `collapse_vars`;
- `side_effects`;
- `inline`;
- combinations required by the winning pass.

### Semantic matrix

Add controls for:

1. direct write in the same sloppy function;
2. write inside a nested arrow capturing the outer parameter;
3. write inside an ordinary nested function that has its own parameter/function scope;
4. strict function;
5. default/rest/destructured parameter lists where mapped-arguments rules differ;
6. `arguments` used but a different parameter written;
7. parameter written but `arguments` never observed.

### Owner map

Once the minimal option set is known:

- identify the exact source decision that replaces `b = 2` with nothing;
- inspect which function-scope `used_arguments` and strictness facts are available there;
- determine whether the same alias information is needed by any other optimizer consumer.

## Current disposition

**MAP OWNER.**

The semantic defect is proven on the pinned target. The next accepted transition is a minimal-option target RED plus exact source owner. Only then prepare a bounded repair and GREEN receipt.

No third-party upstream mutation occurred.
