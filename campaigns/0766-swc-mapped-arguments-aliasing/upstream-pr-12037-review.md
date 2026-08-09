# Upstream PR #12037 review — mapped `arguments` aliasing

## In simple words

Fieldwork independently reproduced and isolated campaign #766 before discovering that upstream already has an active implementation PR for the same defect: `swc-project/swc#12037`, titled `fix(es/minifier): preserve argument aliases in nested scopes`.

The upstream patch is the same one-line repair direction Fieldwork derived from current source: replace `used_arguments(self.ctx.scope)` with `used_arguments(i.id.ctxt)` in `drop_unused_assignments`, so the mapped-arguments safeguard follows the parameter binding instead of the nested child scope.

A SWC maintainer has already identified a deeper problem with that patch: the inline pass can change an identifier's syntax context to avoid name collisions. After such rewriting, the new identifier context may have no corresponding `ScopeData`, so `i.id.ctxt` is not guaranteed to remain a durable pointer to the parameter's declaring function.

This means the one-line candidate is useful as a local-path discriminator but is **not sufficient evidence for a general repair** even if it turns the current non-inline semantic matrix green.

Fieldwork should not create a competing SWC implementation branch while #12037 has active upstream ownership. Its useful role is independent reproduction, option isolation, candidate stress-testing, and documenting the unresolved inline compatibility question.

No upstream mutation occurred.

## Upstream PR identity

- PR: `swc-project/swc#12037`
- State observed: open, mergeable, non-draft
- Head: `0a1971a63345e41de567d4fd97c9927283a13201`
- Branch: `fix-12032-preserve-arguments-alias`
- Base recorded by PR: `1b17f343fd13b665f96dcf8c544479f6676d61c8`
- Current Fieldwork target pin: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Upstream issue: #12032

The patch changes:

```rust
!self.data.used_arguments(self.ctx.scope)
```

to:

```rust
!self.data.used_arguments(i.id.ctxt)
```

and adds a nested-assignment regression fixture.

The PR description reports:

- focused #12032 minifier fixture passing;
- full `swc_ecma_minifier` tests: 2,128 passed, 1 ignored;
- package clippy;
- full formatting check;
- Node execution of input and optimized output.

CodSpeed reported no observed performance change across the benchmark set it compared, with some benchmarks skipped/baselined.

## Maintainer objection

Maintainer `Austaras` commented:

> This would not be enough. In inline pass swc would change ident ctxt(to avoid name collision) which would result in non exist scope data.

The PR head remained the same one-line patch at the time of this Fieldwork review.

This objection is technically consistent with SWC's source model:

- scope metadata is keyed by `SyntaxContext`;
- the proposed repair asks `ProgramData::used_arguments` using the identifier's current context;
- the inliner/remapping machinery can rewrite identifier identity/context when moving code;
- a rewritten context need not correspond to the original declaring function's stored scope metadata.

Evidence class: `source-read` plus upstream maintainer review.

## Fieldwork consequence

Campaign #766's current repair status should be read as:

1. **defect:** target-executed RED — accepted;
2. **responsible option:** `unused` — target-executed bisection;
3. **deletion owner:** `drop_unused_assignments` — source-mapped;
4. **one-line binding-context candidate:** locally plausible and currently under Fieldwork semantic-matrix execution;
5. **general repair:** unresolved because identifier context is unstable across inlining;
6. **implementation ownership:** active upstream PR #12037; Fieldwork observe/verify only.

## Highest-value next discriminator

After the local candidate matrix completes, do not promote the one-line patch merely because it is green.

The next useful research question is the maintainer's inline counterexample:

- construct a program where an enclosing sloppy function observes mapped `arguments`;
- the relevant parameter write is moved/copied through an inline transformation that changes identifier context;
- confirm whether the `i.id.ctxt` patch loses access to the original `USED_ARGUMENTS` scope fact;
- distinguish runtime miscompilation from a conservative missed optimization or absent scope metadata.

If that counterexample is reproduced, Fieldwork can document the actual durable data requirement: parameter-to-declaring-function ownership must survive identifier remapping, rather than being reconstructed from whichever `SyntaxContext` the identifier currently carries.

## Coordination disposition

**OBSERVE ACTIVE UPSTREAM / VERIFY REVIEW CONCERN.**

No competing SWC PR, branch, comment, or other upstream mutation should be created automatically. Keep #12037 as the implementation owner and use Fieldwork only for independent evidence and review support.
