# Tests — Miniflare runtime-first disposal

## In simple words

The exact clean source and three lifecycle controls exist. The source fence is verified. The first control now waits for the killed workerd child to exit, closing the test-harness leak found during self-review. Repository CI and a narrow focused carrier are running. The remaining work is to retain candidate and baseline receipts and classify ordinary gates.

Current test judgment: **EXECUTE**

## Exact candidate target

Base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`  
Canonical branch: `teamleaderleo/workers-sdk:upstream/miniflare-runtime-first-disposal`  
Canonical source head: `e5ac5d046a8b2ac634027e9da59dec93c61a650e`  
Canonical source PR: `teamleaderleo/workers-sdk#5`

Materialization carrier:

- PR: `teamleaderleo/workers-sdk#4`, closed;
- head: `92eeb04c7866775351e184085cc53c0b9d3b1446`;
- run/job: `30674559186` / `91299001548`;
- result: success.

Focused execution carrier:

- branch: `fieldwork/unit15-focused-execution`;
- head: `9853642ffa91838a9080b34f072355d95dd12c3d`;
- source parent: `e5ac5d046a8b2ac634027e9da59dec93c61a650e`;
- extra file: `.github/workflows/fieldwork-unit15-focused.yml`;
- commands: focused lifecycle test, then Miniflare type check;
- carrier machinery is absent from the canonical source branch.

## Exact source fence

Verified through the base-to-head comparison:

- one commit ahead;
- zero commits behind;
- exactly three changed files;
- `136` additions and `4` deletions.

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

## Target-native test file

Committed path:

[`packages/miniflare/test/teardown-lifecycle.spec.ts`](https://github.com/teamleaderleo/workers-sdk/blob/e5ac5d046a8b2ac634027e9da59dec93c61a650e/packages/miniflare/test/teardown-lifecycle.spec.ts)

The file uses Vitest, real Miniflare instances, controlled prototype injection, a workerd-specific child-kill observer, explicit fallback cleanup, and child-exit waiting after the rejected-proxy control.

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
- the test restores the proxy mock and calls disposal again to terminate the child before failing the ownership assertion.

### Expected candidate

- disposal rejects with the injected proxy error;
- the first disposal already requested `SIGKILL` for the workerd child;
- the test awaits that child's exit before completing.

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

The legacy carrier also contains a failed-initialization plus later-cleanup rejection test. That control checks error retention and aggregation. It belongs to a separate unit and remains absent from this candidate.

## Executed evidence

### Materialization receipt

Workflow run `30674559186`, job `91299001548` completed successfully.

Established:

- branch creation from exact base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- current-source patch application;
- creation of the three-test file and changeset;
- publication of the initial clean source head.

Evidence class: source materialization. This receipt contains no target assertion.

### A001 executable models

The accepted A001 investigation recorded passing direct Node controls for:

- sequential cleanup skipping a later ownership action after rejection;
- isolated cleanup continuing to later owners;
- a bounded pending cleanup hook;
- a post-runtime failure negative control.

Recorded commands:

```text
node /tmp/teardown-ownership.mjs
node /tmp/bounded-cleanup.mjs
```

Evidence point: `fa39841a98d71edd2df7561beb877f4dacbc6b7c`, summarized through `teamleaderleo/fieldwork#112`.

Evidence class: `model-executed`. These controls validate JavaScript control flow and leave package behavior for target execution.

### Source and complete-diff inspection

Executed through GitHub at exact base and candidate head:

- repository and package instructions read;
- current `Miniflare.dispose()` and `Runtime.dispose()` inspected;
- legacy and current bases reconciled;
- legacy four-test carrier split into this unit's three controls and the excluded aggregation control;
- complete source PR `#5` patch reviewed;
- first-test child-exit concern found and repaired;
- repaired source squashed to one canonical commit.

Evidence class: `source-read`, `target-test-prepared`, and complete-diff review.

### Local clone attempt

Direct Git access from the local runner failed with:

```text
Could not resolve host: github.com
```

Classification: local runner network limitation. GitHub reads, writes, source materialization, and owned-fork Actions remain available.

## Current exact-head workflows

Canonical source head: `e5ac5d046a8b2ac634027e9da59dec93c61a650e`

| Workflow | Run | State at last inspection |
| --- | ---: | --- |
| CI | `30690979156` | pending / jobs queued |
| CI (Other Node Versions) | `30690979168` | pending |
| Changeset Review | `30690979176` | pending |
| Semgrep OSS scan | `30690979141` | queued |
| Wrangler E2E | `30690979155` | pending |
| Vite Plugin E2E | `30690979169` | pending |
| Vite plugin playgrounds | `30690979153` | pending |
| C3 E2E | `30690979151` | pending |
| Local Explorer UI E2E | `30690979145` | pending |
| Deploy Previews | `30690979172` | skipped |
| Prerelease | `30690979154` | skipped |

The broad repository matrix exceeds this unit's direct scope. Each result must be classified by whether it built or executed the Miniflare source and focused test.

## Tests still required

### Baseline focused controls

Run the exact three-test file against base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`.

Expected:

- rejected proxy control: fail after performing fallback cleanup;
- pending proxy control: fail after releasing the controlled promise;
- later registry rejection control: pass.

### Candidate focused controls

Run the same file against candidate head `e5ac5d046a8b2ac634027e9da59dec93c61a650e`.

Expected: all three pass.

### Ordinary Miniflare gates

Exact commands selected from current package scripts:

```text
pnpm install --frozen-lockfile
pnpm --filter miniflare test -- teardown-lifecycle.spec.ts
pnpm --filter miniflare check:type
```

The repository CI also covers broader package and workspace checks. Retain the exact command, source head, runner environment, assertion count, run, job, and result. Classify installation, setup, fixture, timeout, and unrelated-package failures separately.

## Review controls

- confirm only `SIGKILL` calls on a child whose spawn file begins with `workerd` satisfy the observer;
- confirm prototype mocks are restored;
- confirm vulnerable-baseline cleanup completes before its assertion fails;
- confirm the candidate rejection control awaits child exit;
- confirm the pending test observes kill initiation before releasing its hook;
- confirm error aggregation stays outside the candidate;
- confirm early runtime termination leaves Browser Rendering cleanup independent and diagnosable.

## Remaining execution blockers

1. A retained candidate focused-test receipt is pending.
2. A retained baseline focused-test receipt is pending.
3. Ordinary Miniflare gate conclusions are pending.
4. Browser Rendering interaction review is pending.
5. Independent final review is pending.

Public-contact authority is a later submission boundary and does not block owned-fork execution.

## Acceptance rule

Promote the test judgment from **EXECUTE** when:

- baseline and candidate focused receipts exist;
- candidate focused controls pass;
- applicable ordinary gates pass or every failure is classified with exact logs and unaffected-file proof;
- Browser Rendering interaction review clears;
- independent review accepts the exact source head.
