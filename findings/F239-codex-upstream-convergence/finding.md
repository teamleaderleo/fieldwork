# F239-codex-upstream-convergence: Separate Codex tool continuity into reviewable ownership boundaries

Finding state: `comparative-evaluation-active`

Workstream: `J/O/I — current-source convergence, synthesis, and cross-repository audit`  
Canonical Fieldwork issue: `#239`  
Canonical finding path: `findings/F239-codex-upstream-convergence/finding.md`  
Investigation workspace: `investigations/239-codex-upstream-convergence/`  
Canonical implementation or alternatives: `several bounded owned Codex candidates; no combined implementation`  
Exact active heads: `append #80@401c2e5e6a37730aae3e8da95591cc6f56655cfc; terminal Fieldwork #268@58c0d027e2acf80fb9e16d89d0daba65de0dc563; MCP publication #77@0fb2e6b09a6ff03bcfcbd665b187cadb64d36b4b; MCP reconnect #82@fee6e8350673b2fb87841dfb7b96d3c2ea8def0d; MCP authority #79@40ad25450b9b1296906b66126b710ea877dc7e82; other current candidates named below`  
Exact base or source revision: `openai/codex@413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Strongest evidence class: `target-executed` for current-pin append, bounded terminal retention, and MCP publication; other current candidates remain executing or queued  
Reviewed input generation: `read-only public source snapshot, exact carrier heads, complete workspace evidence map, Codex CI prerequisite map`  
Current review disposition: `EXECUTE, MATERIALIZE, and COMPARE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Codex tells a model which tools exist, chooses a runtime, sends a call, waits or cancels, reports a result, stores history, and later reconstructs that history. Those steps are connected, but they are not one state machine.

A tool can be visible without matching executable authority. A timeout can occur while a remote effect still finishes. A result can reach live conversation memory while durable append fails. A subprocess can produce bytes before a late listener subscribes.

The selected direction is one shared lifecycle explanation plus several bounded technical findings and source candidates. Current execution has now cleared the append prerequisite, bounded terminal-retention controls, and MCP publication controls. Reconnect, live authority, replay, typed identity, Responses Lite, and deferred discovery remain at separate gates. One mega-patch would mix unrelated authority, execution, persistence, replay, and output contracts.

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
- carrier failures being mistaken for product failures when required repository tools or current source anchors are missing.

Frequency and aggregate user impact are not measured. Each consequence remains limited to its exact source and execution record.

## Governing goals and invariant

Governing invariant: every state transition must preserve the identity, authority, and certainty facts owned at that boundary without treating success in another layer as equivalent proof.

| Goal or contract | Primary source | Consequence for the design |
| --- | --- | --- |
| Model-visible tools have executable authority | request construction, Code Mode host, MCP snapshots | declaration and dispatch share a captured identity |
| Current runtime publication cannot regress | MCP manager and refresh work | only an eligible generation publishes; active calls keep captured binding |
| Cancellation is not remote-effect settlement | Fieldwork #134/#162 and current MCP ownership | retain deadline, delivery, transport, and effect certainty separately |
| Model-visible result and durable append are separate | current session / `LiveThread` / `ThreadStore` path | append acknowledgement becomes an explicit fact |
| History readers consume conservative persistence facts | rollout, projection, compaction, resume, fork | ambiguous append cannot authorize unsafe retry or cleanup |
| Terminal completion uses non-lossy retained input | unified execution producer and bounded buffer | retain before best-effort broadcast and preserve current deque behavior |
| Historical execution does not imply current portability | Fieldwork exact-head policy | current claims need current source, diff, tests, and overlap review |
| Carrier setup follows target entrypoints | current Codex workflows, `setup-ci`, root `justfile`, and `scripts/format.py` | missing `just`, `uv`, nextest, or a current source anchor is harness evidence only |

## Current finding

The Codex portfolio should remain separated into independently reviewable findings and proposal packets.

The shared lifecycle model is useful for orientation. It does not authorize a combined source change. Current source ownership and rollback boundaries support these independent areas:

1. model-visible capability and deferred executable authority;
2. MCP refresh freshness and generation publication;
3. prepared or active call runtime binding;
4. operation timeout, cancellation, transport, and remote-effect certainty;
5. live result formation and durable append acknowledgement;
6. receipt wire, typed identity, history projection, compaction, resume, fork, rollback, and replay;
7. producer-owned terminal transcript retention;
8. evidence-carrier setup, retirement, and canonical-source transfer.

### Claim table

| Claim | Evidence class | Exact support | Current limit |
| --- | --- | --- | --- |
| One mega-patch crosses several state owners and rollback boundaries | `source-read` | workspace problem map and public Codex at `413492cd...` | Later composition remains possible after independent acceptance |
| Current session append path needs caller-visible acknowledgement | `source-read` plus `target-executed` | owned Codex #51/#80; run `30583967538` passed | Clean source successor, current-head relation, and complete-diff review remain |
| Terminal producer-owned retention survives current deque behavior | `source-read` plus `target-executed` | owned Codex #49/#53 and Fieldwork #268; run `30587866332` passed | Artifact/source materialization, integrity, and independent source review remain |
| MCP newest-generation publication remains an independent invariant | `source-read` plus `target-executed` | owned Codex #75/#77; run `30584055792` passed | Source-only publication and current-head review remain |
| Explicit reconnect overlaps historical #46 but still needs live request-path proof | `source-read` plus execution in progress | upstream #34952/#35151; owned #76/#82 | Run `30584136349` was in progress at refresh |
| Model-advertised versus live MCP authority needs a captured comparison | `source-read`; carrier repair queued | owned #79; failed run `30584093534`; repair `40ad2545...` | Repaired exact run `30588729054` queued |
| Current public head moved to `413492cd...` without active-fence overlap | `source-read` | compare `3016671... → 413492...`; permission/sandbox files only | A later relevant commit expires this carry-forward |
| Deferred-tool authority has a current source candidate and mixed-catalogue gate | `source-read`; execution queued | source #81 at `8f73d8e...`; carrier #64 at `c09a94d...` | Run `30584556260` queued |
| Responses Lite capability-prefix behavior remains separate from trace correctness | `source-read`; execution in progress | owned #58 at `40a56eef...` | Run `30584165709` in progress |
| Codex full formatting requires explicit `uv` outside `setup-ci` | `source-read` plus carrier failure | current upstream repo checks, root entrypoints, PR #53 run `30582012412` | Exact versions must be refreshed from the inspected target revision |

## System and ownership map

```text
model-visible capability manifest
→ captured runtime generation and authority
→ operation identity and dispatch
→ local or remote execution
→ caller deadline, cancellation, transport, and effect settlement
→ model-visible result
→ durable append acknowledgement
→ receipt replay, history projection, compaction, resume, fork, and rollback
```

Subprocess output has a parallel chain:

```text
process output producer
→ bounded retained transcript
→ best-effort live broadcast
→ terminal completion item
```

The workspace carries orientation, evidence notes, alternatives, prior art, audience-specific outputs, and an exact handoff. This finding owns the present technical conclusion and transition state.

## Historical precedent

### ThreadStore and writer ownership

- Sources: openai/codex PRs #18882, #21874, #30669, #31155, and #27249.
- Principle supported: canonical append, metadata projection, writer generation, rotation, and cleanup have explicit owners and different completion points.
- Important difference: those changes do not expose the original result append outcome to the session caller.

### MCP runtime reconciliation and reconnect

- Sources: openai/codex PRs #34952, #35151, #30083, #31471, #31292, and #31626.
- Principle supported: managers own immutable published runtime state; ordinary reuse, explicit freshness, targeted replacement, request-stable snapshots, and shared reconnect work are distinct.
- Important difference: newest-generation publication, accepted-result identity, and captured active-call authority require their own exact controls.

### Responses Lite and standalone Code Mode host

- Sources: commits `33cc928d...`, `20fedaff...`, `97576b...`; openai/codex PRs #35271 and #36129.
- Principle supported: capability declarations, normalized identifiers, trace reconstruction, and executable host authority are distinct but related.
- Important difference: logical trace repair does not prove the first generated capability prefix reached the model.

### Unified execution retention

- Sources: openai/codex PRs #31802, #34713, and #36194.
- Principle supported: output is bounded, close/drain ordering is consequential, and invalid UTF-8 progress should be preserved.
- Important difference: best-effort subscribers still should not define the producer's final retained transcript.

### Repository CI prerequisites

- Sources: current public `.github/actions/setup-ci/action.yml`, `.github/workflows/repo-checks.yml`, root `justfile`, and `scripts/format.py`.
- Principle supported: repository entrypoints define their complete environment; a shared setup action can intentionally install only part of it.
- Important difference: Fieldwork carriers select narrower commands and must derive the required subset at an exact target revision.

The full precedent ledger is `investigations/239-codex-upstream-convergence/precedent/fieldwork-and-upstream-prior-art.md`. The exact CI prerequisite receipt is `evidence/20260731-codex-ci-prerequisites.md` in this finding directory.

## Decision criteria

| Priority | Criterion | How it will be measured or falsified |
| --- | --- | --- |
| 1 | Correct owner | exact source path and state owner for each invariant |
| 2 | Independent falsifiability | controls that reject one candidate without relying on unrelated layers |
| 3 | Current-source compatibility | exact public pin, overlap map, and complete current diff |
| 4 | Conservative authority | no retry, compaction, publication, or cleanup inferred from weaker evidence |
| 5 | Target-native execution | current repository entrypoints with complete declared prerequisites |
| 6 | Rollback and carrier hygiene | source-only successor, immutable receipts, temporary workflow retirement |
| 7 | Reader clarity | one canonical finding and workspace map without reconstructing issue chronology |

## Alternatives instantiated or analyzed

### Option A — One lifecycle model plus bounded technical findings

- Artifact or branch: this finding and the #239 workspace.
- Invariant implemented: shared orientation without merging independent source authority.
- Expected benefit: clear review scope, independent execution, and reusable negative results.
- Expected cost: more records and coordination.
- Discriminating control: each candidate survives exact current-source execution and complete-diff review.
- Rollback boundary: retire or supersede individual outputs without discarding the shared model.

### Option B — One end-to-end mega-patch

- Artifact or branch: paper-only.
- Expected benefit: apparent end-to-end coherence.
- Failure: mixes owners, evidence classes, compatibility surfaces, and rollback.
- Discriminating control: demonstrate one source owner and one test matrix can establish every claimed layer.
- Rollback boundary: broad coupled revert.

### Option C — Independent findings with no synthesis layer

- Artifact or branch: historical issue/PR layout.
- Expected benefit: maximal source-level separation.
- Failure: readers cannot identify current relationships, overlap, or presentation status.
- Discriminating control: orientation and contradictory-state audit.
- Rollback boundary: retain findings and remove workspace index.

### Option D — One new issue for every intermediate observation

- Artifact or branch: paper-only.
- Expected benefit: obvious ownership.
- Failure: duplicates existing campaigns, repeats background, and creates coordination overhead before a bounded proposal is actionable.
- Discriminating control: promote only after a finding owns one implementation or one independently reviewable proposal packet.
- Rollback boundary: close duplicate issue with successor mapping.

## Comparative results

| Criterion | Option A | Option B | Option C | Option D | Winner or unresolved reason |
| --- | --- | --- | --- | --- | --- |
| Owner fidelity | strong | weak | strong | strong but fragmented | A/C |
| Reader orientation | strong | superficially strong | weak | weak across many issues | A |
| Independent execution | strong | weak | strong | strong | A/C/D |
| Preserves disagreement | strong | weak | weakly visible | visible but dispersed | A |
| Current source readiness | partial with several green gates | absent | partial | premature for some packets | A |
| Review and rollback scope | bounded | broad | bounded but fragmented | bounded with issue overhead | A |

## Independent criticism

| Reviewer or evidence source | Counterexample or criticism | Response or new control | Effect on recommendation |
| --- | --- | --- | --- |
| PR #271 cross-review | Workspace links depended on an uncomposed canonical-findings branch | Compose canonical findings, decisions, and workspaces in PR #283 | Strengthens Option A only as a composed protocol |
| State-vocabulary audit | `comparative-evaluation-active` was missing from governing tables | Define it consistently and keep it off the human decision desk | Makes current #239 state explicit |
| Protocol discussion gap | PR #283 had no obvious issue for broad review | Open Fieldwork #289 as the protocol-review surface | Gives the proposal a durable invitation and decision record |
| Current source drift | Public head advanced through `413492cd...` | Compare every new delta and preserve source-fence expiry | Keeps present-tense claims bounded |
| Carrier prerequisite failure | `setup-ci` installed `just` but full formatting still failed without `uv` | Add target-map guidance and an exact evidence note | Prevents repeated harness failures and false product conclusions |
| MCP authority carrier drift | Generator anchor matched two current locations | Narrow anchor to the `handle_mcp_tool_call` parse boundary | Preserves candidate semantics and renews execution |

## Selected direction and losing reasons

Selected direction: Option A — one lifecycle model, several canonical findings and evidence notes, and several bounded proposal packets.

Why it wins: it preserves current ownership, supports technical comparison, gives readers a coherent map, and lets each source candidate fail or succeed independently.

| Losing or deferred option | Reason it lost or moved elsewhere | Reopening trigger |
| --- | --- | --- |
| Mega-patch | Mixed authority and evidence; incompatible rollback | Current architecture consolidates owners and independent findings are accepted together |
| No synthesis | Durable facts remain difficult to navigate and reconcile | Workspace proves more costly than useful after real adoption |
| Immediate single answer | Current carriers and source-owner comparisons remain open | Every candidate receives a settled disposition |
| Issue per intermediate result | Existing campaigns already own the work and several packets remain unmaterialized | A bounded packet gains one owner, current source, exact evidence, and independent actionability |

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Public source drift after canonical pin | `3016671... → 413492...` complete compare | only Windows permission/sandbox files changed; active candidate fences unchanged |
| Append historical versus current-pin execution | #51/#52 and current-pin #80 | current-pin append run `30583967538` passed |
| Terminal historical patch versus current deque behavior | #49/#53 and Fieldwork #268 | bounded current-source run `30587866332` passed |
| Overlapping MCP publication | #75/#77 | exact publication run `30584055792` passed |
| Explicit versus ordinary MCP refresh | upstream #34952/#35151 and #76/#82 | live app-server execution remained in progress at refresh |
| Advertised versus live MCP authority | #79 | old generator failed before source; repair run queued |
| Trace correctness versus capability delivery | Responses Lite precedent and #58 | separate exact-source controls running |
| Live result versus durable append | session/ThreadStore source map and #80 | append prerequisite executed; typed result state remains separate |
| Broadcast versus completion transcript | unified-exec source map and #268 | producer retention executed under bounded gates |
| Missing `just`, `uv`, or nextest | Codex target map and CI prerequisite evidence note | classified as carrier failures; required setup recorded |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Current MCP reconnect source acceptance | live app-server run and source publication pending | #82 and successor source review |
| Prepared-call authority acceptance | repaired carrier queued | #79 and dedicated MCP authority finding after execution |
| Typed `Persisted/Ambiguous` result state | append acknowledgement prerequisite first | successor after #80 source review |
| Receipt replay and typed identity | separate wire/replay owners and gates | #73/#74/#78/#83 |
| Remote mutation replay | unsafe while outcome unknown | MCP operation finding |
| Hard process termination, Windows containment, restart reattachment | separate lifecycle owners | dedicated process findings |
| Public proposal packaging | no authorization and several current gates incomplete | explicit delivery/upstream request |

## Exact execution and receipts

| Repository/head | Command or workflow | Result at refresh | Evidence class |
| --- | --- | --- | --- |
| `teamleaderleo/codex#80@401c2e5...` | run `30583967538` | success | `target-executed` append prerequisite |
| `teamleaderleo/fieldwork#268@58c0d027...` | run `30587866332` | success | `target-executed` bounded terminal retention |
| `teamleaderleo/codex#77@0fb2e6b...` | run `30584055792` | success | `target-executed` MCP publication |
| `teamleaderleo/codex#82@fee6e83...` | run `30584136349` | in progress | execution pending for app-server reconnect |
| `teamleaderleo/codex#79@d96bcf0...` | run `30584093534`, job `91011250342` | generator failed before source; superseded | carrier-only |
| `teamleaderleo/codex#79@40ad254...` | run `30588729054` | queued | authority execution pending |
| `teamleaderleo/codex#78@e156bef...` | run `30584251271` | in progress | replay execution pending |
| `teamleaderleo/codex#83@78fd39e...` | run `30584411308` | queued | typed-identity execution pending |
| `teamleaderleo/codex#58@40a56ee...` | run `30584165709` | in progress | Responses Lite execution pending |
| `teamleaderleo/codex#64@c09a94d...` | run `30584556260` | queued | deferred mixed-catalogue execution pending |
| `openai/codex@413492cd...` | compare from `3016671...` | one Windows permission-normalization commit; no active-fence overlap | `source-read` |

Broad repository workflows such as `blocking-ci`, Fieldwork integrity, artifact review, and source-only materialization remain separate gates. A green bounded carrier does not by itself accept or merge source.

## Complete-diff and compatibility review

- Canonical findings, autonomous comparison, and investigation workspaces are composed in Fieldwork PR #283.
- Fieldwork issue #289 is the protocol discussion and review surface.
- This CI-prerequisite and current-state refresh is stacked on PR #283 so the canonical finding changes with its evidence.
- Append, terminal, MCP, Responses Lite, and receipt workflows remain execution machinery and require source-only successors plus retirement receipts.
- Current compatibility surfaces: standalone Code Mode host, MCP manager snapshots/reconnect, prepared-call authority, ThreadStore writer generations, rollout reconciliation, unified-exec deque and lifecycle ordering, and target workflow prerequisites.
- Exact-head review of each source successor remains required.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `EXECUTE, MATERIALIZE, and COMPARE`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: materialize and independently review append, terminal, and MCP-publication source successors; settle reconnect, authority, Responses Lite, replay, typed identity, and deferred mixed-catalogue gates; then split accepted bounded technical findings or stopped records.
- Clearing condition: every current and historical candidate has a current-source disposition, canonical finding or stopped record, exact receipt, and carrier successor/retirement state.
- Required subgates: current-source overlap, exact tests, complete diff, compatibility, source-only publication, independent review.
- Autonomous work remaining: execution, source materialization, comparative review, canonical finding splits, and carrier cleanup.
- Non-delegable human decision: none currently.

## Issue and proposal packaging

Issue #239 remains the portfolio command surface and this file remains the meta-analysis finding. Do not replace it with one public-style mega-issue.

Create or reuse separate technical issues only when a packet becomes independently actionable: one bounded invariant, one current source owner, one implementation or explicit design comparison, exact evidence, and one review transition. Existing campaign issues #83, #84, #85, and #134 remain the current technical owners. New duplicate issues would add routing work before the packets are ready.

The closest candidates for later standalone proposal drafts are append acknowledgement, terminal producer-owned retention, and MCP publication because their current exact controls are green. They still need source-only materialization and complete-diff review before the draft can claim a current implementation.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | PR #266 | Created one workspace and selected bounded outputs over a mega-patch |
| 2026-07-31 | PR #271 review | Identified missing canonical-findings dependency and state-vocabulary contradiction |
| 2026-07-31 | PR #283 | Composed the protocol, canonical finding, comparative state, and refreshed source/carrier identities |
| 2026-07-31 | current stacked refresh | Recorded Codex CI prerequisites, public head `413492cd...`, green append/terminal/publication gates, and repaired MCP authority execution |

## References

- Fieldwork issues #239, #254, and protocol review #289.
- Fieldwork PRs #268 and #283.
- `investigations/239-codex-upstream-convergence/`.
- `targets/codex/map.md`.
- `findings/F239-codex-upstream-convergence/evidence/20260731-codex-ci-prerequisites.md`.
- Owned Codex PRs #51, #52, #53, #58, #64, #73–#83.
- Public Codex source through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`, read-only.
- Public upstream interaction: none.
