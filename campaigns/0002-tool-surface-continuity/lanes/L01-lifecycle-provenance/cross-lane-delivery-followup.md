# L01 follow-up after the L05 delivery review

Review date: 2026-07-30  
Related work: issue #40 and draft PR #77

## What the deeper L05 pass changes

The L01 lifecycle result remains intact: saved host dynamic tools and selected capability roots survive cold reconstruction, and the public resume/fork requests provide no current-host replacement fields.

The deeper L05 pass sharpens how that state is classified:

1. A logical discovery loader counts as effective only when it is delivered on the generated wire request or the same manifest is verified as inherited through `previous_response_id`.
2. A stale saved host generation can still have a valid, executable discovery route. That is a lifecycle-provenance warning, not a discovery-route failure.
3. A stale thread catalogue can also have a valid loader that searches an old index. That belongs to catalogue convergence rather than lifecycle provenance.

The resulting ownership split is:

- L01: saved/current generation, preserve/clear/replace semantics, and lifecycle mismatch;
- L02: direct wire delivery or verified previous-response inheritance;
- L04: catalogue, binding, and search-index generation convergence;
- L05: logical loader presence, searchable metadata, and executable load-existing semantics;
- L06: first-divergence receipt joining these observations.

## Effect on the L01 fixture

The `host_old` mismatch remains a valid demonstration. It should now be read as:

```text
saved declaration preserved
+ loader may be valid
+ saved generation differs from current host generation
= stale_saved_provenance warning
```

It should not be used as evidence that discovery itself is absent.

## Receipt additions

The campaign diagnostic receipt should include bounded digests or generations for:

- logical advertised loader;
- direct wire manifest;
- inherited manifest and verification state;
- host catalogue, thread binding, and deferred search index;
- saved and current dynamic-tool generations.

These additions preserve the separate repair boundaries. Loader absence, wire omission, stale catalogue, and stale saved provenance require different actions.

OpenAI/Codex remained read-only. No upstream contact occurred.
