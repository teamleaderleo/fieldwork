# Tests and receipts — unit 22 gomarkdoc checks

## Current conclusion

The target experiments identify Go 1.25 as the only required repair ingredient. The simplified clean source head `5c17b14e271611c3418e3e2f572366766f6aa3cc` has not yet received exact-head Linux and Darwin execution.

Disposition: `EXECUTE`.

## Canonical source fence

- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `5c17b14e271611c3418e3e2f572366766f6aa3cc`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Relation: one commit, one file, 4 additions, 6 deletions

## Historical branch/toolchain control

| Snapshot | Branch class | Unversioned Go | gomarkdoc source/vendor/selection |
| --- | --- | --- | --- |
| `4590696c...` | release-25.11 backport | Go 1.25 | unchanged |
| `acd02b877...` | master | Go 1.26 | unchanged |

Evidence class: `source-read`.

## Repair-isolation execution

- Initial setup-only failure: run `30692303477`, job `91349062757`; exact carrier history was unavailable because checkout depth was one. No package source ran.
- Corrected run: [`30692403974`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692403974)
- Job: `91349338842` — success
- Platform: macOS 14.8.7 arm64, image `macos-14-arm64` version `20260629.0180.1`
- Nix: 2.35.1
- Carrier head: `c1b0b0f1ffb92d989e84cfceefe1ab18b8b670bb`
- Tested source checkout: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`, with package variants generated in the disposable checkout
- Artifact: [`8816151764`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692403974/artifacts/8816151764)
- Digest: `sha256:8597cc8e25daa9975c20a36c1a824d939820f373bc8a0521d2a022ac60e5471e`
- Size: 10840 bytes; 12 files
- Expiry: 2026-08-31T08:49:53Z

| Variant | Status | checkPhase | command result |
| --- | ---: | ---: | ---: |
| Go 1.25 + fixture + flag cleanup | 0 | observed | pass |
| Go 1.25 + fixture only | 0 | observed | pass |
| Go 1.25 + flag cleanup only | 0 | observed | pass |
| Go 1.25 only | 0 | observed | pass |
| Go 1.26 + fixture + flag cleanup | 1 | observed | fail |

The Go 1.26 failure is `TestCommand/./docs`, a generated markdown mismatch. The Go 1.25-only variant proves the fixture and flag cleanup are unnecessary.

Evidence class: `target-executed comparative experiment`.

Detailed receipt: [`receipts/2026-08-01-repair-isolation.md`](./receipts/2026-08-01-repair-isolation.md).

## Prior command-package execution

Runs `30598626867` and `30598687251` passed the Go 1.25 command-package path and version on Linux and Darwin, but use an older source generation.

Run `30690828310`, Darwin job `91345125710`, passed source head `569c0c4d...` with fixture and flag cleanup. Artifact `8815619734`, digest `sha256:db5516d38b64307b5d67ffb6bc23c33028dbdeaeb2b681b60a1cc7440958021a`.

These receipts support Go 1.25 compatibility but do not replace execution at `5c17b14e...`.

## Full-discovery negative control

- Source: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- Run: `30674969557` — failure
- Integrity: `30674969559` — success
- Linux job `91300175276`, artifact `8810710677`, digest `sha256:bb7ba3579d8157fa344d1a6e7ba30a5cedf1f32f4f1f1d4eb2e3b2cd077b1a75`
- Darwin job `91300175296`, artifact `8810556627`, digest `sha256:f471756f78106e2b74945a96e5596487baa234f33c3bae83f28195f54dfa106d`

Passing before failure:

```text
ok github.com/princjef/gomarkdoc
ok github.com/princjef/gomarkdoc/cmd/gomarkdoc
ok github.com/princjef/gomarkdoc/format
ok github.com/princjef/gomarkdoc/format/formatcore
```

Failing:

```text
FAIL github.com/princjef/gomarkdoc/lang
[Scanner] != Scanner
*[os.File] != *os.File
```

Evidence class: `target-executed negative control`.

## Next exact-head commands

```bash
nix-build .target/nixpkgs -A gomarkdoc --no-out-link
nix-build .target/nixpkgs -A gomarkdoc.tests.version --no-out-link
nixpkgs-review rev HEAD --no-shell  # Linux
```

The carrier must also execute installed `gomarkdoc --help`, assert exactly one selected gomarkdoc package result, retain the source diff, and upload logs and artifacts.

## Current missing evidence

- x86_64-linux exact head `5c17b14e...`;
- aarch64-darwin exact head `5c17b14e...`;
- Linux `nixpkgs-review` for that head;
- Fieldwork integrity covering the packet consuming those receipts.
