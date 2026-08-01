# Deep dive — unit 22 gomarkdoc checks

## Technical conclusion

The regression is a Go-toolchain compatibility failure, not a missing test fixture or a fatal leaked `GOFLAGS` token.

The clean repair pins gomarkdoc 1.1.0 to Go 1.25 and restores the default selected-package checks. It deliberately does not mutate the test environment.

## Historical comparison

The public issue compares two revisions that are not a linear before/after pair:

- `4590696c8693fea477850fe379a01544293ca4e2` is a `release-25.11` backport dated 2026-03-23.
- `acd02b8771d0546f96ee281ac45c3a6f81b9bfba` is a master revision dated 2026-05-01.
- Their histories diverge.

At the release revision:

```nix
go = go_1_25;
buildGoModule = buildGo125Module;
```

At the master revision:

```nix
go = go_1_26;
buildGoModule = buildGo126Module;
```

The gomarkdoc package remains version 1.1.0 with the same source hash, vendor hash, and command-only `subPackages`. The expression was refactored from `rec` to `finalAttrs`, but that does not explain the golden mismatch.

## Why the visible diagnostics were misleading

### Missing empty config

`command_test.go` requests `../.gomarkdoc-empty.yml`, and the release tag does not contain that file. However, `buildConfig` prints `viper.ReadInConfig` errors and does not return them. The command test can pass with the file absent.

The isolation run confirmed this: the Go 1.25 variant without the fixture passed.

### Unknown `GOFLAGS`

`defaultTags()` parses `GOFLAGS`, accepts only `-tags`, prints an error for unknown flags, and returns no tags. The tests intentionally include unknown `GOFLAGS` cases and expect command success.

The isolation run confirmed that retaining Nix's inherited flags under Go 1.25 still passes.

Go suppresses output from successful tests. When the Go 1.26 golden assertion fails, captured diagnostics from other successful subtests become visible in the package failure log. The public issue identified the last visible messages rather than the failing assertion.

## Exact failing behavior under Go 1.26

The command package fails `TestCommand/./docs` because generated markdown changes. One observed difference is link resolution for a field reference:

```text
GetField gets [\\\*AnotherStruct.Field](<#AnotherStruct>).
```

versus the retained expected text:

```text
GetField gets \[\*AnotherStruct.Field\].
```

The default-Go variant failed even with both the empty fixture and `GOFLAGS` cleanup present.

## Broader test packages

Clearing `subPackages` reaches the complete upstream package set. On Go 1.25, root, command, and formatter packages pass, while `lang` fails on standard-library prose:

```text
[Scanner] != Scanner
*[os.File] != *os.File
```

Version boundary review found:

- Go 1.21 uses plain `Scanner` and plain `*os.File` in the relevant comments.
- Go 1.22 introduces the `*[os.File]` link.
- Go 1.23 introduces the `[Scanner]` link.

Both old expectations therefore require Go 1.21 or older. Current Nixpkgs retains Go 1.25 and Go 1.26, and its policy removes fixed builders after their Go line reaches end of life. Broad restoration by pinning an ancient Go release is not a viable Nixpkgs repair.

## Upstream intent

gomarkdoc v1.1.0 declares Go 1.18 and its own CI pins Go 1.20.x on Linux, macOS, and Windows. The repository has seen no substantive maintenance since 2023. Its exact documentation goldens were written for an older Go documentation corpus.

## Selected source

- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Head: `5c17b14e271611c3418e3e2f572366766f6aa3cc`
- File: `pkgs/by-name/go/gomarkdoc/package.nix`

The source:

1. changes `buildGoModule` to `buildGo125Module`;
2. removes the stale disable-tests comment and `doCheck = false`;
3. leaves source/vendor hashes, command selection, linker flags, version test, and metadata unchanged.

## Product compatibility effect

The Go pin affects the installed executable, not only checkPhase. `go/build.Default` falls back to the compiled code's GOROOT. gomarkdoc reads package source and documentation through Go APIs, so its generated output may differ between Go 1.25 and Go 1.26.

The selected choice restores a tested, supported toolchain close to upstream's pinned Go 1.20 line. It also creates a future upgrade obligation. The packet no longer claims output is unchanged.

## Alternatives

### Patch Go 1.26 goldens

This would keep the current production toolchain and validate its output. It would add source patches tied to evolving Go documentation semantics and likely require updates on future Go bumps. Viable, but wider than the selected one-file package repair.

### Test with Go 1.25 and build with Go 1.26

This separates the checked toolchain from the shipped toolchain. The tests would no longer validate the production binary's documentation behavior. Rejected.

### Restore every upstream package

Requires unsupported Go 1.21-or-older semantics or patches/skips for language goldens. Rejected for this unit.

### Update gomarkdoc

No newer tagged release exists. Moving to an arbitrary revision changes source, dependencies, and hashes and needs a separate update review. Rejected here.

## Current uncertainty

The simplified exact Git head still requires fresh Linux and Darwin execution. Submission also requires regeneration on a current public Nixpkgs head because the retained base is stale.

No public upstream interaction occurred.
