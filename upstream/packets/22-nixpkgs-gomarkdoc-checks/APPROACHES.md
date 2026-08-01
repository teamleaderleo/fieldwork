# Approaches — unit 22 gomarkdoc checks

## In simple words

The selected source keeps the command-only installation target and clears that selector only before standard Go test discovery. It also keeps the previously exercised Go 1.25, fixture, and `GOFLAGS` setup. The major rejected options either leave tests disabled, repeat the one-package false positive, widen the package build, duplicate the Go builder, or turn a one-package repair into a shared-builder change.

One detail remains a legitimate review question: upstream issue #516481 and gomarkdoc source show that `-mod=vendor` produces a benign parser diagnostic. Keeping the token is therefore a viable narrower variant, although the selected candidate removes the build-only flag from the application parser as assigned.

## Decision

Selected: keep `subPackages` for binary installation, then clear it inside `preCheck` so the standard Nixpkgs Go check phase discovers the full test set.

Canonical source: [`94be3956403ebf368b9d8262fdc9e5a5d2e80683`](https://github.com/teamleaderleo/nixpkgs/commit/94be3956403ebf368b9d8262fdc9e5a5d2e80683)

Current disposition: `HOLD` pending exact-head Linux/Darwin execution, Linux `nixpkgs-review`, Fieldwork integrity, receipt transfer, and carrier closure.

## Approach A — leave `doCheck = false`

### Advantages

- package build remains green;
- current behavior is merged and cached;
- zero test execution cost during package builds.

### Problems

- every upstream test remains bypassed;
- root, language, formatter, and command regressions receive no package signal;
- open upstream issue #516481 remains contained rather than repaired.

### Disposition

Rejected. This is the current containment.

## Approach B — retain the old Fieldwork candidate unchanged

Components:

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

`subPackages = [ "cmd/gomarkdoc" ]` also narrowed check discovery. The root, `lang`, and format packages never ran. The old report's full-suite claim was incorrect.

### Disposition

Superseded as a final candidate. Retained as partial execution evidence and compatibility prior art.

## Approach C — remove `subPackages` from the expression

### Advantages

- generic build and test discovery would cover every Go package;
- no custom phase logic.

### Problems

- installation would attempt every buildable package instead of the intended command package;
- output contents and build behavior could expand;
- it mixes test restoration with a binary-target change.

### Disposition

Rejected. It alters the product build fence.

## Approach D — replace the whole `checkPhase`

A package-local `checkPhase` could call `go test` over a manual list or `go list ./...`.

### Advantages

- explicit test package control;
- easy to assert an exact package list.

### Problems

- duplicates Nixpkgs' `buildGoDir` behavior;
- must carry `checkFlags`, tags, parallelism, vet behavior, debug output, and future builder changes;
- raises long-term maintenance cost for a one-package compatibility fix.

### Disposition

Rejected while the standard check phase can express the requirement.

## Approach E — add a second test-only derivation

The package could remain unchecked while `passthru.tests` builds a separate derivation that runs the suite.

### Advantages

- normal package builds stay lighter;
- test setup can differ independently.

### Problems

- ordinary Hydra package builds still skip upstream tests;
- duplicates source and Go setup;
- leaves the package's `doCheck` behavior misleading;
- expands the expression and review surface.

### Disposition

Rejected. Direct package checks are the more accurate restoration.

## Approach F — change generic `buildGoModule`

The builder could gain `checkSubPackages`, or always discover tests separately from build targets.

### Advantages

- declarative package expression;
- potentially reusable for other packages with narrow build targets.

### Problems

- broad builder change for one demonstrated package;
- extensive compatibility and regression burden;
- independent design discussion and target-wide testing required;
- exceeds unit 22's one-package scope.

### Disposition

Rejected for this contribution. A generalized builder enhancement belongs in a separate unit.

## Approach G — update gomarkdoc beyond 1.1.0

A newer revision might avoid the fixture or golden behavior.

### Advantages

- could remove compatibility workarounds;
- delivers upstream features and fixes.

### Problems

- no newer tagged release was established by this unit;
- source and vendor hashes would change;
- update review would require changelog, dependency, behavior, and compatibility analysis;
- test restoration becomes entangled with a version update.

### Disposition

Rejected for unit 22. Nixpkgs still packages 1.1.0.

## Approach H — patch or regenerate the documentation golden

### Advantages

- could allow the current default Go builder;
- avoids a package-specific Go pin.

### Problems

- dynamically regenerating expected output from the candidate erases regression value;
- carrying a static golden patch requires proving Go 1.26 output is intended for gomarkdoc 1.1.0;
- expands the source patch beyond package configuration;
- future Go output changes remain an upgrade question.

### Disposition

Rejected with current evidence. Reopen when a gomarkdoc release or maintainer record establishes the newer golden as intended.

## Approach I — keep `-mod=vendor` during checks

### Basis

Open Nixpkgs issue [#516481](https://github.com/NixOS/nixpkgs/issues/516481) calls the unknown-flag messages benign. gomarkdoc's [`defaultTags()`](https://github.com/princjef/gomarkdoc/blob/v1.1.0/cmd/gomarkdoc/command.go) returns `nil` after a parse error.

A narrower variant could therefore use Go 1.25, synthesize the fixture, clear `subPackages`, and leave `GOFLAGS` unchanged.

### Advantages

- fewer environment mutations;
- preserves Nixpkgs' explicit `-mod=vendor` token throughout the check phase;
- targets only the observed fixture/golden blockers plus discovery.

### Problems

- gomarkdoc's application parser still receives a Nix build-system option and emits diagnostics;
- the assignment explicitly calls for avoiding leaked Nix `GOFLAGS`;
- the previously successful command-package path used token removal;
- a comparative exact-head full-suite run has not been prepared.

### Disposition

Viable alternative, not selected. Reopen if a reviewer objects to test-time token removal or the selected matrix reveals vendor-mode uncertainty.

## Approach J — selected check-time selector reset

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
- the standard builder still controls tags, flags, parallelism, vet behavior, output handling, vendor materialization, and offline module mode;
- the source diff remains one file;
- it preserves the assignment's semantic boundary between Nix build flags and gomarkdoc application flags.

### Risks

1. **Shell representation risk**
   - `subPackages` is converted through Nixpkgs' `concatTo` helper.
   - execution must prove that `subPackages=()` reaches fallback discovery on both platforms.

2. **Toolchain pin risk**
   - `buildGo125Module` is a compatibility pin for 1.1.0's golden output.
   - future cleanup may prefer an upstream version update.

3. **Fixture synthesis risk**
   - the empty config is generated in the disposable build tree.
   - reviewers should confirm that an empty file, rather than absent configuration, is the intended fixture.

4. **`GOFLAGS` mutation risk**
   - the candidate removes one token only during tests.
   - old execution supports vendor-backed offline build behavior; repaired exact-head execution remains pending.

## Selected validation fence

The current carrier head [`b6003f2a3523f01880ff5690798b69afcb4e11f5`](https://github.com/teamleaderleo/fieldwork/commit/b6003f2a3523f01880ff5690798b69afcb4e11f5) must show:

- exact source head and parent;
- one changed package file;
- `git diff --check` success;
- package build success on x86_64-linux and aarch64-darwin;
- executable installed `bin/gomarkdoc` and usable help output;
- check phase execution;
- root package test result;
- `lang` package test result;
- format-package test result;
- command-package test result;
- at least four distinct gomarkdoc package result lines;
- version passthru output `1.1.0`;
- Linux `nixpkgs-review rev HEAD --no-shell` success;
- current Fieldwork-integrity success;
- transferred artifacts and closed execution carrier.

Hydra, ofborg, merge-queue, fresh-public-head, authorization, and independent-review gates remain later boundaries.
