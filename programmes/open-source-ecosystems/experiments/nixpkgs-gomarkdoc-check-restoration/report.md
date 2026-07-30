# Nixpkgs gomarkdoc check restoration

## In simple words

Current Nixpkgs builds gomarkdoc with its upstream tests disabled. The package tests call gomarkdoc's CLI parser in-process, so ambient `GOFLAGS=-mod=vendor` is mistaken for a gomarkdoc application flag and rejected.

The bounded repair restores checks and removes only the package-manager token from `GOFLAGS` during `preCheck`. The vendor tree remains materialized, Go 1.18's vendor selection remains available, and the shared `buildGoModule` framework stays unchanged.

## Exact source fence

- Nixpkgs commit: `bbbd95e512a066deaefa89e3a244b541ed6c8c7f`.
- Package path: `pkgs/by-name/go/gomarkdoc/package.nix`.
- Framework path: `pkgs/build-support/go/module.nix`.
- gomarkdoc version: `1.1.0`.
- Fieldwork issue: #241.

At this fence:

- the package carries `doCheck = false` and the GOFLAGS collision comment;
- `buildGoModule` materializes `vendor/` for non-proxy vendoring;
- it exports `GOFLAGS` with `-mod=vendor` and usually `-trimpath`;
- `checkPhase` removes only `-trimpath` before invoking `go test`.

## Candidate

```nix
  doCheck = true;

  preCheck = ''
    export GOFLAGS="''${GOFLAGS//-mod=vendor/}"
  '';
```

The doubled single quote preserves shell interpolation inside the Nix indented string. The substitution removes only `-mod=vendor`; other package-specific Go flags remain available.

## Execution matrix

The owned workflow applies the one-file patch to the exact source fence and runs on:

- `x86_64-linux` through `ubuntu-24.04`;
- `aarch64-darwin` through `macos-14`.

Each job must:

1. evaluate the patched package;
2. build `gomarkdoc` with checks enabled;
3. retain logs containing `Running phase: checkPhase`;
4. retain the successful `github.com/princjef/gomarkdoc/cmd/gomarkdoc` test line;
5. build `gomarkdoc.tests.version`;
6. keep the diff limited to the one package expression.

## Evidence boundary

Source mechanism and patch spelling are source-read. The candidate becomes target-executed only after both platform jobs pass at one exact Fieldwork head. A platform-specific failure must be classified as package behavior, Nix runner setup, cache/fetch behavior, or target test failure before changing the repair.

## Contact boundary

Owned Fieldwork execution only. No public Nixpkgs or gomarkdoc interaction is authorized or included.
