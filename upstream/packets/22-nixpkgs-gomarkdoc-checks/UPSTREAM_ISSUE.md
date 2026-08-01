# Upstream issue draft — gomarkdoc checks

## Route recommendation

Direct pull request preferred. The repair is one package file, the failing behavior and prior containment are documented in Nixpkgs history, and the candidate has an executable acceptance test. Use this issue draft only when a maintainer requests issue-first discussion.

Public posting authority: `absent`

## Proposed title

`gomarkdoc: restore disabled upstream checks`

## Draft body

The `gomarkdoc` 1.1.0 package currently disables its upstream Go tests after they failed in the Nixpkgs build environment.

The failure has three package-specific causes:

- the v1.1.0 documentation golden output aligns with Go 1.25 symbol resolution;
- command tests call gomarkdoc's flag parser directly, so Nixpkgs' test environment `GOFLAGS=-mod=vendor ...` is interpreted as application flags;
- the release tag omits the empty `.gomarkdoc-empty.yml` fixture referenced by command tests.

There is one additional coverage detail: the expression builds only `cmd/gomarkdoc` through `subPackages`. The generic `buildGoModule` check phase also uses that selector, so simply enabling checks exercises only the command package.

A package-local restoration can:

1. use `buildGo125Module` for the v1.1.0 golden output;
2. remove only `-mod=vendor` from `GOFLAGS` during checks while retaining the materialized vendor tree and offline module mode;
3. create the omitted empty config fixture in `preCheck`;
4. clear the build-only package selector in `preCheck`, allowing the standard check phase to discover all packages containing tests.

Acceptance criteria:

- `gomarkdoc` still installs only the command binary;
- source and vendor hashes remain unchanged;
- package checks pass on Linux and Darwin;
- the check log includes the root package, `lang`, a format package, and `cmd/gomarkdoc`;
- `gomarkdoc.tests.version` still reports `1.1.0`.

## Maintainer questions

- Is pinning this package to `buildGo125Module` acceptable until gomarkdoc publishes a release with updated generated-document fixtures?
- Does clearing `subPackages` inside `preCheck` fit current Nixpkgs Go packaging practice, or would maintainers prefer a separate declarative test-package selector?

## Draft limits

- This draft describes gomarkdoc 1.1.0 at the inspected Nixpkgs base.
- A newer gomarkdoc release could change the preferred repair.
- Hydra and merge-queue results require an authorized upstream pull request.
