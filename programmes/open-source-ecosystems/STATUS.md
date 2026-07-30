# Open-Source Ecosystems and Upstream Contribution Campaigns

## In simple words

Find consequential work across package collections, runtimes, tools, libraries, databases, and Linux systems; prove each candidate locally; then carry the strongest fixes upstream with tests and a compact evidence packet.

- Programme hub: #207
- State: `investigating`
- Coordinator: `teamleaderleo`
- Upstream contact: unauthorized by default

## Current direction

Run a wide discovery portfolio while keeping implementation and review bounded.

1. Start with package collections because one contribution surface exposes many upstream projects and build systems.
2. Run runtime, standard-library, diagnostic, and developer-tool scouts in parallel.
3. Promote foundational-library and database candidates when a reduced input or deterministic fixture exists.
4. Route Linux package, process, filesystem, service, privilege, container, and kernel-facing work through `linux-fieldwork`.
5. Keep security-sensitive, compiler-backend, hardware-specific, and kernel work behind stronger reproduction and environment gates.

## Retained rounds

- [`2026-07-30 broad-spectrum round`](rounds/2026-07-30-broad-spectrum/README.md) — live issue scan, ranked queue, code-level deep dives, active-PR and claim-state stops, environment gates, and recurring search playbook.

Current first probes from that round:

1. Ruff #27026 — constrain RUF038 to valid annotation contexts and preserve unsupported members;
2. DuckDB #24308 — distinguish SQL NULL from the literal Hive default-partition marker;
3. Nixpkgs #516481 — restore `gomarkdoc` package tests through Linux Fieldwork;
4. systemd #43174 — VM trace of oomd registration loss;
5. CPython #154916 — free-threaded/TSAN design for a safe `GenericAlias` iterator snapshot.

libarchive #3337 is retained as a parser-state and regression-design reference after active PR #3340 appeared. Independent implementation is stopped.

Rust diagnostics #159745, #159686, #159492, #157184, and #157260 are retained as claimed references. Independent implementation is stopped while their assignments remain active.

## Execution waves

### Wave A — broad high-yield surfaces

- Nixpkgs, Homebrew Core, Debian, Fedora, and Arch packaging;
- CPython and unassigned Rust diagnostics or regression coverage;
- Ruff, Clippy, pytest, Meson, and package-manager correctness;
- reproducibility and downstream-patch retirement.

### Wave B — depended-on boundaries

- HTTP, URL, archive, compression, Unicode, date/time, path, and configuration libraries;
- database engines and client drivers;
- cancellation, cleanup, cache, lockfile, and compatibility behavior.

### Wave C — systems work

- systemd, util-linux, Podman, BuildKit, containerd, Mesa, and selected compiler or kernel-facing tools;
- VM, privileged, architecture, filesystem, and kernel-matrix investigations.

## Portfolio rules

- Candidate inventory may grow large.
- Scouts return ranked branches, reproducible evidence, negative results, and a recommendation.
- Experiments answer one distinguishing question.
- Implementation begins after a reproduction, failing test, deterministic difference, or clearly bounded missing capability exists.
- Keep at most three new implementation branches awaiting first review at once.
- Each promoted contribution has one canonical branch, one owner, an exact source revision, and explicit remaining gates.
- Park stale work with the blocker, preserved evidence, and the condition that would reopen it.
- Treat assignees, claim-bot comments, coordinated subdirectory claims, linked work, and matching pull requests as ownership signals.
- Recheck overlap immediately before branch creation; a dated scan does not reserve a candidate.

## First outputs

- [`SCOUT_MATRIX.md`](SCOUT_MATRIX.md) — initial portfolio and promotion gates;
- [`rounds/2026-07-30-broad-spectrum/CANDIDATE_QUEUE.md`](rounds/2026-07-30-broad-spectrum/CANDIDATE_QUEUE.md) — first ranked live queue;
- [`rounds/2026-07-30-broad-spectrum/SEARCH_PLAYBOOK.md`](rounds/2026-07-30-broad-spectrum/SEARCH_PLAYBOOK.md) — recurring searches and overlap checks;
- runtime and developer-tool reduced reproducers;
- a reusable contribution packet template backed by actual submissions;
- a ledger of accepted, declined, superseded, and retained-negative-result work.

## Current decision

Begin executable probes for Ruff #27026, DuckDB #24308, and Nixpkgs #516481. Keep systemd #43174 and CPython #154916 as environment-gated deep lanes. Retain libarchive #3337 as an active-fix reference rather than creating a competing branch. Continue broad reconnaissance, requiring pull-request, linked-work, assignee, and claim-comment checks immediately before code changes.