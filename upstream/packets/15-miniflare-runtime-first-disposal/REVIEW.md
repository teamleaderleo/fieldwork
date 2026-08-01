# Review — Miniflare runtime-first disposal

Review date: `2026-08-01`

Current disposition: **HOLD**

## Reviewed scope

Intended candidate inventory:

```text
.changeset/fuzzy-cats-dispose.md
packages/miniflare/src/index.ts
packages/miniflare/test/teardown-lifecycle.spec.ts
```

Intended production change count: one source location in `Miniflare.dispose()`.

## Revision audit

- Public base: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`
- Fork `main`: restored and verified at the same revision.
- Clean branch: `upstream/miniflare-runtime-first-disposal`
- Current clean head: `95d9b12f2c707f254b66b446e0bd9fd6b8b7d96d`
- Legacy carrier: PR `teamleaderleo/workers-sdk#1`, head `7d51105349020151c2efd0a961706c59228ca9fd`
- Accepted A001 evidence point: `fa39841a98d71edd2df7561beb877f4dacbc6b7c`
- Execution carrier: PR `teamleaderleo/workers-sdk#4`, head `92eeb04c7866775351e184085cc53c0b9d3b1446`
- Materialization run/job: `30674559186` / `91299001548`, queued at review time.

## Repository-policy audit

Read and applied:

- Fieldwork root instructions and contribution method;
- packet workflow and templates;
- Workers SDK `CONTRIBUTING.md`;
- Miniflare package `AGENTS.md` and `package.json`.

Policy consequence: this is a non-trivial lifecycle change, so the proposed route is issue-first. Public contact remains unauthorized.

## Evidence audit

### Direct current-source evidence

Pass. The current base still awaits browser and proxy cleanup before runtime disposal. `Runtime.dispose()` initiates child termination synchronously.

### Legacy evidence separation

Pass. The legacy carrier combines several lifecycle investigations. Unit 15 extracts only the runtime-first source change and three native controls. Vite owner handoff, aggregation, deadlines, and other experiments remain excluded.

### Prior-art correction

Pass. `cloudflare/miniflare#392` is retained only as repository-migration context. Its reviewed diff does not directly prove the fine-grained lifecycle claim previously attributed to it.

### Public symptom attribution

Pass. `cloudflare/workers-sdk#14903` is described as a strong symptom match with an open causal question. The packet makes no causal claim.

## Correctness review

### Ownership invariant

The source owner of the workerd child is `Runtime`. The candidate calls that owner's disposal method before independent awaits can interrupt control flow. This is the right ownership layer.

### Synchronous throw handling

Wrapping the invocation in `try`/`catch` and converting a synchronous throw to a rejected promise gives later code one promise path. Current `Runtime.dispose()` appears non-throwing in ordinary operation, though the wrapper is prudent for future changes and test doubles.

### Pending cleanup

The candidate starts runtime termination before the first awaited independent hook. This directly covers the pending-proxy case, which catch-and-continue alone would miss.

### Rejection observation

The retained runtime promise receives an immediate rejection observer because an earlier hook can reject before the code reaches the final await. This prevents transient unhandled rejection reporting.

Concern: when both runtime disposal and an earlier hook fail, the earlier hook remains the outward rejection and the runtime rejection is only observed. The packet accepts this temporary limit and assigns complete error aggregation elsewhere.

### Browser cleanup interaction

Concern: current source intentionally places browser cleanup before runtime disposal. Browser Rendering now uses its own CDP endpoint and process helper, which suggests independence. A maintainer should confirm that early workerd termination does not impair browser cleanup or diagnostics.

### Later cleanup progression

The candidate preserves the existing behavior where later dispatchers, servers, temporary state, registry, and proxy controllers execute only after browser/proxy cleanup and runtime-exit completion on the successful path. Broader cleanup isolation remains outside this unit.

### Repeated disposal and missing child

`Runtime.dispose()` clears its child reference before killing and returns when no child exists. Early invocation therefore remains safe for repeated calls and partially initialized instances at this boundary.

## Test review

### Focus

Pass. The three prepared tests correspond to rejected pre-runtime cleanup, pending pre-runtime cleanup, and later-cleanup negative control.

### Process identification

The helper filters observed kills to `SIGKILL` on a `ChildProcess` whose spawn file begins with `workerd`. This avoids counting unrelated child processes.

### Cleanup safety

The rejected-proxy baseline test restores the mock and performs fallback disposal when the first call did not kill workerd. This prevents a deliberately failing baseline control from leaving a child alive.

### Missing execution

Blocker. The prepared target-native tests have not executed at the current base or candidate. The clean branch still points to the base.

## Change-fence review

Pending. Verify after materialization:

- one commit over base;
- exactly three files;
- no workflow, experiment, packet, or carrier machinery on the clean source branch;
- changeset names `miniflare` as a patch;
- no aggregation or Vite ownership code.

## Security and privacy review

- no credentials or secrets involved;
- no network-facing behavior change;
- no public upstream interaction performed;
- public drafts exclude internal operational links;
- owned-fork execution records remain private to the project workflow where applicable.

## Current blockers

1. Source candidate has not materialized on the clean branch.
2. Focused baseline and candidate tests have not executed.
3. Ordinary checks have not executed.
4. Browser-cleanup ordering awaits maintainer review.
5. Upstream contact authorization is absent.

## Continuation checklist

1. Inspect carrier run `30674559186`, job `91299001548`.
2. When successful, record the clean source head and verify the three-file fence.
3. Close or retain carrier PR `#4` as an execution receipt; never merge its workflow into fork `main`.
4. Open an owned-fork draft source PR from `upstream/miniflare-runtime-first-disposal` to fork `main` to obtain CI receipts without contacting public upstream.
5. Run baseline and candidate focused controls.
6. Run applicable Miniflare checks.
7. Update every packet file with exact source and test links.
8. Re-review browser interaction and simultaneous-failure handling.
9. Keep public issue and PR drafts dormant until authorization.

## Disposition rationale

The source mechanism is current, the candidate is bounded, and the test design is credible. Execution evidence remains absent at the current base, and the clean branch carries no candidate commit. **HOLD** accurately records the present state.
