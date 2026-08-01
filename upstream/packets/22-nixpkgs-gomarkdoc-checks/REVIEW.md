# Review — unit 22 gomarkdoc check restoration

## In simple words

The clean source candidate is a one-file Nixpkgs package repair. It preserves command-only installation, restores checks, creates the missing empty fixture, uses Go 1.25 for the retained v1.1.0 golden, keeps Nix's build-only vendor token out of gomarkdoc's application parser, and clears the package selector only before test discovery.

The source and packet repair the earlier coverage claim. Exact-head Linux, Darwin, installed-binary, version, Linux `nixpkgs-review`, and Fieldwork-integrity jobs remain queued. The source has no known defect from the completed review; required execution evidence is unavailable, so unit 22 is `HOLD`.

## Review subject

- Work class: `upstream-fork research`
- Target repository: `NixOS/nixpkgs`
- Proposed upstream base: `master`
- Exact source base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Canonical source branch: `teamleaderleo/nixpkgs:fieldwork/unit-22-gomarkdoc-checks`
- Exact source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- Fieldwork packet branch: `p0/435-unit-22-nixpkgs-gomarkdoc-checks`
- Exact packet head: recorded by the final unit-22 handoff on Fieldwork issue #435
- Complete changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Execution carrier: Fieldwork PR #437, head `b6003f2a3523f01880ff5690798b69afcb4e11f5`
- Target run: `30674969557`
- Linux job: `91300175276`
- Darwin job: `91300175296`
- Fieldwork integrity run: `30674969559`
- Reviewed coordination inputs: Fieldwork issue #435, issue #241, PR #265, open Nixpkgs issue #516481
- Upstream-contact authority: `absent`

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [complete source compare](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683)
6. [exact source file](https://github.com/teamleaderleo/nixpkgs/blob/94be3956403ebf368b9d8262fdc9e5a5d2e80683/pkgs/by-name/go/gomarkdoc/package.nix)
7. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
8. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- Complete compare: [`55096b0c...94be3956`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683)
- Production file: [`package.nix`](https://github.com/teamleaderleo/nixpkgs/blob/94be3956403ebf368b9d8262fdc9e5a5d2e80683/pkgs/by-name/go/gomarkdoc/package.nix)
- Tests: upstream Go tests already present in gomarkdoc v1.1.0; the package expression restores their execution
- Generated or dependency files: `not applicable`
- Retained patch: [`patches/0001-gomarkdoc-restore-full-upstream-checks.patch`](./patches/0001-gomarkdoc-restore-full-upstream-checks.patch)

## Claims requiring judgment

| Claim or design choice | Evidence class | Evidence | Reviewer question |
| --- | --- | --- | --- |
| Go 1.25 is the compatibility toolchain for v1.1.0's checked golden | `target-executed` for old command-package candidate, `source-read` for renewed head | runs `30598626867` and `30598687251`; exact source diff | Is a versioned builder preferable to carrying a golden-output patch? |
| removing `-mod=vendor` keeps a build-only option out of gomarkdoc's application parser | `source-read`, old path `target-executed` | `defaultTags()`, issue #516481, old logs | Since the diagnostic is benign, should the token stay for a narrower repair? |
| `.gomarkdoc-empty.yml` should be synthesized in `preCheck` | `source-read`, old command-package path `target-executed` | v1.1.0 command test, issue #516481, old logs | Should the fixture be carried as a source patch instead? |
| `subPackages=()` in `preCheck` restores full check discovery without widening installation | `source-read`, `target-test-prepared` | current builder ordering and PR #437 assertions | Does shell-level selector reset fit Nixpkgs Go conventions? |
| one-file source fence is complete | `source-read` | exact source compare | Is any package-level metadata or passthru adjustment missing? |

## Known risks

- The selector reset depends on the current `buildGoModule` phase ordering and `concatTo` behavior.
- The Go 1.25 pin creates a future upgrade obligation.
- The empty fixture is reconstructed in the disposable source tree.
- The `GOFLAGS` token removal is semantic isolation; upstream issue history treats the diagnostic itself as benign.
- The queued focused builds have no terminal receipt and provide no Hydra, ofborg, or merge-queue evidence.
- The author can prepare and self-review the packet; independent acceptance remains required before promotion.

## Evidence limits

- Old successful jobs ran only `cmd/gomarkdoc`; they support compatibility claims, not full-suite coverage.
- Renewed full-discovery execution is queued at run `30674969557`.
- Installed-binary help, version, and Linux `nixpkgs-review` controls are prepared in that run and unexecuted.
- Fieldwork integrity run `30674969559` remains queued.
- No local Nix execution was possible in the available runtime.
- Public upstream integration requires separate authorization.

## Staleness check

- Public upstream head checked: `f8e81fc7eb063db454f563cdd596fb96a5ad1497` on 2026-08-01
- Candidate base relationship: one commit above `55096b0ce13784d4f6420059c5627475fa26ebb1`; nine public commits behind the checked head
- Relevant source paths changed since candidate creation: `no` in the compared public advance
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: no implementation; issue `NixOS/nixpkgs#516481` owns the regression report
- Packet and PR draft synchronized: yes, pending terminal execution receipts
- Submission-time requirement: rebase onto a fresh public head and rerun exact-head gates

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers in target source diff.
- [x] No stale execution artifacts in target source diff.
- [x] No unrelated formatting or generated churn.
- [x] Required snapshots or lock changes are inapplicable.
- [x] Commit-pinned links resolve to the reviewed source head.
- [x] Complete current source diff reviewed.

## Test review

- [ ] Intended full-discovery assertion ran at source head `94be3956...`.
- [x] Baseline/candidate relationship is clear.
- [x] Setup, product, and coverage-assertion failures are separated.
- [x] Coverage controls reject the prior one-package result.
- [x] Compatibility controls cover Go series, `GOFLAGS`, fixture, package discovery, vendor-backed build, and version behavior.
- [x] Installed binary and Linux `nixpkgs-review` controls are prepared.
- [x] Platform and integration limits are explicit.
- [ ] Terminal run, job, package-list, review, help, and artifact receipts transferred into `TESTS.md`.
- [ ] Current Fieldwork-integrity receipt retained.

## Draft review

- [x] Existing upstream issue #516481 is acknowledged; a duplicate issue is avoided.
- [x] PR draft describes the exact one-file diff and links the existing issue.
- [x] PR wording avoids claiming that the benign `GOFLAGS` diagnostic alone failed the derivation.
- [x] Target terminology and current Nixpkgs checklist style are used.
- [x] Internal process vocabulary and private context are absent from the proposed upstream body.
- [x] Disclosure requirements are reserved for submission-time recheck.
- [ ] Platform and test checkboxes synchronized from terminal receipts.

## Reviewer disposition

`HOLD`

Reviewed source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`  
Reviewed packet head: final branch tip recorded on issue #435  
Reason: source, prior-art framing, coverage claim, and drafts are coherent; required exact-head target and repository-gate execution has no terminal receipt.  
Clearing condition: run `30674969557` must reach terminal state with root, `lang`, format, `cmd/gomarkdoc`, binary-help, version, and Linux `nixpkgs-review` controls; integrity run `30674969559` must complete or be replaced by a current packet-head run; transfer receipts, close PR #437, and obtain independent complete-diff review.  
Reviewer eligibility: `self-review only`

## Continuation-ready guide

1. Inspect run `30674969557`, Linux job `91300175276`, Darwin job `91300175296`, and integrity run `30674969559`.
2. On terminal completion, record every gomarkdoc package line, help result, version output, `nixpkgs-review` result, run/job conclusion, artifact ID, digest, size, and expiry in `TESTS.md`.
3. Classify failures as checkout/setup, Nix installation, source fence, package build, test package, coverage assertion, binary help, version, `nixpkgs-review`, artifact publication, or Fieldwork integrity.
4. Repair only from concrete terminal evidence; rerun exact source head after any source change.
5. Close execution PR #437 after evidence transfer.
6. Obtain independent review, rebase onto a fresh public Nixpkgs head, and rerun before authorized submission.
7. Keep public upstream read-only until exact authorization is granted.

## Human deep-dive guide

The final reviewer should focus on:

1. whether `subPackages=()` inside `preCheck` is the smallest maintainable split between build and test targets;
2. whether removing benign `-mod=vendor` diagnostics remains desirable;
3. whether the Go 1.25 pin is preferable to patching the v1.1.0 golden;
4. whether the full-discovery logs show every intended package family on both platforms;
5. whether the direct PR draft accurately closes existing issue #516481.
