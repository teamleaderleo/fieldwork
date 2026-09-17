# Receipt — gomarkdoc repair isolation

Date: `2026-08-01`

## Purpose

Determine which proposed ingredients are actually required to restore the selected `cmd/gomarkdoc` checks:

- Go 1.25 pin;
- removal of Nix `-mod=vendor` from test-time `GOFLAGS`;
- creation of `.gomarkdoc-empty.yml`.

## Setup-only failed generation

- Run: `30692303477`
- Job: `91349062757`
- Result: setup failure
- Cause: the workflow checked out a synthetic PR merge with depth one, so `HEAD^` was unavailable.
- Product source checkout, Nix installation, and package tests: skipped

Classification: `harness failure`.

## Corrected execution

- Run: [`30692403974`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692403974)
- Job: `91349338842` — success
- Carrier branch: `p0/435-unit-22-execution`
- Carrier head: `c1b0b0f1ffb92d989e84cfceefe1ab18b8b670bb`
- Source checkout: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`
- Source parent: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Platform: macOS 14.8.7 arm64
- Runner image: `macos-14-arm64` version `20260629.0180.1`
- Nix: 2.35.1
- Go versions exercised: 1.25.12 and 1.26.5

## Matrix result

```text
variant                    status  check_phase  command_ok
current                    0       1            1
retain-nix-goflags         0       1            1
omit-empty-fixture         0       1            1
pin-only                   0       1            1
default-go-with-fixes      1       1            0
```

Interpretation:

- Go 1.25 passes with both cleanups.
- Go 1.25 passes when either cleanup is removed.
- Go 1.25 passes when both cleanups are removed.
- Go 1.26 fails even when both cleanups remain.

## Go 1.26 failure

The failing test is:

```text
--- FAIL: TestCommand
    --- FAIL: TestCommand/./docs
```

The generated markdown differs from the retained v1.1.0 expectation. One visible change resolves a field reference as a link instead of escaped literal text.

The later `flag provided but not defined: -other` message comes from a test that deliberately supplies an unknown GOFLAGS token. It appears in the package output because another subtest failed; successful Go tests normally suppress captured output.

## Artifact

- Artifact: [`8816151764`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692403974/artifacts/8816151764)
- Name: `unit-22-gomarkdoc-repair-isolation`
- Digest: `sha256:8597cc8e25daa9975c20a36c1a824d939820f373bc8a0521d2a022ac60e5471e`
- Size: 10840 bytes
- Files: 12
- Created: `2026-08-01T08:49:55Z`
- Expires: `2026-08-31T08:49:53Z`

## Conclusion

The Go 1.25 pin is required. The fixture and `GOFLAGS` edits are unnecessary and were removed from the clean source.

Evidence class: `target-executed comparative experiment`.
