# F241 — Nixpkgs gomarkdoc check restoration

Finding state: `review-ready`

Canonical issue: #241  
Canonical Fieldwork PR: #265  
Exact Nixpkgs fence: `bbbd95e512a066deaefa89e3a244b541ed6c8c7f`  
Package: `gomarkdoc` 1.1.0  
Executed candidate patch generation: `1cdbcfa7bf07086ed9a46f440d3595595afdd241`  
Evidence classes present: `source-read`, `target-executed`, and repository-gate execution  
Current disposition: `ACCEPT requested after cleanup-head review`  
Upstream contact authorized: `no`

## In simple words

Nixpkgs disabled gomarkdoc's tests because the package mistakes Nix's `-mod=vendor` build setting for one of its own command-line flags.

Removing that flag opened the real test suite but exposed two more release assumptions: a referenced empty config file is missing from the tag, and Go 1.26 generates one documentation link differently from the checked golden.

The retained candidate uses Nixpkgs' supported Go 1.25 builder for both the shipped binary and its tests, removes only `-mod=vendor` during checks, and creates the omitted empty fixture in the disposable build tree. The complete package and version checks passed on Linux and Darwin.

## Why we care

Keeping `doCheck = false` leaves the package blind to every upstream regression. Enabling tests carelessly would either break the package or encourage broad suppression. The retained repair restores the real command tests while keeping the change package-local, offline, vendor-backed, and coherent with the binary that is shipped.

## What happens if we leave it alone

Observed: Nixpkgs continues to build gomarkdoc 1.1.0 without executing its upstream suite.

Inferred: regressions covered only by those tests can enter the package unnoticed.

Unknown: failure frequency and user exposure have not been measured.

## Governing contract

- keep the repair limited to `pkgs/by-name/go/gomarkdoc/package.nix`;
- preserve the materialized vendor tree and `GOPROXY=off` behavior;
- run the full discovered upstream package set, including `cmd/gomarkdoc`;
- build and test the final binary with the same Go toolchain;
- do not regenerate expected output from the candidate under test;
- retain `gomarkdoc.tests.version`;
- keep public upstream read-only.

## Current finding

The smallest executed restoration is:

```nix
{
  buildGo125Module,
  ...
}:

buildGo125Module (finalAttrs: {
  doCheck = true;

  preCheck = ''
    export GOFLAGS="''${GOFLAGS//-mod=vendor/}"
    touch .gomarkdoc-empty.yml
  '';
})
```

The builder change is intentional: the v1.1.0 documentation golden matches Go 1.25 behavior, and testing with Go 1.25 while shipping a Go 1.26 binary would validate a different output contract.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Ambient `-mod=vendor` causes the original command-test parser failure | `target-executed` | cross-platform run `30586416205`; removing the token cleared that failure before later assertions | exact gomarkdoc 1.1.0 and Nixpkgs fence only |
| The release tag omits the empty config fixture referenced by tests | `source-read` and `target-executed` | v1.1.0 `command_test.go`, absent tag path, and run `30586416205` | does not establish intent for later releases |
| Go 1.26 changes one checked documentation link | `target-executed` | Linux and Darwin failures in run `30586416205` | exact golden and Go 1.26.5 only |
| The coherent Go 1.25 candidate passes the package and version checks on both platforms | `target-executed` | run `30598687251`, jobs `91056528367` and `91056528347` | two named platforms, not every Nixpkgs system |
| The target diff is one package expression | `target-executed` | applied diff printed in both matrix jobs | Fieldwork documentation and retired carrier are separate |

## System and ownership map

- `pkgs/by-name/go/gomarkdoc/package.nix` owns package-specific builder selection and test setup.
- `pkgs/build-support/go/module.nix` owns vendor materialization, offline Go environment, and discovered-package test execution.
- gomarkdoc's command tests own parsing of `GOFLAGS`, config loading, and generated-documentation comparison.
- Fieldwork PR #265 retains the target patch, source analysis, hypotheses, and exact execution receipts.
- No shared Nixpkgs Go-builder behavior changes.

## Hypothesis history

### Hypothesis A — remove only `-mod=vendor`

Result: **partially confirmed and rejected as a complete restoration.**

Run `30586416205` reached real `checkPhase` on x86_64-linux and aarch64-darwin and removed the original parser error. Both jobs then failed identically on the omitted fixture and Go 1.26 documentation output. This falsified the claim that one environment substitution was sufficient.

### Hypothesis B — coherent supported-toolchain restoration

Result: **confirmed at the exact fence.**

Run `30598687251` passed on x86_64-linux and aarch64-darwin. Both jobs:

- applied and displayed the one-file target diff;
- built with Go 1.25.12 and the materialized vendor tree;
- entered `Running phase: checkPhase`;
- reported `ok github.com/princjef/gomarkdoc/cmd/gomarkdoc`;
- completed the full package derivation;
- passed `gomarkdoc.tests.version` with output `1.1.0`;
- retained exact logs as workflow artifacts.

Fieldwork integrity run `30598687241` passed at the same executed documentation head.

## Historical precedent

### Current Nixpkgs containment

- Source: the pinned gomarkdoc package expression.
- Principle supported: disabling checks can contain an incompatible test environment.
- Important difference: containment restores buildability but not test coverage.

### Supported versioned Go builders

- Source: Nixpkgs package set at the exact source fence, including `buildGo125Module` use in current package expressions.
- Principle supported: a package may select a supported Go generation when source or generated-output compatibility requires it.
- Important difference: this candidate pins the final package and its tests coherently; it does not use an older toolchain only for tests.

## Alternatives considered

### Retained — package-local Go 1.25 restoration

Wins because it passed the full discriminating matrix without filtering tests, changing shared framework behavior, or making expected output tautological.

### Declined — test with Go 1.25 and ship Go 1.26

Would validate different generated documentation from the shipped binary.

### Declined — regenerate the golden during `preCheck`

Would copy candidate output over expected output and erase regression value.

### Declined — exclude `cmd/gomarkdoc` or use `-run`

Would remove the package that owns the original collision and documentation behavior.

### Declined — framework-wide GOFLAGS change

Evidence is package-specific and does not justify changing every Go package.

### Rollback — keep `doCheck = false`

Remains the current containment if the compatibility pin is rejected.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Linux and Darwin | run `30598687251` | both passed |
| Offline vendor-backed build | Nix builder logs | passed with materialized modules and `GOPROXY=off` framework |
| Real command package | grep assertion and test output | passed |
| Full discovered set rather than filtered subset | unchanged `buildGoModule` check loop | passed |
| Version interface | `gomarkdoc.tests.version` | `1.1.0` on both jobs |
| Exact target fence | printed `git diff` and pinned checkout | one package file |
| Negative comparison under Go 1.26 | run `30586416205` | failed after clearing original collision |

## Edge cases outside scope

| Edge case | Why outside scope | Reopening trigger |
| --- | --- | --- |
| Future gomarkdoc releases | release may repair fixtures or goldens | package update |
| Future Go versions | output contract may change again | builder update or failed checks |
| Other Nixpkgs platforms | bounded matrix used one Linux and one Darwin system | platform-specific report or delivery requirement |
| Other packages parsing `GOFLAGS` | no second reproduction | separate package finding |
| Public Nixpkgs proposal | no authority | explicit user authorization |

## Exact execution and receipts

| Repository/head | Command or workflow | Environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| Fieldwork prior head / `30583406545` | first matrix | Linux + Darwin | unsupported `nix-build -L`; harness failure | setup only |
| Fieldwork prior head / `30586416205` | GOFLAGS-only candidate | Linux + Darwin, Go 1.26.5 | original collision cleared; two later failures | `target-executed` negative comparison |
| executed patch generation `1cdbcfa…` / `30598687251` | package build, full check phase, version passthru | x86_64-linux, Go 1.25.12 | success | `target-executed` |
| same | same | aarch64-darwin, supported Go 1.25 builder | success | `target-executed` |
| Fieldwork head `19931964…` / `30598687241` | Fieldwork integrity | GitHub-hosted runner | success | repository gate |

## Complete-diff and compatibility review

- Target changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix` only.
- The package API and main program remain unchanged.
- The final binary and tests use the same toolchain.
- Shared `buildGoModule` behavior remains unchanged.
- Temporary Fieldwork workflow is removed after receipt transfer; its absence requires the later cleanup head.
- Final acceptance still requires an independent review of the retained patch, this finding, the report, and cleanup-head integrity.

## Current disposition and routing

- Finding state: `review-ready`.
- Requested disposition: `ACCEPT` the bounded research candidate or `REPAIR` a concrete compatibility/source defect.
- Exact next transition: confirm cleanup-head integrity and complete-diff review.
- Clearing condition: independent acceptance at the final workflow-free Fieldwork head.
- Non-delegable human decision: none for research completion; public submission or merge authority remains separate.

## Changes to the conclusion

| Date | Evidence | Change |
| --- | --- | --- |
| 2026-07-31 | run `30586416205` | GOFLAGS-only repair reclassified from expected solution to insufficient first hypothesis |
| 2026-07-31 | run `30598687251` | coherent Go 1.25 restoration confirmed on Linux and Darwin |

No public Nixpkgs or gomarkdoc issue, pull request, comment, reaction, or message was created.