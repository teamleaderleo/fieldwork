# Approaches — unit 22 gomarkdoc checks

## Decision

Selected: keep the current Go builder, update the one Go 1.26 command golden under `testData`, and restore the default selected command-package checks.

Canonical source: [`3a036ab91fa1de2fbbd038b2b212552cff1cc5bf`](https://github.com/teamleaderleo/nixpkgs/commit/3a036ab91fa1de2fbbd038b2b212552cff1cc5bf)

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
- The installed candidate binary is byte-identical to the checks-disabled Go 1.26 baseline.
- It preserves the default supported toolchain.
- It avoids a fixed-builder lifecycle pin.
- It keeps the existing command-only package selection and standard Go phases.
- `--replace-fail` makes future source drift explicit.

### Risks

- The expected markdown is coupled to current Go documentation-link semantics.
- A future Go bump may change additional golden output.
- Selected checks cover the built command package, not every upstream library package.
- The package is dormant upstream.

## Executed rejected approach — fixture and `GOFLAGS` cleanup

Run [`30692403974`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692403974) tested all combinations. Go 1.25 passed with neither cleanup, and Go 1.26 failed with both. They are not repair ingredients.

## Executed rejected approach — Go 1.25 pin

Source `5c17b14e271611c3418e3e2f572366766f6aa3cc` changed to `buildGo125Module` and restored checks. Exact aarch64-darwin execution passed.

Rejected after the current-Go comparison because:

- it changes the shipped toolchain and standard-library view;
- it creates removal work when Go 1.25 leaves Nixpkgs;
- the Go 1.26 golden repair restores checks with an identical installed binary.

## Executed rejected approach — full package discovery

Run [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557) reached the broad suite on Linux and Darwin. `lang` failed standard-library documentation goldens whose combined expectations require Go 1.21 or older. Rejected.

## Rejected approach — split build and test toolchains

Building with Go 1.26 while testing with Go 1.25 would not validate production behavior. Rejected.

## Rejected approach — custom checkPhase

The standard selected-package check works after the golden update. Rejected.

## Rejected approach — untagged update

No newer tagged release exists. An untagged update changes dependencies and hashes and exceeds unit 22. Rejected.

## Validation fence

Final acceptance requires:

- exact source head `3a036ab9...` and parent;
- one changed package file and `git diff --check`;
- aarch64-darwin command check, help, version, and binary identity — complete;
- x86_64-linux command check, help, version, and `nixpkgs-review` — pending;
- retained artifacts and current packet integrity;
- clean retirement of temporary execution carriers.
