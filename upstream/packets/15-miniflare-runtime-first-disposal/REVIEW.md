# Review — Miniflare runtime-first disposal

## In simple words

The ownership fix has been extracted onto a clean one-commit source branch with three focused tests and one changeset. The diff matches unit 15 and the temporary materialization workflow has been retired. The current transition is execution: confirm the focused controls, ordinary Miniflare gates, child-exit cleanup, and Browser Rendering interaction at exact head `56f4df168d7c4707890ca3345e3d4a34ee3fa08a`.

Review date: `2026-08-01`

Current disposition: **EXECUTE**

Work class: **upstream-fork research**  
Canonical delivery surface: `teamleaderleo/workers-sdk#5`  
Canonical branch: `upstream/miniflare-runtime-first-disposal`

## Reviewed scope

Exact candidate inventory:

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

Production change count: one source location in `Miniflare.dispose()`.

## Revision audit

- Public base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`
- Fork `main`: verified at the same revision.
- Clean branch: `upstream/miniflare-runtime-first-disposal`
- Exact clean head: `56f4df168d7c4707890ca3345e3d4a34ee3fa08a`
- Canonical owned-fork source PR: `teamleaderleo/workers-sdk#5`
- Source relation: one commit ahead, zero behind.
- Changed-file count: three.
- Diff size: `123` additions, `4` deletions.
- Legacy carrier: PR `teamleaderleo/workers-sdk#1`, head `7d51105349020151c2efd0a961706c59228ca9fd`
- Accepted A001 evidence point: `fa39841a98d71edd2df7561beb877f4dacbc6b7c`
- Retired execution carrier: PR `teamleaderleo/workers-sdk#4`, head `92eeb04c7866775351e184085cc53c0b9d3b1446`
- Materialization run/job: `30674559186` / `91299001548`, success.

## Repository-policy audit

Read and applied:

- Fieldwork `AGENTS.md` and `START_HERE.md`;
- `CHARTER.md`, `CODE_FIRST.md`, `PLAIN_LANGUAGE.md`, `METHOD.md`, and `REFERENCE_POLICY.md`;
- `PROGRAMMES.md`, `TARGET_HUBS.md`, `EXPERIMENTS.md`, `TESTBEDS.md`, and `INTEGRATION_CONTEXT.md`;
- `COORDINATION.md`, `REVIEWING.md`, and `BATCHES.md`;
- packet workflow, unit index, directory rules, and templates;
- Workers SDK `CONTRIBUTING.md`;
- Miniflare package `AGENTS.md` and `package.json`;
- Workers SDK target hub `teamleaderleo/fieldwork#3`.

Policy result: bounded continuation and owned-fork execution are authorized by the assignment. Public upstream interaction remains a separate authority boundary. Missing target execution maps to **EXECUTE**.

## Evidence audit

| Claim | Evidence class | Current limit |
| --- | --- | --- |
| current base waits for browser and proxy cleanup before runtime disposal | `source-read` | exact source ordering |
| `Runtime.dispose()` sends the workerd kill request synchronously | `source-read` | child-exit completion remains asynchronous |
| early rejection/pending control flow can skip or delay a later ownership action | `model-executed` | dependency-free lifecycle models |
| clean candidate exists at current base | source materialization receipt | no target assertion in carrier |
| three target-native controls exist | `target-test-prepared` | exact-head execution receipt pending |
| repository CI started for source PR `#5` | execution initiated | job conclusions pending |

## Legacy evidence separation

Pass. The legacy carrier combines several lifecycle investigations. Unit 15 extracts only the runtime-first source change and three native controls. Vite owner handoff, aggregation, deadlines, container cleanup, and other experiments remain excluded.

## Prior-art correction

Pass. `cloudflare/miniflare#392` is retained only as repository-migration context. Its reviewed diff does not directly prove the fine-grained lifecycle claim previously attributed to it.

## Public symptom attribution

Pass. `cloudflare/workers-sdk#14903` is described as a symptom match with an open causal question. The packet makes no causal claim.

## Correctness review

### Ownership invariant

Pass for design. The source owner of the workerd child is `Runtime`. The candidate invokes that owner's disposal method before independent awaits can interrupt control flow.

### Synchronous throw handling

Pass for prepared code. Wrapping the invocation in `try`/`catch` and converting a synchronous throw to a rejected promise provides one later await path. Current `Runtime.dispose()` appears non-throwing in ordinary operation; the wrapper also covers future changes and test doubles.

### Pending cleanup

Pass for design. The candidate starts runtime termination before the first awaited independent hook. This directly covers the pending-proxy case, which catch-and-continue alone would miss.

### Rejection observation

Pass with a bounded limit. The retained runtime promise receives an immediate rejection observer because an earlier hook can reject before the code reaches the final await.

When both runtime disposal and an earlier hook fail, the earlier hook remains the outward rejection and the runtime rejection is observed without aggregation. Complete error aggregation belongs to a separate unit.

### Browser cleanup interaction

Execution/review item. Current source intentionally places browser cleanup before runtime disposal. Browser Rendering now uses its own CDP endpoint and process helper, suggesting independent ownership. Target review should confirm that early workerd termination preserves browser cleanup and useful diagnostics.

### Later cleanup progression

Pass for successful-path ordering. The candidate still awaits runtime exit before closing runtime and dev-registry dispatchers. Later servers, temporary state, registry, and proxy controllers retain their existing order.

### Repeated disposal and missing child

Pass by source inspection. `Runtime.dispose()` clears its child reference before killing and returns when no child exists. Early invocation remains idempotent at that boundary.

## Test review

### Focus

Pass. The three tests correspond to rejected pre-runtime cleanup, pending pre-runtime cleanup, and a later-cleanup negative control.

### Process identification

Pass by source inspection. The helper filters observed calls to `SIGKILL` on a `ChildProcess` whose spawn file begins with `workerd`.

### Baseline cleanup safety

Pass by source inspection. The rejected-proxy control restores the mock and performs fallback disposal when the vulnerable first call did not kill workerd.

### Candidate child-exit completion

Execution/review item. On the candidate, the first rejected-proxy test observes the kill request and then ends without awaiting the retained runtime-exit promise, because the proxy error exits `mf.dispose()` before its final await. Confirm the killed child exits before the runner completes or amend the test to retain and await an exit signal without changing the property under test.

### Pending-operation control

Pass by source inspection. The pending promise is released before the test awaits disposal, so the candidate completes full disposal and the vulnerable baseline can clean up deterministically.

### Later-cleanup negative control

Pass by source inspection. The injected `DevRegistry.dispose()` failure occurs after runtime disposal and should preserve the workerd-kill observation on both baseline and candidate.

## Change-fence review

Pass.

- one commit over exact base;
- exactly three files;
- no workflow, experiment, packet, or carrier machinery on the clean source branch;
- changeset names `miniflare` as a patch;
- no aggregation or Vite ownership code.

## Execution status

Exact source head: `56f4df168d7c4707890ca3345e3d4a34ee3fa08a`

Started workflows include:

- CI — `30690756068`;
- CI (Other Node Versions) — `30690756037`;
- Changeset Review — `30690756089`;
- Semgrep OSS scan — `30690756086`;
- target integration suites triggered by source PR `#5`.

At this review snapshot, the disposition-relevant jobs remain pending. Skipped preview and prerelease workflows provide no source validation.

## Security and privacy review

- no credentials or secrets involved;
- no network-facing authority change;
- no public upstream interaction performed;
- public drafts remain dormant;
- the owned materialization carrier is closed and absent from the canonical source head.

## Current clearing conditions

1. Obtain a retained candidate focused-test receipt at exact head `56f4df168d7c4707890ca3345e3d4a34ee3fa08a`.
2. Obtain a retained baseline focused-test receipt at exact base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`.
3. Classify ordinary Miniflare and repository gate results by actual source coverage.
4. Clear or repair the first-test child-exit completion concern.
5. Review Browser Rendering interaction and simultaneous-failure precedence.
6. Synchronize all packet files and source PR text at the final exact head.
7. Receive independent final review before `READY`.

Public-contact authority is the final submission boundary and does not block execution or packet completion.

## Continuation checklist

1. Inspect source PR `#5` workflow runs and job logs.
2. Identify the job that executes Miniflare package tests and confirm the new file ran.
3. Add a focused execution carrier only when repository CI omits the exact assertion.
4. Repair the test if child-exit cleanup or TypeScript/lint feedback requires it.
5. Re-run exact-head focused and ordinary gates after any source movement.
6. Update `README.md`, `TESTS.md`, `UPSTREAM_PR.md`, source PR `#5`, and issue `#435`.
7. Request independent review against the final source and packet heads.
8. Keep public upstream drafts dormant until authorization.

## Disposition rationale

The source mechanism is current, the clean candidate is bounded, the file fence is exact, and the execution carrier is retired. Target-native evidence and two focused review items remain. **EXECUTE** names the current transition accurately.
