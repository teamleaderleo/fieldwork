# SWC Mapped `arguments` Aliasing Across Nested Writes

## In simple words

Campaign #766 has now moved past the initial defect and past the obvious one-line repair.

Pinned SWC has a target-reproduced `unused`-pass bug: a nested write to an enclosing simple parameter can be deleted even though a sloppy function later observes that parameter through mapped `arguments[0]`.

Fieldwork isolated the failure to `unused`, mapped the deletion owner to `compress/optimize/unused.rs::drop_unused_assignments`, and initially validated the same one-line candidate as active upstream PR `swc-project/swc#12037` on a seven-case non-inline matrix.

SWC maintainer review warned that `i.id.ctxt` is unstable because inlining gives cloned bindings a fresh `SyntaxContext`. Fieldwork has now reproduced that exact concern with target-native execution: base SWC cloned the function twice and ran `2 2`; applying only the one-line `i.id.ctxt` candidate deleted both parameter writes and ran `1 1`.

The one-line candidate is therefore rejected as a general repair. The next repair must preserve parameter-to-declaring-function mapped-arguments ownership across identifier remapping.

- Campaign issue: #766
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Pinned/current SWC: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Initial RED carrier: `teamleaderleo/fieldwork#765`, retired
- Option bisection carrier: `teamleaderleo/fieldwork#767`, retired
- Ordinary-path candidate carrier: `teamleaderleo/fieldwork#768`, retired
- Inline-remap discriminator: `teamleaderleo/swc#8` at `7ddbae67c1b70cca2319bd5820bdb92a78797366`
- Inline-remap carrier: `teamleaderleo/fieldwork#769` at `79d7c2f685486da1f3820fe16e217a97111a7e6f`
- Inline-remap run/job: `31293367121` / `93194367502`
- Active upstream implementation: `swc-project/swc#12037`
- Ordinary-path receipt: `candidate-local-green-2026-08-09.md`
- Inline-remap receipt: `inline-remap-2026-08-09.md`
- Upstream review note: `upstream-pr-12037-review.md`
- Evidence: `model-executed`, target RED, option bisection, ordinary-path local GREEN, inline-remap target GREEN/RED discriminator
- Upstream contact: prohibited for automated workers

## Language invariant

For an ordinary sloppy function with a simple parameter list:

```text
parameter b  <──────── mapped ────────>  arguments[0]
```

A write to `b` remains observable through `arguments[0]`, including a write performed by a nested closure that captures `b`.

Strict functions and non-simple parameter lists do not use the same mapped-arguments relation.

## Initial target RED

The original discriminator used a sloppy and strict function pair. Pinned SWC under default compression produced `1 1` where JavaScript semantics require `2 1`.

Carrier #765: run `31291592350`, job `93189631053`.

Evidence class: `target-executed` RED.

## Option bisection

Carrier #767, run `31291818612`, job `93190209600`, started from `defaults: false`.

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

Conclusion: `unused` alone is sufficient among the tested compressor options.

## Exact source owner

`drop_unused_assignments` currently guards dead writes to parameters with:

```rust
(!var.flags.contains(VarUsageInfoFlags::DECLARED_AS_FN_PARAM)
    || !self.data.used_arguments(self.ctx.scope)
    || self.ctx.expr_ctx.in_strict)
```

When the assignment to an outer parameter is visited inside a nested function, `self.ctx.scope` belongs to the nested function. The mapped `arguments` object belongs to the enclosing function.

That explains the original bug.

## Ordinary-path one-line candidate

Fieldwork and upstream PR #12037 independently arrived at:

```diff
- || !self.data.used_arguments(self.ctx.scope)
+ || !self.data.used_arguments(i.id.ctxt)
```

Carrier #768 validated this under `{ "defaults": false, "unused": true }` on seven cases covering direct/nested sloppy writes, strict behavior, no-arguments observation, unrelated locals, and a default-parameter control.

Runtime oracle:

```text
2 2 2 1 7 5 1
```

The fixture passed before and after snapshot materialization, plus package clippy, formatting, and `git diff --check`.

Evidence class: local `target-executed` GREEN on the ordinary non-remapped path.

## Inline-remap discriminator — maintainer concern confirmed

Maintainer `Austaras` warned that the inline pass changes identifier context to avoid collisions, so `i.id.ctxt` may no longer have scope metadata.

Owned-fork PR #8 forces SWC's multi-use function-inlining path:

```js
function mapped(b, c, d, e, f, g, h, i, j, k, l, m) {
    return (b = 2, arguments[0]);
}

console.log(mapped(1), mapped(1));
```

with:

```json
{
  "defaults": false,
  "unused": true,
  "inline": 3,
  "toplevel": true
}
```

Carrier #769 first required base SWC to prove cloning. Base output contained two function clones, two `arguments[0]` reads, and both `b = 2` assignments. Runtime:

```text
2 2
```

The runner then applied only the one-line `i.id.ctxt` candidate. Candidate output became:

```js
console.log(function(b, c, d, e, f, g, h, i, j, k, l, m) {
    return arguments[0];
}(1), function(b, c, d, e, f, g, h, i, j, k, l, m) {
    return arguments[0];
}(1));
```

Runtime:

```text
1 1
```

The target fixture then failed its `2 2` stdout assertion with an actual `test result: FAILED` receipt.

Evidence class: `target-executed` base GREEN plus candidate RED.

Exact receipt: `inline-remap-2026-08-09.md`.

## Why the one-line candidate fails

`ProgramData::used_arguments(ctxt)` returns false if there is no `ScopeData` entry for that context.

SWC's inliner gives cloned bindings a fresh `SyntaxContext` and copies `VarUsageInfo` to the remapped `Id`. The fresh binding context does not become the lexical function scope that owns `ScopeData::USED_ARGUMENTS`.

So the one-line candidate confuses:

```text
current binding hygiene context
```

with:

```text
declaring function scope that owns mapped arguments
```

That identity mismatch is now tied directly to the `2 2 -> 1 1` runtime regression.

## Current data-model finding

`VarUsageInfo` already carries `DECLARED_AS_FN_PARAM`, and the inliner already clones the full `VarUsageInfo` record when it remaps an identifier.

`ScopeData::USED_ARGUMENTS` remains function-scoped.

This makes per-binding metadata the strongest current repair direction. The unused pass needs one stable fact:

> This binding is a simple sloppy parameter whose declaring function uses mapped `arguments`.

Two implementation designs remain credible:

1. **mapped-parameter flag** — set an explicit `VarUsageInfo` flag after function analysis establishes simple-parameter + sloppy + `USED_ARGUMENTS`, then let that flag follow remapped clones;
2. **declaring-function owner** — store a stable declaring-function context on parameter metadata and query that owner after code motion.

Copying complete `ScopeData` onto fresh binding contexts is weaker because a hygiene identity should not impersonate a lexical function scope. Walking `SyntaxContext` ancestry to guess the owner is broader and needs its own proof before use.

## Active upstream ownership

Upstream PR #12037 remains the implementation surface. Fieldwork should preserve independent evidence, verify later revisions, and avoid a competing automated upstream implementation.

Durable review: `upstream-pr-12037-review.md`.

## Current disposition

**ONE-LINE CANDIDATE REJECTED / EXPLICIT OWNERSHIP REPAIR REQUIRED / ACTIVE UPSTREAM OWNERSHIP.**

Next research transition:

1. determine the smallest per-binding representation that can express mapped-arguments parameter ownership;
2. prepare a runner-only or owned-fork candidate using that representation;
3. require the existing seven-case matrix and the inline-remap fixture to pass together;
4. retain strict and non-simple-parameter controls;
5. review the exact active upstream PR head before promotion language changes.

No third-party upstream mutation occurred.
