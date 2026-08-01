# Upstream issue route — unit 22 gomarkdoc checks

## Status

`NO NEW ISSUE — EXISTING ISSUE #516481`

A new public issue draft would duplicate [`NixOS/nixpkgs#516481`](https://github.com/NixOS/nixpkgs/issues/516481), which already records the gomarkdoc 1.1.0 check regression, exact missing-fixture failure, reproduction window, and current disable-tests workaround.

Public upstream contact remains unauthorized. This file preserves the issue analysis and future routing text without posting it.

## Existing issue fit

Existing title:

> gomarkdoc 1.1.0 checkPhase regressed between nixpkgs commits 4590696 (2026-03-23) and acd02b8 (2026-05-01)

Existing issue facts relevant to the candidate:

- gomarkdoc 1.1.0 check execution regressed while the package expression stayed unchanged;
- command tests emit unknown-flag diagnostics for `GOFLAGS`;
- the observed failing assertion is the absent `../.gomarkdoc-empty.yml` fixture;
- disabling checks is the current workaround;
- the issue names `buildGoModule`, Go, and stdenv as likely investigation boundaries;
- no comments or competing repair are present.

## Packet correction derived from the issue

The Fieldwork assignment title emphasizes leaked Nix `GOFLAGS`. Source and existing-issue review support a narrower statement:

- `-mod=vendor` reaches gomarkdoc's application parser and produces a diagnostic;
- gomarkdoc returns no default tags after the parse error;
- the public issue treats that output as benign;
- the missing empty fixture is the observed failure blocker;
- Fieldwork's negative Go 1.26 execution found an additional documentation-golden difference.

The candidate still removes `-mod=vendor` during checks to keep a build-system option out of the application parser. The future PR should avoid claiming that this diagnostic alone caused the failed derivation.

## Preferred upstream route after authorization

Open a direct PR against `master` and link the existing issue with:

```text
Closes #516481
```

The PR should contain only `pkgs/by-name/go/gomarkdoc/package.nix` and describe:

1. Go 1.25 compatibility for the v1.1.0 checked golden;
2. creation of the omitted empty test fixture in the disposable build tree;
3. removal of Nix's build-only `-mod=vendor` token before gomarkdoc parses application flags;
4. check-time clearing of `subPackages` so root, language, formatter, and command packages run;
5. unchanged source/vendor hashes and command-only installation output.

## Optional issue comment draft

This draft is retained only for a future explicitly authorized comment on the existing issue. A direct PR with `Closes #516481` remains preferable.

> I reproduced the package behavior and found one additional Nixpkgs packaging detail: `subPackages = [ "cmd/gomarkdoc" ]` also limits the generic `checkPhase`, so a successful command-package run can still skip the root, `lang`, and format packages.
>
> A package-local candidate keeps the command-only build selector, clears it in `preCheck`, recreates the omitted empty config fixture, and uses Go 1.25 for the v1.1.0 documentation golden. The final validation should show root, `lang`, format, command, and version results on Linux and Darwin.

## Authority and disclosure checklist

- [x] Existing public issue found.
- [x] New issue avoided.
- [x] No public comment posted.
- [x] No reaction or maintainer contact performed.
- [ ] Exact authorization obtained for any future public interaction.
- [ ] Current Nixpkgs contribution and disclosure requirements rechecked at filing time.
