# Receipt — current-base acceptance

Date: `2026-08-01`

## Canonical source

- Public base: `97d48ba11e7eeb6896e9da8d64b22b306da14103`
- Candidate head: `e8d97d5d8c67a9473a7aaad3961c0630583aa34b`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Relation: one commit, one file, six additions, four deletions
- Final package blob: `53f4eef322e84133c2c867070a55c60bb14e09ae`

## aarch64-darwin acceptance

- Run: [`30693522616`](https://github.com/teamleaderleo/fieldwork/actions/runs/30693522616)
- Job: `91352347312` — success
- Platform: macOS 14.8.7 arm64
- Runner image: `macos-14-arm64` version `20260629.0180.1`
- Nix: 2.35.1
- Go: 1.26.5

Established:

- exact source head and parent;
- one changed package file and `git diff --check`;
- `Running phase: checkPhase`;
- `ok github.com/princjef/gomarkdoc/cmd/gomarkdoc`;
- exactly one selected gomarkdoc package result;
- installed help output;
- version `1.1.0`;
- checks-disabled current-base baseline and candidate executables pass `cmp`.

Shared executable SHA-256:

```text
199ac9faabb41a65e784ac6128f38c3ccb6d97040e4f69d2b3bbd9b79baa817d
```

Artifact:

- ID: [`8816500818`](https://github.com/teamleaderleo/fieldwork/actions/runs/30693522616/artifacts/8816500818)
- Digest: `sha256:313220b9f7ffff28a8023c249232ba0114eba457d1da38dad7122719bcc0d3e2`
- Size: 6260 bytes
- Files: eight
- Expires: `2026-08-31T09:21:19Z`

## x86_64-linux acceptance

- Run: [`30694249810`](https://github.com/teamleaderleo/fieldwork/actions/runs/30694249810)
- Job: `91354242933` — success
- Platform: Ubuntu 22.04.5 LTS x86_64
- Runner image: `ubuntu-22.04` version `20250720.1`
- Nix: 2.35.1
- Go: 1.26.5

Established:

- exact source head and parent;
- one changed package file and `git diff --check`;
- `Running phase: checkPhase`;
- `ok github.com/princjef/gomarkdoc/cmd/gomarkdoc`;
- exactly one selected gomarkdoc package result;
- installed help output;
- version `1.1.0`.

Exact-parent review:

```bash
nixpkgs-review rev \
  -b 97d48ba11e7eeb6896e9da8d64b22b306da14103 \
  HEAD --no-shell
```

Result: success. The report lists one package built:

```text
gomarkdoc
```

Artifact:

- ID: [`8816799835`](https://github.com/teamleaderleo/fieldwork/actions/runs/30694249810/artifacts/8816799835)
- Digest: `sha256:a5ab307bc9102b1c8ccea478dde8c58b21c8dcf6ce56a617ca13c9c6cd8c4cb6`
- Size: 11433 bytes
- Expires: `2026-08-31T09:51:21Z`

## Test-only fixture confirmation

`command_test.go` writes generated output to `README-test.md` and compares it against `README.md`. The patched `testData/docs/README.md` is the expected golden and is not the generated product path.

## Conclusion

The canonical one-line golden update restores the selected command checks on current Go 1.26, preserves the installed executable on Darwin, passes Linux exact-parent `nixpkgs-review`, and is accepted by the independent review lane.

Evidence class: `target-executed current-base acceptance`.
