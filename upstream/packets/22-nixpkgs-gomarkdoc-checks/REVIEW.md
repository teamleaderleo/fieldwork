# Review — unit 22 gomarkdoc command checks

## Current review identity

- Work class: `submitted upstream contribution`
- Submitted pull request: [gomarkdoc: restore checks on Go 1.26](https://redirect.github.com/NixOS/nixpkgs/pull/549377)
- Submitted base: `356468b500e85491b610431c87a284ca1f41b7bc`
- Submitted head: `060a1f8b8af68af858be896715c5dfc540522235`
- Changed-file fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Source relation: one commit, one file, six additions, four deletions
- Final package-file blob: `53f4eef322e84133c2c867070a55c60bb14e09ae`
- Upstream interaction: user-submitted pull request; no additional automated interaction

## Complete-diff result

The submitted source:

- removes the stale diagnostic-based disable-tests explanation and `doCheck = false`;
- adds one `postPatch` replacement for the Go 1.26 command golden;
- uses `--replace-fail` to reject unexpected source drift;
- retains the current Go builder and `subPackages = [ "cmd/gomarkdoc" ]`.

It does not change the package version, hashes, dependencies, command selection, linker flags, metadata, product source, or generic Go check implementation.

The submitted commit also includes the required `Assisted-by: ChatGPT (GPT-5.6 Thinking)` trailer. The pull-request summary contains a separate automation disclosure reviewed by the user.

## Prior accepted review

The independent review at source head `e8d97d5d8c67a9473a7aaad3961c0630583aa34b` accepted the same package-file blob and established:

1. fixture and `GOFLAGS` edits are not repair requirements;
2. the public issue compares a Go 1.25 release snapshot with Go 1.26 master;
3. a Go 1.25 pin changes the shipped toolchain and was rejected;
4. claims must stay limited to the package-selected command tests;
5. the one-line Go 1.26 expected-output update is causal and sufficient;
6. checks-disabled and checks-enabled installed executables are byte-identical.

## Evidence table

| Claim | Evidence class | Exact support | Current limit |
| --- | --- | --- | --- |
| fixture and flag cleanup are unnecessary | `target-executed` matrix | run `30692403974` | prior exact source generation |
| Go 1.26 fails before the expected-output update | `target-executed` negative control | prior matrix and comparison | prior exact source generation |
| one-line update passes selected command tests | `target-executed` | Linux `30694249810`; Darwin `30693522616` | same package-file blob, earlier base/head |
| baseline/candidate executable is byte-identical | `target-executed` comparative control | `30692966149` and Darwin acceptance | same package-file blob, earlier base/head |
| installed help and version pass | `target-executed` | Linux and Darwin acceptance runs | same package-file blob, earlier base/head |
| exact-parent `nixpkgs-review` passes | `integration-executed` | Linux `30694249810` | earlier exact parent |
| Go 1.27rc2 command check remains green | advisory `target-executed` | `30693795784` | forecast only |
| submitted diff is one file and matches the accepted file blob | `source-read` | submitted head `060a1f8b...` | does not execute the new base |

## Current disposition

`SUBMITTED — CURRENT-HEAD EXECUTION PENDING`

The prior `ACCEPT` remains valid for the patch content and package-file blob. It is not an exact-head acceptance receipt for submitted commit `060a1f8b...` on base `356468b...`.

As checked after submission:

- the pull request is open, non-draft, and mergeable;
- reviewer `brpaz` is requested;
- `Eval Summary` and `no PR failures` are successful;
- the separate `Test` workflow is `action_required`, with no exposed failed job;
- no upstream review or discussion comment has been posted.

## Clearing condition

Obtain current-head package execution or equivalent upstream CI, then review any changed source head or maintainer-requested repair. Preserve the command-only coverage boundary and keep the Go 1.27 result advisory.

Further upstream comment, review, reaction, or message requires the user's direction for that exact interaction.
