# F239-codex-upstream-convergence: Separate Codex tool continuity into reviewable ownership boundaries

Finding state: `comparative-evaluation-active`

Workstream: `J/O/I — current-source convergence, synthesis, and cross-repository audit`  
Canonical Fieldwork issue: `#239`  
Canonical finding path: `findings/F239-codex-upstream-convergence/finding.md`  
Investigation workspace: `investigations/239-codex-upstream-convergence/`  
Canonical implementation or alternatives: `several bounded owned Codex candidates; no combined implementation`  
Exact implementation heads: `append source teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2; terminal exported source 8c7ea38419d790032db459816980e6b4dd38f574 with materialization carrier #85@965a79cc2cd389aca05c3753f52510ac63a4110a; MCP publication #75@c3373c717f3138ff5f0a979d12836f60800d2bcf; reconnect #76@7e9d80c4965a76b802f02d7bace17ea1c4a8931c; deferred exposure #81@8f73d8e0bb9a61e7dec7b1367d13649a88615dea`  
Exact base or source revision: `openai/codex@413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Strongest evidence class: `target-executed` for append acknowledgement, terminal producer retention, MCP publication, direct reconnect, and deferred exposure; publication, compatibility, and route gates remain candidate-specific  
Reviewed input generation: `read-only public-source compare, exact carrier/source heads, target workflow receipts, current canonical sibling findings`  
Current review disposition: `COMPARE, REVIEW CURRENT SOURCE, AND MATERIALIZE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Codex tells a model which tools exist, chooses a runtime, sends a call, waits or cancels, reports a result, stores history, and later reconstructs that history. Those steps are connected, but they have different owners.

A tool can be visible without matching executable authority. A timeout can occur while a remote effect still finishes. A result can reach live conversation memory while durable append fails. A subprocess can produce bytes before a late listener subscribes.

The selected direction is one shared lifecycle explanation plus several bounded technical findings and source candidates. Append acknowledgement and producer-owned terminal retention now have exact target execution. MCP publication and deferred exposure also have bounded receipts. Reconnect has a split result: its direct boundary passed, while the public app-server route remains under execution. One mega-patch would still mix unrelated authority, execution, persistence, replay, and output contracts.

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
- historical candidates appearing current after upstream ownership moved;
- temporary carriers being mistaken for source proposals after their useful evidence has transferred.

Frequency and aggregate user impact are unmeasured. Each consequence remains limited to its own exact source and execution record.

## Governing goals and invariant

Governing invariant: every transition preserves the identity, authority, and certainty facts owned at that boundary without treating success in another layer as equivalent proof.

| Goal or contract | Primary source | Consequence for the design |
| --- | --- | --- |
| Model-visible tools have executable authority | request construction, Code Mode host, MCP snapshots | declaration and dispatch share a captured identity |
| Current runtime publication cannot regress | MCP manager and refresh work | only an eligible generation publishes; active calls keep captured binding |
| Cancellation is separate from remote-effect settlement | Fieldwork #134/#162, RMCP behavior, current MCP ownership | retain deadline, cancellation request, delivery, transport, and effect certainty separately |
| Model-visible result and durable append are separate | current session, `LiveThread`, and `ThreadStore` path | append acknowledgement becomes an explicit fact |
| History readers consume conservative persistence facts | rollout, projection, compaction, resume, fork | ambiguous append cannot authorize unsafe retry or cleanup |
| Terminal completion uses retained producer input | unified-exec producer and bounded buffer | retain before best-effort broadcast and preserve deque/UTF-8 behavior |
| Historical execution does not imply current portability | Fieldwork exact-head policy | current claims need an exact public pin, direct diff, tests, and overlap review |
| Execution machinery is separate from product source | current carrier retirement rules | transfer receipts before cleanup and prove temporary files absent |

## Current finding

The Codex portfolio should remain separated into independently reviewable findings and proposal packets.

The shared lifecycle model is useful for orientation. It grants no combined source change. Current ownership and rollback boundaries support at least these independent areas:

1. model-visible capability and deferred executable authority;
2. MCP refresh freshness and generation publication;
3. prepared or active call runtime binding;
4. operation timeout, cancellation, transport, and remote-effect certainty;
5. live result formation and durable append acknowledgement;
6. history projection, compaction, resume, fork, and replay;
7. producer-owned terminal transcript retention;
8. process termination, descendant containment, and restart recovery;
9. evidence-carrier retirement and canonical-source transfer.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| One mega-patch crosses several owners and rollback boundaries | `source-read` | workspace problem map and current Codex source at `413492cd...` | Does not forbid later composition after independent acceptance |
| Current session append path needed caller-visible acknowledgement | `target-executed` | carrier #80 run `30583967538`; clean source #84 at `d8299b7...` | Typed persistence state and recovery remain separate |
| Producer-owned terminal retention survives current deque and UTF-8 behavior | `target-executed` | Fieldwork run `30587866332`; exported source `8c7ea384...` | Owned source-branch materialization and current-head review remain |
| MCP publication generation tickets preserve bounded publication state | `target-executed` | source #75; run `30584055792`, exact `5/5`, package pass | Live slow-A/fast-B composition remains a separate integration gate |
| Ordinary MCP calls should retain captured authority | `source-read` plus stopped alternative | upstream captured-call precedent; Fieldwork PR #290; retired carrier #79 | Cached-before-startup fallback still requires a live authority path |
| Direct host MCP refresh reconnects ready clients | `target-executed` | source #76; first #82 run passed direct controls `2/2` | App-server route rerun remains queued |
| Deferred exposure can normalize runtimes lacking a loader | `target-executed` identical source | source #81; run `30580836079`, exact planner controls `4/4` | Exposure only; host/runtime authority remains separate |
| Public drift `97576b... -> 413492...` is file-disjoint from named active source fences | `source-read` | complete five-commit GitHub compare | Semantic compatibility and complete current-head review remain required |

## Current candidate ledger

### Append acknowledgement

- Clean source: `teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`.
- Execution carrier: `#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`.
- Authoritative run/job: `30583967538` / `91010830120`.
- Result: reconstruction, formatting, four exact controls, complete `codex-thread-store`, and source publication passed.
- Disposition: `target-executed`; current-head complete-diff review pending.
- Non-goals: typed `Persisted/Ambiguous`, retry, duplicates, compaction, replay, remote settlement.

### Producer-owned terminal retention

- Reconstruction carrier: `teamleaderleo/codex#53@c4e0de2e54d804d1054afb90c30b7150a774151c`.
- Authoritative run/job: Fieldwork `30587866332` / `91023382172`.
- Result: exact refs, reconstruction, `just fmt`, four-file fence, nine unique exact controls through `just test`, core library/integration compile gates, source export, and artifact upload passed.
- Exported commit/tree: `8c7ea38419d790032db459816980e6b4dd38f574` / `563f90ea0b4bec779446aa0ce4497e8011acb0e3`.
- Materialization carrier: `teamleaderleo/codex#85@965a79cc2cd389aca05c3753f52510ac63a4110a`.
- Materialization workflow: `30589829555`, pending at this update.
- Disposition: source behavior `target-executed`; exact Git-object publication and current-head review pending.
- Non-goals: hard termination, Windows containment races, restart reattachment, remote settlement.

### MCP publication and call authority

- Publication source: `teamleaderleo/codex#75@c3373c717f3138ff5f0a979d12836f60800d2bcf`.
- Authoritative run/job: `30584055792` / `91011123543`; exact `5/5`; complete `codex-mcp` package passed.
- Publication carrier #77 cleaned to an empty diff and closed.
- Full serialized-`ToolInfo` live-rebind carrier #79 failed before source execution, transferred its losing reason, cleaned to an empty diff, and closed.
- Retained direction: captured `PreparedMcpCall` for ordinary calls; isolated live fallback for cached-before-startup advertisements with callable-authority equality before side effects.
- Canonical sibling finding: Fieldwork PR #290 at `809673e507a0dad064620bf765a7108060ab6b16`.
- Disposition: publication `target-executed`; broad live-rebind direction `stopped`; bounded integration comparison remains.

### MCP reconnect

- Current source: `teamleaderleo/codex#76@7e9d80c4965a76b802f02d7bace17ea1c4a8931c`.
- Current app-server carrier: `#82@feb0c46d3b88e03c94cb9f07d6ba903205e73f05`.
- First run/job: `30584136349` / `91011387716`.
- Result: direct reconnect controls `2/2`; public-route fixture rejected before handler execution because it used obsolete wire method `mcpServer/refresh`.
- Correct current method: `config/mcpServer/reload`.
- Repaired run/job: `30589313367` / `91027881827`, queued at this update.
- Disposition: direct source behavior `target-executed`; app-server route pending.

### Deferred executable exposure

- Current source: `teamleaderleo/codex#81@8f73d8e0bb9a61e7dec7b1367d13649a88615dea`.
- Transferred receipt: `30580836079` / `91000366783`; exact planner controls `4/4`.
- Stack classifier: default worker stack reproduced the shared overflow; 16 MiB stack passed.
- Disposition: exposure invariant `target-executed` on identical source; current-head complete-diff review pending.
- Non-goals: Code Mode host discovery, MCP lifecycle, transport, routing, approval, or dispatch authority.

### Receipt wire, replay, and Responses Lite

These remain active independent candidates. They do not inherit acceptance from append acknowledgement, MCP publication, deferred exposure, or terminal retention. Their exact heads, controls, privacy boundaries, rollback behavior, and stack-pressure classifiers stay with their owning PRs and findings.

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

The workspace carries orientation, evidence notes, alternatives, prior art, canonical output candidates, and an exact handoff. This finding owns the current technical conclusion and transition state.

## Historical precedent

### ThreadStore and writer ownership

- Sources: openai/codex PRs #18882, #21874, #30669, #31155, and #27249.
- Principle supported: canonical append, metadata projection, writer generation, rotation, and cleanup have explicit owners and different completion points.
- Important difference: those changes do not expose the original result append outcome to the session caller.

### MCP runtime reconciliation and reconnect

- Sources: openai/codex PRs #34952, #35151, #30083, #31471, #31292, #31626, #34588, and #35590.
- Principle supported: managers own immutable published runtime state; ordinary reuse, explicit freshness, captured calls, targeted replacement, cached startup fallback, and shared reconnect work are distinct.
- Important difference: publication tickets, accepted-result identity, cached-only fallback, and active-call binding need separate controls.

### Responses Lite and standalone Code Mode host

- Sources: commits `33cc928d...`, `20fedaff...`, `97576b...`; upstream PRs #35271 and #36129.
- Principle supported: capability declarations, normalized identifiers, trace reconstruction, and executable host authority are distinct but related.
- Important difference: logical trace repair does not prove the first generated capability prefix reached the model, and historical in-core loader placement no longer owns execution.

### Unified execution retention

- Sources: openai/codex PRs #31802, #34713, and #36194.
- Principle supported: output is bounded, close/drain ordering matters, and invalid UTF-8 progress should be preserved.
- Important difference: best-effort subscribers should not define the producer's final retained transcript.

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
- Discriminating control: each candidate survives exact current-source execution and complete-diff review independently.
- Rollback boundary: retire or supersede individual outputs without discarding the shared model.

### Option B — One end-to-end mega-patch

- Artifact or branch: paper-only.
- Expected benefit: one apparent story from capability through persistence and output.
- Failure: mixes owners, evidence classes, compatibility surfaces, and rollback.
- Discriminating control: demonstrate one source owner and one test matrix can establish every claimed layer.
- Rollback boundary: broad, coupled revert.

### Option C — Independent findings with no synthesis layer

- Artifact or branch: historical issue/PR layout.
- Expected benefit: parallelism.
- Failure: readers cannot identify current relationships, overlap, or presentation status.
- Discriminating control: contradictory-state and orientation audit.
- Rollback boundary: retain findings and remove only the workspace index.

### Option D — Immediate single canonical answer

- Artifact or branch: paper-only.
- Expected benefit: simple communication.
- Failure: hides unresolved source ownership and technical comparisons.
- Discriminating control: every active candidate must first receive a settled disposition.
- Rollback boundary: supersede the output and restore alternatives.

## Comparative results

| Criterion | Option A | Option B | Option C | Option D | Winner or unresolved reason |
| --- | --- | --- | --- | --- | --- |
| Owner fidelity | strong | weak | strong | unclear | A/C |
| Reader orientation | strong | superficially strong | weak | strong but premature | A |
| Independent execution | strong | weak | strong | weak | A/C |
| Preserves disagreement and losing reasons | strong | weak | fragmented | weak | A |
| Current source readiness | partial but advancing | absent | partial | absent | A |
| Review and rollback scope | bounded | broad | bounded but fragmented | unclear | A |

## Independent criticism

| Reviewer or evidence source | Counterexample or criticism | Response or control | Effect on recommendation |
| --- | --- | --- | --- |
| PR #271 cross-review | Workspace links depended on an uncomposed canonical-findings branch | Compose the dependency stack in PR #283 | Strengthens A only as a composed stack |
| State-vocabulary audit | Comparative work could be mistaken for a human blocker | Define `comparative-evaluation-active` consistently | Keeps technical choices autonomous |
| Current source drift | Earlier public pins expired | Renew through `413492cd...` and compare complete changed-file sets | Refreshes current-source boundary |
| Carrier drift | #53 and #80 advanced from pending carriers to executed/exported source states | Reconcile F239 and add exact receipts | Prevents stale execution routing |
| MCP source precedent | Full live rebinding would discard captured ordinary-call authority | Retain captured-first execution and isolate cached-only fallback | Rejects the broad live-rebind direction |
| Terminal test seam | Helper-level tests required widened visibility | Exercise the real driver-backed production path instead | Preserves production privacy and strengthens evidence |

## Selected direction and losing reasons

Selected direction: Option A — one lifecycle model, several canonical findings and evidence notes, and several bounded proposal packets.

Why it wins: it preserves current ownership, supports technical comparison, gives readers a coherent map, and lets each candidate fail or succeed independently.

| Losing or deferred option | Reason it lost or moved elsewhere | Reopening trigger |
| --- | --- | --- |
| Mega-patch | Mixed authority and evidence; incompatible rollback | Current architecture consolidates owners and independent findings are accepted together |
| No synthesis | Durable facts remain hard to navigate and reconcile | Workspace proves more costly than useful after real adoption |
| Immediate single answer | Active route, replay, compatibility, and publication gates remain | Every candidate receives a settled disposition |
| Full live MCP rebinding | Conflicts with captured ordinary-call authority and failed before execution | Current source removes captured authority or a counterexample defeats isolated cached-only fallback |
| Helper-visible terminal tests | Widened production visibility for a test seam | Public behavior testing becomes impossible through the production constructor |

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Public source drift after terminal pin | `97576b... -> 413492...` complete compare | five commits; no active source-fence file overlap |
| Append pre-write failure and commit-then-error acknowledgement loss | run `30583967538` | exact controls and package passed; clean source published |
| Broadcast lag with text and invalid UTF-8 | run `30587866332` | retained producer transcript passed nine exact controls |
| Current deque/UTF-8 progress and compile compatibility | same terminal run | formatting and core library/integration compile gates passed |
| MCP publication generation rejection and winner gate | run `30584055792` | exact `5/5`; package passed |
| Captured authority versus cached-only live fallback | Fieldwork PR #290 and retired #79 | two-path direction retained; broad live rebind stopped |
| Explicit versus ordinary MCP refresh | first #82 run | direct controls passed `2/2` |
| Public reconnect route naming | first #82 run | obsolete method rejected before handler; corrected rerun queued |
| Deferred searchable versus unsearchable runtime exposure | run `30580836079` | four planner controls passed |
| Trace correctness versus first generated capability delivery | Responses Lite precedent | separate controls remain required |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Terminal Git-object materialization | behavior already executed; branch publication still pending | Codex #85 exact commit/tree verification |
| Current-head complete-diff review | file disjointness alone does not settle semantic compatibility | source PR review against `413492cd...` |
| Reconnect app-server route | corrected method rerun queued | Codex #82 run `30589313367` |
| MCP live slow-A/fast-B composition | publication primitive is narrower | dedicated MCP finding/candidate |
| Cached-only authority integration matrix | captured-first direction selected, source successor absent | Fieldwork PR #290 transition |
| Typed `Persisted/Ambiguous` result state | acknowledgement prerequisite completed | successor after #84 review |
| Receipt wire and rollback-aware replay | independent persistence/reconstruction owner | owned #73/#78 and dedicated finding |
| Responses Lite full request and retry behavior | independent request/trace owner | owned #58/#71 and campaign #85 |
| Hard process termination, Windows containment, restart reattachment | separate lifecycle owners | dedicated process findings |
| Public proposal packaging | no authorization and gates incomplete | explicit delivery/upstream request |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/codex#80@401c2e5...` | run `30583967538`, job `91010830120` | owned exact-pin carrier | four exact append controls, thread-store package, source publication passed | `target-executed` |
| `teamleaderleo/codex#84@d8299b7...` | clean source successor | exact parent `a01a2d...` | source published; current-head review pending | source-only |
| `teamleaderleo/codex#53@c4e0de2...` | Fieldwork run `30587866332`, job `91023382172` | Ubuntu 22.04, Rust 1.95, repository entrypoints | nine exact controls, compile gates, source export passed | `target-executed` |
| terminal source `8c7ea384...` | materialization run `30589829555` via #85 | owned exact Git object | pending at update | publication pending |
| `teamleaderleo/codex#75@c3373c7...` | run `30584055792`, job `91011123543` | exact current-pin publication carrier | exact `5/5`, complete package passed | `target-executed` |
| `teamleaderleo/codex#76@7e9d80c...` / #82 | run `30584136349`, job `91011387716` | direct and app-server fixture | direct `2/2`; obsolete route rejected before handler | split evidence |
| same reconnect source | repaired run `30589313367`, job `91027881827` | corrected `config/mcpServer/reload` | queued at update | route pending |
| `teamleaderleo/codex#81@8f73d8e...` | transferred run `30580836079`, job `91000366783` | identical current source | planner `4/4`; stack classifier retained | `target-executed` |
| `openai/codex@413492cd...` | compare from `97576b...` | read-only GitHub source | five commits; no named active source-fence overlap | `source-read` |

## Complete-diff and compatibility review

- Canonical-findings protocol and workspace are composed in Fieldwork PR #283.
- This reconciliation is proposed on a separate branch from exact PR #283 head `c2946c71b7330b74d326deb7af18a5ae55afce99`.
- Append, terminal, publication, reconnect, and deferred source proposals remain independently reviewable.
- Execution carriers grant no product acceptance and close only after evidence and successor transfer.
- Current compatibility surfaces include the standalone Code Mode host, MCP captured-call and cached-startup paths, manager snapshots/reconnect, ThreadStore writer generations, rollout reconciliation, unified-exec deque and lifecycle ordering, and Windows sandbox policy.
- File-disjoint public drift supports renewed review; it does not create proposal readiness by itself.
- Exact-head review of PR #283 and this reconciliation remains required.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`.
- Review disposition: `COMPARE, REVIEW CURRENT SOURCE, AND MATERIALIZE`.
- Review Queue entry: none.
- Delivery lane: `not-entered`.
- Exact next transition: verify terminal materialization, settle reconnect route execution, complete current-head reviews for the bounded source PRs, and split accepted candidates into dedicated canonical findings or stopped records.
- Clearing condition: every current and historical candidate has a current-source disposition, canonical finding or stopped record, exact receipt, and carrier successor/retirement state.
- Required subgates: current-source overlap, exact tests, complete diff, compatibility, source-only publication, independent review, and carrier cleanup.
- Autonomous work remaining: execution, current-head review, source maps, comparative prototypes, finding materialization, and cleanup.
- Non-delegable human decision: none currently.

## Changes to the canonical conclusion

| Date | Pull request, commit, or receipt | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | PR #266 | Created one workspace and selected bounded outputs over a mega-patch |
| 2026-07-31 | PR #271 review | Identified missing canonical-findings dependency and state-vocabulary contradiction |
| 2026-07-31 | PR #283 composition | Added the missing dependency, canonical finding, comparative state, and refreshed source/carrier identities |
| 2026-07-31 | append run `30583967538` and source #84 | Moved append acknowledgement from pending execution to target-executed clean source |
| 2026-07-31 | terminal run `30587866332` and export `8c7ea384...` | Moved terminal retention from pending to target-executed exact source, with materialization pending |
| 2026-07-31 | publication run `30584055792` and PR #290 | Recorded publication `5/5`, retired broad live rebinding, and selected captured-first authority with cached-only fallback |
| 2026-07-31 | public source `413492cd...` | Renewed the source fence through five file-disjoint commits |
| 2026-07-31 | this reconciliation | Replaced stale pending states with exact outcomes, limits, losing reasons, and next gates |

## References

- Fieldwork issues #239, #254, #289, and campaign issues linked from the workspace.
- Fieldwork PRs #283 and #290.
- Evidence note `evidence/20260731-current-evidence-reconciliation.md`.
- `investigations/239-codex-upstream-convergence/`.
- Owned Codex PRs #53, #58, #71, #73, #75, #76, #78, #80, #81, #82, #84, and #85.
- Retired carriers #77 and #79 preserve their receipts and losing reasons.
- Public Codex source through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`, read-only.
- Public upstream interaction: none.
