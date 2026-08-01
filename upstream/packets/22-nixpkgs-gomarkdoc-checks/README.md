# Unit 22 — gomarkdoc: restore checks without leaking Nix GOFLAGS

## In simple words

Nixpkgs packages `gomarkdoc` 1.1.0 with checks disabled. The package builds only `cmd/gomarkdoc`, and Nixpkgs' Go builder uses that same `subPackages` selection during `checkPhase`.

A renewed experiment cleared the selector to run every upstream package. Exact-head Linux and Darwin execution reached the root, command, and formatter tests, then failed the same two `lang` golden assertions: modern Go 1.25 standard-library comments contain bracketed documentation links while the v1.1.0 tests expect the older unlinked text. That result is retained as a negative control rather than bypassed.

The clean candidate now restores the command-package checks that correspond to the installed program. It uses Go 1.25, recreates the omitted empty config fixture, and removes Nix's build-only `-mod=vendor` token before gomarkdoc parses `GOFLAGS` as application flags.

## Current disposition

`HOLD`

Last verified: `2026-08-01`  
Worker: `OpenAI`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

Clearing condition: command-check run [`30690828310`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310) and integrity run [`30690828341`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828341) must reach terminal state, receipts must be transferred here, execution carrier #437 must be closed, and an independent reviewer must inspect the final one-file source diff. A fresh public-head rebase and rerun remain required before any authorized submission.

## Contribution

- Target project: [`NixOS/nixpkgs`](https://github.com/NixOS/nixpkgs)
- Proposed destination: `NixOS/nixpkgs:master`
- Proposed title: `gomarkdoc: restore command checks`
- Work class: `upstream-fork research`
- Synopsis: use `buildGo125Module`, enable the selected command-package tests, keep Nix's `-mod=vendor` out of gomarkdoc's application parser during tests, and recreate the omitted empty fixture.

## Exact identities

### Clean target source

- Owned fork: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Branch: [`fieldwork/unit-22-gomarkdoc-checks`](https://github.com/teamleaderleo/nixpkgs/tree/fieldwork/unit-22-gomarkdoc-checks)
- Base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Head: [`569c0c4d11e5a14f3fe6237c0a50dc484f80e744`](https://github.com/teamleaderleo/nixpkgs/commit/569c0c4d11e5a14f3fe6237c0a50dc484f80e744)
- Compare: [`55096b0c...569c0c4d`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...569c0c4d11e5a14f3fe6237c0a50dc484f80e744)
- Changed file: [`pkgs/by-name/go/gomarkdoc/package.nix`](https://github.com/teamleaderleo/nixpkgs/blob/569c0c4d11e5a14f3fe6237c0a50dc484f80e744/pkgs/by-name/go/gomarkdoc/package.nix)
- Commit fence: one commit, one file; source and vendor hashes unchanged; no generated or lock files

### Current-main relation

- Later public `master` checked: [`f8e81fc7eb063db454f563cdd596fb96a5ad1497`](https://github.com/NixOS/nixpkgs/commit/f8e81fc7eb063db454f563cdd596fb96a5ad1497)
- Distance from inspected base at that check: 9 commits ahead
- Relevant-path overlap: none in the package expression or reviewed Go-builder behavior
- Submission action: rebase onto a fresh public head and rerun exact-head gates before authorized posting

### Fieldwork packet

- Path: `upstream/packets/22-nixpkgs-gomarkdoc-checks/`
- Branch: [`p0/435-unit-22-nixpkgs-gomarkdoc-checks`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-22-nixpkgs-gomarkdoc-checks/upstream/packets/22-nixpkgs-gomarkdoc-checks)
- Base: [`920f87cb25dd0cc7901d59ea2019cd4b4a193b94`](https://github.com/teamleaderleo/fieldwork/commit/920f87cb25dd0cc7901d59ea2019cd4b4a193b94)
- Exact packet head: branch tip recorded in the latest unit-22 comment on issue #435

### Active execution carrier

- PR: [Fieldwork #437](https://github.com/teamleaderleo/fieldwork/pull/437)
- Branch: `p0/435-unit-22-execution`
- Head: [`c95da0c4b3f460df9bc8f342e98d05345da66df8`](https://github.com/teamleaderleo/fieldwork/commit/c95da0c4b3f460df9bc8f342e98d05345da66df8)
- Command-check run: [`30690828310`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310)
- Integrity run: [`30690828341`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828341)

## Selected source change

```nix
buildGo125Module (finalAttrs: {
  # ...
  subPackages = [ "cmd/gomarkdoc" ];
  doCheck = true;

  preCheck = ''
    export GOFLAGS="''${GOFLAGS//-mod=vendor/}"
    touch .gomarkdoc-empty.yml
  '';
})
```

This preserves the command-only build and check boundary. It does not skip or rewrite the two incompatible `lang` golden tests because those packages are outside the selected build target.

## Evidence summary

| Claim | Evidence class | Receipt | Limit |
| --- | --- | --- | --- |
| Nixpkgs disables gomarkdoc checks | `source-read` | package at checked public head | 2026-08-01 snapshot |
| Missing empty fixture is the observed public command-test failure | `source-read` / prior art | Nixpkgs issue #516481 | issue evidence |
| Unknown `GOFLAGS` token emits a diagnostic and yields no tags | `source-read` | gomarkdoc v1.1.0 `defaultTags()` | diagnostic alone is not proven fatal |
| Old candidate passed command checks and version on Linux/Darwin | `target-executed` | runs `30598626867` and `30598687251` | older source base; one package |
| Full discovery reaches broader packages but fails two `lang` goldens identically | `target-executed negative control` | run `30674969557`; [retained receipt](./receipts/2026-08-01-full-discovery-failure.md) | help/version/review skipped after build failure |
| Clean narrowed source is one commit and one file | `source-read` | source compare | new exact-head execution queued |
| Clean narrowed command checks pass current gates | `target-test-prepared` | run `30690828310` | queued |

## Duplicate and prior art

Search date: `2026-08-01`

- [#516481 — gomarkdoc 1.1.0 checkPhase regressed](https://github.com/NixOS/nixpkgs/issues/516481)
- [#516792 — gomarkdoc: disable tests](https://github.com/NixOS/nixpkgs/pull/516792)
- [#516381 — NixOS 26.05 Zero Hydra Failures](https://github.com/NixOS/nixpkgs/issues/516381)
- [#279440 — gomarkdoc: init at 1.1.0](https://github.com/NixOS/nixpkgs/pull/279440)
- Equivalent restoration PR found: `no`

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Full-discovery negative receipt](./receipts/2026-08-01-full-discovery-failure.md)
- [Upstream issue route](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review guide](./REVIEW.md)
- [Continuation handoff](./HANDOFF.md)
- [Retained source patch](./patches/0001-gomarkdoc-restore-command-checks.patch)

## Data-quality observation

Fieldwork issue #241 labels `teamleaderleo/fieldwork#11` as the Nixpkgs target hub, while issue #11 describes DuckDB. This packet records the mismatch and leaves every other unit untouched.

## Remaining work, in order

1. Read terminal results for runs `30690828310` and `30690828341`.
2. Transfer command-package, help, version, Linux `nixpkgs-review`, artifact, and integrity receipts.
3. Repair only from a concrete new failure.
4. Close PR #437 after receipt transfer.
5. Obtain independent complete-diff review.
6. Rebase onto a fresh public Nixpkgs head and rerun before any authorized submission.
7. Seek explicit authority for public upstream interaction.

## Latest handoff

State: `HOLD`  
Exact source head: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`  
Tests executed: old command-package Linux/Darwin successes; full-discovery Linux/Darwin deterministic `lang` failure; narrowed exact-head run queued  
Temporary machinery: Fieldwork PR #437 and `.github/workflows/unit-22-gomarkdoc-checks.yml`  
Public upstream interaction: none
