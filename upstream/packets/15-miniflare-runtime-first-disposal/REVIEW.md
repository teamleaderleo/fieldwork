# Review — Miniflare runtime-first disposal

## In simple words

The ownership fix is isolated on a clean one-commit source branch with three focused tests and one changeset. Complete-diff review found a child-exit gap in the first test; the test now waits for the killed workerd child to exit, and the repair was squashed into the canonical commit. Repository and focused execution are running. Browser Rendering interaction, exact target receipts, and independent review remain.

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
- Exact clean head: `e5ac5d046a8b2ac634027e9da59dec93c61a650e`
- Canonical owned-fork source PR: `teamleaderleo/workers-sdk#5`
- Source relation: one commit ahead, zero behind.
- Changed-file count: three.
- Diff size: `136` additions, `4` deletions.
- Focused execution carrier: `fieldwork/unit15-focused-execution` at `9853642ffa91838a9080b34f072355d95dd12c3d`.
- Legacy carrier: PR `teamleaderleo/workers-sdk#1`, head `7d51105349020151c2efd0a961706c59228ca9fd`.
- Accepted A001 evidence point: `fa39841a98d71edd2df7561beb877f4dacbc6b7c`.
- Retired materialization carrier: PR `teamleaderleo/workers-sdk#4`, head `92eeb04c7866775351e184085cc53c0b9d3b1446`.
- Materialization run/job: `30674559186` / `91299001548`, success.

## Repository-policy audit

Read and applied:

- Fieldwork `AGENTS.md` and `START_HERE.md`;
- every root document required by `START_HERE.md`;
- packet workflow, index, directory rules, and templates;
- Workers SDK `CONTRIBUTING.md`;
- Miniflare package `AGENTS.md` and `package.json`;
- Workers SDK target hub `teamleaderleo/fieldwork#3`.

Policy result: bounded continuation and owned-fork execution are authorized by the assignment. Public upstream interaction remains a separate authority boundary. Missing target execution maps to **EXECUTE**.

## Evidence audit

| Claim | Evidence class | Current limit |
| --- | --- | --- |
| current base waits for browser and proxy cleanup before runtime disposal | `source-read` | exact source ordering |
| `Runtime.dispose()` sends the workerd kill request synchronously | `source-read` | child-exit completion is asynchronous |
| early rejection or pending control flow can skip or delay a later ownership action | `model-executed` | dependency-free lifecycle models |
| clean candidate exists at current base | source materialization receipt | carrier contains no target assertion |
| three target-native controls exist | `target-test-prepared` | exact-head execution receipt pending |
| repository and focused execution started | execution initiated | conclusions pending |

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

Repaired. Complete-diff review found that the first candidate test could finish after observing `SIGKILL` while the runtime-exit promise remained unawaited because the proxy rejection exited disposal early. The test now captures the killed workerd child and awaits its `exit` event. The repair is included in canonical head `e5ac5d046a8b2ac634027e9da59dec93c61a650e`.

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

Exact source head: `e5ac5d046a8b2ac634027e9da59dec93c61a650e`

Started repository workflows include:

- CI — `30690979156`;
- CI (Other Node Versions) — `30690979168`;
- Changeset Review — `30690979176`;
- Semgrep OSS scan — `30690979141`;
- target integration suites triggered by source PR `#5`.

A narrow execution carrier also runs:

```text
pnpm install --frozen-lockfile
pnpm --filter miniflare test -- teardown-lifecycle.spec.ts
pnpm --filter miniflare check:type
```

At this review snapshot, disposition-relevant conclusions remain pending. Skipped preview and prerelease workflows provide no source validation.

## Security and privacy review

- no credentials or secrets involved;
- no network-facing authority change;
- no public upstream interaction performed;
- public drafts remain dormant;
- materialization and focused workflow files are absent from the canonical source head.

## Current clearing conditions

1. Obtain a retained candidate focused-test receipt at exact head `e5ac5d046a8b2ac634027e9da59dec93c61a650e`.
2. Obtain a retained baseline focused-test receipt at exact base `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`.
3. Classify ordinary Miniflare and repository gate results by actual source coverage.
4. Review Browser Rendering interaction and simultaneous-failure precedence.
5. Synchronize all packet files and source PR text at the final exact head.
6. Receive independent final review before `READY`.

Public-contact authority is the final submission boundary and does not block execution or packet completion.

## Continuation checklist

1. Inspect source PR `#5` and focused-carrier workflow conclusions.
2. Confirm the focused lifecycle file ran and record assertion count and duration.
3. Build a baseline carrier from the same test file after candidate receipt succeeds.
4. Repair any TypeScript, lint, test, or Browser Rendering feedback on the canonical branch.
5. Re-squash after source movement and re-run exact-head gates.
6. Update `README.md`, `TESTS.md`, `UPSTREAM_PR.md`, source PR `#5`, packet PR `#456`, and issue `#435`.
7. Request independent review against the final source and packet heads.
8. Keep public upstream drafts dormant until authorization.

## Disposition rationale

The source mechanism is current, the clean candidate is bounded, the file fence is exact, and the test-harness leak found in review is repaired. Target-native evidence and Browser Rendering review remain. **EXECUTE** names the current transition accurately.
