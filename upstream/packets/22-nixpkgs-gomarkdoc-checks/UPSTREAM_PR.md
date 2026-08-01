# Upstream pull-request draft — gomarkdoc checks

Public posting authority: `absent`

## Proposed title

`gomarkdoc: restore full upstream checks`

## Draft body

## Description of changes

Restore gomarkdoc 1.1.0's upstream checks with package-local compatibility adjustments:

- build the package with Go 1.25, matching the release's generated-document golden output;
- remove only `-mod=vendor` from test-time `GOFLAGS`, because command tests pass that environment value to gomarkdoc's application flag parser;
- create the empty `.gomarkdoc-empty.yml` fixture omitted from the release tag;
- clear the build-only `subPackages` selector during `preCheck`, allowing the standard `buildGoModule` check phase to discover the root, `lang`, format, and command test packages.

The package still builds and installs only `cmd/gomarkdoc`. The source hash and vendor hash remain unchanged, and the standard builder continues to use the materialized vendor tree with offline module resolution.

## Things done

- Built on platform:
  - [ ] x86_64-linux — pending current execution receipt
  - [ ] aarch64-linux
  - [ ] x86_64-darwin
  - [ ] aarch64-darwin — pending current execution receipt
- Tested, as applicable:
  - [x] Package's upstream Go checks are enabled in the derivation.
  - [ ] Confirmed root, `lang`, format, and `cmd/gomarkdoc` package results on x86_64-linux — pending current execution receipt.
  - [ ] Confirmed root, `lang`, format, and `cmd/gomarkdoc` package results on aarch64-darwin — pending current execution receipt.
  - [ ] Confirmed `gomarkdoc.tests.version` on x86_64-linux — pending current execution receipt.
  - [ ] Confirmed `gomarkdoc.tests.version` on aarch64-darwin — pending current execution receipt.
- [ ] Ran `nixpkgs-review` on this change.
- [ ] Tested basic functionality of the installed binary beyond the existing version passthru.
- [x] No release-note entry needed for this package check restoration.
- [x] The change is limited to `pkgs/by-name/go/gomarkdoc/package.nix`.

## Reviewer focus

Please check whether resetting `subPackages` inside `preCheck` is the preferred package-local way to retain a narrow install target while letting the generic Go check phase discover every test package.

## Packet-only submission notes

These notes stay outside the upstream body:

- Exact base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Exact source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- Clean source branch: `teamleaderleo/nixpkgs:fieldwork/unit-22-gomarkdoc-checks`
- Complete compare: `55096b0ce13784d4f6420059c5627475fa26ebb1...94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- Current execution carrier: Fieldwork PR #437 / run 30674476739
- Update the checklist from terminal receipts before any authorized submission.
- Recheck the target's current contribution and disclosure requirements immediately before submission.
