# Upstream issue route — unit 22 gomarkdoc checks

## Status

`EXISTING ISSUE LINKED FROM SUBMITTED PULL REQUEST`

- Existing issue: [gomarkdoc checkPhase regression](https://redirect.github.com/NixOS/nixpkgs/issues/516481)
- Submitted pull request: [gomarkdoc: restore checks on Go 1.26](https://redirect.github.com/NixOS/nixpkgs/pull/549377)

No duplicate issue was opened. The submitted pull request uses `Closes #516481` and explains the corrected diagnosis.

## Corrected diagnosis

The public issue compares a Go 1.25 release branch with Go 1.26 master. Comparative execution established:

- creating `.gomarkdoc-empty.yml` is unnecessary for the selected command-test repair;
- removing Nix's inherited `GOFLAGS` is unnecessary for the selected command-test repair;
- Go 1.26 fails the command documentation golden even with both cleanups;
- updating one expected Go 1.26 Markdown line restores the package-selected command tests;
- the visible missing-file and unknown-flag messages are captured output, not the failing assertion.

## Submitted route

The user opened a direct pull request against Nixpkgs `master` from:

- branch `teamleaderleo/nixpkgs:contrib/gomarkdoc-go126-checks`;
- head `060a1f8b8af68af858be896715c5dfc540522235`;
- base `356468b500e85491b610431c87a284ca1f41b7bc`.

The submitted body explains the toolchain difference, the one-line expected-output update, the rejected fixture/`GOFLAGS` explanations, the unchanged installed program, prior Linux/Darwin evidence, and the automation disclosure.

## Issue-comment decision

A separate issue comment is unnecessary while the pull request carries the diagnosis and closes the issue. Do not add an issue comment merely to repeat the pull-request body.

If maintainers ask for clarification, prepare the reply in Fieldwork first and obtain the user's direction for that exact upstream interaction.

## Authority and interaction checklist

- [x] Existing issue found.
- [x] Duplicate issue avoided.
- [x] Causal claim independently checked.
- [x] Installed-output identity tested on the prior accepted source fence.
- [x] Current contribution and automation-disclosure requirements rechecked before submission.
- [x] User opened the submitted pull request.
- [x] No automated upstream comment, review, reaction, or message was posted.
- [ ] Current-head package execution or equivalent upstream CI retained.
- [ ] Maintainer review resolved.
- [ ] Merge, closure, withdrawal, or supersession recorded.
