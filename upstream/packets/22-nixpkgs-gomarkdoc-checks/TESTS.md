# Tests and receipts — unit 22 gomarkdoc checks

## Current conclusion

The command-package repair has prior Linux and Darwin execution evidence on an older base. A renewed full-discovery candidate ran at an exact clean source head and failed deterministically in two `lang` exact-text assertions on both platforms. The narrowed clean head is queued for current Linux/Darwin package, help, version, Linux `nixpkgs-review`, and Fieldwork-integrity execution.

Disposition: `HOLD`.

## Canonical source fence

- Repository: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Branch: `fieldwork/unit-22-gomarkdoc-checks`
- Base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Head: [`569c0c4d11e5a14f3fe6237c0a50dc484f80e744`](https://github.com/teamleaderleo/nixpkgs/commit/569c0c4d11e5a14f3fe6237c0a50dc484f80e744)
- Compare: [`55096b0c...569c0c4d`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...569c0c4d11e5a14f3fe6237c0a50dc484f80e744)
- Changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Commit relation: one commit above the exact base

## Source-read results

### Nixpkgs package and builder

- The package uses `subPackages = [ "cmd/gomarkdoc" ]` and currently has `doCheck = false` on the inspected public source.
- Generic Go check discovery uses `subPackages` when nonempty.
- `preCheck` runs before test directory selection.
- Clearing the shell array in `preCheck` reaches the broader test set; retaining it runs the selected command package only.

Evidence class: `source-read`, with execution confirmation from the full-discovery negative control.

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

Classification: `target-executed negative control`. This is a package/test compatibility failure, not a checkout, Nix installation, source-fence, or runner failure. Package failure prevented installed-help, version, and Linux `nixpkgs-review` steps from running.

## Current exact-head command-check execution

- Source head: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`
- Carrier PR: [#437](https://github.com/teamleaderleo/fieldwork/pull/437)
- Carrier head: `c95da0c4b3f460df9bc8f342e98d05345da66df8`
- Target run: [`30690828310`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310)
- Integrity run: [`30690828341`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828341)
- Current state at packet update: queued

### Commands

```bash
nix-build .target/nixpkgs -A gomarkdoc --no-out-link
nix-build .target/nixpkgs -A gomarkdoc.tests.version --no-out-link
nixpkgs-review rev HEAD --no-shell  # x86_64-linux
```

The workflow also executes the installed `gomarkdoc --help` path.

### Required assertions

Each platform must prove:

- exact source head and parent;
- one changed package file and `git diff --check` success;
- `Running phase: checkPhase`;
- successful `github.com/princjef/gomarkdoc/cmd/gomarkdoc` result;
- exactly one selected gomarkdoc package result line;
- installed executable and usable help output;
- version passthru output `1.1.0`.

Linux additionally runs `nixpkgs-review rev HEAD --no-shell`.

Evidence class while queued: `target-test-prepared`.

## Runtime limit

The active local runtime has no `nix` or `nix-build`; no local target-native command ran. Hosted Actions provides the target evidence.

## Gates outside the current receipt

- independent complete-diff review;
- fresh-public-head rebase and exact-head rerun;
- Hydra, ofborg, and merge-queue evidence after an authorized public Nixpkgs PR;
- explicit public-contact authority.

## Continuation receipt

After run `30690828310` is terminal, preserve runner images, job conclusions, source controls, command-package line, help output, version output, Linux `nixpkgs-review`, artifact IDs/digests/expiry, and the exact packet head consuming the result. Classify each skipped or failed step separately.
