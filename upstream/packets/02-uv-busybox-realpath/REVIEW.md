# Review — Unit 02: uv BusyBox `realpath` compatibility

## Current disposition

`TECHNICALLY GREEN — DO NOT REVIEW STALE SOURCE BRANCH`

The four-file candidate is validated. The canonical source branch still points at superseded head `c42973ef0490c75df1c7e7f4e9a54d46c6bca059`; that branch is not the review subject until the exact candidate is republished.

## Validated subject

- Target: `astral-sh/uv`, existing issue `#16209`
- Exact base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Validated carrier: `c8a5c36d60a5cc35f496f583146967e210f87810`
- Run/job: `30753911776` / `91512671857`
- Artifact: `8835628919`
- Artifact ZIP SHA-256: `1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`
- Publication rerun: `30755813495`, job `91518761618`
- Public authority: none

## Exact source fence

- [x] four changed paths only;
- [x] no workflow or Fieldwork files in candidate patch;
- [x] five source `realpath --` delimiters removed;
- [x] two target-native expectations updated;
- [x] two historical forms retained only in migration constants;
- [x] all `dirname --` delimiters retained;
- [x] candidate patch independently downloaded and inspected;
- [ ] exact candidate tree published as one commit on the base;
- [ ] final commit/tree identities recorded.

Candidate blobs:

```text
49c04343714990cfbc8bf891162b4889678b08f5  crates/uv-install-wheel/src/wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  crates/uv-virtualenv/src/virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  crates/uv/src/commands/project/run.rs
f68dc858066242be1888b922262d53e22975856a  crates/uv/tests/python/venv.rs
```

## Technical checklist

- [x] `git diff --check` through the exact workflow;
- [x] `cargo fmt --all --check`;
- [x] affected-crate `cargo check`;
- [x] wheel generated-shebang test;
- [x] four-form `copy_entrypoint` migration test;
- [x] existing relocatable-venv integration test;
- [x] full declared workspace clippy with warnings denied;
- [x] GNU launcher matrix;
- [x] Alpine 3.22 BusyBox launcher matrix;
- [x] GNU sourced-Bash activation matrix;
- [x] Alpine BusyBox sourced-Bash activation matrix;
- [x] direct shebang `$0` discriminator;
- [ ] supplemental executable Fish jobs terminal;
- [ ] optional exact-carrier macOS job;
- [ ] optional full repository suite.

The unchecked supplemental items are not evidence of a source defect. Fish generated text already passes uv's target-native integration test. They remain useful confidence and must be recorded if they reverse the current conclusion.

## Decisions for human review after publication

1. Keep all four exact migration forms in the same patch.
2. Accept the private-function migration test or request an integration-level equivalent.
3. Accept the bounded four-file source boundary rather than introducing cross-crate centralization.
4. Decide whether supplemental macOS/Fish or a full suite is required before public submission.
5. Author the public pull-request text independently.

## Review warning

Do not approve source by reading `upstream/02-busybox-realpath` until its head is replaced and the compare shows one commit ahead, zero behind, and exactly the four candidate paths above.

No public upstream action occurred.