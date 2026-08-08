# Review — unit 22 gomarkdoc command checks

## Review identity

- Work class: `upstream-fork research`
- Reviewer lane: independent complete-diff pass assigned by the user to this workstream
- Public base: `97d48ba11e7eeb6896e9da8d64b22b306da14103`
- Canonical source head: `e8d97d5d8c67a9473a7aaad3961c0630583aa34b`
- Changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Upstream-contact authority: absent

## Complete-diff result

The source is one commit and one file. It:

- removes the stale diagnostic-based disable-tests explanation and `doCheck = false`;
- adds one `postPatch` replacement for the Go 1.26 command golden;
- uses `--replace-fail` to reject unexpected source drift.

It does not change the Go builder, package version, hashes, dependencies, command selection, linker flags, metadata, product source, or generic check implementation. The modified fixture is test-only: tests generate `README-test.md` and compare it with `README.md`.

## Findings repaired during review

1. Fixture and `GOFLAGS` edits were disproved as repair requirements.
2. The issue compares a Go 1.25 release snapshot with Go 1.26 master.
3. A passing Go 1.25 pin was rejected because the current-Go repair preserves installed bytes and avoids lifecycle work.
4. Broad-suite claims were limited to the package-selected command boundary.
5. The final commit was regenerated on current public master after confirming the package path was unchanged.
6. The initial `nixpkgs-review rev HEAD` harness was corrected to use the exact parent, avoiding shallow remote-master ancestry.

## Acceptance evidence

| Claim | Evidence class | Result |
| --- | --- | --- |
| fixture and flag cleanup unnecessary | target matrix | established |
| Go 1.26 fails before golden update | negative control | established |
| one-line golden update passes | Linux/Darwin target execution | established |
| baseline/candidate binary identical | Darwin comparative control | established |
| exact current source is one clean commit/file | source fence | established |
| installed help and version pass | Linux/Darwin target execution | established |
| exact-parent `nixpkgs-review` passes | Linux integration review | established |
| Go 1.27 RC command check remains green | advisory forecast | established |

## Independent disposition

`ACCEPT`

No source, test, coverage, compatibility, or review blocker remains in the assigned unit. The packet is ready for the user's final-mile decision and any explicitly authorized public submission.

## Final-mile cautions

- Recheck current public master and issue state immediately before posting.
- Preserve the selected command-package coverage wording; do not claim every upstream library package passes.
- Keep the Go 1.27 forecast advisory until a final Go 1.27 becomes the default builder.
- Recheck contribution-template and disclosure requirements.

No public interaction is authorized by this review.
