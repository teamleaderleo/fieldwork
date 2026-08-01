# Tests and receipts — unit 22 gomarkdoc checks

## In simple words

The old Go 1.25 candidate built and passed on Linux and Darwin, but its logs prove that only `cmd/gomarkdoc` ran. Those receipts remain useful for toolchain, fixture, vendor-backed build, command-package, and version behavior. They do not support full-suite coverage.

The repaired source adds `subPackages=()` before test discovery. A new pinned matrix requires root, `lang`, format, command, and version results on both platforms. That run remains queued, so the current evidence class for full discovery is `target-test-prepared`.

## Canonical source fence

- Source repository: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Head: [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- Branch: `fieldwork/unit-22-gomarkdoc-checks`
- Complete changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Compare: [`55096b0c...94be3956`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683)

## Source and prior-art checks executed during packet renewal

### Current package and builder read

Read at both the candidate base and later public head [`f8e81fc7eb063db454f563cdd596fb96a5ad1497`](https://github.com/NixOS/nixpkgs/commit/f8e81fc7eb063db454f563cdd596fb96a5ad1497):

- `pkgs/by-name/go/gomarkdoc/package.nix`;
- `pkgs/build-support/go/module.nix`.

Result:

- package still has `subPackages = [ "cmd/gomarkdoc" ]` and `doCheck = false`;
- builder invokes `preCheck` before `getGoDirs test`;
- nonempty `subPackages` overrides discovery;
- package and builder blob SHAs are unchanged between the candidate base and checked later head.

Evidence class: `source-read`.

### gomarkdoc v1.1.0 source read

Read:

- `go.mod`;
- `cmd/gomarkdoc/command.go`;
- `cmd/gomarkdoc/command_test.go`;
- representative root, `lang`, and format test paths.

Result:

- module declares Go 1.18;
- `defaultTags()` reads `GOFLAGS`, accepts only `-tags`, and returns `nil` after parse error;
- command tests reference `../.gomarkdoc-empty.yml` after changing into `testData`;
- tests exist outside `cmd/gomarkdoc`.

Evidence class: `source-read`.

### Current public issue and PR search

Read:

- open issue [Nixpkgs #516481](https://github.com/NixOS/nixpkgs/issues/516481);
- merged introduction PR [#279440](https://github.com/NixOS/nixpkgs/pull/279440);
- merged containment PR [#516792](https://github.com/NixOS/nixpkgs/pull/516792).

Result:

- #516481 reproduces the missing empty fixture and calls unknown-flag output benign;
- #516792 disables checks;
- no equivalent restoration PR was found.

Evidence class: `source-read` and `prior-art`.

## Retained old execution

### Exact old identities

- Fieldwork carrier head: [`19931964ec50d687025d5cc7953b9c29eab7b395`](https://github.com/teamleaderleo/fieldwork/commit/19931964ec50d687025d5cc7953b9c29eab7b395)
- Patch generation: [`1cdbcfa7bf07086ed9a46f440d3595595afdd241`](https://github.com/teamleaderleo/fieldwork/commit/1cdbcfa7bf07086ed9a46f440d3595595afdd241)
- Old Nixpkgs source: [`bbbd95e512a066deaefa89e3a244b541ed6c8c7f`](https://github.com/NixOS/nixpkgs/commit/bbbd95e512a066deaefa89e3a244b541ed6c8c7f)
- Workflow run: [`30598687251`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251)
- x86_64-linux job: `91056528367`
- aarch64-darwin job: `91056528347`

### Old artifacts

| Platform | Artifact ID | Digest | Expiry |
| --- | ---: | --- | --- |
| x86_64-linux | [`8781677778`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251/artifacts/8781677778) | `sha256:7016240f3caaa54af84d0d277ca5dd69a5d05cadcca20fa1c50cd42dbaedd11c` | 2026-08-30 |
| aarch64-darwin | [`8781795710`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251/artifacts/8781795710) | `sha256:a24bbf13b9c0fccacaecad8c8a17d0c244fb6580393a0266ec704522f686957c` | 2026-08-30 |

### Commands

```bash
git -C .target/nixpkgs apply \
  "$GITHUB_WORKSPACE/programmes/open-source-ecosystems/experiments/nixpkgs-gomarkdoc-check-restoration/gomarkdoc.patch"

git -C .target/nixpkgs diff --check

nix-build .target/nixpkgs \
  -A gomarkdoc \
  --no-out-link \
  2>&1 | tee "gomarkdoc-${system}.log"

nix-build .target/nixpkgs \
  -A gomarkdoc.tests.version \
  --no-out-link \
  2>&1 | tee "gomarkdoc-version-${system}.log"
```

### Old results

Both jobs completed successfully. Linux used Go 1.25.12 and a materialized `gomarkdoc-1.1.0-go-modules` path. The package entered `checkPhase`, printed:

```text
ok      github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

and the version passthru printed:

```text
1.1.0
```

Darwin produced the same single command-package result and version output.

Evidence class: `target-executed` for package build, command-package checks, vendor-backed setup, and version behavior at the old source fence.

Coverage limit: exactly one test package ran.

## Superseded old claim

Fieldwork issue #241 and PR #265 originally described run `30598687251` as full discovered coverage. Their later correction establishes that `subPackages` narrowed the check phase. The following claim is retired:

> the full discovered gomarkdoc test set passed

The accurate retained statement is:

> `cmd/gomarkdoc` and the version passthru passed on x86_64-linux and aarch64-darwin under the old Go 1.25 candidate.

## Current execution carrier

- Fieldwork branch: [`p0/435-unit-22-execution`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-22-execution)
- Workflow head: [`5c9d932276679836547b79a38aaf6b951dbdad02`](https://github.com/teamleaderleo/fieldwork/commit/5c9d932276679836547b79a38aaf6b951dbdad02)
- Draft PR: [#437](https://github.com/teamleaderleo/fieldwork/pull/437)
- Workflow: [`.github/workflows/unit-22-gomarkdoc-checks.yml`](https://github.com/teamleaderleo/fieldwork/blob/5c9d932276679836547b79a38aaf6b951dbdad02/.github/workflows/unit-22-gomarkdoc-checks.yml)
- Run: [`30674476739`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674476739)
- Linux job: `91298756809`
- Darwin job: `91298756825`

### Current exact commands

```bash
nix-build .target/nixpkgs \
  -A gomarkdoc \
  --no-out-link \
  2>&1 | tee "gomarkdoc-${system}.log"

nix-build .target/nixpkgs \
  -A gomarkdoc.tests.version \
  --no-out-link \
  2>&1 | tee "gomarkdoc-version-${system}.log"
```

### Current assertions

For each platform, the workflow requires:

```text
Running phase: checkPhase
ok github.com/princjef/gomarkdoc
ok github.com/princjef/gomarkdoc/lang
ok github.com/princjef/gomarkdoc/format/...
ok github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

It also captures all `ok` or `?` gomarkdoc package lines, requires at least four distinct results, and requires version output `1.1.0`.

### Current state

| Job | State | Conclusion | Evidence class |
| --- | --- | --- | --- |
| `91298756809` x86_64-linux | queued | none | `target-test-prepared` |
| `91298756825` aarch64-darwin | queued | none | `target-test-prepared` |
| run `30674476739` | queued | none | execution blocker |
| Fieldwork integrity run `30674476689` | queued | none | repository-gate blocker |

No current artifacts exist because the jobs have not started.

## Local execution attempt

The active runtime was checked for `nix` and `nix-build`; neither executable is present. An attempt to download the official Nix 2.35.1 installer failed in the runtime. No target-native local command ran.

Classification: `setup capability blocker`, not package evidence.

## Required continuation receipt

After both current jobs reach a terminal state, preserve:

1. run and job conclusions;
2. runner image and platform;
3. exact checked-out source head and parent;
4. exact changed-file list and `diff --check` result;
5. full gomarkdoc package result list;
6. root, `lang`, format, and command assertions;
7. version output;
8. artifact IDs, sizes, digests, and expiry;
9. any setup, product, or assertion failure separately;
10. the updated packet head consuming the receipt.

## Gates outside current execution

- `nixpkgs-review`: unexecuted for source head `94be3956...`
- Hydra: requires an authorized public Nixpkgs PR
- ofborg / merge queue: requires an authorized public Nixpkgs PR
- independent complete-diff review: pending after current receipt transfer

## Current test conclusion

The source repair is prepared and the old partial compatibility evidence is retained. Full restored check coverage at the clean source head remains unexecuted because the current Linux and Darwin jobs are queued. This is the exact blocker behind disposition `REPAIR`.
