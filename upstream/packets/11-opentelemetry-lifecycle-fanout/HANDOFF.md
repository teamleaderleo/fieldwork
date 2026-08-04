# Handoff — Unit 11: stabilize lifecycle fanout targets

## Current state

`UPSTREAM PREPARATION IN PROGRESS — SOURCE REVIEW ACCEPTED — EXACT-HEAD CI PENDING`

The repository owner approved moving the candidate into upstream preparation. The source has been refreshed onto current public `main`, overlap and contribution logistics have been checked, and the upstream-facing description has been rewritten in the repository's current pull-request format.

The source preview and packet are intentionally draft while the fresh exact-head workflow matrix runs.

## Exact identities

- refreshed public-main base: `f278e3b8427c406c271b8cba2c0f1a9c47c2f15e`;
- canonical source branch: `teamleaderleo/opentelemetry-js:upstream/unit-11-lifecycle-fanout-v2`;
- exact prepared source head: `f4cb44bcccffbc0eb39e774284655e0f965cfce1`;
- source preview PR: `teamleaderleo/opentelemetry-js#19`;
- packet branch: `p0/435-unit-11-opentelemetry-lifecycle-fanout-current`;
- packet path: `upstream/packets/11-opentelemetry-lifecycle-fanout/`;
- source relation: ahead 1, behind 0.

## Completed preparation

1. Refreshed public `main` and found it three commits ahead of the earlier base.
2. Preserved upstream PR #6929's new per-call trace force-flush timeout API.
3. Preserved the unrelated current-main `MultiSpanProcessor.onEnding()` forwarding behavior.
4. Rebuilt the six-file candidate as one commit on the refreshed base.
5. Updated the provider tests to use the current per-call timeout option.
6. Re-ran issue and PR searches; no equivalent repair was found.
7. Rechecked current contribution, changelog, and pull-request-template requirements.
8. Drafted the exact root and experimental changelog lines, pending a real public PR number.
9. Rewrote the source preview and packet upstream draft in concise upstream-facing form.
10. Performed a fresh complete-diff source review; no blocking defect was found.

## Fresh exact-head execution

Started for `f4cb44bcccffbc0eb39e774284655e0f965cfce1`:

- Unit Tests `30956029453`;
- Lint `30956029480`;
- W3C Trace Context Integration Test `30956029456`;
- Bundler tests `30956029470`;
- Ensure API Peer Dependency `30956029447`;
- CodeQL Analysis `30956029506`;
- E2E Tests `30956029462`;
- Zizmor GitHub Actions Security Analysis `30956029460`;
- Old Node.js Compatibility `30956029502`.

## Remaining gate

1. Classify all fresh exact-head workflows.
2. Repair any candidate-relevant failure rather than parking it.
3. If the matrix is green, mark the source preview and packet ready and present the final public-contact decision.
4. After explicit public-contact authorization, create the upstream PR and immediately add both changelog entries using its assigned number.

## Contact boundary

Public upstream interaction authorized: `false`.  
Public upstream interaction performed: `false`.
