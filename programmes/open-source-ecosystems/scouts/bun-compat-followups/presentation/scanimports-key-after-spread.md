# Candidate: make `scanImports()` report the JSX key-after-spread fallback dependency

Fieldwork #709 follow-up. Deepened 2026-08-09.

Automated upstream contact: **none**.

## Proposed title

`transpiler: report the classic JSX dependency for key-after-spread in scanImports`

## Parent breadcrumb

https://redirect.github.com/oven-sh/bun/pull/35557

Current source pin for this packet: parent head `2f2125e73a65cebef62c32c32acd3d114ac67e09`.

The parent PR changes `Bun.Transpiler` so automatic JSX imports are emitted by default and aligns `.scan()` / `.scanImports()` with the normal automatic-runtime dependency.

It explicitly leaves one known inaccuracy: a deprecated key-after-spread element falls back to `createElement` from the bare JSX package, while the scan-only pass can still report the automatic runtime subpath.

Ownership searches found no separate open PR/issue for this exact follow-up.

## Exact mismatch proved by the parent PR

The parent adds this transform regression:

```tsx
export default <div {...obj} key="after" />;
```

and asserts that `transformSync()` emits:

```js
import { createElement as ... } from "react";
```

But its scan-only implementation adds `p.options.jsx.import_source()` whenever its coarse `needs_jsx_import` bit is true. In development automatic mode that path is `react/jsx-dev-runtime`.

So the mismatch is concrete:

- transformed code depends on `react`;
- `scanImports()` reports `react/jsx-dev-runtime`.

## Why this is smaller than the parent note suggests

The parent description says the scan pass lacks per-symbol use counts. That is true for choosing among individual automatic-runtime symbols, but dependency-path fidelity for this fallback does not require symbol counts.

Current `src/js_parser/parse/parse_jsx.rs` already computes during parsing:

```rust
let is_key_after_spread =
    key_prop_i > -1 && first_spread_prop_i > -1 && key_prop_i > first_spread_prop_i;
```

and stores the corresponding `JSXElement::IsKeyAfterSpread` flag. The full visitor later checks that exact flag and, under automatic runtime, routes the element through `JSXImport::CreateElement`.

The scan-only parser therefore already knows the condition that changes the dependency path. It only loses that fact before scan finalization.

## Prepared source patch

Fieldwork now contains a proposed patch against the parent head:

`../proposed-patches/scanimports-key-after-spread.patch`

It is intentionally narrow:

1. Keep separate scan-only booleans for automatic-runtime JSX and classic-fallback JSX.
2. Classify each JSX element after its attributes are parsed, when `is_key_after_spread` is known.
3. Recursive child elements classify themselves, so a fallback parent containing ordinary JSX can request both dependencies.
4. After `@jsxRuntime` / `@jsxImportSource` normalization, inject:
   - `jsx.import_source()` when ordinary automatic JSX was seen;
   - `jsx.classic_import_source` when key-after-spread fallback JSX was seen.
5. Keep the existing `autoImportJSX` + automatic-runtime gate, so classic runtime and opt-out behavior stay unchanged.

No visitor execution and no symbol-use reconstruction are introduced.

## Hardened regression matrix

The prepared Fieldwork test now covers:

- fallback-only -> bare `react`;
- normal JSX -> `react/jsx-dev-runtime`;
- fragment -> automatic runtime dependency;
- separate normal + fallback elements -> both dependencies;
- normal child nested inside a fallback parent -> both dependencies;
- `jsxImportSource: "preact"` -> bare `preact` for fallback;
- `@jsxImportSource preact` -> bare `preact` for fallback;
- `@jsxRuntime automatic` overriding classic config -> fallback classification still works;
- `@jsxRuntime classic` overriding automatic config -> no injected scan dependency;
- `autoImportJSX: false` -> no injected scan dependency.

The nested case is the important guard against replacing one coarse boolean with another: one JSX tree can legitimately need both the bare package and the runtime subpath.

## Static review notes

- The added bookkeeping is used only by the scan-only path; the full parse/visitor result is unchanged.
- Runtime pragma normalization happens after parsing in the current scan path. The proposed booleans therefore record syntax categories, then finalization applies the resolved runtime/import-source policy.
- `classic_import_source` is already the source used for the classic/createElement package and is updated by the parent's `@jsxImportSource` normalization.
- The parser repository note about bumping the runtime transpiler-cache version applies to changes that affect runtime transformed output. This candidate changes scan-only dependency reporting; it does not alter transform output or the runtime transpiler cache key.

## Remaining validation

Exact Bun execution is still required before treating the patch as target-proven. The current scout environment does not have the pinned Bun build, so this packet remains:

- implementation reasoning: `source-read`
- proposed patch: `source-read`
- regression file: `target-test-prepared`

If exact-target execution reveals that `classic_import_source` is normalized differently for one custom-source case, adjust the finalizer to use the same bare-package accessor as `JSXImport::CreateElement`; do not broaden the parser design.

## Disposition

**Presentable implementation candidate.** The source seam, proposed diff, and regression matrix are ready for exact-target validation after #35557 settles.