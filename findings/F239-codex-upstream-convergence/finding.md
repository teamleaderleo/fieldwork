# F239-codex-upstream-convergence: Separate Codex tool continuity into reviewable ownership boundaries

Finding state: `comparative-evaluation-active`

Workstream: `J/O/I — current-source convergence, synthesis, and cross-repository audit`  
Canonical Fieldwork issue: `#239`  
Canonical finding path: `findings/F239-codex-upstream-convergence/finding.md`  
Investigation workspace: `investigations/239-codex-upstream-convergence/`  
Canonical implementation or alternatives: `several bounded Codex findings and owned candidates; no combined implementation`  
Exact active heads: `append source #84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2; terminal artifact source 8c7ea38419d790032db459816980e6b4dd38f574; MCP publication #75@c3373c717f3138ff5f0a979d12836f60800d2bcf; MCP reconnect carrier #82@feb0c46d3b88e03c94cb9f07d6ba903205e73f05; MCP authority #79@40ad25450b9b1296906b66126b710ea877dc7e82; other current candidates named below`  
Exact base or source revision: `openai/codex@413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Strongest evidence class: `target-executed` for current-pin append, bounded terminal retention, and MCP publication; other current candidates remain executing or queued  
Reviewed input generation: `read-only public source snapshot, exact carrier/source heads, split canonical findings, complete workspace evidence map, Codex CI prerequisite map`  
Current review disposition: `EXECUTE, MATERIALIZE, SPLIT, and COMPARE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Codex tells a model which tools exist, chooses a runtime, sends a call, waits or cancels, reports a result, stores history, and later reconstructs that history. Those steps are connected, but they are not one state machine.

A tool can be visible without matching executable authority. A timeout can occur while a remote effect still finishes. A result can reach live conversation memory while durable append fails. A subprocess can produce bytes before a late listener subscribes.

The selected direction is one shared lifecycle explanation plus several bounded technical findings and source candidates. Current execution and review have now separated three packets into their own canonical findings:

- `F83-codex-append-acknowledgement`;
- `F84-codex-mcp-publication-generation`;
- `F23-codex-terminal-producer-retention`.

Reconnect, live authority, replay, typed identity, Responses Lite, deferred discovery, and operation settlement remain at separate gates. One mega-patch would mix unrelated authority, execution, persistence, replay, and output contracts.

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
- carrier failures being mistaken for product failures when required repository tools, current API names, or source anchors are missing;
- executed source remaining unavailable for review because artifact publication and Git materialization were treated as the same event.

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
| Carrier setup follows target entrypoints | current Codex workflows, `setup-ci`, root `justfile`, and `scripts/format.py` | missing `just`, `uv`, nextest, a current method name, or a unique source anchor is harness evidence only |
| Execution artifact and source branch are separate publication facts | Fieldwork carrier and Git review rules | verify artifact, materialize exact tree, then open source review |

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
8. evidence-carrier setup, artifact verification, Git materialization, retirement, and canonical-source transfer.

### Current split findings

| Canonical finding | State | Accepted conclusion | Exact remaining gate |
| --- | --- | --- | --- |
| `findings/F83-codex-append-acknowledgement/finding.md` | `delivery-gate-ready` | return bounded append acknowledgement to Session caller | direct-current-head packaging and carrier retirement |
| `findings/F84-codex-mcp-publication-generation/finding.md` | `delivery-gate-ready` | generation/freshness ticket owns publication winner | slow-older/fast-newer complete runtime fixture |
| `findings/F23-codex-terminal-producer-retention/finding.md` | `delivery-gate-ready` | completion uses producer-owned bounded transcript | exact artifact-to-owned-Git source materialization |

### Claim table

| Claim | Evidence class | Exact support | Current limit |
| --- | --- | --- | --- |
| One mega-patch crosses several state owners and rollback boundaries | `source-read` | workspace problem map and public Codex at `413492cd...` | Later composition remains possible after independent acceptance |
| Append acknowledgement is a supported bounded prerequisite | `target-executed` plus independent review | #80 run `30583967538`; source #84 review `4823945751`; F83 | Typed persistence and current-head packaging remain |
| Terminal producer retention is supported under bounded normal-close gates | `target-executed` plus artifact review | Fieldwork #268 run `30587866332`; artifact `8777460316`; F23 | Owned Git source commit is absent |
| MCP publication generation is a supported manager invariant | `target-executed` plus independent review | #77 run `30584055792`; source #75 review `4823972975`; F84 | Complete overlapping runtime fixture remains |
| Explicit reconnect source still requires its public app-server path | `source-read`; repaired execution queued | upstream #34952/#35151; #82 | Old run used nonexistent wire method; new run `30589313367` queued |
| Model-advertised versus live MCP authority needs a captured comparison | `source-read`; carrier repair queued | #79; failed run `30584093534`; repair `40ad2545...` | Repaired run `30588729054` queued |
| Current public head moved to `413492cd...` without active-fence overlap | `source-read` | complete public compare | A later relevant commit expires this carry-forward |
| Deferred-tool authority has a current source candidate and mixed-catalogue gate | `source-read`; execution queued | source #81 at `8f73d8e...`; carrier #64 at `c09a94d...` | Run `30584556260` queued |
| Responses Lite capability-prefix behavior remains separate from trace correctness | `source-read`; execution in progress | #58 at `40a56eef...` | Run `30584165709` in progress at refresh |
| Codex full formatting requires explicit `uv` outside `setup-ci` | `source-read` plus carrier failure | current public repo checks, root entrypoints, #53 run `30582012412` | Exact versions refresh from inspected target revision |

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

The workspace carries orientation, evidence notes, alternatives, prior art, audience-specific outputs, and an exact handoff. This finding owns portfolio synthesis and routes bounded conclusions to their canonical technical findings.

## Historical precedent

### ThreadStore and writer ownership

- Sources: openai/codex PRs #18882, #21874, #30669, #31155, and #27249.
- Principle supported: canonical append, metadata projection, writer generation, rotation, and cleanup have explicit owners and different completion points.
- Important difference: those changes do not expose the original result append outcome to the session caller.

### MCP runtime reconciliation and reconnect

- Sources: openai/codex PRs #34952, #35151, #30083, #31471, #31292, and #31626.
- Principle supported: managers own immutable published runtime state; ordinary reuse, explicit freshness, targeted replacement, request-stable snapshots, and shared reconnect work are distinct.
- Important difference: newest-generation publication, accepted-result identity, and captured active-call authority require separate controls.

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
| 6 | Artifact-to-source integrity | exact parent, tree, files, patch, checksums, and owned branch identity |
| 7 | Rollback and carrier hygiene | source-only successor, immutable receipts, temporary workflow retirement |
| 8 | Reader clarity | meta finding plus bounded canonical findings without reconstructing issue chronology |

## Alternatives instantiated or analyzed

### Option A — One lifecycle model plus bounded technical findings

- Artifact: F239 workspace plus F83, F84, F23, and later splits.
- Benefit: clear review scope, independent execution, reusable negative results, and issue stability.
- Cost: more records and explicit routing.
- Discriminating control: each candidate survives exact current-source execution and complete-diff review.
- Rollback: retire or supersede individual findings without discarding the shared model.

### Option B — One end-to-end mega-patch or mega-issue

- Benefit: apparent end-to-end coherence.
- Failure: mixes owners, evidence classes, compatibility surfaces, and rollback.
- Discriminating control: demonstrate one source owner and test matrix can establish every claimed layer.
- Rollback: broad coupled revert or issue rewrite.

### Option C — Independent findings with no synthesis layer

- Benefit: maximal source-level separation.
- Failure: readers cannot identify current relationships, overlap, or presentation status.
- Discriminating control: orientation and contradictory-state audit.
- Rollback: retain findings and remove workspace index.

### Option D — One new issue for every intermediate observation

- Benefit: obvious ownership.
- Failure: duplicates existing campaigns, repeats background, and creates coordination overhead before a bounded proposal is actionable.
- Discriminating control: promote only after a finding owns one implementation or one independently reviewable proposal packet.
- Rollback: close duplicate issue with successor mapping.

## Comparative results

| Criterion | Option A | Option B | Option C | Option D | Winner or unresolved reason |
| --- | --- | --- | --- | --- | --- |
| Owner fidelity | strong | weak | strong | strong but fragmented | A/C |
| Reader orientation | strong | superficially strong | weak | weak across many issues | A |
| Independent execution | strong | weak | strong | strong | A/C/D |
| Preserves disagreement | strong | weak | weakly visible | visible but dispersed | A |
| Current source readiness | partial with three split findings | absent | partial | premature for remaining packets | A |
| Review and rollback scope | bounded | broad | bounded but fragmented | bounded with issue overhead | A |

## Independent criticism

| Reviewer or evidence source | Counterexample or criticism | Response or new control | Effect on recommendation |
| --- | --- | --- | --- |
| PR #271 cross-review | Workspace links depended on an uncomposed canonical-findings branch | Compose canonical findings, decisions, and workspaces in PR #283 | Strengthens Option A only as a composed protocol |
| State-vocabulary audit | `comparative-evaluation-active` was missing from governing tables | Define it consistently and keep it off the human decision desk | Makes current #239 state explicit |
| Protocol discussion gap | PR #283 had no obvious issue for broad review | Open Fieldwork #289 as the protocol-review surface | Gives the proposal a durable invitation and decision record |
| Current source drift | Public head advanced through `413492cd...` | Compare every new delta and preserve source-fence expiry | Keeps present-tense claims bounded |
| Carrier prerequisite failure | `setup-ci` installed `just` but full formatting still failed without `uv` | Add target-map guidance and exact evidence note | Prevents repeated harness failures and false product conclusions |
| MCP authority carrier drift | Generator anchor matched two current locations | Narrow anchor to `handle_mcp_tool_call` parse boundary | Preserves candidate semantics and renews execution |
| App-server reconnect control | Test used nonexistent `mcpServer/refresh` | Use current typed wire method `config/mcpServer/reload`; rerun queued | Separates request-harness error from reconnect behavior |
| Terminal materialization check | Intended branch existed but remained identical to base | Verify artifact and require exact Git tree before source PR | Prevents artifact success from becoming a false source claim |

## Selected direction and losing reasons

Selected direction: Option A — one lifecycle model, bounded canonical findings and evidence notes, and several proposal packets under existing owner issues.

Why it wins: it preserves current ownership, supports technical comparison, gives readers a coherent map, and lets each source candidate fail or succeed independently.

| Losing or deferred option | Reason it lost or moved elsewhere | Reopening trigger |
| --- | --- | --- |
| Mega-patch or mega-issue | Mixed authority and evidence; incompatible rollback | Current architecture consolidates owners and findings are accepted together |
| No synthesis | Durable facts remain difficult to navigate and reconcile | Workspace proves more costly than useful after real adoption |
| Immediate single answer | Current carriers and source-owner comparisons remain open | Every candidate receives a settled disposition |
| Issue per intermediate result | Existing campaigns already own the work and several packets remain unmaterialized | A bounded packet lacks an existing owner and gains current source plus exact evidence |

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Public source drift after canonical pin | complete compare through `413492cd...` | active candidate fences unchanged |
| Append historical versus current-pin execution | #51/#52/#80/#84 and F83 | source prerequisite accepted; current-head packaging remains |
| Terminal historical patch versus current deque behavior | #49/#53/#268 artifact and F23 | target behavior accepted; Git materialization remains |
| Overlapping MCP publication | #75/#77 and F84 | manager publication invariant accepted; full runtime fixture remains |
| Explicit versus ordinary MCP refresh | upstream #34952/#35151 and #76/#82 | old app-server method rejected; corrected run queued |
| Advertised versus live MCP authority | #79 | old generator failed before source; repaired run queued |
| Trace correctness versus capability delivery | Responses Lite precedent and #58 | separate controls remain active |
| Live result versus durable append | Session/ThreadStore source map and F83 | append prerequisite split; typed result state remains separate |
| Broadcast versus completion transcript | unified-exec source map and F23 | producer retention executed under bounded gates |
| Missing `just`, `uv`, nextest, or current method | target map and CI evidence note | classified as carrier failures; prerequisites recorded |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Current MCP reconnect acceptance | corrected app-server run pending | #82 and later reconnect finding |
| Prepared-call authority acceptance | repaired carrier queued | #79 and later MCP authority finding |
| Typed `Persisted/Ambiguous` result state | append prerequisite accepted first | successor F83 finding |
| Receipt replay and typed identity | separate wire/replay owners and gates | #73/#74/#78/#83 |
| Remote mutation replay | unsafe while outcome unknown | MCP operation finding |
| Hard process termination, Windows containment, restart reattachment | separate lifecycle owners | dedicated process findings |
| Public proposal packaging | no authorization and current gates incomplete | explicit delivery/upstream request |

## Exact execution and receipts

| Repository/head | Command or workflow | Result at refresh | Evidence class |
| --- | --- | --- | --- |
| `teamleaderleo/codex#80@401c2e5...` | run `30583967538` | success | `target-executed` append prerequisite |
| `teamleaderleo/codex#84@d8299b7...` | review `4823945751` | bounded source accepted | independent source review |
| `teamleaderleo/fieldwork#268@58c0d027...` | run `30587866332` | success | `target-executed` bounded terminal retention |
| artifact `8777460316` | checksum/tree inspection | verified; owned source branch still untouched base | artifact review |
| `teamleaderleo/codex#77@0fb2e6b...` | run `30584055792` | success | `target-executed` MCP publication |
| `teamleaderleo/codex#75@c3373c7...` | review `4823972975` | manager invariant accepted | independent source review |
| `teamleaderleo/codex#82@fee6e83...` | run `30584136349` | failed before handler on unknown method | carrier-only |
| `teamleaderleo/codex#82@feb0c46...` | run `30589313367` | queued | reconnect execution pending |
| `teamleaderleo/codex#79@d96bcf0...` | run `30584093534` | generator failed before source | carrier-only |
| `teamleaderleo/codex#79@40ad254...` | run `30588729054` | queued | authority execution pending |
| `teamleaderleo/codex#78@e156bef...` | run `30584251271` | in progress at prior refresh | replay execution pending |
| `teamleaderleo/codex#83@78fd39e...` | run `30584411308` | queued at prior refresh | typed-identity execution pending |
| `teamleaderleo/codex#58@40a56ee...` | run `30584165709` | in progress at prior refresh | Responses Lite execution pending |
| `teamleaderleo/codex#64@c09a94d...` | run `30584556260` | queued at prior refresh | deferred mixed-catalogue execution pending |
| `openai/codex@413492cd...` | compare from `3016671...` | one Windows permission-normalization commit; no active-fence overlap | `source-read` |

Broad repository workflows such as `blocking-ci`, Fieldwork integrity, artifact review, source-only materialization, and carrier retirement remain separate gates. A green bounded carrier does not by itself accept or merge source.

## Complete-diff and compatibility review

- Canonical findings, autonomous comparison, and investigation workspaces are composed in Fieldwork PR #283.
- Fieldwork issue #289 is the protocol discussion and review surface.
- Stacked PR #292 carries Codex prerequisites, current F239 synthesis, and the first three split findings.
- F83 and F84 have real source PRs plus independent complete-diff reviews.
- F23 has accepted target evidence and a verified artifact, while its intended owned branch still lacks the source commit.
- Current compatibility surfaces: standalone Code Mode host, MCP manager snapshots/reconnect, prepared-call authority, ThreadStore writer generations, rollout reconciliation, unified-exec deque/lifecycle ordering, and target workflow prerequisites.
- Exact-head review of each source successor remains required.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `EXECUTE, MATERIALIZE, SPLIT, and COMPARE`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: materialize F23 source; finish corrected reconnect and authority runs; refresh replay, typed identity, Responses Lite, and deferred gates; split each supported conclusion into a canonical finding or stopped record.
- Clearing condition: every current and historical candidate has a current-source disposition, canonical finding or stopped record, exact receipt, and carrier successor/retirement state.
- Required subgates: current-source overlap, exact tests, complete diff, compatibility, source-only publication, independent review.
- Autonomous work remaining: execution, source materialization, comparative review, finding splits, and carrier cleanup.
- Non-delegable human decision: none currently.

## Issue and proposal packaging

Issue #239 remains the portfolio command surface and this file remains the meta-analysis finding. It should not become one public-style mega-issue.

Existing campaign issues #83, #84, #85, #134, and scout #23 remain the technical owner surfaces. The first accepted packets are represented by separate canonical findings under those existing issues. New issues are warranted only when a bounded packet lacks an existing owner or becomes a distinct implementation/review decision that the current issue cannot carry cleanly.

Current source review surfaces:

- append acknowledgement: owned source PR #84 and F83;
- MCP publication generation: owned source PR #75 and F84;
- terminal producer retention: F23, source PR blocked on Git materialization.

No public proposal draft should claim full Codex tool continuity. Future drafts should present one bounded invariant, its exact cases, source owner, alternatives, compatibility limits, and evidence.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | PR #266 | Created one workspace and selected bounded outputs over a mega-patch |
| 2026-07-31 | PR #271 review | Identified missing canonical-findings dependency and state-vocabulary contradiction |
| 2026-07-31 | PR #283 | Composed protocol, canonical finding, comparative state, and refreshed source/carrier identities |
| 2026-07-31 | PR #292 initial refresh | Recorded Codex CI prerequisites, public head `413492cd...`, green append/terminal/publication gates, and repaired authority execution |
| 2026-07-31 | F83/F84/F23 split | Promoted supported packets into canonical technical findings; retained different delivery gates instead of one issue draft |

## References

- Fieldwork issues #23, #83, #84, #85, #134, #239, #254, and protocol review #289.
- Fieldwork PRs #268, #283, and #292.
- `investigations/239-codex-upstream-convergence/`.
- `targets/codex/map.md`.
- `findings/F83-codex-append-acknowledgement/finding.md`.
- `findings/F84-codex-mcp-publication-generation/finding.md`.
- `findings/F23-codex-terminal-producer-retention/finding.md`.
- `findings/F239-codex-upstream-convergence/evidence/20260731-codex-ci-prerequisites.md`.
- Owned Codex PRs #51, #52, #53, #58, #64, #73–#84.
- Public Codex source through `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`, read-only.
- Public upstream interaction: none.
