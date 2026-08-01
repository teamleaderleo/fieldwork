# Unit 22 — gomarkdoc: restore checks without leaking Nix GOFLAGS

## In simple words

Nixpkgs packages `gomarkdoc` 1.1.0 with its upstream checks disabled. Public issue #516481 records the missing empty config fixture as the observed test failure; the unknown `GOFLAGS` token produces a diagnostic and returns no tags. Retained Fieldwork execution also found a Go 1.26 documentation-golden difference.

The earlier Fieldwork repair handled the Go version, test-time `GOFLAGS`, and fixture, yet it exercised only `cmd/gomarkdoc`. Nixpkgs uses `subPackages = [ "cmd/gomarkdoc" ]` for both binary build selection and generic check discovery, so the old “full suite” claim is superseded.

The clean candidate preserves the narrow binary install, clears `subPackages` only inside `preCheck`, and lets the standard Go builder discover every package containing tests. The source is complete. Hosted Linux, Darwin, `nixpkgs-review`, binary-help, and final Fieldwork-integrity jobs remain queued.

## Current disposition

`HOLD`

Last verified: `2026-08-01`  
Worker: `OpenAI`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

Clearing condition: [Fieldwork PR #437](https://github.com/teamleaderleo/fieldwork/pull/437) run [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557) reaches terminal state with the intended controls on both platforms, run [`30674969559`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969559) supplies current packet-integrity evidence, all receipts are transferred here, and the carrier is closed.

## Contribution

- Target project: [`NixOS/nixpkgs`](https://github.com/NixOS/nixpkgs)
- Proposed destination: `NixOS/nixpkgs:master`
- Proposed title: `gomarkdoc: restore full upstream checks`
- Work class: `upstream-fork research`
- Synopsis: use `buildGo125Module`, enable checks, keep Nix's `-mod=vendor` out of gomarkdoc's application parser during tests, recreate the omitted empty fixture, and clear the build-only package selector before standard check discovery.

## Exact identities

### Clean target source

- Owned fork: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Branch: [`fieldwork/unit-22-gomarkdoc-checks`](https://github.com/teamleaderleo/nixpkgs/tree/fieldwork/unit-22-gomarkdoc-checks)
- Base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Head: [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- Compare: [`55096b0c...94be3956`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- Changed file: [`pkgs/by-name/go/gomarkdoc/package.nix`](https://github.com/teamleaderleo/nixpkgs/blob/94be3956403ebf368b9d8262fdc9e5a5d2e80683/pkgs/by-name/go/gomarkdoc/package.nix)

### Current-main relation

- Newer public `master` checked: [`f8e81fc7eb063db454f563cdd596fb96a5ad1497`](https://github.com/NixOS/nixpkgs/commit/f8e81fc7eb063db454f563cdd596fb96a5ad1497)
- Distance from inspected base: 9 commits ahead
- Relevant-path overlap: none in `package.nix` or the reviewed Go-builder behavior
- Submission action: rebase onto a fresh public head and rerun exact-head gates before authorized upstream posting

### Fieldwork packet

- Path: `upstream/packets/22-nixpkgs-gomarkdoc-checks/`
- Branch: [`p0/435-unit-22-nixpkgs-gomarkdoc-checks`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-22-nixpkgs-gomarkdoc-checks/upstream/packets/22-nixpkgs-gomarkdoc-checks)
- Base: [`920f87cb25dd0cc7901d59ea2019cd4b4a193b94`](https://github.com/teamleaderleo/fieldwork/commit/920f87cb25dd0cc7901d59ea2019cd4b4a193b94)
- Exact packet head: recorded in the final unit-22 comment on [issue #435](https://github.com/teamleaderleo/fieldwork/issues/435); the branch tip is canonical

### Active execution carrier

- PR: [Fieldwork #437](https://github.com/teamleaderleo/fieldwork/pull/437)
- Carrier branch: `p0/435-unit-22-execution`
- Carrier head: [`b6003f2a3523f01880ff5690798b69afcb4e11f5`](https://github.com/teamleaderleo/fieldwork/commit/b6003f2a3523f01880ff5690798b69afcb4e11f5)
- Target run: [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557)
- Linux job: `91300175276`
- Darwin job: `91300175296`
- Fieldwork integrity run: [`30674969559`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969559)
- Superseded carrier head/run: `5c9d932276679836547b79a38aaf6b951dbdad02` / `30674476739`

### Superseded retained candidate

- Fieldwork issue: [#241](https://github.com/teamleaderleo/fieldwork/issues/241)
- Fieldwork PR: [#265](https://github.com/teamleaderleo/fieldwork/pull/265)
- Retained head: [`d559a9756294b94c7a8ee4e68cae6ed603352986`](https://github.com/teamleaderleo/fieldwork/commit/d559a9756294b94c7a8ee4e68cae6ed603352986)
- Execution patch head: [`1cdbcfa7bf07086ed9a46f440d3595595afdd241`](https://github.com/teamleaderleo/fieldwork/commit/1cdbcfa7bf07086ed9a46f440d3595595afdd241)
- Run: [`30598626867`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867)

## Code and retained patch

- Exact source file: [`package.nix`](https://github.com/teamleaderleo/nixpkgs/blob/94be3956403ebf368b9d8262fdc9e5a5d2e80683/pkgs/by-name/go/gomarkdoc/package.nix)
- Retained patch: [`patches/0001-gomarkdoc-restore-full-upstream-checks.patch`](./patches/0001-gomarkdoc-restore-full-upstream-checks.patch)
- Source/vendor hashes: unchanged
- Generated or lock files: none

## Changed-file fence

| Path | Role | Upstream candidate |
| --- | --- | --- |
| `pkgs/by-name/go/gomarkdoc/package.nix` | package definition and check repair | yes |

## Intended gates

```sh
nix-build . -A gomarkdoc --no-out-link
nix-build . -A gomarkdoc.tests.version --no-out-link
nixpkgs-review rev HEAD --no-shell
```

The active carrier also executes the installed binary's help path and requires result lines for:

- `github.com/princjef/gomarkdoc`
- `github.com/princjef/gomarkdoc/lang`
- at least one `github.com/princjef/gomarkdoc/format/...` package
- `github.com/princjef/gomarkdoc/cmd/gomarkdoc`
- at least four distinct gomarkdoc package result lines
- version output `1.1.0`

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Nixpkgs still disables gomarkdoc checks | `source-read` | [package at `f8e81fc7`](https://github.com/NixOS/nixpkgs/blob/f8e81fc7eb063db454f563cdd596fb96a5ad1497/pkgs/by-name/go/gomarkdoc/package.nix) | 2026-08-01 snapshot |
| `preCheck` runs before `getGoDirs test`; nonempty `subPackages` wins | `source-read` | [`module.nix` at `f8e81fc7`](https://github.com/NixOS/nixpkgs/blob/f8e81fc7eb063db454f563cdd596fb96a5ad1497/pkgs/build-support/go/module.nix) | exact builder revision |
| Missing empty fixture is an observed public failure | `source-read` / public prior art | [Nixpkgs issue #516481](https://github.com/NixOS/nixpkgs/issues/516481) | Linux reproduction from May 2026 |
| Unknown `GOFLAGS` token emits a diagnostic and yields no tags | `source-read` | [`defaultTags()` v1.1.0](https://github.com/princjef/gomarkdoc/blob/v1.1.0/cmd/gomarkdoc/command.go) | diagnostic alone is not proven to fail the suite |
| Old candidate built on Linux and Darwin, ran command-package checks, and reported version `1.1.0` | `target-executed` | [run 30598626867](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867) | only `cmd/gomarkdoc` ran |
| Clean repair is one commit and one file | `source-read` | [source compare](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683) | full execution pending |
| Full intended package set passes on Linux/Darwin | `target-test-prepared` | [PR #437 checks](https://github.com/teamleaderleo/fieldwork/pull/437/checks) | jobs remain queued |

## Duplicate and prior art

Search date: `2026-08-01`

- [#516481 — gomarkdoc 1.1.0 checkPhase regressed](https://github.com/NixOS/nixpkgs/issues/516481)
- [#516792 — gomarkdoc: disable tests](https://github.com/NixOS/nixpkgs/pull/516792)
- [#516381 — NixOS 26.05 Zero Hydra Failures](https://github.com/NixOS/nixpkgs/issues/516381), release campaign context linked from the disablement
- [#279440 — gomarkdoc: init at 1.1.0](https://github.com/NixOS/nixpkgs/pull/279440)
- Equivalent restoration PR found: `no`

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue route](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Data-quality observation

Fieldwork issue #241 labels [`teamleaderleo/fieldwork#11`](https://github.com/teamleaderleo/fieldwork/issues/11) as the Nixpkgs target hub. Issue #11 describes DuckDB. This packet records the mismatch and leaves every other unit untouched.

## Remaining work, in order

1. Let runs `30674969557` and `30674969559` reach terminal state.
2. Transfer exact job conclusions, package lines, help output, version output, `nixpkgs-review` report, artifact IDs/digests, and integrity result into this packet.
3. Repair source or harness only when terminal logs identify a concrete defect.
4. Close PR #437 after receipt transfer.
5. Obtain independent complete-diff review.
6. Rebase onto a fresh public Nixpkgs head and rerun exact-head gates before any authorized submission.
7. Seek explicit authority for public upstream interaction.

## Blockers and limits

- Target run `30674969557`, jobs `91300175276` and `91300175296`, and integrity run `30674969559` remain queued.
- The available runtime has no `nix` or `nix-build`; its attempt to retrieve the official Nix 2.35.1 installer failed, so it cannot replace hosted execution.
- GitHub's public status showed Actions operational during the queue; repository/account workload remains the observable execution dependency.
- Public upstream contact authority is absent.
- Hydra, ofborg, and merge-queue evidence require a future authorized NixOS pull request.
- Final independent acceptance remains required.

## Latest handoff

State: `HOLD`  
Exact source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`  
Exact packet head: see the final unit-22 comment on issue #435  
Tests executed: old partial Linux/Darwin run `30598626867`; clean-candidate run `30674969557` and integrity run `30674969559` are queued  
Temporary machinery: active carrier branch `p0/435-unit-22-execution`, workflow `.github/workflows/unit-22-gomarkdoc-checks.yml`, PR #437  
Next action: read terminal PR #437 receipts, update packet status, and close the carrier  
Public upstream interaction: none
