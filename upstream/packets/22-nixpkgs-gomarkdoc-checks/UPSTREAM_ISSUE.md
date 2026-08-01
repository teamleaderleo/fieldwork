# Upstream issue route — unit 22 gomarkdoc checks

## Status

`NO NEW ISSUE — USE EXISTING NixOS/nixpkgs#516481`

A new issue would duplicate the existing regression report. A future authorized pull request should link the issue and correct its causal explanation.

Public upstream contact remains unauthorized.

## Corrected diagnosis

The issue compares a Go 1.25 release branch with Go 1.26 master. Comparative execution proves:

- creating `.gomarkdoc-empty.yml` is unnecessary;
- removing Nix's inherited `GOFLAGS` is unnecessary;
- Go 1.26 fails the command documentation golden even with both cleanups;
- updating one expected Go 1.26 markdown line restores the command check.

The visible missing-file and unknown-flag messages are captured output, not the failing assertion.

## Preferred authorized route

Open a direct PR against current `master` and use:

```text
Closes #516481
```

The PR should explain the release-branch/master toolchain difference, the exact Go 1.26 golden update, and the byte-identical installed-binary control.

## Optional future issue comment

A separate issue comment is unnecessary if the PR explains the result. If maintainers ask, retained wording is:

> The passing reproducer is a release-25.11 snapshot using Go 1.25, while the failing master snapshot uses Go 1.26. A variant matrix shows fixture and GOFLAGS changes are unnecessary. Updating the one Go 1.26 command golden restores checks, and the checks-enabled installed binary is byte-identical to the current checks-disabled package.

This text is retained only for future explicit authorization.

## Authority checklist

- [x] Existing issue found.
- [x] Duplicate issue avoided.
- [x] Causal claim independently checked.
- [x] Installed-output identity tested.
- [x] No public comment, reaction, or maintainer contact performed.
- [ ] Explicit authorization obtained for future public action.
- [ ] Current issue state and contribution policy rechecked at submission time.
