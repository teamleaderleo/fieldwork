# Tests and receipts — unit 22 gomarkdoc checks

## In simple words

Two retained Linux/Darwin executions prove that the old Go 1.25 candidate built, ran `cmd/gomarkdoc`, and passed the version passthru. Their logs also prove the coverage defect: only the command package ran.

The clean source adds `subPackages=()` before test discovery. Active run `30674969557` requires root, `lang`, format, command, installed-binary help, version, and Linux `nixpkgs-review` evidence. Both platform jobs and Fieldwork integrity remain queued. Full clean-head coverage therefore remains `target-test-prepared`.

Current packet disposition: `HOLD`.

## Canonical source fence

- Repository: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Branch: `fieldwork/unit-22-gomarkdoc-checks`
- Base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Head: [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- Changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Compare: [`55096b0c...94be3956`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- Newer public head checked: [`f8e81fc7eb063db454f563cdd596fb96a5ad1497`](https://github.com/NixOS/nixpkgs/commit/f8e81fc7eb063db454f563cdd596fb96a5ad1497), 9 commits ahead of the source base with no relevant-path overlap

## Source and prior-art checks executed

### Nixpkgs package and builder

Read at the source base and the later public head:

- `pkgs/by-name/go/gomarkdoc/package.nix`
- `pkgs/build-support/go/module.nix`

Results:

- package still has `subPackages = [ "cmd/gomarkdoc" ]` and `doCheck = false`;
- builder invokes `preCheck` before `getGoDirs test`;
- nonempty `subPackages` overrides test discovery;
- the relevant package and builder behavior remained unchanged across the checked public advance.

Evidence class: `source-read`.

### gomarkdoc v1.1.0

Read:

- `go.mod`;
- `cmd/gomarkdoc/command.go`;
- `cmd/gomarkdoc/command_test.go`;
- representative root, `lang`, `format`, and command test files.

Results:

- module declares Go 1.18;
- `defaultTags()` reads `GOFLAGS`, accepts only `-tags`, emits a diagnostic on other flags, and returns `nil`;
- command tests reference `../.gomarkdoc-empty.yml` after changing into `testData`;
- tests exist in the root, `lang`, format packages, and `cmd/gomarkdoc`.

Evidence class: `source-read`.

### Public issue and PR history

Read:

- open issue [#516481](https://github.com/NixOS/nixpkgs/issues/516481);
- release-campaign issue [#516381](https://github.com/NixOS/nixpkgs/issues/516381);
- introduction PR [#279440](https://github.com/NixOS/nixpkgs/pull/279440) and its review discussion;
- containment PR [#516792](https://github.com/NixOS/nixpkgs/pull/516792), comments, `nixpkgs-review` receipt, and linked release context.

Results:

- #516481 reproduces the missing empty fixture and calls unknown-flag output benign;
- #516792 disables checks and built gomarkdoc on four platforms through `nixpkgs-review` after containment;
- no equivalent restoration PR was found on 2026-08-01.

Evidence class: `source-read` / `prior-art`.

## Retained old execution A

- Old Nixpkgs base: [`bbbd95e512a066deaefa89e3a244b541ed6c8c7f`](https://github.com/NixOS/nixpkgs/commit/bbbd95e512a066deaefa89e3a244b541ed6c8c7f)
- Patch head: [`1cdbcfa7bf07086ed9a46f440d3595595afdd241`](https://github.com/teamleaderleo/fieldwork/commit/1cdbcfa7bf07086ed9a46f440d3595595afdd241)
- Run: [`30598626867`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867)

| Platform | Job | Conclusion | Artifact | Established | Limit |
| --- | ---: | --- | ---: | --- | --- |
| x86_64-linux | `91056349644` | success | `8781532516` | package build, command-package test, version `1.1.0` | one test package |
| aarch64-darwin | `91056349617` | success | `8781695770` | package build, command-package test, version `1.1.0` | one test package |

## Retained old execution B

- Carrier head: [`19931964ec50d687025d5cc7953b9c29eab7b395`](https://github.com/teamleaderleo/fieldwork/commit/19931964ec50d687025d5cc7953b9c29eab7b395)
- Patch generation: [`1cdbcfa7bf07086ed9a46f440d3595595afdd241`](https://github.com/teamleaderleo/fieldwork/commit/1cdbcfa7bf07086ed9a46f440d3595595afdd241)
- Run: [`30598687251`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251)

| Platform | Job | Conclusion | Artifact | Digest | Expiry |
| --- | ---: | --- | ---: | --- | --- |
| x86_64-linux | `91056528367` | success | [`8781677778`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251/artifacts/8781677778) | `sha256:7016240f3caaa54af84d0d277ca5dd69a5d05cadcca20fa1c50cd42dbaedd11c` | 2026-08-30 |
| aarch64-darwin | `91056528347` | success | [`8781795710`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251/artifacts/8781795710) | `sha256:a24bbf13b9c0fccacaecad8c8a17d0c244fb6580393a0266ec704522f686957c` | 2026-08-30 |

### Old commands

```bash
git -C .target/nixpkgs apply \
  "$GITHUB_WORKSPACE/programmes/open-source-ecosystems/experiments/nixpkgs-gomarkdoc-check-restoration/gomarkdoc.patch"

git -C .target/nixpkgs diff --check

nix-build .target/nixpkgs -A gomarkdoc --no-out-link \
  2>&1 | tee "gomarkdoc-${system}.log"

nix-build .target/nixpkgs -A gomarkdoc.tests.version --no-out-link \
  2>&1 | tee "gomarkdoc-version-${system}.log"
```

### Old decisive output

Both retained executions emitted only:

```text
Running phase: checkPhase
ok      github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

Version output:

```text
1.1.0
```

Accurate retained statement:

> The Go 1.25 candidate built and passed `cmd/gomarkdoc` plus the version passthru on x86_64-linux and aarch64-darwin.

Retired statement:

> The full discovered gomarkdoc suite passed.

## Active execution carrier

- Branch: [`p0/435-unit-22-execution`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-22-execution)
- PR: [#437](https://github.com/teamleaderleo/fieldwork/pull/437)
- Head: [`b6003f2a3523f01880ff5690798b69afcb4e11f5`](https://github.com/teamleaderleo/fieldwork/commit/b6003f2a3523f01880ff5690798b69afcb4e11f5)
- Workflow: [`.github/workflows/unit-22-gomarkdoc-checks.yml`](https://github.com/teamleaderleo/fieldwork/blob/b6003f2a3523f01880ff5690798b69afcb4e11f5/.github/workflows/unit-22-gomarkdoc-checks.yml)
- Target run: [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557)
- Linux job: `91300175276`
- Darwin job: `91300175296`
- Fieldwork integrity run: [`30674969559`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969559)
- Superseded active-run generation: head `5c9d932276679836547b79a38aaf6b951dbdad02`, run `30674476739`, jobs `91298756809` / `91298756825`

### Exact source controls

```bash
test "$(git -C .target/nixpkgs rev-parse HEAD)" = \
  "94be3956403ebf368b9d8262fdc9e5a5d2e80683"

test "$(git -C .target/nixpkgs rev-parse HEAD^)" = \
  "55096b0ce13784d4f6420059c5627475fa26ebb1"

test "$(git -C .target/nixpkgs diff --name-only HEAD^ HEAD)" = \
  "pkgs/by-name/go/gomarkdoc/package.nix"

git -C .target/nixpkgs diff --check HEAD^ HEAD
```

### Target commands

```bash
nix-build .target/nixpkgs -A gomarkdoc --no-out-link
nix-build .target/nixpkgs -A gomarkdoc.tests.version --no-out-link
nixpkgs-review rev HEAD --no-shell  # Linux
```

The workflow also executes the installed `gomarkdoc --help` path.

### Required assertions

Each platform must show:

```text
Running phase: checkPhase
ok github.com/princjef/gomarkdoc
ok github.com/princjef/gomarkdoc/lang
ok github.com/princjef/gomarkdoc/format/...
ok github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

Additional controls:

- at least four distinct gomarkdoc package result lines;
- executable installed `bin/gomarkdoc`;
- help/usage output;
- version output `1.1.0`;
- Linux terminal `nixpkgs-review` report;
- retained source diff and logs.

### Current state

| Item | State | Conclusion | Evidence class |
| --- | --- | --- | --- |
| Linux job `91300175276` | queued | none | `target-test-prepared` |
| Darwin job `91300175296` | queued | none | `target-test-prepared` |
| target run `30674969557` | queued | none | execution blocker |
| Fieldwork integrity `30674969559` | queued | none | repository-gate blocker |
| current artifacts | absent | jobs have not started | none |

## Runtime execution attempt

- `nix` and `nix-build` are absent from the active runtime.
- An attempt retained in packet history to download the official Nix 2.35.1 installer failed.
- No local target-native Nix command ran.

Classification: `setup capability blocker`, not package evidence.

## Gates outside the active receipt

- Hydra: requires authorized public Nixpkgs PR
- ofborg / merge queue: requires authorized public Nixpkgs PR
- independent complete-diff review: pending after terminal receipt transfer
- fresh-head rebase and exact-head rerun: required before authorized submission

## Required continuation receipt

After terminal execution, preserve:

1. run, job, and step conclusions;
2. runner image and platform;
3. checked-out source head and parent;
4. changed-file list and `diff --check` result;
5. complete gomarkdoc package result list;
6. root, `lang`, format, and command assertions;
7. installed-binary help result;
8. version output;
9. Linux `nixpkgs-review` report;
10. artifact IDs, sizes, digests, and expiry;
11. setup, product, assertion, and repository-gate failures separately;
12. exact packet head consuming the receipt.

## Current test conclusion

The clean source and discriminating gates are prepared. Old compatibility evidence is retained with its one-package limit. Full restored coverage at source head `94be3956403ebf368b9d8262fdc9e5a5d2e80683` remains unexecuted because target run `30674969557` and integrity run `30674969559` are queued. This is the exact blocker behind disposition `HOLD`.
