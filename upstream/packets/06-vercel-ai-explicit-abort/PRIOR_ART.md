# Prior art and duplicate scan — unit 06

Search refreshed: `2026-08-01`

Public upstream was read only. No comments, reviews, reactions, branches, or pull requests were created there.

## Primary issue and implementation lineage

### `vercel/ai#15430`

The primary report covers `streamText` / `ToolLoopAgent.stream()` result promises remaining pending after a mid-stream abort. It includes a production scenario, minimal reproduction, source diagnosis, and an upstream reproduction receipt.

Relationship: primary issue; do not duplicate.

### `vercel/ai#16852` at `0ef2ae9a7f143d90972b4ff217046e0b04ea67f1`

Maintainer-authored pending-read fix. It adds independent abort observation, root rejection, one abort chunk, pending reader cancellation, and normal-completion suppression.

Relationship: direct implementation provenance. Unit 06 extends its terminal-ordering and race coverage. Public delivery should update, replace, or supplement this PR only with maintainer agreement.

### `vercel/ai#15495` at `98bd4b03b3b8bfb889b5c391832a171ab183a59e`

Separate open candidate for a provider stream error/cancellation when the SDK's own operation signal has not fired. It rejects still-pending result promises on mid-body error and reports Node, Edge, generate-text, agent, type, and lint execution.

Relationship: complementary error path. It does not replace explicit caller-abort ownership, callback ordering, or registration-gap cancellation. A future combined review must prevent duplicated result-rejection helpers or conflicting error/abort arbitration.

### `vercel/ai#11166`

Earlier candidate proposed treating any `AbortError` from middleware as abort even when the caller signal is not the source.

Relationship: compatibility warning. Unit 06 intentionally makes caller abort win once selected; it does not classify every provider or middleware `AbortError` as the caller's operation abort.

## Lifecycle and cleanup precedent

### `vercel/ai#17561`

First-content timeout work records timer and abort-listener ownership across completion, setup failure, provider error, cancellation, and multi-step re-arming in Node and Edge.

Relationship: direct test-design precedent for listener and timer cleanup controls.

### `vercel/ai#18240`

Instrumentation reproduction reports an abort part, only `onAbort`, completed spans, and zero unhandled rejections under first-party OpenTelemetry on a later AI SDK version.

Relationship: observability and unhandled-rejection precedent. It does not exercise the pending-read and hostile direct-cancel gaps.

### Scout-recorded commits

- `86a84c90c05a2dbbf828505b2809a0350b13c7e8` — abort should surface as one abort outcome rather than both error and abort.
- `2696562b90b6f181df8696c40b2f6dfbe89a0386` — result getters must own enough stream progress to settle without hidden extra consumption.
- `eeefc3f64920fc4f576263f1272194e004edae4d` — lazy stream lifetime owns step-timeout cleanup.
- `106ea59106671b9e782d32c1fa2acdbce2ab5057` — first-content timeout expands cleanup coverage across semantic activity, abort, error, cancellation, and runtimes.

Relationship: accepted behavioral and test precedent, not equivalent implementations.

## Adjacent terminal-result work

### `vercel/ai#17499`

Adds explicit terminal finish/error representation for stream paths that emit an error and close without finish.

Relationship: adjacent provider-error and UI outcome work. Unit 06 stays scoped to explicit caller abort and does not choose incomplete/error finish representation.

### `vercel/ai#17182`

Streaming transcription result getters claim and drain a live stream so promises settle without requiring separate stream consumption.

Relationship: public result-settlement ownership precedent.

## Duplicate conclusion

Equivalent complete implementation found: `no`.

Partial overlapping work exists in #16852 and #15495. The narrow contribution still adds distinct value through:

- callback-independent terminal mechanics;
- deterministic caller-abort versus later provider-error arbitration;
- multi-consumer cardinality controls;
- direct registration-gap provider cancellation;
- hostile rejecting and never-settling cancellation controls;
- listener, timer, reader, and unhandled-rejection review.

## Delivery implication

A standalone public PR would compete with open #16852 and overlap #15495. The preferred route, after authorization, is maintainer-directed consolidation or an update to the existing explicit-abort candidate. Until then, keep the source and packet in owned repositories.