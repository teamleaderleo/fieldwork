# Upstream pull-request draft — unit 22 gomarkdoc checks

Proposed title:

```text
gomarkdoc: restore command checks
```

Proposed body:

---

Closes #516481.

gomarkdoc 1.1.0 currently has `doCheck = false`. Restore the checks for the selected `cmd/gomarkdoc` package while preserving the existing command-only build and installed output.

The tagged command tests need three package-local compatibility adjustments:

- use `buildGo125Module` because the retained v1.1.0 command golden matches Go 1.25 output;
- create the empty `.gomarkdoc-empty.yml` fixture referenced by the tagged tests;
- remove Nix's build-only `-mod=vendor` token before gomarkdoc parses `GOFLAGS` as application flags.

The unknown-flag diagnostic recorded in #516481 is benign by itself; the missing empty fixture is the observed public failure. Removing the token keeps a build-system flag out of gomarkdoc's application parser.

`subPackages = [ "cmd/gomarkdoc" ]` remains unchanged, so the standard Go builder runs the tests corresponding to the built command. The source hash, vendor hash, linker flags, installed program, and version passthru are unchanged.

## Things done

- Built on platform:
  - [ ] x86_64-linux — exact-head job pending
  - [ ] aarch64-linux
  - [ ] x86_64-darwin
  - [x] aarch64-darwin
- Tested, as applicable:
  - [ ] Package build with selected command checks enabled on x86_64-linux.
  - [x] Package build with selected command checks enabled on aarch64-darwin.
  - [ ] Installed `gomarkdoc --help` path on x86_64-linux.
  - [x] Installed `gomarkdoc --help` path on aarch64-darwin.
  - [ ] `gomarkdoc.tests.version` prints `1.1.0` on x86_64-linux.
  - [x] `gomarkdoc.tests.version` prints `1.1.0` on aarch64-darwin.
- [ ] Ran `nixpkgs-review rev HEAD --no-shell` on x86_64-linux.
- Nixpkgs Release Notes:
  - [x] No release-note entry; package version and interface are unchanged.
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

The aarch64-darwin checkboxes reflect exact-head job `91345125710` from run `30690828310`. Linux remains pending. The Darwin job verified source identity, the one-file fence, command-package check output, installed help, and version `1.1.0`.

A separate full-discovery experiment is intentionally excluded from the proposed public body. It reached root, command, and formatter tests but failed two `lang` exact-text assertions on both platforms because modern Go standard-library comments use bracketed documentation links. This PR neither skips nor rewrites those library-package tests; it restores the checks selected by the package's existing command build boundary.

The final authorized submission must:

1. rebase or regenerate the one-file commit on a fresh current `master`;
2. rerun every exact-head gate;
3. fill Linux checkboxes from the final receipts;
4. recheck current contribution and disclosure requirements;
5. preserve `Closes #516481` only if the issue still owns this regression.

## Current source identity

- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`
- Branch: `teamleaderleo/nixpkgs:fieldwork/unit-22-gomarkdoc-checks`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Refreshed public head: `63c4c8011115076be7a315edd8f740fd751b168a`
- Public-head distance: 384 commits from the candidate base
- Relevant overlap in the checked advance: none

## Current execution identity

- Fieldwork carrier PR: `#437`
- Carrier head: `c95da0c4b3f460df9bc8f342e98d05345da66df8`
- Target run: `30690828310`
- Darwin job: `91345125710` — success
- Darwin artifact: `8815619734`
- Darwin artifact digest: `sha256:db5516d38b64307b5d67ffb6bc23c33028dbdeaeb2b681b60a1cc7440958021a`
- Linux job: `91345125742` — queued at latest check
- Carrier integrity run: `30690828341`
- Packet disposition: `HOLD`

## Public interaction status

This is a retained draft. No public Nixpkgs pull request, comment, reaction, or maintainer contact occurred, and no authority to perform one has been granted.
