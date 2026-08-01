# Unit 22 — gomarkdoc command checks

## Current answer

Nixpkgs disabled gomarkdoc 1.1.0 checks after a Go-toolchain transition exposed a generated-documentation golden mismatch. The visible missing-config and unknown-flag diagnostics were captured output, not the failing assertion.

The selected repair keeps the current Go 1.26 builder and updates the one command-test golden line whose link resolution changed. It removes `doCheck = false`, restores the package-selected `cmd/gomarkdoc` tests, and leaves product source and package metadata unchanged.

A patch-equivalent aarch64-darwin comparison proved the checks-enabled installed binary is byte-for-byte identical to the checks-disabled baseline. The canonical commit has now been regenerated on the current public Nixpkgs head and requires exact-head Linux/Darwin acceptance.

## Disposition

`EXECUTE`

Independent review accepts the source direction. Current-base exact-head target execution and packet integrity remain before `ACCEPT`.

Upstream contact authorized: `no`.

## Exact current source

- Repository: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Branch: [`fieldwork/unit-22-gomarkdoc-checks`](https://github.com/teamleaderleo/nixpkgs/tree/fieldwork/unit-22-gomarkdoc-checks)
- Public base: [`97d48ba11e7eeb6896e9da8d64b22b306da14103`](https://github.com/NixOS/nixpkgs/commit/97d48ba11e7eeb6896e9da8d64b22b306da14103)
- Canonical head: [`e8d97d5d8c67a9473a7aaad3961c0630583aa34b`](https://github.com/teamleaderleo/nixpkgs/commit/e8d97d5d8c67a9473a7aaad3961c0630583aa34b)
- Compare: [`97d48ba1...e8d97d5d`](https://github.com/teamleaderleo/nixpkgs/compare/97d48ba11e7eeb6896e9da8d64b22b306da14103...e8d97d5d8c67a9473a7aaad3961c0630583aa34b)
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Fence: one commit, one file, six additions and four deletions
- Regenerated: 2026-08-01 after confirming the public package still had blob `149e1cf1908f421132ba3f9bbe08588f9d424a92`

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

## Why this is preferred over the Go 1.25 pin

A Go 1.25 pin also passes, but it changes the compiler and standard-library view used by the installed documentation generator and creates a near-term lifecycle obligation.

The selected Go 1.26 repair changes only test data under `testData`. A target comparison built both the checks-disabled baseline and checks-enabled candidate with Go 1.26, then proved their installed binaries are byte-identical:

```text
b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e
```

## Strongest evidence

### Repair isolation

Run [`30692403974`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692403974) proved that fixture creation and `GOFLAGS` cleanup are unnecessary, while Go 1.26 still fails with both. Artifact `8816151764`, digest `sha256:8597cc8e25daa9975c20a36c1a824d939820f373bc8a0521d2a022ac60e5471e`.

### Go 1.26 golden comparison

Patch-equivalent source `3a036ab91fa1de2fbbd038b2b212552cff1cc5bf` ran in [`30692966149`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692966149), job `91350898702`, on aarch64-darwin. Command check, help, version, and binary identity passed. Artifact `8816337182`, digest `sha256:14ae794f8160a5f6c68bcf113dd430d628fa4b8399ad9ceb65f1d5f33770e5e1`.

The canonical current-base commit uses the same final package blob `53f4eef322e84133c2c867070a55c60bb14e09ae`.

Detailed receipt: [`receipts/2026-08-01-go126-golden-comparison.md`](./receipts/2026-08-01-go126-golden-comparison.md).

### Broader-suite negative control

Run [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557) proved broad discovery reaches root, command, formatter, and language packages. `lang` then failed standard-library prose goldens whose two expectations jointly align only with Go 1.21 or older. Broad restoration remains outside this command-selected package repair.

## Independent review

The complete final diff, target comparisons, installed-output identity, builder behavior, upstream tests, and drafts were reviewed as the assigned independent lane. No separate external-review dependency remains.

Receipt: [`receipts/2026-08-01-independent-code-review.md`](./receipts/2026-08-01-independent-code-review.md).

## Remaining sequence

1. Run exact current source `e8d97d5d...` on x86_64-linux and aarch64-darwin.
2. Preserve source fence, command result, help, version, Linux `nixpkgs-review`, Darwin baseline/candidate binary identity, artifacts, and Fieldwork integrity.
3. Transfer receipts and retire temporary carriers.
4. Mark the research packet `ACCEPT` for the user's final-mile public decision.

No public upstream interaction occurred.
