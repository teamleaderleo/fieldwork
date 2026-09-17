# F239-codex-upstream-convergence: Separate Codex tool continuity into reviewable ownership boundaries

Finding state: `comparative-evaluation-active`

Workstream: `J/O/I — current-source convergence, synthesis, and cross-repository audit`  
Canonical Fieldwork issue: `#239`  
Canonical finding path: `findings/F239-codex-upstream-convergence/finding.md`  
Investigation workspace: `investigations/239-codex-upstream-convergence/`  
Canonical implementation or alternatives: `several bounded owned Codex candidates; no combined implementation`  
Exact implementation heads: `append carrier teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc; terminal carrier #53@c4e0de2e54d804d1054afb90c30b7150a774151c; historical and MCP heads linked in the workspace`  
Exact base or source revision: `openai/codex@3016671bb077c43448b8fa88f3edfa9772e17058`  
Strongest evidence class: `target-executed` for bounded historical findings; current-pin append and terminal carriers remain executing  
Reviewed input generation: `read-only source snapshot, exact carrier heads, complete workspace evidence map`  
Current review disposition: `EXECUTE and COMPARE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Codex tells a model which tools exist, chooses a runtime, sends a call, waits or cancels, reports a result, stores history, and later reconstructs that history. Those steps are connected, but they are not one state machine.

A tool can be visible without a matching executable authority. A timeout can occur while a remote effect still finishes. A result can reach live conversation memory while durable append fails. A subprocess can produce bytes before a late listener subscribes.

The current direction is one shared lifecycle explanation plus several bounded technical findings and source candidates. The alternatives are still being executed and compared at their real owners. One mega-patch would mix unrelated authority, execution, persistence, replay, and output contracts.

## Why we care

Codex coordinates actions that can have external effects. The model, user, restart path, and source reviewer need accurate answers to different questions:

- Which tool definition authorized this call?
- Which runtime received it?
- Did the request leave Codex?
- Did cancellation reach the service?
- Did the external effect settle, remain possible, or become unknown?
- Did the model see the result?
- Did durable history accept the result?
- Can resume, fork, replay, and compaction reconstruct the same logical operation?
- Did terminal completion include the output retained by the producer?

Collapsing those facts can cause stale tool use, unsafe retry, misleading timeout language, missing durable history, wrong replay, or incomplete terminal completion.

## What happens if we leave it alone

Observed bounded consequences across the linked findings include:

- stale or mismatched capability and runtime ownership;
- cancellation and timeout results that do not prove remote-effect absence;
- live result formation without caller-visible durable append outcome;
- completion derived from best-effort output subscribers instead of producer-retained state;
- historical candidates appearing current after upstream ownership moved.

Frequency and aggregate user impact are not measured. Each consequence remains limited to its own exact source and execution record.

## Governing goals and invariant

Governing invariant: every state transition must preserve the identity, authority, and certainty facts owned at that boundary without treating success in another layer as equivalent proof.

| Goal or contract | Primary source | Consequence for the design |
| --- | --- | --- |
| Model-visible tools have executable authority | request construction, Code Mode host, MCP snapshots | declaration and dispatch must share a captured identity |
| Current runtime publication cannot regress | MCP manager and refresh work | only an eligible generation publishes; active calls keep captured binding |
| Cancellation is not remote-effect settlement | Fieldwork #134/#162 and current MCP ownership | retain deadline, delivery, transport, and effect certainty separately |
| Model-visible result and durable append are separate | current session / `LiveThread` / `ThreadStore` path | append acknowledgement must become an explicit fact |
| History readers consume conservative persistence facts | rollout, projection, compaction, resume, fork | ambiguous append cannot authorize unsafe retry or cleanup |
| Terminal completion uses non-lossy retained input | unified execution producer and bounded buffer | retain before best-effort broadcast and preserve current deque behavior |
| Historical execution does not imply current portability | Fieldwork exact-head policy | current claims need current source, diff, tests, and overlap review |

## Current finding

The Codex portfolio should remain separated into independently reviewable findings and proposal packets.

The shared lifecycle model is useful for orientation. It does not authorize a combined source change. Current source ownership and rollback boundaries support at least these independent areas:

1. model-visible capability and deferred executable authority;
2. MCP refresh freshness and generation publication;
3. prepared or active call runtime binding;
4. operation timeout, cancellation, transport, and remote-effect certainty;
5. live result formation and durable append acknowledgement;
6. history projection, compaction, resume, fork, and replay;
7. producer-owned terminal transcript retention;
8. evidence-carrier retirement and canonical-source transfer.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| One mega-patch crosses several state owners and rollback boundaries | `source-read` | workspace problem map and current Codex source at `3016671...` | Does not forbid later composition after independent acceptance |
| Current session append path retains an acknowledgement gap | `source-read` plus historical target execution | owned Codex #51/#52/#80 and current source fence | Current-pin carrier #80 is still queued |
| Terminal retention remains semantically useful after upstream deque work | `source-read` plus historical target execution | owned Codex #49/#53, current `VecDeque` precedent | Current carrier #53 is pending |
| Explicit MCP reconnect may absorb part of historical #46 | `source-read` | upstream #34952/#35151 and workspace precedent | Exact current call-path comparison remains |
| Current public head moved from `a01a2d...` to `3016671...` without active-fence overlap | `source-read` | one-commit compare; account-plan, auth, rate-limit, app-server schema and status files | A later relevant commit expires this carry-forward |
| Deferred tool authority needs redesign around the standalone host | `source-read` | Code Mode move at `97576b...` and current request/host boundaries | No current implementation candidate yet |

## System and ownership map

```text
model-visible capability manifest
→ captured runtime generation and authority
→ operation identity and dispatch
→ local or remote execution
→ caller deadline, cancellation, transport, and effect settlement
→ model-visible result
→ durable append acknowledgement
→ history projection, compaction, resume, fork, and replay
```

Subprocess output has a parallel chain:

```text
process output producer
→ bounded retained transcript
→ best-effort live broadcast
→ terminal completion item
```

The workspace carries orientation, evidence notes, alternatives, prior art, canonical output candidates, and an exact handoff. This finding owns the present technical conclusion and transition state.

## Historical precedent

### ThreadStore and writer ownership

- Sources: openai/codex PRs #18882, #21874, #30669, #31155, and #27249.
- Principle supported: canonical append, metadata projection, writer generation, rotation, and cleanup have explicit owners and different completion points.
- Important difference: those changes do not expose the original result append outcome to the session caller.

### MCP runtime reconciliation and reconnect

- Sources: openai/codex PRs #34952, #35151, #30083, #31471, #31292, and #31626.
- Principle supported: managers own immutable published runtime state; ordinary reuse, explicit freshness, targeted replacement, request-stable snapshots, and shared reconnect work are distinct.
- Important difference: newest-generation publication, accepted-result identity, and captured active-call authority still require exact comparison.

### Responses Lite and standalone Code Mode host

- Sources: commits `33cc928d...`, `20fedaff...`, `97576b...`; upstream PRs #35271 and #36129.
- Principle supported: capability declarations, normalized identifiers, trace reconstruction, and executable host authority are distinct but related.
- Important difference: logical trace repair does not prove the first generated capability prefix reached the model, and historical in-core loader placement no longer owns execution.

### Unified execution retention

- Sources: openai/codex PRs #31802, #34713, #36194.
- Principle supported: output is bounded, close/drain ordering matters, and invalid UTF-8 progress should be preserved.
- Important difference: best-effort subscribers still should not define the producer's final retained transcript.

The full precedent ledger is `investigations/239-codex-upstream-convergence/precedent/fieldwork-and-upstream-prior-art.md`.

## Decision criteria

| Priority | Criterion | How it will be measured or falsified |
| --- | --- | --- |
| 1 | Correct owner | exact source path and state owner for each invariant |
| 2 | Independent falsifiability | controls that can reject one candidate without relying on unrelated layers |
| 3 | Current-source compatibility | exact public pin, overlap map, and complete current diff |
| 4 | Conservative authority | no retry, compaction, publication, or cleanup inferred from weaker evidence |
| 5 | Rollback and carrier hygiene | source-only successor, immutable receipts, temporary workflow retirement |
| 6 | Reader clarity | one canonical finding and workspace map without reconstructing issue chronology |

## Alternatives instantiated or analyzed

### Option A — One lifecycle model plus bounded technical findings

- Artifact or branch: this finding and the #239 workspace.
- Invariant implemented: shared orientation without merging independent source authority.
- Expected benefit: clear review scope, independent execution, and reusable negative results.
- Expected cost or failure: more records and coordination.
- Discriminating control: each candidate must survive exact current-source execution and complete-diff review.
- Rollback boundary: retire or supersede individual outputs without discarding the shared model.

### Option B — One end-to-end mega-patch

- Artifact or branch: paper-only.
- Invariant implemented: one combined story from capability through persistence and output.
- Expected benefit: apparent end-to-end coherence.
- Expected cost or failure: mixes owners, evidence classes, compatibility surfaces, and rollback.
- Discriminating control: demonstrate one source owner and one test matrix can establish every claimed layer.
- Rollback boundary: broad, coupled revert.

### Option C — Independent findings with no synthesis layer

- Artifact or branch: historical issue/PR layout.
- Invariant implemented: maximal source-level separation.
- Expected benefit: parallelism.
- Expected cost or failure: readers cannot identify current relationships, overlap, or presentation status.
- Discriminating control: orientation time and contradictory-state audit.
- Rollback boundary: retain files and remove workspace index.

### Option D — Immediate single canonical answer

- Artifact or branch: paper-only.
- Invariant implemented: one present narrative.
- Expected benefit: simple communication.
- Expected cost or failure: hides unresolved source ownership and technical comparisons.
- Discriminating control: all active carriers and current-source comparisons would need to settle first.
- Rollback boundary: supersede the output and restore alternatives.

## Comparative results

| Criterion | Option A | Option B | Option C | Option D | Winner or unresolved reason |
| --- | --- | --- | --- | --- | --- |
| Owner fidelity | strong | weak | strong | unclear | A/C |
| Reader orientation | strong | superficially strong | weak | strong but premature | A |
| Independent execution | strong | weak | strong | weak | A/C |
| Preserves disagreement | strong | weak | weakly visible | weak | A |
| Current source readiness | partial | absent | partial | absent | A, still executing |
| Review and rollback scope | bounded | broad | bounded but fragmented | unclear | A |

## Independent criticism

| Reviewer or evidence source | Counterexample or criticism | Response or new control | Effect on recommendation |
| --- | --- | --- | --- |
| PR #271 cross-review | Workspace links depended on an uncomposed canonical-findings branch | Build this composed integration branch on PR #264 | Strengthens Option A only as a composed stack |
| State-vocabulary audit | `comparative-evaluation-active` appeared in one template but not governing tables | Define it consistently and keep it off the human decision desk | Makes current #239 state explicit |
| Current source drift | `a01a2d...` was no longer public head | Compare `a01a2d... → 3016671...`; record no active-fence overlap | Refreshes current-source boundary |
| Carrier drift | #53 moved from `0bd2fad...` to `c4e0de2...`; #80 became the current-pin append carrier | Update workspace and handoff identities | Prevents stale execution routing |

## Selected direction and losing reasons

Selected direction: Option A — one lifecycle model, several canonical findings and evidence notes, and several bounded proposal packets.

Why it wins: it preserves current ownership, supports technical comparison, gives readers a coherent map, and lets each source candidate fail or succeed independently.

| Losing or deferred option | Reason it lost or moved elsewhere | Reopening trigger |
| --- | --- | --- |
| Mega-patch | Mixed authority and evidence; incompatible rollback | Current architecture consolidates owners and independent findings are accepted together |
| No synthesis | Durable facts remain hard to navigate and reconcile | Workspace proves more costly than useful after real adoption |
| Immediate single answer | Current carriers and source-owner comparisons remain open | Every candidate receives a settled disposition |

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Public source drift after workspace pin | `a01a2d... → 3016671...` complete file compare | no overlap in declared active source fences |
| Append historical versus current-pin execution | PR #52 and current-pin PR #80 | historical receipt retained; current-pin carrier #80 queued |
| Terminal historical patch versus current deque behavior | PR #53 source reconstruction and precedent | semantic residue retained; carrier at `c4e0de2...` pending |
| Explicit versus ordinary MCP refresh | upstream #34952/#35151 and owned #46/#48 | partial overlap; exact comparison remains |
| Trace correctness versus capability delivery | Responses Lite precedent | separate controls required |
| Live result versus durable append | session/ThreadStore source map | separate facts retained |
| Broadcast versus completion transcript | unified-exec source map | producer retention remains separate |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Current MCP source restacks | Exact call-path comparison pending | dedicated MCP finding/candidate |
| Deferred authority implementation | standalone host ownership map pending | dedicated current-host finding |
| Typed `Persisted/Ambiguous` result state | append acknowledgement prerequisite first | successor after PR #80 result |
| Remote mutation replay | unsafe while outcome unknown | MCP operation finding |
| Hard process termination, Windows containment, restart reattachment | separate lifecycle owners | dedicated process findings |
| Public proposal packaging | no authorization and current gates incomplete | explicit delivery/upstream request |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/codex#52@324ddcc...` | run `30582576317` | owned exact-pin carrier | cancelled; superseded | carrier-only |
| same | run `30583872587` | owned exact-pin carrier | queued at refresh | target execution pending |
| `teamleaderleo/codex#80@401c2e5...` | run `30583967538` | current-pin append carrier | queued at refresh | target execution pending |
| `teamleaderleo/codex#53@c4e0de2...` | run `30585540688` | terminal source reconstruction and exact controls | pending at refresh | target execution pending |
| `openai/codex@3016671...` | compare from `a01a2d...` | read-only GitHub source | one account-plan commit; no declared active-fence overlap | source-read |

## Complete-diff and compatibility review

- Canonical-findings protocol comes from PR #264 head `578fb94a641905a02ee8feaa292ff928756d5ad6`.
- Workspace dossier comes from PR #266 plus PR #271's alignment repair and is composed on `integration/canonical-findings-workspaces-2026-07-31`.
- The workspace source branches remain documentation/research carriers; they grant no product merge or upstream authority.
- Append and terminal workflows remain execution-only and require source-only successors plus retirement receipts.
- Current compatibility surfaces: standalone Code Mode host, MCP manager snapshots/reconnect, ThreadStore writer generations, rollout reconciliation, unified-exec deque and lifecycle ordering.
- Exact-head review of the composed integration branch remains required.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `EXECUTE and COMPARE`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: settle current-pin append and terminal carriers, then update the candidate ledger and split accepted source findings.
- Clearing condition: every current and historical candidate has a current-source disposition, canonical finding or stopped record, exact receipt, and carrier successor/retirement state.
- Required subgates: current-source overlap, exact tests, complete diff, compatibility, source-only publication, independent review.
- Autonomous work remaining: execution, source maps, comparative prototypes, canonical finding materialization, and carrier cleanup.
- Non-delegable human decision: none currently.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | PR #266 | Created one workspace and selected bounded outputs over a mega-patch |
| 2026-07-31 | PR #271 review | Identified missing canonical-findings dependency and state-vocabulary contradiction |
| 2026-07-31 | composed integration branch | Added the missing dependency, canonical finding, comparative state, and refreshed source/carrier identities |

## References

- Fieldwork issue #239 and initiative #254.
- Fieldwork PRs #264, #266, #271, and the composed integration PR.
- `investigations/239-codex-upstream-convergence/`.
- Owned Codex PRs #45, #46, #48, #49, #51, #52, #53, and #80.
- Public Codex source through `3016671bb077c43448b8fa88f3edfa9772e17058`, read-only.
- Public upstream interaction: none.
