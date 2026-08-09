# Upstream PR #12037 review — mapped `arguments` aliasing

## In simple words

Fieldwork independently reproduced campaign #766 and initially derived the same one-line repair as active upstream PR `swc-project/swc#12037`:

```diff
- !self.data.used_arguments(self.ctx.scope)
+ !self.data.used_arguments(i.id.ctxt)
```

That one-line repair is now target-executed **RED** under real SWC inline remapping. Fieldwork also found a separate current-scope strictness bug that the one-line change does not address.

A stronger explicit per-binding ownership candidate is locally GREEN across the original seven-case matrix, the strict-writer/outer-owner discriminator, and real inline cloning, and it passes SWC formatting/package clippy through a deterministic source-pinned patcher.

Active upstream PR #12037 remains the implementation owner. Fieldwork's role is independent evidence and review; no upstream mutation occurred.

## Upstream PR identity

- PR: `swc-project/swc#12037`
- State observed: open, mergeable, non-draft
- Head observed during latest review: `0a1971a63345e41de567d4fd97c9927283a13201`
- Branch: `fix-12032-preserve-arguments-alias`
- Upstream issue: #12032
- Current Fieldwork target pin: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`

At the latest review, upstream still uses the one-line `i.id.ctxt` implementation.

## What the one-line patch gets right

Fieldwork carrier #768 applied the same change under `{ "defaults": false, "unused": true }` and passed a seven-case ordinary-path matrix plus formatting/package clippy.

Oracle:

```text
2 2 2 1 7 5 1
```

That proves `i.id.ctxt` corrects the original nested-scope failure while the parameter binding retains its original context.

Receipt: `candidate-local-green-2026-08-09.md`.

## Maintainer remap objection — confirmed

Maintainer `Austaras` warned that inlining changes identifier contexts to avoid collisions, so a cloned parameter's fresh context may have no corresponding function scope metadata.

Owned-fork PR #8 forces multi-use cloning of a sloppy mapped parameter. Carrier #769 first proved real cloning on pinned base SWC: two cloned bodies retained both `b = 2` assignments and runtime was `2 2`.

Applying only the upstream/Fieldwork one-line candidate removed both assignments and changed runtime to:

```text
1 1
```

The target fixture then failed its `2 2` stdout assertion with an actual `test result: FAILED` receipt.

Evidence: `target-executed` base GREEN plus candidate RED.

Exact receipt: `inline-remap-2026-08-09.md`.

### Why it fails

`ProgramData::used_arguments(ctxt)` returns false when the supplied context has no `ScopeData` record.

The inliner gives cloned bindings a fresh `SyntaxContext` and copies full `VarUsageInfo` to the new Id. The fresh binding context is a hygiene identity, not the lexical function scope that owns `ScopeData::USED_ARGUMENTS`.

```text
binding identity after remap
        !=
declaring function scope that owns mapped arguments
```

## Additional ownership defect — writer strictness

The current guard also uses:

```rust
self.ctx.expr_ctx.in_strict
```

from the scope currently visiting the assignment.

Fieldwork added a discriminator where a strict nested function writes a parameter of a sloppy outer function. JavaScript requires the outer mapped `arguments[0]` to observe that write.

Expected:

```text
2 1
```

Pinned SWC removed both nested writes and produced:

```text
1 1
```

Evidence: `target-executed` RED. Receipt: `owner-strictness-red-2026-08-09.md`.

This shows the repair must preserve declaring-function ownership for both `arguments` use and strictness semantics; switching only from `self.ctx.scope` to `i.id.ctxt` cannot solve the full problem.

## Explicit ownership candidate — GREEN

Fieldwork's replacement candidate adds a per-binding `VarUsageInfo` fact for parameters of ordinary functions whose lexical scope uses `arguments`.

The usage analyzer establishes the fact after the declaring function body is analyzed. The inliner already clones `VarUsageInfo`, so the fact survives fresh binding contexts. `drop_unused_assignments` consults that stable metadata instead of writer scope or current binding context.

Carrier #770 semantic run `31294224774`, job `93196547013`, passed:

- seven-case ordinary matrix — `2 2 2 1 7 5 1`;
- declaring-owner strictness — `2 1`;
- real inline-remap cloning — `2 2`.

A deterministic source-pinned patcher `apply-explicit-ownership.py` was then validated by run `31294497411`, job `93197236450`:

```text
cargo fmt --all -- --check
cargo clippy -p swc_ecma_minifier --all-targets -- -D warnings
git diff --check
```

All passed.

Exact receipt: `explicit-ownership-candidate-2026-08-09.md`.

## Precision caveat

The candidate currently records a conservative fact:

> parameter of an ordinary function whose lexical scope uses `arguments`

It does not encode strict/non-simple declaring-function rules exactly. Consequently, some semantically dead parameter writes can remain in strict or non-simple controls.

That is a compression-quality cost, not a correctness failure. The usage analyzer currently lacks strict-mode state, so exact strictness precision would widen the analysis change. SWC's dedicated `arguments` optimizer offers useful precedent for plain-identifier/duplicate/shadowing precision.

## Coordination disposition

**CURRENT UPSTREAM ONE-LINE PATCH REJECTED BY TARGET EVIDENCE / EXPLICIT-OWNERSHIP ALTERNATIVE GREEN / OBSERVE ACTIVE UPSTREAM.**

Fieldwork should:

1. measure the conservative retention cost;
2. re-run the inline-remap and owner-strictness discriminators on any new upstream #12037 revision;
3. keep upstream ownership human-driven and perform no automated comments, reviews, branch writes, or pull requests.
