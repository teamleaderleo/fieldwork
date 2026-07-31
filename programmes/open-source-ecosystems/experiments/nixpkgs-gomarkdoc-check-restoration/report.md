# Nixpkgs gomarkdoc check restoration

## TL;DR

Removing Nixpkgs' `-mod=vendor` token from gomarkdoc's test environment clears the original parser collision, but it does not restore the v1.1.0 suite on current Go 1.26.

The executed Linux/Darwin matrix exposed two additional release-level assumptions:

- command tests reference an empty `.gomarkdoc-empty.yml` fixture absent from the tag;
- the docs golden expects field-link resolution that changes under Go 1.26.

The current package-local experiment builds and tests the final binary with supported `buildGo125Module`, removes only `-mod=vendor` during checks, and creates the omitted empty config in the disposable build tree.

## Input → action → result

### Baseline containment

Input: gomarkdoc 1.1.0 under Nixpkgs `buildGoModule`.  
Action: `doCheck = false`.  
Result: package builds; no upstream tests execute.

### First restoration candidate

Input: current Go 1.26.5 builder and real vendored source.  
Action: enable checks and remove only `-mod=vendor` in `preCheck`.  
Result: both Linux and Darwin reach `checkPhase`; the original GOFLAGS error is gone; command tests fail on the absent config fixture and changed docs output.

### Current restoration candidate

Input: the same exact Nixpkgs and gomarkdoc revisions.  
Action: use supported Go 1.25 for both build and test, remove `-mod=vendor`, and create the omitted empty fixture.  
Expected result: full upstream suite and version passthru pass on both platforms without filtering tests or changing shared builder behavior.

## Exact fences

- Nixpkgs: `bbbd95e512a066deaefa89e3a244b541ed6c8c7f`;
- gomarkdoc: v1.1.0;
- package path: `pkgs/by-name/go/gomarkdoc/package.nix`;
- framework path: `pkgs/build-support/go/module.nix`;
- Fieldwork issue: #241;
- Fieldwork PR: #265;
- second-candidate patch head: `1cdbcfa7bf07086ed9a46f440d3595595afdd241`.

## Current target patch

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

The vendor tree remains materialized and `GOPROXY=off` remains owned by the shared builder. The empty fixture is created in the temporary source tree and is not installed.

## Why the same toolchain matters

The failed golden describes generated documentation produced by the final binary. Testing with Go 1.25 while shipping a Go 1.26 binary would validate different behavior. The current experiment therefore changes the package builder coherently for both compilation and tests.

## Executed matrix

Run `30586416205` on x86_64-linux and aarch64-darwin proved:

- exact package patch application;
- real offline vendored build;
- entry into `checkPhase`;
- clearance of the original `-mod=vendor` parsing failure;
- identical remaining failures under Go 1.26.5;
- docs golden divergence at field-link resolution;
- missing `.gomarkdoc-empty.yml` in tests that request it.

Fieldwork integrity run `30586416247` passed at the same prior head.

## Required current result

Each platform job must:

1. build the exact patched package;
2. show `Running phase: checkPhase`;
3. show successful `github.com/princjef/gomarkdoc/cmd/gomarkdoc` output;
4. run the full discovered test set without exclusion or `-run` filtering;
5. pass `gomarkdoc.tests.version`;
6. retain logs and a one-file Nixpkgs target diff.

## Rejected shortcuts

- dynamically regenerate expected docs from candidate output;
- exclude the command package that owns the defect;
- test with a different Go version than the shipped binary;
- remove vendoring flags framework-wide;
- call the Go 1.26 failures platform-specific.

## Evidence boundary

This is an owned cross-platform package experiment. It does not propose a public Nixpkgs patch, update gomarkdoc fixtures, or establish compatibility beyond the exact revisions and two named platforms.

## Current disposition

`research-active / EXECUTE GO 1.25 COHERENT RESTORATION`.

No public upstream interaction occurred or is authorized.