# Handoff — Unit 02: uv BusyBox `realpath` compatibility

Updated: `2026-08-03`

State: `TECHNICALLY GREEN — CLEAN SOURCE PUBLICATION PENDING`

External contact: `unauthorized; none occurred`

## Canonical locations

- Routing issue: `teamleaderleo/fieldwork#435`, unit 02
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Fork: `teamleaderleo/uv`
- Execution PR: `teamleaderleo/uv#7`
- Supplemental Fish PR: `teamleaderleo/uv#18`
- Intended clean branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Existing public issue: `astral-sh/uv#16209`

## Exact technical result

The active correction is a four-file candidate on public base `79bbface771210df216b738e9bdc7df95e5a9e6b`.

It removes only unsupported `realpath --` delimiters, retains all `dirname --` delimiters, preserves `realpath` canonicalization introduced for externally symlinked launchers, recognizes corrected and historical `python`/`python3` generated shebangs, and updates uv's existing relocatable-venv assertions.

Exact patch fence:

```text
2   2  crates/uv-install-wheel/src/wheel.rs
4   4  crates/uv-virtualenv/src/virtualenv.rs
81  7  crates/uv/src/commands/project/run.rs
2   2  crates/uv/tests/python/venv.rs
```

Candidate blobs:

```text
49c04343714990cfbc8bf891162b4889678b08f5  wheel.rs
b251b09b63771e6833b872ef05003e5290501bd3  virtualenv.rs
91bfe0517944f19aa3ac79f6788619131cd07949  run.rs
f68dc858066242be1888b922262d53e22975856a  venv.rs
```

## Exact evidence

Successful Linux workflow:

- carrier: `c8a5c36d60a5cc35f496f583146967e210f87810`;
- run: `30753911776`;
- job: `91512671857`;
- artifact: `8835628919`;
- artifact ZIP SHA-256: `1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`.

Passed:

- formatting;
- affected-crate compilation;
- wheel shebang unit test;
- four-form migration unit test;
- existing relocatable-venv integration test;
- full declared workspace clippy with warnings denied;
- GNU and Alpine BusyBox launcher matrices;
- GNU and Alpine BusyBox sourced-Bash activation matrices;
- direct generated-shebang `$0` discriminator.

Baseline BusyBox succeeds with false stderr. Candidate BusyBox succeeds with empty stderr. GNU remains clean. The downloaded artifact independently matches the four-file, 175-line candidate patch.

## Important review outcomes

- Preserve `realpath`: removing it would risk reopening external-symlink behavior fixed by historical upstream PR #8079.
- Preserve `dirname --`: it passes the concrete BusyBox matrix; broader delimiter removal is unsupported.
- Reject generation-host BusyBox detection: relocatable files can run elsewhere.
- Do not add a speculative option-like `$0` branch: direct shebang execution supplies the script pathname.
- Keep migration recognition exact: current/historical × `python`/`python3`. Do not guess versioned or alternate interpreter forms without a producer.
- No active equivalent upstream pull request was found.

## Stale branch warning

`teamleaderleo/uv:upstream/02-busybox-realpath` still points at superseded head `c42973ef0490c75df1c7e7f4e9a54d46c6bca059` when this handoff was written. It is not reviewable or submit-ready.

## In-flight internal jobs

- Source publisher rerun: workflow `30755813495`, job `91518761618`; queued at handoff time.
- Fish supplement: workflow `30755096609`, jobs `91515786243` and `91515786224`; queued at handoff time.

The publisher has already been restarted once after a concurrency cancellation. Do not create another source design or weaken the one-commit publication fence because of runner queueing.

## First incomplete step

Publish the exact validated four-file tree as one source-only commit whose sole parent is `79bbface771210df216b738e9bdc7df95e5a9e6b`, then force the controlled clean branch from its superseded internal head to that new commit.

After publication:

1. record source commit, tree, one-ahead/zero-behind relation, four changed paths, and final blob identities;
2. update README, TESTS, DEEP_DIVE, REVIEW, and this handoff to the final human-review state;
3. record Fish results if terminal;
4. update the existing unit 02 checkpoint in issue #435 rather than posting duplicate progress comments;
5. close execution-only carriers after unique evidence transfer if repository tooling permits;
6. stop at the public-action boundary unless explicit unit-specific authorization is given.

## Safe stop state

If hosted publication remains unavailable, preserve the exact artifact and this packet. The technical candidate is green; the clean-branch commit identity is the missing mechanical receipt. No public contact is authorized.