# Tests — Miniflare runtime-first disposal

## In simple words

The clean source and three target-native lifecycle controls now exist at one exact head. The source fence is verified. Repository CI is running on the canonical owned-fork source PR. The remaining evidence task is to confirm the focused assertions executed, capture a baseline receipt, and classify the ordinary gates.

Current test judgment: **EXECUTE**

## Exact candidate target

Base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`  
Branch: `teamleaderleo/workers-sdk:upstream/miniflare-runtime-first-disposal`  
Candidate head: `56f4df168d7c4707890ca3345e3d4a34ee3fa08a`  
Canonical source PR: `teamleaderleo/workers-sdk#5`  
Retired materialization carrier: `teamleaderleo/workers-sdk#4` at `92eeb04c7866775351e184085cc53c0b9d3b1446`  
Carrier run/job: `30674559186` / `91299001548`  
Carrier result: `success`

## Exact source fence

Verified through the base-to-head comparison:

- one commit ahead;
- zero commits behind;
- exactly three changed files;
- `123` additions and `4` deletions on source PR `#5`.

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

The canonical head contains no workflow, packet, playground, or legacy experiment files.

## Target-native test file

Committed path:

[`packages/miniflare/test/teardown-lifecycle.spec.ts`](https://github.com/teamleaderleo/workers-sdk/blob/56f4df168d7c4707890ca3345e3d4a34ee3fa08a/packages/miniflare/test/teardown-lifecycle.spec.ts)

The file uses Vitest, real Miniflare instances, controlled prototype injection, a workerd-specific child-kill observer, and explicit cleanup fallback.

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

### Materialization receipt

Workflow run `30674559186`, job `91299001548` completed successfully.

Established:

- branch creation from exact base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- current-source patch application;
- creation of the exact three-test file;
- creation of the Miniflare patch changeset;
- publication of source head `56f4df168d7c4707890ca3345e3d4a34ee3fa08a`.

Evidence class: source materialization. This receipt contains no target test execution.

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

Evidence class: `model-executed`. These controls validate JavaScript control flow and leave package behavior for target execution.

### Repository inspection

Executed through GitHub at exact current base and exact candidate head:

- read `CONTRIBUTING.md`;
- read package `AGENTS.md` and `package.json`;
- inspected current `Miniflare.dispose()` and `Runtime.dispose()`;
- compared legacy base `161443215fba3ac77407ba30f6996aa9963a0276` with current base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`;
- inspected the legacy patch and four-test carrier file;
- separated the three lifecycle controls from the aggregation control;
- reviewed the complete source PR `#5` patch.

Evidence class: `source-read` and `target-test-prepared`.

### Local clone attempt

Attempted direct Git access from the execution environment.

Result:

```text
Could not resolve host: github.com
```

Classification: runner network limitation. GitHub connector reads and writes remained available, and the owned-fork workflow materialized the clean branch.

## Current exact-head workflows

Source head: `56f4df168d7c4707890ca3345e3d4a34ee3fa08a`

| Workflow | Run | Current recorded state |
| --- | ---: | --- |
| CI | `30690756068` | queued at last inspection |
| CI (Other Node Versions) | `30690756037` | queued at last inspection |
| Changeset Review | `30690756089` | queued at last inspection |
| Semgrep OSS scan | `30690756086` | queued at last inspection |
| Wrangler E2E | `30690756036` | queued at last inspection |
| Vite Plugin E2E | `30690756056` | queued at last inspection |
| Vite plugin playgrounds | `30690756058` | queued at last inspection |
| C3 E2E | `30690756051` | queued at last inspection |
| Local Explorer UI E2E | `30690756098` | queued at last inspection |
| Deploy Previews | `30690756055` | skipped |
| Prerelease | `30690756085` | skipped |

The broad repository matrix exceeds this unit's direct scope. Each result must be classified by whether it built or executed the Miniflare source and focused test.

## Tests still required

### Baseline focused controls

Run the exact three-test file against base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`.

Expected:

- rejected proxy control: fail;
- pending proxy control: fail;
- later registry rejection control: pass.

### Candidate focused controls

Run the same file against candidate head `56f4df168d7c4707890ca3345e3d4a34ee3fa08a`.

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

Retain the exact command, source head, runner environment, assertion count, run, job, and result. Classify installation, setup, fixture, timeout, and unrelated-package failures separately.

## Review controls

- confirm the test only counts `SIGKILL` calls on a child whose spawn file begins with `workerd`;
- confirm prototype mocks are restored after every test;
- confirm baseline cleanup fallback cannot turn a failed ownership assertion into a leaked CI process;
- confirm the first control allows the killed child to finish exiting before the test process ends;
- confirm the test observes initiation of the kill request instead of child-exit timing;
- confirm error-aggregation behavior stays outside the candidate;
- confirm early runtime termination leaves Browser Rendering cleanup independent and diagnosable.

## Remaining execution blockers

1. A retained candidate focused-test receipt is pending.
2. A retained baseline focused-test receipt is pending.
3. Ordinary Miniflare gate conclusions are pending.
4. Independent final review is pending.

Public-contact authority is a later submission boundary and does not block owned-fork execution.

## Acceptance rule

Promote the test judgment from **EXECUTE** when:

- baseline and candidate focused receipts exist;
- candidate focused controls pass;
- applicable ordinary gates pass or every failure is classified with exact logs and unaffected-file proof;
- complete-diff review clears the first-test child-exit concern and browser-cleanup interaction;
- independent review accepts the exact source head.
