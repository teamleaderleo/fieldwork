# Tests and receipts — unit 22 gomarkdoc checks

## Test subject

- Target repository: `teamleaderleo/nixpkgs`
- Exact source base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Exact source head: [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- Source branch: `fieldwork/unit-22-gomarkdoc-checks`
- Changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Current execution carrier: [Fieldwork PR #437](https://github.com/teamleaderleo/fieldwork/pull/437)
- Carrier head: [`5c9d932276679836547b79a38aaf6b951dbdad02`](https://github.com/teamleaderleo/fieldwork/commit/5c9d932276679836547b79a38aaf6b951dbdad02)
- Current run: [30674476739](https://github.com/teamleaderleo/fieldwork/actions/runs/30674476739)

## Current status

`PENDING EXECUTION`

The renewed candidate has passed source-level fence checks through GitHub compare inspection. The pinned Linux/Darwin matrix is queued. This file must be updated from the exact terminal job logs before the packet leaves `REPAIR`.

## Superseded execution receipts

The prior Fieldwork candidate established several package-local compatibility facts. It failed to establish full test coverage.

### Exact old identities

- Old target base: [`bbbd95e512a066deaefa89e3a244b541ed6c8c7f`](https://github.com/NixOS/nixpkgs/commit/bbbd95e512a066deaefa89e3a244b541ed6c8c7f)
- Old patch head: [`1cdbcfa7bf07086ed9a46f440d3595595afdd241`](https://github.com/teamleaderleo/fieldwork/commit/1cdbcfa7bf07086ed9a46f440d3595595afdd241)
- Old workflow run: [30598626867](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867)

| Platform | Job ID | Result | Artifact ID | Established | Limit |
| --- | ---: | --- | ---: | --- | --- |
| x86_64-linux | `91056349644` | success | `8781532516` | Go 1.25 package build, command-package check, version `1.1.0` | only `cmd/gomarkdoc` ran |
| aarch64-darwin | `91056349617` | success | `8781695770` | Go 1.25 package build, command-package check, version `1.1.0` | only `cmd/gomarkdoc` ran |

### Exact old commands

```sh
nix-build .target/nixpkgs \
  -A gomarkdoc \
  --no-out-link

nix-build .target/nixpkgs \
  -A gomarkdoc.tests.version \
  --no-out-link
```

### Decisive old output

Both jobs reached `checkPhase` and emitted only:

```text
ok      github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

Both version passthru jobs emitted:

```text
1.1.0
```

### Correct interpretation

- `buildGo125Module` addressed the golden-output compatibility observed under newer Go behavior.
- removing `-mod=vendor` from test-time `GOFLAGS` addressed gomarkdoc's command flag parsing.
- creating `.gomarkdoc-empty.yml` supplied the empty fixture missing from the release tag.
- `subPackages = [ "cmd/gomarkdoc" ]` kept the generic check phase on one package, so the old “full suite” label is superseded.

## Renewed execution design

The workflow at [`5c9d9322`](https://github.com/teamleaderleo/fieldwork/blob/5c9d932276679836547b79a38aaf6b951dbdad02/.github/workflows/unit-22-gomarkdoc-checks.yml) uses two hosted runners:

| Runner | Nix platform label | Purpose |
| --- | --- | --- |
| `ubuntu-24.04` | `x86_64-linux` | native Linux package and version execution |
| `macos-14` | `aarch64-darwin` | native Darwin package and version execution |

### Source controls

Before installing Nix, each job asserts:

```sh
test "$(git -C .target/nixpkgs rev-parse HEAD)" = \
  "94be3956403ebf368b9d8262fdc9e5a5d2e80683"

test "$(git -C .target/nixpkgs rev-parse HEAD^)" = \
  "55096b0ce13784d4f6420059c5627475fa26ebb1"

test "$(git -C .target/nixpkgs diff --name-only HEAD^ HEAD)" = \
  "pkgs/by-name/go/gomarkdoc/package.nix"

git -C .target/nixpkgs diff --check HEAD^ HEAD
```

### Focused package gate

```sh
nix-build .target/nixpkgs \
  -A gomarkdoc \
  --no-out-link
```

The job then requires exact evidence for:

```text
github.com/princjef/gomarkdoc
github.com/princjef/gomarkdoc/lang
github.com/princjef/gomarkdoc/format/...
github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

It also requires at least four distinct gomarkdoc package result lines. This control catches the prior one-package false positive.

### Package passthru gate

```sh
nix-build .target/nixpkgs \
  -A gomarkdoc.tests.version \
  --no-out-link
```

The receipt must contain `1.1.0`.

### Receipt preservation

Each matrix job uploads:

- `source-diff.patch`
- full package build log
- normalized gomarkdoc package result list
- version passthru log

Retention: 30 days. Exact artifact IDs and digests belong in this file after execution.

## Result table — renewed candidate

| Platform | Job ID | Package build | Full-discovery controls | Version | Artifact | Current interpretation |
| --- | ---: | --- | --- | --- | --- | --- |
| x86_64-linux | pending | pending | pending | pending | pending | execution queued |
| aarch64-darwin | pending | pending | pending | pending | pending | execution queued |

## Ordinary target gates

| Gate | State | Receipt or blocker |
| --- | --- | --- |
| exact one-file compare | passed | [`55096b0c...94be3956`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683) |
| whitespace/error fence | prepared | executed inside run 30674476739 |
| native package build | pending | Linux and Darwin jobs queued |
| upstream package checks | pending | full-discovery assertions queued |
| version passthru | pending | Linux and Darwin jobs queued |
| `nixpkgs-review` | unexecuted | requires a later review pass; focused one-package native builds are the current executable gate |
| public Hydra and merge queue | unavailable in this unit | requires an authorized NixOS pull request |

## Failure classification

Use this order when reading a failed job:

1. **Source-fence failure** — wrong commit, parent, changed path, or malformed diff.
2. **Runner/setup failure** — checkout, Nix install, cache, disk, or hosted-runner issue before the derivation starts.
3. **Evaluation failure** — package expression or attribute resolution fails.
4. **Build failure** — gomarkdoc binary compilation fails before `checkPhase`.
5. **Product-test failure** — an upstream Go test fails during `checkPhase`.
6. **Coverage assertion failure** — build succeeds, yet required root/`lang`/format/command evidence is missing.
7. **Version-test failure** — package builds, while the passthru fails to report `1.1.0`.

Preserve the exact job log and artifact link for every failure. Repair source only for categories 3–7 when the evidence points to the candidate.

## Remaining test work

1. Let run 30674476739 reach terminal state.
2. Record both job IDs, conclusions, exact package result lines, version lines, artifact IDs, and artifact digests.
3. Run or explicitly defer `nixpkgs-review` with an exact reason.
4. Update `README.md`, `REVIEW.md`, `UPSTREAM_PR.md`, and the issue #435 handoff.
5. Close PR #437 after all receipts are durable in this packet.
