# Approaches — unit 22 gomarkdoc checks

## Decision

Selected: pin gomarkdoc 1.1.0 to `buildGo125Module` and restore the default command-package checks by removing `doCheck = false`.

Canonical source: [`5c17b14e271611c3418e3e2f572366766f6aa3cc`](https://github.com/teamleaderleo/nixpkgs/commit/5c17b14e271611c3418e3e2f572366766f6aa3cc)

Current disposition: `EXECUTE`.

## Selected approach — Go 1.25 pin only

```nix
{
  buildGo125Module,
  # ...
}:

buildGo125Module (finalAttrs: {
  # gomarkdoc 1.1.0's command tests compare generated documentation that
  # changed with Go 1.26. Keep the oldest supported Go toolchain for now.
})
```

`buildGoModule` enables checks by default, so removing the explicit disable restores `cmd/gomarkdoc` tests.

### Why selected

- The repair-isolation run proves Go 1.25 alone passes.
- The same run proves Go 1.26 fails even after fixture and flag cleanup.
- It preserves the existing command-only package selection.
- It uses the standard Nixpkgs Go build and check phases.
- It adds no test patch, custom check phase, fixture, or shell mutation.
- Versioned Go builders are the documented Nixpkgs response for toolchain-sensitive packages.

### Risks

- The installed binary changes from Go 1.26 to Go 1.25, which can change generated documentation.
- Go 1.25 is temporary and will eventually leave the supported Nixpkgs window.
- Selected checks cover the built command package, not the complete upstream library suite.
- The package is dormant upstream, making a future clean update uncertain.

## Executed rejected approach — fixture and `GOFLAGS` cleanup as fixes

Run [`30692403974`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692403974) tested all combinations.

Go 1.25 passed with:

- both cleanups;
- only fixture creation;
- only `GOFLAGS` cleanup;
- neither cleanup.

The cleanups are not required repairs. They were removed to satisfy the smallest-proven-diff rule.

## Executed rejected approach — current Go with both cleanups

Go 1.26 plus the empty fixture and `GOFLAGS` cleanup failed `TestCommand/./docs`. This disproves the original causal theory.

## Executed rejected approach — full package discovery

Run [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557) cleared `subPackages` and reached the broad suite on Linux and Darwin. `lang` failed deterministic standard-library documentation goldens.

Both expected strings align only with Go 1.21 or older. Current Nixpkgs does not retain such an old supported builder. Rejected.

## Viable future approach — patch current-Go goldens

Patch the gomarkdoc v1.1.0 expected documentation for Go 1.26 and retain the default builder. This would validate the currently shipped toolchain but adds test-data patches coupled to Go's evolving documentation output. Consider when the Go 1.25 pin ages out.

## Rejected approach — split build and test toolchains

Building the product with Go 1.26 while running tests with Go 1.25 would make the checks pass without validating production behavior. Rejected.

## Rejected approach — custom checkPhase

The standard selected-package check phase works under Go 1.25. A custom phase adds unnecessary divergence. Rejected.

## Rejected approach — update to an untagged gomarkdoc revision

No newer tagged release exists. An untagged update changes dependencies and hashes and exceeds unit 22. Rejected.

## Validation fence

The next execution carrier must prove for source head `5c17b14e...`:

- exact parent `55096b0c...`;
- one changed package file and `git diff --check`;
- package build and `cmd/gomarkdoc` check on x86_64-linux and aarch64-darwin;
- exactly one gomarkdoc package result;
- installed help output;
- version `1.1.0`;
- Linux `nixpkgs-review rev HEAD --no-shell`;
- retained artifacts and current packet integrity.
