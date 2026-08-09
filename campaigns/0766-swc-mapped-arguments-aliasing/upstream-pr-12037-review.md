# Upstream PR #12037 review — mapped `arguments` aliasing

## In simple words

Fieldwork independently reproduced and isolated campaign #766 before discovering active upstream PR `swc-project/swc#12037`, titled `fix(es/minifier): preserve argument aliases in nested scopes`.

The upstream patch uses the same one-line repair Fieldwork initially derived:

```diff
- !self.data.used_arguments(self.ctx.scope)
+ !self.data.used_arguments(i.id.ctxt)
```

SWC maintainer `Austaras` objected that the inline pass changes identifier contexts to avoid collisions, so a cloned parameter's new context may have no corresponding scope metadata.

Fieldwork has now reproduced that exact objection with target-native execution. Pinned SWC clones/inlines the test function twice and correctly runs `2 2`. Applying only the one-line candidate removes both mapped parameter writes and changes runtime output to `1 1`.

The one-line candidate is therefore **rejected as a general repair**. Active upstream PR #12037 remains the implementation owner; Fieldwork's role is independent evidence and repair-model research. No upstream mutation occurred.

## Upstream PR identity

- PR: `swc-project/swc#12037`
- State observed: open, mergeable, non-draft
- Head observed during review: `0a1971a63345e41de567d4fd97c9927283a13201`
- Branch: `fix-12032-preserve-arguments-alias`
- Upstream issue: #12032
- Current Fieldwork target pin: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`

## What the local ordinary-path matrix proved

Before the inline stress test, Fieldwork carrier #768 applied the same one-line candidate under `{ "defaults": false, "unused": true }` and passed a seven-case semantic matrix plus formatting, package clippy, and diff checks.

That result established that `i.id.ctxt` corrects the ordinary nested-scope bug when the parameter's identity has not been remapped. It did not establish durability under code motion.

Receipt: `candidate-local-green-2026-08-09.md`.

## Maintainer objection — now target-executed

The exact stress discriminator is owned-fork PR `teamleaderleo/swc#8` at `7ddbae67c1b70cca2319bd5820bdb92a78797366`.

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

Fieldwork carrier #769, run `31293367121`, job `93194367502`, first proved that base SWC cloned the body twice. Base output retained `b = 2` in each clone and ran:

```text
2 2
```

The runner then applied only:

```diff
- || !self.data.used_arguments(self.ctx.scope)
+ || !self.data.used_arguments(i.id.ctxt)
```

Candidate output removed both assignments:

```js
console.log(function(b, c, d, e, f, g, h, i, j, k, l, m) {
    return arguments[0];
}(1), function(b, c, d, e, f, g, h, i, j, k, l, m) {
    return arguments[0];
}(1));
```

Runtime became:

```text
1 1
```

The target fixture then failed its `2 2` stdout assertion with an actual `test result: FAILED` receipt.

Evidence class: `target-executed` base GREEN plus candidate RED.

Exact receipt: `inline-remap-2026-08-09.md`.

## Why it fails

`ProgramData::used_arguments(ctxt)` returns `false` when the supplied context has no `ScopeData` record.

The inliner assigns cloned bindings a fresh `SyntaxContext` and copies `VarUsageInfo` to the remapped `Id`. That new binding context is a hygiene identity, not the lexical function scope that owns `ScopeData::USED_ARGUMENTS`.

The one-line patch therefore conflates two identities:

```text
binding identity after remap
        !=
declaring function scope that owns mapped arguments
```

That conflation is now directly tied to a runtime miscompile.

## Repair model

The durable query in `drop_unused_assignments` is not "does the current identifier context use arguments?" It is:

> Is this binding a simple sloppy parameter whose declaring function uses the mapped `arguments` object?

The strongest current direction is explicit per-binding metadata, because `VarUsageInfo` already survives inline cloning. Two designs remain worth comparing:

1. add a mapped-arguments parameter flag to `VarUsageInfo` after function analysis establishes both simple-parameter status and `USED_ARGUMENTS`;
2. store the parameter's declaring-function context/owner on variable metadata and query that stable owner after remapping.

Copying complete `ScopeData` onto fresh binding contexts is weaker conceptually because it makes a hygiene context impersonate a lexical function scope. Recovering ownership through `SyntaxContext` ancestry is also broader and should require a separate discriminator before use.

## Coordination disposition

**MAINTAINER OBJECTION CONFIRMED / ONE-LINE PATCH REJECTED / OBSERVE ACTIVE UPSTREAM.**

Fieldwork should continue with an explicit ownership candidate and run both the existing seven-case semantic matrix and the inline-remap discriminator. Do not create an automated upstream branch, comment, review, or PR.
