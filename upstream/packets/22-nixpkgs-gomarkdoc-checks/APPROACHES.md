# Approaches — unit 22 gomarkdoc checks

## Decision

Selected and accepted: keep the current Go builder, update the one Go 1.26 command golden under `testData`, and restore the default selected command-package checks.

Canonical source: [`e8d97d5d8c67a9473a7aaad3961c0630583aa34b`](https://github.com/teamleaderleo/nixpkgs/commit/e8d97d5d8c67a9473a7aaad3961c0630583aa34b)

Disposition: `ACCEPT`.

## Selected approach — current-Go golden repair

```nix
postPatch = ''
  substituteInPlace testData/docs/README.md \
    --replace-fail 'GetField gets \[\*AnotherStruct.Field\].' \
    'GetField gets [\\\*AnotherStruct.Field](<#AnotherStruct>).'
'';
```

Removing `doCheck = false` restores the standard selected-package check.

### Why selected

- Go 1.26 command checks pass after one exact golden update.
- The change touches a test-only expected-output file, not product source.
- Current-base checks-disabled and checks-enabled executables are byte-identical.
- It preserves the default supported toolchain.
- It avoids a fixed-builder lifecycle pin.
- It keeps the existing command-only package selection and standard Go phases.
- `--replace-fail` makes future source drift explicit.
- Linux and Darwin exact-head gates and Linux `nixpkgs-review` pass.
- The same golden passes an advisory Go 1.27rc2 forecast.

### Risks retained

- The expected markdown is coupled to Go documentation-link semantics.
- A future Go bump can change another golden.
- Selected checks cover the built command package, not every upstream library package.
- The package is dormant upstream.

## Executed rejected approaches

### Fixture and `GOFLAGS` cleanup

Run `30692403974` proved both edits unnecessary.

### Go 1.25 pin

The pin passed but changed the shipped toolchain and introduced lifecycle work. Rejected after the current-Go binary-identity comparison.

### Full package discovery

Run `30674969557` reached the broad suite but failed language goldens requiring Go 1.21-or-older standard-library prose. Rejected.

### Split build/test toolchains, custom checkPhase, untagged update

Rejected because they either fail to test production behavior or add unnecessary scope.

## Acceptance fence

- exact source head and parent: pass;
- one changed package file and `diff --check`: pass;
- x86_64-linux command/help/version: pass;
- aarch64-darwin command/help/version: pass;
- Darwin baseline/candidate executable identity: pass;
- exact-parent Linux `nixpkgs-review`: pass;
- independent complete-diff review: pass.
