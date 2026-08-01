# Review — unit 22 gomarkdoc check restoration

## In simple words

The source candidate is a clean one-file Nixpkgs package repair. It preserves the narrow command build, restores package checks, and corrects the prior execution gap by resetting the package selector only before test discovery. The decisive remaining step is exact-head Linux and Darwin execution that visibly includes root, `lang`, format, and command packages.

## Review subject

- Work class: `upstream-fork research`
- Target repository: `NixOS/nixpkgs`
- Proposed upstream base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Canonical source branch: `teamleaderleo/nixpkgs:fieldwork/unit-22-gomarkdoc-checks`
- Exact source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- Fieldwork packet branch: `p0/435-unit-22-nixpkgs-gomarkdoc-checks`
- Exact packet head: recorded in the latest issue #435 handoff; branch tip is canonical
- Complete changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Execution carrier: Fieldwork PR #437, head `5c9d932276679836547b79a38aaf6b951dbdad02`, run `30674476739`
- Reviewed coordination input: Fieldwork issue #435 assignment for unit 22 and issue #241/PR #265 retained history, read on 2026-08-01
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
- Tests: upstream Go tests already present in gomarkdoc v1.1.0; this expression restores their execution
- Generated or dependency files: `not applicable`
- Retained patch: [`patches/0001-gomarkdoc-restore-full-upstream-checks.patch`](./patches/0001-gomarkdoc-restore-full-upstream-checks.patch)

## Claims requiring judgment

| Claim or design choice | Evidence class | Evidence | Reviewer question |
| --- | --- | --- | --- |
| Go 1.25 is the compatibility toolchain for v1.1.0's golden output | `target-executed` for old candidate, `source-read` for renewed head | old run 30598626867; renewed `package.nix` | Is a package-specific Go pin preferable to carrying a golden-output patch? |
| test-time removal of `-mod=vendor` preserves offline vendoring | `target-executed` for old candidate | old Linux/Darwin logs show the vendored module derivation and successful command tests | Does substring removal remain narrow enough if future default `GOFLAGS` ordering changes? |
| `.gomarkdoc-empty.yml` should be synthesized in `preCheck` | `target-executed` for old candidate | old command-package checks passed after fixture creation | Should the fixture be carried as a patch instead for greater explicitness? |
| `subPackages=()` in `preCheck` restores full check discovery without widening installation | `source-read`, `target-test-prepared` | current builder ordering plus run 30674476739 assertions | Does shell-level selector reset fit Nixpkgs Go conventions? |
| one-file source fence is complete | `source-read` | exact source compare | Is any package-level comment or passthru adjustment missing? |

## Known risks

- The test selector reset depends on the current `buildGoModule` phase ordering and `concatTo` behavior.
- The Go 1.25 pin may become stale after a gomarkdoc release or future Nixpkgs toolchain cleanup.
- The empty fixture is reconstructed during the build because Git cannot retain an empty tracked file in a release archive without an entry.
- The focused native builds do not provide Hydra or merge-queue evidence.
- The author is eligible to prepare and self-review this packet, while independent acceptance remains required for final promotion.

## Evidence limits

- Old successful jobs ran only `cmd/gomarkdoc`; they support compatibility claims, not full-suite coverage.
- Renewed full-discovery execution is pending at run 30674476739.
- `nixpkgs-review` remains unexecuted.
- Public upstream integration requires separate authorization.

## Staleness check

- Current upstream head checked: `55096b0ce13784d4f6420059c5627475fa26ebb1` on 2026-08-01
- Candidate base relationship: exact one-commit descendant
- Relevant source paths changed upstream since retained execution: the package expression stayed semantically unchanged in the reviewed area; the generic builder was reread at the renewed base
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: none in the gomarkdoc PR search
- Packet and target PR descriptions synchronized: yes, pending execution-result updates

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers in target source diff.
- [x] No stale execution artifacts in target source diff.
- [x] No unrelated formatting or generated churn.
- [x] Required snapshots or lock changes are inapplicable.
- [x] Commit-pinned links resolve to the reviewed source head.
- [x] Complete current source diff reviewed.

## Test review

- [ ] Intended full-discovery assertion actually ran — pending run 30674476739.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures have separate classifications.
- [x] Coverage controls reject the prior one-package result.
- [x] Compatibility controls cover Go series, `GOFLAGS`, and the omitted fixture.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately.
- [ ] Terminal job and artifact receipts transferred into `TESTS.md`.

## Draft review

- [x] Issue draft describes the package-specific failure without prevalence claims.
- [x] PR draft describes the exact current one-file diff.
- [x] Target terminology and current Nixpkgs checklist style are used.
- [x] Internal process vocabulary and private context are absent from proposed upstream bodies.
- [x] Disclosure requirements are marked for submission-time recheck.
- [ ] Platform checklist synchronized from terminal receipts.

## Reviewer disposition

`EXECUTE`

Reviewed source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`  
Reviewed packet head: branch tip at this review generation  
Reason: the implementation and discriminating assertions are prepared, while target-native full-discovery execution is still queued.  
Clearing condition: run 30674476739 completes on both platforms with root, `lang`, format, command, and version controls, followed by receipt transfer and carrier closure.  
Reviewer eligibility: `self-review only`; independent acceptance required before promotion.

## Human deep-dive guide

The final human reviewer should focus on:

1. whether `subPackages=()` inside `preCheck` is the smallest maintainable split between build and test targets;
2. whether the Go 1.25 pin is preferable to patching the v1.1.0 documentation golden;
3. whether the full-discovery logs show every intended package family on both platforms;
4. whether direct PR remains preferable to issue-first discussion.

Suggested response:

`Unit 22 looks ready for upstream preparation`  
—or—  
`Unit 22 concern: <specific source, test, compatibility, or framing issue>`
