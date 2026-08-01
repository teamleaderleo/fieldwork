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

The unknown-flag diagnostic recorded in #516481 is benign by itself; the missing empty fixture is the observed public failure. Removing the token keeps build-system flags out of the application parser.

`subPackages = [ "cmd/gomarkdoc" ]` is still needed for installation, but `buildGoModule` also uses that selector during `checkPhase`. Clear it in `preCheck` so the standard test discovery runs the root, `lang`, format, and command packages.

The source hash, vendor hash, linker flags, installed program, and version passthru remain unchanged.

## Things done

- Built on platform:
  - [ ] x86_64-linux — exact-head run queued
  - [ ] aarch64-linux
  - [ ] x86_64-darwin
  - [ ] aarch64-darwin — exact-head run queued
- Tested, as applicable:
  - [ ] Package build with upstream checks enabled at the proposed source head.
  - [ ] Root, `lang`, format, and `cmd/gomarkdoc` test results observed on x86_64-linux.
  - [ ] Root, `lang`, format, and `cmd/gomarkdoc` test results observed on aarch64-darwin.
  - [ ] Installed `gomarkdoc --help` path executed on x86_64-linux.
  - [ ] Installed `gomarkdoc --help` path executed on aarch64-darwin.
  - [ ] `gomarkdoc.tests.version` prints `1.1.0` on x86_64-linux.
  - [ ] `gomarkdoc.tests.version` prints `1.1.0` on aarch64-darwin.
- [ ] Ran `nixpkgs-review rev HEAD --no-shell` on this change — queued on x86_64-linux.
- Nixpkgs Release Notes:
  - [x] No release-note entry; package version and interface are unchanged.
- NixOS Release Notes:
  - [x] Not applicable.
- [ ] Fits `CONTRIBUTING.md`, `pkgs/README.md`, and other relevant instructions at submission time.

## Commands

```console
$ nix-build . -A gomarkdoc --no-out-link
$ nix-build . -A gomarkdoc.tests.version --no-out-link
$ nixpkgs-review rev HEAD --no-shell
```

---

## Draft synchronization notes

The platform and test checkboxes remain empty until the exact repaired source head produces terminal receipts. Active execution targets x86_64-linux and aarch64-darwin and also checks installed-binary help plus Linux `nixpkgs-review`.

The final authorized submission should:

1. rebase or regenerate the one-file commit on a fresh current `master`;
2. rerun every exact-head gate;
3. replace queued text with exact tested platforms, commands, and receipts;
4. recheck the current pull-request template, contribution rules, and any disclosure requirement;
5. preserve `Closes #516481` unless that issue has changed state or scope.

## Current source identity

- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- Branch: `teamleaderleo/nixpkgs:fieldwork/unit-22-gomarkdoc-checks`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Checked later public head: `f8e81fc7eb063db454f563cdd596fb96a5ad1497`
- Relevant overlap in the checked public advance: none

## Current execution identity

- Fieldwork carrier PR: `#437`
- Carrier head: `b6003f2a3523f01880ff5690798b69afcb4e11f5`
- Target run: `30674969557`
- Linux job: `91300175276`
- Darwin job: `91300175296`
- Fieldwork-integrity run: `30674969559`
- Packet disposition: `HOLD`

## Public interaction status

This is a retained draft. No public Nixpkgs pull request, comment, reaction, or maintainer contact occurred, and no authority to perform one has been granted.
