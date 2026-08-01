# Receipt — independent code review

Date: `2026-08-01`

## Assignment

The user assigned this workstream responsibility for independent review and retained the final-mile authority for any public upstream action.

## Reviewed scope

- Source repository: `teamleaderleo/nixpkgs`
- Base: `55096b0ce13784d4f6420059c5627475fa26ebb1`
- Final reviewed source: `5c17b14e271611c3418e3e2f572366766f6aa3cc`
- Complete source fence: `pkgs/by-name/go/gomarkdoc/package.nix`
- Historical package/builder snapshots at `4590696c...` and `acd02b877...`
- gomarkdoc v1.1.0 command implementation, tests, Go module, Mage test task, and CI workflow
- Go 1.21, 1.22, 1.23, 1.25 standard-library documentation behavior
- Nixpkgs Go-builder behavior and versioned-builder policy
- Full-discovery and repair-isolation execution receipts
- Packet issue and pull-request drafts

## Findings

### High — original cause was incorrect

The passing and failing revisions come from different Nixpkgs lines. The passing release snapshot uses Go 1.25; failing master uses Go 1.26. A target matrix proves the fixture and Nix `GOFLAGS` are not required.

Action: source and packet rewritten.

### Medium — source carried unnecessary mutations

The prior candidate synthesized an empty config and rewrote `GOFLAGS`. Both were disproved as repair requirements.

Action: removed from source.

### Medium — product compatibility effect was understated

Changing the builder changes the installed binary's compiled GOROOT view and can alter generated documentation.

Action: packet and PR draft now state this explicitly and treat the pin as temporary.

### Medium — full-suite wording exceeded supported policy

The broader language goldens require Go 1.21 or older, outside current supported Nixpkgs builders.

Action: full discovery retained as a negative control; selected coverage limited to the built command package.

## Complete-diff judgment

The final source is the smallest proven package repair:

- one commit;
- one file;
- `buildGo125Module`;
- removal of `doCheck = false`;
- no custom phase, fixture, test skip, test patch, dependency change, hash change, or output-selection change.

No source defect remains from the independent code review.

## Disposition

`EXECUTE`

The source direction is accepted. Fresh exact-head Linux and Darwin target execution is required because the source head changed after the comparative experiment.

After those receipts and packet integrity pass, the review lane can issue `ACCEPT` for handoff to the user's final-mile decision.

## Authority

This review does not authorize a public pull request, issue comment, reaction, or maintainer contact.
