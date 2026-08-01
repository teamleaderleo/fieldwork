# Handoff — unit 22 gomarkdoc checks

## Current disposition

`EXECUTE`

Independent review selected the current-Go golden repair and regenerated it on the current public Nixpkgs head. Exact current-base execution remains.

## Exact source

- Repository: `teamleaderleo/nixpkgs`
- Branch: `fieldwork/unit-22-gomarkdoc-checks`
- Public base: `97d48ba11e7eeb6896e9da8d64b22b306da14103`
- Canonical head: `e8d97d5d8c67a9473a7aaad3961c0630583aa34b`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Relation: one commit, one file, six additions, four deletions

## Source decision

- retain the default Go 1.26 builder;
- restore selected command checks by removing `doCheck = false`;
- update one expected markdown line in `testData/docs/README.md`;
- retain `subPackages = [ "cmd/gomarkdoc" ]`;
- do not create a fixture;
- do not rewrite `GOFLAGS`.

## Preserved evidence

- Repair isolation: run `30692403974`, job `91349338842`.
- Go 1.26 patch-equivalent acceptance: run `30692966149`, job `91350898702`, artifact `8816337182`, binary SHA-256 `b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e`.
- Broad-suite negative control: run `30674969557`.
- Comparison carrier PR #490 closed after receipt transfer.
- Unit 01 PR #438 remains unrelated and intact.

## Required continuation

1. Launch a clean carrier anchored to the packet revision containing this handoff.
2. Run current source `e8d97d5d...` on x86_64-linux and aarch64-darwin.
3. Preserve source fence, command result, help, version, Darwin baseline/candidate binary identity, Linux `nixpkgs-review`, artifacts, and integrity.
4. Transfer receipts and retire canonical execution PR #437.
5. Mark the packet `ACCEPT` for the user's final-mile public decision if all gates pass.

## Public interaction

No public upstream interaction occurred. Authority remains with the user.
