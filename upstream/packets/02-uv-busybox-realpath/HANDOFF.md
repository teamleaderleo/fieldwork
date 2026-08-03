# Handoff — Unit 02: uv BusyBox `realpath` compatibility

Updated: `2026-08-03`

State: `READY FOR HUMAN REVIEW`

External contact: `unauthorized; none occurred`

## Canonical locations

- Routing issue: `teamleaderleo/fieldwork#435`, unit 02
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Fork: `teamleaderleo/uv`
- Clean branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Main execution PR: `teamleaderleo/uv#7` — closed without merge after evidence transfer
- Supplemental Fish PR: `teamleaderleo/uv#18` — execution complete; close without merge after this transfer
- Existing public issue: `astral-sh/uv#16209`

## Exact clean source

- Public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Current clean head: `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`
- Previous byte-identical publication: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Source tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Relationship: one commit ahead, zero behind
- Diff: four files, 89 insertions, 15 deletions

The rerun republished the same validated tree with a new commit identity. The four changed-file blob hashes remain:

```text
49c04343714990cfbc8bf891162b4889678b08f5  crates/uv-install-wheel/src/wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  crates/uv-virtualenv/src/virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  crates/uv/src/commands/project/run.rs
f68dc858066242be1888b922262d53e22975856a  crates/uv/tests/python/venv.rs
```

The source commit contains no workflow, harness, packet, dependency, lockfile, or unrelated file.

## Selected behavior

The correction removes only unsupported `realpath --` delimiters. It retains every `dirname --` delimiter, preserves `realpath` canonicalization for externally symlinked entrypoints, recognizes corrected and historical `python`/`python3` relocatable launchers, and updates the existing uv generated-text expectations.

Review boundaries:

- do not remove `realpath`; historical upstream PR #8079 established its symlink semantics;
- do not remove supported `dirname --` without new evidence;
- do not branch on generator-host BusyBox detection for a relocatable artifact;
- do not add speculative option-like `$0` normalization; direct shebang execution supplies the script path;
- do not broaden the migration parser beyond observed `python` and `python3` producers without a failing generated example.

No active equivalent upstream pull request was found during the latest packet review.

## Terminal validation evidence

### Main exact-source carrier

Run `30753911776`, latest attempt:

- Linux/source job `91621197004`: success
- macOS job `91621196098`: success
- publication job `91621231746`: success

Retained artifacts:

- Linux artifact `8835628919`, digest `sha256:1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`
- macOS artifact `8847852798`, digest `sha256:5053067966a50e9bcf842a9433f9509b89d49e0d202e492884e5ced8f203646b`
- publication artifact `8847875671`, digest `sha256:0c7f3655f2ec681db1d3d2caf4ab1c6a7de29b3657898cb13d96a75b9d849b9d`

The earlier independent publication run also succeeded:

- run/job `30756408587` / `91519210841`
- artifact `8836056361`
- digest `sha256:e0684ec5da7025a7b7cf4a8f7b932e06c3385d07e2146a5e8d5a8c344a2ed634`

### Fish activation supplement

Run `30755096609`:

- GNU and Alpine/BusyBox Fish job `91515786243`: success
- macOS Fish job `91515786224`: success

Retained artifacts:

- Linux Fish artifact `8836836696`, digest `sha256:cf515d657784f09ba555517769842f364738a7961ee91151552c3b5aebccc9b0`
- macOS Fish artifact `8836553214`, digest `sha256:23a08fed67b9edc573122025f6057560b68872e9cb580dd9ea316468ab755615`

## What passed

- exact generation and four-file publication fences;
- formatting and affected-crate compilation;
- wheel generated-shebang test;
- four-form current/legacy `python` and `python3` migration test;
- existing relocatable-venv integration test;
- full locked workspace/all-target/all-feature clippy with warnings denied;
- GNU and Alpine 3.22 / BusyBox 1.37 launcher matrices;
- GNU, Alpine/BusyBox, and macOS Bash activation/platform probes;
- GNU, Alpine/BusyBox, and macOS sourced Fish activation matrices;
- Linux direct-shebang `$0` discriminator;
- exact source publication and branch relationship checks.

The baseline BusyBox launchers and activation fragments completed while emitting the false `realpath: --:` diagnostic. The candidate completed with empty stderr. GNU and macOS remained clean. Spaces, relative paths, PATH lookup, `./-tool`/`./-activate`, and external symlinks were covered where applicable.

## Remaining evidence limits

- The complete repository test suite was not run. The affected crates, focused native tests, full workspace clippy, and platform matrices are green.
- Public overlap must be refreshed immediately before any human-owned upstream action.
- Astral contribution and AI-policy compliance, final wording, and the decision to contact upstream remain human gates.

No known source defect or failed required focused gate remains.

## Human review sequence

1. Read exact source commit `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8` as one four-file diff.
2. Confirm the scope rule: remove only `realpath --`; retain `dirname --` and legacy recognition.
3. Check the test addition in `project/run.rs` and the existing virtualenv expectations.
4. Review the terminal Linux, macOS, and Fish receipts above.
5. Refresh upstream issue/PR/assignment state.
6. Decide whether to prepare a human-authored public pull request and explicitly authorize that exact action.

Until that decision, preserve the clean branch and receipts and do not contact upstream.

No public issue comment, pull request, review, reaction, email, or other upstream action occurred.
