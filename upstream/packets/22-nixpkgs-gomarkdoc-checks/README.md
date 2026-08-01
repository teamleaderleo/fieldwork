# Unit 22 — gomarkdoc: restore checks without leaking Nix GOFLAGS

## In simple words

Nixpkgs packages `gomarkdoc` 1.1.0 with checks disabled. The package builds only `cmd/gomarkdoc`, and Nixpkgs' Go builder applies that same `subPackages` selection during checks.

A full-discovery experiment cleared the selector and ran the broader suite on Linux and Darwin. Root, command, and formatter packages passed, then two `lang` exact-text tests failed on both platforms because modern Go 1.25 standard-library comments contain bracketed documentation links. That result is retained as a negative control rather than hidden with skips or rewritten expectations.

The clean candidate restores the command-package checks corresponding to the installed program. It uses Go 1.25, recreates the empty config fixture omitted from the release tag, and removes Nix's build-only `-mod=vendor` token before gomarkdoc parses `GOFLAGS` as application flags.

The exact clean head passes its complete aarch64-darwin package, command-check, installed-help, and version fence. A clean packet-anchored Linux gate and Fieldwork integrity generation are queued.

## Current disposition

`HOLD`

Last verified: `2026-08-01`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

Clearing condition: Linux run [`30691551270`](https://github.com/teamleaderleo/fieldwork/actions/runs/30691551270) must complete the package, command check, help, version, and `nixpkgs-review` gates; integrity run [`30691551312`](https://github.com/teamleaderleo/fieldwork/actions/runs/30691551312) must pass; receipts must be transferred; execution carrier #437 must be closed; and an independent reviewer must inspect the final source diff. A fresh public-head rebase and rerun remain required before authorized submission.

## Contribution

- Target project: [`NixOS/nixpkgs`](https://github.com/NixOS/nixpkgs)
- Proposed destination: `NixOS/nixpkgs:master`
- Proposed title: `gomarkdoc: restore command checks`
- Work class: `upstream-fork research`
- Synopsis: use `buildGo125Module`, enable the selected command-package tests, remove Nix's `-mod=vendor` token from gomarkdoc's test-time application parsing, and recreate the omitted empty fixture.

## Exact clean source

- Owned fork: [`teamleaderleo/nixpkgs`](https://github.com/teamleaderleo/nixpkgs)
- Branch: [`fieldwork/unit-22-gomarkdoc-checks`](https://github.com/teamleaderleo/nixpkgs/tree/fieldwork/unit-22-gomarkdoc-checks)
- Base: [`55096b0ce13784d4f6420059c5627475fa26ebb1`](https://github.com/NixOS/nixpkgs/commit/55096b0ce13784d4f6420059c5627475fa26ebb1)
- Head: [`569c0c4d11e5a14f3fe6237c0a50dc484f80e744`](https://github.com/teamleaderleo/nixpkgs/commit/569c0c4d11e5a14f3fe6237c0a50dc484f80e744)
- Compare: [`55096b0c...569c0c4d`](https://github.com/teamleaderleo/nixpkgs/compare/55096b0ce13784d4f6420059c5627475fa26ebb1...569c0c4d11e5a14f3fe6237c0a50dc484f80e744)
- Changed file: [`pkgs/by-name/go/gomarkdoc/package.nix`](https://github.com/teamleaderleo/nixpkgs/blob/569c0c4d11e5a14f3fe6237c0a50dc484f80e744/pkgs/by-name/go/gomarkdoc/package.nix)
- Fence: one commit, one file; source/vendor hashes unchanged; no generated or lock files

## Current public-head boundary

Public `master` head [`63c4c8011115076be7a315edd8f740fd751b168a`](https://github.com/NixOS/nixpkgs/commit/63c4c8011115076be7a315edd8f740fd751b168a), dated `2026-08-01T08:02:42Z`, was checked after the candidate execution began.

- It is 384 commits ahead of the candidate base.
- The checked advance contains no change to the gomarkdoc package or Go module builder.
- At that head, gomarkdoc remains version `1.1.0` with `subPackages = [ "cmd/gomarkdoc" ]` and `doCheck = false`.
- The Go builder still uses nonempty `subPackages` for test selection and runs `preCheck` before `getGoDirs test`.

The premise remains current, while the tested source is stale. Submission requires a fresh-head rebase and exact-head rerun.

## Selected source change

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

This preserves the command-only build and check boundary. It does not skip or rewrite the incompatible `lang` tests because those packages are outside the selected build target.

## Evidence

### Prior command-package execution

Runs [`30598626867`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598626867) and [`30598687251`](https://github.com/teamleaderleo/fieldwork/actions/runs/30598687251) passed the Go 1.25 command-package path and version `1.1.0` on Linux and Darwin. Their coverage is exactly one package and their source base is older.

### Full-discovery negative control

Run [`30674969557`](https://github.com/teamleaderleo/fieldwork/actions/runs/30674969557) verified the exact superseded source fence and broad discovery on both platforms, then failed `lang` identically:

```text
[Scanner] != Scanner
*[os.File] != *os.File
```

- Linux job `91300175276`, artifact `8810710677`, digest `sha256:bb7ba3579d8157fa344d1a6e7ba30a5cedf1f32f4f1f1d4eb2e3b2cd077b1a75`
- Darwin job `91300175296`, artifact `8810556627`, digest `sha256:f471756f78106e2b74945a96e5596487baa234f33c3bae83f28195f54dfa106d`
- Fieldwork integrity run `30674969559`: success

Receipt: [`receipts/2026-08-01-full-discovery-failure.md`](./receipts/2026-08-01-full-discovery-failure.md).

### Exact-head Darwin receipt

Darwin job `91345125710` in run [`30690828310`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310) completed successfully on macOS 14.8.7 arm64 with Nix 2.35.1 and Go 1.25.12. It verified the exact source head and parent, one-file fence, `git diff --check`, selected command check, exactly one gomarkdoc package result, installed help, and version `1.1.0`.

- Artifact: [`8815619734`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310/artifacts/8815619734)
- Digest: `sha256:db5516d38b64307b5d67ffb6bc23c33028dbdeaeb2b681b60a1cc7440958021a`
- Size: 5478 bytes; five files

### Packet-anchored Linux and integrity gates

- Carrier PR: [#437](https://github.com/teamleaderleo/fieldwork/pull/437)
- Packet base: `527021b7ff1535e8be4f27dc3ba7226b559a1630`
- Carrier head: `178e6388bf06b965970dd3ab7435db9e756a13e4`
- Carrier fence: one commit changing `.github/workflows/unit-22-gomarkdoc-checks.yml`
- Linux run: [`30691551270`](https://github.com/teamleaderleo/fieldwork/actions/runs/30691551270), job `91347062784` — queued
- Integrity run: [`30691551312`](https://github.com/teamleaderleo/fieldwork/actions/runs/30691551312), job `91347062807` — queued

The Linux job asserts the carrier parent, exact source identity, one-file source fence, selected command check, exactly one gomarkdoc package result, installed help, version `1.1.0`, `nixpkgs-review rev HEAD --no-shell`, and artifact upload.

The integrity generation covers packet content through `527021b7ff1535e8be4f27dc3ba7226b559a1630` plus the one-file carrier. Later packet commits are receipt and status reconciliation.

Receipt: [`receipts/2026-08-01-command-checks.md`](./receipts/2026-08-01-command-checks.md).

## Duplicate and prior art

Search date: `2026-08-01`

- [#516481 — gomarkdoc 1.1.0 checkPhase regressed](https://github.com/NixOS/nixpkgs/issues/516481)
- [#516792 — gomarkdoc: disable tests](https://github.com/NixOS/nixpkgs/pull/516792)
- [#516381 — NixOS 26.05 Zero Hydra Failures](https://github.com/NixOS/nixpkgs/issues/516381)
- [#279440 — gomarkdoc: init at 1.1.0](https://github.com/NixOS/nixpkgs/pull/279440)
- Equivalent restoration PR found: `no`

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Command-check receipt](./receipts/2026-08-01-command-checks.md)
- [Full-discovery negative receipt](./receipts/2026-08-01-full-discovery-failure.md)
- [Upstream issue route](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review guide](./REVIEW.md)
- [Continuation handoff](./HANDOFF.md)
- [Retained source patch](./patches/0001-gomarkdoc-restore-command-checks.patch)

## Remaining work

1. Read terminal Linux run `30691551270` and integrity run `30691551312`.
2. Transfer Linux package/check/help/version/`nixpkgs-review`, artifact, and integrity receipts.
3. Repair only from a concrete failure.
4. Close PR #437 after receipt transfer.
5. Obtain independent complete-diff review.
6. Rebase onto a fresh public Nixpkgs head and rerun before authorized submission.
7. Seek explicit authority for public upstream interaction.

## Latest handoff

State: `HOLD`  
Exact source head: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`  
Executed current evidence: aarch64-darwin package, selected command check, installed help, and version passed  
Queued packet-anchored evidence: x86_64-linux including `nixpkgs-review`, Fieldwork integrity  
Additional blockers: receipt transfer, carrier closure, independent review, fresh-head execution, public-contact authority  
Public upstream interaction: none
