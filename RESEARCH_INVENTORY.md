# Comprehensive Research Inventory

Snapshot date: 2026-07-31

This is the broad Fieldwork ledger. It covers mature target portfolios, standalone scouts, cross-target campaigns, owned-fork candidates, broad ecosystem rounds, ready but unstarted lanes, stopped work, and the separate Linux Fieldwork repository.

Use this file to answer **what work exists**. Use [`CURRENT.md`](CURRENT.md) to answer **what should finish next**, [`TARGET_PORTFOLIOS.md`](TARGET_PORTFOLIOS.md) for deep target-specific maps, [`REPOSITORIES.md`](REPOSITORIES.md) for account-level repository classification, and live issues and pull requests for exact current state.

## State vocabulary

- **Durable result** — the research packet and its evidence are retained and reviewed. A separate production repair may still be open.
- **Active candidate** — source or test work exists and has an exact remaining gate.
- **Active research** — characterization, execution, or design selection is underway; no production fix is accepted.
- **Ready lane** — a bounded assignment exists but no completed report or executed candidate was found.
- **Stopped or reference-only** — useful evidence remains, but duplicate work, active upstream overlap, supersession, or a stop decision prevents current implementation.

A repository name or issue label does not determine maturity. Every entry below points to its canonical evidence owner.

## Deep target portfolios

The detailed maps for Playwright, Vercel AI SDK, Gemini CLI, and Vite live in [`TARGET_PORTFOLIOS.md`](TARGET_PORTFOLIOS.md). That file also records the Cloudflare Vite work hidden under Workers SDK labels.

Additional mapped target-hub portfolios appear below with their active scouts, campaigns, and retained results.

## Runtime, process, and foundational-library work

### Execa — durable result; owned draft retained

- Canonical issue: [#106](https://github.com/teamleaderleo/fieldwork/issues/106)
- Merged Fieldwork evidence: [PR #109](https://github.com/teamleaderleo/fieldwork/pull/109)
- Durable path: `programmes/agent-cli-execution/scouts/execa-descendant-termination/`
- Owned working copy: `teamleaderleo/execa`
- Owned implementation: `teamleaderleo/execa#1`

The completed matrix proved that Execa 10 descendant termination could route signal `0`, normally used as a liveness probe, through Windows forced tree termination. The narrow dispatcher repair was validated across supported operating systems and Node versions. The research is complete; the owned target PR remains a draft and no upstream contact is authorized.

### wgpu — active research; target execution still absent

- Canonical lane: [#116](https://github.com/teamleaderleo/fieldwork/issues/116)
- Fieldwork draft: [PR #126](https://github.com/teamleaderleo/fieldwork/pull/126)
- Durable path: `programmes/high-leverage-open-source/scouts/wgpu-portability-lifecycle/`
- Owned working copy: `teamleaderleo/wgpu`
- Owned characterization draft: `teamleaderleo/wgpu#1`

The source map covers browser surface configuration, partial mutation before rejection, native acquire/present ownership, and loss of backend-specific presentation status. Evidence is source-read and target-test-prepared. Browser and native GPU execution, platform matrices, and focused compilation remain required before promoting any defect or repair.

### Wasmtime — durable first-pass result

- Canonical lane: [#117](https://github.com/teamleaderleo/fieldwork/issues/117)
- Landed Fieldwork packet: [PR #166](https://github.com/teamleaderleo/fieldwork/pull/166)
- Durable path: `programmes/high-leverage-open-source/scouts/wasmtime-capability-interruption/`

The executed packet separates epoch interruption, cancellation of a suspended async host call after a host effect has already committed, and resource-limit denial versus trapping policy. This is an embedding receipt and reconciliation requirement, not a claimed Wasmtime defect. Further capability, component-model, and host-resource work remains separate.

### HTTPX and HTTPCore — active candidate family

- Async response close ownership: [issue #171](https://github.com/teamleaderleo/fieldwork/issues/171) / [PR #173](https://github.com/teamleaderleo/fieldwork/pull/173)
- Related sync response ownership: issue #185
- HTTPCore connection ownership: issue #227
- Client shutdown boundary: issue #177
- Owned working copy: `teamleaderleo/httpx`

The selected public custom-stream contract treats delegated cleanup failure as a shared terminal outcome and runs the arbitrary stream cleanup once. Source-only finalization, target execution, and adjacent client/connection classifications still control readiness.

### Deno global installation — active research

- Canonical issue: [#175](https://github.com/teamleaderleo/fieldwork/issues/175)
- Owned draft: `teamleaderleo/deno#1`

A failed fresh global npm lifecycle install can leave command-owned private state before public shim publication, changing retry behavior. The fresh-install cleanup invariant is accepted, but the target characterization needs an exact attempt counter, replacement controls, failure-position coverage, cleanup-error receipts, and target execution.

### uv extracted wheel cache — active research

- Canonical issue: [#176](https://github.com/teamleaderleo/fieldwork/issues/176)
- Owned draft: `teamleaderleo/uv#1`

The accepted mechanism is that rename gives namespace atomicity but does not prove extracted wheel data survived sudden power loss. The current design cannot use the extracted archive's mutable `RECORD` as its sole authority. A repaired reproducer and a decision among durable publication, independent validation, or a hybrid are still required.

### node-lru-cache — active candidate

- Canonical issue: #132
- Fieldwork candidate: PR #135
- Owned working copy: `teamleaderleo/node-lru-cache`

The released invalid `backgroundFetchSize` boundary and its owned candidate remain a distinct library portfolio. Exact target execution and current-head review own the disposition.

## Data, storage, publication, and state work

### DuckDB — mature multi-campaign portfolio

- Target hub: [#11](https://github.com/teamleaderleo/fieldwork/issues/11)
- Main scout: issue #28 / merged PR #52
- Local publication result: merged PR #56
- Remote publication campaign: issue #96 / open PR #99
- Active S3 interruption repair lane: [#103](https://github.com/teamleaderleo/fieldwork/issues/103)
- Ecosystem experiments: #223 Hive partition marker collision and #240 `ROWS FOLLOWING` offset overflow
- Owned working copy: `teamleaderleo/duckdb`

The retained work spans local file publication, remote multipart interruption, final-key visibility, rollback and cleanup ownership, and current ecosystem experiments. A cancelled S3 export has been shown capable of returning interruption after the requested object was published; the source repair and fail-closed native proof remain active.

### DataFusion and Polars — active research and execution carrier

- Canonical lane: [#122](https://github.com/teamleaderleo/fieldwork/issues/122)
- Fieldwork draft: [PR #219](https://github.com/teamleaderleo/fieldwork/pull/219)
- Durable path: `programmes/high-leverage-open-source/scouts/datafusion-polars-reproducible-analytics/`

The current question compares cancellation after Parquet output begins. The branch contains a real DataFusion multipart barrier and a real Polars local-final-path barrier with exact source pins. Exact engine runs, source-to-package binding, and current-head integrity were still pending at this snapshot.

### Tantivy — durable finding; production repair and MSRV work remain

- Base lane: [#120](https://github.com/teamleaderleo/fieldwork/issues/120)
- Accepted finding: issue #180 / merged PR #182
- Owned execution carrier: `teamleaderleo/tantivy#1`
- Separate MSRV candidate: issue #200

The executed finding proved a mixed writer generation can survive a failed `prepare_commit`: an old worker may publish after a replacement accepts new work. No corruption was observed. The production repair must join old workers, retain ownership handles, retire or rebuild the writer after failure, and preserve the initiating error.

### Jotai — durable finding plus two active repair surfaces

- Released finding: merged PR #228
- JSON storage key-isolation candidate: issue #235 / PR #236
- Removal-settlement repair: PR #242

Released cross-key object aliasing is reproduced and retained. One candidate scopes parsed identity by storage key; another handles removal settlement. Execution, dynamic-key cache retention, and exact-head review remain separate gates.

### Zustand — one completed closeout and one active lifecycle candidate

- Undefined-option preservation: completed PR #172 and owned merge
- Explicit hydration settlement: issue #158 / PR #159
- Owned working copy: `teamleaderleo/zustand`

The undefined-options result is durable. The hydration work still needs the finalized observer matrix, explicit terminal ownership, and ordinary repository gates.

### Supabase — active lifecycle portfolio

- Target hub: [#12](https://github.com/teamleaderleo/fieldwork/issues/12)
- Main scout: issue #21
- Refresh notification campaign: issue #148 / PR #91
- Owned working copies: `teamleaderleo/supabase`, `teamleaderleo/supabase-js`

Current evidence covers overlapping refresh generations. Same-token distinct-result ownership, invalidation, server-rendering execution, and clean candidate selection remain.

## SDK, protocol, web-tooling, and observability work

### OpenTelemetry JS — durable synthesis plus active provider composition

- Target hub: #4
- Scout: [#19](https://github.com/teamleaderleo/fieldwork/issues/19)
- Main packet: PR #32
- Signals worker: issue #194
- Delayed lifecycle reentry model: issue #216 / merged PR #221
- Owned working copy: `teamleaderleo/opentelemetry-js`

The portfolio covers trace, logs, metrics, provider shutdown, processor fanout, delayed same-owner reentry, and pre-existing work during shutdown. The reentry model is durable; provider composition and exact target matrices remain active.

### MCP TypeScript SDK and Stensibly — mature campaign with one unclaimed lane

- Target hub: #7
- Scout: issue #20
- Reconnect campaign: issue #65
- Concurrent-stream lane: issue #66, still ready and unclaimed
- Timeout/reconnect result: issue #67 / merged PR #90
- Stensibly version A/B trial: issue #68 / merged PR #104
- Campaign synthesis: PR #102
- Owned working copy: `teamleaderleo/typescript-sdk`
- Owned testbed: `teamleaderleo/stensibly`

The retained work distinguishes reconnect budget, request timeout, transport-owned resumed GET traffic, late results, replay behavior, duplicate delivery, duplicate execution, and durable idempotency. The concurrent per-stream state lane remains a separate unclaimed question.

### Workers SDK, Workerd, and Cloudflare Vite plugin — active multi-surface portfolio

- Workers SDK scout: issue #18 / PR #41
- Follow-up batch: `batches/B20260730-001-workers-sdk-lifecycle-followup/`
- Batch synthesis: PR #112
- Workerd receiver-aware generated types: issue #230 / PR #232
- Cloudflare Vite candidates: #165, #179, #183, #186, #187, and #190
- Owned working copies: `teamleaderleo/workers-sdk`, `teamleaderleo/workerd`

This portfolio includes Miniflare teardown, config selection, deployment-state reporting, generated type inheritance, Vite runtime ownership, container cleanup, build-scope state, authenticated remote sessions, registry authority, and Wrangler import-time proxy routing.

### Biome — durable negative result and active safe-fix audit

- Target hub: #6
- Broad scout negative result: merged PR #54
- Active safe-fix lane: issue #89
- Active Fieldwork packet: PR #97
- Candidate issues include #144, #145, #146, and #151
- Owned working copy: `teamleaderleo/biome`

The initial transform/fix-safety pass produced a useful negative result. The active lane tests rules labelled safe against executable JavaScript and TypeScript behavior and keeps distinct candidates separate.

### Vite and Playwright

See [`TARGET_PORTFOLIOS.md`](TARGET_PORTFOLIOS.md). Those targets have full maps because their work spans multiple owned working copies, reports, execution receipts, and cross-target packages.

## Agent, CLI, and control-surface work

### Codex — broad active campaign family

- Target hub: #8
- Main scout: issue #23 / PR #33
- Tool-surface campaign: PR #51 and its child issues
- Host and MCP lifecycle packet: PR #101
- Deferred discovery work: PR #77
- Current-upstream convergence: issue #239
- Owned working copy: `teamleaderleo/codex`

The work spans tool discovery, subprocess and terminal state, MCP lifecycle, timeout and cancellation receipts, repository-state persistence, compaction, and current-upstream drift. Proposal readiness is controlled by exact-name/count receipts, prerequisite ordering, source pins, and clean current-head branches.

### Gemini CLI and cross-agent process semantics

See [`TARGET_PORTFOLIOS.md`](TARGET_PORTFOLIOS.md). Cross-agent process and terminal work is retained in issue #24 / PR #50 and is reused by later control-surface scouts.

### OpenCode and T3 Code — active comparative research

- Harness/control-surface scout: PR #63
- Deeper implementation and event-lifecycle work: PR #75
- Related issue family: #71 and #234
- Owned working copies: `teamleaderleo/opencode`, `teamleaderleo/t3code`

These packets compare direct harnesses, PTY/process contracts, provider-event normalization, persistence, interruption, recovery, and hot reload. Divergent experimental branches are characterization surfaces, not accepted product fixes.

### Execa

Execa is indexed under runtime and process work above because its result is a standalone descendant-termination finding, even though its programme home is Agent and CLI execution.

## High-leverage lanes that have not yet produced completed research

Programme [#114](https://github.com/teamleaderleo/fieldwork/issues/114) originally dispatched a broad portfolio through historical PR #115. The dated ranking in that PR is reference-only; the individual issues below remain canonical.

- **Tauri authority, packaging, and lifecycle — issue #118:** ready, unclaimed.
- **Automerge/Yjs local-first identity and recovery — issue #121:** ready, unclaimed.
- **Godot web, automation, and authoritative-state boundaries — issue #123:** ready, unclaimed.
- **Bevy ECS, scheduling, assets, and replay — issue #124:** ready, unclaimed.
- **FFmpeg interruption, finalization, and media provenance — issue #125:** ready, unclaimed.

wgpu, Wasmtime, Tantivy, DataFusion/Polars, Deno, and uv started from the same programme and are classified in their active sections above.

## Open-source ecosystem discovery and experiments

### Programme and scouts

- Programme: [#207](https://github.com/teamleaderleo/fieldwork/issues/207)
- Package collections and build failures: #208
- Runtimes, standard libraries, and compilers: #209
- Developer tools, package managers, and build systems: #210
- Foundational libraries, databases, and Linux systems: #211
- Broad-spectrum round: merged PR #220
- Durable paths: `programmes/open-source-ecosystems/rounds/` and `programmes/open-source-ecosystems/scouts/`

The broad round is a dated intake snapshot. Before implementation, refresh current ownership, active upstream work, source revisions, and environment gates.

### Current experiments and dispositions

- **Ruff RUF038 — #222:** useful experiment record; implementation held when another contributor's intent became clear.
- **DuckDB Hive partition marker collision — #223:** claimed; native characterization active.
- **libarchive PPMd small-buffer boundary — #224:** stopped because an active equivalent upstream fix appeared.
- **CPython GenericAlias free-threaded snapshot — #229:** ready.
- **DuckDB `ROWS FOLLOWING` overflow — #240:** claimed; native characterization preparing.
- **Nixpkgs gomarkdoc test restoration — #241:** source analysis complete; Linux execution route remains.

The broad round also retained systemd-oomd, package-collection, compiler, standard-library, and supply-chain leads. A queue entry is not permission to contact upstream.

## Linux Fieldwork — separate execution repository

Repository: `teamleaderleo/linux-fieldwork`

Linux work is extensive enough to require its own handoff and programme maps. Do not reduce it to one Fieldwork queue card.

### Canonical current entry points

- Active mmdebstrap and cache-proxy handoff: `linux-fieldwork` PR #187
- mmdebstrap source-audit journal: PR #71
- Ecosystem contribution intake: merged PR #106
- First Linux ecosystem scan: merged PR #131

### Main Linux portfolios

#### mmdebstrap, autopkgtest, and package-test lifecycle

Active and retained work includes reusable autopkgtest tooling, exact failure ownership, hook-free capability scheduling, signal termination, QEMU image publication, gpgv wrapper status and signal handling, proxysolver status, mirror process ownership, subordinate-ID setup, and source-audit handoffs.

Current prominent carriers include PRs #72, #171, #172, #177, #180, #187, and #192. The historical `dev-ptmx`/`bsdutils` correction is durable through merged PR #89.

#### Rootless and chrootless package execution

- Core host-service and credential inheritance scout: PRs #21 and #22
- Chrootless environment hardening: merged PR #57
- Canonical maintainer-script path candidate: PR #109
- Evidence provenance and generated summary: PRs #115 and #129
- Upgrade failure and recovery matrix: PR #178

This work separates host configuration, maintainer-script authority, environment and socket inheritance, target containment, package state, and evidence provenance.

#### Cache proxy security and reliability

Durable merged results include atomic publication (#96), response framing (#120), declared-length validation (#137), and request-header separation (#139). Active work includes authority and path containment (#118), post-commit errors (#147), canonical composition (#162), origin-status validation (#169), and additional cleanup/ownership gates.

Each cache property remains independently owned. An individually green patch is not treated as a proven composed source state.

#### tarfilter and archive compatibility

Durable work covers byte-preserving no-op behavior, dotfile and parent matching, hard-link and PAX path rewriting, GNU transform replacement and scope semantics, sparse archive preservation, occurrence selectors, legacy regular-file encodings, ownership metadata, repeated slash components, negative stripping, regex dialects, expression lists, and replacement case conversion.

Most accepted slices are merged. The active regex-dialect repair is PR #151. Historical aggregate and stale-stack PRs are kept closed to preserve one canonical carrier per invariant.

#### Reproducibility, maintainer-script interruption, and ecosystem intake

- Maintainer-script interruption fixture: merged PR #18
- Debian package variance corpus: merged PR #112
- Linux ecosystem refresh and overlap work: PR #142
- Nixpkgs/systemd/libarchive routes are governed by current overlap and environment checks.

### Linux inventory rule

Use the latest Linux handoff before acting. Many older branches are deliberately closed diagnostics, superseded stacks, or historical evidence carriers. The public Fieldwork inventory records the portfolio and canonical entry points; exact Linux branch state remains in `teamleaderleo/linux-fieldwork`.

## Repositories and notes without an established active portfolio

[`REPOSITORIES.md`](REPOSITORIES.md) lists public working copies and unclassified repositories. Some working copies exist because of earlier comparisons, experiments, or retained mirrors but do not currently have a canonical active issue or durable report. Do not infer an active campaign from repository existence alone.

## Discovery checklist

Before declaring a target or topic fully inventoried, search:

1. target hub and target map;
2. programme issue and registry;
3. open and closed issues by target name, repository name, and mechanism;
4. open, merged, and closed Fieldwork pull requests;
5. scout, campaign, batch, context, research, and ledger paths;
6. owned working-copy pull requests and branches;
7. handoff and closeout issues;
8. related integration-package labels;
9. `teamleaderleo/linux-fieldwork` when package, process, filesystem, privilege, VM, or Linux execution is involved;
10. duplicate, stopped, superseded, and upstream-overlap records.

## Maintenance rule

Add every new substantial result or lane here when it becomes durable enough to rediscover. Preserve one canonical issue or PR for each invariant. Keep exact heads and live workflow results in the owning issue or pull request, not in this broad snapshot. Move stale carriers to stopped or superseded status without deleting their evidence history.