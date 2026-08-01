# Approaches — unit 22 gomarkdoc checks

## Decision

Selected: restore the `cmd/gomarkdoc` checks selected by the package's existing `subPackages = [ "cmd/gomarkdoc" ]` boundary.

Canonical source: [`569c0c4d11e5a14f3fe6237c0a50dc484f80e744`](https://github.com/teamleaderleo/nixpkgs/commit/569c0c4d11e5a14f3fe6237c0a50dc484f80e744)

Current disposition: `HOLD`. Exact-head Darwin passed; Linux, final packet integrity, carrier closure, independent review, and fresh-head execution remain pending.

## Selected approach — command-package checks

```nix
buildGo125Module (finalAttrs: {
  subPackages = [ "cmd/gomarkdoc" ];
  doCheck = true;

  preCheck = ''
    export GOFLAGS="''${GOFLAGS//-mod=vendor/}"
    touch .gomarkdoc-empty.yml
  '';
})
```

### Why it fits

- It restores tests for the program Nixpkgs builds and installs.
- It preserves the package's existing build and check target selection.
- It reuses the standard Nixpkgs Go check phase.
- It recreates the fixture omitted from the v1.1.0 tag.
- It keeps Nix's build-only `-mod=vendor` token out of gomarkdoc's application flag parser.
- It keeps source/vendor hashes, linker flags, output contents, and version passthru unchanged.
- Exact-head aarch64-darwin passed package build, selected command check, installed help, and version `1.1.0`.
- Retained older execution also passed this command-package path on Linux and Darwin.

### Risks

- `buildGo125Module` is a compatibility pin and creates future update work.
- Public issue #516481 calls the unknown-flag diagnostic benign, so `GOFLAGS` token removal remains semantic isolation rather than a proven sole blocker.
- The fixture is synthesized in the disposable build tree.
- Root, `lang`, and formatter tests are outside this package-selected check boundary.
- The candidate base is 384 commits behind refreshed public head `63c4c8011115076be7a315edd8f740fd751b168a`, although the checked advance has no relevant package or builder overlap.

## Executed losing approach — clear `subPackages` for full discovery

Superseded source head: `94be3956403ebf368b9d8262fdc9e5a5d2e80683`  
Run: [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557)  
Receipt: [`receipts/2026-08-01-full-discovery-failure.md`](./receipts/2026-08-01-full-discovery-failure.md)

### Result

Clearing `subPackages` inside `preCheck` successfully reached the broad package set on Linux and Darwin. Root, command, and formatter packages passed. `lang` failed the same two exact-text tests on both platforms because modern Go 1.25 standard-library comments contain bracketed documentation links:

- `[Scanner]` instead of `Scanner`;
- `*[os.File]` instead of `*os.File`.

### Disposition

Rejected for this unit. The result proves the selector reset mechanism, while also proving that a claimed full upstream restoration requires additional upstream-test compatibility policy. Unit 22 does not skip or rewrite those language assertions.

### Reopening trigger

Reopen broad discovery only when one of these is established:

- a newer gomarkdoc release updates the exact-text expectations;
- gomarkdoc maintainers define bracketed Go doc links as the intended v1.1.0 output;
- Nixpkgs maintainers request a package patch or narrowly justified test skip;
- a supported older Go toolchain is accepted for the whole suite.

## Rejected approach — leave `doCheck = false`

Current containment leaves the built command untested. Rejected.

## Rejected approach — remove `subPackages` from the package expression

This would widen build/install behavior beyond the command package. Rejected.

## Rejected approach — replace `checkPhase`

A manual `go test` phase would duplicate Nixpkgs Go-builder handling for tags, flags, parallelism, vet behavior, and output. Rejected while the standard selected-package phase works.

## Rejected approach — skip the two `lang` tests

A `-skip` expression could make broad discovery green, but it would weaken upstream coverage specifically to accommodate evolving standard-library prose. No maintainer policy supports that choice. Rejected.

## Rejected approach — patch exact `lang` expectations

Replacing `Scanner` with `[Scanner]` and `*os.File` with `*[os.File]` would bind gomarkdoc 1.1.0 tests to current Go standard-library wording and expand the Nixpkgs patch beyond package configuration. Rejected.

## Rejected approach — generic `buildGoModule` enhancement

A separate `checkSubPackages` option could express different build and test sets, but the full-discovery result shows that broader tests still fail. A shared-builder change would not solve the package compatibility issue and exceeds unit scope. Rejected.

## Rejected approach — newer gomarkdoc revision

No newer tagged release was established for this package. A version update changes source/vendor hashes and requires independent changelog and dependency review. Rejected for unit 22.

## Viable narrower variant — retain `-mod=vendor`

The public issue and gomarkdoc source indicate the unknown token is diagnostic rather than fatal. A reviewer could request Go 1.25 plus fixture synthesis while leaving `GOFLAGS` unchanged.

The selected source removes the token because the assignment concerns leaked Nix flags and passing command-package execution used this setup. Reopen only on reviewer request or comparative evidence.

## Validation fence

Current carrier head `c95da0c4b3f460df9bc8f342e98d05345da66df8` has established on Darwin:

- exact source head `569c0c4d11e5a14f3fe6237c0a50dc484f80e744` and parent;
- one changed package file and `git diff --check` success;
- selected command-package build/check and exactly one package result;
- installed executable and help output;
- version passthru `1.1.0`;
- artifact `8815619734`, digest `sha256:db5516d38b64307b5d67ffb6bc23c33028dbdeaeb2b681b60a1cc7440958021a`.

Remaining validation:

- the same package/check/help/version controls on x86_64-linux;
- Linux `nixpkgs-review rev HEAD --no-shell`;
- final packet-tip Fieldwork integrity;
- transferred artifacts and closed execution carrier;
- independent complete-diff review;
- fresh-head rebase and rerun before authorized submission.
