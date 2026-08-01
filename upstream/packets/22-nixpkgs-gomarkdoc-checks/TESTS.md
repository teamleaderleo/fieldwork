# Tests and receipts — unit 22 gomarkdoc checks

## Current conclusion

The selected Go 1.26 golden content passes patch-equivalent aarch64-darwin command, help, version, and binary-identity controls. The canonical source is now regenerated on current public Nixpkgs head `97d48ba1...` as `e8d97d5d...`; exact current-base execution remains.

Disposition: `EXECUTE`.

## Canonical source fence

- Base: `97d48ba11e7eeb6896e9da8d64b22b306da14103`
- Head: `e8d97d5d8c67a9473a7aaad3961c0630583aa34b`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Relation: one commit, one file, six additions, four deletions
- Final package blob: `53f4eef322e84133c2c867070a55c60bb14e09ae`

## Repair-isolation execution

- Run: `30692403974`
- Job: `91349338842` — success
- Artifact: `8816151764`
- Digest: `sha256:8597cc8e25daa9975c20a36c1a824d939820f373bc8a0521d2a022ac60e5471e`

Go 1.25 passed with neither fixture nor flag cleanup; Go 1.26 failed with both. Conclusion: the environment edits are unnecessary and the Go 1.26 golden differs.

## Go 1.26 golden comparison

Patch-equivalent source `3a036ab91fa1de2fbbd038b2b212552cff1cc5bf` ran in `30692966149`, job `91350898702`, on macOS 14.8.7 arm64 with Nix 2.35.1 and Go 1.26.5.

Established:

```text
Running phase: checkPhase
ok github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

Additional controls:

- exactly one gomarkdoc package result;
- installed help accepted;
- version passthru `1.1.0`;
- baseline/candidate executables passed `cmp`;
- shared SHA-256 `b8bc993930c3a8af5ebf141d0fa5e2f422b117a420630f532296e20e4428e93e`.

Artifact `8816337182`, digest `sha256:14ae794f8160a5f6c68bcf113dd430d628fa4b8399ad9ceb65f1d5f33770e5e1`, expires 2026-08-31T09:05:52Z.

The canonical current-base commit uses the same package blob but needs exact execution because its surrounding Nixpkgs tree changed.

## Full-discovery negative control

Run `30674969557` reached root, command, formatter, and language packages on Linux/Darwin. `lang` failed `[Scanner] != Scanner` and `*[os.File] != *os.File`. Evidence class: target-executed negative control.

## Superseded pin execution

The Go 1.25 source `5c17b14e...` passed exact aarch64-darwin gates in run `30692796676`. It is not canonical.

## Required current-base commands

```bash
nix-build .candidate/nixpkgs -A gomarkdoc --no-out-link
nix-build .candidate/nixpkgs -A gomarkdoc.tests.version --no-out-link
nixpkgs-review rev HEAD --no-shell  # Linux
```

Darwin must also build the checks-disabled current-base package and compare its installed binary with the candidate.

## Missing evidence

- x86_64-linux exact head `e8d97d5d...`;
- aarch64-darwin exact head `e8d97d5d...` plus current-base binary identity;
- Linux `nixpkgs-review`;
- Fieldwork integrity covering the packet consuming final receipts.
