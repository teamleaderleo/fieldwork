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

The candidate was also compared with the current checks-disabled Go 1.26 package. Their installed `gomarkdoc` binaries are byte-for-byte identical and share SHA-256:

```text
b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e
```

The package version, source hash, vendor hash, build toolchain, command selection, linker flags, installed output, and version passthru remain unchanged.

## Things done

- Built on platform:
  - [ ] x86_64-linux — exact-head run pending
  - [ ] aarch64-linux
  - [ ] x86_64-darwin
  - [x] aarch64-darwin
- Tested, as applicable:
  - [ ] `cmd/gomarkdoc` checks on x86_64-linux.
  - [x] `cmd/gomarkdoc` checks on aarch64-darwin.
  - [ ] Installed `gomarkdoc --help` on x86_64-linux.
  - [x] Installed `gomarkdoc --help` on aarch64-darwin.
  - [ ] Version passthru prints `1.1.0` on x86_64-linux.
  - [x] Version passthru prints `1.1.0` on aarch64-darwin.
  - [x] Installed binary matches the checks-disabled Go 1.26 baseline byte-for-byte on aarch64-darwin.
- [ ] Ran `nixpkgs-review rev HEAD --no-shell` on x86_64-linux.
- Nixpkgs Release Notes:
  - [x] No release-note entry; installed output is unchanged.
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

The Darwin checkboxes reflect exact source head `3a036ab91fa1de2fbbd038b2b212552cff1cc5bf`, run `30692966149`, job `91350898702`. Linux remains pending.

The broader root/library suite is outside the package's existing command-only selection and contains additional standard-library documentation expectations. This PR does not skip, patch, or claim coverage for those packages.

## Public interaction status

This is a retained draft. No public Nixpkgs pull request, issue comment, reaction, or maintainer contact occurred.
