# Deep dive — unit 22 gomarkdoc checks

## In simple words

Nixpkgs currently disables gomarkdoc 1.1.0's Go tests. Existing upstream history identifies an omitted empty fixture as the observed failure, while Fieldwork execution also found a Go 1.26 documentation-golden difference. The retained repair addressed those compatibility points but accidentally exercised only the command package because Nixpkgs reuses `subPackages` for test discovery.

The clean candidate preserves the narrow installed binary and clears that selector only before checks. Its full-discovery Linux and Darwin execution remains queued, so the current answer is a source-complete repair with an exact execution blocker.

## Scope

This packet covers one Nixpkgs package expression:

- `pkgs/by-name/go/gomarkdoc/package.nix`

It carries forward Fieldwork issue #241 and PR #265, corrects their retained coverage claim, renews the candidate on an owned Nixpkgs branch, and records the current upstream issue, source, tests, alternatives, drafts, and blocker. Every other upstream unit remains outside scope.

## Current upstream state

At public Nixpkgs commit [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1), gomarkdoc remains version 1.1.0 and uses:

- `buildGoModule`;
- `subPackages = [ "cmd/gomarkdoc" ]`;
- `doCheck = false`;
- unchanged source and vendor hashes;
- a `testers.testVersion` passthru.

A later public head, [`f8e81fc7eb063db454f563cdd596fb96a5ad1497`](https://github.com/NixOS/nixpkgs/commit/f8e81fc7eb063db454f563cdd596fb96a5ad1497), has the same gomarkdoc package blob and the same Go builder blob. The candidate is five public commits behind that checked head with no relevant-path drift.

## Upstream problem record and history

### Nixpkgs issue #516481

Open issue [#516481](https://github.com/NixOS/nixpkgs/issues/516481) records that gomarkdoc checks regressed between March and May 2026. Its reproduced failure includes:

```text
flag provided but not defined: -mod
open ../.gomarkdoc-empty.yml: no such file or directory
```

The issue classifies the unknown-flag messages as stable diagnostics and the missing `.gomarkdoc-empty.yml` as the observed failure cause. It has no competing implementation or discussion.

### Nixpkgs PR #516792

Merged PR [#516792](https://github.com/NixOS/nixpkgs/pull/516792) restored package buildability by adding `doCheck = false`. This is the current containment and the direct historical predecessor of unit 22.

### Nixpkgs PR #279440

Merged PR [#279440](https://github.com/NixOS/nixpkgs/pull/279440) introduced gomarkdoc 1.1.0 with `subPackages = [ "cmd/gomarkdoc" ]`, the source/vendor hashes, linker flags, version passthru, and maintainer metadata.

No equivalent PR restoring all checks was found on 2026-08-01.

## gomarkdoc v1.1.0 source behavior

### `GOFLAGS` parsing

[`defaultTags()`](https://github.com/princjef/gomarkdoc/blob/v1.1.0/cmd/gomarkdoc/command.go) reads `GOFLAGS`, creates a `flag.FlagSet` that recognizes only `-tags`, and returns `nil` after any parse error. Nixpkgs' `-mod=vendor` therefore reaches an application parser, emits a diagnostic, and yields no default tags.

This source read narrows the candidate claim: removing `-mod=vendor` keeps a Nix build-only option out of gomarkdoc's application parser and avoids the diagnostic. The current records do not establish that this diagnostic alone fails the suite.

### Missing fixture

[`command_test.go`](https://github.com/princjef/gomarkdoc/blob/v1.1.0/cmd/gomarkdoc/command_test.go) changes into `testData` and passes:

```text
--config ../.gomarkdoc-empty.yml
```

The v1.1.0 tag does not contain that empty file. `touch .gomarkdoc-empty.yml` at the unpacked source root recreates the exact referenced empty fixture in the disposable build tree.

### Test package set

The tag contains tests in the root package, `lang`, multiple `format` packages, and `cmd/gomarkdoc`. Representative files include:

- `renderer_test.go`;
- `lang/func_test.go`, `lang/type_test.go`, and related files;
- `format/plain_test.go`, `format/devops_test.go`, `format/github_test.go`;
- `format/formatcore/base_test.go`;
- `cmd/gomarkdoc/command_test.go`.

The package's `go.mod` declares Go 1.18. Fieldwork's retained negative comparison found a v1.1.0 golden mismatch under Go 1.26, while the old Go 1.25 command-package execution passed.

## Retained Fieldwork investigation

### Exact revisions and receipts

- Old Nixpkgs base: [`bbbd95e512a066deaefa89e3a244b541ed6c8c7f`](https://github.com/NixOS/nixpkgs/commit/bbbd95e512a066deaefa89e3a244b541ed6c8c7f)
- Old execution patch commit: [`1cdbcfa7bf07086ed9a46f440d3595595afdd241`](https://github.com/teamleaderleo/fieldwork/commit/1cdbcfa7bf07086ed9a46f440d3595595afdd241)
- Old retained Fieldwork head: [`d559a9756294b94c7a8ee4e68cae6ed603352986`](https://github.com/teamleaderleo/fieldwork/commit/d559a9756294b94c7a8ee4e68cae6ed603352986)
- Old execution run: [30598626867](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867)
- Linux job: `91056349644`
- Darwin job: `91056349617`
- Linux artifact: `8781532516`
- Darwin artifact: `8781695770`

### What the old candidate established

1. `buildGo125Module` built the final package on x86_64-linux and aarch64-darwin.
2. Test-time `GOFLAGS` removal plus fixture creation allowed the command package to pass.
3. The version passthru printed `1.1.0` on both platforms.
4. The source and vendor hashes remained unchanged.

### The old coverage error

The old report and PR description called the successful build a full suite. The logs show one test package:

```text
Running phase: checkPhase
ok      github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

Nixpkgs' generic Go builder defines `getGoDirs`. When `subPackages` is nonempty, `getGoDirs test` emits those selected packages instead of discovering directories containing `*_test.go`. Because gomarkdoc uses `subPackages = [ "cmd/gomarkdoc" ]`, the old check phase skipped the root package, `lang`, and format packages.

Fieldwork issue #241 comment `5145303967` and PR #265 review `4828305183` preserve this correction. All earlier “full suite” wording is superseded.

## Builder behavior at the renewed and current heads

At both the renewed base and checked public head, [`pkgs/build-support/go/module.nix`](https://github.com/NixOS/nixpkgs/blob/f8e81fc7eb063db454f563cdd596fb96a5ad1497/pkgs/build-support/go/module.nix):

1. defines `getGoDirs` during `buildPhase`;
2. converts `subPackages` through `concatTo`;
3. uses that array when nonempty;
4. otherwise discovers directories containing files matching `*$type.go`;
5. runs `preCheck` before `getGoDirs test`;
6. removes `-trimpath` for tests;
7. invokes the standard `buildGoDir test` helper for every selected directory.

This ordering permits a package-local adjustment: assign `subPackages=()` after the binary build and before test discovery.

## Selected repair

The canonical source commit is [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683).

It changes one file and performs four actions:

1. `buildGoModule` → `buildGo125Module`.
2. `doCheck = false` → `doCheck = true`.
3. In `preCheck`, remove `-mod=vendor` from `GOFLAGS` and create `.gomarkdoc-empty.yml`.
4. In `preCheck`, set `subPackages=()` so the standard check phase discovers all real test packages.

The package still installs only `cmd/gomarkdoc`, keeps both hashes unchanged, retains the materialized vendor directory and `GOPROXY=off`, and keeps the version passthru.

## Why this stays package-local

The compatibility and discovery concerns belong to gomarkdoc 1.1.0's package expression:

- a release-specific documentation golden;
- application parsing of build-environment `GOFLAGS`;
- an omitted empty release fixture;
- a narrower binary build target than test target set.

Changing the generic Go builder would affect many packages. Updating gomarkdoc would expand the contribution into a version/dependency change. Replacing `checkPhase` would duplicate standard builder flags, tags, parallelism, and error handling. The one-file expression remains the smallest current candidate.

## Open design judgment: keep or remove `-mod=vendor`

Source and issue history show that the diagnostic is benign. Two coherent variants remain:

- **selected candidate:** remove the build-only token so gomarkdoc's parser sees only application-relevant flags;
- **minimal blocker-only variant:** retain `-mod=vendor`, synthesize the fixture, pin Go 1.25, and clear the test selector.

The selected variant preserves the assignment's stated contract and the previously executed path. A future reviewer may request a comparative exact-head run with the token retained. That is a source-review question, not a reason to widen unit 22 today.

## Source cleanliness

Compare [`55096b0c...94be3956`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683):

- one commit;
- one changed file;
- 13 additions and 6 deletions;
- no workflows, Fieldwork files, generated output, hash churn, or unrelated formatting.

## Execution state

Fieldwork PR [#437](https://github.com/teamleaderleo/fieldwork/pull/437) pins the exact source head and requires root, `lang`, format, command, and version evidence on x86_64-linux and aarch64-darwin.

- Run: `30674476739`
- Linux job: `91298756809`
- Darwin job: `91298756825`
- Current state: both queued

This runtime has no `nix` or `nix-build`, and an attempt to retrieve the official Nix 2.35.1 installer failed. It cannot replace the hosted execution.

## Linked Fieldwork records

- Parent consolidation issue: [#435](https://github.com/teamleaderleo/fieldwork/issues/435)
- Unit investigation: [#241](https://github.com/teamleaderleo/fieldwork/issues/241)
- Retained PR: [#265](https://github.com/teamleaderleo/fieldwork/pull/265)
- Open-source ecosystem programme: [#207](https://github.com/teamleaderleo/fieldwork/issues/207)
- Scout record: [#211](https://github.com/teamleaderleo/fieldwork/issues/211)
- Initiative: [#254](https://github.com/teamleaderleo/fieldwork/issues/254)
- Referenced target issue: [#11](https://github.com/teamleaderleo/fieldwork/issues/11), which describes DuckDB and represents a link-label mismatch in #241.

## Public interaction boundary

All NixOS and gomarkdoc activity in this unit is read-only. The clean source commit, execution carrier, packet, drafts, and handoff live in repositories owned by `teamleaderleo`. No public issue, pull request, review, comment, reaction, or maintainer contact was created or modified.
