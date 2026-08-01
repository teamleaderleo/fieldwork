# Handoff — unit 22 gomarkdoc checks

## Current disposition

`HOLD`

The one-file clean source candidate and full packet are prepared. Required exact-head target execution and Fieldwork integrity remain queued.

## Exact source

- Repository: `teamleaderleo/nixpkgs`
- Branch: `fieldwork/unit-22-gomarkdoc-checks`
- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`

## Exact packet

- Repository: `teamleaderleo/fieldwork`
- Branch: `p0/435-unit-22-nixpkgs-gomarkdoc-checks`
- Base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Head: record the commit created with this file in the unit-22 comment on issue #435
- Directory: `upstream/packets/22-nixpkgs-gomarkdoc-checks/`

## Active execution

- PR: `teamleaderleo/fieldwork#437`
- Branch: `p0/435-unit-22-execution`
- Head: `b6003f2a3523f01880ff5690798b69afcb4e11f5`
- Target run: `30674969557`
- Linux job: `91300175276`
- Darwin job: `91300175296`
- Fieldwork integrity run: `30674969559`
- Current state: queued, with no terminal target or integrity receipt

Superseded execution generation:

- head `5c9d932276679836547b79a38aaf6b951dbdad02`
- run `30674476739`

## Tests executed

Retained old executions:

- run `30598626867`, Linux job `91056349644`, Darwin job `91056349617`
- run `30598687251`, Linux job `91056528367`, Darwin job `91056528347`

Both old runs built the Go 1.25 candidate on Linux and Darwin, ran only `github.com/princjef/gomarkdoc/cmd/gomarkdoc`, and passed version output `1.1.0`. They prove compatibility and expose the one-package coverage limit.

Current prepared gates:

- exact source head/parent and one-file diff;
- `git diff --check`;
- package builds on x86_64-linux and aarch64-darwin;
- root, `lang`, format, and command-package result assertions;
- installed executable and help output;
- version passthru;
- Linux `nixpkgs-review rev HEAD --no-shell`;
- current Fieldwork integrity;
- retained logs, package list, review output, source diff, and artifacts.

## Remaining blockers

1. Target run `30674969557` has no terminal result.
2. Fieldwork integrity run `30674969559` has no terminal result.
3. The active runtime has no `nix` or `nix-build`, and its Nix installer retrieval attempt failed.
4. Execution receipts have not been transferred and PR #437 remains open.
5. Independent complete-diff acceptance is pending.
6. Fresh-public-head rebase and rerun remain required before submission.
7. Hydra, ofborg, and merge-queue evidence require an authorized public Nixpkgs PR.
8. Public upstream contact authority is absent.

## Continuation sequence

1. Inspect target run `30674969557`, jobs `91300175276` and `91300175296`, plus integrity run `30674969559`.
2. Preserve terminal conclusions, runner images, source verification, complete package result lines, installed-help output, version output, Linux `nixpkgs-review`, artifacts and digests, and integrity output.
3. Classify any failure by checkout, setup, source fence, package build, package test, coverage assertion, installed binary, version, review gate, artifact publication, or repository integrity.
4. Repair only from concrete terminal evidence and rerun the exact source head after any source change.
5. Update `README.md`, `TESTS.md`, `REVIEW.md`, drafts, and this handoff from the terminal receipts.
6. Close PR #437 after evidence transfer.
7. Obtain independent review, rebase onto a fresh public Nixpkgs head, and rerun exact-head gates.
8. Keep all public upstream interaction read-only until explicit authority is granted.
