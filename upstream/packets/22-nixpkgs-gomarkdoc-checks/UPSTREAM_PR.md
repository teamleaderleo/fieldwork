# Upstream pull-request draft — unit 22 gomarkdoc checks

Proposed title:

```text
gomarkdoc: update Go 1.26 command golden
```

Proposed body:

---

Closes #516481.

gomarkdoc 1.1.0's selected command tests compare generated markdown. Go 1.26 now resolves one field reference as a documentation link, so the retained fixture no longer matches.

Update that single expected line and remove `doCheck = false`. The existing `subPackages = [ "cmd/gomarkdoc" ]` selection remains unchanged, so the standard Go builder runs the tests for the command Nixpkgs builds and installs.

A comparison of the issue's reproducer revisions shows that the passing revision is a `release-25.11` snapshot using Go 1.25, while the failing revision is master using Go 1.26. A separate variant matrix shows that creating `.gomarkdoc-empty.yml` and removing Nix's `-mod=vendor` flag are not required.

A patch-equivalent candidate was compared with the checks-disabled Go 1.26 package. Their installed `gomarkdoc` binaries are byte-for-byte identical and share SHA-256:

```text
b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e
```

The final one-file commit is regenerated on current master head `97d48ba11e7eeb6896e9da8d64b22b306da14103`.

The package version, source hash, vendor hash, build toolchain, command selection, linker flags, and version passthru remain unchanged.

## Things done

- Built on platform:
  - [ ] x86_64-linux — current-base exact head pending
  - [ ] aarch64-linux
  - [ ] x86_64-darwin
  - [ ] aarch64-darwin — current-base exact head pending
- Tested, as applicable:
  - [ ] `cmd/gomarkdoc` checks on x86_64-linux.
  - [ ] `cmd/gomarkdoc` checks on aarch64-darwin.
  - [ ] Installed `gomarkdoc --help` on both target platforms.
  - [ ] Version passthru prints `1.1.0` on both target platforms.
  - [ ] Current-base installed binary matches the checks-disabled baseline on aarch64-darwin.
- [ ] Ran `nixpkgs-review rev HEAD --no-shell` on x86_64-linux.
- Nixpkgs Release Notes:
  - [x] No release-note entry expected; product source and toolchain are unchanged.
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

The checkboxes remain empty until exact current source head `e8d97d5d8c67a9473a7aaad3961c0630583aa34b` produces terminal receipts.

The broader root/library suite is outside the package's existing command-only selection and contains additional standard-library documentation expectations. This PR does not skip, patch, or claim coverage for those packages.

## Public interaction status

This is a retained draft. No public Nixpkgs pull request, issue comment, reaction, or maintainer contact occurred.
