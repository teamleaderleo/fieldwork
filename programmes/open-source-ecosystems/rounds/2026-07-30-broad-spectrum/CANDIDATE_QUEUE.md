# Candidate Queue — Broad-Spectrum Round 001

Snapshot: 2026-07-30. Rankings combine consequence, reproducibility, owning-boundary clarity, environment cost, review size, active pull requests, assignees, and project-specific claim state.

| Rank | Target | Candidate | Consequence | Environment | Overlap | Next probe | Disposition |
|---:|---|---|---|---|---|---|---|
| 1 | Ruff | [RUF038 runtime/fix issue](https://redirect.github.com/astral-sh/ruff/issues/27026) | runtime behavior and evaluation can change under an automatic fix | current CI | no matching fix PR found; stabilization PR 26919 is exposed to the bug | add runtime-context and mixed-member fixtures; trace invocation from expression analysis | promote |
| 2 | DuckDB | [partitioned COPY data-loss issue](https://redirect.github.com/duckdb/duckdb/issues/24308) | two distinct partition values collide on disk | current CI | no matching PR found | add reserved-token collision case to `parquet_hive_null.test`; inspect reversible path encoding | promote |
| 3 | Nixpkgs | [`gomarkdoc` test-regression issue](https://redirect.github.com/NixOS/nixpkgs/issues/516481) | package ships with its tests disabled | current CI | no matching PR found | re-enable checks in an override, isolate `GOFLAGS` and working-directory effects, bisect build hooks | promote through Linux Fieldwork LF-35 |
| 4 | DuckDB | [large FOLLOWING-frame issue](https://redirect.github.com/duckdb/duckdb/issues/24307) | incorrect SQL result | current CI | no matching PR found | reduce numeric boundary and add window-frame regression test | promote after the partition collision |
| 5 | DuckDB | [DECIMAL median issue](https://redirect.github.com/duckdb/duckdb/issues/24314) | incorrect analytical result | current CI | no matching PR found | compare integer interpolation paths and add two-value precision fixture | promote after the partition collision |
| 6 | Ruff | [B006 multiline-string fix issue](https://redirect.github.com/astral-sh/ruff/issues/27022) | automatic fix changes runtime value | current CI | issue blocks an active patch stack | preserve literal source value in fixture and identify indentation rewrite owner | promote or coordinate |
| 7 | Ruff | [RUF055 buffer-behavior issue](https://redirect.github.com/astral-sh/ruff/issues/27024) | a safe fix changes accepted inputs | current CI | no matching PR found in sampled search | compare pre/post execution for bytes regex and buffer objects; reassess fix safety | promote |
| 8 | libarchive | [PPMd small-buffer issue](https://redirect.github.com/libarchive/libarchive/issues/3337) | valid archive decode depends on caller buffer size | current CI | no matching PR checked in round | retain minimal 7z fixture; vary read chunk size; trace PPMd refill boundary | promote |
| 9 | systemd | [oomd reload-registration issue](https://redirect.github.com/systemd/systemd/issues/43174) | silent loss of a memory-pressure guardrail | VM | no matching PR found | capture ManagedOOM notifications around user reload; add `TEST-55-OOMD.sh` scenario | promote through Linux Fieldwork, VM queue |
| 10 | CPython | [`GenericAlias` iterator race issue](https://redirect.github.com/python/cpython/issues/154916) | free-threaded data race | free-threaded TSAN | no matching PR found; follows merged change 154108 | design atomic read/strong-reference path; use a bounded test accepted by maintainers | issue-first or focused patch |
| 11 | CPython | [`<>` tokenizer issue](https://redirect.github.com/python/cpython/issues/151464) | token stream and parser language disagree | current CI | related syntax-suggestion work exists, exact issue uncovered | specify token behavior with and without `barry_as_FLUFL`; add tokenizer regression | retain |
| 12 | systemd | [router-advertisement solicitation issue](https://redirect.github.com/systemd/systemd/issues/43205) | network discovery can stop after an unusable advertisement | network namespace/VM | no overlap checked | build namespace fixture with lifetime-zero RA and observe RS schedule | retain behind VM lane |
| 13 | Nixpkgs | [AAVMF regression issue](https://redirect.github.com/NixOS/nixpkgs/issues/485220) | aarch64 firmware no longer reaches boot flow | aarch64 QEMU/VM | no matching PR found | automate good/bad firmware boot signature and bisect OVMF inputs | capability queue |
| 14 | Ruff | [EXE001 nested-comment issue](https://redirect.github.com/astral-sh/ruff/issues/27028) | false positive on ordinary source comments | current CI | no matching PR checked | enforce file-start/interpreter semantics in fixture | retain |
| 15 | pip | [build-dependency hash-policy issue](https://redirect.github.com/pypa/pip/issues/13984) | integrity policy has an undocumented boundary | current CI with local index | security discussion already occurred; maintainer direction needed | build fully local sdist/index fixture and map policy options | issue-first |
| 16 | libarchive | [Windows signed-shift issue](https://redirect.github.com/libarchive/libarchive/issues/3283) | public helper reaches undefined behavior | Windows CLANG64 UBSan | no overlap checked | add high-bit test and define size/inode overflow policy | capability queue |
| 17 | Homebrew Core | [unsolved-formula tracker](https://redirect.github.com/Homebrew/homebrew-core/issues/139929) | recurring build and test failures block package updates | macOS/Linux CI varies | tracker intentionally invites help | select leaves with reproducible logs and no active PR | recurring intake |
| 18 | Homebrew Core | [OpenSSL 4 migration tracker](https://redirect.github.com/Homebrew/homebrew-core/issues/278366) | broad compatibility migration across dependents | macOS/Linux CI | coordinated tracker | take leaf formulae by dependent count and build system | batch source |

## Claimed reference candidates

| Target | Issue | Claim state | Retained value |
|---|---|---|---|
| Rust | [nested-turbofish diagnostic](https://redirect.github.com/rust-lang/rust/issues/159745) | assigned after rustbot claims | compact UI diagnostic packet |
| Rust | [missing-match-arm diagnostic](https://redirect.github.com/rust-lang/rust/issues/159686) | assigned | match-arm recovery and suggestion design |
| Rust | [dyn-compatibility wording](https://redirect.github.com/rust-lang/rust/issues/159492) | assigned and mentored | pedagogic diagnostic wording |
| Rust | [tidy/attributes validation](https://redirect.github.com/rust-lang/rust/issues/157184) | assigned | validation across registry and `.gitattributes` |
| Rust | [ineffective `#[path]` attributes](https://redirect.github.com/rust-lang/rust/issues/157260) | assigned and mentored | attribute validation |

Stop independent implementation unless a claim is released or the contributor/maintainers explicitly invite collaboration.

## Removed from active implementation

| Target | Issue | Existing work | Retained value |
|---|---|---|---|
| Nixpkgs | [pandoc Lua feature issue](https://redirect.github.com/NixOS/nixpkgs/issues/540900) | [package PR 540913](https://redirect.github.com/NixOS/nixpkgs/pull/540913) | converting a silently disabled feature into a hard build contract |
| Nixpkgs | [Darwin libffi issue](https://redirect.github.com/NixOS/nixpkgs/issues/541367) | [package PR 541990](https://redirect.github.com/NixOS/nixpkgs/pull/541990) | platform-transition diagnosis and focused workaround |
| CPython | [zip repack/live-reader issue](https://redirect.github.com/python/cpython/issues/154842) | [PR 154843](https://redirect.github.com/python/cpython/pull/154843) | guard mutable archive operations against live readers |
| CPython | [incremental iconv issue](https://redirect.github.com/python/cpython/issues/154859) | [PR 154862](https://redirect.github.com/python/cpython/pull/154862) | persistent state for incremental codecs |
| CPython | [ISO-2022-CN-EXT issue](https://redirect.github.com/python/cpython/issues/154863) | [PR 154899](https://redirect.github.com/python/cpython/pull/154899) | distinguish flush counts from substitution failures |
| CPython | [negative curses attributes issue](https://redirect.github.com/python/cpython/issues/154874) | PRs 154875 and 154887 | signed-versus-unsigned terminal attributes and portable tests |
| CPython | [Future traceback issue](https://redirect.github.com/python/cpython/issues/154791) | [PR 154798](https://redirect.github.com/python/cpython/pull/154798) | compare C and pure-Python implementations for lifecycle drift |
| libarchive | [standalone AppleDouble issue](https://redirect.github.com/libarchive/libarchive/issues/3310) | [PR 3334](https://redirect.github.com/libarchive/libarchive/pull/3334) | pairing validation before consuming ambiguous metadata-looking input |
| pip | [latest-marker issue](https://redirect.github.com/pypa/pip/issues/14177) | [PR 14178](https://redirect.github.com/pypa/pip/pull/14178) | type-consistent comparison restoring an unreachable branch |

## Active implementation limit

Keep at most three newly implemented candidates awaiting first review. The preferred first three are Ruff's annotation/runtime boundary, DuckDB's partition collision, and libarchive's short-read boundary. The Nixpkgs package diagnosis can run independently because it begins with an override and test restoration rather than an upstream code branch.