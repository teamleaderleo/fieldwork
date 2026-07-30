# B20260730-001 status

Batch issue: #88

State: `ready-for-synthesis`

Coordinator-owned file. Workers must not edit this file directly.

`complete` means the bounded research result is complete. It does not mean package execution or source integration is complete.

| Assignment | Role | State | Workers SDK branch / PR | Fieldwork result | Review |
| --- | --- | --- | --- | --- | --- |
| A001 | Teardown lifecycle ownership | complete | `fieldwork/teardown-lifecycle-hardening` / fork PR #1 | `results/A001.md` via Fieldwork PR #98 | Mechanism accepted; Vite findings extracted to #165, #179, and #183; package execution and test-stack split remain |
| A002 | Configuration selection contract | complete | `fieldwork/config-selection-contract` / fork PR #2 | `results/A002.md` | Characterization tightened and accepted; execution remains |
| A003 | Partial deployment state | complete | `fieldwork/deploy-state-reporting` / fork PR #3 | `results/A003.md` | Reporting-failure flaw fixed and modeled; package execution remains |
| A004 | Independent review and prior art | withdrawn | none | `results/A004.md` | Duties redistributed at user direction |

## Exact evidence heads

- A001 core and earlier logical-owner artifacts: `fa39841a98d71edd2df7561beb877f4dacbc6b7c`
- #165 container cleanup: `c7dd4411bf474a09f87cd1575594e7aaa8e1cacd`
- #179 logical runtime/tunnel: `de3ed9fbf45a04cf2201a5571ade9afbe081a987`
- #183 build operation scope: `26556bcf7cda31009039b3aaf1527a8e4649e37f`
- A002: `82ffab5d51abf7b5311891f31c6aa77f42bec41f`
- A003: `bc0dc5b064f3f4fd684b9ca8afa0b34de8489376`

## Acceptance queue

### A001

- execute the first three Miniflare tests before and after the runtime-first patch;
- preserve workerd-specific child identity;
- prove no leaked child, worker thread, dispatcher, or unhandled rejection;
- review initialization-plus-cleanup aggregation separately.

### A002

- execute the six-layout matrix on Windows and POSIX;
- verify selected, parsed, watched, and reported paths;
- centralize current outcomes before considering default migration.

### A003

- execute helper tests including the throwing-reporter regression;
- inject legacy/container, versions/trigger, and legacy/trigger failure;
- accept terminal and machine-readable receipt contracts;
- keep automatic rollback out of the first patch.

### #165 — Vite container cleanup ownership

- test multiple dev/preview instances;
- test partial preparation failure and exact-error preservation;
- test preview programmatic close;
- test cleanup failure, warning, retained ownership, and retry;
- test failed restart cleanup retaining old and new tags.

Durable note: `notes/vite-container-cleanup-ownership.md`.

### #179 — Vite logical runtime/tunnel ownership

- execute the narrow restart-counter regression;
- execute owner handoff on Vite 6, 7, and 8;
- prove concurrent Miniflare and tunnel isolation;
- prove a later server does not reuse an earlier server's tunnel logger;
- prove concurrent restarts do not cross-claim owners;
- prove failed replacement and stale generations retain exactly one cleanup owner.

Durable note: `notes/vite-shared-context-ownership.md`.

### #183 — Vite build operation scope

- execute programmatic build followed by independent preview without manual env deletion;
- execute failed-build and concurrent-preview controls;
- prove nested build preview selects prerender while independent preview selects entry;
- prove process environment is unchanged;
- characterize a child preview created during `configResolved()` on Vite 6, 7, and 8.

Durable note: `notes/vite-build-marker-scope.md`.

## Validation

Executed dependency-free models:

- A001 teardown ownership and bounded cleanup;
- A002 predecessor discovery and redirect probes;
- A003 post-activation receipt and reporting guard;
- #165 container ownership, exit registry, and restart tag retention;
- #179 shared runtime, restart handoff, and tunnel manager lifetime;
- #183 sticky build marker and scoped operation state.

Prepared but unexecuted:

- Miniflare package lifecycle tests;
- Vite configuration-selection package matrix;
- deploy-helper package and mocked integration tests;
- Vite container-cleanup plugin tests;
- Vite logical-owner/multi-server tests across Vite 6/7/8;
- Vite programmatic build/preview and configResolved child-preview tests across Vite 6/7/8.

## Coordination placement

- #88 is the canonical batch review hub.
- #165 is the container-cleanup candidate.
- #179 is the logical runtime/tunnel candidate.
- #183 is the build-operation scope candidate.
- #112 retains synthesis and durable notes.
- #87 owns generated coordination and stale-state validation.
- PR #105 is a dated projection, not canonical live state.

No live deployment, tunnel, Docker reproduction, browser multi-server run, or upstream interaction occurred.
