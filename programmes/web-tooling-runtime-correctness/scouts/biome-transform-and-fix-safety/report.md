# Biome transform and fix safety scout

## In simple words

Biome 2.5.6 produced stable second-pass formatting across three realistic owned repositories. A minimized Node case proved that `organizeImports` can reorder re-export declarations and reverse JavaScript module evaluation order, changing output from `star,named` to `named,star` after ordinary `biome check --write`.

A follow-up standards, source-design, and ecosystem review changed the product conclusion. The semantic effect is real, but sorting normal imports and re-exports while protecting only obvious side-effect imports is a common organizer policy and was an intentional part of Biome's import-sorter design. The case does not currently justify an upstream bug, production fix, finding, or campaign without realistic breakage or a stronger project promise.

The trials also found an expected Tailwind CSS parser option, one correctly rejected malformed JSON file, consistent parent configuration discovery, and a Prettier migration blocked by an undeclared dependency in the project's own configuration. No upstream contact occurred.

**Current answer:** retain the re-export reproduction as a documented semantic caveat and negative product conclusion. Do not promote or contact upstream. Retain the Tailwind case as compatibility evidence. Repeat Prettier migration with a project whose existing Prettier command succeeds. Treat the Renderprove full-suite failures as unresolved project-test sensitivity because formatter-only output preserved the JavaScript and TypeScript ASTs examined.

## Identity

- Fieldwork issue: #27
- Programme: #15, Web tooling runtime correctness
- Target hub: #6, Biome
- Worker: `chatgpt:gpt-5.6-thinking`
- Initial scout date: 2026-07-29
- Follow-up synthesis date: 2026-07-30
- Owned path: `programmes/web-tooling-runtime-correctness/scouts/biome-transform-and-fix-safety/`
- Scout branch: `scout/27-biome-transform-fix-safety`
- Upstream contact authorized: `no`
- Upstream interaction performed: `none`

## Question

Which Biome parser, formatter, safe-fix, configuration, migration, and project-compatibility boundaries produce consequential behaviour on realistic JavaScript and TypeScript projects?

## Scope supported

The scout exercised:

- JavaScript, TypeScript, TSX, JSON, and CSS parsing and formatting;
- project-wide first and second formatter passes;
- `check --write` safe fixes and assists;
- nested working-directory configuration discovery;
- Tailwind-specific CSS parsing;
- Prettier migration startup;
- post-change type checks and tests where the project suite remained a valid oracle.

It does not support a language-server correctness claim, a formal performance comparison, browser-editor integration, Windows behaviour, or every Biome language.

## Revisions

### Target

- Package: `@biomejs/biome@2.5.6`
- Matching source revision: `biomejs/biome@d890b39c3ef21040bded453d9af91e1b301a0d67`
- Source reference: https://redirect.github.com/biomejs/biome/commit/d890b39c3ef21040bded453d9af91e1b301a0d67

### Fieldwork

- Protocol revision read at claim time: `09fe47ac92ec9c0c333b4979011f6321795deff2`
- Scout branch base after intervening documentation changes: `976b436d4d7e2741dee5505b6715839db9bd4e15`

### Testbeds

| Testbed | Content revision | Trial branch head | Actions merge revision | Trial PR |
| --- | --- | --- | --- | --- |
| Elatura | `bbea414c6e400ba748d053caedb777ecee1cc381` | `af8c853b12524765443cf8328b2624998550972e` | `61a01db0bd7b201f87c8905aae75604b6705bd99` | https://redirect.github.com/teamleaderleo/elatura/pull/57 |
| Scrapbook | `ea708e027d63bd4235ccbcd358e81efcd41a560b` | `b79c04f0e8877400da21f78cbf2074ed7b02b5cc` | `9cd8105c95ed453724560db6ca46be36c393df0d` | https://redirect.github.com/teamleaderleo/scrapbook/pull/492 |
| Renderprove | `3e954bdbf37b71dc06db6dd5a0b46bf2f296eb29` | `889785fdb681118c3adcc90e9cd87ec8b346b005` | `1e203d75443e47d18a02e45d1a0329b8f1ff72c2` | https://redirect.github.com/teamleaderleo/renderprove/pull/36 |

The Actions merge revisions contain the pinned testbed content plus the reversible trial workflow.

## Why these testbeds

- **Elatura:** a TypeScript workspace and browser-sidecar project with JSON schemas, Vitest, type checking, builds, and package boundaries.
- **Scrapbook:** a large Next.js and React application with TSX, CSS, Tailwind directives, pnpm, Prettier, Vitest, and Playwright.
- **Renderprove:** a pure ESM JavaScript package with MCP commands, browser automation, JSON schemas, Node tests, and many import/re-export surfaces.

## Method

Each trial used a dedicated `fieldwork/biome/issue-27` branch and draft pull request. Workflows had read-only repository permissions, synthetic public environment values where required, no production credentials, and a close-without-merge disposition.

Common sequence:

1. install pinned project dependencies;
2. record Biome 2.5.6;
3. run `biome check .` with bounded diagnostics;
4. reset the tree;
5. run `biome format . --write` and retain the patch;
6. run the same formatter command again and compare complete patches byte-for-byte;
7. reset the tree;
8. run `biome check . --write` and retain the safe-fix patch;
9. run project validation and tests;
10. compare nested configuration discovery using actual output files;
11. add targeted Tailwind, migration, assist-isolation, and ESM evaluation probes;
12. challenge the strongest candidate against the language standard, Biome's design record, comparable tools, and existing issue norms before promotion.

## Code and test map

Target source revision: `d890b39c3ef21040bded453d9af91e1b301a0d67`.

| Area | Primary code | Relevant tests or harness | Relevance |
| --- | --- | --- | --- |
| Package identity | `packages/@biomejs/biome/package.json` | release process | Pins version 2.5.6. |
| `check` orchestration | `crates/biome_cli/src/commands/check.rs` | `crates/biome_cli/tests/commands/check.rs` | Requests format, lint, and assist features; `--write` selects safe fixes unless unsafe mode is requested. |
| Import/export organization | `crates/biome_js_analyze/src/assist/source/organize_imports.rs` | assist specs and CLI cases | Handles imports and exports, is recommended, and declares `FixKind::Safe`. |
| Sort keys | `crates/biome_js_analyze/src/assist/source/organize_imports/import_key.rs` | assist specs | Determines statement ordering. |
| Formatter convergence | language formatter crates and `crates/biome_formatter_test/src/spec.rs` | language quick tests | Shared formatter test harness; this scout adds realistic project-wide second passes. |
| CSS parser options | `crates/biome_configuration/src/css.rs`, `crates/biome_service/src/file_handlers/css.rs` | CSS suites | Carries `tailwindDirectives` into parsing. |
| Prettier migration | `crates/biome_cli/src/execute/migrate.rs` | migrate command cases | Loads external formatter configuration and writes Biome configuration. |
| Language server | `crates/biome_lsp/src/handlers/analysis.rs`, `crates/biome_lsp/src/server.tests.rs` | LSP tests | Mapped for follow-on work; no realistic editor session was run. |

## Results overview

| Testbed | First format | Second pass | Safe-fix validation | Parser/config result | Disposition |
| --- | --- | --- | --- | --- | --- |
| Elatura | 86 tracked files changed; one JSON parse error | identical patch | type check passed; tests passed | malformed project JSON correctly rejected; parent config output consistent | negative parser result; compatibility pass |
| Scrapbook | 365 tracked files changed; Tailwind CSS parse errors | identical patch | type check passed; tests passed | default rejects `@apply`; `tailwindDirectives: true` succeeds; parent config output consistent | retain compatibility case |
| Renderprove | 80 tracked files changed | identical patch | broad suite became an unreliable oracle after rewrites | reduced safe assist reverses re-export evaluation; parent config output consistent | retain semantic caveat; no promotion |

## Observation 1: re-export sorting can change module evaluation order

### State

`retain as caveat; do not promote`

### Confidence

- Semantic mechanism: high. The behaviour reproduced in a small Node ESM project with no framework, bundler, or project configuration and follows ECMAScript module-request ordering.
- Product-defect conclusion: low. Follow-up review found the behaviour consistent with Biome's documented design direction and common organizer norms.

### Baseline

```js
export * from "./star.mjs";
export { named } from "./named.mjs";
```

Both target modules append a marker to `globalThis.order`. The consumer prints:

```text
1:2:star,named
```

### Biome action

```sh
npx -y @biomejs/biome@2.5.6 check index.mjs --write
```

Biome rewrites the file to:

```js
export { named } from "./named.mjs";
export * from "./star.mjs";
```

The consumer then prints:

```text
1:2:named,star
```

### Consequence

The exported values remain `1` and `2`, while module initialization order changes. JavaScript permits imported and re-exported modules to perform top-level work, so the observable effect is genuine.

The case is not unique to re-exports. Sorting ordinary binding imports can create the same class of change because imported modules also evaluate. Preserving every potentially meaningful dependency order would conflict with the central purpose of an import organizer unless the tool performed impractical whole-program effect analysis.

### Minimal reproduction

See `reproductions/export-reexport-order/`.

### Follow-up standards and ecosystem review

- ECMAScript records requested modules in source-text occurrence order and evaluates the dependency graph through that ordered list: https://tc39.es/ecma262/multipage/ecmascript-language-scripts-and-modules.html
- Biome's import-sorter RFC intentionally includes `export ... from` declarations and uses side-effect-only imports as sorting boundaries: https://redirect.github.com/biomejs/biome/discussions/3015
- An earlier Biome discussion describes preserving side-effect-import boundaries as important, showing the ordering tradeoff was considered rather than wholly overlooked: https://redirect.github.com/biomejs/biome/discussions/645
- Prettier core avoids import sorting because moving statements is a transformation with possible side effects: https://prettier.io/docs/rationale.html
- ESLint core's `sort-imports` fixer sorts members within one declaration but does not automatically reorder declaration lines: https://eslint.org/docs/latest/rules/sort-imports
- `eslint-plugin-import/order` reorders ordinary imports while refusing to move unbound side-effect imports: https://redirect.github.com/import-js/eslint-plugin-import/blob/main/docs/rules/order.md
- `eslint-plugin-simple-import-sort`, a design reference named by Biome's RFC, sorts re-exports while retaining the relative order of side-effect-only imports: https://redirect.github.com/lydell/eslint-plugin-simple-import-sort

### Product conclusion

This is a real semantic caveat of deterministic dependency sorting, not currently a strong Biome-specific correctness defect. The practical ecosystem convention is that ordinary imports and barrel re-exports should not secretly depend on sibling initialization order; explicit initialization belongs in deliberate side-effect imports or entry-point code.

No upstream report or source change is recommended without at least one stronger signal:

- realistic production breakage caused by the reorder;
- a Biome contract promising stronger semantic preservation than the implementation provides;
- a comparable declaration form that Biome uniquely reorders while peer tools protect it;
- a narrow, reliable detection rule that improves safety without effectively disabling organization.

A documentation clarification could be reasonable, but it does not presently clear Fieldwork's maintainer-burden threshold.

### Fork follow-up

A reproduction-only draft exists at https://redirect.github.com/teamleaderleo/biome/pull/1. It contains a pinned reproducer and proposed implementation notes, not a production source fix. The final recommendation is not to merge it as a fix or submit it upstream. It may be closed or retained temporarily as experimental evidence.

## Observation 2: project-wide formatter output converged

All three repositories produced byte-identical first- and second-pass patches:

- Elatura: 86 formatted tracked files;
- Scrapbook: 365 formatted tracked files;
- Renderprove: 80 formatted tracked files.

This is a negative result for unstable formatting at these revisions. It covers broad TS, TSX, ESM JS, JSON, CSS, manifests, and schemas accepted by Biome.

## Observation 3: Tailwind directives require explicit parser configuration

Scrapbook's `app/globals.css` contains five `@apply` directives. Default parsing emitted five diagnostics stating that Tailwind-specific syntax was disabled and recommending `tailwindDirectives`.

The same file formatted successfully with:

```json
{
  "css": {
    "parser": {
      "tailwindDirectives": true
    }
  }
}
```

This is expected, actionable configuration behaviour. It is consequential for migrations because a no-config project-wide run stops on valid Tailwind application CSS. See `reproductions/tailwind-directives/`.

## Observation 4: Prettier migration was blocked by project configuration

Scrapbook's `prettier.config.js` imports `@vercel/style-guide/prettier`, while the pinned package manifest does not declare `@vercel/style-guide`. After successful `biome init`, `biome migrate prettier --write` invoked Node to resolve the configuration and received `MODULE_NOT_FOUND`.

This does not support a Biome migration defect. It supports two narrower claims:

1. migration executes JavaScript Prettier configuration through Node;
2. unresolved configuration dependencies block migration with the underlying Node error preserved.

Repeat this trial on a repository whose existing Prettier command succeeds first.

## Observation 5: parent configuration discovery was consistent

A synthetic root `biome.json` set `formatter.lineWidth` to 40. The same nested JavaScript file was formatted from the root and from its own directory. Resulting contents matched in Scrapbook and Renderprove. Elatura's initial `divergent` marker came from comparing elapsed-time text; the formatted stdout content itself matched, so that marker is discarded.

This is a negative result for working-directory-dependent parent configuration discovery in the exercised single-root case.

## Observation 6: Elatura parser error was a project defect

`benchmarks/schema/benchmark-run-manifest-v2.schema.json` ends an `else` object with one closing brace missing before the final `allOf` array bracket. Biome reported `expected ',' but instead found ']'` and aborted formatting that file.

The source is malformed JSON. Biome's rejection is correct and sits inside the stop condition for application syntax correctly rejected by the tool.

## Observation 7: Renderprove's broad post-format failures remain unattributed

Renderprove's ordinary CI passed on both trial branch heads. Running the full suite after formatter-only, assist-only, no-assist, and default safe-fix rewrites produced the same three failures and two cancellations.

The scout reconstructed every complete changed JavaScript and TypeScript file from the formatter patch and compared TypeScript compiler AST traversals while ignoring trivia, quote choice, redundant parentheses, and trailing punctuation. All 61 complete JS/TS files preserved the examined AST content.

This evidence does not attribute the full-suite failures to a formatter semantic rewrite. Plausible project-side causes include tests that observe source bytes, timing changes, shared state, or incomplete cleanup. The ESM re-export reproduction is independent but no longer supplies a promotion candidate after ecosystem review.

## Fix-safety summary

- Elatura safe fixes preserved successful type checking and tests.
- Scrapbook safe fixes preserved successful type checking and tests.
- The `organizeImports` safe assist can change ESM module evaluation order in isolation.
- That effect belongs to the accepted risk model used by many declaration organizers rather than a demonstrated Biome-specific regression.
- Biome's `Safe` classification should be treated as a practical automation category, not a formal proof that every observable program behaviour is preserved.
- No unsafe-fix run was needed; the semantic change occurs under ordinary `check --write`.

## Parser summary

- Correct rejection: malformed Elatura JSON.
- Expected opt-in syntax: Scrapbook Tailwind `@apply` directives.
- No parser crash, hang, silent truncation, or accepted-invalid case observed.
- No minimized parser defect retained.

## Compatibility summary

### Positive

- Three repository trees completed broad Biome traversal.
- Repeated formatting converged.
- Parent configuration discovery was consistent in the corrected probe.
- Elatura and Scrapbook retained passing validation after safe fixes.
- Tailwind CSS formatted after the parser option was enabled.

### Friction and caveats

- Default formatting generates large policy churn in projects using other formatter defaults.
- Tailwind directives stop a no-config project-wide run.
- JavaScript Prettier migration depends on Node resolving imported configuration modules.
- Import/export organization can reach runtime evaluation order when modules rely on top-level effects.

## Performance observations

The workflows completed within their 20–25 minute caps. Formatter command time in retained logs was sub-second to low-second, while dependency installation and project tests dominated workflow duration. Runner load was uncontrolled and samples were not repeated, so this scout makes no comparative performance claim.

## Ranked follow-on candidates

### 1. New scout: realistic safe-fix runtime semantics

- Priority: high
- Question: which recommended or user-configured safe fixes directly change realistic runtime behaviour without relying on deliberately order-sensitive module architecture?
- Method: prioritize narrow syntax transformations with executable before/after assertions; search existing issues before retaining any candidate.
- Avoid duplication: known upstream examples already include named-function `.name` changes, decorator metadata affected by `useImportType`, and incorrect import-extension fixes.
- Exit: an unreported minimized case, realistic integration consequence, narrow source boundary, and plausible fix or applicability change.

### 2. Repeat: migration from a valid shared Prettier configuration

- Priority: medium
- Evidence: current trial blocked by the testbed's missing module
- Exit: mapped options, omitted plugins, diagnostics, and generated Biome configuration are recorded.

### 3. Realistic LSP and save-action convergence

- Priority: medium
- Question: do editor save actions, nested configuration, multiple workspaces, and concurrent formatting/fixing produce the same stable result as CLI execution?
- Exit: deterministic replay with captured request sequence, document versions, and final bytes, or a minimized divergence.

### 4. Repeat with a narrower oracle: Renderprove suite sensitivity

- Priority: medium-low
- Evidence: repeatable suite failures with equivalent examined JS/TS ASTs
- Exit: isolate a file rewrite, shared-state leak, source-byte dependency, or timing dependency.

### 5. Retain as compatibility example: Tailwind parser option

- Priority: low
- Evidence: direct default failure and configured success.

## Negative results

- No non-convergent second formatter pass across the three testbeds.
- No parser crash or silent data loss.
- No parent configuration divergence after comparing actual output files.
- Elatura's JSON error was valid input rejection.
- Scrapbook's migration failure originated in an undeclared project dependency.
- Renderprove's broad suite failures lack an examined formatter AST change and remain unattributed.
- Re-export ordering is not retained as a Biome product defect after standards and ecosystem review.
- No formal performance regression was measured.
- No realistic LSP session was exercised.

## Evidence inventory

| Testbed | Actions run | Artifact ID | Artifact digest |
| --- | --- | --- | --- |
| Elatura | `30467416414` | `8730145295` | `sha256:2d0ce7fee2ebf60f76fe0a27e79b3d3a5f5b3416b906ac9bf54032ad0bc35638` |
| Scrapbook | `30468280222` | `8730522904` | `sha256:367256e8636ab5b614c7888841856f3cacc41e9f8647cd55ee52dabdda1290cd` |
| Renderprove | `30467874688` | `8730351639` | `sha256:4e4ca9c3f7507a71042553aac8b51c827438a26b82edc0106c6b78e12a7eeb7a` |

Trial links:

- https://redirect.github.com/teamleaderleo/elatura/actions/runs/30467416414
- https://redirect.github.com/teamleaderleo/scrapbook/actions/runs/30468280222
- https://redirect.github.com/teamleaderleo/renderprove/actions/runs/30467874688

## Cleanup

- Destructive operations performed: none.
- Production systems touched: none.
- Secrets or private data retained: `no`.
- Testbed PR disposition: closed without merge after evidence capture.
- Trial workflow rollback: closing the pull request leaves the workflow only on the trial branch.
- Durable retained content: this report and minimized cases in Fieldwork.
- Fork draft disposition: reproduction-only; do not merge or submit as a fix under the current conclusion.

## Disposition

- Re-export evaluation-order case: `retain as semantic caveat and negative product conclusion; do not promote`.
- Tailwind compatibility case: `retain as an example`.
- Prettier migration: `repeat on a valid configuration`.
- Formatter instability hypothesis: `negative result for these testbeds`.
- Parser defect hypothesis: `negative result`.
- Best next Biome direction: `new safe-fix semantics scout or realistic LSP/save-action scout`.

## Upstream boundary

Upstream contact authorized: `no`

Interaction performed: `none`
