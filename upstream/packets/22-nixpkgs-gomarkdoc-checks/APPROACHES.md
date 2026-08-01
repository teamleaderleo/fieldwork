# Approaches — unit 22 gomarkdoc checks

## Decision

Selected: keep the current Go builder, update the one Go 1.26 command golden under `testData`, and restore the default selected command-package checks.

Canonical source: [`e8d97d5d8c67a9473a7aaad3961c0630583aa34b`](https://github.com/teamleaderleo/nixpkgs/commit/e8d97d5d8c67a9473a7aaad3961c0630583aa34b)

Current disposition: `EXECUTE`.

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
- The change touches test data, not product source.
- A patch-equivalent installed candidate is byte-identical to the checks-disabled Go 1.26 baseline.
- It preserves the default supported toolchain.
- It avoids a fixed-builder lifecycle pin.
- It keeps the existing command-only package selection and standard Go phases.
- `--replace-fail` makes future source drift explicit.
- The final commit is regenerated on public `master` head `97d48ba1...`.

### Risks

- The expected markdown is coupled to current Go documentation-link semantics.
- A future Go bump may change additional golden output.
- Selected checks cover the built command package, not every upstream library package.
- The package is dormant upstream.

## Executed rejected approach — fixture and `GOFLAGS` cleanup

Run `30692403974` tested all combinations. Go 1.25 passed with neither cleanup, and Go 1.26 failed with both. They are not repair ingredients.

## Executed rejected approach — Go 1.25 pin

Source `5c17b14e...` changed to `buildGo125Module` and restored checks. Exact aarch64-darwin execution passed.

Rejected because it changes the shipped toolchain and the final Go 1.26 repair preserves installed bytes and avoids a lifecycle pin.

## Executed rejected approach — full package discovery

Run `30674969557` reached the broad suite on Linux and Darwin. `lang` failed standard-library documentation goldens whose combined expectations require Go 1.21 or older. Rejected.

## Validation fence

Final acceptance requires:

- exact source head `e8d97d5d...` and parent `97d48ba1...`;
- one changed package file and `git diff --check`;
- command check, help, and version on x86_64-linux and aarch64-darwin;
- Darwin checks-disabled baseline/candidate binary identity;
- Linux `nixpkgs-review rev HEAD --no-shell`;
- retained artifacts and current packet integrity;
- clean retirement of temporary execution carriers.
