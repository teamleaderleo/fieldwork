# Deep dive — unit 22 gomarkdoc checks

## Scope

This packet covers one Nixpkgs package expression:

- `pkgs/by-name/go/gomarkdoc/package.nix`

It carries forward the investigation from Fieldwork issue #241 and PR #265, corrects the retained execution claim, renews the candidate on current Nixpkgs `master`, and prepares a clean source branch plus drafts. It leaves every other upstream unit and shared record unchanged.

## Current upstream state

At public Nixpkgs commit [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1), gomarkdoc remains version 1.1.0 and uses:

- `buildGoModule`
- `subPackages = [ "cmd/gomarkdoc" ]`
- `doCheck = false`
- the existing source and vendor hashes
- a `testers.testVersion` passthru

The disabled-check comment says gomarkdoc command tests read `GOFLAGS`, then reject Nixpkgs' `-mod=vendor` flag as an unknown application flag.

The disabling change was merged through Nixpkgs PR [#516792](https://github.com/NixOS/nixpkgs/pull/516792) after a Hydra failure. The initial package entered through [#279440](https://github.com/NixOS/nixpkgs/pull/279440).

## Retained Fieldwork investigation

### Exact revisions

- Old Nixpkgs base: [`bbbd95e512a066deaefa89e3a244b541ed6c8c7f`](https://github.com/NixOS/nixpkgs/commit/bbbd95e512a066deaefa89e3a244b541ed6c8c7f)
- Old execution patch commit: [`1cdbcfa7bf07086ed9a46f440d3595595afdd241`](https://github.com/teamleaderleo/fieldwork/commit/1cdbcfa7bf07086ed9a46f440d3595595afdd241)
- Old retained Fieldwork head: [`d559a9756294b94c7a8ee4e68cae6ed603352986`](https://github.com/teamleaderleo/fieldwork/commit/d559a9756294b94c7a8ee4e68cae6ed603352986)
- Old execution run: [30598626867](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867)
- Linux job: `91056349644`
- Darwin job: `91056349617`
- Linux artifact: `8781532516`
- Darwin artifact: `8781695770`

### What the old candidate got right

1. **Go toolchain compatibility**
   - gomarkdoc v1.1.0's generated-document golden output aligns with Go 1.25 behavior.
   - `buildGo125Module` supplied Go 1.25.12 in the recorded run.

2. **Nix `GOFLAGS` isolation**
   - the candidate removed only `-mod=vendor` during tests.
   - the vendored dependency tree remained materialized and network access remained disabled through the standard builder.

3. **Missing release fixture**
   - command tests refer to `.gomarkdoc-empty.yml`.
   - the release tag omits that empty file.
   - `touch .gomarkdoc-empty.yml` restores the expected fixture locally.

4. **Version behavior**
   - `gomarkdoc.tests.version` printed `1.1.0` on Linux and Darwin.

### The old coverage error

The old report and PR description called the successful build a full suite. The logs show one test package:

```text
Running phase: checkPhase
ok      github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

Nixpkgs' generic Go builder defines `getGoDirs`. When `subPackages` is nonempty, `getGoDirs test` emits those selected packages instead of discovering directories containing `*_test.go`. Because gomarkdoc uses `subPackages = [ "cmd/gomarkdoc" ]`, the old check phase skipped the root package, `lang`, and format packages.

That observation came from the repair review on Fieldwork PR #265 and the exact `module.nix` source. It supersedes the old “full suite” wording while preserving every valid compatibility finding.

## Builder behavior at the renewed base

At [`55096b0c`](https://github.com/NixOS/nixpkgs/blob/55096b0ce13784d4f6420059c5627475fa26ebb1/pkgs/build-support/go/module.nix), `buildGoModule`:

1. defines `getGoDirs` during `buildPhase`;
2. uses `subPackages` when that value is nonempty;
3. otherwise discovers directories containing files matching `*$type.go`;
4. runs `preCheck` at the start of `checkPhase`;
5. strips `-trimpath` for tests;
6. calls `getGoDirs test` and passes each package to the standard `buildGoDir test` helper.

This ordering permits a package-local adjustment in `preCheck`: assign `subPackages=()` after installation targets have already been selected and before test package discovery occurs.

## Selected repair

The canonical source commit is [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683).

It changes one file and performs four actions:

1. `buildGoModule` → `buildGo125Module`.
2. `doCheck = false` → `doCheck = true`.
3. In `preCheck`, remove only `-mod=vendor` and create `.gomarkdoc-empty.yml`.
4. In `preCheck`, set `subPackages=()` so the standard check phase discovers all real test packages.

The package still installs only `cmd/gomarkdoc`, keeps both hashes unchanged, retains offline vendor mode, and keeps the version passthru.

## Why this is package-local

The behavior mismatch belongs to gomarkdoc v1.1.0:

- its golden output depends on a specific Go series;
- its command tests consume `GOFLAGS` through application flag parsing;
- its release archive omits a test fixture;
- its Nix expression needs a narrower binary build target than its test target set.

Changing the generic Go builder would affect thousands of packages. Updating gomarkdoc itself would expand the contribution into a version update with different source and dependency hashes. The one-file expression repair keeps the contribution reviewable and reversible.

## Source cleanliness

Compare [`55096b0c...94be3956`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683):

- one commit;
- one changed file;
- 13 additions and 6 deletions;
- no workflows;
- no Fieldwork files;
- no generated files;
- no hash churn;
- no unrelated formatting.

## Duplicate and recent-history search

The 2026-08-01 search found:

- [#279440](https://github.com/NixOS/nixpkgs/pull/279440): package introduction;
- [#516792](https://github.com/NixOS/nixpkgs/pull/516792): test disablement after Hydra failure;
- treewide changes that happened to touch the expression;
- no open or merged PR restoring the gomarkdoc test suite.

The current upstream expression remains semantically identical in the relevant area to the old Fieldwork target, so the renewed patch is a direct continuation, not a competing implementation.

## Linked Fieldwork records

- Parent consolidation issue: [#435](https://github.com/teamleaderleo/fieldwork/issues/435)
- Unit investigation: [#241](https://github.com/teamleaderleo/fieldwork/issues/241)
- Retained PR: [#265](https://github.com/teamleaderleo/fieldwork/pull/265)
- Open-source ecosystem programme: [#207](https://github.com/teamleaderleo/fieldwork/issues/207)
- Scout record: [#211](https://github.com/teamleaderleo/fieldwork/issues/211)
- Initiative: [#254](https://github.com/teamleaderleo/fieldwork/issues/254)
- Referenced target issue: [#11](https://github.com/teamleaderleo/fieldwork/issues/11), which currently describes DuckDB and therefore represents a link-label mismatch in #241.

## Public interaction boundary

All NixOS and gomarkdoc activity in this unit is read-only. The clean source commit, execution carrier, packet, drafts, and handoff live in repositories owned by `teamleaderleo`. No NixOS issue, pull request, review, comment, reaction, or maintainer contact was created.
