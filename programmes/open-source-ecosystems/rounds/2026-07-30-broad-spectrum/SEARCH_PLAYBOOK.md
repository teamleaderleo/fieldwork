# Ecosystem Search Playbook

Snapshot: 2026-07-30. These searches create candidate inventories; they do not grant permission to claim work or contact maintainers.

## Universal sequence

For every candidate:

1. open the issue and record exact tested versions, revisions, environment, and reproducer;
2. search open and closed pull requests using the issue number, rule code, error text, and owning function;
3. inspect the current source file and adjacent tests at an exact revision;
4. classify the owning boundary: downstream package, upstream project, toolchain, environment, or unsupported use;
5. run or restate the smallest distinguishing probe;
6. record consequence, environment cost, overlap, and the next command;
7. promote, park, split, or stop.

GitHub pull-request search can miss linked work. Read the issue body's `Linked PRs` section and comments before treating a candidate as uncovered.

## Package collections

### Nixpkgs

Recurring searches:

```text
repo:NixOS/nixpkgs is:issue is:open "build failure"
repo:NixOS/nixpkgs is:issue is:open regression package
repo:NixOS/nixpkgs is:issue is:open "checkPhase"
repo:NixOS/nixpkgs is:issue is:open "works" "fails" nixpkgs
```

Prefer reports with:

- one known-good and one known-bad nixpkgs revision;
- a direct `nix build` command;
- unchanged package expression across the regression window;
- a Hydra/local discrepancy worth explaining;
- a disabled `doCheck`, removed test, downstream patch, or automatic feature flag.

Inspect:

```text
pkgs/by-name/<prefix>/<package>/package.nix
pkgs/build-support/
pkgs/stdenv/
```

Then search PRs by issue number and package name. Silent feature loss deserves a package test that turns the loss into a build failure.

### Homebrew Core

Start from durable trackers:

- issue #139929 — formula updates blocked by build or test failures;
- issue #278366 — OpenSSL 4 migration;
- issue #191352 — additional architecture-independent bottle candidates.

For one formula, capture:

```sh
brew info --json=v2 FORMULA
brew audit --strict FORMULA
brew test-bot --only-formulae FORMULA
```

Use `diffoscope` for bottle differences and inspect both the formula and upstream release/build changes.

### Debian, Fedora, and Arch

Add these after the first Nixpkgs/Homebrew batch:

- Debian newcomer, orphaned-package, release-critical, reproducibility, and autopkgtest queues;
- Fedora FTBFS/FTI, Koschei, and dist-git issues;
- Arch package build failures and carefully selected AUR cases with an upstream consequence.

The first retained result should include exact package source identity, distribution patch set, build command, and whether the correction belongs downstream or upstream.

## Runtimes and standard libraries

### CPython

Recurring searches:

```text
repo:python/cpython is:issue is:open label:type-bug created:>YYYY-MM-DD
repo:python/cpython is:issue is:open label:easy label:type-bug
repo:python/cpython is:issue is:open "free-threaded" race
repo:python/cpython is:issue is:open "incorrect" stdlib
```

Strong candidates include:

- a Python-only reproducer;
- a mismatch between C and pure-Python implementations;
- platform behavior isolated to one extension module;
- a small parser or error-output fixture;
- a ThreadSanitizer report with a compact owning field.

Inspect the issue's linked PR block. Several live issues in this round already had patches despite weak direct PR-search results.

### Rust

Recurring searches:

```text
repo:rust-lang/rust is:issue is:open label:E-easy created:>YYYY-MM-DD
repo:rust-lang/rust is:issue is:open label:E-mentor
repo:rust-lang/rust is:issue is:open label:E-needs-test
repo:rust-lang/rust is:issue is:open diagnostic "Current output" "Desired output"
```

Prefer UI-test candidates with:

- a source fixture under twenty lines;
- exact current and desired output;
- a localized parser or diagnostic owner;
- no active assignment or pull request.

Run focused UI tests before a full bootstrap test.

## Developer tools

### Ruff

Recurring searches:

```text
repo:astral-sh/ruff is:issue is:open label:bug created:>YYYY-MM-DD
repo:astral-sh/ruff is:issue is:open "safe fix" behavior
repo:astral-sh/ruff is:issue is:open "Failed to converge"
repo:astral-sh/ruff is:issue is:open "syntax error" fix
```

For fix bugs, preserve three artifacts:

1. source before the fix;
2. source after the fix;
3. runtime output or parse result before and after.

Search by rule code and inspect any stabilization PR. A stabilization change can become the coordination point even when the fix itself has no PR.

### pip and package managers

Recurring searches:

```text
repo:pypa/pip is:issue is:open created:>YYYY-MM-DD
repo:pypa/pip is:issue is:open hashes build dependencies
repo:pypa/pip is:issue is:open resolver hint
```

Build local fixtures with a local package index, sdists, wheels, lockfiles, and offline mode. Separate policy/design questions from implementation bugs before proposing code.

## Foundational libraries

### libarchive

Recurring searches:

```text
repo:libarchive/libarchive is:issue is:open created:>YYYY-MM-DD
repo:libarchive/libarchive is:issue is:open buffer overflow
repo:libarchive/libarchive is:issue is:open small buffer
repo:libarchive/libarchive is:issue is:open UBSan
```

Retain the smallest archive fixture and vary one reader parameter at a time. Check parser state, refill boundaries, integer width, metadata pairing, and platform-specific helpers. Security-sensitive reports require the project's disclosure expectations.

## Databases

### DuckDB

Recurring searches:

```text
repo:duckdb/duckdb is:issue is:open label:reproduced created:>YYYY-MM-DD
repo:duckdb/duckdb is:issue is:open "different results"
repo:duckdb/duckdb is:issue is:open "lose data"
repo:duckdb/duckdb is:issue is:open "incorrect" SQL
```

Prefer pure SQL cases. Record:

- exact DuckDB commit;
- optimizer and configuration settings;
- expected and actual result;
- the smallest values that cross the boundary;
- an adjacent `.test` file capable of holding the regression.

## Linux systems

### systemd

Recurring searches:

```text
repo:systemd/systemd is:issue is:open created:>YYYY-MM-DD
repo:systemd/systemd is:issue is:open race
repo:systemd/systemd is:issue is:open "daemon-reload"
repo:systemd/systemd is:issue is:open "silently"
```

Classify each candidate before execution:

- current CI;
- privileged CI;
- network namespace;
- VM;
- device or suspend/resume;
- kernel or TPM matrix.

Record the matching `TEST-*.sh` suite, exact unit settings, cgroup mode, kernel, and distribution. For state-loss bugs, capture the protocol messages or unit-property notifications that cause insertion and removal.

## Stop checks

Stop duplicate implementation when an active PR already contains:

- the same reproducer;
- the same owning boundary;
- a regression test covering the consequence;
- an implementation that has entered maintainer review.

Retain the candidate as a reference when it demonstrates an especially useful diagnosis, test method, or downstream patch-retirement opportunity.