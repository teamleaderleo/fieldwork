# Review — unit 22 gomarkdoc check restoration

## Review subject

- Work class: `upstream-fork research`
- Target: `NixOS/nixpkgs:master`
- Exact source base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Canonical source branch: `teamleaderleo/nixpkgs:fieldwork/unit-22-gomarkdoc-checks`
- Exact source head: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`
- Complete source fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Source relation: one commit above the exact base
- Packet branch: `p0/435-unit-22-nixpkgs-gomarkdoc-checks`
- Execution carrier: Fieldwork PR #437, head `c95da0c4b3f460df9bc8f342e98d05345da66df8`
- Command-check run: `30690828310`
- Carrier integrity run: `30690828341`
- Upstream-contact authority: `absent`

## Complete-diff result

The clean source changes one package expression and:

- selects `buildGo125Module`;
- sets `doCheck = true`;
- removes `-mod=vendor` from test-time `GOFLAGS`;
- creates the omitted empty config fixture;
- retains `subPackages = [ "cmd/gomarkdoc" ]` for build and checks.

It contains no Fieldwork files, workflows, generated output, dependency changes, unrelated formatting, or widened install targets.

Complete compare: [`55096b0c...569c0c4d`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...569c0c4d11e5a14f3fe6237c0a50dc484f80e744)

## Current public-head review

- Public head: `63c4c8011115076be7a315edd8f740fd751b168a`
- Timestamp: `2026-08-01T08:02:42Z`
- Distance from candidate base: 384 commits
- Relevant source overlap: none in the gomarkdoc package or Go module builder
- Public package still has version `1.1.0`, command-only `subPackages`, and `doCheck = false`
- Public builder still runs `preCheck` before test selection and uses nonempty `subPackages`

The candidate premise remains current. The 384-commit distance makes a fresh-head rebase and exact-head rerun a mandatory pre-submission gate.

## Disposition-relevant claims

| Claim | Evidence class | Evidence | Limit |
| --- | --- | --- | --- |
| The v1.1.0 command tests need the omitted empty fixture | `source-read`, `target-executed` | issue #516481, command test, Darwin job `91345125710` | release-specific |
| Go 1.25 is compatible with the selected command golden | `target-executed` | current Darwin job and older Linux/Darwin runs | current Linux pending |
| Removing `-mod=vendor` isolates application parsing from a Nix build flag | `source-read`, `target-executed` | `defaultTags()`, current Darwin job | diagnostic alone is not proven fatal |
| Broad selector reset reaches all package families | `target-executed` | run `30674969557` on Linux/Darwin | superseded experiment |
| Broad suite passes on Go 1.25 | disproved | same run | two deterministic `lang` failures |
| Retaining `subPackages` restores checks for the built command without widening output | `source-read`, Darwin `target-executed`, Linux `target-test-prepared` | source diff and run `30690828310` | Linux pending |
| Source is one clean commit and one file | `source-read` | exact compare | current base requires refresh |

## Negative control review

Full-discovery source head `94be3956403ebf368b9d8262fdc9e5a5d2e80683` ran in workflow `30674969557`.

Both platforms passed root, command, `format`, and `format/formatcore`, then failed `lang` on:

- `[Scanner]` versus `Scanner`;
- `*[os.File]` versus `*os.File`.

The source fence and Nix setup succeeded. This is a target compatibility result. Installed help, version passthru, and Linux `nixpkgs-review` were skipped after the package failure. The candidate was rewritten rather than hiding those failures.

Detailed receipt: [`receipts/2026-08-01-full-discovery-failure.md`](./receipts/2026-08-01-full-discovery-failure.md).

## Current exact-head review

Darwin job `91345125710` succeeded on macOS 14.8.7 arm64 with Nix 2.35.1 and Go 1.25.12.

Established:

- exact source head and parent;
- one changed package file and `git diff --check` success;
- selected command package built and checked;
- exactly one gomarkdoc package result;
- installed help output;
- version passthru `1.1.0`;
- artifact `8815619734`, digest `sha256:db5516d38b64307b5d67ffb6bc23c33028dbdeaeb2b681b60a1cc7440958021a`.

Linux job `91345125742`, including `nixpkgs-review`, and carrier-integrity job `91345125771` remain queued. Receipt: [`receipts/2026-08-01-command-checks.md`](./receipts/2026-08-01-command-checks.md).

## Known risks

- Go 1.25 pin requires future cleanup.
- The empty fixture is generated in the disposable source tree.
- `GOFLAGS` token removal is semantically clean but broader than the publicly observed missing-fixture blocker.
- Selected checks cover the built command package, not every upstream library package.
- Exact-head Linux and final packet-tip integrity remain pending.
- The candidate base is 384 public commits behind the refreshed head.
- Independent acceptance and public authority remain absent.

## Source cleanliness

- [x] One source commit and one changed file.
- [x] No Fieldwork-only source files.
- [x] No temporary workflow in target source.
- [x] No source/vendor hash changes.
- [x] No generated or lock-file changes.
- [x] No widened install target.
- [x] Complete current source diff reviewed.

## Test review

- [x] Older Linux/Darwin command-package passes are retained with their one-package limit.
- [x] Full discovery ran at an exact head on Linux and Darwin.
- [x] Full-discovery failures are classified as target compatibility failures.
- [x] The disproved full-suite claim is removed.
- [x] The selected candidate keeps the package-selected command boundary.
- [x] Current exact-head Darwin command-package build/check passed.
- [x] Current Darwin installed-help and version receipts are retained.
- [ ] Current Linux build/check/help/version/`nixpkgs-review` receipt is retained.
- [ ] Final packet-tip Fieldwork integrity receipt is retained.
- [ ] Execution carrier is closed after transfer.

## Draft review

- [x] Existing issue #516481 is reused; no duplicate issue is proposed.
- [x] Proposed title says `restore command checks`, not `restore full upstream checks`.
- [x] Draft avoids claiming the benign `GOFLAGS` diagnostic alone caused the failure.
- [x] Draft states the selected-package coverage boundary.
- [x] Internal Fieldwork process is excluded from the proposed upstream body.
- [x] Darwin checkbox may be synchronized from the exact-head receipt.
- [ ] Linux checkboxes await terminal evidence.
- [ ] Submission-time template and disclosure requirements require a fresh check.

## Reviewer disposition

`HOLD`

Reviewed source head: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`  
Reason: the clean source and negative control are coherent, and exact-head Darwin passed; Linux, final packet integrity, carrier closure, independent review, and fresh-head execution remain incomplete.  
Clearing condition for packet execution: transfer terminal Linux and final-integrity receipts, close PR #437, then obtain independent complete-diff review. Rebase and rerun on a fresh public head before any authorized submission.  
Reviewer eligibility: `self-review only`

## Human inspection guide

Focus on:

1. whether selected command-package tests are the appropriate Nixpkgs package boundary;
2. whether `buildGo125Module` is preferable to a source golden patch;
3. whether test-time `-mod=vendor` removal is desirable despite the benign diagnostic;
4. whether synthesizing the empty fixture in `preCheck` matches Nixpkgs conventions;
5. whether the full-discovery negative control justifies excluding broader library tests from this package repair;
6. whether final Linux logs prove build, command test, help, version, and `nixpkgs-review` without broader claims.

## Continuation

1. Inspect Linux job `91345125742` and carrier-integrity job `91345125771`.
2. Transfer exact job, platform, assertion, artifact, digest, and skipped-step results.
3. Trigger and retain a final packet-tip integrity generation.
4. Repair only from a concrete terminal failure.
5. Close execution PR #437 after transfer.
6. Obtain independent review.
7. Rebase onto a fresh public Nixpkgs head and rerun before authorized submission.
8. Keep public upstream read-only until explicit authority is granted.
