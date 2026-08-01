# Approaches — unit 22 gomarkdoc checks

## Decision

Selected: keep the binary build selector, then clear `subPackages` inside `preCheck` so the standard Nixpkgs Go check phase discovers the full test set.

Canonical source: [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683)

## Approach A — leave `doCheck = false`

### Advantages

- package build remains green;
- current behavior is already merged and cached;
- zero execution cost during package builds.

### Problems

- every upstream test remains bypassed;
- the known incompatibilities stay undocumented by executable package behavior;
- future toolchain or packaging regressions receive no signal.

### Disposition

Rejected. This is containment, not restoration.

## Approach B — retain the old candidate unchanged

Candidate components:

- `buildGo125Module`;
- `doCheck = true`;
- remove `-mod=vendor` during tests;
- create `.gomarkdoc-empty.yml`.

### Advantages

- Linux and Darwin package builds succeeded;
- command-package tests succeeded;
- version passthru succeeded;
- source and vendor hashes stayed stable.

### Problems

`subPackages = [ "cmd/gomarkdoc" ]` also narrowed check discovery. The root, `lang`, and format packages never ran. The old report's full-suite claim was therefore incorrect.

### Disposition

Superseded as a final candidate. Retained as partial execution evidence and compatibility prior art.

## Approach C — remove `subPackages` from the expression

### Advantages

- generic build and test discovery would cover all Go packages;
- no custom phase logic.

### Problems

- installation would attempt every buildable package instead of the intended command package;
- output contents and build behavior could expand;
- it mixes the desired test-set repair with a binary-target change.

### Disposition

Rejected. It alters the product build fence.

## Approach D — replace the whole `checkPhase`

A package-local `checkPhase` could call `go test` over a manually specified package list or `go list ./...`.

### Advantages

- explicit test package control;
- easy to assert an exact package list.

### Problems

- duplicates Nixpkgs' `buildGoDir` behavior;
- must carry `checkFlags`, tags, parallelism, vet behavior, Nix debug behavior, and future builder changes;
- raises long-term maintenance cost for a one-package compatibility fix.

### Disposition

Rejected while the standard check phase can express the requirement.

## Approach E — add a second test-only derivation

The package could remain unchecked while `passthru.tests` builds a separate derivation that runs the suite.

### Advantages

- normal package builds stay lightweight;
- package test can use independent configuration.

### Problems

- regular Hydra package builds still skip upstream tests;
- duplicates source and Go setup;
- leaves the package's own `doCheck` behavior misleading;
- larger expression and review surface.

### Disposition

Rejected. Direct package checks are the more accurate restoration.

## Approach F — change generic `buildGoModule`

The builder could gain separate `checkSubPackages` support or always discover test packages independently.

### Advantages

- reusable for other packages with narrower build targets than test targets;
- declarative package expression.

### Problems

- broad builder change for one demonstrated package;
- extensive compatibility and regression burden;
- independent design discussion and target-wide testing required;
- exceeds unit 22's one-package scope.

### Disposition

Rejected for this contribution. A future generalized builder enhancement would be a separate unit.

## Approach G — update gomarkdoc beyond 1.1.0

A newer upstream revision might avoid one or more compatibility gaps.

### Advantages

- could remove the old golden or fixture behavior;
- delivers upstream features and fixes.

### Problems

- no newer tagged release was established by this unit;
- source and vendor hashes would change;
- update review would need changelog, dependency, behavior, and compatibility analysis;
- test restoration becomes entangled with a version update.

### Disposition

Rejected for unit 22. The current package version remains 1.1.0 upstream.

## Approach H — selected check-time selector reset

```nix
preCheck = ''
  export GOFLAGS="''${GOFLAGS//-mod=vendor/}"
  touch .gomarkdoc-empty.yml
  subPackages=()
'';
```

### Why it fits

- `buildPhase` has already used `subPackages` to install only `cmd/gomarkdoc`;
- `checkPhase` invokes `preCheck` before `getGoDirs test`;
- the empty array makes `getGoDirs test` discover directories containing tests;
- the standard builder still controls tags, flags, parallelism, vet behavior, output handling, and offline module mode;
- the source diff remains one file.

### Risks

1. **Shell representation risk**
   - `subPackages` is converted through Nixpkgs' `concatTo` helper.
   - execution must prove that `subPackages=()` reaches the fallback discovery path on both tested platforms.

2. **Toolchain pin risk**
   - `buildGo125Module` is a compatibility pin for 1.1.0's golden output.
   - future Nixpkgs cleanup may require an upstream version update instead.

3. **Fixture synthesis risk**
   - the empty config is generated in the build tree because Git omits empty files.
   - reviewers should confirm the command test expects an empty file rather than absent configuration.

4. **`GOFLAGS` mutation risk**
   - the candidate removes the `-mod=vendor` substring only during tests.
   - execution must continue to show that dependencies come from the materialized vendor tree with `GOPROXY=off`.

## Selected validation fence

The candidate must show all of the following on x86_64-linux and aarch64-darwin:

- exact source head and parent;
- one changed package file;
- `git diff --check` success;
- package build success;
- check phase executed;
- root package test result;
- `lang` package test result;
- format-package test result;
- command-package test result;
- at least four distinct gomarkdoc package result lines;
- version passthru output `1.1.0`.

Full Nixpkgs merge-queue and Hydra confidence remains a later authorized-upstream gate.
