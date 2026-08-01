# Deep dive — unit 22 gomarkdoc checks

## Current technical answer

Nixpkgs builds only `cmd/gomarkdoc`, and its generic Go builder applies the same nonempty `subPackages` list to check discovery. Unit 22 restores that selected command-package check path with three package-local compatibility adjustments:

1. use Go 1.25 for gomarkdoc 1.1.0's retained command golden;
2. recreate the empty config fixture omitted from the release tag;
3. remove Nix's build-only `-mod=vendor` token before gomarkdoc parses `GOFLAGS` as application flags.

A separate exact-head experiment proved that clearing `subPackages` does reach all upstream test packages. It also proved that the broader suite is not compatible with modern Go 1.25: two `lang` tests compare old standard-library prose against newer bracketed documentation links. Unit 22 retains that failure and does not weaken those tests.

## Scope and exact source

Changed file:

- [`pkgs/by-name/go/gomarkdoc/package.nix`](https://github.com/teamleaderleo/nixpkgs/blob/569c0c4d11e5a14f3fe6237c0a50dc484f80e744/pkgs/by-name/go/gomarkdoc/package.nix)

Exact identities:

- public base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- clean branch: `teamleaderleo/nixpkgs:fieldwork/unit-22-gomarkdoc-checks`
- clean head: [`569c0c4d11e5a14f3fe6237c0a50dc484f80e744`](https://github.com/teamleaderleo/nixpkgs/commit/569c0c4d11e5a14f3fe6237c0a50dc484f80e744)
- compare: [`55096b0c...569c0c4d`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...569c0c4d11e5a14f3fe6237c0a50dc484f80e744)
- source fence: one commit, one file
- later public head checked: `f8e81fc7eb063db454f563cdd596fb96a5ad1497`; no relevant overlap found in the checked advance

## Public history

- Open issue [NixOS/nixpkgs#516481](https://github.com/NixOS/nixpkgs/issues/516481) records unknown-flag output and the missing `.gomarkdoc-empty.yml` failure. It treats the flag diagnostic as benign.
- Merged PR [#516792](https://github.com/NixOS/nixpkgs/pull/516792) disables checks as containment.
- Merged PR [#279440](https://github.com/NixOS/nixpkgs/pull/279440) introduced gomarkdoc 1.1.0 with `subPackages = [ "cmd/gomarkdoc" ]`.
- No equivalent restoration PR was found on 2026-08-01.

No public interaction occurred.

## Source behavior

### Application parsing of `GOFLAGS`

gomarkdoc v1.1.0's `defaultTags()` reads `GOFLAGS`, accepts only `-tags`, emits a diagnostic for unknown tokens, and returns no default tags after parse failure. Nixpkgs' `-mod=vendor` is a build-system option, not a gomarkdoc application option.

The selected candidate removes only that token during checks. This is semantic isolation; available evidence does not establish the diagnostic as the sole failing condition.

### Omitted fixture

`cmd/gomarkdoc/command_test.go` changes into `testData` and references `../.gomarkdoc-empty.yml`. The tagged release omits the file. `touch .gomarkdoc-empty.yml` restores the expected empty fixture in the disposable build tree.

### Package selection

`subPackages = [ "cmd/gomarkdoc" ]` selects the built command. The Go builder also uses that list for tests when nonempty. The selected source retains this behavior, so the test boundary corresponds to the package output.

## Full-discovery experiment

Superseded source head `94be3956403ebf368b9d8262fdc9e5a5d2e80683` added `subPackages=()` inside `preCheck`.

Run [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557) verified on x86_64-linux and aarch64-darwin that:

- exact source and one-file fence were correct;
- `preCheck` ran before test selection;
- root, command, `format`, and `format/formatcore` passed;
- `lang` failed identically on both platforms.

The failures were:

```text
[Scanner] != Scanner
*[os.File] != *os.File
```

The tests read Go standard-library documentation and compare exact summaries. Modern Go comments use bracketed links, while gomarkdoc v1.1.0 expectations retain earlier prose. Detailed receipt: [`receipts/2026-08-01-full-discovery-failure.md`](./receipts/2026-08-01-full-discovery-failure.md).

This disproves the former claim that Go 1.25 makes the complete upstream suite pass. It supports a narrower claim: Go 1.25 plus fixture and flag isolation makes the selected command-package tests pass in retained prior execution.

## Selected repair

Commit [`569c0c4d11e5a14f3fe6237c0a50dc484f80e744`](https://github.com/teamleaderleo/nixpkgs/commit/569c0c4d11e5a14f3fe6237c0a50dc484f80e744):

- changes `buildGoModule` to `buildGo125Module`;
- enables checks;
- removes `-mod=vendor` during checks;
- creates `.gomarkdoc-empty.yml`;
- retains `subPackages = [ "cmd/gomarkdoc" ]` for build and checks.

Unchanged:

- source and vendor hashes;
- command-only output;
- linker flags;
- version passthru;
- generic Go build/check implementation.

## Why broader repairs were rejected

- Skipping the two `lang` tests would weaken upstream coverage without maintainer policy.
- Patching exact expected prose would bind the package to current Go standard-library wording.
- Removing `subPackages` globally would widen installation.
- Replacing `checkPhase` would duplicate Nixpkgs Go-builder behavior.
- A shared-builder option would not solve the demonstrated language-test incompatibility.
- Updating gomarkdoc would introduce separate version, dependency, and hash scope.

## Compatibility and rollback

- Platform: retained older command runs passed Linux and Darwin; current exact-head rerun is queued.
- API/output: installed program and package interface are unchanged.
- Performance: package builds now execute selected command tests.
- Rollback: restore `buildGoModule` and `doCheck = false`; no data migration or generated state is involved.
- Future cleanup: update gomarkdoc or revisit the Go pin when upstream tests accommodate current Go documentation syntax.

## Current execution generation

- Carrier PR: [Fieldwork #437](https://github.com/teamleaderleo/fieldwork/pull/437)
- Carrier head: `c95da0c4b3f460df9bc8f342e98d05345da66df8`
- Source head: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`
- Command-check run: [`30690828310`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310)
- Integrity run: [`30690828341`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828341)
- State at this update: queued

Required controls are exact source/parent, one-file fence, `diff --check`, command-package result on Linux and Darwin, installed help, version `1.1.0`, Linux `nixpkgs-review`, artifacts, and Fieldwork integrity.

## Remaining uncertainty

- current exact-head command execution has not reached terminal state;
- independent review is pending;
- the source must be rebased onto a fresh public head and rerun before submission;
- Hydra, ofborg, and merge-queue evidence require a future authorized public PR;
- public-contact authority is absent.

Current disposition: `HOLD`.
