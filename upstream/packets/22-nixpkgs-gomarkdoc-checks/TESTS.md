# Tests and receipts — unit 22 gomarkdoc checks

## Current conclusion

The selected Go 1.26 golden candidate passes exact aarch64-darwin command, help, and version checks and produces a byte-identical installed binary to the current checks-disabled baseline. Linux and packet integrity remain.

Disposition: `EXECUTE`.

## Canonical source fence

- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `3a036ab91fa1de2fbbd038b2b212552cff1cc5bf`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Relation: one commit, one file, six additions, four deletions

## Historical branch/toolchain control

| Snapshot | Line | Unversioned Go | gomarkdoc package |
| --- | --- | --- | --- |
| `4590696c...` | release-25.11 | Go 1.25 | same version/hash/selection |
| `acd02b877...` | master | Go 1.26 | same version/hash/selection |

Evidence class: `source-read`.

## Repair-isolation execution

- Corrected run: [`30692403974`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692403974)
- Job: `91349338842` — success
- Artifact: `8816151764`
- Digest: `sha256:8597cc8e25daa9975c20a36c1a824d939820f373bc8a0521d2a022ac60e5471e`

| Variant | Result |
| --- | --- |
| Go 1.25 + fixture + flag cleanup | pass |
| Go 1.25 + fixture only | pass |
| Go 1.25 + flag cleanup only | pass |
| Go 1.25 only | pass |
| Go 1.26 + both cleanups | fail |

Conclusion: fixture and flag edits are unnecessary; Go 1.26 command output differs.

Detailed receipt: [`receipts/2026-08-01-repair-isolation.md`](./receipts/2026-08-01-repair-isolation.md).

## Go 1.26 golden comparison

- Run: [`30692966149`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692966149)
- Job: `91350898702` — success
- Carrier head: `9bdb7ce730010ac953e4f6d66cba752bdfb9449a`
- Candidate source: `3a036ab91fa1de2fbbd038b2b212552cff1cc5bf`
- Baseline source: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Platform: macOS 14.8.7 arm64, image `macos-14-arm64` version `20260629.0180.1`
- Nix: 2.35.1
- Go: 1.26.5

Established:

```text
Running phase: checkPhase
ok github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

Additional controls:

- exactly one gomarkdoc package result;
- installed help output accepted;
- version passthru printed `1.1.0`;
- checks-disabled baseline and checks-enabled candidate binaries passed `cmp`;
- both binaries had SHA-256 `b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e`.

Artifact:

- ID: [`8816337182`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692966149/artifacts/8816337182)
- Digest: `sha256:14ae794f8160a5f6c68bcf113dd430d628fa4b8399ad9ceb65f1d5f33770e5e1`
- Size: 5974 bytes
- Files: 7
- Created: 2026-08-01T09:05:53Z
- Expires: 2026-08-31T09:05:52Z

Evidence class: `target-executed comparative acceptance control`.

Detailed receipt: [`receipts/2026-08-01-go126-golden-comparison.md`](./receipts/2026-08-01-go126-golden-comparison.md).

## Full-discovery negative control

- Source: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`
- Run: `30674969557` — failure
- Integrity: `30674969559` — success
- Linux artifact `8810710677`, digest `sha256:bb7ba3579d8157fa344d1a6e7ba30a5cedf1f32f4f1f1d4eb2e3b2cd077b1a75`
- Darwin artifact `8810556627`, digest `sha256:f471756f78106e2b74945a96e5596487baa234f33c3bae83f28195f54dfa106d`

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

## Superseded pin execution

The Go 1.25 source `5c17b14e...` passed exact aarch64-darwin command/help/version gates in run `30692796676`. This remains useful alternative evidence but is not the canonical source.

## Required Linux commands

```bash
nix-build .target/nixpkgs -A gomarkdoc --no-out-link
nix-build .target/nixpkgs -A gomarkdoc.tests.version --no-out-link
nixpkgs-review rev HEAD --no-shell
```

The carrier must also verify exact source identity, one changed file, `diff --check`, one package result, installed help, and artifact upload.

## Current missing evidence

- x86_64-linux exact source `3a036ab9...`;
- Linux `nixpkgs-review` for that source;
- Fieldwork integrity covering the packet that consumes the final receipts.
