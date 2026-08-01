# Receipt — selected gomarkdoc command checks

Date: `2026-08-01`  
Source base: `55096b0ce13784d4f6420059c5627475fa26ebb1`  
Source head: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`  
Carrier head: `c95da0c4b3f460df9bc8f342e98d05345da66df8`  
Workflow run: [`30690828310`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310)  
Fieldwork integrity: [`30690828341`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828341)

## Source controls

The completed Darwin job verified:

- exact source head `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`;
- exact parent `55096b0ce13784d4f6420059c5627475fa26ebb1`;
- one changed file: `pkgs/by-name/go/gomarkdoc/package.nix`;
- `git diff --check` success.

## aarch64-darwin

- Job: `91345125710` — `success`
- Runner: macOS 14.8.7, image `macos-14-arm64` version `20260629.0180.1`
- Nix: 2.35.1
- Go: 1.25.12
- Artifact: [`8815619734`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310/artifacts/8815619734)
- Artifact digest: `sha256:db5516d38b64307b5d67ffb6bc23c33028dbdeaeb2b681b60a1cc7440958021a`
- Artifact size: 5478 bytes
- Artifact files: 5

Established:

```text
Building subPackage ./cmd/gomarkdoc
Running phase: checkPhase
ok github.com/princjef/gomarkdoc/cmd/gomarkdoc
```

The workflow observed exactly one selected gomarkdoc package result line, installed `bin/gomarkdoc`, and accepted its help output:

```text
generate markdown documentation for golang code
Usage:
```

The version passthru built and printed:

```text
1.1.0
```

`nixpkgs-review` is Linux-only and was skipped as designed.

Evidence class: `target-executed` for aarch64-darwin package build, selected command check, installed help, and version passthru.

## x86_64-linux

- Job: `91345125742`
- State at latest packet update: `queued`
- Required additional gate: `nixpkgs-review rev HEAD --no-shell`

Evidence class while queued: `target-test-prepared`.

## Fieldwork integrity

Run `30690828341` remained queued at the latest packet update.

## Current conclusion

The narrowed clean source passes its complete Darwin validation fence. Linux package/check/help/version/review and current integrity remain the execution blockers behind disposition `HOLD`.
