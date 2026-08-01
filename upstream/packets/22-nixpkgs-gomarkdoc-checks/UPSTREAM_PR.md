# Upstream pull-request draft — unit 22 gomarkdoc checks

Proposed title:

```text
gomarkdoc: restore full upstream checks
```

Proposed body:

---

Closes #516481.

gomarkdoc 1.1.0 currently has `doCheck = false`. Restore its Go tests package-locally while preserving the command-only installed output.

The package needs three compatibility adjustments:

- use `buildGo125Module` because the checked v1.1.0 documentation golden matches Go 1.25 output;
- create the empty `.gomarkdoc-empty.yml` fixture referenced by the tagged command tests;
- remove Nix's build-only `-mod=vendor` token before gomarkdoc parses `GOFLAGS` as application flags.

`subPackages = [ "cmd/gomarkdoc" ]` is still needed for installation, but `buildGoModule` also uses that selector during `checkPhase`. Clear it in `preCheck` so the standard test discovery runs the root, `lang`, format, and command packages.

The source hash, vendor hash, linker flags, installed program, and version passthru remain unchanged.

## Things done

- Built on platform:
  - [ ] x86_64-linux
  - [ ] aarch64-linux
  - [ ] x86_64-darwin
  - [ ] aarch64-darwin
- Tested, as applicable:
  - [ ] Package build with upstream checks enabled.
  - [ ] Root, `lang`, format, and `cmd/gomarkdoc` test results observed.
  - [ ] `gomarkdoc.tests.version` prints `1.1.0`.
- [ ] Ran `nixpkgs-review` on this change.
- [ ] Tested basic functionality of `gomarkdoc`.
- Nixpkgs Release Notes:
  - [x] No release-note entry; package version and interface are unchanged.
- NixOS Release Notes:
  - [x] Not applicable.
- [ ] Fits `CONTRIBUTING.md`, `pkgs/README.md`, and other relevant instructions.

## Commands

```console
$ nix-build . -A gomarkdoc --no-out-link
$ nix-build . -A gomarkdoc.tests.version --no-out-link
```

---

## Draft synchronization notes

The platform and test checkboxes remain empty until the exact repaired source head produces terminal receipts. Prepared execution targets x86_64-linux and aarch64-darwin.

The final authorized submission should:

1. rebase or regenerate the one-file commit on current `master` if relevant paths moved;
2. replace this note with exact tested platforms and commands;
3. add `nixpkgs-review` results when executed;
4. test the installed `gomarkdoc` binary;
5. recheck the current pull-request template, contribution rules, and any disclosure requirement;
6. preserve `Closes #516481` unless that issue has changed state or scope.

## Current source identity

- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- Branch: `teamleaderleo/nixpkgs:fieldwork/unit-22-gomarkdoc-checks`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`

## Public interaction status

This is a retained draft. No public Nixpkgs pull request was opened, and no authority to open one has been granted.
