# Deep dive — unit 22 gomarkdoc checks

## Technical conclusion

The regression is a Go 1.26 generated-documentation golden mismatch. It is not caused by a missing empty config file or a fatal leaked Nix `GOFLAGS` token.

The selected repair keeps the current Go builder, updates one expected markdown line under `testData`, and restores the existing selected command-package checks. A patch-equivalent comparison proved the installed binary remains byte-identical to the checks-disabled baseline.

## Historical comparison

The public issue compares revisions from different Nixpkgs lines:

- `4590696c8693fea477850fe379a01544293ca4e2` is a `release-25.11` backport using Go 1.25.
- `acd02b8771d0546f96ee281ac45c3a6f81b9bfba` is a master revision using Go 1.26.
- The gomarkdoc source, vendor hash, version, and command selection remain materially unchanged.

This explains why the older branch passes and master fails without a package-source regression.

## Why the visible diagnostics were misleading

### Missing empty config

`command_test.go` requests `../.gomarkdoc-empty.yml`, but `buildConfig` prints `viper.ReadInConfig` errors without returning them. The Go 1.25 variant without the file passed.

### Unknown `GOFLAGS`

`defaultTags()` accepts only `-tags`, prints unknown-flag diagnostics, and returns no tags after parse failure. Upstream tests deliberately exercise unknown `GOFLAGS` and expect command success. The Go 1.25 variant retaining Nix flags passed.

Successful Go tests suppress captured output. When another subtest fails, package output exposes diagnostics from otherwise successful cases. The issue identified visible messages rather than the failing assertion.

## Exact Go 1.26 command failure

The failing subtest is `TestCommand/./docs`. One retained fixture line expects an escaped literal field reference:

```text
GetField gets \[\*AnotherStruct.Field\].
```

Go 1.26 generation resolves it as a documentation link:

```text
GetField gets [\\\*AnotherStruct.Field](<#AnotherStruct>).
```

Updating that one expected line makes the selected command package pass under Go 1.26.

## Binary-identity proof

The Go 1.26 comparison built the checks-disabled baseline and checks-enabled patch-equivalent candidate with the same Go 1.26.5 builder. The candidate patch touches only `testData/docs/README.md`. The installed binaries passed `cmp` and shared SHA-256:

```text
b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e
```

The final current-base commit contains the identical package blob used by that candidate.

## Current-base regeneration

- Public base: `97d48ba11e7eeb6896e9da8d64b22b306da14103`
- Canonical head: `e8d97d5d8c67a9473a7aaad3961c0630583aa34b`
- Package path before regeneration: unchanged disabled package blob `149e1cf1908f421132ba3f9bbe08588f9d424a92`
- Package path after regeneration: accepted candidate blob `53f4eef322e84133c2c867070a55c60bb14e09ae`

The old and current candidates have identical one-file package content. Exact current-base execution remains required because unrelated Nixpkgs dependencies and builders can move.

## Broader test packages

Clearing `subPackages` reaches the complete upstream package set. On Go 1.25, root, command, and formatter packages pass while `lang` fails on standard-library prose:

```text
[Scanner] != Scanner
*[os.File] != *os.File
```

The two old expectations jointly require Go 1.21 or older. Current Nixpkgs does not retain that as a supported fixed builder. Broad restoration would require more golden patches or skips and is not selected.

## Upstream intent

gomarkdoc v1.1.0 declares Go 1.18 and its CI pins Go 1.20.x on Linux, macOS, and Windows. The repository has seen no substantive maintenance since 2023. Exact documentation goldens therefore reflect an older Go documentation corpus.

## Selected source

The source:

1. removes the stale diagnostic-based disable-tests comment and `doCheck = false`;
2. adds a `postPatch` `substituteInPlace --replace-fail` for the one Go 1.26 command golden;
3. keeps the default Go builder, source/vendor hashes, command selection, linker flags, version test, and metadata.

## Why the Go 1.25 pin was rejected after execution

The pin passes and received exact Darwin execution. It also changes the compiler and GOROOT view used by the installed generator and will need removal when Go 1.25 ages out.

The current-Go golden repair passes, preserves installed bytes exactly, and avoids a toolchain lifecycle pin. It is the better package repair despite adding a test-data adjustment.

## Current uncertainty

The canonical current-base commit requires Linux and Darwin target execution. No public upstream interaction occurred.
