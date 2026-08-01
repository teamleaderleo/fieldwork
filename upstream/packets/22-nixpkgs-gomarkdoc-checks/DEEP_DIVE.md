# Deep dive — unit 22 gomarkdoc checks

## In simple words

Nixpkgs disables gomarkdoc 1.1.0's tests. Public history identifies an omitted empty fixture as the observed failure, and retained Fieldwork execution also found a Go 1.26 documentation-golden difference. The earlier repair addressed those points but tested only `cmd/gomarkdoc` because Nixpkgs reused `subPackages` for check discovery.

The clean candidate preserves command-only installation and clears that selector only before checks. Its source diff is complete. Full Linux, Darwin, installed-help, version, Linux `nixpkgs-review`, and Fieldwork-integrity receipts remain queued, so the unit is held at the execution boundary.

## Scope and exact source

This unit changes one file:

- [`pkgs/by-name/go/gomarkdoc/package.nix`](https://github.com/teamleaderleo/nixpkgs/blob/94be3956403ebf368b9d8262fdc9e5a5d2e80683/pkgs/by-name/go/gomarkdoc/package.nix)

Exact identities:

- public base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- clean branch: `teamleaderleo/nixpkgs:fieldwork/unit-22-gomarkdoc-checks`
- clean head: [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- complete compare: [`55096b0c...94be3956`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- later public head checked: [`f8e81fc7eb063db454f563cdd596fb96a5ad1497`](https://github.com/NixOS/nixpkgs/commit/f8e81fc7eb063db454f563cdd596fb96a5ad1497)
- relevant package and Go-builder behavior at that later head: unchanged

## Public upstream history

### Issue #516481

Open [Nixpkgs issue #516481](https://github.com/NixOS/nixpkgs/issues/516481) reproduces:

```text
flag provided but not defined: -mod
open ../.gomarkdoc-empty.yml: no such file or directory
```

It treats the unknown-flag output as benign and identifies the missing empty fixture as the observed failure. It has no comments or competing implementation.

### PR #516792

Merged [PR #516792](https://github.com/NixOS/nixpkgs/pull/516792) adds `doCheck = false` as containment. Its `nixpkgs-review` receipt built gomarkdoc on four platforms after checks were disabled.

### PR #279440

Merged [PR #279440](https://github.com/NixOS/nixpkgs/pull/279440) introduced gomarkdoc 1.1.0 with `subPackages = [ "cmd/gomarkdoc" ]`, fixed source/vendor hashes, linker flags, version passthru, and maintainer metadata.

### Release context

Issue [#516381](https://github.com/NixOS/nixpkgs/issues/516381) is the release-campaign context linked from the disable-tests PR.

No equivalent restoration PR was found on 2026-08-01.

## gomarkdoc v1.1.0 source behavior

### `GOFLAGS`

[`defaultTags()`](https://github.com/princjef/gomarkdoc/blob/v1.1.0/cmd/gomarkdoc/command.go) reads `GOFLAGS`, accepts only `-tags`, and returns `nil` after a parse error. `-mod=vendor` therefore reaches an application parser, emits a diagnostic, and yields no default tags.

The candidate removes that token during tests as semantic isolation. Current evidence does not establish that the diagnostic alone fails the suite.

### Missing fixture

[`command_test.go`](https://github.com/princjef/gomarkdoc/blob/v1.1.0/cmd/gomarkdoc/command_test.go) changes into `testData` and references `../.gomarkdoc-empty.yml`. The v1.1.0 tag omits that empty file. `touch .gomarkdoc-empty.yml` recreates the exact fixture in the disposable source tree.

### Test package set

The tag has tests in:

- the root package;
- `lang`;
- multiple format packages, including `format/formatcore`;
- `cmd/gomarkdoc`.

Its `go.mod` declares Go 1.18. Retained Fieldwork comparison found a checked golden mismatch under Go 1.26; old Go 1.25 command-package execution passed.

## The old coverage error

Retained Fieldwork issue [#241](https://github.com/teamleaderleo/fieldwork/issues/241) and PR [#265](https://github.com/teamleaderleo/fieldwork/pull/265) originally called the result a full suite. Two retained runs prove otherwise:

- run [`30598626867`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867);
- run [`30598687251`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251).

Both Linux and Darwin logs showed only:

```text
Running phase: checkPhase
ok      github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

and version output `1.1.0`.

Nixpkgs' Go builder uses nonempty `subPackages` in both build and test discovery. The old candidate therefore skipped root, `lang`, and format packages. Issue #241 comment `5145303967` and PR #265 review `4828305183` preserve this correction.

## Builder behavior

At the renewed and later checked heads, [`module.nix`](https://github.com/NixOS/nixpkgs/blob/f8e81fc7eb063db454f563cdd596fb96a5ad1497/pkgs/build-support/go/module.nix):

1. defines `getGoDirs` during build setup;
2. converts `subPackages` through `concatTo`;
3. uses that array when nonempty;
4. otherwise discovers directories containing matching Go files;
5. runs `preCheck` before `getGoDirs test`;
6. invokes the standard `buildGoDir test` helper.

This ordering permits `subPackages=()` after the binary build and before test discovery.

## Selected source repair

Commit [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683):

1. selects `buildGo125Module`;
2. enables checks;
3. removes `-mod=vendor` during checks;
4. creates `.gomarkdoc-empty.yml`;
5. clears `subPackages` before standard test discovery.

It keeps command-only installation, source and vendor hashes, linker flags, offline module setup, and version passthru unchanged.

## Why the repair stays package-local

The concerns are specific to gomarkdoc 1.1.0:

- release-specific checked output;
- application parsing of build-environment flags;
- an omitted release fixture;
- different build and test target sets.

A generic builder change would affect many packages. Updating gomarkdoc would add version/dependency scope. Replacing `checkPhase` would duplicate standard Nixpkgs Go behavior.

## Open design judgment

A narrower variant could retain `-mod=vendor`, because the public issue and source classify its parser output as benign. The selected candidate removes it to preserve the assignment's separation between build-system and application flags and because the retained passing path used that setup. A future reviewer may request a comparative run without widening this unit now.

## Active execution generation

- carrier PR: [Fieldwork #437](https://github.com/teamleaderleo/fieldwork/pull/437)
- branch: `p0/435-unit-22-execution`
- current carrier head: [`b6003f2a3523f01880ff5690798b69afcb4e11f5`](https://github.com/teamleaderleo/fieldwork/commit/b6003f2a3523f01880ff5690798b69afcb4e11f5)
- target run: [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557)
- Linux job: `91300175276`
- Darwin job: `91300175296`
- integrity run: [`30674969559`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969559)
- superseded carrier head/run: `5c9d932276679836547b79a38aaf6b951dbdad02` / `30674476739`

Current carrier controls:

- exact source head, parent, one-file fence, and `diff --check`;
- package build on Linux and Darwin;
- root, `lang`, format, command, and minimum package-count assertions;
- installed executable and help output;
- version passthru;
- Linux `nixpkgs-review rev HEAD --no-shell`;
- retained logs and source diff.

All current target jobs and Fieldwork integrity remain queued. The runtime has no `nix` or `nix-build`, and its installer retrieval attempt failed, so it cannot replace hosted execution.

## Linked Fieldwork records

- parent: [#435](https://github.com/teamleaderleo/fieldwork/issues/435)
- investigation: [#241](https://github.com/teamleaderleo/fieldwork/issues/241)
- retained PR: [#265](https://github.com/teamleaderleo/fieldwork/pull/265)
- programme: [#207](https://github.com/teamleaderleo/fieldwork/issues/207)
- scout: [#211](https://github.com/teamleaderleo/fieldwork/issues/211)
- initiative: [#254](https://github.com/teamleaderleo/fieldwork/issues/254)
- referenced target issue: [#11](https://github.com/teamleaderleo/fieldwork/issues/11), which describes DuckDB and exposes a link-label mismatch in #241.

## Current answer

The source candidate, alternatives, prior art, and discriminating gates are durable. Required clean-head execution, repository integrity, receipt transfer, carrier retirement, fresh-head rerun, independent acceptance, and public authority remain absent. Current disposition: `HOLD`.

No public upstream interaction occurred.
