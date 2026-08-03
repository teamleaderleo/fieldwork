# Handoff — Unit 02: uv BusyBox `realpath` compatibility

Updated: `2026-08-03`

State: `READY FOR HUMAN REVIEW`

External contact: `unauthorized; none occurred`

## Canonical ownership

- Routing issue: `teamleaderleo/fieldwork#435`, unit 02
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Decision brief: `PRESENTATION.md`
- Original investigation: `teamleaderleo/linux-fieldwork#307` — closed completed after promotion here
- Fork: `teamleaderleo/uv`
- Clean branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Main execution PR: `teamleaderleo/uv#7` — closed without merge after evidence transfer
- Supplemental Fish PR: `teamleaderleo/uv#18` — closed without merge after evidence transfer
- Existing public issue: `astral-sh/uv#16209`

Linux Fieldwork retains the investigation provenance. This Fieldwork packet is the sole finished proposal owner.

## Exact clean source

- Public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Current clean head: `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`
- Previous byte-identical publication: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Source tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Relationship: one commit ahead, zero behind
- Diff: four files, 89 insertions, 15 deletions

The rerun republished the same validated tree with a new commit identity. Changed-file blob hashes:

```text
49c04343714990cfbc8bf891162b4889678b08f5  crates/uv-install-wheel/src/wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  crates/uv-virtualenv/src/virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  crates/uv/src/commands/project/run.rs
f68dc858066242be1888b922262d53e22975856a  crates/uv/tests/python/venv.rs
```

The source commit contains no workflow, harness, packet, dependency, lockfile, or unrelated file.

## Selected behavior

The correction removes only unsupported `realpath --` delimiters. It retains every `dirname --`, preserves `realpath` canonicalization for externally symlinked entrypoints, recognizes corrected and historical `python`/`python3` relocatable launchers, and updates uv's existing generated-text expectations.

Review boundaries:

- do not remove `realpath`; historical upstream work established its symlink semantics;
- do not remove supported `dirname --` without new evidence;
- do not branch on generator-host BusyBox detection for a relocatable artifact;
- do not add speculative option-like `$0` normalization without a supported failing invocation;
- do not broaden the migration parser beyond observed `python` and `python3` producers without a generated example.

No active equivalent upstream pull request was found during the latest review. The public issue remains open and has a recent reproduction report.

## Terminal evidence

### Main exact-source carrier

Run `30753911776`, latest attempt:

- Linux/source job `91621197004`: success
- macOS job `91621196098`: success
- publication job `91621231746`: success

Artifacts:

- Linux `8835628919`, digest `sha256:1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`
- macOS `8847852798`, digest `sha256:5053067966a50e9bcf842a9433f9509b89d49e0d202e492884e5ced8f203646b`
- publication `8847875671`, digest `sha256:0c7f3655f2ec681db1d3d2caf4ab1c6a7de29b3657898cb13d96a75b9d849b9d`

### Fish activation supplement

Run `30755096609`:

- GNU and Alpine/BusyBox Fish job `91515786243`: success
- macOS Fish job `91515786224`: success

Artifacts:

- Linux Fish `8836836696`, digest `sha256:cf515d657784f09ba555517769842f364738a7961ee91151552c3b5aebccc9b0`
- macOS Fish `8836553214`, digest `sha256:23a08fed67b9edc573122025f6057560b68872e9cb580dd9ea316468ab755615`

## What passed

- exact generation and four-file publication fences;
- formatting and affected-crate compilation;
- wheel generated-shebang test;
- four-form current/legacy `python` and `python3` migration test;
- existing relocatable-venv integration test;
- full locked workspace/all-target/all-feature clippy with warnings denied;
- GNU and Alpine 3.22 / BusyBox 1.37 launcher matrices;
- GNU, Alpine/BusyBox, and macOS Bash activation probes;
- GNU, Alpine/BusyBox, and macOS Fish activation matrices;
- Linux direct-shebang `$0` discriminator;
- exact source publication and branch relationship checks.

The baseline BusyBox launchers and activation fragments completed while emitting the false diagnostic. The candidate completed with empty stderr. GNU and macOS remained clean. Spaces, relative paths, PATH lookup, leading-hyphen path forms, and external symlinks were covered where applicable.

## Remaining limits

- The complete repository test suite was not run. Affected crates, focused native tests, full workspace clippy, and platform matrices are green.
- Public overlap and current-main applicability must be refreshed immediately before a human-owned submission.
- Astral contribution and AI-policy compliance, public wording, and the decision to contact upstream remain human gates.

No known source defect or failed required focused gate remains.

## Human review sequence

1. Read `PRESENTATION.md` for the decision case and objections.
2. Read exact source commit `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8` as one four-file diff.
3. Confirm the scope rule: remove only `realpath --`; retain `dirname --`, canonicalization, and legacy recognition.
4. Check the project-run migration test and existing virtualenv expectations.
5. Review the terminal Linux, BusyBox, macOS, Bash, and Fish receipts.
6. Refresh upstream issue/PR/assignment and current-main source state.
7. Verify contribution-policy compliance and decide whether to prepare a human-authored public pull request.
8. Explicitly authorize any public action.

Until that decision, preserve the clean branch and receipts and do not contact upstream.

No public issue comment, pull request, review, reaction, email, or other upstream action occurred.