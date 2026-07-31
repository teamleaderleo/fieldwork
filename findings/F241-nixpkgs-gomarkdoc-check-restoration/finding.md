# F241 — Nixpkgs gomarkdoc check restoration

Finding state: `research-active — second hypothesis executing`

Canonical issue: #241  
Execution carrier: PR #265  
Exact Nixpkgs fence: `bbbd95e512a066deaefa89e3a244b541ed6c8c7f`  
Package: `gomarkdoc` 1.1.0  
Candidate patch head: `1cdbcfa7bf07086ed9a46f440d3595595afdd241`  
Upstream contact authorized: `no`

## TL;DR

The original package comment identified a real defect: Nixpkgs injects `GOFLAGS=-mod=vendor`, and gomarkdoc's in-process command tests parse that package-manager flag as application input.

Removing only `-mod=vendor` successfully gets both Linux and Darwin into the real upstream test suite. It does not restore the suite by itself. The executed matrix exposed two independent v1.1.0 compatibility problems:

1. the release tests reference `.gomarkdoc-empty.yml`, but that file is absent from the release tag;
2. the checked documentation golden expects symbol-link resolution that changes under Go 1.26, turning a previously linked field reference into broken-link text.

The second bounded candidate builds and tests the final package with Nixpkgs' supported Go 1.25 builder, removes only `-mod=vendor` during checks, and creates the omitted empty config fixture in the disposable build tree.

## Explain like I'm five

The first lock on the test door was Nix's extra flag. Removing it opened the door. Inside, two more things were broken: a test asks for an empty file that was never shipped, and the newest Go version writes one documentation link differently from the file the test expects.

The current experiment uses the older supported Go toolchain that matches the expected output and supplies the missing empty file only while testing.

## Why care

Keeping `doCheck = false` hides every upstream regression. Enabling the suite without understanding its failures would either break the package or encourage broad test suppression. A valid restoration must run meaningful tests against the same toolchain used to build the shipped binary.

## Governing contract

- keep the repair package-local;
- preserve the materialized vendor tree and offline build;
- run the real upstream packages rather than replacing them with synthetic tests;
- build and test with the same Go toolchain;
- avoid dynamically regenerating expected output from the candidate under test;
- retain the existing version passthru check;
- keep public upstream read-only.

## Exact source map

At the pinned Nixpkgs revision:

- `pkgs/by-name/go/gomarkdoc/package.nix` uses `buildGoModule` and sets `doCheck = false`;
- `pkgs/build-support/go/module.nix` materializes `vendor/`, exports `GOPROXY=off`, adds `-mod=vendor`, and runs each discovered test package in `checkPhase`;
- `buildGo125Module` is a supported package builder at the same revision;
- gomarkdoc v1.1.0's `cmd/gomarkdoc/command_test.go` references `../.gomarkdoc-empty.yml`;
- `.gomarkdoc-empty.yml` is absent from the v1.1.0 release tag;
- `testData/docs/README.md` expects `*AnotherStruct.Field` to resolve to an anchor link.

## Hypothesis history

### Hypothesis A — remove only `-mod=vendor`

```nix
preCheck = ''
  export GOFLAGS="''${GOFLAGS//-mod=vendor/}"
'';
```

Result: **partially confirmed, insufficient as a full restoration.**

Cross-platform run `30586416205` reached `Running phase: checkPhase` on x86_64-linux and aarch64-darwin. The original `-mod=vendor` parser failure was gone. Both platforms then failed identically inside `github.com/princjef/gomarkdoc/cmd/gomarkdoc` because of the missing empty config fixture and the documentation golden mismatch under Go 1.26.5.

This is target evidence. It falsifies the claim that one environment substitution restores the full suite.

### Hypothesis B — coherent supported-toolchain restoration

Current package-only patch:

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

Rationale:

- Go 1.25 is a supported Nixpkgs builder at the exact fence;
- the shipped binary and its tests use the same toolchain;
- the missing fixture is explicitly empty by name and test intent, and is created only in the disposable source tree;
- expected documentation is not regenerated from candidate output;
- shared `buildGoModule` semantics remain unchanged.

## Rejected or deferred alternatives

### Test with Go 1.25 but ship a Go 1.26 binary

Rejected. The failing golden describes behavior of the generated documentation, so a different test toolchain would not validate the shipped binary.

### Dynamically replace the golden during `preCheck`

Rejected. Copying candidate output over expected output makes the comparison tautological and erases regression value.

### Exclude `cmd/gomarkdoc` or use a narrow `-run` filter

Deferred. That package owns the exact GOFLAGS collision and documentation behavior under investigation. Excluding it would restore only unrelated packages and leave the package's primary command surface untested.

### Framework-wide GOFLAGS change

Rejected at current evidence. The collision is package-specific; changing every Go package would require a separate cross-package campaign.

### Permanent `doCheck = false`

Current containment remains the rollback boundary, not the preferred conclusion.

## Executed evidence

| Head/run | Platform | Result | Classification |
| --- | --- | --- | --- |
| `641f2e2…` / `30583406545` | Linux + Darwin | `nix-build` rejected workflow flag `-L` | harness failure |
| `5f14c1a…` / `30586416247` | Fieldwork integrity | passed | repository gate |
| `5f14c1a…` / `30586416205` | x86_64-linux | entered `checkPhase`; command tests failed after GOFLAGS repair | target-executed discriminator |
| same | aarch64-darwin | same independent failures under Go 1.26.5 | target-executed cross-platform discriminator |
| `1cdbcfa…` | Linux + Darwin | second candidate pending | target-test-prepared |

## Exact failure interpretation

What run `30586416205` proves:

- the Nix expression evaluates on both platforms;
- the one-file patch applies cleanly;
- vendored, offline compilation reaches the real test phase;
- removing `-mod=vendor` clears the original parser collision;
- the remaining failures reproduce across Linux and Darwin;
- the failure is not a runner-only or Nix-install issue.

What it does not prove:

- that Go 1.25 restores the expected symbol-link output;
- that creating the empty fixture clears every GOFLAGS test;
- that the package and version passthru pass;
- that pinning Go 1.25 has no other compatibility consequence.

## Current decision criteria

The second candidate advances only if one exact head proves:

1. package evaluation and build on x86_64-linux and aarch64-darwin;
2. `Running phase: checkPhase` in both logs;
3. successful `cmd/gomarkdoc` test output;
4. successful full discovered test set, not a filtered subset;
5. successful `gomarkdoc.tests.version`;
6. target diff limited to `pkgs/by-name/go/gomarkdoc/package.nix`;
7. complete-diff review and temporary-workflow retirement decision.

## Evidence boundary

The matrix covers two Nixpkgs platforms and the exact package expression. It does not establish behavior for future Go versions, other gomarkdoc releases, other Nixpkgs revisions, or other packages that parse `GOFLAGS`.

## Current disposition

`EXECUTE HYPOTHESIS B`.

If the Go 1.25 matrix passes, the candidate becomes a reviewable package-local compatibility restoration. If it fails, classify the exact remaining test before considering fixture patching or a deliberately reduced stable subset.

No public Nixpkgs or gomarkdoc issue, pull request, comment, reaction, or message was created.