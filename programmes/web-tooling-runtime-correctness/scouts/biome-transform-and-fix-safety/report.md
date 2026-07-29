# Biome transform and fix safety scout

## In simple words

Biome 2.5.6 produced stable second-pass formatting across three realistic owned repositories, and its ordinary parser diagnostics were actionable. One safe assist crossed a semantic boundary: the recommended `organizeImports` action reordered two re-exports and reversed JavaScript module evaluation order. A minimized Node reproduction changes observable output from `star,named` to `named,star` after `biome check --write`.

The three project trials also found an expected Tailwind CSS configuration requirement, one correctly rejected malformed JSON file, consistent parent-directory configuration discovery, and a Prettier migration blocked by an undeclared dependency in the project’s own Prettier configuration. No upstream contact occurred.

**Current answer:** retain the re-export reproduction as a regression candidate and promote it to a focused finding or campaign. Keep the Tailwind and migration observations as compatibility evidence. Treat the Renderprove full-suite failures as an unresolved project-test sensitivity because AST comparison found no JavaScript or TypeScript AST change from formatter-only output.

## Identity

- Fieldwork issue: #27
- Programme: #15, Web tooling runtime correctness
- Target hub: #6, Biome
- Worker: `chatgpt:gpt-5.6-thinking`
- Claim date: 2026-07-29
- Owned path: `programmes/web-tooling-runtime-correctness/scouts/biome-transform-and-fix-safety/`
- Scout branch: `scout/27-biome-transform-fix-safety`
- Upstream contact authorized: `no`
- Upstream interaction performed: `none`

## Scout question

Which Biome parser, formatter, safe-fix, configuration, migration, and project-compatibility boundaries produce consequential behaviour on realistic JavaScript and TypeScript code?

## Scope supported

This scout supports mechanism and owned-project integration claims for:

- JavaScript, TypeScript, TSX, JSON, and CSS parsing and formatting;
- repeated formatter output;
- `check --write` safe fixes and assists;
- nested working-directory configuration discovery;
- Tailwind-specific CSS parser configuration;
- Prettier configuration migration startup;
- post-change type checks and tests where the project suite remained a valid oracle.

The scout does not support a language-server correctness claim, a formal performance comparison, browser-editor integration, Windows behaviour, or every Biome language.

## Revisions

### Target

- Package: `@biomejs/biome@2.5.6`
- Source revision matching package version 2.5.6: `biomejs/biome@d890b39c3ef21040bded453d9af91e1b301a0d67`
- Source reference: https://redirect.github.com/biomejs/biome/commit/d890b39c3ef21040bded453d9af91e1b301a0d67

### Fieldwork

- Protocol revision read at claim time: `teamleaderleo/fieldwork@09fe47ac92ec9c0c333b4979011f6321795deff2`
- Scout branch base after intervening documentation cleanups: `teamleaderleo/fieldwork@976b436d4d7e2741dee5505b6715839db9bd4e15`

### Testbeds

| Testbed | Content revision | Trial branch head | Actions merge revision | Trial PR |
| --- | --- | --- | --- | --- |
| Elatura | `bbea414c6e400ba748d053caedb777ecee1cc381` | `af8c853b12524765443cf8328b2624998550972e` | `61a01db0bd7b201f87c8905aae75604b6705bd99` | https://redirect.github.com/teamleaderleo/elatura/pull/57 |
| Scrapbook | `ea708e027d63bd4235ccbcd358e81efcd41a560b` | `b79c04f0e8877400da21f78cbf2074ed7b02b5cc` | `9cd8105c95ed453724560db6ca46be36c393df0d` | https://redirect.github.com/teamleaderleo/scrapbook/pull/492 |
| Renderprove | `3e954bdbf37b71dc06db6dd5a0b46bf2f296eb29` | `889785fdb681118c3adcc90e9cd87ec8b346b005` | `1e203d75443e47d18a02e45d1a0329b8f1ff72c2` | https://redirect.github.com/teamleaderleo/renderprove/pull/36 |

The Actions merge revisions contain only the pinned testbed content plus the reversible trial workflow.

## Why these testbeds

### Elatura

A TypeScript workspace and browser-sidecar project with package workspaces, JSON schemas, Vitest, type checking, build commands, and security checks. It exercises TS/JSON parsing, workspace traversal, generated-schema-like content, and safe fixes across package boundaries.

### Scrapbook

A large Next.js and React application with TSX, CSS, Tailwind directives, pnpm, Prettier, `prettier-plugin-tailwindcss`, Vitest, Playwright, and a broad application tree. It exercises TSX, CSS parser options, project-wide traversal, migration startup, and compatibility with an existing formatter setup.

### Renderprove

A pure ESM JavaScript package with MCP commands, browser automation code, JSON schemas, Node’s test runner, and many re-export/import surfaces. It exercises ESM evaluation, formatter output, assist behaviour, schemas, CLIs, and project tests that observe repository content.

## Method

Each trial used a dedicated `fieldwork/biome/issue-27` branch and a draft pull request. The workflow carried read-only repository permissions, synthetic public environment values where required, no production credentials, and an explicit close-without-merge disposition.

The common sequence was:

1. install the pinned project dependencies;
2. record Biome 2.5.6;
3. run `biome check .` with bounded diagnostics;
4. reset the tree;
5. run `biome format . --write` and retain the patch;
6. run the same formatter command again and compare complete patches byte-for-byte;
7. reset the tree;
8. run `biome check . --write` and retain the safe-fix patch;
9. run the project’s type check or validation and tests;
10. exercise nested configuration discovery with the same file invoked from the repository root and a nested working directory;
11. add targeted probes for Tailwind directives, Prettier migration, assist isolation, and re-export evaluation.

Retained Actions artifacts recorded status files, command output, file lists, patches, test output, and digests. The artifacts expire; the minimized cases in this directory are durable.

## Code and test map

Target source revision: `d890b39c3ef21040bded453d9af91e1b301a0d67`.

| Area | Primary code | Relevant tests or harness | Why it is relevant |
| --- | --- | --- | --- |
| Package identity | `packages/@biomejs/biome/package.json` | package release process | Pins version 2.5.6 and supported package entry points. |
| `check` orchestration | `crates/biome_cli/src/commands/check.rs` | `crates/biome_cli/tests/commands/check.rs` | `check` requests format, lint, and assist features; `--write` selects safe fixes unless unsafe mode is requested. |
| Import/export organization | `crates/biome_js_analyze/src/assist/source/organize_imports.rs` | assist specs and CLI override cases | The action handles imports and exports, is recommended, and declares `FixKind::Safe`. |
| Import/export sort keys | `crates/biome_js_analyze/src/assist/source/organize_imports/import_key.rs` | assist specs | Determines source and statement ordering used by the action. |
| Formatter convergence | language formatter crates plus `crates/biome_formatter_test/src/spec.rs` | language quick tests | The shared formatter harness checks output and convergence; the scout adds project-wide second-pass checks. |
| CSS parser options | `crates/biome_configuration/src/css.rs` and `crates/biome_service/src/file_handlers/css.rs` | CSS parser/formatter suites | Carries `tailwindDirectives` from configuration to parsing. |
| Configuration merge | `crates/biome_cli/src/commands/check.rs` and CLI traversal/configuration code | CLI configuration cases | Merges discovered file configuration with command-line feature flags and parser options. |
| Prettier migration | `crates/biome_cli/src/execute/migrate.rs` | migrate command snapshots/cases | Loads external formatter configuration and writes Biome configuration. |
| Language server | `crates/biome_lsp/src/handlers/analysis.rs`, `crates/biome_lsp/src/server.tests.rs` | LSP server tests | Mapped for follow-on work; no realistic editor session was run here. |

### Mechanism behind the strongest finding

The `organizeImports` source documentation says it sorts imports and exports. The rule declaration marks the action `recommended: true` and `fix_kind: FixKind::Safe`. Its module query includes both `JsImport` and `JsExport` items. The reduced case shows that sorting export-from declarations can reorder evaluation of their source modules.

JavaScript modules evaluate requested modules according to the module dependency graph and source traversal. Reordering export-from declarations can therefore alter observable side effects even when exported bindings and final values stay the same.

## Results overview

| Testbed | First format | Second pass | Safe fix validation | Parser/config result | Disposition |
| --- | --- | --- | --- | --- | --- |
| Elatura | 86 tracked files changed; one JSON parse error | identical patch | type check passed; tests passed | malformed project JSON correctly rejected; nested config consistent | negative parser result; compatibility pass |
| Scrapbook | 365 tracked files changed; Tailwind CSS parse errors | identical patch | type check passed; tests passed | default rejects `@apply`; `tailwindDirectives: true` succeeds; nested config consistent | retain compatibility repro |
| Renderprove | 80 tracked files changed | identical patch | full-suite oracle became unreliable after any broad rewrite | reduced safe assist reverses re-export evaluation; nested config consistent | promote semantic finding |

## Finding 1: safe re-export sorting changes module evaluation

### State

`promote`

### Confidence

High. The behaviour reproduced in a six-file isolated Node ESM project with no project framework, build system, or test runner dependency.

### Baseline

`index.mjs`:

```js
export * from "./star.mjs";
export { named } from "./named.mjs";
```

Both target modules append a marker to `globalThis.order`. Importing bindings through `index.mjs` prints:

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

The same consumer then prints:

```text
1:2:named,star
```

### Consequence

The exported values remain `1` and `2`, while module initialization order changes. Real modules can register handlers, initialize globals, install polyfills, mutate shared registries, or require one dependency’s initialization to precede another. The action’s `Safe` classification therefore exceeds the demonstrated semantic boundary.

### Minimal reproduction

See `reproductions/export-reexport-order/`.

### Candidate improvement

Preserve relative order across export-from declarations unless the implementation proves the involved declarations commute. A narrower initial rule could sort named specifiers inside one export declaration while retaining declaration order. Another option is to classify declaration reordering as unsafe while preserving safe specifier sorting and duplicate merging.

### Regression-test candidate

Add a case where two export-from targets have observable top-level effects and assert that applying the safe action preserves their source order. Cover at least:

- `export * from` followed by `export { ... } from`;
- the reverse order;
- two named export-from declarations;
- exports separated by comments;
- an export group mixed with imports.

## Observation 2: project-wide formatter output converged

All three realistic repositories produced byte-identical first- and second-pass patches:

- Elatura: 86 formatted tracked files;
- Scrapbook: 365 formatted tracked files;
- Renderprove: 80 formatted tracked files.

This is a negative result for unstable formatting at these revisions. It covers broad TS, TSX, ESM JS, JSON, CSS, package manifests, schemas, and workflow-adjacent text accepted by Biome. It does not prove convergence for every language or option set.

## Observation 3: Tailwind directives require explicit parser configuration

Scrapbook’s `app/globals.css` contains five `@apply` directives. Default Biome parsing emitted five direct diagnostics:

```text
Tailwind-specific syntax is disabled.
Enable `tailwindDirectives` in the css parser options.
```

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

This is expected, actionable configuration behaviour. It is consequential for migrations because a no-config project-wide run stops on otherwise valid Tailwind application CSS. The durable compatibility case is in `reproductions/tailwind-directives/`.

### Candidate follow-on

Measure whether `biome migrate prettier` or onboarding guidance detects `prettier-plugin-tailwindcss` and offers the parser option. This scout could not reach that migration path because Scrapbook’s current Prettier configuration imports an undeclared module.

## Observation 4: Prettier migration was blocked by project configuration

Scrapbook’s `prettier.config.js` starts with:

```js
const styleguide = require('@vercel/style-guide/prettier');
```

The package manifest at the pinned revision does not declare `@vercel/style-guide`. After a successful `biome init`, `biome migrate prettier --write` invoked Node to resolve the configuration and received `MODULE_NOT_FOUND` for that package.

This result does not support a Biome migration defect. It supports two narrower claims:

1. migration executes the project’s JavaScript Prettier configuration through Node;
2. an unresolved shared configuration dependency blocks migration with the underlying Node error preserved.

A follow-on migration trial should use a project whose existing Prettier command succeeds first, then compare migrated settings and plugin-related omissions.

## Observation 5: nested configuration discovery was consistent

A synthetic root `biome.json` set `formatter.lineWidth` to 40. The same nested JavaScript file was formatted once from the root and once from its own directory. The resulting file contents matched in Scrapbook and Renderprove after correcting the initial probe to compare files instead of timing-bearing stdout. Elatura’s captured stdout also showed the same formatted contents; its initial `divergent` marker came from elapsed-time text and is discarded.

This is a negative result for working-directory-dependent parent configuration discovery in the exercised single-root case.

## Observation 6: Elatura parser error was a project defect

Elatura’s `benchmarks/schema/benchmark-run-manifest-v2.schema.json` ends an `else` object with one closing brace missing before the final `allOf` array bracket. Biome reported `expected ',' but instead found ']'` at the closing bracket and aborted formatting that file.

The source is malformed JSON. Biome’s rejection is correct and the diagnostic points at the first token that cannot complete the object. This sits inside the scout stop condition for application syntax correctly rejected by the tool.

## Observation 7: Renderprove’s broad post-format tests are an unresolved compatibility signal

Renderprove’s ordinary CI passed on both trial branch heads. Running the full suite immediately after formatting or broad rewriting produced the same three failures and two cancellations across formatter-only, assist-only, no-assist, and default safe-fix variants.

The failures involved policy defaults, an MCP process identifier assertion, and pending interaction promises. To test whether formatter output changed JavaScript meaning, the scout reconstructed every complete changed JavaScript and TypeScript file from the formatter patch and compared TypeScript compiler ASTs while ignoring trivia, quote choice, redundant parentheses, and trailing punctuation. All 61 complete JS/TS files had equivalent semantic AST traversals.

This evidence does not attribute the full-suite failures to a formatter semantic rewrite. Plausible project-side causes include tests that observe source bytes, timing changes from rewritten files, shared state, or incomplete cleanup. The safe re-export reproduction is independent and remains valid.

### Follow-on

A project campaign could bisect the Renderprove suite with source-only, test-only, and fixture-only formatting, then isolate any timing or self-observation dependency. That work belongs to Renderprove test reliability unless a second minimal Biome transformation changes runtime behaviour.

## Fix-safety summary

### Supported

- Elatura safe fixes preserved successful type checking and tests.
- Scrapbook safe fixes preserved successful type checking and tests.
- The `organizeImports` safe assist can change ESM module evaluation order in isolation.

### Limited

- Renderprove’s full suite became an unreliable broad oracle after project-wide rewrites. The reduced ESM case supplies the direct safety evidence.
- No unsafe-fix run was needed for the strongest finding; the change occurs under ordinary `check --write`.

## Parser summary

- Correct rejection: malformed Elatura JSON schema.
- Expected opt-in syntax: Scrapbook Tailwind `@apply` directives.
- No parser crash, hang, silent truncation, or accepted-invalid case observed.
- No minimized parser defect retained.

## Compatibility summary

### Positive

- Three repository trees completed broad Biome traversal.
- Repeated formatting converged.
- Parent configuration discovery was consistent in the corrected probe.
- Elatura and Scrapbook retained passing project validation after safe fixes.
- Tailwind CSS formatted after the documented parser option was enabled.

### Friction

- Default formatting generates large policy churn in projects using other formatter defaults.
- Tailwind directives stop a no-config project-wide run.
- JavaScript Prettier migration depends on Node resolving the project configuration and its imported modules.
- Safe export organization reaches runtime evaluation order.

## Performance and resource observations

The workflows completed within their 20–25 minute caps, and Biome’s formatter passes themselves completed in sub-second to low-second command time in the retained logs. Dependency installation and project tests dominated total workflow time. This scout did not control runner load or collect repeated timing samples, so it makes no comparative performance claim.

## Ranked branch candidates

### 1. Promote: re-export evaluation order under safe organizeImports

- Priority: highest
- Evidence: direct runtime change plus minimized reproduction
- Suggested vehicle: focused finding, then a campaign if more export forms reproduce
- Exit criterion: safe application preserves evaluation order, or declaration reordering is reclassified outside safe fixes

### 2. Repeat: migration from a valid shared Prettier configuration

- Priority: medium
- Evidence: current trial blocked by the testbed’s missing module
- Suggested vehicle: narrow integration trial on an owned repository whose Prettier command passes
- Exit criterion: mapped options, omitted plugins, diagnostics, and resulting Biome configuration are recorded

### 3. Repeat only with a narrower oracle: Renderprove post-format suite sensitivity

- Priority: medium-low
- Evidence: repeatable suite failures with equivalent JS/TS ASTs
- Suggested vehicle: owned-project test reliability probe
- Exit criterion: isolate a file transformation, shared-state leak, source-byte dependency, or timing dependency

### 4. Retain as compatibility example: Tailwind parser option

- Priority: low
- Evidence: direct default failure and configured success
- Suggested vehicle: documentation/onboarding example inside Fieldwork
- Exit criterion: none required unless migration auto-detection is studied

## Regressions and negative results

- No non-convergent second formatter pass across the three testbeds.
- No parser crash or silent data loss.
- No nested-root configuration divergence after comparing actual output files.
- Elatura’s JSON error was valid input rejection.
- Scrapbook’s migration failure originated in an undeclared project dependency.
- Renderprove’s broad suite failures lack a formatter AST change and remain unattributed.
- No formal performance regression was measured.
- No realistic LSP session was exercised.

## What the scout preserves

- exact package and repository revisions;
- isolated testbed branches;
- command status and diagnostic logs;
- artifact IDs and SHA-256 digests;
- minimized, runnable compatibility and semantic cases;
- explicit boundaries between observed behaviour and inference;
- reversible cleanup through closing the unmerged trial pull requests.

## What the scout omits

- editor/LSP interaction with a real workspace;
- Windows and macOS runs;
- HTML, GraphQL, Vue, Svelte, and Astro project trials;
- formal benchmark repetitions;
- unsafe fixes;
- upstream issue search and upstream contact;
- migration output from a fully valid shared Prettier configuration.

## Evidence inventory

| Testbed | Actions run | Artifact ID | Artifact digest |
| --- | --- | --- | --- |
| Elatura | `30467416414` | `8730145295` | `sha256:2d0ce7f2375a60f8c6378c71f8a4296c26ba060cdb610e88c81496f0f7e2104c` |
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
- Testbed PR disposition: close without merge after evidence capture.
- Trial workflow rollback: close the pull request; the workflow exists only on the trial branch.
- Durable retained content: this report and minimized cases in Fieldwork.

## Disposition

- Strongest finding: `promote to a finding`.
- Tailwind compatibility case: `retain as an example`.
- Prettier migration: `repeat on a valid configuration`.
- Formatter instability hypothesis: `negative result for these testbeds`.
- Parser defect hypothesis: `negative result`.

## Upstream boundary

Upstream contact authorized: `no`

Interaction performed: `none`
