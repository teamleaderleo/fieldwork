# B20260730-001 status

Batch issue: #88

State: `ready-for-synthesis`

Coordinator-owned file. Workers must not edit this file directly.

`complete` means the bounded research result is complete. It does not mean package execution or source integration is complete.

| Assignment | Role | State | Workers SDK branch / PR | Fieldwork result | Review |
| --- | --- | --- | --- | --- | --- |
| A001 | Teardown lifecycle ownership | complete | `fieldwork/teardown-lifecycle-hardening` / fork PR #1 | `results/A001.md` via Fieldwork PR #98 | Mechanism accepted; workerd-specific kill assertion retained; adjacent Vite findings extracted to #165 and #179; package execution and test-stack split remain |
| A002 | Configuration selection contract | complete | `fieldwork/config-selection-contract` / fork PR #2 | `results/A002.md` | Matrix tightened for nearer JSONC/TOML and relative explicit paths; characterization accepted; execution remains |
| A003 | Partial deployment state | complete | `fieldwork/deploy-state-reporting` / fork PR #3 | `results/A003.md` | Activation-path matrix corrected; reporting-failure flaw fixed and modeled; package execution remains |
| A004 | Independent review and prior art | withdrawn | none | `results/A004.md` | Duties redistributed at user direction |

## Reviewed Workers SDK heads

- A001 and logical-owner artifacts: `fa39841a98d71edd2df7561beb877f4dacbc6b7c`
- Candidate #165 container artifacts: `c7dd4411bf474a09f87cd1575594e7aaa8e1cacd`
- A002: `82ffab5d51abf7b5311891f31c6aa77f42bec41f`
- A003: `bc0dc5b064f3f4fd684b9ca8afa0b34de8489376`

## Shared boundaries

- Upstream contact authorized: `false`
- Upstream contact performed: `false`
- Live hosted deployment authorized: `false`
- Shared-file edits by workers: `false`
- Current active implementation workers: `0`
- Maximum useful parallelism if execution resumes: `2`

## Acceptance queue

### A001

Mechanism accepted. Before source integration:

- execute the first three Miniflare lifecycle tests before and after the runtime-first patch;
- preserve the workerd-specific child assertion;
- separate child ownership from the fourth error-aggregation test;
- prove no child process, worker thread, dispatcher, or unhandled rejection remains.

### A002

Protocol direction accepted. Before behavior changes:

- execute the six-layout Vite package matrix on Windows and POSIX;
- verify the selected path is parsed, watched, and reported in a complete plugin flow;
- centralize current outcomes behind named profiles;
- add a stable selection trace or `config explain` surface;
- do not align defaults until ambiguous layouts and migration cost are understood.

### A003

Guarded state-reporting direction accepted. Before source integration:

- execute deploy-helper package tests, including the report-throws regression;
- inject legacy-upload/container failure;
- inject versions-deployment/trigger failure;
- inject legacy-upload/trigger failure;
- review terminal and machine-readable output contracts;
- keep automatic rollback out of the first patch.

### Candidate #165 — Vite container cleanup ownership

Source-confirmed and model-executed. Before production edits:

- test two dev and two preview instances with distinct cleanup owners;
- test partial image-preparation failure;
- test programmatic preview close;
- test successful unregister without disturbing another owner;
- test cleanup failure, warning, retained ownership, and retry;
- test failed restart cleanup retaining old and new tags;
- preserve the original preparation or close error.

Durable note: `notes/vite-container-cleanup-ownership.md`.

### Candidate #179 — Vite logical runtime ownership

Source-confirmed and model-executed. The narrow restart-counter patch and async-scoped owner-handoff direction are prepared. Before production edits:

- test unrelated final close during another server's restart;
- test owner handoff across Vite 6, 7, and 8;
- test two concurrent servers with distinct Miniflare options and routing;
- test two concurrent tunnels with distinct origins, URLs, loggers, and host state;
- test concurrent restarts do not cross-claim owners;
- test failed replacement construction preserves the old owner and exact error;
- test a stale old generation cannot dispose the replacement;
- test final close removes only the intended owner record.

Durable note: `notes/vite-shared-context-ownership.md`.

## Validation

Executed dependency-free models:

- A001 teardown ownership and bounded cleanup;
- A002 predecessor discovery and redirect probes;
- A003 post-activation receipt and reporting-failure guard;
- #165 early cleanup ownership, exit registry, and restart tag retention;
- #179 global shared-state failure, owner isolation, sequential restart continuity, concurrent async handoff, and failed replacement construction.

Prepared but unexecuted:

- Miniflare package lifecycle tests;
- Vite configuration-selection package matrix;
- deploy-helper package tests and mocked integration paths;
- Vite container-cleanup plugin tests;
- Vite logical-owner and multi-server tests across Vite 6/7/8.

No owned-fork Actions runs appeared for the reviewed Workers SDK heads at the last check.

## Coordination placement

- #88 is the canonical batch review and disposition hub.
- #165 is the canonical Vite container-cleanup candidate.
- #179 is the canonical Vite logical-runtime candidate.
- #112 is the durable synthesis and notes PR.
- #87 owns generated coordination and stale-state validation.

The existing labels are sufficient for generated filtering; no extra ad hoc candidate label is required.

## Synthesis

`synthesis.md` is ready for programme-level review after the review corrections, Vite candidate extraction, supported-version restart trace, and centralized visibility updates. The next implementation work requires a complete Workers SDK checkout with dependencies or an owned CI route capable of executing the package and multi-server tests.
