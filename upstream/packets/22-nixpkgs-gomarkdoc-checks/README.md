# Unit 22 — gomarkdoc command checks

## Current answer

Nixpkgs disabled gomarkdoc 1.1.0 checks after a Go-toolchain transition exposed a generated-documentation golden mismatch. The visible missing-config and unknown-flag diagnostics were captured output, not the failing assertion.

The accepted repair keeps the current Go 1.26 builder, updates the one command-test golden line whose link resolution changed, and removes `doCheck = false`. The package-selected `cmd/gomarkdoc` checks now pass on Linux and Darwin. The changed file is a test-only expected-output fixture: tests generate `README-test.md` and compare it with `testData/docs/README.md`.

## Disposition

`ACCEPT`

Independent complete-diff review and current-base target execution are complete. The packet is ready for the user's final-mile public-upstream decision.

Upstream contact authorized: `no`.

## Exact source

- Repository: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Branch: [`fieldwork/unit-22-gomarkdoc-checks`](https://github.com/teamleaderleo/nixpkgs/tree/fieldwork/unit-22-gomarkdoc-checks)
- Public base: [`97d48ba11e7eeb6896e9da8d64b22b306da14103`](https://github.com/NixOS/nixpkgs/commit/97d48ba11e7eeb6896e9da8d64b22b306da14103)
- Canonical head: [`e8d97d5d8c67a9473a7aaad3961c0630583aa34b`](https://github.com/teamleaderleo/nixpkgs/commit/e8d97d5d8c67a9473a7aaad3961c0630583aa34b)
- Compare: [`97d48ba1...e8d97d5d`](https://github.com/teamleaderleo/nixpkgs/compare/97d48ba11e7eeb6896e9da8d64b22b306da14103...e8d97d5d8c67a9473a7aaad3961c0630583aa34b)
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Fence: one commit, one file, six additions and four deletions
- Final package blob: `53f4eef322e84133c2c867070a55c60bb14e09ae`

## Selected source change

```nix
# Go 1.26 resolves this field reference while generating the command golden.
postPatch = ''
  substituteInPlace testData/docs/README.md \
    --replace-fail 'GetField gets \[\*AnotherStruct.Field\].' \
    'GetField gets [\\\*AnotherStruct.Field](<#AnotherStruct>).'
'';
```

Removing `doCheck = false` restores the generic Go builder's selected command-package check. `subPackages = [ "cmd/gomarkdoc" ]` remains unchanged.

## Why this repair

A five-variant target run disproved fixture creation and `GOFLAGS` cleanup as causes. Go 1.26 still failed with both cleanups; the actual failure was the one generated markdown line.

A patch-equivalent Go 1.26 comparison then proved the checks-enabled installed binary is byte-for-byte identical to the checks-disabled baseline. Current-base Darwin repeated the binary-identity control. The repair therefore validates the shipped toolchain without changing the executable.

## Current-base acceptance

### aarch64-darwin

- Run: [`30693522616`](https://github.com/teamleaderleo/fieldwork/actions/runs/30693522616)
- Job: `91352347312` — success
- Exact source fence, command check, one-package count, installed help, version `1.1.0`: success
- Checks-disabled baseline/candidate binary identity: success
- Binary SHA-256: `199ac9faabb41a65e784ac6128f38c3ccb6d97040e4f69d2b3bbd9b79baa817d`
- Artifact: [`8816500818`](https://github.com/teamleaderleo/fieldwork/actions/runs/30693522616/artifacts/8816500818)
- Digest: `sha256:313220b9f7ffff28a8023c249232ba0114eba457d1da38dad7122719bcc0d3e2`

### x86_64-linux

- Run: [`30694249810`](https://github.com/teamleaderleo/fieldwork/actions/runs/30694249810)
- Job: `91354242933` — success
- Exact source fence, command check, one-package count, installed help, version `1.1.0`: success
- `nixpkgs-review rev -b 97d48ba11e7eeb6896e9da8d64b22b306da14103 HEAD --no-shell`: success; one package built (`gomarkdoc`)
- Artifact: [`8816799835`](https://github.com/teamleaderleo/fieldwork/actions/runs/30694249810/artifacts/8816799835)
- Digest: `sha256:a5ab307bc9102b1c8ccea478dde8c58b21c8dcf6ce56a617ca13c9c6cd8c4cb6`

Detailed receipt: [`receipts/2026-08-01-current-base-acceptance.md`](./receipts/2026-08-01-current-base-acceptance.md).

## Additional evidence

- Repair isolation: run `30692403974`, artifact `8816151764`.
- Patch-equivalent Go 1.26 binary comparison: run `30692966149`, artifact `8816337182`.
- Broad-suite negative control: run `30674969557`.
- Go 1.27 RC2 forecast: run `30693795784`, artifact `8816586391`; command check, help, and version passed.
- Independent review: [`receipts/2026-08-01-independent-code-review.md`](./receipts/2026-08-01-independent-code-review.md).

## Final-mile notes

The source is current enough for this packet: the checked public advance after the base had no gomarkdoc or Go-builder overlap. Recheck public master, contribution instructions, PR template, and issue state immediately before authorized submission.

No public upstream interaction occurred.
