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

It does not change the Go builder, package version, hashes, dependencies, command selection, linker flags, metadata, or generic check implementation.

## Findings repaired during review

1. Fixture and `GOFLAGS` edits were disproved as repair requirements.
2. The issue compares a Go 1.25 release snapshot with Go 1.26 master.
3. A passing Go 1.25 pin was rejected because the current-Go repair preserves installed bytes and avoids lifecycle work.
4. Broad-suite claims were limited to the package-selected command boundary.
5. The final commit was regenerated on current public master after confirming the package path was unchanged.

## Evidence table

| Claim | Evidence class | Result | Limit |
| --- | --- | --- | --- |
| fixture and flag cleanup unnecessary | target matrix | established | Darwin experiment |
| Go 1.26 fails before golden update | negative control | established | command package |
| one-line golden update passes | target executed | established | patch-equivalent Darwin |
| baseline/candidate binary identical | comparative control | established | patch-equivalent Darwin |
| current source is one clean commit/file | source-read | established | exact execution pending |
| current Linux/Darwin gates pass | prepared | pending | next carrier |

## Independent disposition

`EXECUTE`

The source design and complete current-base diff are accepted. Exact current-base target execution and packet integrity remain. No additional independent-review dependency exists.

Clearing condition: `e8d97d5d...` passes Linux/Darwin package/check/help/version, Darwin binary identity, Linux `nixpkgs-review`, and packet integrity. Then issue `ACCEPT` for the user's final-mile upstream decision.

No public interaction is authorized by this review.
