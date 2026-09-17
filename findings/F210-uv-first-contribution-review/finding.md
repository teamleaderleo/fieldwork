# uv first-contribution review — final handoff

Updated: `2026-08-04`

## Decision

`UNIT 02 READY FOR HUMAN REVIEW / LOCK DIAGNOSTIC HELD FOR REPAIR`

The selected first-contribution candidate is the Alpine/BusyBox relocatable-launcher repair. Its exact source, focused native tests, full locked clippy gate, GNU/BusyBox/macOS platform probes, Fish activation supplement, and clean source publication are terminal and green.

The separate lockfile-as-requirements diagnostic is not review-ready. Its current source has a valid-requirements filename collision, and both follow-up execution carriers failed before product tests.

No public upstream interaction occurred or is authorized.

## Assignment and authority

- Coordination: `teamleaderleo/fieldwork#210`.
- Upstream packet routing: `teamleaderleo/fieldwork#435`, unit 02.
- Canonical packet: `upstream/packets/02-uv-busybox-realpath/`.
- Packet branch/head: `upstream/02-uv-busybox-realpath-packet@85748635b05fee2ffe78c1b317d0acbf5e2d984f`.
- Public target observed quietly: `astral-sh/uv`.
- Public upstream contact authorized/performed: `false` / `false`.

# Selected lane — Unit 02 BusyBox `realpath` compatibility

## Exact source

- Public base: `79bbface771210df216b738e9bdc7df95e5a9e6b`.
- Clean owned branch: `teamleaderleo/uv:upstream/02-busybox-realpath`.
- Current source head: `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`.
- Previous byte-identical publication: `047b724212905c034c15d4f4f6f9ef330bbd2daf`.
- Source tree: `e0832686bd982b5c15f6e9bdd6d6631d30ec24cf`.
- Relationship at the recorded generation: one commit ahead, zero behind.
- Diff: four files, 89 insertions, 15 deletions.

Changed files exactly:

- `crates/uv-install-wheel/src/wheel.rs`
- `crates/uv-virtualenv/src/virtualenv.rs`
- `crates/uv/src/commands/project/run.rs`
- `crates/uv/tests/python/venv.rs`

The rerun republished the same validated tree with a new commit identity. The four changed-file blob hashes match the prior publication.

## Selected behavior

The source:

- removes only unsupported `realpath --` delimiters;
- retains every supported `dirname --` delimiter;
- preserves `realpath` symlink canonicalization;
- recognizes corrected and historical relocatable launchers for both `python` and `python3`;
- updates existing generated-text expectations;
- adds a native migration test covering all four current/legacy launcher forms and executable-mode preservation.

Rejected directions remain:

- removing `realpath`, which would weaken external-symlink behavior;
- removing supported `dirname --` delimiters;
- generator-host BusyBox detection, which would make artifacts depend on their build host;
- speculative option-like `$0` handling without a failing direct-shebang case;
- widening recognition beyond the observed `python` and `python3` producers.

## Terminal execution

Main run `30753911776`, latest attempt:

- Linux/source job `91621197004`: success;
- macOS job `91621196098`: success;
- publication job `91621231746`: success.

Main artifacts:

- Linux `8835628919`, digest `sha256:1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`;
- macOS `8847852798`, digest `sha256:5053067966a50e9bcf842a9433f9509b89d49e0d202e492884e5ced8f203646b`;
- publication `8847875671`, digest `sha256:0c7f3655f2ec681db1d3d2caf4ab1c6a7de29b3657898cb13d96a75b9d849b9d`.

Independent earlier publication:

- run/job `30756408587` / `91519210841`: success;
- artifact `8836056361`;
- digest `sha256:e0684ec5da7025a7b7cf4a8f7b932e06c3385d07e2146a5e8d5a8c344a2ed634`.

Fish supplement run `30755096609`:

- GNU and Alpine/BusyBox Fish job `91515786243`: success;
- macOS Fish job `91515786224`: success;
- Linux Fish artifact `8836836696`, digest `sha256:cf515d657784f09ba555517769842f364738a7961ee91151552c3b5aebccc9b0`;
- macOS Fish artifact `8836553214`, digest `sha256:23a08fed67b9edc573122025f6057560b68872e9cb580dd9ea316468ab755615`.

Execution-only PRs `teamleaderleo/uv#7` and `#18` were closed without merge after evidence transfer.

## Green gates

- exact generation and four-file publication fences;
- formatting and affected-crate compilation;
- wheel generated-shebang test;
- current/legacy `python` and `python3` migration test;
- existing relocatable-venv integration test;
- full `cargo clippy --locked --workspace --all-targets --all-features -- -D warnings`;
- GNU and Alpine 3.22 / BusyBox 1.37 launcher matrices;
- GNU, Alpine/BusyBox, and macOS Bash/platform probes;
- GNU, Alpine/BusyBox, and macOS sourced Fish activation matrices;
- direct shebang `$0` discriminator;
- exact source publication and branch relationship checks.

Baseline BusyBox forms emitted the known false `realpath: --:` diagnostic while still completing. Candidate forms completed with empty stderr. GNU and macOS remained clean. Relative paths, PATH lookup, spaces, leading-hyphen names through `./-tool` or `./-activate`, and external symlinks were covered where applicable.

## Evidence limits and human gates

- The complete repository test suite was not run. Affected crates, focused native tests, full workspace clippy, and platform matrices are green.
- Public issue, pull-request, assignment, and contributor-intent state must be refreshed immediately before upstream action.
- Astral contribution and AI-policy compliance, final wording, and the decision to contact upstream remain human-owned.

No known source defect or failed required focused gate remains.

## Unit 02 disposition

`READY FOR HUMAN REVIEW`

Read `upstream/packets/02-uv-busybox-realpath/HANDOFF.md`, then inspect exact commit `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8` as one four-file diff. No more implementation work is recommended before human review.

# Held lane — `uv.lock` passed to `-r`

## Current source

- Source PR: `teamleaderleo/uv#12`.
- Exact source head: `ba55497fe83ea9bb07c04452f8ba190fa4440a05`.
- Public issue: `astral-sh/uv#16192`.

The source attempted to identify uv-generated project and PEP 723 lockfile names without content sniffing and added producer-backed positive tests plus non-UTF-8 filename handling.

## Blocking design collision

Detection runs before requirements parsing. A valid requirements file named `action.py.lock` is rejected whenever a neighboring `action.py` contains valid PEP 723 metadata. The existing arbitrary-`.lock` control did not include this same-name PEP 723 collision.

The earlier source acceptance is superseded.

Current disposition: `HOLD / REPAIR`.

## Execution results

Clean current-source carrier `teamleaderleo/uv#15`:

- run `30754710006`, job `91514796254`: failure before tests;
- source identity and three-file fence passed;
- `cargo fmt --all --check` found formatting changes in the new test file;
- compile and focused tests were skipped.

Parse-failure experiment `teamleaderleo/uv#13`:

- run `30755038821`, job `91515650405`: failure before tests;
- runner patch expected one source snippet but found zero matches;
- fallback formatting lacked the installed rustfmt component;
- no product behavior was executed.

The public lane is crowded with prior and current attempts. Do not include this work in the first-contribution packet.

## Lock-lane disposition

`HOLD / REPAIR / INTERNAL ONLY`

A future pass must first design parse-failure-only diagnostics that preserve valid same-name requirements files, then repair the exact transformation and run formatting, compilation, and focused tests. Public routing remains held regardless.

# EnvironmentOptions screen

The adjacent `environment-options-screen.md` remains a codebase map. Most easy-looking variables have prior attempts. Apparently unoccupied variables cross leaf-crate identity, early thread initialization, or lower-level global-policy and error-semantics boundaries.

Disposition: `STOP AS FIRST-PATCH LANE / RETAIN AS CODEBASE MAP`.

# Human review checklist

1. Read the canonical Unit 02 packet handoff.
2. Inspect exact source head `17fb4489a71cc63a59b90ecc52b08f703ca0d0e8`.
3. Confirm the scope rule: remove only `realpath --`; retain `dirname --`, canonicalization, and legacy recognition.
4. Review the native migration test and existing virtualenv expectation changes.
5. Review the terminal Linux, macOS, and Fish receipts.
6. Refresh public overlap and repository contribution policy.
7. Decide whether to prepare and explicitly authorize a human-owned upstream pull request.

No public issue, pull request, comment, review, reaction, email, or maintainer message was created by this work.
