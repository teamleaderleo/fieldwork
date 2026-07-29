# B20260730-001 status

Batch issue: #88

State: `ready-for-synthesis`

Coordinator-owned file. Workers must not edit this file directly.

`complete` below means the bounded research result is complete. It does not mean package execution or source integration is complete.

| Assignment | Role | State | Workers SDK branch / PR | Fieldwork result | Review |
| --- | --- | --- | --- | --- | --- |
| A001 | Teardown lifecycle ownership | complete | `fieldwork/teardown-lifecycle-hardening` / fork PR #1 | `results/A001.md` via Fieldwork PR #98 | Mechanism accepted; kill assertions bind to workerd; adjacent Vite cleanup ownership moved to candidate #165; execution and test-stack split remain |
| A002 | Configuration selection contract | complete | `fieldwork/config-selection-contract` / fork PR #2 | `results/A002.md` | Matrix tightened for nearer JSONC/TOML and relative explicit paths; formal characterization review recorded; execution remains |
| A003 | Partial deployment state | complete | `fieldwork/deploy-state-reporting` / fork PR #3 | `results/A003.md` | Activation-path matrix corrected; reporting-failure flaw fixed and modeled; formal review recorded; package execution remains |
| A004 | Independent review and prior art | withdrawn | none | `results/A004.md` | Duties redistributed at user direction |

## Reviewed Workers SDK heads

- A001 and adjacent Vite artifacts: `3d67e4cf38fe270a8d871056536b0e36d9a80893`
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
- verify the selected path is also parsed, watched, and reported in a complete plugin flow;
- centralize current outcomes behind named `wrangler-cli`, `wrangler-dev`, and `vite-root` profiles;
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

Source-confirmed and model-executed; separate from the first A001 patch. Before production edits:

- test two same-mode dev instances and two same-mode preview instances;
- test partial image-preparation failure after earlier image work;
- test programmatic preview close;
- test successful unregister without disturbing another owner;
- test cleanup returning `false`, warning, retained ownership, and later retry;
- preserve the original preparation or close error;
- keep the patch separate from Miniflare child-ownership work.

Durable note: `notes/vite-container-cleanup-ownership.md`.

Canonical candidate: #165.

## Validation

Executed dependency-free models:

- A001 teardown ownership and bounded cleanup;
- A002 predecessor discovery and redirect probes;
- A003 refreshed post-activation receipt and reporting-failure model;
- Vite early container cleanup ownership;
- Vite single-slot exit negative control and per-instance cleanup registry.

Prepared but unexecuted:

- Miniflare package lifecycle tests;
- Vite configuration-selection package matrix;
- deploy-helper package tests and mocked integration paths;
- Vite dev/preview container cleanup plugin tests.

No owned-fork Actions runs appeared for the reviewed Workers SDK heads at the last check.

## Coordination placement

- #88 is the canonical batch review and disposition hub.
- #165 is the canonical Vite cleanup candidate.
- #112 is the durable synthesis and notes PR.
- #87 owns the generated board and stale-state validation convention.

The existing labels are sufficient for generated filtering; no extra ad hoc candidate label is required.

## Synthesis

`synthesis.md` is ready for programme-level review after the adversarial test corrections, A003 reporting fix, Vite cleanup candidate extraction, and centralized visibility updates. The next useful implementation work requires a complete Workers SDK checkout with dependencies or an owned CI route capable of executing the package tests.
