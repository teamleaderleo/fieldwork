# SWC Mapped `arguments` Aliasing Across Nested Writes

## In simple words

Campaign #766 now has a target-executed defect, a minimal responsible compressor option, and an exact source deletion condition.

In sloppy JavaScript with a simple parameter list, a parameter and its matching `arguments` entry are mapped. Current pinned SWC's `unused` pass deletes a write to an enclosing function parameter when that write occurs inside a child arrow, even though the enclosing function later reads `arguments[0]`.

Option bisection shows `unused` alone is sufficient. `reduce_vars`, `collapse_vars`, `side_effects`, `inline`, and `reduce_vars + collapse_vars` all preserve the correct runtime. Adding `unused` reproduces the failure.

Source reading then found the exact safeguard in `compress/optimize/unused.rs`. `drop_unused_assignments` already knows parameter assignments must be preserved when the relevant function uses `arguments` and is sloppy. The nested-closure failure occurs because that guard queries `self.data.used_arguments(self.ctx.scope)`: while optimizing the assignment inside the arrow, `self.ctx.scope` is the arrow scope, not the enclosing function scope that owns both the parameter and `arguments` object.

The leading bounded repair is therefore to anchor the existing safeguard to the assigned parameter binding's owning context rather than the currently visited child scope. A candidate must still be executed against a semantic matrix before promotion.

- Campaign issue: #766
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Pinned/current SWC: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Initial execution carrier: `teamleaderleo/fieldwork#765`, retired
- Option-bisection carrier: `teamleaderleo/fieldwork#767` at `69ecf2ef708e0f7050cdaad44524154c9d7fb35a`
- Bisection workflow run: `31291818612`
- Bisection job: `93190209600`
- Evidence: `model-executed`, `target-executed` RED, `source-read`
- Upstream context: open `swc-project/swc#12032`
- Upstream contact: prohibited for automated workers

## Language invariant

For an ordinary sloppy function with a simple parameter list:

```text
parameter b  <──────── mapped ────────>  arguments[0]
     │
     └── assignment to b must remain observable through arguments[0]
```

For strict functions, and other cases where the arguments object is unmapped, that alias does not exist.

The optimizer therefore cannot decide whether `b = value` is dead from lexical references to `b` alone.

## Initial target RED

Under:

```json
{
  "defaults": true
}
```

this source:

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

has runtime oracle:

```text
2 1
```

Current SWC emitted:

```js
function sloppy(b) {
    return run(()=>{}), arguments[0];
}
function strict(b) {
    return run(()=>{}), arguments[0];
}
```

and produced:

```text
1 1
```

Evidence class: `target-executed` RED.

The strict result is correct; the sloppy result is wrong.

## Compressor-option bisection

Carrier #767 started from `defaults: false` and tested the same runtime oracle under individual passes and small combinations.

Observed results:

| configuration | runtime | disposition |
| --- | --- | --- |
| `unused` | `1 1` | RED |
| `reduce_vars` | `2 1` | correct |
| `collapse_vars` | `2 1` | correct |
| `side_effects` | `2 1` | correct |
| `inline` | `2 1` | correct |
| `unused + reduce_vars` | `1 1` | RED |
| `unused + collapse_vars` | `1 1` | RED |
| `reduce_vars + collapse_vars` | `2 1` | correct |

The carrier's matrix recorder labelled failing `unused` fixtures `HARNESS_NO_OUTPUT` because the SWC fixture harness aborts at the expected stdout assertion before snapshot persistence. The logs nevertheless contain the generated optimized output and exact `1 1` vs `2 1` assertion failure. This is a recorder/harness-label defect, not ambiguity in the option result.

Conclusion: **`unused` alone is sufficient and necessary among the tested options.**

Evidence class: `target-executed` option discriminator.

## Exact source owner

`crates/swc_ecma_minifier/src/compress/optimize/unused.rs::drop_unused_assignments` contains the deletion condition for simple identifier assignments.

The relevant logic requires:

```text
variable usage_count == 0
AND variable is declared
AND one of:
    variable is not a function parameter
    OR current scope does not use arguments
    OR current expression context is strict
```

In source form, the parameter safeguard is:

```rust
(!var.flags.contains(VarUsageInfoFlags::DECLARED_AS_FN_PARAM)
    || !self.data.used_arguments(self.ctx.scope)
    || self.ctx.expr_ctx.in_strict)
```

That guard is semantically appropriate when the assignment is visited in the parameter's owning function. It fails for nested closures because optimizer context changes at every function-like node. Arrow/function visitors set `scope` and `var_scope` to the child function's `ctxt`.

For the failing source:

```text
sloppy function scope: uses arguments
    parameter b: declared here
    nested arrow scope: does not use arguments
        assignment b = 2: visited here
```

So `used_arguments(self.ctx.scope)` asks the arrow scope, gets false, and permits deletion even though the assigned identifier is the outer function parameter whose mapped arguments object is observed.

## Program-data behavior

`ProgramData` stores `USED_ARGUMENTS` per syntax-context scope.

Its scope merge behavior propagates `arguments` usage through arrows when the arrow itself uses outer `arguments`, but that does not help this case: the `arguments[0]` read is in the outer function while the parameter assignment is visited inside a child arrow.

The assigned identifier retains its binding `SyntaxContext`, giving a plausible way to ask about the owning parameter scope directly. The exact relationship must be proven by candidate execution rather than assumed from naming alone.

## Leading candidate

The smallest candidate to test is to anchor the existing parameter safeguard to the assigned identifier's binding context instead of the current child optimization scope, conceptually:

```rust
self.data.used_arguments(i.id.ctxt)
```

instead of:

```rust
self.data.used_arguments(self.ctx.scope)
```

This is attractive because it does not invent a new alias-analysis system. It makes the existing mapped-arguments fence follow the parameter binding across nested closures.

This is still a **candidate**, not an accepted repair.

## Required candidate matrix

Before promotion, run the candidate against `unused: true` with at least:

1. direct write in the same sloppy function + `arguments[0]` read — must preserve;
2. nested arrow write to outer simple parameter — must preserve;
3. nested ordinary-function write to outer simple parameter — must preserve;
4. strict function nested write — assignment may remain removable;
5. sloppy function where `arguments` is never observed — assignment may remain removable;
6. write to a non-parameter local while `arguments` is observed — removable behavior should stay unchanged;
7. default/rest/destructured parameter controls — verify no semantic regression and record whether the existing conservative parameter fence already retains extra writes.

Then run focused minifier fixtures, formatting, package clippy, and inspect output-size consequences.

## Related source risk

`compress/optimize/dead_code.rs` contains a similar function-parameter / `used_arguments(self.ctx.scope)` safeguard for assignments before function termination. The current campaign RED is isolated to `unused`, but a successful repair should review that sibling condition for the same nested-scope assumption rather than silently fixing only one copy.

Do not broaden the implementation until a discriminator proves the sibling path is affected.

## Current disposition

**OWNER MAPPED; CANDIDATE EXECUTION NEXT.**

The semantic defect is proven, `unused` is isolated as the responsible option, and `drop_unused_assignments` is the exact current deletion owner. The next accepted transition is a semantic-matrix RED/GREEN run for the binding-context candidate, followed by review of the sibling dead-code guard.

No third-party upstream mutation occurred.
