# Upstream issue route — unit 22 gomarkdoc checks

## Status

`NO NEW ISSUE — EXISTING ISSUE #516481`

A new public issue would duplicate [`NixOS/nixpkgs#516481`](https://github.com/NixOS/nixpkgs/issues/516481), which already records the gomarkdoc 1.1.0 command-check regression, missing empty fixture, and disable-tests workaround.

Public upstream contact remains unauthorized. This file preserves routing analysis without posting anything.

## Existing issue fit

Relevant facts already recorded by the issue:

- gomarkdoc 1.1.0 checks regressed while the package expression stayed unchanged;
- command tests emit unknown-flag diagnostics while parsing `GOFLAGS`;
- the observed failing condition is the absent `../.gomarkdoc-empty.yml` fixture;
- disabling checks is the current workaround;
- the issue points to `buildGoModule`, Go, and stdenv as investigation boundaries;
- no competing repair is present.

## Refined claim boundary

Source review and retained execution support these statements:

- `-mod=vendor` reaches gomarkdoc's application parser and produces a diagnostic;
- gomarkdoc returns no default tags after that parse error;
- the public issue treats the diagnostic as benign;
- the missing empty fixture is the observed command-test blocker;
- Go 1.25 plus fixture synthesis and flag isolation passed the selected command package in retained Linux and Darwin runs;
- a separate full-discovery experiment failed two `lang` exact-text tests because modern Go standard-library comments use bracketed documentation links.

The selected repair therefore restores the checks corresponding to the package's existing `cmd/gomarkdoc` build target. It does not claim a passing complete upstream library suite.

## Preferred upstream route after authorization

Open a direct PR against `master` with:

```text
Closes #516481
```

The PR should change only `pkgs/by-name/go/gomarkdoc/package.nix` and describe:

1. Go 1.25 compatibility for the selected v1.1.0 command golden;
2. creation of the omitted empty fixture in the disposable build tree;
3. removal of Nix's build-only `-mod=vendor` token before application flag parsing;
4. unchanged `subPackages = [ "cmd/gomarkdoc" ]` build and check selection;
5. unchanged source/vendor hashes and installed output.

## Optional issue comment draft

A direct PR is preferable. This comment remains unposted and would require exact authorization:

> I reproduced the command-package failure and prepared a package-local repair that uses Go 1.25, recreates the omitted empty config fixture, and keeps Nix's `-mod=vendor` option out of gomarkdoc's application flag parser during checks. The existing `subPackages = [ "cmd/gomarkdoc" ]` boundary remains unchanged, so the restored checks correspond to the built command.
>
> I also tested broader Go package discovery separately. Root, command, and formatter packages passed, while two `lang` exact-text assertions failed because current Go standard-library comments contain bracketed documentation links. The proposed package repair does not skip or rewrite those tests.

## Authority checklist

- [x] Existing public issue found.
- [x] New issue avoided.
- [x] No public comment posted.
- [x] No reaction or maintainer contact performed.
- [ ] Exact authorization obtained for any future public interaction.
- [ ] Current contribution and disclosure requirements rechecked at filing time.
