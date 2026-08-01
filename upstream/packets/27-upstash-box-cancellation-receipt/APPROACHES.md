# Approaches — Unit 27 cancellation-request receipt

## In simple words

The selected direction keeps remote run status authoritative and returns a separate immutable request receipt. It wins on compatibility and bounded scope. The current patch needs one TypeScript stream-abort repair before renewed execution.

## Decision criteria

1. Local request state stays separate from remote terminal outcome.
2. Legacy TypeScript and Python `cancel()` returns remain compatible.
3. Concurrent callers within one run object share one operation and result.
4. One caller cancellation cannot cancel shared Python work.
5. Generated sync Python remains reproducible.
6. The change avoids a new polling lifecycle.

## Selected approach

### Additive shared request receipt per run object

- Design: `requestCancel()` / `request_cancel()` returns an immutable accepted/failed receipt with outcome `unknown`; existing `cancel()` delegates.
- Owning boundary: each in-memory `Run` object.
- Evidence: target execution `30642924979`; exact patch and receipt retained in this packet.
- Advantages:
  - preserves legacy returns;
  - prevents duplicate requests within one run object;
  - gives callers a truthful operation result;
  - keeps provider detail out of the public value;
  - works across TypeScript, async Python, and generated sync Python.
- Costs and risks:
  - failed receipts stay cached;
  - separate wrappers for one remote run do not coordinate;
  - TypeScript observer-abort composition remains broken.
- Remaining controls: real stream-path abort origin, timeout separation, two-wrapper boundary, current-head gates.

## Viable alternatives

### Nonterminal `cancelling` plus reconciliation

- Design: publish a new nonterminal status and poll or consume events until terminal state arrives.
- Why plausible: richer lifecycle visibility.
- What it improves: callers can distinguish request acceptance from terminal reconciliation.
- What it widens: public state, network ownership, retries, backoff, stop conditions, event/poll ordering, compatibility.
- Reopening trigger: maintainers require built-in terminal reconciliation.

### Throw request failures

- Design: preserve status and reject `cancel()` on HTTP/transport failure.
- Why plausible: conventional error propagation and easy deliberate retry.
- Cost: breaks the existing non-throwing caller contract and open CLI cancellation work.
- Reopening trigger: project policy permits a breaking major-version change.

### Box/run-ID keyed registry

- Design: store cancellation operations by box plus remote run ID.
- Improvement: coordination across wrapper objects.
- Cost: lifecycle, garbage collection, retries, stale IDs, cross-client semantics, and process boundaries.
- Reopening trigger: documented cross-wrapper coordination requirement.

## Executed losing approaches

### Directly change `cancel()` return type

- Record: model comparison PR #372 at `c178f689ab165d30c9ba863187b8424031a6c78f`.
- Result: runtime-compatible for ignored results, but static assignments and overrides can break.
- Why it lost: additive split preserves stronger source compatibility.

### `cancelling` plus mandatory reconciliation

- Record: PR #372.
- Result: coherent but wider than required to fix false terminal publication and duplicate requests.
- Why it lost: more network and lifecycle obligations.

### Initial patch artifact generation

- Record: PR #389 early heads and artifact `8797603134`.
- Result: retained patch omitted untracked new files.
- Why it lost: tested tree and durable patch differed.
- Retained lesson: exact 15-path inventory and replayable artifact are required.

### Abort observer only when creating the shared request

- Record: pre-rerun PR #389 generation.
- Result: a later observer attached after receipt settlement stayed active.
- Why it lost: legacy `cancel()` behavior expected current observer shutdown.
- Retained lesson: post-settlement observer control.

## Rejected easy answers

### Keep assigning `status = "cancelled"`

Request acceptance or failure does not prove remote terminal outcome. Baseline request failure still assigns terminal `cancelled`.

### Swallow failure with no receipt

Callers still cannot distinguish request success/failure, and concurrent calls still duplicate the operation.

### Retry failed requests automatically

A request may have reached the provider despite local failure. Hidden replay can duplicate an operation.

### Claim at-most-once per remote run

Coordinator state lives on one object. Two wrappers with the same ID remain independent.

## Prior upstream approaches

| Link | Approach | Status | Relationship |
| --- | --- | --- | --- |
| [`upstash/box#68`](https://github.com/upstash/box/pull/68) | current `Run`/`StreamRun` model and cached status | merged | defines the ownership boundary |
| [`upstash/box#51`](https://github.com/upstash/box/pull/51) | integration cancellation coverage | merged | confirms cancellation is a supported path |
| [`upstash/box#82`](https://github.com/upstash/box/pull/82) | Ctrl+C calls `run.cancel()` and tracks caller intent separately | open | compatibility consumer; no shared receipt |
| Fieldwork PR #332 | exact baseline characterization | closed historical | establishes current defect |
| Fieldwork PR #337 | bounded characterization claims | closed historical | separates observer control from full stream execution |
| Fieldwork PR #372 | repair-family comparison | closed historical | selects additive receipt |
| Fieldwork PR #389 | target materialization and execution | open research carrier | retained candidate and blocker |
| Fieldwork PR #391 | duplicate rerun carrier | closed superseded | no unique source |

## Deferred adjacent work

- terminal polling/reconciliation;
- explicit retry;
- cross-object registry;
- hosted behavior and billing;
- CLI presentation.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-31 | #329 characterization | select truthful operation receipt | false terminal state and duplicate requests are separable from reconciliation | baseline disproved |
| 2026-07-31 | PR #372 `c178f689...` | select additive split API | strongest compatibility | target policy permits direct return-type change |
| 2026-07-31 | PR #389 `1e7909da...`, run `30642924979` | retain cross-SDK candidate | focused/full gates green and artifact complete | stronger complete-path review |
| 2026-07-31 | review `4830012327` at `ccaa28e...` | `REPAIR` | real stream iterator still maps cancellation-request abort to terminal cancelled | stream-path repair and renewed execution |
| 2026-08-01 | upstream `9f7533c...` plus artifact verification | keep `REPAIR` | relevant source unchanged; patch integrity confirmed; blocker persists | repaired target-native stream control passes |
