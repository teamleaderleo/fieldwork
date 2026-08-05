# Handoff — unit 22 gomarkdoc checks

## Current disposition

`SUBMITTED`

The user opened the upstream pull request. The submitted source keeps the accepted Go 1.26 golden repair and includes the required automation disclosures.

- Upstream pull request: [gomarkdoc: restore checks on Go 1.26](https://redirect.github.com/NixOS/nixpkgs/pull/549377)
- Related upstream issue: [gomarkdoc checkPhase regression](https://redirect.github.com/NixOS/nixpkgs/issues/516481)

## Submitted source

- repository: `teamleaderleo/nixpkgs`;
- branch: `contrib/gomarkdoc-go126-checks`;
- base: `356468b500e85491b610431c87a284ca1f41b7bc`;
- head: `060a1f8b8af68af858be896715c5dfc540522235`;
- changed file: `pkgs/by-name/go/gomarkdoc/package.nix`;
- relation: one commit, one file, six additions, four deletions;
- final package-file blob: `53f4eef322e84133c2c867070a55c60bb14e09ae`.

## Source decision

- retain the default Go 1.26 builder;
- restore selected command tests by removing `doCheck = false`;
- update one expected Markdown line in `testData/docs/README.md`;
- retain `subPackages = [ "cmd/gomarkdoc" ]`;
- do not create the missing fixture;
- do not rewrite `GOFLAGS`;
- do not claim broader root, formatter, or `lang` package coverage.

## Prior execution supporting the unchanged patch

### aarch64-darwin

- run `30693522616`, job `91352347312`: success;
- package, command tests, help, version, and baseline/candidate executable identity: success;
- artifact `8816500818`;
- digest `sha256:313220b9f7ffff28a8023c249232ba0114eba457d1da38dad7122719bcc0d3e2`.

### x86_64-linux

- run `30694249810`, job `91354242933`: success;
- package, command tests, help, and version: success;
- exact-parent `nixpkgs-review`: success; one package built (`gomarkdoc`);
- artifact `8816799835`;
- digest `sha256:a5ab307bc9102b1c8ccea478dde8c58b21c8dcf6ce56a617ca13c9c6cd8c4cb6`.

Supporting runs:

- repair isolation `30692403974`;
- Go 1.26 binary comparison `30692966149`;
- broad-suite negative control `30674969557`;
- Go 1.27rc2 forecast `30693795784`.

## Current upstream state

As checked after submission:

- pull request is open, non-draft, and mergeable;
- reviewer `brpaz` is requested;
- `Eval Summary` and `no PR failures` are successful;
- the separate `Test` workflow is `action_required` with no exposed failed job;
- no review or discussion comment has been posted.

The previous execution belongs to an earlier exact source head with the identical package-file blob. It is supporting evidence, not exact-head execution of submitted commit `060a1f8b...`.

## Continuation

1. obtain current-head CI or equivalent exact-head package execution;
2. record maintainer review and any requested repair;
3. update exact head and evidence if the branch moves;
4. record merge, closure, withdrawal, or supersession;
5. perform no additional upstream comment, reaction, review, or message unless the user directs that exact interaction.

## Public interaction

The user performed the submitted upstream interaction. Fieldwork automation performed no additional upstream contact.
