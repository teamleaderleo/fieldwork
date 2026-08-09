# SWC Mapped `arguments` Aliasing Across Nested Writes

## In simple words

Campaign #766 has now progressed from target reproduction through option bisection, exact source ownership, and a locally GREEN candidate matrix.

Current pinned SWC's `unused` pass deletes writes to an enclosing simple parameter when those writes occur in nested functions, even though a sloppy function later observes the mapped parameter through `arguments[0]`. The defect is target-executed. `unused` alone is sufficient among the tested compressor options, and the exact deletion owner is `compress/optimize/unused.rs::drop_unused_assignments`.

Fieldwork independently derived a one-line candidate that makes the existing mapped-arguments safeguard query the assigned identifier's context rather than the currently visited nested scope. That candidate passes a seven-case semantic matrix, formatting, package clippy, and diff checks on pinned SWC.

However, active upstream PR `swc-project/swc#12037` already owns the same repair direction, and maintainer review identifies a deeper compatibility problem: SWC's inline pass can remap an identifier's syntax context to avoid collisions, so `i.id.ctxt` is not guaranteed to remain a durable key for the declaring function's scope metadata. The local candidate is therefore **GREEN for the ordinary nested-scope path but not accepted as a general repair**.

Fieldwork will observe and stress-test the active upstream implementation rather than create a competing SWC branch.

- Campaign issue: #766
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Pinned/current SWC: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Initial RED carrier: `teamleaderleo/fieldwork#765`, retired
- Option bisection carrier: `teamleaderleo/fieldwork#767`, retired
- Candidate carrier: `teamleaderleo/fieldwork#768` at `a5becad36b191a83b9a349092e89706c678bb34d`
- Candidate workflow run: `31292179758`
- Candidate job: `93191110056`
- Active upstream implementation: `swc-project/swc#12037`, head observed `0a1971a63345e41de567d4fd97c9927283a13201`
- Local candidate receipt: `candidate-local-green-2026-08-09.md`
- Upstream review note: `upstream-pr-12037-review.md`
- Evidence: `model-executed`, `target-executed` RED, option bisection, `source-read`, local `target-executed` GREEN
- Upstream contact: prohibited for automated workers

## Language invariant

For an ordinary sloppy function with a simple parameter list:

```text
parameter b  <──────── mapped ────────>  arguments[0]
     │
     └── assignment to b must remain observable through arguments[0]
```

Strict functions and non-simple parameter-list cases do not have the same mapped-arguments relation.

The optimizer therefore cannot determine whether a parameter write is dead from ordinary lexical reference counts alone.

## Initial target RED

Under default compression, this source:

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

Pinned SWC emitted empty nested arrow bodies and produced:

```text
1 1
```

The strict result is correct. The sloppy result is wrong.

Carrier #765: workflow `31291592350`, job `93189631053`.

Evidence class: `target-executed` RED.

## Compressor-option bisection

Carrier #767, workflow `31291818612`, job `93190209600`, started from `defaults: false`.

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

Conclusion: **`unused` alone is sufficient and necessary among the tested options.**

The recorder called failing fixtures `HARNESS_NO_OUTPUT` because the SWC fixture harness aborts on stdout mismatch before snapshot persistence. The logs still contain the optimized output and exact `1 1` versus `2 1` assertion, so this label does not weaken the discriminator.

Evidence class: `target-executed` option discriminator.

## Exact source owner

`crates/swc_ecma_minifier/src/compress/optimize/unused.rs::drop_unused_assignments` contains the deletion condition.

Its function-parameter fence is:

```rust
(!var.flags.contains(VarUsageInfoFlags::DECLARED_AS_FN_PARAM)
    || !self.data.used_arguments(self.ctx.scope)
    || self.ctx.expr_ctx.in_strict)
```

When a write to outer parameter `b` is visited inside a nested arrow/function, `self.ctx.scope` is the child function's context. The child does not use its own `arguments`, so the safeguard allows deletion even though the enclosing function owns the parameter and observes its mapped arguments object.

The campaign's source model is therefore:

```text
outer sloppy function scope: USED_ARGUMENTS
    parameter b declared here
    child function scope: no USED_ARGUMENTS
        assignment b = 2 visited here
```

The existing safeguard asks the child-scope question at the wrong nesting level.

## Locally GREEN candidate

Fieldwork tested this one-line runner-only candidate:

```diff
- || !self.data.used_arguments(self.ctx.scope)
+ || !self.data.used_arguments(i.id.ctxt)
```

Carrier #768, exact head `a5becad36b191a83b9a349092e89706c678bb34d`, workflow `31292179758`, job `93191110056`.

Configuration:

```json
{
  "defaults": false,
  "unused": true
}
```

Semantic matrix runtime oracle:

```text
2 2 2 1 7 5 1
```

The cases were:

1. direct sloppy parameter write — retained, runtime `2`;
2. nested arrow write to outer sloppy parameter — retained, runtime `2`;
3. nested ordinary-function write to outer sloppy parameter — retained, runtime `2`;
4. strict nested write — removed, runtime `1`;
5. no `arguments` observation — removed, runtime `7`;
6. unrelated local write while `arguments` is observed — removed, original argument `5` preserved;
7. default-parameter control — runtime correct at `1`, with candidate conservatively retaining the write.

Both fixture executions passed:

```text
UPDATE=1 cargo test -p swc_ecma_minifier --test compress -- mapped_arguments_candidate --nocapture
cargo test -p swc_ecma_minifier --test compress -- mapped_arguments_candidate --nocapture
```

Each reported:

```text
test result: ok. 1 passed; 0 failed; 2927 filtered out
```

The carrier then successfully ran:

```text
cargo fmt --all -- --check
cargo clippy -p swc_ecma_minifier --all-targets -- -D warnings
git diff --check
```

Overall job conclusion: `success`.

Evidence class: local `target-executed` GREEN plus focused package checks. This is not a full repository gate and the candidate exists only inside an execution carrier.

Exact receipt: `candidate-local-green-2026-08-09.md`.

## Why the candidate is still incomplete

Upstream PR #12037 independently contains the same one-line change. SWC maintainer review states:

```text
This would not be enough. In inline pass swc would change ident ctxt(to avoid name collision) which would result in non exist scope data.
```

This is a substantive ownership problem, not a contradiction of the local GREEN result.

`ProgramData` stores `USED_ARGUMENTS` per `SyntaxContext`. The one-line candidate assumes an identifier's current context can be used to find the original declaring-function scope. That assumption holds in the local semantic matrix.

Inlining/remapping can clone or rename bindings with a fresh context. After such code motion:

```text
current identifier ctxt != original declaring-function scope key
```

and `used_arguments(i.id.ctxt)` can fail to recover the original mapped-arguments fact.

The durable semantic requirement is therefore:

> Parameter-to-declaring-function mapped-arguments ownership must survive transformations that rewrite identifier identity/context.

How SWC should represent that ownership remains unresolved.

## Active upstream ownership

Upstream PR #12037 is the implementation surface for this defect. Fieldwork discovered it after independently reproducing the issue, isolating `unused`, mapping `drop_unused_assignments`, and deriving the same one-line candidate.

At Fieldwork review time, #12037 was open and its head still contained the one-line context substitution. Its PR description reports focused and full minifier validation, formatting, clippy, Node runtime comparison, and no observed CodSpeed regression among compared benchmarks. Maintainer review nevertheless blocks treating the patch as complete because of the inline context-remapping case.

Durable review note: `upstream-pr-12037-review.md`.

Disposition: **observe/verify, do not compete.**

## Sibling source condition

`compress/optimize/dead_code.rs` contains a similar `used_arguments(self.ctx.scope)` condition, but it also requires `IS_FN_LOCAL`. Usage analysis clears function-local status across nested function boundaries, so the current nested-write defect does not by itself prove that sibling path is affected.

Do not modify the sibling without a direct discriminator.

## Current disposition

**LOCAL GREEN ACCEPTED; GENERAL REPAIR HOLD / ACTIVE UPSTREAM OWNERSHIP.**

The campaign has proven the defect, isolated the responsible option and source owner, and validated the obvious one-line repair on the ordinary nested-scope path. That is not enough for promotion because identifier context can be rewritten by inlining.

Highest-value next research transition:

1. reproduce or rule out the maintainer's inline/remapped-context concern with a target-native discriminator;
2. determine whether the one-line patch reintroduces the semantic bug after inlining, becomes conservatively safe, or hits missing scope metadata in another way;
3. identify what durable ownership metadata must survive remapping;
4. keep upstream PR #12037 as the implementation owner and make no automated upstream contact.

No third-party upstream mutation occurred.
