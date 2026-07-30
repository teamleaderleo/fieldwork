# F241-nixpkgs-gomarkdoc-check-restoration: Restore gomarkdoc checks without leaking Nix GOFLAGS

Finding state: `research-active`

Workstream: `F/G/I — language tooling, Linux execution, and cross-repository audit`  
Canonical Fieldwork issue: `#241`  
Canonical finding path: `findings/F241-nixpkgs-gomarkdoc-check-restoration/finding.md`  
Canonical implementation or alternatives: `Fieldwork PR #265; one package-local Nixpkgs patch`  
Exact implementation heads: `e5eda30b6cf23c1eaab40d659ac72fdcf4b8b467`  
Exact base or source revision: `NixOS/nixpkgs@bbbd95e512a066deaefa89e3a244b541ed6c8c7f`  
Strongest evidence class: `target-test-prepared`; prior execution failed in the harness before package evaluation  
Reviewed input generation: `exact package expression and framework source at the named Nixpkgs revision`  
Current review disposition: `EXECUTE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Nixpkgs currently builds gomarkdoc while skipping its upstream tests. The tests call gomarkdoc's command parser inside the test process. Nix's Go builder exports `GOFLAGS=-mod=vendor`, and gomarkdoc mistakes that package-manager setting for one of its own command-line flags.

The narrow repair turns checks back on and removes only `-mod=vendor` during gomarkdoc's test phase. The already-materialized vendor directory remains present, and shared `buildGoModule` behavior stays unchanged.

## Why we care

A package that builds only because its test suite is disabled can drift unnoticed. Restoring the tests would make Nixpkgs exercise gomarkdoc's real command suite on every supported build instead of carrying permanent containment for an environment-variable collision.

## What happens if we leave it alone

Observed consequence: current Nixpkgs continues to skip gomarkdoc's upstream checks.

Inferred consequence: regressions covered only by those tests can reach the package build without being detected there.

Unknown: no failure frequency or user-impact rate has been measured.

## Governing goals and invariant

Governing invariant: package-local tests should receive application-relevant environment, while the build remains offline and uses the materialized vendor tree.

| Goal or contract | Primary source | Consequence for the design |
| --- | --- | --- |
| Restore upstream tests | `pkgs/by-name/go/gomarkdoc/package.nix` at `bbbd95e...` | `doCheck` must become true and the command tests must actually run |
| Preserve Nixpkgs vendoring | `pkgs/build-support/go/module.nix` at `bbbd95e...` | Keep `vendor/`, `GOPROXY=off`, and package-manager behavior outside the test parser |
| Avoid framework-wide behavior change | Fieldwork #241 source review | Change only the gomarkdoc expression |
| Preserve version validation | `gomarkdoc.tests.version` | Passthru test must remain green on the executed head |

## Current finding

The package-local `preCheck` below is the smallest source-supported candidate:

```nix
  doCheck = true;

  preCheck = ''
    export GOFLAGS="''${GOFLAGS//-mod=vendor/}"
  '';
```

It removes the exact token gomarkdoc rejects while retaining every other `GOFLAGS` token. The doubled single quote is required so shell parameter expansion occurs at build time rather than Nix interpolation time.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Nixpkgs disables gomarkdoc checks because of the ambient `-mod=vendor` collision | `source-read` | package comment and `doCheck = false` at `bbbd95e...` | Comment accuracy still needs restored execution |
| `buildGoModule` materializes `vendor/` and removes only `-trimpath` before tests | `source-read` | `pkgs/build-support/go/module.nix` at `bbbd95e...` | Does not prove implicit vendor selection succeeds for this package |
| The first Fieldwork matrix failure was unrelated to the package | `target-executed setup failure` | run `30583406545`; both jobs failed on `nix-build: unrecognised flag '-L'` | No package build or test result was produced |
| Removing `-L` repairs the harness syntax | `source-read` | exact failed command and updated workflow at `e5eda30...` | Requires rerun on Linux and Darwin |

## System and ownership map

- Nixpkgs `buildGoModule` owns vendor materialization, offline Go environment, and test invocation.
- The gomarkdoc package expression owns package-specific test environment repair.
- gomarkdoc's in-process command tests own parsing of `GOFLAGS` as application input.
- Fieldwork PR #265 owns the temporary cross-platform execution workflow and retained report.
- No public upstream repository is modified or contacted.

## Historical precedent

### Nixpkgs containment change

- Source: `NixOS/nixpkgs#516792`
- Revision or date: merged 2026-05-16
- Principle supported: disabling checks can contain a package build failure when the immediate test environment is incompatible.
- Important difference: containment does not restore coverage and should not be mistaken for a final repair.

### Current buildGoModule test environment

- Source: `pkgs/build-support/go/module.nix` at `bbbd95e512a066deaefa89e3a244b541ed6c8c7f`
- Principle supported: the framework deliberately exports vendoring flags and already strips `-trimpath` for tests.
- Important difference: the gomarkdoc collision is package-specific; removing `-mod=vendor` globally would change every Go package's test environment.

## Decision criteria

| Priority | Criterion | How it will be measured or falsified |
| --- | --- | --- |
| 1 | Upstream tests genuinely run | logs contain `Running phase: checkPhase` and successful `cmd/gomarkdoc` package output |
| 2 | Build remains offline and vendor-backed | exact Nix build succeeds with framework `GOPROXY=off` and materialized `vendor/` |
| 3 | Cross-platform compatibility | x86_64-linux and aarch64-darwin jobs pass at one head |
| 4 | Patch remains package-local | complete applied diff contains only `pkgs/by-name/go/gomarkdoc/package.nix` |
| 5 | Existing package interface remains valid | `gomarkdoc.tests.version` passes |

## Alternatives instantiated or analyzed

### Option A — Package-local `preCheck` token removal

- Artifact or branch: PR #265 / `investigation/241-gomarkdoc-check-restoration`
- Invariant implemented: gomarkdoc tests do not receive `-mod=vendor`; the vendor tree remains present.
- Expected benefit: restores checks with one package expression change.
- Expected cost or failure: implicit vendor selection might differ by Go version or platform.
- Discriminating control: Linux and Darwin package builds plus version test.
- Rollback boundary: remove `preCheck` and return to current containment.

### Option B — Framework-wide removal of `-mod=vendor` during checks

- Artifact or branch: paper-only.
- Invariant implemented: no Go package test sees the explicit vendoring token.
- Expected benefit: avoids similar parser collisions.
- Expected cost or failure: changes the test environment for the entire Nixpkgs Go package set without evidence of a general defect.
- Discriminating control: broad package matrix would be required.
- Rollback boundary: shared framework revert.

### Option C — Keep `doCheck = false`

- Artifact or branch: current Nixpkgs state.
- Invariant implemented: package continues to build.
- Expected benefit: no immediate test failure.
- Expected cost or failure: permanent loss of upstream test coverage.
- Discriminating control: successful restored-test matrix makes containment unnecessary.
- Rollback boundary: already current.

## Comparative results

| Criterion | Current containment | Option A | Option B | Winner or unresolved reason |
| --- | --- | --- | --- | --- |
| Package builds | source-known | pending rerun | untested | unresolved until Option A executes |
| Upstream tests run | no | pending rerun | unknown | Option A if matrix passes |
| Scope | one package | one package | all Go packages | Option A |
| Cross-platform evidence | containment exists | pending | absent | unresolved |

## Independent criticism

| Reviewer or evidence source | Counterexample or criticism | Response or new control | Effect on recommendation |
| --- | --- | --- | --- |
| F/G cross-review on #241 | Removing a Nix interpolation token incorrectly could produce a literal or evaluation error | Use `''${...}` and execute on both platforms | Kept Option A but required exact execution |
| Run `30583406545` | Initial workflow used the `nix build` short flag `-L` with `nix-build` | Remove `-L`; classify as harness failure | No change to package hypothesis |

## Selected direction and losing reasons

Selected direction: Option A remains the only bounded candidate worth executing.

Why it wins: it targets the exact environment collision, restores checks, preserves the vendor tree, and avoids changing shared framework semantics.

| Losing or deferred option | Reason it lost or moved elsewhere | Reopening trigger |
| --- | --- | --- |
| Framework-wide test GOFLAGS change | Evidence is package-specific | Multiple independently reproduced package collisions with the same required contract |
| Permanent disabled checks | Retains technical debt and test blind spot | Only if restored tests cannot be made reliable within package scope |

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Exact package-only patch | workflow applies and displays one path | prepared |
| Linux runner setup | run `30583406545`, job `91008982749` | setup succeeded through patch application; harness command failed before evaluation |
| Darwin runner setup | run `30583406545`, job `91008982872` | setup succeeded through patch application; harness command failed before evaluation |
| Fieldwork integrity | run `30583406439` | passed at `641f2e2...` |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Other packages that parse `GOFLAGS` | No second reproduction | New package-specific finding or framework campaign |
| Other Darwin architectures | One Darwin platform is the current bounded gate | Platform-specific failure or delivery request |
| Full Nixpkgs evaluation | Disproportionate for one package expression | Required only before external proposal or landing decision |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/fieldwork@641f2e2c7922ecc291434652e8c7360498b62fde` | Fieldwork integrity `30583406439` | GitHub-hosted runner | success | repository gate |
| same | gomarkdoc matrix `30583406545`, job `91008982749` | Ubuntu 24.04 / x86_64-linux | harness failed: `nix-build` rejected `-L` | classified setup failure |
| same | gomarkdoc matrix `30583406545`, job `91008982872` | macOS 14 / aarch64-darwin | same harness failure | classified setup failure |
| `teamleaderleo/fieldwork@e5eda30b6cf23c1eaab40d659ac72fdcf4b8b467` | repaired matrix | Linux and Darwin | pending | target-test-prepared |

## Complete-diff and compatibility review

- Active Fieldwork files: one temporary workflow, one patch file, one report, and this canonical finding.
- Applied target diff: `pkgs/by-name/go/gomarkdoc/package.nix` only.
- Base relationship: exact Fieldwork main `896a617...`; exact Nixpkgs source `bbbd95e...`.
- Temporary carrier status: workflow must be retired or explicitly retained after the final receipt is transferred.
- Known routine repair remaining: execute the corrected command and classify any package-level failure.
- Reviewer eligibility: exact-head review must follow the rerun.

## Current disposition and desk routing

- Finding state: `research-active`
- Review disposition: `EXECUTE`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: run the corrected Linux/Darwin matrix at the new exact head.
- Clearing condition: both package builds, test-log assertions, and version passthru tests pass at one head.
- Required subgates: Fieldwork integrity, complete diff, carrier retirement decision.
- Autonomous work remaining: execution, failure classification, report synchronization, exact-head review.
- Non-delegable human decision: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | PR #265 initial head `641f2e2...` | Prepared package-local restoration and cross-platform gate |
| 2026-07-31 | run `30583406545` | Classified failure as workflow syntax, not package behavior |
| 2026-07-31 | `e5eda30...` | Removed invalid `-L` and retriggered exact-head execution |

## References

- Fieldwork issue #241.
- Fieldwork PR #265.
- Nixpkgs `pkgs/by-name/go/gomarkdoc/package.nix` at `bbbd95e512a066deaefa89e3a244b541ed6c8c7f`.
- Nixpkgs `pkgs/build-support/go/module.nix` at the same revision.
- Nixpkgs PR #516792 and public issue #516481, read-only.
- Workflow runs `30583406439` and `30583406545`.
- No public upstream interaction occurred.
