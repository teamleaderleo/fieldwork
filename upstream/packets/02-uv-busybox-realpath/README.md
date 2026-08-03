# Unit 02 — uv BusyBox `realpath` compatibility

## Disposition

`READY FOR HUMAN REVIEW`

A clean, source-only candidate removes only the unsupported `--` operand from generated `realpath` calls. It preserves every `dirname --`, retains symlink canonicalization, and keeps project-run compatible with persisted relocatable launchers generated before the change in both `python` and `python3` forms.

## Cross-repository ownership

This contribution appears in both internal repositories for different reasons:

- `teamleaderleo/linux-fieldwork#307` owns the original investigation, reproduction, and promotion evidence;
- `teamleaderleo/fieldwork#435`, unit 02, owns the finished source packet, clean branch, review guide, and human publication decision.

The Fieldwork packet is now canonical. Linux Fieldwork should point here rather than continue a second implementation lane.

## Exact identity

- Public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Clean source branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Current clean head: `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`
- Previous byte-identical publication: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Source tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Relationship: one commit ahead, zero behind the reviewed base
- Existing public issue: `astral-sh/uv#16209`
- Public upstream interaction authorized: `no`

The two commit identities contain the same source tree. The current clean branch contains one source commit and no workflow, harness, packet, receipt, dependency, or unrelated file.

## Source boundary

| File | Change |
| --- | --- |
| `crates/uv-install-wheel/src/wheel.rs` | Generate `realpath "$0"` while retaining `dirname --`; update the exact wheel assertion. |
| `crates/uv-virtualenv/src/virtualenv.rs` | Apply the same realpath-only correction to POSIX and Fish activation generation. |
| `crates/uv/src/commands/project/run.rs` | Recognize corrected and historical `python`/`python3` relocatable shebangs; test all four forms. |
| `crates/uv/tests/python/venv.rs` | Update uv's existing relocatable activation expectations. |

Diff: four files, 89 insertions, 15 deletions.

Source blobs:

```text
49c04343714990cfbc8bf891162b4889678b08f5  crates/uv-install-wheel/src/wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  crates/uv-virtualenv/src/virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  crates/uv/src/commands/project/run.rs
f68dc858066242be1888b922262d53e22975856a  crates/uv/tests/python/venv.rs
```

## Why this exact boundary

BusyBox `dirname` explicitly accepts an optional `--`. BusyBox `realpath` instead treats every argument as a pathname and reports `--` as missing. Removing both delimiters would fix the symptom, but would discard protection where BusyBox already supports it.

Generating different launchers based on the build host is also the wrong abstraction: a relocatable environment may be created on one system and executed on another. The unconditional realpath-only form is accepted by GNU, BusyBox, and macOS in the completed matrices.

Existing relocatable environments can contain either `/'python'` or `/'python3'`. Recognizing corrected and historical forms prevents an upgrade-time copy regression while keeping the accepted grammar deliberately narrow.

## Final evidence

Main exact-source carrier, run `30753911776`:

- Linux/source job `91621197004`: success
- macOS job `91621196098`: success
- publication job `91621231746`: success

Fish supplement, run `30755096609`:

- GNU and Alpine/BusyBox Fish job `91515786243`: success
- macOS Fish job `91515786224`: success

Passed gates:

- exact four-file generation and publication fences;
- `git diff --check` and `cargo fmt --all --check`;
- affected-crate compilation;
- wheel shebang test;
- four-form project-run migration test;
- existing relocatable-venv integration test;
- full locked workspace/all-target/all-feature clippy;
- GNU and Alpine 3.22 / BusyBox 1.37 launcher matrices;
- GNU, Alpine/BusyBox, and macOS Bash activation probes;
- GNU, Alpine/BusyBox, and macOS Fish activation matrices;
- Linux direct-shebang `$0` discriminator;
- exact source publication and branch relationship checks.

The baseline completed while emitting the false `realpath: --:` diagnostic on BusyBox. The candidate completed with empty stderr while preserving the selected interpreter/environment. GNU and macOS remained clean. Spaces, relative paths, PATH lookup, `./-tool`/`./-activate`, and external symlinks were covered where applicable.

## Limits

- The complete repository test suite was not run. Affected crates, focused native tests, full workspace clippy, and platform matrices are green.
- Upstream overlap and the exact public base must be refreshed immediately before any human-owned submission.
- Astral contribution and AI-policy compliance, final public wording, and the decision to contact upstream remain human gates.

## Recommendation

Advance this unit to a human last-mile review. It fixes an open, currently reproduced compatibility defect with a small source boundary, preserves the historical symlink behavior, covers all known text producers and the matching consumer, and has exact Linux, BusyBox, macOS, Bash, and Fish evidence.

No public upstream interaction occurred.