# Package Collections Scout — Round 001

Date: 2026-07-30  
Programme: [Open-Source Ecosystems](../../STATUS.md)  
Scout issue: [#208](https://github.com/teamleaderleo/fieldwork/issues/208)

## In simple words

Package collections offer a continuing supply of useful work because each failure exposes both a packaged project and the machinery used to build, test, patch, and distribute it. The strongest reports already carry pinned revisions and direct build commands. The first lane should harvest those reports, then classify whether the correction belongs in the package, the shared build tooling, or upstream.

## Surfaces inspected

### Nixpkgs

Repository: `NixOS/nixpkgs`

Useful issue classes found in this round:

- silent feature loss after a platform or SDK transition;
- a package test phase disabled after a shared build-tool regression;
- known-good/known-bad revision comparisons;
- architecture-specific firmware or virtualization regressions;
- locally reproducible failures that Hydra does not reproduce.

### Homebrew Core

Repository: `Homebrew/homebrew-core`

Durable intake issues:

- [unsolved-formula tracker](https://redirect.github.com/Homebrew/homebrew-core/issues/139929) — formula updates blocked by build, test, or other unresolved failures;
- [OpenSSL 4 migration tracker](https://redirect.github.com/Homebrew/homebrew-core/issues/278366) — grouped by dependent count and build system;
- [architecture-independent bottle tracker](https://redirect.github.com/Homebrew/homebrew-core/issues/191352) — additional bottle candidates.

These trackers are better starting points than an unfiltered formula scan because they already express a package consequence and often expose logs or a failed automation path.

## Deep dive A — restore `gomarkdoc` tests

Issue: [`gomarkdoc` test-regression issue](https://redirect.github.com/NixOS/nixpkgs/issues/516481)

### Evidence

- Build succeeds at nixpkgs revision `4590696c8693fea477850fe379a01544293ca4e2`.
- `checkPhase` fails at `acd02b8` and later sampled revisions.
- The package version and package expression stayed unchanged across the reported regression window.
- Current `pkgs/by-name/go/gomarkdoc/package.nix` sets `doCheck = false`.
- The package comment attributes the failure to tests calling `main()` directly while nixpkgs exports `GOFLAGS=-mod=vendor`; gomarkdoc's parser accepts only `-tags`.
- The original issue also reports a missing `../.gomarkdoc-empty.yml`, so working-directory or subpackage test selection may be a second boundary.

### Likely owning areas

```text
pkgs/by-name/go/gomarkdoc/package.nix
pkgs/build-support/go/module.nix
gomarkdoc cmd/gomarkdoc tests
Go test environment and GOFLAGS handling
```

### First executable probe

1. Override `doCheck = true` on current nixpkgs.
2. Run the check with the package's current `subPackages` setting.
3. Repeat with `GOFLAGS` cleared, filtered to accepted flags, and left unchanged.
4. Record the test working directory and presence of `.gomarkdoc-empty.yml`.
5. Run the same matrix at the known-good revision.

Distinguishing outcomes:

- clearing or filtering `GOFLAGS` restores the suite;
- changing the test working directory or subpackage selection restores the fixture path;
- both changes are required;
- the upstream test itself relies on an unsupported invocation pattern.

### Promotion rule

Promote when the suite can be restored with a bounded package or shared-tool correction and the fix avoids hiding valid Go flags from ordinary packages. Retain a negative result if the upstream tests intentionally parse the process-wide `GOFLAGS` in a way incompatible with supported Go behavior.

## Deep dive B — AAVMF regression

Issue: [AAVMF regression issue](https://redirect.github.com/NixOS/nixpkgs/issues/485220)

The issue includes a QEMU script and pinned good and bad revisions. Firmware from stable reaches PXE behavior; sampled unstable revisions stop after the UEFI banner. No matching pull request was found in this round.

This belongs behind an aarch64 QEMU or VM capability gate. The first retained artifact should turn the observed console boundary into a pass/fail script and bisect package inputs rather than only nixpkgs commits.

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

- **Promote:** `gomarkdoc` into Linux Fieldwork LF-35.
- **Capability queue:** AAVMF.
- **Recurring intake:** Homebrew blocked updates and OpenSSL migration.
- **Stop duplicate implementation:** pandoc Lua and Darwin libffi.
- **Next scout expansion:** Debian reproducibility/autopkgtest and Fedora FTBFS after the first package probe is executable.