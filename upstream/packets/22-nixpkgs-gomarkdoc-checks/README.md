# Unit 22 — gomarkdoc command checks

## Current answer

Nixpkgs disabled gomarkdoc 1.1.0 checks after a failure was reported when comparing a `release-25.11` revision with a `master` revision. A direct snapshot comparison shows the package itself stayed materially the same while the unversioned Go builder changed from Go 1.25 on the release branch to Go 1.26 on master.

A five-variant target experiment proves the repair boundary:

| Variant | Result |
| --- | --- |
| Go 1.25 pin, no other changes | pass |
| Go 1.25 plus `GOFLAGS` cleanup | pass |
| Go 1.25 plus empty fixture | pass |
| Go 1.25 plus both cleanups | pass |
| Go 1.26 plus both cleanups | fail |

The missing-config and unknown-flag messages were captured output from a test that failed for a generated-documentation mismatch. They were not the cause of the failure.

The clean candidate is therefore intentionally small: use `buildGo125Module` and remove `doCheck = false`. No test fixture is synthesized and no environment flag is rewritten.

## Disposition

`EXECUTE`

The independent complete-diff review accepts the source direction. Exact-head Linux and Darwin package, help, version, and Linux `nixpkgs-review` receipts must now be regenerated for the simplified source head.

Upstream contact authorized: `no`.

## Exact clean source

- Repository: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Branch: [`fieldwork/unit-22-gomarkdoc-checks`](https://github.com/teamleaderleo/nixpkgs/tree/fieldwork/unit-22-gomarkdoc-checks)
- Base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Head: [`5c17b14e271611c3418e3e2f572366766f6aa3cc`](https://github.com/teamleaderleo/nixpkgs/commit/5c17b14e271611c3418e3e2f572366766f6aa3cc)
- Compare: [`55096b0c...5c17b14e`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...5c17b14e271611c3418e3e2f572366766f6aa3cc)
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Fence: one commit, one file, 4 additions and 6 deletions

## Selected source change

```nix
buildGo125Module (finalAttrs: {
  # ...

  # gomarkdoc 1.1.0's command tests compare generated documentation that
  # changed with Go 1.26. Keep the oldest supported Go toolchain for now.
})
```

`buildGoModule` enables checks by default. Removing the package's `doCheck = false` restores the selected `cmd/gomarkdoc` test package.

## Why the Go pin is a product decision

gomarkdoc uses Go's documentation and build packages. `go/build.Default` uses the compiled binary's Go architecture, operating system, and GOROOT when environment overrides are absent. Building with Go 1.25 therefore changes the installed binary's standard-library source view compared with the current Go 1.26 package.

The command-line interface and package version remain unchanged. Generated documentation can differ. This compatibility choice is explicit and temporary; it must be revisited when gomarkdoc is updated or Go 1.25 leaves the supported Nixpkgs window.

## Strongest evidence

### Stable-versus-master snapshot

- `4590696c...` is a `release-25.11` backport and maps `buildGoModule` to `buildGo125Module`.
- `acd02b877...` is a master revision and maps `buildGoModule` to `buildGo126Module`.
- Both package snapshots use gomarkdoc 1.1.0, the same source/vendor hashes, and `subPackages = [ "cmd/gomarkdoc" ]`.

### Repair isolation

- Run: [`30692403974`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692403974)
- Job: `91349338842` — success
- Carrier head: `c1b0b0f1ffb92d989e84cfceefe1ab18b8b670bb`
- Artifact: [`8816151764`](https://github.com/teamleaderleo/fieldwork/actions/runs/30692403974/artifacts/8816151764)
- Digest: `sha256:8597cc8e25daa9975c20a36c1a824d939820f373bc8a0521d2a022ac60e5471e`

Detailed receipt: [`receipts/2026-08-01-repair-isolation.md`](./receipts/2026-08-01-repair-isolation.md).

### Broader-suite negative control

Run [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557) proved that clearing `subPackages` reaches root, command, formatter, and language packages. The broader suite then failed deterministic standard-library prose goldens on Linux and Darwin. Both recorded expectations align only with Go 1.21 or older, outside the current supported Nixpkgs Go window.

Detailed receipt: [`receipts/2026-08-01-full-discovery-failure.md`](./receipts/2026-08-01-full-discovery-failure.md).

## Independent review

The complete simplified source diff, historical snapshots, builder behavior, upstream tests, target executions, compatibility effect, and public draft were reviewed as a separate pass. The source direction is accepted for exact-head execution; no external review dependency remains in this unit.

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

1. Run exact source head `5c17b14e...` on x86_64-linux and aarch64-darwin.
2. Preserve command-package, installed-help, version, artifact, integrity, and Linux `nixpkgs-review` receipts.
3. Recheck the current public head and regenerate the one-file commit before authorized submission.
4. Hand the accepted research packet to the user for the final public-upstream decision.

No public upstream interaction occurred.
