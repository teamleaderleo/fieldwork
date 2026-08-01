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

The issue's passing reproducer is a `release-25.11` snapshot using Go 1.25, while the failing revision is master using Go 1.26. A separate variant matrix shows that creating `.gomarkdoc-empty.yml` and removing Nix's `-mod=vendor` flag are not required.

The changed file under `testData` is an expected-output fixture: tests generate `README-test.md` and compare it with `README.md`. Current-base baseline and candidate installed `gomarkdoc` binaries are byte-for-byte identical.

The package version, source hash, vendor hash, Go toolchain, command selection, linker flags, and version passthru remain unchanged.

## Things done

- Built on platform:
  - [x] x86_64-linux
  - [ ] aarch64-linux
  - [ ] x86_64-darwin
  - [x] aarch64-darwin
- Tested, as applicable:
  - [x] `cmd/gomarkdoc` checks on x86_64-linux.
  - [x] `cmd/gomarkdoc` checks on aarch64-darwin.
  - [x] Installed `gomarkdoc --help` on both tested platforms.
  - [x] Version passthru prints `1.1.0` on both tested platforms.
  - [x] Current-base installed binary matches the checks-disabled baseline on aarch64-darwin.
- [x] Ran `nixpkgs-review rev -b 97d48ba11e7eeb6896e9da8d64b22b306da14103 HEAD --no-shell` on x86_64-linux; one package built (`gomarkdoc`).
- Nixpkgs Release Notes:
  - [x] No release-note entry expected; product source, toolchain, and installed executable are unchanged.
- NixOS Release Notes:
  - [x] Not applicable.
- [ ] Rechecked current contribution instructions and pull-request template at submission time.

## Commands

```console
$ nix-build . -A gomarkdoc --no-out-link
$ nix-build . -A gomarkdoc.tests.version --no-out-link
$ nixpkgs-review rev -b 97d48ba11e7eeb6896e9da8d64b22b306da14103 HEAD --no-shell
```

---

## Draft synchronization notes

- Source head: `e8d97d5d8c67a9473a7aaad3961c0630583aa34b`
- Linux run/job: `30694249810` / `91354242933`
- Darwin run/job: `30693522616` / `91352347312`
- Broader root/library packages are outside the existing command-only selection and are not claimed here.

## Public interaction status

This is a retained draft. No public Nixpkgs pull request, issue comment, reaction, or maintainer contact occurred.
