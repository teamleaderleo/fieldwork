# Unit 22 — gomarkdoc command checks

## Current answer

Nixpkgs disables gomarkdoc 1.1.0's command tests. The visible missing-config and `GOFLAGS` diagnostics in the public report are captured output, not the failing assertion.

Go 1.26 changes one generated Markdown line by resolving a field reference as a documentation link. The submitted repair updates that expected line and removes `doCheck = false`, restoring the existing `cmd/gomarkdoc` tests without changing the package version, source, vendor hash, Go toolchain, linker flags, command selection, or installed executable.

## Disposition

`SUBMITTED`

- Upstream pull request: [gomarkdoc: restore checks on Go 1.26](https://redirect.github.com/NixOS/nixpkgs/pull/549377)
- Related upstream issue: [gomarkdoc checkPhase regression](https://redirect.github.com/NixOS/nixpkgs/issues/516481)
- Submitted branch: `teamleaderleo/nixpkgs:contrib/gomarkdoc-go126-checks`
- Submitted head: `060a1f8b8af68af858be896715c5dfc540522235`
- Submitted base: `356468b500e85491b610431c87a284ca1f41b7bc`
- Changed file: `pkgs/by-name/go/gomarkdoc/package.nix`
- Fence: one commit, one file, six additions, four deletions
- Final package-file blob: `53f4eef322e84133c2c867070a55c60bb14e09ae`

The user opened the upstream pull request. No additional upstream comment, review, reaction, or message was performed by Fieldwork automation.

## Submitted source change

```nix
# Go 1.26 resolves this field reference while generating the command golden.
postPatch = ''
  substituteInPlace testData/docs/README.md \
    --replace-fail 'GetField gets \[\*AnotherStruct.Field\].' \
    'GetField gets [\\\*AnotherStruct.Field](<#AnotherStruct>).'
'';
```

Removing `doCheck = false` restores the generic Go builder's selected command-package tests. `subPackages = [ "cmd/gomarkdoc" ]` remains unchanged.

## Why this repair

A variant matrix disproved fixture creation and `GOFLAGS` cleanup as sufficient causes. Go 1.26 still failed with both changes; the failing assertion was the one generated-Markdown difference.

A Go 1.26 comparison proved the checks-enabled installed executable was byte-for-byte identical to the checks-disabled baseline. The repair restores validation without changing the installed program.

## Retained evidence

The identical final package-file blob was executed at source head `e8d97d5d8c67a9473a7aaad3961c0630583aa34b`:

### aarch64-darwin

- run `30693522616`, job `91352347312`: success;
- command tests, one-package count, installed help, and version `1.1.0`: success;
- checks-disabled baseline/candidate executable identity: success;
- artifact `8816500818`;
- digest `sha256:313220b9f7ffff28a8023c249232ba0114eba457d1da38dad7122719bcc0d3e2`.

### x86_64-linux

- run `30694249810`, job `91354242933`: success;
- command tests, one-package count, installed help, and version `1.1.0`: success;
- exact-parent `nixpkgs-review`: success; one package built (`gomarkdoc`);
- artifact `8816799835`;
- digest `sha256:a5ab307bc9102b1c8ccea478dde8c58b21c8dcf6ce56a617ca13c9c6cd8c4cb6`.

Additional evidence:

- repair isolation run `30692403974`;
- Go 1.26 binary comparison run `30692966149`;
- broad-suite negative control run `30674969557`;
- Go 1.27rc2 forecast run `30693795784`;
- independent complete-diff review in `receipts/2026-08-01-independent-code-review.md`.

## Evidence boundary

The prior execution supports the unchanged patch content and final package-file blob. It is not exact-head execution of submitted commit `060a1f8b...` on base `356468b...`.

As checked after submission:

- the upstream pull request is open, non-draft, and mergeable;
- reviewer `brpaz` is requested;
- `Eval Summary` and `no PR failures` are successful;
- the separate `Test` workflow is `action_required` with no exposed job failure;
- no review or discussion comment has been posted.

## Next transition

Obtain current-head CI or equivalent exact-head package execution, then record any maintainer review, changed head, merge, closure, or withdrawal. Further upstream interaction requires the user's direction for that exact action.
