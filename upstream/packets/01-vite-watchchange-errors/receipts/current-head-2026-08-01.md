# Current-head receipt — 2026-08-01

## Review fence

- Public Vite base: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Canonical owned source: `a2ab7ca6183ad74d64066d6706e57a546e355224`
- Canonical source branch: `fix/fieldwork-25-watchchange-error-isolation`
- Canonical source PR: [`teamleaderleo/vite#4`](https://github.com/teamleaderleo/vite/pull/4)
- Diff relation: two commits ahead, zero behind
- Diff inventory: exactly two files, 198 additions, 12 deletions

## Current-head source review

Durable review comment: [`teamleaderleo/vite#4` comment `5148481573`](https://github.com/teamleaderleo/vite/pull/4#issuecomment-5148481573)

Result:

- server-local environment fanout is the correct ownership boundary;
- `EnvironmentPluginContainer.watchChange` is async and awaits `hookParallel`, so synchronous hook throws and asynchronous hook rejections both reach the server as rejected environment promises;
- settle-all preserves successful ordering and allows every environment result to be reported;
- complete diff contains no temporary workflow or research artifact;
- no blocking product-code defect was found by source read.

## Current-head workflows

### Zizmor

- Run: [`30674314445`](https://github.com/teamleaderleo/vite/actions/runs/30674314445)
- Result: `success`

### CI

- Run: [`30674314447`](https://github.com/teamleaderleo/vite/actions/runs/30674314447)
- Changed-files job `91298285131`: `success`
- Lint job `91298285154`: `success`

The lint job completed:

- checkout;
- dependency installation;
- build;
- lint;
- formatting check;
- typecheck;
- documentation tests;
- workflow-file checks.

Build&Test jobs at receipt creation:

- Linux Node 20: queued
- Linux Node 22: queued
- Linux Node 24: queued
- Linux Node 26: queued
- macOS Node 24: queued
- Windows Node 24.15: queued

### Preview

- Run: [`30674314449`](https://github.com/teamleaderleo/vite/actions/runs/30674314449)
- Result: `skipped`
- Classification: expected internal-source PR behavior; no product claim

## Current disposition

`REPAIR`

The source, formatter, lint, typecheck, docs, build step, and Zizmor have current-head success receipts. The supported-platform Build&Test matrix and final receipt review remain open.

Any source-head movement expires this receipt. No public upstream interaction or merge is authorized.
