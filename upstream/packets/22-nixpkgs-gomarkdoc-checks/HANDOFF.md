# Handoff — unit 22 gomarkdoc checks

## Current disposition

`ACCEPT`

Independent review and current-base acceptance execution are complete. The packet is ready for the user's final-mile public-upstream decision.

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

## Terminal current-base evidence

### Darwin

- Run `30693522616`, job `91352347312`: success
- Package/check/help/version and baseline/candidate binary identity: success
- Artifact `8816500818`
- Digest `sha256:313220b9f7ffff28a8023c249232ba0114eba457d1da38dad7122719bcc0d3e2`
- Binary SHA-256 `199ac9faabb41a65e784ac6128f38c3ccb6d97040e4f69d2b3bbd9b79baa817d`

### Linux

- Run `30694249810`, job `91354242933`: success
- Package/check/help/version: success
- Exact-parent `nixpkgs-review`: success; one package built (`gomarkdoc`)
- Artifact `8816799835`
- Digest `sha256:a5ab307bc9102b1c8ccea478dde8c58b21c8dcf6ce56a617ca13c9c6cd8c4cb6`

## Supporting evidence

- Repair isolation run `30692403974`.
- Patch-equivalent binary comparison run `30692966149`.
- Broad-suite negative control run `30674969557`.
- Go 1.27 RC forecast run `30693795784`.
- Independent review receipt `receipts/2026-08-01-independent-code-review.md`.
- Current-base acceptance receipt `receipts/2026-08-01-current-base-acceptance.md`.

## Final continuation

1. Record exact packet-tip Fieldwork integrity in issue #435.
2. Retire execution PR #437 after receipt transfer.
3. Recheck public master, contribution instructions, PR template, and issue state.
4. Submit or communicate publicly only under the user's explicit authority.

## Public interaction

No public upstream interaction occurred. Authority remains with the user.
