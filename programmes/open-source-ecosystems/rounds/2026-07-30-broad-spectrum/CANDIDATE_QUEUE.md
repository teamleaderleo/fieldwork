# Candidate Queue — Broad-Spectrum Round 001

Snapshot: 2026-07-30. Rankings combine consequence, reproducibility, owning-boundary clarity, environment cost, review size, and overlap with active work.

| Rank | Target | Candidate | Consequence | Environment | Overlap | Next probe | Disposition |
|---:|---|---|---|---|---|---|---|
| 1 | Ruff | [#27026](https://github.com/astral-sh/ruff/issues/27026) — RUF038 changes runtime expressions and drops members | runtime behavior and evaluation can change under an automatic fix | current CI | no matching fix PR found; stabilization PR #26919 is exposed to the bug | add runtime-context and mixed-member fixtures; trace invocation from expression analysis | promote |
| 2 | DuckDB | [#24308](https://github.com/duckdb/duckdb/issues/24308) — partitioned COPY can lose data | two distinct partition values collide on disk | current CI | no matching PR found | add reserved-token collision case to `parquet_hive_null.test`; inspect reversible path encoding | promote |
| 3 | Rust | [#159745](https://github.com/rust-lang/rust/issues/159745) — nested turbofish diagnostic | parser gives a terse error and misses an actionable correction | current CI | no matching PR found | run UI test, locate comparison-versus-generic parse recovery, add expected suggestion | promote |
| 4 | Nixpkgs | [#516481](https://github.com/NixOS/nixpkgs/issues/516481) — `gomarkdoc` test regression | package ships with its tests disabled | current CI | no matching PR found | re-enable checks in an override, isolate `GOFLAGS` and working-directory effects, bisect build hooks | promote through Linux Fieldwork LF-35 |
| 5 | Rust | [#159686](https://github.com/rust-lang/rust/issues/159686) — missing match arm receives irrelevant suggestions | misleading compiler guidance | current CI | no matching PR found | add UI case and identify comma-in-pattern recovery owner | promote |
| 6 | DuckDB | [#24307](https://github.com/duckdb/duckdb/issues/24307) — huge FOLLOWING frame returns rows | incorrect SQL result | current CI | no matching PR found | reduce numeric boundary and add window-frame regression test | promote after #24308 |
| 7 | DuckDB | [#24314](https://github.com/duckdb/duckdb/issues/24314) — DECIMAL(38,0) median error | incorrect analytical result | current CI | no matching PR found | compare integer interpolation paths and add two-value precision fixture | promote after #24308 |
| 8 | Ruff | [#27022](https://github.com/astral-sh/ruff/issues/27022) — B006 preview fix alters multiline string contents | automatic fix changes runtime value | current CI | issue blocks an active patch stack | preserve literal source value in fixture and identify indentation rewrite owner | promote or coordinate |
| 9 | Ruff | [#27024](https://github.com/astral-sh/ruff/issues/27024) — RUF055 safe fix changes buffer-protocol behavior | a safe fix changes accepted inputs | current CI | no matching PR found in sampled search | compare pre/post execution for bytes regex and buffer objects; reassess fix safety | promote |
| 10 | systemd | [#43174](https://github.com/systemd/systemd/issues/43174) — oomd loses user service monitoring after reload | silent loss of a memory-pressure guardrail | VM | no matching PR found | capture ManagedOOM notifications around user reload; add `TEST-55-OOMD.sh` scenario | promote through Linux Fieldwork, VM queue |
| 11 | CPython | [#154916](https://github.com/python/cpython/issues/154916) — `GenericAlias` iterator reduce race | free-threaded data race | free-threaded TSAN | no matching PR found; follows merged #154108 | design atomic read/strong-reference path; use a bounded test accepted by maintainers | issue-first or focused patch |
| 12 | libarchive | [#3337](https://github.com/libarchive/libarchive/issues/3337) — PPMd fails with small read buffers | valid archive decode depends on caller buffer size | current CI | no matching PR checked in round | retain minimal 7z fixture; vary read chunk size; trace PPMd refill boundary | promote |
| 13 | CPython | [#151464](https://github.com/python/cpython/issues/151464) — tokenizer emits `<>` outside grammar | token stream and parser language disagree | current CI | related syntax-suggestion PR exists, exact issue uncovered | specify token behavior with and without `barry_as_FLUFL`; add tokenizer regression | retain |
| 14 | systemd | [#43205](https://github.com/systemd/systemd/issues/43205) — discarded RA cancels router solicitation | network discovery can stop after an unusable advertisement | network namespace/VM | no overlap checked | build namespace fixture with lifetime-zero RA and observe RS schedule | retain behind VM lane |
| 15 | Nixpkgs | [#485220](https://github.com/NixOS/nixpkgs/issues/485220) — AAVMF regression | aarch64 firmware no longer reaches boot flow | aarch64 QEMU/VM | no matching PR found | automate good/bad firmware boot signature and bisect OVMF inputs | capability queue |
| 16 | Ruff | [#27028](https://github.com/astral-sh/ruff/issues/27028) — EXE001 treats nested `#!` comment as shebang | false positive on ordinary source comments | current CI | no matching PR checked | enforce file-start/interpreter semantics in fixture | retain |
| 17 | pip | [#13984](https://github.com/pypa/pip/issues/13984) — hash requirement bypass for build dependencies | integrity policy has an undocumented boundary | current CI with local index | security discussion already occurred; maintainer direction needed | build fully local sdist/index fixture and map policy options | issue-first |
| 18 | libarchive | [#3283](https://github.com/libarchive/libarchive/issues/3283) — signed left-shift UB on Windows | public helper reaches undefined behavior | Windows CLANG64 UBSan | no overlap checked | add high-bit test and define size/inode overflow policy | capability queue |
| 19 | Homebrew Core | [#139929](https://github.com/Homebrew/homebrew-core/issues/139929) — unsolved formula updates | recurring build and test failures block package updates | macOS/Linux CI varies | tracker intentionally invites help | select leaves with reproducible logs and no active PR | recurring intake |
| 20 | Homebrew Core | [#278366](https://github.com/Homebrew/homebrew-core/issues/278366) — OpenSSL 4 migration | broad compatibility migration across dependents | macOS/Linux CI | coordinated tracker | take leaf formulae by dependent count and build system | batch source |

## Removed from active implementation

| Target | Issue | Existing work | Retained value |
|---|---|---|---|
| Nixpkgs | #540900 | PR #540913 | pattern for converting a silently disabled feature into a hard build contract |
| Nixpkgs | #541367 | PR #541990 | platform-transition diagnosis and focused packaging workaround |
| CPython | #154842 | PR #154843 | guard mutable archive operations against live readers |
| CPython | #154859 | PR #154862 | persistent state for incremental codecs |
| CPython | #154863 | PR #154899 | distinguish iconv flush counts from substitution failures |
| CPython | #154874 | PRs #154875/#154887 | signed-versus-unsigned terminal attribute handling and portable pseudo-terminal tests |
| CPython | #154791 | PR #154798 | compare C and pure-Python implementations to find lifecycle drift |
| libarchive | #3310 | PR #3334 | pairing validation before consuming an ambiguous metadata-looking entry |
| pip | #14177 | PR #14178 | type-consistent comparison restoring an unreachable output branch |

## Active implementation limit

Keep at most three newly implemented candidates awaiting first review. The preferred first three are Ruff #27026, DuckDB #24308, and Rust #159745. Nixpkgs #516481 can run as an independent diagnosis because it begins with a package override and test restoration rather than an upstream code branch.