# Receipt — selected gomarkdoc command checks

Date: `2026-08-01`  
Source base: `55096b0ce13784d4f6420059c5627475fa26ebb1`  
Source head: `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`

## aarch64-darwin — executed

Carrier head: `c95da0c4b3f460df9bc8f342e98d05345da66df8`  
Workflow run: [`30690828310`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690828310)  
Job: `91345125710` — `success`

### Source controls

The completed Darwin job verified:

- exact source head `569c0c4d11e5a14f3fe6237c0a50dc484f80e744`;
- exact parent `55096b0ce13784d4f6420059c5627475fa26ebb1`;
- one changed file: `pkgs/by-name/go/gomarkdoc/package.nix`;
- `git diff --check` success.

### Runtime and artifact

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

`nixpkgs-review` was skipped as designed because that gate is Linux-only.

Evidence class: `target-executed` for aarch64-darwin package build, selected command check, installed help, and version passthru.

## x86_64-linux — packet-anchored gate

Packet base: `527021b7ff1535e8be4f27dc3ba7226b559a1630`  
Carrier head: `178e6388bf06b965970dd3ab7435db9e756a13e4`  
Carrier fence: one commit changing `.github/workflows/unit-22-gomarkdoc-checks.yml`  
Workflow run: [`30691551270`](https://github.com/teamleaderleo/fieldwork/actions/runs/30691551270)  
Job: `91347062784`

State at this packet update: `queued`.

The job is prepared to verify:

- carrier parent equals packet base `527021b7ff1535e8be4f27dc3ba7226b559a1630`;
- exact source head and parent;
- one-file source fence and `git diff --check`;
- package build and selected `cmd/gomarkdoc` check;
- exactly one gomarkdoc package result line;
- installed help output;
- version passthru `1.1.0`;
- `nixpkgs-review rev HEAD --no-shell`;
- uploaded source diff, package log, package list, help, version, and review receipts.

Evidence class while queued: `target-test-prepared`.

## Fieldwork integrity — packet-anchored gate

- Packet base: `527021b7ff1535e8be4f27dc3ba7226b559a1630`
- Carrier head: `178e6388bf06b965970dd3ab7435db9e756a13e4`
- Run: [`30691551312`](https://github.com/teamleaderleo/fieldwork/actions/runs/30691551312)
- Job: `91347062807`
- State at this packet update: `queued`

This run validates the packet content through `527021b7ff1535e8be4f27dc3ba7226b559a1630` plus the one-file carrier diff. Receipt-only packet commits made afterward must be identified as such.

## Superseded queued generation

Run `30690828310` also contains Linux job `91345125742`, which remained queued after the carrier branch was rebuilt. It is superseded by packet-anchored Linux run `30691551270`. Its completed Darwin job remains authoritative and preserved above.

Carrier integrity run `30690828341` is likewise superseded by packet-anchored integrity run `30691551312`.

## Current conclusion

The narrowed clean source passes its complete Darwin validation fence. Packet-anchored Linux package/check/help/version/review and integrity receipts remain the execution blockers behind disposition `HOLD`.
