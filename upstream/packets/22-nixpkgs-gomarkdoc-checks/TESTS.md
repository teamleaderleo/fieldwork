# Tests and receipts — unit 22 gomarkdoc checks

## Current conclusion

The selected command-package repair passes its exact-head aarch64-darwin package, command-check, installed-help, and version gates. A clean packet-anchored x86_64-linux gate, including `nixpkgs-review`, and Fieldwork integrity are queued.

A separate exact-head full-discovery experiment failed deterministically in two `lang` exact-text assertions on both platforms. That negative control is retained and the selected source does not hide those failures.

Disposition: `HOLD`.

## Canonical source fence

- Repository: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Branch: `fieldwork/unit-22-gomarkdoc-checks`
- Base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Head: [`569c0c4d11e5a14f3fe6237c0a50dc484f80e744`](https://github.com/teamleaderleo/nixpkgs/commit/569c0c4d11e5a14f3fe6237c0a50dc484f80e744)
- Compare: [`55096b0c...569c0c4d`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...569c0c4d11e5a14f3fe6237c0a50dc484f80e744)
- Changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Commit relation: one commit above the exact base

## Current public-head check

- Public `master` head checked: [`63c4c8011115076be7a315edd8f740fd751b168a`](https://github.com/NixOS/nixpkgs/commit/63c4c8011115076be7a315edd8f740fd751b168a)
- Checked at: `2026-08-01T08:02:42Z`
- Distance from candidate base: 384 commits ahead
- Relevant overlap in that advance: none for `pkgs/by-name/go/gomarkdoc/package.nix` or `pkgs/build-support/go/module.nix`
- Current public package state: version `1.1.0`, `subPackages = [ "cmd/gomarkdoc" ]`, `doCheck = false`
- Current builder state: nonempty `subPackages` still controls test selection; `preCheck` still runs before `getGoDirs test`

This is a staleness assessment, not execution at the public head. A fresh-head rebase and exact-head rerun remain mandatory before authorized submission.

## Source-read results

### gomarkdoc v1.1.0

- `defaultTags()` parses `GOFLAGS` as application flags, accepts `-tags`, emits a diagnostic for unknown tokens, and returns no tags after parse failure.
- Command tests reference an empty `.gomarkdoc-empty.yml` fixture omitted from the v1.1.0 tag.
- Tests exist in root, `lang`, formatter, and command packages.
- `lang/func_test.go` compares exact summaries from Go standard-library comments and expects pre-link text without `[Scanner]` or `[os.File]`.

Evidence class: `source-read`.

## Prior successful command-package execution

### Run A

- Patch head: `1cdbcfa7bf07086ed9a46f440d3595595afdd241`
- Run: [`30598626867`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867)

| Platform | Job | Conclusion | Artifact | Established |
| --- | ---: | --- | ---: | --- |
| x86_64-linux | `91056349644` | success | `8781532516` | package build, `cmd/gomarkdoc`, version `1.1.0` |
| aarch64-darwin | `91056349617` | success | `8781695770` | package build, `cmd/gomarkdoc`, version `1.1.0` |

### Run B

- Carrier head: `19931964ec50d687025d5cc7953b9c29eab7b395`
- Patch head: `1cdbcfa7bf07086ed9a46f440d3595595afdd241`
- Run: [`30598687251`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251)

| Platform | Job | Conclusion | Artifact | Digest | Expiry |
| --- | ---: | --- | ---: | --- | --- |
| x86_64-linux | `91056528367` | success | [`8781677778`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251/artifacts/8781677778) | `sha256:7016240f3caaa54af84d0d277ca5dd69a5d05cadcca20fa1c50cd42dbaedd11c` | 2026-08-30 |
| aarch64-darwin | `91056528347` | success | [`8781795710`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251/artifacts/8781795710) | `sha256:a24bbf13b9c0fccacaecad8c8a17d0c244fb6580393a0266ec704522f686957c` | 2026-08-30 |

Both runs emitted:

```text
Running phase: checkPhase
ok github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

They establish command-package compatibility on the older candidate. They do not establish broader upstream-suite coverage.

## Exact-head full-discovery negative control

- Superseded source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- Carrier head: `b6003f2a3523f01880ff5690798b69afcb4e11f5`
- Run: [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557) — `failure`
- Integrity run: [`30674969559`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969559) — `success`
- Detailed receipt: [`receipts/2026-08-01-full-discovery-failure.md`](./receipts/2026-08-01-full-discovery-failure.md)

| Platform | Job | Result | Artifact | Digest |
| --- | ---: | --- | ---: | --- |
| x86_64-linux | `91300175276` | deterministic `lang` failure | `8810710677` | `sha256:bb7ba3579d8157fa344d1a6e7ba30a5cedf1f32f4f1f1d4eb2e3b2cd077b1a75` |
| aarch64-darwin | `91300175296` | deterministic `lang` failure | `8810556627` | `sha256:f471756f78106e2b74945a96e5596487baa234f33c3bae83f28195f54dfa106d` |

Both jobs verified the exact source head, parent, one-file fence, and `git diff --check`. Both used Nix 2.35.1 and Go 1.25.12.

Passing packages before failure:

```text
ok github.com/princjef/gomarkdoc
ok github.com/princjef/gomarkdoc/cmd/gomarkdoc
ok github.com/princjef/gomarkdoc/format
ok github.com/princjef/gomarkdoc/format/formatcore
```

Failing package and assertions:

```text
FAIL github.com/princjef/gomarkdoc/lang

actual:   Init initializes a [Scanner] with a new source and returns s.
expected: Init initializes a Scanner with a new source and returns s.

actual:   ... returns the resulting *[os.File].
expected: ... returns the resulting *os.File.
```

Classification: `target-executed negative control`. This is a package/test compatibility failure. Package failure prevented installed-help, version, and Linux `nixpkgs-review` from running.

## Current exact-head command-check evidence

Detailed receipt: [`receipts/2026-08-01-command-checks.md`](./receipts/2026-08-01-command-checks.md)

### aarch64-darwin — executed

- Carrier head: `c95da0c4b3f460df9bc8f342e98d05345da66df8`
- Run: [`30690828310`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310)
- Job: `91345125710` — `success`
- Runner: macOS 14.8.7 arm64; image `macos-14-arm64` version `20260629.0180.1`
- Nix: 2.35.1
- Go: 1.25.12
- Source head, parent, one-file fence, and `git diff --check`: success
- Selected package result count: exactly one
- Check result: `ok github.com/princjef/gomarkdoc/cmd/gomarkdoc`
- Installed help: `generate markdown documentation for golang code` and `Usage:`
- Version passthru: `1.1.0`
- Artifact: [`8815619734`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310/artifacts/8815619734)
- Digest: `sha256:db5516d38b64307b5d67ffb6bc23c33028dbdeaeb2b681b60a1cc7440958021a`
- Size: 5478 bytes; five files
- Linux-only review step: skipped as designed

Evidence class: `target-executed`.

### x86_64-linux — packet-anchored gate

- Packet base: `527021b7ff1535e8be4f27dc3ba7226b559a1630`
- Carrier head: `178e6388bf06b965970dd3ab7435db9e756a13e4`
- Carrier relation: one commit and one workflow file
- Run: [`30691551270`](https://github.com/teamleaderleo/fieldwork/actions/runs/30691551270)
- Job: `91347062784`
- State at this packet update: queued
- Required additional gate: `nixpkgs-review rev HEAD --no-shell`

Prepared assertions:

- carrier parent equals packet base;
- exact source head and parent;
- one changed package file and `git diff --check` success;
- selected command check and exactly one gomarkdoc package result;
- installed help output;
- version passthru `1.1.0`;
- Linux `nixpkgs-review`;
- exact artifact upload.

Evidence class: `target-test-prepared`.

### Packet-anchored integrity

- Packet base: `527021b7ff1535e8be4f27dc3ba7226b559a1630`
- Carrier head: `178e6388bf06b965970dd3ab7435db9e756a13e4`
- Run: [`30691551312`](https://github.com/teamleaderleo/fieldwork/actions/runs/30691551312)
- Job: `91347062807`
- State at this packet update: queued

This integrity generation covers packet content through `527021b7ff1535e8be4f27dc3ba7226b559a1630` plus the one-file carrier. Subsequent packet changes are receipt and status reconciliation and must be identified as such.

### Superseded queued jobs

- Linux job `91345125742` in run `30690828310` remained queued after the carrier branch was rebuilt. It is superseded by job `91347062784`.
- Integrity job `91345125771` in run `30690828341` is superseded by job `91347062807`.

## Commands

```bash
nix-build .target/nixpkgs -A gomarkdoc --no-out-link
nix-build .target/nixpkgs -A gomarkdoc.tests.version --no-out-link
nixpkgs-review rev HEAD --no-shell  # x86_64-linux
```

## Runtime limit

The active local runtime has no `nix` or `nix-build`; hosted Actions provides the target evidence.

## Gates outside the current receipt

- terminal packet-anchored x86_64-linux package/check/help/version/review receipt;
- terminal packet-anchored integrity receipt;
- carrier closure after evidence transfer;
- independent complete-diff review;
- fresh-public-head rebase and exact-head rerun;
- Hydra, ofborg, and merge-queue evidence after an authorized public Nixpkgs PR;
- explicit public-contact authority.
