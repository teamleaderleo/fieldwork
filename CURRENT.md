# Current Fieldwork Publication Pass

Snapshot date: 2026-07-31

This page answers what can move toward publication or landing now. The comprehensive research ledger lives in [`RESEARCH_INVENTORY.md`](RESEARCH_INVENTORY.md), deep multi-repository target maps live in [`TARGET_PORTFOLIOS.md`](TARGET_PORTFOLIOS.md), and the account-level repository inventory lives in [`REPOSITORIES.md`](REPOSITORIES.md).

Live exact-head decisions remain in [issue #213](https://github.com/teamleaderleo/fieldwork/issues/213) and implementation, final gates, landing, and cleanup remain in the [Delivery Desk, issue #160](https://github.com/teamleaderleo/fieldwork/issues/160).

## Closest to landing

### 1. Playground validator primitive strictness — PR #238 / issue #237

Current source-and-test head: `bc3a40a18890d0a0faa90630748618a15c8c99d1`.

The branch validates pack defaults and case overrides independently, handles huge integers through the promised error boundary, distinguishes JSON booleans from numbers, and contains no temporary repair carrier.

Exact-head Playground/context run `30566396493` and Fieldwork integrity run `30566396740` passed. The remaining transition is human signoff on the reviewed four-file source, test, and permanent workflow-hook diff.

### 2. Receipt boolean schema-version repair — PR #231

Current source-only head: `b7d64f2318c9799ebb229eaaeae275f17e0f60c5`.

The durable change is limited to the receipt classifier and focused tests. The temporary execution workflow is absent from the current diff; Effective surface receipts run `30561575792` and Fieldwork integrity run `30561575896` passed. The remaining transition is human signoff.

### 3. Workerd receiver-aware generated types — PR #232 / issue #230

The lexical-heritage collision repair is retained, while the current complete-diff review found a generic full-replacement defect: a nongeneric replacement can inherit a generated receiver such as `this: Owner<T>` without declaring `T`. Repair the exact owned workerd head, add the three-case generic/nongeneric replacement matrix, then execute generator, repository, lint, coverage, and complete-diff gates. Fork-only workflow material must disappear before proposal preparation.

### 4. OpenTelemetry provider shutdown and delayed reentry — issue #194

The provider candidate, delayed-reentry stack, and pre-existing-span experiment form one lifecycle question. The provider matrix, linear restack, attempt-all processor fanout, and pre-existing-span completion rule remain.

## Major active portfolios

These portfolios contain substantial notes and candidate work even when none currently occupies the first four finish slots.

### Playwright

The complete portfolio is indexed under [`TARGET_PORTFOLIOS.md#playwright`](TARGET_PORTFOLIOS.md#playwright). It includes four executed findings, 25 files in Fieldwork PR #49, a durable handoff in issue #181, and active owned work across Playwright core, Python, and MCP.

Current decisions:

- fixture cleanup separation repair, issue #141;
- expected-failure cleanup accounting, issue #142;
- Python async stop ownership, issue #149;
- partial MCP video receipts, issue #153.

### Vercel AI SDK

The complete portfolio is indexed under [`TARGET_PORTFOLIOS.md#vercel-ai-sdk`](TARGET_PORTFOLIOS.md#vercel-ai-sdk). Scout PR #34 contains nine retained files and promotes four independent campaigns:

- explicit-abort terminal settlement, issue #76;
- truncated stream outcome classification, issue #94;
- resumable Stop run identity, issue #95;
- idle UI stream keep-alive, issue #150.

### Gemini CLI

The complete portfolio is indexed under [`TARGET_PORTFOLIOS.md#gemini-cli`](TARGET_PORTFOLIOS.md#gemini-cli). Scout PR #45 contains eight retained files, PR #50 contains the cross-agent case pack, and four test-only owned candidate PRs cover subprocess abort, approval affinity, waiting-state cleanup, and asynchronous kill ownership.

### Vite

The complete portfolio is indexed under [`TARGET_PORTFOLIOS.md#vite`](TARGET_PORTFOLIOS.md#vite). It has two distinct bodies of work:

1. the direct Vite scout in PR #48 with three candidates around `watchChange`, post-transform graph accuracy, and bundled-development `hotUpdate`;
2. six Cloudflare Vite plugin candidates under Workers SDK issue #88 and batch `B20260730-001-workers-sdk-lifecycle-followup`.

The second group is labeled `target:workers-sdk`, so a Vite-only label search misses it.

### High-leverage runtime and data work

The complete set is indexed in [`RESEARCH_INVENTORY.md`](RESEARCH_INVENTORY.md). Current movement includes:

- HTTPX delegated close terminal outcomes — issue #171 / PR #173;
- wgpu browser/native lifecycle characterization — issue #116 / PR #126;
- DataFusion/Polars publication cancellation — issue #122 / PR #219;
- Tantivy production repair after the accepted mixed-generation finding — issue #180;
- Deno failed-install cleanup characterization — issue #175;
- uv extracted-wheel crash consistency — issue #176.

### Linux Fieldwork

Linux package, process, filesystem, privilege, archive, cache, and VM work is maintained in `teamleaderleo/linux-fieldwork`. The landed historical handoff is [Linux Fieldwork PR #187](https://github.com/teamleaderleo/linux-fieldwork/pull/187); the live last-mile receipt and routing surface is [Linux Fieldwork issue #194](https://github.com/teamleaderleo/linux-fieldwork/issues/194).

Current composition state includes merged QEMU lifecycle PR #195, canonical open gpgv lifecycle PR #196, hosted-green LF-02 PR #197 and LF-23 PR #199, and the green nine-file caching-proxy composition PR #198. Focused predecessors remain evidence records and do not replace those composed carriers.

## Other implementation underway

- Zustand hydration-source and observer settlement — issue #158 / PR #159.
- Jotai JSON storage key isolation and removal settlement — issue #235 / PRs #236 and #242.
- Supabase refresh notification ownership — issue #148 / PR #91.
- Codex current-upstream convergence and proposal readiness — issue #239.
- MCP reconnect and session synthesis — campaign #65 / PR #102.
- Biome safe-fix runtime audit — issue #89 / PR #97.

## Durable research packets in good condition

- broad-spectrum ecosystem round 001 and ranked candidate queue;
- Execa signal-zero descendant-termination result;
- Wasmtime interruption and host-effect ownership;
- Tantivy mixed-generation `prepare_commit` finding;
- OpenTelemetry delayed lifecycle reentry model;
- Jotai released cross-key identity reproduction;
- Zustand undefined-option preservation closeout;
- Codex MCP timeout outcome model;
- Playwright four-finding lifecycle packet;
- Vercel AI four-campaign scout packet;
- Gemini deterministic tool and session lifecycle packet;
- Vite direct scout and Workers SDK follow-up synthesis;
- Linux Fieldwork tarfilter, cache-publication, package-test, and maintainer-script results recorded in their canonical repository.

## Work requiring more passes

- wgpu browser/native execution and platform coverage;
- Tantivy production repair candidate;
- Gemini exact-call modification snapshot and adjacent state-manager fixtures;
- Vite/Workers SDK mocked package and generated-request executions;
- Deno and uv target-native characterizations;
- DataFusion/Polars locked source-to-package execution;
- Linux privileged and VM gates in `teamleaderleo/linux-fieldwork`;
- ready but unclaimed Tauri, Automerge/Yjs, Godot, Bevy, and FFmpeg lanes;
- editorial conversion of durable research into publishable articles or podcast episodes.

## Editorial and podcast inventory

The indexed repositories contain no dedicated podcast draft, transcript, episode outline, or audio-production packet. The strongest source packets are now visible in [`RESEARCH_INVENTORY.md`](RESEARCH_INVENTORY.md). Any editorial lane should name one packet, one listener-facing thesis, the exact confirmed behavior, and the proposed repair boundary.

## Maintenance rule

Keep this page focused on current movement. Preserve the broad research map in `RESEARCH_INVENTORY.md`, deep target detail in `TARGET_PORTFOLIOS.md`, exact evidence in canonical reports and receipts, and live decision text in issues and pull requests.
