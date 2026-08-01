# Review — unit 22 gomarkdoc check restoration

## In simple words

The clean source candidate is a one-file Nixpkgs package repair. It preserves command-only installation, restores checks, creates the missing empty fixture, uses Go 1.25 for the retained v1.1.0 golden, keeps Nix's build-only vendor token out of gomarkdoc's application parser, and clears the package selector only before test discovery.

The source and packet repair the earlier coverage claim. The decisive full-discovery Linux and Darwin run remains queued. Unit 22 therefore stays `REPAIR` until exact-head receipts show the root, `lang`, format, command, and version controls.

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
- Execution carrier: Fieldwork PR #437, head `5c9d932276679836547b79a38aaf6b951dbdad02`, run `30674476739`
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
| Go 1.25 is the compatibility toolchain for v1.1.0's checked golden | `target-executed` for old command-package candidate, `source-read` for renewed head | run `30598687251`, exact source diff | Is a versioned builder preferable to carrying a golden-output patch? |
| removing `-mod=vendor` keeps a build-only option out of gomarkdoc's application parser | `source-read`, old path `target-executed` | `defaultTags()`, issue #516481, old logs | Since the diagnostic is benign, should the token stay for a narrower repair? |
| `.gomarkdoc-empty.yml` should be synthesized in `preCheck` | `source-read`, old command-package path `target-executed` | v1.1.0 command test, issue #516481, old logs | Should the fixture be carried as a source patch instead? |
| `subPackages=()` in `preCheck` restores full check discovery without widening installation | `source-read`, `target-test-prepared` | current builder ordering and PR #437 assertions | Does shell-level selector reset fit Nixpkgs Go conventions? |
| one-file source fence is complete | `source-read` | exact source compare | Is any package-level metadata or passthru adjustment missing? |

## Known risks

- The selector reset depends on the current `buildGoModule` phase ordering and `concatTo` behavior.
- The Go 1.25 pin creates a future upgrade obligation.
- The empty fixture is reconstructed in the disposable source tree.
- The `GOFLAGS` token removal is semantic isolation; upstream issue history treats the diagnostic itself as benign.
- The focused native builds do not provide Hydra, ofborg, merge-queue, or `nixpkgs-review` evidence.
- The author can prepare and self-review the packet; independent acceptance remains required before promotion.

## Evidence limits

- Old successful jobs ran only `cmd/gomarkdoc`; they support compatibility claims, not full-suite coverage.
- Renewed full-discovery execution is queued at run `30674476739`.
- No local Nix execution was possible in this runtime.
- Public upstream integration requires separate authorization.

## Staleness check

- Current upstream head checked: `f8e81fc7eb063db454f563cdd596fb96a5ad1497` on 2026-08-01
- Candidate base relationship: one commit above `55096b0ce13784d4f6420059c5627475fa26ebb1`; five public commits behind checked head
- Relevant source paths changed since candidate creation: `no`; package and builder blob SHAs are unchanged
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: no implementation; issue `NixOS/nixpkgs#516481` owns the regression report
- Packet and PR draft synchronized: yes, pending terminal execution receipts

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers in target source diff.
- [x] No stale execution artifacts in target source diff.
- [x] No unrelated formatting or generated churn.
- [x] Required snapshots or lock changes are inapplicable.
- [x] Commit-pinned links resolve to the reviewed source head.
- [x] Complete current source diff reviewed.

## Test review

- [ ] Intended full-discovery assertion actually ran at source head `94be3956...`.
- [x] Baseline/candidate relationship is clear.
- [x] Setup, product, and coverage-assertion failures are separated.
- [x] Coverage controls reject the prior one-package result.
- [x] Compatibility controls cover Go series, `GOFLAGS`, fixture, package discovery, vendor-backed build, and version behavior.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately.
- [ ] Terminal run, job, package-list, and artifact receipts transferred into `TESTS.md`.

## Draft review

- [x] Existing upstream issue #516481 is acknowledged; a duplicate issue is avoided.
- [x] PR draft describes the exact one-file diff and links the existing issue.
- [x] PR wording avoids claiming that the benign `GOFLAGS` diagnostic alone failed the derivation.
- [x] Target terminology and current Nixpkgs checklist style are used.
- [x] Internal process vocabulary and private context are absent from the proposed upstream body.
- [x] Disclosure requirements are reserved for submission-time recheck.
- [ ] Platform and test checkboxes synchronized from terminal receipts.

## Reviewer disposition

`REPAIR`

Reviewed source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`  
Reviewed packet head: final branch tip recorded on issue #435  
Reason: the source, prior-art framing, coverage claim, and drafts are repaired, while the exact full-discovery Linux/Darwin execution has no terminal receipt.  
Clearing condition: run `30674476739` must show root, `lang`, format, `cmd/gomarkdoc`, and version success on both platforms; transfer exact jobs and artifacts into the packet; close PR #437; then obtain independent complete-diff review.  
Reviewer eligibility: `self-review only`

## Continuation-ready guide

1. Inspect run `30674476739`, Linux job `91298756809`, and Darwin job `91298756825`.
2. On terminal completion, record every gomarkdoc package line, version output, run/job conclusion, artifact ID, digest, size, and expiry in `TESTS.md`.
3. Classify failures as checkout/setup, Nix installation, source fence, package build, test package, coverage assertion, version, or artifact publication.
4. If both platforms pass, update all packet files from `REPAIR` to the disposition supported by the receipts, close execution PR #437, and request independent review.
5. If the matrix stays queued, preserve that exact state; this runtime lacks `nix` and could not retrieve the official installer.
6. Keep public upstream read-only until exact authorization is granted.

## Human deep-dive guide

The final reviewer should focus on:

1. whether `subPackages=()` inside `preCheck` is the smallest maintainable split between build and test targets;
2. whether removing benign `-mod=vendor` diagnostics remains desirable;
3. whether the Go 1.25 pin is preferable to patching the v1.1.0 golden;
4. whether the full-discovery logs show every intended package family on both platforms;
5. whether the direct PR draft accurately closes existing issue #516481.
