# Unit 22 — gomarkdoc command checks

## Current answer

Nixpkgs disabled gomarkdoc 1.1.0 checks after a Go-toolchain transition exposed a generated-documentation golden mismatch. The visible missing-config and unknown-flag diagnostics were captured output, not the failing assertion.

The selected repair keeps the current Go 1.26 builder and updates the one command-test golden line whose link resolution changed. It removes `doCheck = false`, restores the package-selected `cmd/gomarkdoc` tests, and leaves the installed binary byte-for-byte identical to the current checks-disabled package.

## Disposition

`EXECUTE`

Independent review accepts the source direction. The exact final source has passed its aarch64-darwin command, help, version, and binary-identity comparison. A packet-anchored x86_64-linux build plus `nixpkgs-review` and current Fieldwork integrity remain before `ACCEPT`.

Upstream contact authorized: `no`.

## Exact clean source

- Repository: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Branch: [`fieldwork/unit-22-gomarkdoc-checks`](https://github.com/teamleaderleo/nixpkgs/tree/fieldwork/unit-22-gomarkdoc-checks)
- Base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Head: [`3a036ab91fa1de2fbbd038b2b212552cff1cc5bf`](https://github.com/teamleaderleo/nixpkgs/commit/3a036ab91fa1de2fbbd038b2b212552cff1cc5bf)
- Compare: [`55096b0c...3a036ab9`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...3a036ab91fa1de2fbbd038b2b212552cff1cc5bf)
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Fence: one commit, one file, six additions and four deletions

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

- Run: [`30692966149`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692966149)
- Job: `91350898702` — success
- Source: `3a036ab91fa1de2fbbd038b2b212552cff1cc5bf`
- Platform: aarch64-darwin
- Command check: pass
- Installed help: pass
- Version `1.1.0`: pass
- Baseline/candidate binary `cmp`: pass
- Shared binary SHA-256: `b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e`
- Artifact: [`8816337182`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692966149/artifacts/8816337182)
- Digest: `sha256:14ae794f8160a5f6c68bcf113dd430d628fa4b8399ad9ceb65f1d5f33770e5e1`

Detailed receipt: [`receipts/2026-08-01-go126-golden-comparison.md`](./receipts/2026-08-01-go126-golden-comparison.md).

### Broader-suite negative control

Run [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557) proved broad discovery reaches root, command, formatter, and language packages. `lang` then failed standard-library prose goldens whose two expectations jointly align only with Go 1.21 or older. Broad restoration remains outside this command-selected package repair.

## Independent review

The complete final diff, target comparisons, installed-output identity, builder behavior, upstream tests, and drafts were reviewed as the assigned independent lane. No separate external-review dependency remains.

Receipt: [`receipts/2026-08-01-independent-code-review.md`](./receipts/2026-08-01-independent-code-review.md).

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue route](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review](./REVIEW.md)
- [Handoff](./HANDOFF.md)
- [Retained source patch](./patches/0001-gomarkdoc-restore-command-checks.patch)

## Remaining sequence

1. Run exact source head `3a036ab9...` on x86_64-linux with `nixpkgs-review` from a carrier anchored to this packet revision.
2. Preserve the Linux package/check/help/version/review artifact and current Fieldwork-integrity receipt.
3. Transfer receipts and retire temporary carriers.
4. Mark the research packet `ACCEPT` for the user's final-mile public decision.
5. Regenerate the one-file commit on a fresh public Nixpkgs head before any authorized submission.

No public upstream interaction occurred.
