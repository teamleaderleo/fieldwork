# Tests and receipts — unit 22 gomarkdoc checks

## Current conclusion

The submitted source uses the same final package-file blob that passed prior x86_64-linux and aarch64-darwin package, selected command-test, installed-help, version, binary-identity, and `nixpkgs-review` controls.

Disposition: `SUBMITTED — exact-current-head execution pending`.

## Submitted source fence

- Upstream pull request: [gomarkdoc: restore checks on Go 1.26](https://redirect.github.com/NixOS/nixpkgs/pull/549377)
- Base: `356468b500e85491b610431c87a284ca1f41b7bc`
- Head: `060a1f8b8af68af858be896715c5dfc540522235`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Relation: one commit, one file, six additions, four deletions
- Final package-file blob: `53f4eef322e84133c2c867070a55c60bb14e09ae`

The submitted head has not yet received retained exact-head package execution. The upstream repository reports successful `Eval Summary` and `no PR failures`; its separate `Test` workflow is `action_required` with no exposed failed job.

## Prior accepted source fence

- Base: `97d48ba11e7eeb6896e9da8d64b22b306da14103`
- Head: `e8d97d5d8c67a9473a7aaad3961c0630583aa34b`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Relation: one commit, one file, six additions, four deletions
- Final package-file blob: `53f4eef322e84133c2c867070a55c60bb14e09ae`

The package-file blob is identical to the submitted source. The following receipts support the patch content but remain exact to this earlier base/head.

## aarch64-darwin acceptance

- Run: `30693522616`
- Job: `91352347312` — success
- Runner: macOS 14.8.7 arm64; image `macos-14-arm64` version `20260629.0180.1`
- Nix: 2.35.1
- Go: 1.26.5
- Source head/parent, one-file fence, `diff --check`: success
- `cmd/gomarkdoc` tests and exactly one package result: success
- Installed help and version `1.1.0`: success
- Checks-disabled baseline/candidate executable `cmp`: success
- Shared executable SHA-256: `199ac9faabb41a65e784ac6128f38c3ccb6d97040e4f69d2b3bbd9b79baa817d`
- Artifact: `8816500818`
- Digest: `sha256:313220b9f7ffff28a8023c249232ba0114eba457d1da38dad7122719bcc0d3e2`

## x86_64-linux acceptance

- Run: `30694249810`
- Job: `91354242933` — success
- Runner: Ubuntu 22.04.5 LTS; image `ubuntu-22.04` version `20250720.1`
- Nix: 2.35.1
- Go: 1.26.5
- Source head/parent, one-file fence, `diff --check`: success
- `cmd/gomarkdoc` tests and exactly one package result: success
- Installed help and version `1.1.0`: success
- Exact-parent review command:

```bash
nixpkgs-review rev \
  -b 97d48ba11e7eeb6896e9da8d64b22b306da14103 \
  HEAD --no-shell
```

- `nixpkgs-review`: success; report lists one package built, `gomarkdoc`
- Artifact: `8816799835`
- Digest: `sha256:a5ab307bc9102b1c8ccea478dde8c58b21c8dcf6ce56a617ca13c9c6cd8c4cb6`

## Repair isolation

Run `30692403974`, job `91349338842`, proved:

- Go 1.25 passes with both, either, or neither fixture/flag cleanup;
- Go 1.26 fails even with both;
- the fixture and `GOFLAGS` cleanups are not repair requirements.

Artifact `8816151764`, digest `sha256:8597cc8e25daa9975c20a36c1a824d939820f373bc8a0521d2a022ac60e5471e`.

## Go 1.26 binary comparison

Run `30692966149`, job `91350898702`, passed the selected command tests, help, version, and checks-disabled baseline/candidate executable comparison.

Shared executable SHA-256: `b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e`.

Artifact `8816337182`, digest `sha256:14ae794f8160a5f6c68bcf113dd430d628fa4b8399ad9ceb65f1d5f33770e5e1`.

## Broad-discovery negative control

Run `30674969557` reached root, command, formatter, and language packages on Linux and Darwin. `lang` failed `[Scanner] != Scanner` and `*[os.File] != *os.File`. These expectations require older standard-library prose.

This result limits the contribution claim to the existing package-selected `cmd/gomarkdoc` tests. It does not claim the complete upstream package set passes.

## Go 1.27rc2 forecast

Run `30693795784`, job `91353047424`, passed the selected command tests, installed help, and version under Go 1.27rc2.

Artifact `8816586391`, digest `sha256:7e838a7596cfecda65876899bd5c5b8ee9cbd2907e8aef6c022fb4a1cd2653dd`.

This is advisory. The submitted base uses Go 1.26.

## Evidence conclusion

The one-line command-golden update is causal, sufficient for the package-selected command tests, and product-neutral at the executable-byte level on the prior executed fence.

The remaining evidence task is current-head execution of submitted commit `060a1f8b...` or an equivalent upstream CI receipt. Any source-head change expires the current submitted-fence description and must be recorded before further review.
