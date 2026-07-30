# Broad-Spectrum Ecosystem Round — 2026-07-30

## In simple words

This round surveyed live contribution queues across package collections, runtimes, developer tools, foundational libraries, databases, and Linux user space. It retained the places where useful work repeatedly appears, reduced several current issues to likely owning code and tests, and separated open work from candidates already covered by active pull requests or contributor claims.

## Source boundary

Research was performed on 2026-07-30 against public GitHub issue, pull-request, assignment, comment, and source views. Exact issue and source revisions are recorded in the scout reports. This is reconnaissance and local planning only; no upstream contact was authorized or made.

## First result

The portfolio can sustain broad parallel discovery. The highest-yield surfaces share three properties:

1. issues include a deterministic reproducer or pinned working and failing revisions;
2. the likely owning code and adjacent test suite are compact;
3. overlap checks cover active pull requests, linked work, assignees, and project-specific claim bots.

## Best immediate current-CI candidates

1. **Ruff #27026 — RUF038 changes runtime expressions and drops `Literal` members.** The rule claims annotation scope but receives a general expression and can replace an entire runtime `Literal` expression. The owning rule file is compact and the issue includes a playground reproducer.
2. **DuckDB #24308 — partitioned COPY can lose data.** SQL NULL and the literal string `__HIVE_DEFAULT_PARTITION__` map to the same directory. The writer and adjacent test file are identified, and the reproducer is a small SQL fixture.
3. **Nixpkgs #516481 — restore `gomarkdoc` tests.** The package currently disables `checkPhase`. The failure is pinned to a nixpkgs revision window and points toward `buildGoModule`, `GOFLAGS`, working-directory behavior, or an upstream test assumption.
4. **DuckDB #24307 and #24314 — window-frame and high-precision median errors.** Both are pure SQL reproducers with no matching pull request found.
5. **Ruff #27022 and #27024 — automatic fixes change string or buffer behavior.** Both carry compact before/after fixtures and clear fix-safety consequences.
6. **libarchive #3337 — PPMd decompression depends on caller read-buffer size.** This offers a compact archive fixture and current-CI parser/refill investigation.

## Claimed reference candidates

Rust #159745, #159686, #159492, #157184, and #157260 are already assigned or claimed. They remain valuable diagnostic and contribution-packet references, while independent implementation is stopped unless their claims are released or coordination explicitly invites help.

## Environment-gated candidates

- **systemd #43174:** `systemd-oomd` silently drops a continuously running `user@<uid>.service` after a user-manager reload. Route through a VM and `TEST-55-OOMD.sh`.
- **CPython #154916:** free-threaded `GenericAlias` iterator data race between `next()` and `__reduce__()`. Route through a free-threaded ThreadSanitizer build and keep the regression test small enough for maintainer review.
- **Nixpkgs #485220:** AAVMF regression with pinned good and bad nixpkgs revisions. Requires aarch64 QEMU or equivalent VM capacity.
- **libarchive #3283:** Windows signed-shift undefined behavior. Requires a Windows CLANG64 UBSan environment.

## Duplicate-work stops retained as examples

Several attractive issues already had focused fixes in flight:

- Nixpkgs #540900 → PR #540913;
- Nixpkgs #541367 → PR #541990;
- CPython #154842 → PR #154843;
- CPython #154859 → PR #154862;
- CPython #154863 → PR #154899;
- CPython #154874 → PRs #154875 and #154887;
- CPython #154791 → PR #154798;
- libarchive #3310 → PR #3334;
- pip #14177 → PR #14178.

These remain useful as contribution-packet examples, test-design references, and downstream patch-retirement signals. They are removed from the implementation queue.

## Retained files

- [`CANDIDATE_QUEUE.md`](CANDIDATE_QUEUE.md) — ranked live queue and dispositions;
- [`SEARCH_PLAYBOOK.md`](SEARCH_PLAYBOOK.md) — recurring searches and overlap checks;
- [`../../scouts/package-collections/ROUND-001.md`](../../scouts/package-collections/ROUND-001.md) — package-collection report;
- [`../../scouts/runtimes-standard-libraries/ROUND-001.md`](../../scouts/runtimes-standard-libraries/ROUND-001.md) — runtime and standard-library report;
- [`../../scouts/developer-tools-build-systems/ROUND-001.md`](../../scouts/developer-tools-build-systems/ROUND-001.md) — developer-tool report;
- [`../../scouts/foundational-systems/ROUND-001.md`](../../scouts/foundational-systems/ROUND-001.md) — libraries, databases, and Linux systems report.

## Current decision

Promote Ruff #27026, DuckDB #24308, Nixpkgs #516481, and libarchive #3337 into executable probes first. Keep one VM lane and one free-threaded/TSAN lane ready behind them. Treat claimed Rust diagnostics as references and continue searching for unassigned compiler work. Run pull-request, linked-work, assignee, and claim-comment checks before code work begins.