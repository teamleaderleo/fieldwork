# Codex portfolio live receipts at `97576b1794872e342450ebd577123e052ab57626`

Authority: this file supersedes carrier-head and live-run fields in `codex-portfolio-convergence-97576.md`. The larger dossier remains the portfolio analysis and proposal packet; this file owns changed-head receipts and final disposition.

Fieldwork command: #239  
Proposal owner: #260  
Dossier PR: #258  
Public upstream interaction authorized: `false`

## Complete-diff review of PR #258

The PR changes documentation only. The first commit added one 369-line dossier. Complete-diff review found one blocking freshness defect: the initial convergence table named carrier heads that moved during concurrent repairs.

The initial snapshot recorded:

- #52 at `ec78830e3d6f67454b56900427c683a2da7bc29b`;
- #53 at `600bba1f556d63a75f4fdecd6217c2bab9f458ec`;
- #55 at `0f50a5612a2b4d471de2be35512540222d6673b3`.

Those heads are historical phase receipts. The following exact heads now own execution:

- append acknowledgement #52: `2cf5f5aabb6f4d8f3e1120d9a621396f85d916df`;
- terminal retention #53: `0f2f56d3bb758649ade3fe8cdc1e8840da44af0a`;
- deferred discovery receipt #55: `f27b14dddbb0a24ee4eab17b59f76bf8dd26e6b0`.

No other blocking contradiction was found in the complete documentation diff. Proposal boundaries, historical receipts, source relations, cross-lane constraints, and retirement classes remain coherent.

## Deferred discovery

Source PR #54 remains exact current source:

```text
2b9fd0fc597965341a1a9c61559b67135ed0a49d
parent: 97576b1794872e342450ebd577123e052ab57626
files: codex-rs/core/src/tools/spec_plan.rs
       codex-rs/core/src/tools/spec_plan_tests.rs
```

Receipt carrier #55 first current run:

```text
run: 30580196749
job: 90998234427
source fence: passed
format: passed
planner exact controls: 4/4 passed
standalone-host fallback: default worker stack overflow, exit 101
```

The fallback test was:

```text
suite::code_mode::missing_process_host_falls_back_to_direct_tools_and_warns_once
```

Carrier #55 head `f27b14dddbb0a24ee4eab17b59f76bf8dd26e6b0` now runs the unchanged fallback control on the default stack and at `RUST_MIN_STACK=16777216`, requires the large-stack control to pass, requires a stack-overflow signature when the default execution fails, and emits:

```text
FIELDWORK_CODE_MODE_FALLBACK=default:<status>;large:<status>
```

Current run: `30580836079`, executing at this ledger revision.

## Append acknowledgement

Historical source #51 remains:

```text
30a0a9b50da5fd2f7d58ee81315e0311e84e221e
```

Carrier #52 head `2cf5f5aabb6f4d8f3e1120d9a621396f85d916df`:

- applies the reviewed three-file binary diff with `git apply --3way` onto exact upstream `97576b...`;
- lists current `codex-core` library tests;
- requires exactly one full-name match for each of four append-outcome suffixes;
- runs every resolved name with `--exact --nocapture`;
- runs the complete `codex-thread-store` package;
- verifies the three-file source fence;
- publishes `fieldwork/83-append-outcome-upstream-97576b`.

Current run: `30581101002`, queued at this ledger revision.

Earlier run `30560746088` / job `90932794178` failed during stale source transformation before tests and executed zero source controls. Later attempts were cancelled during setup as the carrier head advanced.

## Terminal retention

Historical source #49 remains:

```text
7db66fe3f235df77c36a9db521677e23379bcac5
```

Carrier #53 head `0f2f56d3bb758649ade3fe8cdc1e8840da44af0a` is based on exact branch `fieldwork/upstream-97576-base` at `97576b...`.

The authoritative workflow `fieldwork-terminal-97576-shallow`:

- checks out the exact carrier head;
- fetches only exact upstream and historical source refs;
- reconstructs the reviewed source with the two known conflict resolutions;
- preserves upstream `VecDeque` and invalid-UTF-8 progress behavior;
- removes test-only visibility widening;
- verifies the exact four-file source fence;
- resolves nine unique terminal/deque names and runs them with `--exact`;
- runs focused `codex-core`;
- publishes `fieldwork/23-terminal-97576-source`.

Current run: `30581285698`, queued at this ledger revision.

Historical phase receipts:

- run `30579629635` / job `90996353540`: failed during cherry-pick on the two expected conflicts; zero tests;
- run `30579942527` / job `90997384432`: conflict repair and exact four-file fence passed; execution stopped because `just` was absent.

## Retirement gate

Refresh every PR head immediately before closure.

- Close #45 and #55 only after the final #55 receipt transfers to #239, #260, and this ledger.
- Close #51 and #52 only after a published source-only head is independently compared with `97576b...` and its exact receipt transfers.
- Close #49 and #53 only after a published source-only head is independently compared with `97576b...` and its exact receipt transfers.
- Keep #46 and #48 open until exact-current source successors exist.
- Keep #23 and #32 as historical evidence until clean successor source heads absorb their remaining residue.

Execution carriers remain outside R2/R3 and Delivery Desk D0.

## Final handoff fields

For every completed or blocked lane, record:

1. public upstream head;
2. source branch and exact head;
3. source parent and complete file list;
4. carrier head, workflow run, and job;
5. exact test names and count;
6. focused package gate outcome;
7. publication outcome and source branch;
8. absorption/conflict classification;
9. retired carrier list;
10. public upstream interaction performed: `false`.
