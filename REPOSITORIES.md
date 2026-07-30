# Repository Map

Snapshot date: 2026-07-30

This map separates Fieldwork coordination, public owned testbeds, target working copies, and repositories that still need classification. It covers repositories visible through the connected GitHub account. Private repository names stay outside this public index.

## Coordination repositories

- `teamleaderleo/fieldwork` — durable research, experiments, campaigns, receipts, review, delivery, and publication readiness.
- `teamleaderleo/linux-fieldwork` — Linux package, process, filesystem, service, privilege, container, VM, and kernel-facing investigations.

## Registered public owned testbeds

These repositories already appear in `testbeds/registry.yml` and may host controlled integration trials after a concrete question is assigned:

- `teamleaderleo/stensibly`
- `teamleaderleo/elatura`
- `teamleaderleo/scrapbook`
- `teamleaderleo/proofwake`
- `teamleaderleo/renderprove`
- `teamleaderleo/smolrunner`
- `teamleaderleo/starsector-preflight`
- `teamleaderleo/bsc-compare`
- `teamleaderleo/fin-agent`
- `teamleaderleo/simple-email-filter`
- `teamleaderleo/api-for-bizarre-pose-estimator`
- `teamleaderleo/reddit-narrative-detection`
- `teamleaderleo/narrative-duckdb`
- `teamleaderleo/gh-tidy-branches`
- `teamleaderleo/terminal-kit`

A registry entry provides orientation. A real trial still needs an exact revision, branch, owner, question, rollback rule, and result packet.

## Fieldwork-linked target working copies

These public repositories correspond to active or retained Fieldwork targets, experiments, implementation candidates, or comparative research. Confirm the exact upstream base and canonical branch in the owning issue before changing code.

### Agents, SDKs, and execution

- `teamleaderleo/ai`
- `teamleaderleo/antigravity-cli`
- `teamleaderleo/antigravity-sdk-python`
- `teamleaderleo/codex`
- `teamleaderleo/gemini-cli`
- `teamleaderleo/opencode`
- `teamleaderleo/t3code`
- `teamleaderleo/typescript-sdk`

### Web tooling, runtimes, and generated interfaces

- `teamleaderleo/biome`
- `teamleaderleo/deno`
- `teamleaderleo/next.js`
- `teamleaderleo/playwright`
- `teamleaderleo/playwright-cli`
- `teamleaderleo/playwright-mcp`
- `teamleaderleo/playwright-python`
- `teamleaderleo/react`
- `teamleaderleo/vite`
- `teamleaderleo/vite-plus`
- `teamleaderleo/wgpu`
- `teamleaderleo/workerd`
- `teamleaderleo/workers-sdk`

### Data, state, clients, and foundational libraries

- `teamleaderleo/duckdb`
- `teamleaderleo/execa`
- `teamleaderleo/httpx`
- `teamleaderleo/node-lru-cache`
- `teamleaderleo/opentelemetry-js`
- `teamleaderleo/supabase`
- `teamleaderleo/supabase-js`
- `teamleaderleo/tantivy`
- `teamleaderleo/uv`
- `teamleaderleo/zustand`

These repositories are working surfaces. Fieldwork issues, reports, and receipts remain the durable source of claim scope, execution identity, review state, and contact authority.

## Other public repositories requiring classification

These repositories are visible under the account but lack a current entry in the public testbed registry or active target map. Classify each as an owned product, reusable testbed, retained experiment, tutorial/legacy project, upstream mirror, or archive before connecting it to Fieldwork:

- `teamleaderleo/Asteroids-with-one-invisible-asteroid`
- `teamleaderleo/Bank-management-application`
- `teamleaderleo/barebones-issue-management`
- `teamleaderleo/Bookmark-Carousel`
- `teamleaderleo/clean-slate-repo`
- `teamleaderleo/cleaner-slate`
- `teamleaderleo/code-depth-gradations`
- `teamleaderleo/crittericons`
- `teamleaderleo/docs`
- `teamleaderleo/emoji-mood-tracker-basic`
- `teamleaderleo/first-contributions`
- `teamleaderleo/fold-single-line-comments`
- `teamleaderleo/fullstack-practice`
- `teamleaderleo/git-inline`
- `teamleaderleo/github-pages-with-jekyll`
- `teamleaderleo/layer5`
- `teamleaderleo/lots-of-loads`
- `teamleaderleo/playground`
- `teamleaderleo/Pong-in-Java`
- `teamleaderleo/potato-quality-image-compressor`
- `teamleaderleo/r3f-first-try-cards-forked`
- `teamleaderleo/reddit-hidden-profile-filter`
- `teamleaderleo/restack-example`
- `teamleaderleo/starsector-font-picker`
- `teamleaderleo/TriOS`

## Classification checklist

For every repository added to an active Fieldwork lane, record:

1. repository role: coordination, target working copy, owned testbed, experiment, or archive;
2. canonical upstream or ownership source;
3. exact base revision and canonical branch;
4. owning Fieldwork issue, programme, or campaign;
5. active candidate and current head, when one exists;
6. evidence class and remaining execution gates;
7. whether public interaction is authorized;
8. retirement or cleanup condition.

## Coverage boundary

This public map intentionally omits private repository names. It also avoids declaring every similarly named repository a fork or mirror without verified parent metadata. The live issue and PR map decides which repositories are active; this file keeps the account-level inventory readable.
