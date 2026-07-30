# Repository Map

Snapshot date: 2026-07-31

This map separates Fieldwork coordination, public owned testbeds, target working copies, and repositories that still need classification. It covers repositories visible through the connected GitHub account. Private repository names stay outside this public index.

For the research attached to each working copy, use [`RESEARCH_INVENTORY.md`](RESEARCH_INVENTORY.md). Deep Playwright, Vercel AI SDK, Gemini CLI, and Vite maps live in [`TARGET_PORTFOLIOS.md`](TARGET_PORTFOLIOS.md). A repository name alone does not identify the active branch, accepted claim, or current gate.

## Coordination repositories

- `teamleaderleo/fieldwork` — durable research, experiments, campaigns, receipts, review, delivery, and publication readiness.
- `teamleaderleo/linux-fieldwork` — Linux package, process, filesystem, service, privilege, container, VM, and kernel-facing investigations. Use its current handoff before acting; it contains many independently owned live and historical branches.

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

- `teamleaderleo/ai` — Vercel AI SDK scout and four promoted campaigns.
- `teamleaderleo/antigravity-cli`
- `teamleaderleo/antigravity-sdk-python`
- `teamleaderleo/codex` — tool, process, terminal, MCP, repository-state, and current-upstream work.
- `teamleaderleo/gemini-cli` — four current test-only candidate PRs plus a retired execution carrier.
- `teamleaderleo/opencode` — harness, PTY, process, and control-surface research.
- `teamleaderleo/t3code` — provider-event, persistence, interruption, recovery, and hot-reload research.
- `teamleaderleo/typescript-sdk` — MCP reconnect, timeout, cancellation, and session work.

### Web tooling, runtimes, and generated interfaces

- `teamleaderleo/biome` — safe-fix runtime audit and retained negative result.
- `teamleaderleo/deno` — failed global-install lifecycle characterization.
- `teamleaderleo/next.js`
- `teamleaderleo/playwright` — core fixture, result-accounting, and prototype work.
- `teamleaderleo/playwright-cli` — retained separate CLI video boundary.
- `teamleaderleo/playwright-mcp` — partial video-finalization receipt reproduction.
- `teamleaderleo/playwright-python` — async shutdown cancellation and retry ownership.
- `teamleaderleo/react`
- `teamleaderleo/vite` — direct HMR, invalidation, and graph candidates.
- `teamleaderleo/vite-plus`
- `teamleaderleo/wgpu` — browser/native portability and presentation-lifecycle characterization.
- `teamleaderleo/workerd` — generated interface and runtime work.
- `teamleaderleo/workers-sdk` — Workers SDK lifecycle work plus six Cloudflare Vite plugin candidates.

### Data, state, clients, and foundational libraries

- `teamleaderleo/duckdb` — local and remote publication, interruption, and ecosystem experiments.
- `teamleaderleo/execa` — completed signal-zero descendant-termination result and owned draft.
- `teamleaderleo/httpx` — response close, client shutdown, and HTTPCore ownership work.
- `teamleaderleo/node-lru-cache` — released background-fetch boundary candidate.
- `teamleaderleo/opentelemetry-js` — signal providers, shutdown, fanout, and delayed reentry.
- `teamleaderleo/supabase`
- `teamleaderleo/supabase-js`
- `teamleaderleo/tantivy` — accepted mixed-generation finding, production repair, and MSRV work.
- `teamleaderleo/uv` — extracted-wheel cache crash-consistency characterization.
- `teamleaderleo/zustand` — completed option preservation and active hydration settlement.

These repositories are working surfaces. Fieldwork issues, reports, and receipts remain the durable source of claim scope, execution identity, review state, and contact authority.

## Cross-target discovery rule

Search by code owner as well as user-facing target. Examples:

- Cloudflare Vite plugin work lives in `teamleaderleo/workers-sdk` and is labeled `target:workers-sdk`.
- Playwright research spans core, Python, MCP, and CLI working copies.
- Gemini research includes a cross-agent Gemini/Codex case pack.
- Vercel AI work is split into four campaign issues under one `teamleaderleo/ai` working copy.
- Execa, wgpu, Wasmtime, Deno, uv, DataFusion/Polars, and Tantivy began under broader programme lanes instead of stable target hubs.
- Linux package, archive, process, privilege, cache, and VM work lives in `teamleaderleo/linux-fieldwork` and must be read through its own handoffs.

Use `RESEARCH_INVENTORY.md` before declaring a target or topic complete.

## Other public repositories requiring classification

These repositories are visible under the account but lack a current entry in the public testbed registry or active research inventory. Classify each as an owned product, reusable testbed, retained experiment, tutorial or legacy project, upstream mirror, or archive before connecting it to Fieldwork:

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