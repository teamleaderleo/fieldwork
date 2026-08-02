# Handoff — Unit 02: uv BusyBox `realpath` compatibility

Updated: `2026-08-03`

State: `READY FOR LAST-MILE LOOK`

External contact: `unauthorized; none occurred`

## Canonical locations

- Routing issue: `teamleaderleo/fieldwork#435`, unit 02
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Fork: `teamleaderleo/uv`
- Clean branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Execution PR: `teamleaderleo/uv#7`
- Supplemental Fish PR: `teamleaderleo/uv#18`
- Existing public issue: `astral-sh/uv#16209`

## Exact clean source

- Base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Head: `047b724212905c034c15d4f4f6f9ef330bbd2daf`
- Tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`
- Relationship: one commit ahead, zero behind
- Diff: four files, 89 insertions, 15 deletions

```text
49c04343714990cfbc8bf891162b4889678b08f5  crates/uv-install-wheel/src/wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  crates/uv-virtualenv/src/virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  crates/uv/src/commands/project/run.rs
f68dc858066242be1888b922262d53e22975856a  crates/uv/tests/python/venv.rs
```

The source commit contains no workflow, harness, packet, dependency, lockfile, or unrelated file.

## Selected behavior

The correction removes only unsupported `realpath --` delimiters. It retains all `dirname --` delimiters, preserves `realpath` canonicalization for externally symlinked entrypoints, recognizes corrected and historical `python`/`python3` relocatable launchers, and updates the existing uv generated-text expectations.

Review boundaries:

- do not remove `realpath`; historical upstream PR #8079 established its symlink semantics;
- do not remove supported `dirname --` without new evidence;
- do not branch on generator-host BusyBox detection for a relocatable artifact;
- do not add speculative option-like `$0` normalization; direct shebang execution supplies the script path;
- do not broaden the exact migration parser beyond observed `python` and `python3` producers without a failing generated example.

No active equivalent upstream pull request was found.

## Exact validation evidence

Validation:

- carrier: `c8a5c36d60a5cc35f496f583146967e210f87810`;
- run/job: `30753911776` / `91512671857` — success;
- artifact: `8835628919`;
- digest: `sha256:1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`.

Publication:

- carrier: `76836268a70c0a9ba49035a5e3eab4477044ed10`;
- run/job: `30756408587` / `91519210841` — success;
- artifact: `8836056361`;
- digest: `sha256:e0684ec5da7025a7b7cf4a8f7b932e06c3385d07e2146a5e8d5a8c344a2ed634`.

Passed:

- exact generation and four-file publication fences;
- formatting and affected-crate compilation;
- wheel generated-shebang test;
- four-form migration test;
- existing relocatable-venv integration test;
- full locked workspace/all-target/all-feature clippy with warnings denied;
- GNU and Alpine 3.22 BusyBox launcher matrices;
- GNU and Alpine sourced-Bash activation matrices;
- Linux direct-shebang `$0` discriminator.

The baseline BusyBox launchers and activation fragments completed while emitting the false `realpath: --:` diagnostic. The candidate completed with empty stderr. GNU remained clean.

## Evidence limits

- The exact final source did not obtain a terminal macOS run before the carrier advanced. Earlier macOS 15 evidence passed the broader delimiter-free form; this is supporting, not exact-final, evidence.
- The executable Fish supplement in `teamleaderleo/uv#18` remained queued. The exact target-native Fish generated-text assertion passed.
- The complete repository suite was not run.

These are human gate choices, not known technical defects.

## First incomplete step

A human reads the exact four-file diff and decides whether the completed gates are sufficient for public preparation. If yes, independently author the public pull-request text and explicitly authorize the specific action.

Until then:

- preserve the clean branch and exact receipts;
- record any terminal Fish result if it reverses the conclusion;
- avoid new implementation or speculative widening;
- do not contact upstream.

No public issue comment, pull request, review, reaction, email, or other upstream action occurred.