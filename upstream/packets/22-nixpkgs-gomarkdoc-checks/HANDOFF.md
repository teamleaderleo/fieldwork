# Handoff — unit 22 gomarkdoc checks

## Current disposition

`EXECUTE`

Independent code review selected the current-Go golden repair. Exact Darwin acceptance controls pass; Linux and packet integrity remain.

## Exact source

- Repository: `teamleaderleo/nixpkgs`
- Branch: `fieldwork/unit-22-gomarkdoc-checks`
- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `3a036ab91fa1de2fbbd038b2b212552cff1cc5bf`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Relation: one commit, one file, six additions, four deletions

## Source decision

- retain the default Go 1.26 builder;
- restore selected command checks by removing `doCheck = false`;
- update one expected markdown line in `testData/docs/README.md`;
- retain `subPackages = [ "cmd/gomarkdoc" ]`;
- do not create a fixture;
- do not rewrite `GOFLAGS`.

## Why

A target matrix disproved the original environment-cleanup theory. A current-Go comparison then proved the one-line golden update passes and leaves the installed binary byte-for-byte identical to the checks-disabled package.

## Executed evidence

### Go 1.26 golden acceptance

- Run `30692966149` — success
- Job `91350898702`
- Artifact `8816337182`
- Digest `sha256:14ae794f8160a5f6c68bcf113dd430d628fa4b8399ad9ceb65f1d5f33770e5e1`
- Command check, help, version, and binary identity: pass
- Shared binary SHA-256: `b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e`

### Repair isolation

- Run `30692403974` — success
- Job `91349338842`
- Conclusion: fixture and flag edits unnecessary; Go 1.26 golden mismatch is causal

### Broader-suite negative control

- Run `30674969557` — expected failure
- Linux and Darwin reached broad package discovery
- Both failed deterministic `lang` standard-library prose expectations

### Superseded pin

The Go 1.25 candidate passed exact Darwin gates but is rejected because the final Go 1.26 repair preserves installed bytes and avoids a toolchain pin.

## Independent review

The final diff, causal chain, compatibility behavior, and drafts are accepted. No additional independent-review dependency remains.

Receipt: `receipts/2026-08-01-independent-code-review.md`.

## Required continuation

1. Create a clean Linux execution carrier anchored to the packet revision containing this handoff.
2. Run source `3a036ab9...` on x86_64-linux with package/check/help/version and `nixpkgs-review` gates.
3. Preserve artifact and current Fieldwork-integrity receipts.
4. Transfer receipts and retire PRs #437 and #438.
5. Mark the packet `ACCEPT` for the user's final-mile public decision if all gates pass.
6. Regenerate on a fresh public Nixpkgs head before authorized submission.

## Public interaction

No public upstream interaction occurred. Authority remains with the user.
