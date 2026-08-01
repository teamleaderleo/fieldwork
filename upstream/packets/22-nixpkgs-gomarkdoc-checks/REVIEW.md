# Review — unit 22 gomarkdoc command checks

## Review identity

- Work class: `upstream-fork research`
- Reviewer lane: independent complete-diff pass assigned by the user to this workstream
- Source base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Canonical source head: `3a036ab91fa1de2fbbd038b2b212552cff1cc5bf`
- Changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Upstream-contact authority: absent

## Complete-diff result

The source is one commit and one file. It:

- removes the stale diagnostic-based disable-tests explanation and `doCheck = false`;
- adds one `postPatch` replacement for the Go 1.26 command golden;
- uses `--replace-fail` to reject unexpected source drift.

It does not change the Go builder, package version, hashes, dependencies, command selection, linker flags, metadata, installed files, or generic check implementation.

## Findings repaired during review

### 1. Incorrect causal attribution — repaired

Fixture creation and `GOFLAGS` cleanup were disproved as requirements by a five-variant target matrix.

### 2. Branch comparison ambiguity — repaired

The public issue compares a Go 1.25 release snapshot with Go 1.26 master, not a linear same-branch package regression.

### 3. Go-pin product risk — avoided

A Go 1.25 pin passed but changed the shipped toolchain and created lifecycle work. The final current-Go repair preserves installed bytes exactly.

### 4. Full-suite wording — corrected

Broad discovery reaches additional packages with older standard-library prose goldens. Selected coverage remains the command package built by Nixpkgs.

## Evidence table

| Claim | Evidence class | Result | Limit |
| --- | --- | --- | --- |
| release uses Go 1.25; master uses Go 1.26 | `source-read` | established | named snapshots |
| fixture and flag cleanup are unnecessary | `target-executed matrix` | established | aarch64-darwin |
| Go 1.26 fails before golden update | `target-executed negative control` | established | command package |
| one-line Go 1.26 golden update passes | `target-executed` | established | aarch64-darwin |
| installed baseline/candidate binaries are identical | `target-executed comparative control` | established | aarch64-darwin |
| broader discovery reaches all package families | `target-executed` | established | superseded generation |
| canonical source is one clean commit/file | `source-read` | established | Linux pending |
| canonical Linux check/review passes | `target-test-prepared` | pending | queued next |

## Compatibility judgment

The selected candidate is preferable because it restores a meaningful production-toolchain test while leaving the installed executable unchanged. The test-data adjustment is coupled to Go 1.26 documentation semantics, but `--replace-fail` and future Go bumps make that maintenance visible.

## Independent disposition

`EXECUTE`

The final source design and complete diff are accepted. The remaining transition is Linux target execution and packet integrity, not another review dependency.

Clearing condition: exact source `3a036ab9...` must pass x86_64-linux package/check/help/version and `nixpkgs-review`, followed by current packet integrity. Then this lane may issue `ACCEPT` for the user's final-mile upstream decision.

## Reviewer eligibility

This receipt records the independent responsibility assigned by the user. The user retains final authority for public upstream submission. No public interaction is authorized by this review.
