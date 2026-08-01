# Upstream issue route — unit 22 gomarkdoc checks

## Status

`NO NEW ISSUE — USE EXISTING NixOS/nixpkgs#516481`

A new issue would duplicate the existing regression report. The existing issue should be linked by a future authorized pull request, while its causal explanation should be corrected in the PR body.

Public upstream contact remains unauthorized.

## Corrected diagnosis

The issue compares:

- a `release-25.11` backport using Go 1.25;
- a master revision using Go 1.26.

The package source, vendor hash, and command selection remain the same. A comparative target run proves:

- Go 1.25 passes without adding the missing fixture and without removing Nix `GOFLAGS`;
- Go 1.26 fails even when both cleanups are applied.

The visible missing-file and unknown-flag messages are captured output printed when the package test fails. They are not established failure causes.

## Preferred authorized route

Open a direct pull request against current `master` and use:

```text
Closes #516481
```

The PR should explain that gomarkdoc 1.1.0's generated-documentation tests are toolchain-sensitive and that Nixpkgs' Go 1.25 release branch passes while Go 1.26 master does not.

## Optional future issue comment

A separate issue comment is unnecessary if a direct PR accurately explains the result. If maintainers ask, a concise correction would be:

> The two reproducer revisions are from different Nixpkgs lines: the passing release-25.11 snapshot maps buildGoModule to Go 1.25, while the failing master snapshot maps it to Go 1.26. A variant matrix shows Go 1.25 passes without fixture or GOFLAGS changes, and Go 1.26 fails with both. The visible diagnostics are captured output, not the failing assertion.

This text is retained only for future explicit authorization.

## Authority checklist

- [x] Existing issue found.
- [x] Duplicate issue avoided.
- [x] Causal claim independently checked.
- [x] No public comment, reaction, or maintainer contact performed.
- [ ] Explicit authorization obtained for any future public action.
- [ ] Current issue state and contribution policy rechecked at submission time.
