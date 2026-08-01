# Handoff — unit 22 gomarkdoc checks

## Current disposition

`EXECUTE`

Independent code review is complete. The simplified exact source requires fresh target execution.

## Exact source

- Repository: `teamleaderleo/nixpkgs`
- Branch: `fieldwork/unit-22-gomarkdoc-checks`
- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `5c17b14e271611c3418e3e2f572366766f6aa3cc`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Relation: one commit, one file, 4 additions, 6 deletions

## Source decision

- use `buildGo125Module`;
- restore default command checks by removing `doCheck = false`;
- retain `subPackages = [ "cmd/gomarkdoc" ]`;
- do not create a missing fixture;
- do not rewrite `GOFLAGS`.

## Why

A target variant matrix proves Go 1.25 alone passes and Go 1.26 fails even with both proposed environment cleanups. The public issue compared a Go 1.25 release branch with Go 1.26 master and misidentified captured diagnostics as the cause.

## Executed evidence

### Repair isolation

- Run `30692403974` — success
- Job `91349338842`
- Artifact `8816151764`
- Digest `sha256:8597cc8e25daa9975c20a36c1a824d939820f373bc8a0521d2a022ac60e5471e`
- Conclusion: pin required; fixture and flag edits unnecessary

### Broader-suite negative control

- Run `30674969557` — failure by design
- Linux and Darwin reached broad package discovery
- Both failed deterministic `lang` standard-library prose expectations

### Superseded exact-head passes

Prior Go 1.25 command-package executions on Linux and Darwin remain useful compatibility evidence but do not validate source head `5c17b14e...`.

## Independent review

Complete-diff review accepted the simplified source direction and repaired the packet's causal and compatibility claims. No additional independent-review dependency remains.

Receipt: `receipts/2026-08-01-independent-code-review.md`.

## Required continuation

1. Create a clean execution carrier anchored to the packet revision containing this handoff.
2. Run source head `5c17b14e...` on x86_64-linux and aarch64-darwin.
3. Preserve source fence, command result, one-package count, installed help, version, Linux `nixpkgs-review`, artifacts, and integrity.
4. Transfer receipts and retire the execution carrier.
5. Mark the research packet `ACCEPT` for the user's final-mile public decision if all exact-head gates pass.
6. Rebase/regenerate on a fresh public Nixpkgs head before any authorized submission.

## Public interaction

No public upstream interaction occurred. Authority remains with the user.
