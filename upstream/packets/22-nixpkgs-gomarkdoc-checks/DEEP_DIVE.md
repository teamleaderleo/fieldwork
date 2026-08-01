# Deep dive — unit 22 gomarkdoc checks

## Technical conclusion

The regression is a Go 1.26 generated-documentation golden mismatch. It is not caused by a missing empty config file or a fatal leaked Nix `GOFLAGS` token.

The selected repair keeps the current Go builder, updates one expected markdown line under `testData`, and restores the existing selected command-package checks. The installed binary remains byte-identical to the checks-disabled baseline.

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

The Go 1.26 comparison built:

1. the checks-disabled baseline at source base `55096b0c...`;
2. the checks-enabled golden candidate at `3a036ab9...`.

Both used the same Go 1.26.5 builder. The candidate patch touches only `testData/docs/README.md`. The installed binaries passed `cmp` and shared SHA-256:

```text
b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e
```

This is stronger than an interface-only compatibility claim: the shipped executable bytes are unchanged.

## Broader test packages

Clearing `subPackages` reaches the complete upstream package set. On Go 1.25, root, command, and formatter packages pass while `lang` fails on standard-library prose:

```text
[Scanner] != Scanner
*[os.File] != *os.File
```

Version-boundary review found:

- Go 1.21 uses plain `Scanner` and `*os.File` in the relevant comments.
- Go 1.22 introduces the `*[os.File]` link.
- Go 1.23 introduces the `[Scanner]` link.

Both old expectations require Go 1.21 or older. Current Nixpkgs does not retain that as a supported fixed builder. Broad restoration would require more golden patches or skips and is not selected.

## Upstream intent

gomarkdoc v1.1.0 declares Go 1.18 and its CI pins Go 1.20.x on Linux, macOS, and Windows. The repository has seen no substantive maintenance since 2023. Exact documentation goldens therefore reflect an older Go documentation corpus.

## Selected source

- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `3a036ab91fa1de2fbbd038b2b212552cff1cc5bf`
- File: `pkgs/by-name/go/gomarkdoc/package.nix`

The source:

1. removes the stale diagnostic-based disable-tests comment and `doCheck = false`;
2. adds a `postPatch` `substituteInPlace --replace-fail` for the one Go 1.26 command golden;
3. keeps the default Go builder, source/vendor hashes, command selection, linker flags, version test, and metadata.

## Why the Go 1.25 pin was rejected after execution

The pin passes and received exact Darwin execution. It also changes the compiler and GOROOT view used by the installed generator and will need removal when Go 1.25 ages out.

The current-Go golden repair passes, preserves installed bytes exactly, and avoids a toolchain lifecycle pin. It is the better package repair despite adding a test-data adjustment.

## Other alternatives

### Build with Go 1.26, test with Go 1.25

This would make tests green without validating production behavior. Rejected.

### Restore every upstream package

Requires unsupported Go 1.21-or-older semantics or multiple golden patches/skips. Rejected.

### Update gomarkdoc

No newer tagged release exists. Moving to an arbitrary revision changes dependencies and hashes and needs a separate update review. Rejected here.

## Current uncertainty

The exact final source has Darwin target evidence. Linux package/check/help/version, `nixpkgs-review`, and packet integrity remain pending. Submission also requires regeneration on a fresh public head.

No public upstream interaction occurred.
