# Tests — Miniflare runtime-first disposal

Current test judgment: **HOLD**

## Exact candidate target

Base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`  
Branch: `teamleaderleo/workers-sdk:upstream/miniflare-runtime-first-disposal`  
Current branch head: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`  
Materialization carrier: `teamleaderleo/workers-sdk#4` at `92eeb04c7866775351e184085cc53c0b9d3b1446`  
Carrier run: `30674559186`  
Carrier job: `91299001548`  
Observed carrier status: `queued`

## Target-native test file

Prepared path:

`packages/miniflare/test/teardown-lifecycle.spec.ts`

The file follows the package guidance in `packages/miniflare/AGENTS.md`: Vitest, `.spec.ts`, real Miniflare instances, controlled prototype injection, and explicit cleanup fallback.

## Control 1 — rejected proxy cleanup

### Setup

- construct a real Miniflare instance;
- await `mf.ready`;
- inject one rejection from `ProxyClient.prototype.dispose()`;
- spy on `ChildProcess.prototype.kill()`;
- call `mf.dispose()`.

### Expected baseline

- disposal rejects with the injected proxy error;
- no `SIGKILL` call for the workerd child occurs during that first disposal;
- a cleanup fallback restores the prototype and calls disposal again to terminate the child.

### Expected candidate

- disposal rejects with the injected proxy error;
- the first disposal already requested `SIGKILL` for the workerd child.

### Property

A rejected independent cleanup hook cannot skip the runtime termination request.

## Control 2 — pending proxy cleanup

### Setup

- construct and ready a real Miniflare instance;
- replace the first proxy disposal with a promise controlled by the test;
- spy on child kill;
- begin `mf.dispose()`;
- wait until proxy cleanup begins while leaving it pending;
- inspect whether workerd termination was already requested;
- release the pending proxy cleanup and finish disposal.

### Expected baseline

The workerd kill request is absent while proxy cleanup remains pending.

### Expected candidate

The workerd kill request is present before proxy cleanup is released.

### Property

A pending independent cleanup hook cannot delay initiation of runtime termination.

## Control 3 — later cleanup rejection

### Setup

- construct and ready a real Miniflare instance;
- inject one rejection from `DevRegistry.prototype.dispose()`;
- spy on child kill;
- call `mf.dispose()`.

### Expected baseline and candidate

- disposal rejects with the injected registry error;
- the workerd kill request already occurred.

### Property

The observer distinguishes the pre-runtime ordering defect from generic later cleanup failure.

## Explicit exclusion

The legacy carrier also contains a test for failed initialization followed by later cleanup rejection. That control checks error retention and aggregation. It is assigned to a separate unit and is absent from this candidate.

## Executed evidence

### A001 executable models

The accepted A001 investigation recorded successful direct Node controls for:

- sequential cleanup skipping a later ownership action after rejection;
- isolated cleanup continuing to later owners;
- a bounded pending cleanup hook;
- a post-runtime failure negative control.

Recorded commands:

```text
node /tmp/teardown-ownership.mjs
node /tmp/bounded-cleanup.mjs
```

Recorded result: pass at the A001 evidence point ending at `fa39841a98d71edd2df7561beb877f4dacbc6b7c` and summarized through `teamleaderleo/fieldwork#112`.

These models validate control flow. They do not replace target-native package execution.

### Repository inspection

Executed through GitHub at exact current base:

- read `CONTRIBUTING.md`;
- read package `AGENTS.md` and `package.json`;
- inspected current `Miniflare.dispose()` and `Runtime.dispose()`;
- compared legacy base `161443215fba3ac77407ba30f6996aa9963a0276` with current base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- inspected the legacy patch and four-test carrier file;
- separated the three lifecycle controls from the aggregation control.

Result: source mechanism remains present on current base; target code has evolved around Browser Rendering, dispatchers, temporary cleanup, and registry teardown, so current-base execution remains required.

### Local clone attempt

Attempted direct Git access from the execution environment.

Result:

```text
Could not resolve host: github.com
```

Classification: execution-environment network blocker. GitHub connector reads and writes remain available.

## Tests still required

### Baseline focused controls

Run the exact three-test file against base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`.

Expected:

- rejected proxy control: fail;
- pending proxy control: fail;
- later registry rejection control: pass.

### Candidate focused controls

Run the same file against the clean candidate head.

Expected: all three pass.

### Ordinary Miniflare gates

Use repository-supported commands for the exact candidate revision. The package scripts and contribution guide indicate these gates:

```text
pnpm install
pnpm --filter miniflare check:type
pnpm --filter miniflare test -- teardown-lifecycle.spec.ts
pnpm --filter miniflare test
pnpm run check
```

The exact accepted command set should follow current workspace behavior and CI configuration. Retain run and job links for every executed gate.

### Diff fence

Verify one commit over the base and exactly:

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

### Review controls

- confirm the test only counts `SIGKILL` calls on a child whose spawn file begins with `workerd`;
- confirm prototype mocks are restored after every test;
- confirm baseline cleanup fallback cannot turn a failed ownership assertion into a leaked CI process;
- confirm the test does not depend on child exit timing, only initiation of the kill request;
- confirm error-aggregation behavior stays outside the candidate.

## Blockers

1. Carrier run `30674559186` is queued, so the clean candidate commit has not been published.
2. Target-native controls have not executed on baseline or candidate.
3. Full package and repository checks have not executed for the candidate.
4. Public upstream issue engagement is unauthorized.

## Acceptance rule

Move the test judgment from **HOLD** only when:

- the exact clean source head is recorded;
- baseline and candidate focused receipts exist;
- candidate focused controls pass;
- applicable ordinary gates pass or every failure is classified with exact logs and unaffected-file proof;
- the source diff fence is exact;
- self-review has no unresolved correctness concern.
