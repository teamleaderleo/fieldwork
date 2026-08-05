# Submitted upstream pull request — unit 22 gomarkdoc checks

## Submission

- Title: `gomarkdoc: restore checks on Go 1.26`
- Pull request: [submitted upstream pull request](https://redirect.github.com/NixOS/nixpkgs/pull/549377)
- Related issue: [gomarkdoc checkPhase regression](https://redirect.github.com/NixOS/nixpkgs/issues/516481)
- Submitted branch: `teamleaderleo/nixpkgs:contrib/gomarkdoc-go126-checks`
- Submitted head: `060a1f8b8af68af858be896715c5dfc540522235`
- Submitted base: `356468b500e85491b610431c87a284ca1f41b7bc`
- Submitted at: `2026-08-05`

## Submitted summary

The pull request explains that gomarkdoc 1.1.0's command tests generate Markdown from fixture packages and compare it with expected output.

With Go 1.26, one field reference is rendered as a documentation link instead of escaped plain text. The patch updates that expected line and removes `doCheck = false`, restoring the existing `cmd/gomarkdoc` tests.

It also corrects the public issue's causal interpretation: the visible `GOFLAGS` and missing-config diagnostics are not the failing assertion. Removing `-mod=vendor` or creating `.gomarkdoc-empty.yml` does not fix the Go 1.26 failure; the failing assertion is the generated-Markdown mismatch.

The pull request states that `subPackages = [ "cmd/gomarkdoc" ]` remains unchanged and that the package version, source hash, vendor hash, Go toolchain, linker flags, and installed program do not change.

## Validation disclosed in the pull request

The pull request reports prior execution of the identical package-file change on:

- x86_64-linux: command tests, `gomarkdoc --help`, version `1.1.0`, and `nixpkgs-review` passed;
- aarch64-darwin: command tests, help, version, and checks-disabled/checks-enabled executable identity passed;
- Go 1.27rc2: command tests, help, and version passed as an advisory forecast.

It explicitly states that the current commit applies the same one-file change to a newer Nixpkgs `master` revision and that tests for the current commit are pending.

## Automation disclosure

The submitted commit includes:

```text
Assisted-by: ChatGPT (GPT-5.6 Thinking)
```

The pull-request body separately discloses that ChatGPT using GPT-5.6 Thinking assisted with source analysis, test planning, review, and drafting, and that the user reviewed the change and evidence and accepts responsibility for the contribution.

## Current upstream state

As checked after submission:

- open, non-draft, and mergeable;
- one commit and one changed file;
- reviewer `brpaz` requested;
- `Eval Summary` and `no PR failures` successful;
- separate `Test` workflow marked `action_required`, with no exposed failed job;
- no review or discussion comment posted.

## Interaction boundary

The user opened the pull request. Fieldwork automation did not post an upstream comment, review, reaction, or message. Further upstream interaction requires the user's direction for that exact action.
