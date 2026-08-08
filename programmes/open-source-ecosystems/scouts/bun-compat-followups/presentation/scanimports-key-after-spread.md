# Candidate: make `scanImports()` report the JSX key-after-spread fallback dependency

Fieldwork #709 follow-up. Prepared 2026-08-09.

Automated upstream contact: **none**.

## Proposed title

`transpiler: report the classic JSX dependency for key-after-spread in scanImports`

## Parent breadcrumb

https://redirect.github.com/oven-sh/bun/pull/35557

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

But its scan-only implementation adds one dependency whenever `p.needs_jsx_import` is true:

```rust
let import_source = p.options.jsx.import_source();
p.add_import_record(ImportKind::Stmt, ..., import_source);
```

For the same development config, that path is `react/jsx-dev-runtime`.

So the mismatch is concrete:

- transformed code depends on `react`;
- `scanImports()` reports `react/jsx-dev-runtime`.

## Why this may be smaller than the parent note suggests

The parent description says the scan pass lacks per-symbol use counts. That is true for determining exactly which `jsx` / `jsxs` / `Fragment` symbols are needed, but dependency-path fidelity for this fallback does not appear to require symbol counts.

Current `src/js_parser/parse/parse_jsx.rs` already computes, during parsing:

```rust
let is_key_after_spread =
    key_prop_i > -1 && first_spread_prop_i > -1 && key_prop_i > first_spread_prop_i;
```

and sets `JSXElement::IsKeyAfterSpread` before returning the element. The full visitor later checks that flag and, under automatic runtime, routes the element through `JSXImport::CreateElement`.

The scan-only parser therefore already knows the exact condition that changes the dependency path. It only fails to retain that fact in scan-level bookkeeping.

## Suggested implementation seam

Prepare on top of #35557 once it settles.

A narrow implementation should be possible with two scan-level facts:

- some JSX needs the automatic runtime import;
- some JSX needs the classic bare-package `createElement` import because of key-after-spread fallback.

Possible implementation:

1. Add a scan-only parser boolean such as `needs_classic_jsx_import`.
2. In `parse_jsx_element`, after `is_key_after_spread` is known, mark the classic boolean when runtime is automatic and this element will take the fallback.
3. Ensure `needs_jsx_import` means at least one element/fragment actually uses the automatic transform, rather than unconditionally setting it for every JSX element before attributes are parsed.
4. At scan finalization, when `autoImportJSX` is enabled under automatic runtime:
   - add `p.options.jsx.import_source()` if automatic JSX was seen;
   - add the bare/classic import source (`react`, `preact`, custom `jsxImportSource`, etc.) if fallback JSX was seen.
5. If both forms occur in one file, report both dependencies.

The pragma/config normalization already added by #35557 should be reused so custom `@jsxImportSource` / tsconfig sources choose the same bare package that `transformSync()` uses.

## Regression matrix

With development automatic runtime:

### Fallback only

```tsx
export default <div {...obj} key="after" />;
```

Expected `.scanImports()` / `.scan().imports`:

```js
[{ kind: "import-statement", path: "react" }]
```

### Normal automatic only

```tsx
export default <div />;
```

Expected:

```js
[{ kind: "import-statement", path: "react/jsx-dev-runtime" }]
```

### Mixed

```tsx
export const normal = <span />;
export const fallback = <div {...obj} key="after" />;
```

Expected dependency set contains both:

- `react/jsx-dev-runtime`
- `react`

### Custom source

With `jsxImportSource: "preact"`, fallback-only should report `preact`, while normal automatic JSX reports `preact/jsx-runtime` or `preact/jsx-dev-runtime` according to mode.

### Opt-out/control

- `autoImportJSX: false` → no injected dependency records
- classic runtime → preserve existing scan behavior
- no JSX → none

## Risk

Low-to-medium. The main subtlety is mixed files and fragments: scan bookkeeping must not replace the automatic-runtime record merely because one separate element takes the classic fallback.

This should stay parser-local plus tests. If implementation starts requiring visitor execution or symbol-usage reconstruction, demote it rather than broadening the change.

## Evidence

- parent transform/scan tests: `source-read`
- current parse-time `is_key_after_spread` detection: `source-read`
- current full-visitor fallback to `JSXImport::CreateElement`: `source-read`
- prepared regression: `target-test-prepared` after candidate test file is added
- exact Bun execution: unavailable in current scout environment

## Disposition

**Promote.** This is a good small follow-up candidate after #35557 stabilizes and is probably simpler than the parent PR's prose initially implied.