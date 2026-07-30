# Broad-Spectrum Ecosystem Round — 2026-07-30

## In simple words

This round surveyed live contribution queues across package collections, runtimes, developer tools, foundational libraries, databases, and Linux user space. It retained the places where useful work repeatedly appears, reduced several current issues to likely owning code and tests, and separated open work from candidates already covered by active pull requests, assignments, or contributor claim intent.

## Source boundary

Research was performed on 2026-07-30 against public GitHub issue, pull-request, assignment, comment, and source views. Exact issue and source revisions are recorded in the scout reports. This is reconnaissance and local planning only; no upstream contact was authorized or made.

Promotion state is perishable. A live review refresh found that libarchive #3337 gained PR #3340 after the original scan, and a later refresh found a contributor publicly asking to take Ruff #27026. The round retains those cases as references and stops independent implementation unless coordination reopens them. Every candidate must be rechecked immediately before a branch is created.

## First result

The portfolio can sustain broad parallel discovery. The highest-yield surfaces share three properties:

1. issues include a deterministic reproducer or pinned working and failing revisions;
2. the likely owning code and adjacent test suite are compact;
3. overlap checks cover active pull requests, linked work, assignees, contributor intent, and project-specific claim bots.

## Best immediate current-CI candidates

1. **DuckDB #24308 — partitioned COPY can lose data.** SQL NULL and the literal string `__HIVE_DEFAULT_PARTITION__` map to the same directory. The issue remains open, reproduced, unassigned, without comments or a matching pull request in the review refresh.
2. **Nixpkgs #516481 — restore `gomarkdoc` tests.** The package currently disables `checkPhase`. The failure is pinned to a nixpkgs revision window and points toward `buildGoModule`, `GOFLAGS`, working-directory behavior, or an upstream test assumption. No active claim or matching pull request was found.
3. **DuckDB #24307 — large FOLLOWING frames return non-empty results.** The pure SQL reproducer remains open, reproduced, unassigned, without comments or a matching pull request in the review refresh.
4. **DuckDB #24314 — high-precision median error.** The issue offers a compact analytical boundary behind the first two database probes.
5. **Ruff #27022 and #27024 — automatic fixes change string or buffer behavior.** Both carry compact before/after fixtures, but overlap must be refreshed before selection.

## Coordination/reference candidates

**Ruff #27026 — RUF038 runtime mutation and dropped `Literal` members** remains a high-value diagnosis, but it is no longer an independent first implementation. The issue discussion separates two concerns:

- whether all `Literal[...]` rewrites should remain unsafe because annotations are runtime-visible through introspection;
- the narrower correctness bug where an unsupported member such as `values[0]` is dropped.

A contributor has publicly asked to work on the issue. Retain the fixtures and split diagnosis, but coordinate before opening a branch.

Rust #159745, #159686, #159492, #157184, and #157260 are already assigned or claimed. They remain valuable diagnostic and contribution-packet references, while independent implementation is stopped unless their claims are released or coordination explicitly invites help.

libarchive #3337 now has active PR #3340 with the same small-buffer reproducer and a focused PPMd input-accounting fix. It remains useful as a parser-refill and regression-fixture reference, but it is removed from the implementation queue.

## Environment-gated candidates

- **systemd #43174:** `systemd-oomd` silently drops a continuously running `user@<uid>.service` after a user-manager reload. Route through a VM and `TEST-55-OOMD.sh`.
- **CPython #154916:** free-threaded `GenericAlias` iterator data race between `next()` and `__reduce__()`. Route through a free-threaded ThreadSanitizer build and keep the regression test small enough for maintainer review.
- **Nixpkgs #485220:** AAVMF regression with pinned good and bad nixpkgs revisions. Requires aarch64 QEMU or equivalent VM capacity.
- **libarchive #3283:** Windows signed-shift undefined behavior. Requires a Windows CLANG64 UBSan environment.

## Duplicate-work stops retained as examples

Several attractive issues already had focused fixes in flight:

- libarchive #3337 → PR #3340;
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

Promote DuckDB #24308, Nixpkgs #516481, and DuckDB #24307 into the first independent executable probes. Keep Ruff #27026 as a coordination/reference packet until the contributor intent is resolved. Keep one VM lane and one free-threaded/TSAN lane ready behind them. Retain libarchive #3337 as an active-fix reference. Run pull-request, linked-work, assignee, contributor-intent, and claim-comment checks immediately before code work begins.
