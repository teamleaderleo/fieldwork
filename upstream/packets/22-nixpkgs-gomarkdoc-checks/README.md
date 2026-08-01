# Unit 22 — gomarkdoc: restore checks without leaking Nix GOFLAGS

## In simple words

Nixpkgs packages `gomarkdoc` 1.1.0 with upstream tests disabled. The current expression says Nix's `-mod=vendor` reaches gomarkdoc's application flag parser. Source review and upstream issue #516481 narrow the observed failure: the unknown flag produces a diagnostic and returns no tags, while the missing empty config fixture and later Go golden divergence are the test blockers established by execution.

The retained Fieldwork candidate repaired the toolchain, `GOFLAGS`, and fixture concerns, yet its execution only tested `cmd/gomarkdoc`. Nixpkgs uses `subPackages = [ "cmd/gomarkdoc" ]` both for installation and generic check discovery. The earlier “full suite” claim is superseded.

The repaired candidate keeps the build selector, clears it inside `preCheck`, and lets the standard `buildGoModule` check phase discover every directory containing tests. It also keeps `-mod=vendor` out of gomarkdoc's application parser while retaining the materialized vendor tree and offline Go environment. A pinned Linux/Darwin execution carrier requires representative root, `lang`, format, command-package, and version results.

## Current disposition

`REPAIR`

Last verified: `2026-08-01`  
Worker: `OpenAI`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

Clearing condition: execution carrier [Fieldwork PR #437](https://github.com/teamleaderleo/fieldwork/pull/437) completes on x86_64-linux and aarch64-darwin with root, `lang`, format, `cmd/gomarkdoc`, and version controls all observed.

## Contribution

- Target project: [`NixOS/nixpkgs`](https://github.com/NixOS/nixpkgs)
- Proposed upstream destination: `NixOS/nixpkgs:master`
- Proposed title: `gomarkdoc: restore full upstream checks`
- Contribution synopsis: switch gomarkdoc 1.1.0 to `buildGo125Module`, enable checks, remove only `-mod=vendor` from test-time `GOFLAGS`, recreate the omitted empty config fixture, and clear the build-only package selector during check discovery.
- Work class: `upstream-fork research`

## Exact identities

- Public upstream base inspected: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Newer public head checked for staleness: [`f8e81fc7eb063db454f563cdd596fb96a5ad1497`](https://github.com/NixOS/nixpkgs/commit/f8e81fc7eb063db454f563cdd596fb96a5ad1497); relevant package and builder blobs are unchanged
- Owned target fork: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Canonical source branch: [`fieldwork/unit-22-gomarkdoc-checks`](https://github.com/teamleaderleo/nixpkgs/tree/fieldwork/unit-22-gomarkdoc-checks)
- Canonical source head: [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- Source compare: [`55096b0c...94be3956`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- Fieldwork packet branch: [`p0/435-unit-22-nixpkgs-gomarkdoc-checks`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-22-nixpkgs-gomarkdoc-checks/upstream/packets/22-nixpkgs-gomarkdoc-checks)
- Packet base: [`920f87cb25dd0cc7901d59ea2019cd4b4a193b94`](https://github.com/teamleaderleo/fieldwork/commit/920f87cb25dd0cc7901d59ea2019cd4b4a193b94)
- Exact packet head: recorded in the final unit-22 handoff on [Fieldwork issue #435](https://github.com/teamleaderleo/fieldwork/issues/435); the branch tip is canonical
- Execution carrier: [Fieldwork PR #437](https://github.com/teamleaderleo/fieldwork/pull/437), workflow head [`5c9d932276679836547b79a38aaf6b951dbdad02`](https://github.com/teamleaderleo/fieldwork/commit/5c9d932276679836547b79a38aaf6b951dbdad02), run [`30674476739`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674476739)
- Superseded source evidence: Fieldwork issue [#241](https://github.com/teamleaderleo/fieldwork/issues/241), PR [#265](https://github.com/teamleaderleo/fieldwork/pull/265), final retained head [`d559a9756294b94c7a8ee4e68cae6ed603352986`](https://github.com/teamleaderleo/fieldwork/commit/d559a9756294b94c7a8ee4e68cae6ed603352986), execution patch head [`1cdbcfa7bf07086ed9a46f440d3595595afdd241`](https://github.com/teamleaderleo/fieldwork/commit/1cdbcfa7bf07086ed9a46f440d3595595afdd241)

## Current code and tests

### Product code

- [`pkgs/by-name/go/gomarkdoc/package.nix`](https://github.com/teamleaderleo/nixpkgs/blob/94be3956403ebf368b9d8262fdc9e5a5d2e80683/pkgs/by-name/go/gomarkdoc/package.nix) — the complete one-file candidate.
- [`patches/0001-gomarkdoc-restore-full-upstream-checks.patch`](./patches/0001-gomarkdoc-restore-full-upstream-checks.patch) — retained mailbox-style patch for continuation or rebasing.

### Target-native tests

- `nix-build . -A gomarkdoc --no-out-link`
- `nix-build . -A gomarkdoc.tests.version --no-out-link`
- Execution carrier assertions require observed result lines for:
  - `github.com/princjef/gomarkdoc`
  - `github.com/princjef/gomarkdoc/lang`
  - at least one `github.com/princjef/gomarkdoc/format/...` package
  - `github.com/princjef/gomarkdoc/cmd/gomarkdoc`
  - version output `1.1.0`

### Required generated or dependency files

None. The source hash and vendor hash remain unchanged.

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `pkgs/by-name/go/gomarkdoc/package.nix` | package definition and check repair | yes |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Current Nixpkgs still disables gomarkdoc tests | source-read | [package at `f8e81fc7`](https://github.com/NixOS/nixpkgs/blob/f8e81fc7eb063db454f563cdd596fb96a5ad1497/pkgs/by-name/go/gomarkdoc/package.nix) | snapshot from 2026-08-01 |
| Generic Go checks call `preCheck` before `getGoDirs test`, and nonempty `subPackages` wins | source-read | [`module.nix` at `f8e81fc7`](https://github.com/NixOS/nixpkgs/blob/f8e81fc7eb063db454f563cdd596fb96a5ad1497/pkgs/build-support/go/module.nix) | depends on this exact builder revision |
| The missing empty fixture is an observed upstream failure | source-read and public prior art | [Nixpkgs issue #516481](https://github.com/NixOS/nixpkgs/issues/516481) and [v1.1.0 command test](https://github.com/princjef/gomarkdoc/blob/v1.1.0/cmd/gomarkdoc/command_test.go) | exact version and reported regression window |
| Unknown `GOFLAGS` tokens produce a diagnostic and return no tags | source-read | [`defaultTags()` v1.1.0](https://github.com/princjef/gomarkdoc/blob/v1.1.0/cmd/gomarkdoc/command.go) | removal is semantic isolation, not a separately proven failure blocker |
| Old candidate built and ran the command-package test on Linux and Darwin | target-executed | [run 30598626867](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867) | only `cmd/gomarkdoc` ran |
| Old candidate passed the version passthru on Linux and Darwin | target-executed | [run 30598626867](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867) | tied to old target base `bbbd95e5` |
| Repaired candidate is a one-file commit directly above the inspected base | source-read | [compare](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683) | execution pending |
| Repaired candidate runs the intended package set on Linux and Darwin | target-test-prepared | [PR #437 checks](https://github.com/teamleaderleo/fieldwork/pull/437/checks) | jobs `91298756809` and `91298756825` remain queued |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue route](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issue: [#516481 — gomarkdoc 1.1.0 checkPhase regressed](https://github.com/NixOS/nixpkgs/issues/516481)
- Relevant upstream pull requests:
  - [#279440 — gomarkdoc: init at 1.1.0](https://github.com/NixOS/nixpkgs/pull/279440)
  - [#516792 — gomarkdoc: disable tests](https://github.com/NixOS/nixpkgs/pull/516792)
- Equivalent restoration found: `no`
- Relationship to prior work: proposed source repair for the open regression report and the containment introduced by #516792.

## Data-quality observation

Fieldwork issue #241 labels [`teamleaderleo/fieldwork#11`](https://github.com/teamleaderleo/fieldwork/issues/11) as the Nixpkgs target hub. Issue #11 is the DuckDB target record. This packet records the mismatch and leaves other units untouched.

## Remaining work

Complete in this order:

1. Read PR #437 job logs and transfer exact run, job, package-result, version, and artifact links into `TESTS.md`.
2. Update this packet and `REVIEW.md` to one final disposition.
3. Close the temporary execution carrier after receipt transfer.
4. Obtain independent complete-diff review.
5. Seek explicit authority before any public upstream action.

## Blockers and limits

- Run `30674476739` and jobs `91298756809` / `91298756825` remain queued.
- This runtime has no `nix-build` or `nix` executable, and its attempt to download the official Nix 2.35.1 installer failed, so it cannot replace the hosted execution.
- Public upstream contact authority is absent.
- Full Nixpkgs merge-queue/Hydra execution requires a future authorized upstream PR.
- `nixpkgs-review` has yet to run for the repaired source head.
- AI/contribution disclosure requirements require a final human recheck at submission time; no explicit repository-wide AI disclosure text was located in the inspected contribution files.

## Latest handoff

State: `REPAIR`  
Exact source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`  
Exact packet head: see final unit-22 comment on issue #435  
Tests: old partial Linux/Darwin receipts retained; repaired full-discovery matrix queued in PR #437  
Temporary machinery remaining: branch `p0/435-unit-22-execution`, workflow `.github/workflows/unit-22-gomarkdoc-checks.yml`, PR #437  
Next worker action: inspect PR #437 once both jobs reach a terminal state and transfer the receipts  
Public upstream interaction: none
