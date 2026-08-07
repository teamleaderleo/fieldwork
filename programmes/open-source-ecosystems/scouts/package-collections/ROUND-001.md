# Package Collections Scout — Round 001

Date: 2026-07-30  
Disposition refresh: 2026-08-05  
Programme: [Open-Source Ecosystems](../../STATUS.md)  
Scout issue: [#208](https://github.com/teamleaderleo/fieldwork/issues/208)

## In simple words

Package collections offer a continuing supply of useful work because each failure exposes both a packaged project and the machinery used to build, test, patch, and distribute it. The strongest reports already carry pinned revisions and direct build commands. The first lane harvested those reports, then classified whether each correction belonged in the package, the shared build tooling, or upstream.

The gomarkdoc selection completed investigation and owner review. The user submitted [gomarkdoc: restore checks on Go 1.26](https://redirect.github.com/NixOS/nixpkgs/pull/549377). Canonical submission state is tracked in #241.

## Surfaces inspected

### Nixpkgs

Repository: `NixOS/nixpkgs`

Useful issue classes found in this round:

- silent feature loss after a platform or SDK transition;
- a package test phase disabled after a shared build-tool regression;
- known-good/known-bad revision comparisons;
- architecture-specific firmware or virtualization regressions;
- locally reproducible failures that Hydra doesn't reproduce.

### Homebrew Core

Repository: `Homebrew/homebrew-core`

Durable intake issues:

- [unsolved-formula tracker](https://redirect.github.com/Homebrew/homebrew-core/issues/139929) — formula updates blocked by build, test, or other unresolved failures;
- [OpenSSL 4 migration tracker](https://redirect.github.com/Homebrew/homebrew-core/issues/278366) — grouped by dependent count and build system;
- [architecture-independent bottle tracker](https://redirect.github.com/Homebrew/homebrew-core/issues/191352) — additional bottle candidates.

These trackers are better starting points than an unfiltered formula scan because they already express a package consequence and often expose logs or a failed automation path.

## Deep dive A — restore `gomarkdoc` tests

Issue: [`gomarkdoc` test-regression issue](https://redirect.github.com/NixOS/nixpkgs/issues/516481)  
Submitted pull request: [gomarkdoc: restore checks on Go 1.26](https://redirect.github.com/NixOS/nixpkgs/pull/549377)  
Current disposition: `submitted`

### Original evidence and hypotheses

- Build succeeded at Nixpkgs revision `4590696c8693fea477850fe379a01544293ca4e2`.
- `checkPhase` failed at `acd02b8` and later sampled revisions.
- The package version and package expression stayed unchanged across the reported regression window.
- `pkgs/by-name/go/gomarkdoc/package.nix` set `doCheck = false`.
- The package comment blamed tests calling `main()` while Nixpkgs exported `GOFLAGS=-mod=vendor`; gomarkdoc's parser accepted only `-tags`.
- The public issue also reported a missing `../.gomarkdoc-empty.yml`.

The first executable matrix varied inherited flags, supported-tag filtering, working directory, fixture presence, package selection, Go generation, and pinned Nixpkgs revisions.

### Final diagnosis

The visible `GOFLAGS` and missing-config diagnostics were captured output, not the failing assertion. Removing `-mod=vendor` and creating `.gomarkdoc-empty.yml` weren't sufficient.

The failing Go 1.26 assertion was one generated-Markdown expected-output difference: a field reference became a documentation link.

The selected repair:

- keeps the current Go 1.26 builder;
- retains `subPackages = [ "cmd/gomarkdoc" ]`;
- updates one expected Markdown line with `substituteInPlace --replace-fail`;
- removes `doCheck = false`;
- doesn't create the missing fixture or rewrite `GOFLAGS`;
- doesn't change the package version, source, vendor hash, linker flags, selected command, or installed executable.

Broader root, formatter, and `lang` package discovery exposed additional old standard-library prose goldens and wasn't selected. The contribution claim remains limited to the existing package-selected `cmd/gomarkdoc` tests.

### Submission and evidence boundary

- submitted branch: `teamleaderleo/nixpkgs:contrib/gomarkdoc-go126-checks`;
- submitted base: `356468b500e85491b610431c87a284ca1f41b7bc`;
- submitted head: `060a1f8b8af68af858be896715c5dfc540522235`;
- final package-file blob: `53f4eef322e84133c2c867070a55c60bb14e09ae`.

Prior Linux and Darwin execution applies to that identical package-file blob. Exact-current-head execution remains pending. The earlier Go 1.25/fixture/flag-filter candidate is superseded.

## Deep dive B — AAVMF regression

Issue: [AAVMF regression issue](https://redirect.github.com/NixOS/nixpkgs/issues/485220)

The issue includes a QEMU script and pinned good and bad revisions. Firmware from stable reaches PXE behavior; sampled unstable revisions stop after the UEFI banner. No matching pull request was found in this round.

This belongs behind an aarch64 QEMU or VM capability gate. The first retained artifact should turn the observed console boundary into a pass/fail script and bisect package inputs rather than only Nixpkgs commits.

Likely areas:

```text
OVMF/AAVMF package expression
edk2 build flags and firmware variants
QEMU machine and pflash compatibility
cross-compilation inputs
```

## Duplicate stops and reference examples

### Pandoc Lua feature regression

- Issue: [pandoc Lua feature issue](https://redirect.github.com/NixOS/nixpkgs/issues/540900)
- Active fix: [package PR](https://redirect.github.com/NixOS/nixpkgs/pull/540913)

The top-level static pandoc silently lost Lua support after an Apple SDK update. The active fix forces automatic default-on flags so future feature loss becomes a build failure. Retain this as the preferred package-test pattern.

### Darwin libffi on macOS 27

- Issue: [Darwin libffi issue](https://redirect.github.com/NixOS/nixpkgs/issues/541367)
- Active fix: [package PR](https://redirect.github.com/NixOS/nixpkgs/pull/541990)

Retain as a platform-transition diagnosis example. Stop independent implementation while the focused fix is active.

## Ranked next searches

1. Disabled checks in Nixpkgs packages with an open issue or explanatory comment.
2. Leaves in the Homebrew unsolved-formula tracker with current logs and no active pull request.
3. Automatic build features that silently disable themselves after SDK/compiler transitions.
4. Downstream patches whose upstream equivalent has landed.
5. Hydra-versus-local discrepancies with a small environment delta.
6. OpenSSL 4 leaf migrations from the Homebrew tracker.

## Return

- **Submitted:** `gomarkdoc` through Linux Fieldwork LF-35; monitor CI and maintainer review in #241 and `teamleaderleo/linux-fieldwork#136`.
- **Capability queue:** AAVMF.
- **Recurring intake:** Homebrew blocked updates and OpenSSL migration.
- **Stop duplicate implementation:** pandoc Lua and Darwin libffi.
- **Next scout expansion:** Debian reproducibility/autopkgtest and Fedora FTBFS after the first package probe is executable.

The user opened the submitted gomarkdoc pull request. Fieldwork automation didn't perform additional upstream contact.
