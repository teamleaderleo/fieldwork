# Upstream pull-request draft — unit 22 gomarkdoc checks

Proposed title:

```text
gomarkdoc: restore command checks
```

Proposed body:

---

Closes #516481.

gomarkdoc 1.1.0's checks pass on the Go 1.25 release line and fail on current Go 1.26 because the command tests compare generated documentation output.

Pin the package to `buildGo125Module` and remove `doCheck = false`. The existing `subPackages = [ "cmd/gomarkdoc" ]` selection remains unchanged, so the standard Go builder runs the tests for the command that Nixpkgs builds and installs.

A comparison of the issue's reproducer revisions shows that the passing revision is a `release-25.11` backport using Go 1.25, while the failing revision is on master using Go 1.26. A five-variant run also shows that creating `.gomarkdoc-empty.yml` and removing Nix's `-mod=vendor` flag are not required: Go 1.25 passes without either, and Go 1.26 fails with both.

The package version, source hash, vendor hash, command selection, linker flags, and version passthru remain unchanged.

This pin changes the Go toolchain used by the installed binary and can affect generated documentation. It is a compatibility pin for the dormant v1.1.0 release and should be revisited when gomarkdoc is updated or Go 1.25 is removed from Nixpkgs.

## Things done

- Built on platform:
  - [ ] x86_64-linux — simplified exact head pending
  - [ ] aarch64-linux
  - [ ] x86_64-darwin
  - [ ] aarch64-darwin — simplified exact head pending
- Tested, as applicable:
  - [ ] `cmd/gomarkdoc` checks on x86_64-linux.
  - [ ] `cmd/gomarkdoc` checks on aarch64-darwin.
  - [ ] Installed `gomarkdoc --help` on x86_64-linux.
  - [ ] Installed `gomarkdoc --help` on aarch64-darwin.
  - [ ] Version passthru prints `1.1.0` on x86_64-linux.
  - [ ] Version passthru prints `1.1.0` on aarch64-darwin.
- [ ] Ran `nixpkgs-review rev HEAD --no-shell` on x86_64-linux.
- Nixpkgs Release Notes:
  - [x] No release-note entry; package version and CLI are unchanged.
- NixOS Release Notes:
  - [x] Not applicable.
- [ ] Rechecked current contribution instructions and pull-request template at submission time.

## Commands

```console
$ nix-build . -A gomarkdoc --no-out-link
$ nix-build . -A gomarkdoc.tests.version --no-out-link
$ nixpkgs-review rev HEAD --no-shell
```

---

## Draft synchronization notes

The checklist remains empty until exact source head `5c17b14e271611c3418e3e2f572366766f6aa3cc` produces terminal receipts.

The broader root/library suite is outside the package's existing command-only selection and contains standard-library documentation expectations requiring Go 1.21 or older. This PR does not skip, patch, or claim coverage for those packages.

## Public interaction status

This is a retained draft. No public Nixpkgs pull request, issue comment, reaction, or maintainer contact occurred.
