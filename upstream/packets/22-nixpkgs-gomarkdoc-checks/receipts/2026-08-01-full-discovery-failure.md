# Receipt — full gomarkdoc discovery fails on modern Go 1.25

Date: `2026-08-01`  
Work class: `target-executed negative control`  
Source base: `55096b0ce13784d4f6420059c5627475fa26ebb1`  
Source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`  
Carrier head: `b6003f2a3523f01880ff5690798b69afcb4e11f5`  
Workflow run: [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557) — `failure`  
Fieldwork integrity: [`30674969559`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969559) — `success`

## Source controls

Both platform jobs verified:

- exact source head `94be3956403ebf368b9d8262fdc9e5a5d2e80683`;
- exact parent `55096b0ce13784d4f6420059c5627475fa26ebb1`;
- one changed file: `pkgs/by-name/go/gomarkdoc/package.nix`;
- `git diff --check` success.

The candidate cleared `subPackages` in `preCheck`, proving that the standard Go builder then discovered the broader test set.

## x86_64-linux

- Job: `91300175276` — `failure`
- Runner: Ubuntu 24.04
- Nix: 2.35.1
- Go: 1.25.12
- Artifact: [`8810710677`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557/artifacts/8810710677)
- Artifact digest: `sha256:bb7ba3579d8157fa344d1a6e7ba30a5cedf1f32f4f1f1d4eb2e3b2cd077b1a75`

Observed package results before failure:

```text
ok github.com/princjef/gomarkdoc
ok github.com/princjef/gomarkdoc/cmd/gomarkdoc
ok github.com/princjef/gomarkdoc/format
ok github.com/princjef/gomarkdoc/format/formatcore
FAIL github.com/princjef/gomarkdoc/lang
```

## aarch64-darwin

- Job: `91300175296` — `failure`
- Runner: macOS 14.8.7 arm64
- Nix: 2.35.1
- Go: 1.25.12
- Artifact: [`8810556627`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557/artifacts/8810556627)
- Artifact digest: `sha256:f471756f78106e2b74945a96e5596487baa234f33c3bae83f28195f54dfa106d`

Observed package results were identical to Linux.

## Decisive failures

Both platforms failed the same two `lang` assertions:

```text
TestFunc_textScannerInit
actual:   Init initializes a [Scanner] with a new source and returns s.
expected: Init initializes a Scanner with a new source and returns s.

TestFunc_ioIoutilTempFile
actual:   TempFile creates a new temporary file in the directory dir, opens the file for reading and writing, and returns the resulting *[os.File].
expected: TempFile creates a new temporary file in the directory dir, opens the file for reading and writing, and returns the resulting *os.File.
```

The v1.1.0 tests compare exact standard-library documentation text. Modern Go 1.25 standard-library comments use bracketed documentation links, and gomarkdoc's summary path preserves those brackets. The failure is deterministic across the two hosted platforms.

## Coverage boundary

Established:

- check-time selector reset reaches the broad package set;
- root, command, and formatter packages pass under Go 1.25.12;
- `lang` has two exact-text compatibility failures;
- the failure is a package/test compatibility result, not checkout, Nix installation, source-fence, or runner setup.

Unexecuted after the package failure:

- installed binary help control;
- version passthru;
- Linux `nixpkgs-review`.

## Resulting decision

The full-discovery candidate is superseded. Unit 22 retains command-package check restoration, matching the package's existing `subPackages = [ "cmd/gomarkdoc" ]` build boundary. The two language golden tests are not skipped or rewritten in this unit.
