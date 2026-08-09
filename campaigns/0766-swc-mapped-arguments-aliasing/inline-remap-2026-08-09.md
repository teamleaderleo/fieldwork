# SWC mapped `arguments` inline-remap receipt

## In simple words

The maintainer objection to the one-line `i.id.ctxt` repair is now target-executed and confirmed.

Pinned SWC correctly preserves sloppy parameter/`arguments` aliasing after cloning the same function body twice through the multi-use inliner. Applying only the active one-line candidate inside the runner then deletes the parameter assignment in both cloned functions and changes runtime output from `2 2` to `1 1`.

This proves that the identifier's remapped `SyntaxContext` is not a durable substitute for the declaring function's mapped-arguments ownership.

Evidence class: `target-executed` base GREEN plus candidate RED.

No third-party upstream mutation occurred.

## Exact execution identity

- SWC test-only discriminator: `teamleaderleo/swc#8`
- exact SWC head: `7ddbae67c1b70cca2319bd5820bdb92a78797366`
- pinned source ancestor: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Fieldwork execution carrier: `teamleaderleo/fieldwork#769`
- exact carrier head: `79d7c2f685486da1f3820fe16e217a97111a7e6f`
- workflow run: `31293367121`
- job: `93194367502`
- runner: Ubuntu 24.04, GitHub-hosted, Azure westus
- Rust toolchain: `nightly-2026-04-10`, rustc `1.96.0-nightly (f5eca4fcf 2026-04-09)`

## Discriminator

Configuration:

```json
{
  "defaults": false,
  "unused": true,
  "inline": 3,
  "toplevel": true
}
```

Input:

```js
function mapped(b, c, d, e, f, g, h, i, j, k, l, m) {
    return (b = 2, arguments[0]);
}

console.log(mapped(1), mapped(1));
```

Runtime oracle:

```text
2 2
```

The extra declared parameters raise SWC's multi-use inline cost budget. `toplevel: true` clears the top-level declaration-removal gate. The semantic dependency remains only on simple sloppy parameter `b` and mapped `arguments[0]`.

## Base result — GREEN after proven cloning

The pinned base fixture passed before the candidate was applied.

Generated output:

```js
console.log(function(b, c, d, e, f, g, h, i, j, k, l, m) {
    return b = 2, arguments[0];
}(1), function(b, c, d, e, f, g, h, i, j, k, l, m) {
    return b = 2, arguments[0];
}(1));
```

Runtime:

```text
2 2
```

The carrier also required two proof conditions before continuing:

- the original `function mapped` declaration had disappeared;
- generated output contained two `arguments[0]` occurrences.

Both held. This is target evidence that the function body was cloned/inlined twice while base SWC preserved mapped aliasing.

## Candidate applied

The runner then changed exactly one source condition:

```diff
- || !self.data.used_arguments(self.ctx.scope)
+ || !self.data.used_arguments(i.id.ctxt)
```

No other production source change was applied.

## Candidate result — RED

Generated output after the one-line candidate:

```js
console.log(function(b, c, d, e, f, g, h, i, j, k, l, m) {
    return arguments[0];
}(1), function(b, c, d, e, f, g, h, i, j, k, l, m) {
    return arguments[0];
}(1));
```

Both `b = 2` assignments disappeared.

Direct Node runtime:

```text
1 1
```

The target fixture was then re-run with the `2 2` runtime oracle and failed with an actual semantic assertion:

```text
Diff < left / right > :
<1 1
>2 2

test result: FAILED. 0 passed; 1 failed; 2927 filtered out
```

This is the intended target RED, not a setup or compilation failure.

## Source explanation

`ProgramData::used_arguments(ctxt)` returns `false` when no scope record exists for the supplied context.

The inliner gives cloned bindings a fresh `SyntaxContext` and copies their `VarUsageInfo` to the remapped `Id`. It does not make that fresh binding context the lexical function scope that owns `ScopeData::USED_ARGUMENTS`.

Therefore the one-line candidate asks a function-scope question using a hygiene identity that is free to change during cloning:

```text
declaring function scope owns USED_ARGUMENTS
        │
        ├── original parameter Id
        │
        └── inline clone gets fresh binding ctxt
                 │
                 └── used_arguments(fresh ctxt) => false
```

`drop_unused_assignments` then treats the cloned parameter assignment as dead and removes it.

## Repair consequence

**REJECT the one-line `i.id.ctxt` candidate as a general repair.**

The durable fact needed by the unused pass is:

> This variable is a simple sloppy function parameter whose declaring function uses its mapped `arguments` object.

That fact must survive identifier remapping.

The leading implementation direction is to carry the mapped-parameter ownership/fact with `VarUsageInfo` or another explicit per-binding owner record, because `VarUsageInfo` is already cloned onto remapped IDs by the inliner. Copying or inferring whole function `ScopeData` from arbitrary binding contexts would mix lexical-function metadata with hygiene identity.

A secondary direction is an explicit map from parameter binding to declaring-function context that the inliner remaps alongside variable metadata. Syntax-context ancestry should be treated as a fallback research branch rather than the default ownership model.

## Disposition

**TARGET-EXECUTED REVIEW CONCERN CONFIRMED / ONE-LINE CANDIDATE REJECTED.**

Next research transition:

1. design an explicit mapped-parameter ownership representation that survives remapping;
2. run the existing seven-case matrix plus this inline-remap fixture against that candidate;
3. preserve strict and non-simple-parameter controls;
4. keep active upstream PR `swc-project/swc#12037` as the implementation owner and make no automated upstream contact.
