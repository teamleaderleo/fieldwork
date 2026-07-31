# Codex dependency and boundary map

Date: 2026-07-31  
Evidence class: `source-read` and `issue-read`  
Public source pin: `openai/codex@ef293f7ac9d756f793f3e952a790f9bec16a6eeb`  
Prior pin carried by this finding: `4642370542739d5dd080b0c87a9de06a6435d3db`  
Upstream interaction: read-only; no comment, review, reaction, submission, or other contact

## Purpose

This note maps Codex package boundaries, current public ownership signals, and issue clusters that can support bounded follow-up investigations. It does not classify a package as defective merely because it is large, native, pinned, or externally maintained.

The governing test remains: each lifecycle boundary must prove the fact it owns. SDK completion cannot prove runtime persistence. Tool advertisement cannot prove executable authority. A valid rollout cannot prove that the SQLite projection contains it. A successful credential refresh cannot prove that every loaded runtime adopted the replacement.

## Public-head movement

The public source moved eight commits from `464237054...` to `ef293f7ac...`. The delta touches MCP, core tool planning and registration, skills, app-server protocol exports, and related tests.

This expires present-tense claims for older MCP and tool-authority source carriers until they are compared or restacked. It does not erase their historical execution receipts.

Two public commits are direct first-party precedent for the convergence thesis:

1. `ef293f7ac9d756f793f3e952a790f9bec16a6eeb` restricts the legacy unnamespaced `shell_command` to exactly one local environment, reserves the name from external claims, and uses namespaced external tools for remote or multi-environment cases.
2. `164b3bfeabdbc8e33c7320437e7cd875f93a534e` scopes MCP OAuth credentials by environment and prevents an executor-owned MCP server from consuming same-name host credentials.

These changes make environment identity part of executable authority rather than presentation metadata.

## Package and runtime map

### Rust workspace

`codex-rs/Cargo.toml` defines a Rust 2024 workspace with more than one hundred internal crates. Major ownership areas include:

- app-server, protocol, client, and transport;
- core, core-api, plugins, and skills;
- unified execution, shell execution, process management, and sandboxes;
- Code Mode and Responses API handling;
- MCP client, server, and `rmcp` integration;
- rollout, thread-store, state, history, and persistence;
- extension providers and environment routing;
- CLI and TUI surfaces;
- telemetry, cloud tasks, memories, tools, and shared utilities.

Important external dependency families include:

- async and network: Tokio, Futures, Axum, Reqwest, Tungstenite, and Tonic;
- persistence: SQLx 0.9, bundled SQLite, and `libsqlite3-sys 0.37` pinned for the referenced WAL-reset corruption fix;
- protocols and runtimes: `rmcp = 3.0.0` and `v8 = 150.4.0` exact pins;
- terminal UI: Ratatui and Crossterm;
- security and sandboxing: Landlock, seccompiler, Rustls, aws-lc, keyring, age, crypto_box, ed25519, and clatter;
- parsing and retrieval: tree-sitter, Starlark, and bm25;
- telemetry: OpenTelemetry, Sentry, and tracing;
- Git-pinned components: nucleo and runfiles.

The exact V8, RMCP, SQLite/native, and Git-pinned dependencies are compatibility and reproducibility boundaries. A later audit should inspect update ownership, generated/native artifact provenance, and target-platform coverage. This note makes no vulnerability claim.

### Node workspace

The root private package requires Node 22 and pnpm 10.33. The pnpm workspace includes the native CLI wrapper, Responses API proxy wrapper, and TypeScript SDK.

The workspace applies a seven-day minimum release age, blocks exotic subdependencies, prevents dependency downgrades, and allows no dependency build scripts by default. This is a deliberate supply-chain policy boundary rather than a general package preference.

The TypeScript SDK is a wrapper around the Codex runtime. Its tests can establish wrapper contracts, spawn behavior, and TypeScript API semantics. They cannot independently establish Rust runtime authority, persistence, settlement, or replay.

### Python SDK and runtime wheel

The Python SDK supports Python 3.10+ and depends on Pydantic 2.12+. It pins the runtime wheel exactly as `openai-codex-cli-bin==0.144.4`.

That exact pin is a compatibility contract between Python API behavior and the shipped native runtime. SDK release success alone cannot prove that the runtime binary, generated protocol, and source revision all carry the same lifecycle behavior.

## Boundary-oriented investigation lanes

### Lane A — Environment-scoped tool and credential authority

Question: do advertisement, credential lookup, runtime selection, and dispatch all use the same captured environment identity?

Current first-party direction:

- legacy `shell_command` is available only when one local environment owns it;
- externally supplied shell tools are namespaced;
- executor-owned MCP credentials are separated from host credentials;
- ordinary active calls should retain their prepared binding while explicit refresh replaces later calls.

Candidate controls:

1. a tool advertised from environment A cannot dispatch to environment B after catalogue refresh;
2. host and executor MCP servers with the same name and URL retain separate credentials;
3. CLI login and app-server runtime reconciliation expose the same environment-qualified server identity;
4. a replacement generation actually serves the next call;
5. cancellation between reconnect intent and publication cannot leave a latent replacement armed;
6. model-specific publication tests establish callable-authority equality, not catalogue presence alone.

Existing reconnect source PR `teamleaderleo/codex#101` retains the historical exact `4/4` reconnect receipt. Its old base overlaps the new public MCP delta, so current delivery classification requires a new compare/restack. Two remaining controls are specifically replacement-call service and cancellation atomicity.

### Lane B — Rollout and SQLite reconciliation

Question: when rollout JSONL is valid but the SQLite state/index is absent, stale, partial, or large, which representation owns recovery and how is reconciliation acknowledged?

Public issue cluster reviewed:

- `openai/codex#31433`: valid rollout files absent from the state database and no supported reindex path;
- `openai/codex#26990`: power loss can lose pin/project/config coherence while conversations largely survive;
- `openai/codex#30236`: TRACE data persisted to SQLite despite a higher configured log level, producing large WAL and disk writes;
- `openai/codex#24510`: large active-thread metadata/history can drive high CPU and large database/rollout state.

This lane is distinct from F83 append acknowledgement. Append acknowledgement asks whether a specific durable write was accepted. Reconciliation asks how readers recover when two durable representations disagree or one projection is absent.

Candidate controls:

1. rebuild an absent index from valid rollouts without inventing entries;
2. rerun reconciliation idempotently;
3. preserve deterministic identity when a partial database row and complete rollout describe the same thread;
4. reject or quarantine malformed/truncated rollouts without dropping valid neighbors;
5. survive interruption between canonical append and projection publication;
6. bound scan, memory, and write amplification for large histories;
7. distinguish diagnostic-log retention from conversation-state retention;
8. report recovered, skipped, ambiguous, and failed records separately.

No current Fieldwork issue was found by the targeted search for Codex rollout/SQLite reconciliation. F239 should own source reading until one bounded implementation or proposal packet exists; then a new technical owner issue is appropriate.

### Lane C — SDK/runtime/version coherence

Question: which generated protocol, wrapper package, native binary, and Rust source revision jointly define one released behavior?

Candidate controls:

1. exact Python runtime wheel version matches the source/protocol behavior claimed by the SDK release;
2. TypeScript protocol types and app-server exports correspond to the runtime used by tests;
3. wrapper cancellation/timeout language does not imply remote-effect settlement without runtime evidence;
4. SDK resume/fork tests distinguish API success from rollout and SQLite recovery;
5. native target matrix proves the same boundary behavior across supported platforms.

This lane begins as a release-coherence audit. It should remain separate from product source changes until a concrete mismatch is reproduced.

### Lane D — Dependency and native-runtime provenance

Question: can exact pins, Git dependencies, generated bindings, and native libraries be reproduced and updated with a clear owner and platform matrix?

Initial focus:

- exact V8 and RMCP pins;
- bundled SQLite and `libsqlite3-sys` compatibility;
- Git-pinned nucleo and runfiles revisions;
- native sandbox/security dependencies across Linux, macOS, and Windows;
- generated app-server protocol exports consumed by wrappers.

Candidate outputs are a dependency-owner ledger, update test matrix, and reproducibility receipt. Security findings require concrete affected versions and behavior; package presence alone is insufficient.

## Active-carrier classification at this pin

| Carrier | Historical fact retained | Current limitation |
| --- | --- | --- |
| terminal source `teamleaderleo/codex#93@7f15307...` | nine candidate-specific terminal controls previously passed on reconstructed/current-at-the-time source | base is `464237054...`; compare/restack required at `ef293f7ac...` |
| terminal execution carrier `#94@f3d34f3...` | exact source fence and candidate controls reached the broader package gate | broad package run hit an unrelated stack-exhaustion condition; raised-stack rerun remains |
| reconnect source `#101@df954cf...` | exact-one reconnect, failed-reload preservation, and quiescence have an exact `4/4` receipt | public MCP delta overlaps its old base; replacement-call and cancellation controls remain |
| F239 carrier `teamleaderleo/fieldwork#292@7c9a64b...` | canonical synthesis through the prior public pin | this note changes its head and requires renewed integrity and complete-diff review |

Execution carriers remain disposable evidence producers and are never merge candidates.

## Selected follow-up order

1. Compare and restack the terminal and reconnect source fences onto `ef293f7ac...` when overlap permits.
2. Re-run the terminal broad package gate under the already observed raised-stack condition; preserve the ordinary-stack failure as diagnostic evidence.
3. Add reconnect controls for replacement-call service and cancellation atomicity.
4. Read current rollout/thread-store/state source and produce a reconciliation state-owner map before implementing recovery.
5. Produce an SDK/runtime version-coherence table tied to exact release artifacts and protocol exports.
6. Produce a dependency-owner ledger for exact, Git-pinned, generated, and native dependencies.

## Limits

- This is a source and issue map, not a product-behavior execution receipt.
- Public issues describe reports and hypotheses; they do not prove root cause.
- The public source can move again and expire currentness claims.
- No merge, deployment, credentials, or public upstream interaction occurred while producing this note.
