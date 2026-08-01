# Review — unit 22 gomarkdoc command checks

## Review identity

- Work class: `upstream-fork research`
- Reviewer lane: independent complete-diff pass assigned by the user to this workstream
- Canonical source: `teamleaderleo/nixpkgs:fieldwork/unit-22-gomarkdoc-checks`
- Source base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Source head: `5c17b14e271611c3418e3e2f572366766f6aa3cc`
- Changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Upstream authority: absent

## Complete-diff result

The source is one commit and one file. It:

- replaces `buildGoModule` with `buildGo125Module`;
- removes the stale diagnostic-based disable-tests explanation;
- removes `doCheck = false` so the standard command-package check runs;
- adds a two-line compatibility comment.

It does not add fixtures, environment mutations, custom checks, test patches, generated files, dependency changes, hash changes, widened package selection, or Fieldwork files.

## Findings repaired during review

### 1. Incorrect causal attribution — repaired

The previous packet treated the missing fixture and leaked `-mod=vendor` as repair requirements. Comparative target execution proves neither is required. The source and packet were simplified.

### 2. Branch comparison ambiguity — repaired

The public issue's passing revision is from release-25.11 and its failing revision is from master. The decisive difference is Go 1.25 versus Go 1.26. The packet no longer presents them as a same-branch temporal regression.

### 3. Product-output compatibility claim — repaired

Pinning the builder changes the installed binary's Go runtime/GOROOT view and can change generated documentation. Earlier wording claiming unchanged output was removed.

### 4. Broader-suite feasibility — clarified

The two observed language goldens jointly require Go 1.21 or older. Current Nixpkgs does not retain that as a supported builder. Full-suite restoration is not part of this package-selected command repair.

## Evidence table

| Claim | Evidence class | Result | Limit |
| --- | --- | --- | --- |
| release snapshot uses Go 1.25; master snapshot uses Go 1.26 | `source-read` | established | two named snapshots |
| Go 1.25 alone passes command checks | `target-executed comparative experiment` | established | generated variant, not final Git head |
| fixture and flag cleanup are unnecessary | `target-executed comparative experiment` | established | aarch64-darwin experiment |
| Go 1.26 fails with both cleanups | `target-executed negative control` | established | aarch64-darwin command package |
| broad discovery reaches all package families | `target-executed` | established | superseded source generation |
| broad suite is compatible with supported Go | disproved | deterministic language failures | Go 1.25 only |
| simplified source is one clean commit/file | `source-read` | established | execution pending |
| simplified exact head passes Linux/Darwin | `target-test-prepared` | pending | no exact-head receipt yet |

## Compatibility judgment

The Go 1.25 pin is acceptable as a bounded compatibility repair because:

- upstream v1.1.0 CI pinned Go 1.20;
- current Go 1.26 changes checked generated output;
- Go 1.25 is the oldest currently supported Nixpkgs toolchain;
- the package is dormant and has no newer tagged release.

The pin is not permanent. A future update should prefer a maintained gomarkdoc release or current-Go golden repair over carrying an unsupported Go builder.

## Independent disposition

`EXECUTE`

The source design and complete diff are accepted. The next transition is exact-head target execution, not another review dependency.

Clearing condition: source head `5c17b14e...` must pass the prepared Linux and Darwin package/check/help/version gates, Linux `nixpkgs-review`, and packet integrity. After receipt transfer, this review lane may issue `ACCEPT` for handoff to the user's final-mile upstream decision.

## Reviewer eligibility

This receipt records the independent review responsibility explicitly assigned by the user. The user retains the final authority for public upstream submission. No public interaction is authorized by this review.
