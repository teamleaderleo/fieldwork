# Workers SDK lifecycle follow-up synthesis

State: `ready-for-synthesis`

Batch: `B20260730-001`

Issue: #88

Upstream contact authorized: `false`

Upstream contact performed: `false`

`complete` means a bounded research result is complete. It does not mean target package tests ran or production source is ready.

## In simple words

The batch produced three core Workers SDK candidates and two extracted Cloudflare Vite-plugin candidates:

1. Miniflare can delay or skip terminating `workerd` when earlier cleanup fails or never settles.
2. Wrangler and Vite can choose different configuration files from the same project tree.
3. Wrangler can activate Worker code and then fail later without clearly reporting the activation path, activated version, and failed phase.
4. Vite container cleanup can lose ownership across partial preparation, multiple same-mode instances, programmatic preview close, and failed restart cleanup.
5. Vite process-global runtime and tunnel state can conflate unrelated servers, while sequential restart generations still need an explicit state handoff.

None of the target package/plugin suites executed in the available environment. The dependency-free models are evidence for control-flow and ownership contracts, not substitutes for full integration execution.

## Reviewed heads

| Candidate | Exact evidence head |
| --- | --- |
| A001 — teardown lifecycle | `fa39841a98d71edd2df7561beb877f4dacbc6b7c` |
| A002 — configuration selection | `82ffab5d51abf7b5311891f31c6aa77f42bec41f` |
| A003 — post-activation state | `bc0dc5b064f3f4fd684b9ca8afa0b34de8489376` |
| #165 — Vite container cleanup | `c7dd4411bf474a09f87cd1575594e7aaa8e1cacd` |
| #179 — Vite logical runtime ownership | `fa39841a98d71edd2df7561beb877f4dacbc6b7c` |

## A001 — teardown lifecycle ownership

Disposition: **accept mechanism; hold source integration for package execution and test-slice separation**

The current Miniflare cleanup sequence awaits browser and proxy cleanup before `Runtime.dispose()`. A rejection can skip runtime disposal; a pending promise can delay it indefinitely. `Runtime.dispose()` sends `SIGKILL` synchronously before returning its exit promise, so requesting runtime termination earlier is a bounded ownership fix.

The real-runtime package tests now count only `SIGKILL` calls made on the child whose executable basename starts with `workerd`. The first three tests cover:

- rejection before runtime disposal;
- deterministic pending cleanup before runtime disposal;
- a post-runtime rejection negative control.

The fourth test, preserving both initialization and cleanup failures, requires phased aggregation and remains a separate implementation slice.

Next gate:

- execute the first three tests before and after `runtime-first-dispose.patch`;
- prove no child, worker thread, dispatcher, or unhandled rejection remains;
- review primary-error aggregation separately.

## A002 — configuration selection contract

Disposition: **accept behavior-preserving protocol direction; hold default changes**

Workers Utils and the Vite plugin differ across:

- JSON/JSONC/TOML precedence;
- upward versus root-only search;
- deploy-config redirect enablement;
- explicit-path convergence.

The prepared six-layout matrix directly covers a farther parent JSON against nearer JSONC and nearer TOML, uses caller-neutral redirect language, and starts the explicit-path control from a Vite-relative path before the absolute Workers Utils handoff.

The predecessor discovery and redirect probes executed. The cross-package matrix remains unexecuted.

Recommended direction:

- centralize selection mechanics without changing outcomes;
- retain named caller profiles;
- expose a selection trace or `config explain` surface;
- warn on ambiguous layouts before considering a major-version default migration.

## A003 — post-activation deployment state

Disposition: **accept guarded state reporting; hold automatic rollback and integration for execution**

Code activation can precede later container or trigger failure. At the pinned revision:

- container rollout failure follows legacy script upload;
- trigger failure can follow either versions deployment or legacy upload.

The helper reports activation method, activated version when available, failed phase, and possible partial application while rethrowing the exact original error.

Review found a real defect in the first helper version: a throwing reporting callback could replace the deployment error. Reporting is now best-effort, and the executed model proves the operation error remains authoritative.

Next gate:

- execute the helper package test including the throwing-reporter regression;
- add mocked legacy-upload/container, versions/trigger, and legacy/trigger paths;
- accept terminal and machine-readable receipt contracts;
- keep automatic rollback out of the first patch.

## Candidate #165 — Vite container cleanup ownership

Disposition: **accept as source-confirmed and model-executed; hold production edits for mocked plugin tests**

Canonical issue: #165

Durable note: `notes/vite-container-cleanup-ownership.md`

The source establishes three connected ownership gaps:

1. current-session tags are registered only after asynchronous image preparation succeeds;
2. dev and preview each keep one module-global process-exit callback slot, so a later same-mode instance can replace an earlier owner;
3. failed dev restart cleanup can lose old tags when later preparation replaces the set.

The model passed:

```text
PASS: a single exit slot loses earlier cleanup ownership
PASS: a per-instance registry cleans every live server owner
PASS: failed cleanup retains ownership for an exit retry
PASS: successful close unregisters and avoids duplicate cleanup
PASS: preparation failure preserves its original error
PASS: failed restart cleanup retains old tags alongside new tags
```

The unapplied patch candidate combines:

- per-instance callbacks;
- ownership registration before preparation;
- old/new tag union after failed restart cleanup;
- cleanup on preparation failure with exact-error preservation;
- programmatic preview-close cleanup;
- warnings and retry retention when cleanup returns `false`;
- unregistering only after successful final cleanup.

Next gate:

- execute mocked two-dev and two-preview instance tests;
- execute partial-preparation, close, warning, retry, and restart-tag tests;
- preserve primary errors and prove one owner cannot unregister another.

## Candidate #179 — Vite logical runtime ownership

Disposition: **accept the source finding and async owner-handoff direction; hold broad implementation for Vite 6/7/8 package tests**

Canonical issue: #179

Durable note: `notes/vite-shared-context-ownership.md`

### Process-global ownership conflation

`src/index.ts` creates one module-global `SharedContext`, and every `cloudflare()` call creates a fresh `PluginContext` backed by it.

The shared object contains Miniflare, Worker export types, the warning latch, restart accounting, and tunnel hostnames. The tunnel plugin separately keeps one module-global `TunnelManager`.

Consequences established by source:

- a second plugin can call `setOptions()` on the Miniflare observed by the first;
- one server's restart counter can cause another server to skip final container, tunnel, and Miniflare cleanup;
- a later tunnel can replace an earlier server's tunnel;
- closing one server can dispose process-global tunnel state;
- export, warning, and host state use the same cross-server boundary.

Ordinary CLI use commonly has one server, so incidence is unknown. Programmatic Vite use, tests, orchestrators, monorepo tooling, and embedded dev environments are the important surfaces.

### Supported-version restart order

The plugin supports Vite 6, 7, and 8. Source review of Vite 6.1.0, 7.1.12, and 8.1.5 found the same relevant order:

1. create the replacement server and plugins from existing inline config;
2. close the old generation;
3. assign replacement properties onto the existing user server object;
4. rebind the replacement's internal server reference;
5. listen again.

Replacement `cloudflare()` calls therefore occur inside the old server's `restart()` call before old-generation close.

### Executed models

The global-versus-owner-scoped model passed:

```text
PASS: a global runtime lets one plugin overwrite another plugin runtime
PASS: a global restart counter can suppress an unrelated final close
PASS: owner-scoped runtimes isolate concurrent servers
PASS: owner-scoped restart state does not suppress another owner cleanup
PASS: sequential generations of one logical server retain restart continuity
```

The async owner-handoff model passed:

```text
PASS: independent first-generation servers receive distinct owners
PASS: replacement plugins inherit only the restarting server owner
PASS: unrelated final close proceeds during another server restart
PASS: concurrent restarts keep owner handoffs isolated
PASS: failed replacement construction preserves the original server owner and error
```

### Repair slices

A narrow patch moves restart accounting into one `PluginContext`. This prevents one server's restart from suppressing another server's close and can be reviewed independently.

The broad repair needs a logical-owner record and explicit generation handoff. A promising foundation is an async-scoped owner context:

- initial plugin factories outside restart create distinct owners;
- the patched restart runs Vite's original restart inside one owner's async context;
- replacement factories claim only that owner;
- concurrent restarts keep separate async contexts;
- failed replacement construction leaves the old owner and error intact.

The complete owner record should include Miniflare, tunnel manager, export types, warning state, and tunnel hostnames. It also needs stale-generation protection and removal after true final close.

Do not use a project-root-only key or process-global handoff queue.

Next gate:

- execute the narrow restart-counter package regression;
- instrument owner handoff on Vite 6, 7, and 8;
- prove two concurrent runtimes and tunnels remain isolated;
- prove concurrent restarts do not cross-claim owners;
- prove failed replacement and stale old generations preserve exactly one cleanup owner.

## Cross-review result

A004 was withdrawn at user direction. Review coverage was retained through coordinator and peer review.

The review pass:

- strengthened A001's child identity assertion;
- tightened A002's characterization and wording;
- corrected A003's activation-path matrix;
- found and fixed A003's reporting-failure flaw;
- extracted container cleanup into candidate #165;
- extracted process-global Vite ownership into candidate #179;
- verified the restart construction order across every supported Vite major;
- kept all package execution gaps explicit.

## Centralized visibility

- #88 is the canonical batch review and disposition hub.
- #165 is the canonical Vite container-cleanup candidate.
- #179 is the canonical Vite logical-runtime candidate.
- #112 carries this synthesis and the durable notes.
- #87 owns generated coordination and stale-state validation.
- PR #105 remains a dated projection and must not override live issue state.

Both extracted candidates use the existing filterable convention:

- `state:ready`
- `type:lane`
- `parallel-safe`
- `target:workers-sdk`
- `programme:sdk-integration-lifecycle`

## Recommended order

1. Execute A001's first three package regressions and validate the runtime-first patch.
2. Execute A003 helper and mocked deploy-flow tests; refine the output contract.
3. Execute A002's cross-selector matrix and implement behavior-preserving policy disclosure.
4. Execute #165's mocked container-ownership matrix.
5. Execute #179's restart-counter regression and Vite 6/7/8 owner-handoff instrumentation.
6. Prove #179 concurrent runtime/tunnel isolation before drafting the broad owner registry.
7. Return to A001 error aggregation and named cleanup deadlines separately.
8. Add accepted candidates to the generated review queue with exact execution evidence.

## Batch boundary

No live Cloudflare deployment, route update, container rollout, tunnel, retry, rollback, Docker/container reproduction, or browser multi-server run was performed.

No issue, pull request, comment, review, reaction, branch, or message was created in public upstream repositories.
