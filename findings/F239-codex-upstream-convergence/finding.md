# F239-codex-upstream-convergence: Separate Codex lifecycle facts into reviewable ownership boundaries

Finding state: `comparative-evaluation-active`

Workstream: `J/O/I — current-source convergence, synthesis, and cross-repository audit`  
Canonical Fieldwork issue: `#239`  
Canonical finding path: `findings/F239-codex-upstream-convergence/finding.md`  
Investigation workspace: `investigations/239-codex-upstream-convergence/`  
Canonical implementation or alternatives: `several bounded findings, owned source candidates, and investigation issue #390; no combined implementation`  
Exact active heads: `F239 carrier teamleaderleo/fieldwork#292; append #84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2; MCP publication #75@c3373c717f3138ff5f0a979d12836f60800d2bcf; terminal #93@7f15307fd2c157d8a139310d2e8243f3f2b391a4; reconnect #101@df954cf401db38c55cbfc80b758fd9141ad0a31e`  
Exact base or source revision: `openai/codex@5548c95d66e29aeb994a982db8a378d9453694b0`; older execution receipts retain their exact pins  
Strongest evidence class: `target-executed` for append acknowledgement, MCP publication generation, terminal producer retention, Responses Lite client controls, deferred runtime exposure, and MCP reconnect; `source-read` for current dependency and persistence maps  
Reviewed input generation: `read-only public source and issue snapshots; exact owned source/carrier heads; target workflow receipts; artifact verification; complete-diff reviews; split findings; package and state-owner maps`  
Current review disposition: `RESTACK, EXECUTE, SPLIT, and COMPARE`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Codex advertises tools, selects an environment, dispatches work, waits or cancels, reports results, persists history, rebuilds indexes, and later resumes or replays that history. Those actions are connected. They are owned by different lifecycle boundaries.

The governing rule is:

> Codex must preserve the fact owned by each lifecycle boundary. One layer's success cannot prove a stronger fact owned by another layer.

Examples:

- capability visibility does not prove executable authority;
- dispatch does not prove remote-effect settlement;
- model-visible result does not prove durable append;
- canonical rollout durability does not prove SQLite projection freshness;
- best-effort broadcast does not prove the final terminal transcript;
- SDK success does not prove the native runtime carried the same persistence or settlement fact.

The selected direction is one shared explanation plus bounded findings and investigation packets. A combined patch would cross unrelated owners, test matrices, compatibility surfaces, and rollback boundaries.

## Why we care

Codex can perform actions with external effects and can later reconstruct their history. The model, user, retry policy, restart path, and source reviewer need different answers:

- Which definition and environment authorized the call?
- Which runtime received it?
- Did the request leave Codex?
- Did cancellation reach the executor or service?
- Did the effect settle, remain possible, or become unknown?
- Did the model receive the result?
- Did canonical history accept the result?
- Are metadata and turns/items projections current?
- Can resume, fork, rollback, compaction, and replay reconstruct the same operation?
- Did terminal completion include bytes retained by the producer?

Collapsing those facts can authorize stale tool use, unsafe retry, duplicate persistence, misleading timeout language, missing history, stale indexes, or incomplete terminal output.

## What happens if we leave it alone

Observed bounded consequences across the linked source and execution records include:

- model-visible tools with stale or mismatched runtime ownership;
- explicit refresh that succeeds before a replacement is proven usable;
- cancellation and timeout results that do not establish remote-effect absence;
- canonical append followed by metadata or projection failure;
- live result formation without caller-visible durable append outcome;
- valid rollout files omitted by SQLite-dependent read surfaces;
- completion derived from best-effort subscribers instead of producer-retained output;
- historical candidates described as current after public source ownership moved;
- carrier setup failures mistaken for product failures;
- executed source retained only as an artifact rather than a reviewable Git tree.

Frequency and aggregate user impact remain unmeasured. Each conclusion is limited to its exact source and receipt.

## Governing goals and invariant

| Goal or contract | Primary owner | Consequence |
| --- | --- | --- |
| Model-visible tools have executable authority | request construction, tool planner, Code Mode host, MCP snapshot | declaration and dispatch share a captured environment-qualified identity |
| Runtime publication cannot regress | MCP manager and refresh generation | only an eligible generation publishes; active calls keep their prepared binding |
| Cancellation is separate from settlement | operation owner, transport, executor/service | deadline, delivery, cancellation, transport, and effect certainty remain distinct |
| Live result and durable append are separate | Session, `LiveThread`, `ThreadStore` | append acknowledgement is explicit and typed follow-up remains separate |
| Canonical history and projections are separate | rollout writer, state DB, history DB | repair reports which representation is current and never advances a projection past canonical history |
| History readers consume conservative facts | resume, fork, rollback, compaction, replay | ambiguous persistence cannot authorize duplicate retry or destructive cleanup |
| Terminal completion uses retained producer state | unified execution producer and bounded transcript | retain before broadcast; subscribers do not define final completion |
| SDK and runtime release identities agree | generated protocol, wrappers, native runtime | wrapper tests cannot substitute for native source and artifact identity |
| Historical execution does not imply current portability | Fieldwork exact-head protocol | current claims need current public pin, overlap review, source identity, and target execution |
| Carrier setup follows repository entrypoints | target workflows and toolchain files | missing prerequisites and obsolete API anchors are carrier evidence only |
| Artifact and source branch are separate facts | execution carrier and Git publication | verify artifact, materialize exact tree, open source review, then retire carrier |

## Current finding

The Codex portfolio should remain separated into independently reviewable findings and investigation packets.

Current ownership areas are:

1. model-visible capability and environment-qualified authority;
2. MCP refresh freshness and generation publication;
3. prepared or active call runtime binding;
4. timeout, cancellation, transport, and remote-effect certainty;
5. live result formation and canonical append acknowledgement;
6. metadata and history projection, reconciliation, compaction, resume, fork, rollback, and replay;
7. producer-owned terminal transcript retention;
8. SDK/runtime/protocol version coherence;
9. exact/native/Git/generated dependency provenance;
10. carrier setup, artifact verification, source materialization, review, and retirement.

### Current split findings and investigations

| Owner | State | Accepted or current conclusion | Exact remaining gate |
| --- | --- | --- | --- |
| `F83-codex-append-acknowledgement` | `delivery-gate-ready` | expose bounded canonical append acknowledgement | current-public-head packaging; typed persistence separate |
| `F84-codex-mcp-publication-generation` | `delivery-gate-ready` | generation/freshness ticket owns publication winner | complete slow-older/fast-newer runtime fixture and current restack |
| `F23-codex-terminal-producer-retention` | `delivery-gate-ready` historically | completion consumes producer-owned bounded transcript | raised-stack broad gate and current public restack |
| `F85-codex-responses-lite-first-generated-request` | bounded evidence | client proves first generated request behavior | runtime stack behavior and current packaging |
| deferred runtime exposure | bounded evidence | effective Direct-mode loader reachability proved | Code Mode remains separate |
| MCP explicit reconnect | exact `4/4` historical receipt | explicit reload replaces exactly once and failed reload preserves ready client | current restack; replacement-call service; cancellation atomicity |
| Fieldwork #390 | `source-read` investigation | rollout JSONL, metadata SQLite, and history SQLite have distinct owners and repair paths | fault-injected state matrix |
| SDK/runtime coherence | scoped investigation | wrapper result cannot prove native runtime fact | exact release/protocol/runtime identity table |
| dependency provenance | scoped investigation | exact, Git, generated, and native dependencies require owner and platform receipts | dependency-owner ledger and reproducibility matrix |

### Claim table

| Claim | Evidence class | Exact support | Current limit |
| --- | --- | --- | --- |
| One combined implementation crosses several state owners and rollback boundaries | `source-read` | F239 workspace and current public source map | Later composition can follow independent acceptance |
| Append acknowledgement is a supported bounded prerequisite | `target-executed` plus review | run `30583967538`; source #84; review `4823945751`; F83 | typed `Persisted/Ambiguous` and current restack remain |
| MCP publication generation is a supported manager invariant | `target-executed` plus review | run `30584055792`; exact `5/5`; source #75; review `4823972975`; F84 | complete overlapping runtime fixture and current restack remain |
| Terminal producer retention is supported for bounded normal-close behavior | `target-executed` plus artifact/source review | run `30587866332`; exact `9/9`; artifact `8777460316`; source #93 | broad gate hit unrelated stack exhaustion; current restack remains |
| Explicit reconnect exact-one and failed-reload preservation are supported on the old pin | `target-executed` | carrier #90 run `30595049466`; clean source #101 | public MCP changes overlap; two stronger controls remain |
| Public source is actively enforcing environment-qualified authority | `source-read` | shell restriction `ef293f7...`; environment-scoped OAuth `164b3b...` | does not prove every tool and credential path uses the same identity |
| Rollout JSONL is canonical while two SQLite representations can lag | `source-read` | public `5548c95...` local writer, state DB, history materializer, listing paths | exact failures and user surfaces still require fault injection |
| SDK wrappers cannot independently prove native runtime persistence or settlement | `source-read` | TypeScript/Python package boundaries and exact Python runtime pin | release-artifact identity table remains |
| Package presence alone is no defect or vulnerability proof | review rule | dependency map evidence note | concrete version, reachability, and behavior are required |

## System and ownership map

```text
model-visible capability
→ captured environment and runtime authority
→ operation identity and dispatch
→ local or remote execution
→ deadline, cancellation, transport, and effect settlement
→ model-visible result
→ canonical rollout append
→ metadata SQLite and history SQLite projection
→ resume, fork, rollback, compaction, and replay
```

Terminal output has a parallel chain:

```text
process output producer
→ bounded retained transcript
→ best-effort live broadcast
→ terminal completion item
```

Release packaging has another:

```text
Rust source and generated protocol
→ native runtime artifact
→ TypeScript or Python wrapper package
→ user-visible SDK behavior
```

Each arrow is a boundary where a weaker fact must not be promoted into a stronger one.

## Historical and current precedent

### Thread persistence and writer ownership

- Sources: public PRs #18882, #21874, #27249, #30669, #31155, and current thread-store/rollout source.
- Supported principle: canonical append, metadata publication, history projection, writer generation, rotation, and cleanup have different owners and completion points.
- Difference: current reconciliation still needs one fault-injected matrix across every read/list mode.

### MCP runtime reconciliation and reconnect

- Sources: public PRs #30083, #31292, #31471, #31626, #34952, #35151, plus owned #75/#90/#101.
- Supported principle: immutable runtime snapshots, explicit freshness, targeted replacement, request-stable binding, and shared reconnect work are distinct.
- Difference: current public changes add environment-qualified credentials and MCP skills after the old execution pin.

### Environment-qualified authority

- Sources: public commits `164b3bfe...` and `ef293f7a...`.
- Supported principle: environment identity owns credential and tool authority; same names are insufficient across host, executor, local, and external runtimes.
- Difference: model publication, CLI login, app-server reconciliation, and actual dispatch still need end-to-end identity controls.

### Responses Lite and standalone Code Mode host

- Sources: commits `33cc928d...`, `20fedaff...`, `97576b...`; public PRs #35271 and #36129.
- Supported principle: capability declaration, normalized identifier, trace reconstruction, and executable host authority are related but distinct.
- Difference: trace repair does not prove first-request capability delivery or callable authority.

### Unified execution retention

- Sources: public PRs #31802, #34713, #36194; owned terminal receipts.
- Supported principle: output is bounded, close/drain ordering is consequential, and invalid UTF-8 progress should be preserved.
- Difference: hard termination, Windows containment, and restart/remote reattachment remain separate.

### Repository CI prerequisites and source publication

- Sources: public `setup-ci`, repo checks, root `justfile`, formatter script; Fieldwork carrier history.
- Supported principle: repository entrypoints define the complete target environment, and an execution artifact is separate from an owned Git source tree.
- Difference: each current candidate still needs exact current-head execution and a complete source review.

## Decision criteria

| Priority | Criterion | Measurement or falsifier |
| --- | --- | --- |
| 1 | Correct owner | exact source path and state owner for each claimed fact |
| 2 | Independent falsifiability | one candidate can fail without relying on unrelated layers |
| 3 | Current-source compatibility | exact public pin, overlap map, complete diff, and restack |
| 4 | Conservative authority | no retry, publication, compaction, or cleanup from weaker evidence |
| 5 | Target-native execution | repository entrypoints with declared prerequisites |
| 6 | Cross-representation recovery | canonical, metadata, projection, reader, and retry states all recorded |
| 7 | Artifact/source integrity | exact parent, tree, files, checksums, and branch identity |
| 8 | Rollback and carrier hygiene | source-only successor and disposable carrier retirement |
| 9 | Reader clarity | meta synthesis plus bounded technical owners |

## Alternatives instantiated or analyzed

### Option A — Shared lifecycle model plus bounded findings

- Benefit: preserves source owners, independent tests, currentness, and rollback.
- Cost: requires explicit routing and more records.
- Discriminating control: every candidate survives its exact current-source gate and complete-diff review.
- Rollback: retire one finding without discarding the shared model.

### Option B — One end-to-end mega-patch or mega-issue

- Benefit: one narrative.
- Failure: mixes environment authority, execution, settlement, persistence, projection, replay, terminal output, and packaging.
- Discriminating control: prove one owner and one test matrix establish every fact.
- Rollback: broad coupled revert or issue rewrite.

### Option C — Independent work with no synthesis

- Benefit: maximal source separation.
- Failure: readers cannot identify overlap, expiry, or current delivery state.
- Discriminating control: contradictory-state and orientation audit.
- Rollback: retain findings and remove the meta index.

### Option D — New issue for every observation

- Benefit: visible ownership.
- Failure: duplicates existing campaigns before a bounded proposal exists.
- Discriminating control: open a new issue only when a packet lacks an owner and has one reviewable question or implementation.
- Rollback: close as duplicate with successor mapping.

## Comparative results

| Criterion | A | B | C | D | Result |
| --- | --- | --- | --- | --- | --- |
| Owner fidelity | strong | weak | strong | strong but fragmented | A/C |
| Reader orientation | strong | superficially strong | weak | weak across many issues | A |
| Independent execution | strong | weak | strong | strong | A/C/D |
| Currentness tracking | strong | weak | local only | local only | A |
| Review and rollback | bounded | broad | bounded but fragmented | bounded with issue overhead | A |
| Preserves disagreement | strong | weak | weakly visible | dispersed | A |

## Independent criticism

| Evidence source | Criticism or counterexample | Response or control | Effect |
| --- | --- | --- | --- |
| protocol review | workspace links and state vocabulary previously depended on uncomposed branches | compose protocol in #283 and use #289 for review | keeps Option A valid only with exact composition |
| repeated public drift | carriers described as current after overlapping commits landed | expire present-tense claims and restack at exact public pins | currentness becomes an explicit gate |
| carrier prerequisite failures | missing `uv`, nextest, current methods, or unique anchors stopped execution | classify as harness evidence and document target prerequisites | avoids false product conclusions |
| terminal source publication | executed artifact existed before a real source branch | verify checksums/tree and require owned Git materialization | separates behavior receipt from delivery source |
| reconnect review | exact-one publication did not prove the replacement served a call or cancellation was atomic | add replacement-call and cancellation controls | retains bounded result and blocks broader claim |
| persistence source map | default listing repairs, while DB-only/relation/section paths depend more strongly on SQLite | exercise every mode in one fault-injected fixture | creates #390 rather than overclaiming one root cause |
| dependency map | exact and native packages can look suspicious without evidence | require affected version, reachability, behavior, owner, and platform receipt | prevents speculative security claims |

## Selected direction and losing reasons

Selected direction: Option A — one lifecycle model, bounded canonical findings, non-exclusive investigation owners, and exact current-source source/review gates.

| Losing or deferred option | Reason | Reopening trigger |
| --- | --- | --- |
| Mega-patch or mega-issue | crosses independent owners and rollback boundaries | architecture consolidates owners and all findings are accepted together |
| No synthesis | durable facts become difficult to reconcile | meta layer proves more costly than useful after adoption |
| Issue per observation | produces duplicate coordination surfaces | packet lacks an owner and gains one bounded question or implementation |
| Immediate public proposal | current gates and authorization are absent | explicit delivery request plus settled bounded packet |

## Edge cases covered

| Edge case | Evidence | Result |
| --- | --- | --- |
| pre-write versus commit-then-error append | F83 exact controls | same boolean can hide different durable histories; typed follow-up required |
| overlapping MCP publication | F84 exact `5/5` | generation owner accepted; full runtime overlap fixture remains |
| explicit reconnect and failed reload | #90 exact `4/4` | one replacement, quiescence, error propagation, and ready-client preservation proved on old pin |
| terminal late subscriber and bounded transcript | terminal exact `9/9` | producer retention accepted for bounded normal-close cases |
| first generated Responses Lite request | F85 client controls `2/2` | capability-prefix path proved at client boundary |
| deferred mixed catalogue | exact planner controls `5/5` | effective Direct-mode reachability proved; Code Mode separate |
| environment name collisions | public shell/OAuth changes | authority is environment-qualified, not name-only |
| canonical rollout ahead of history SQLite | current source map | intentional lag is possible; projection never owns canonical durability |
| metadata failure after canonical append | current source ordering | composite caller error can coexist with durable replay history |
| SQLite absent or stale during listing | current scan/repair and DB-only routes | read mode determines repair/fallback contract |

## Edge cases deferred or outside scope

| Edge case | Reason | Owner or trigger |
| --- | --- | --- |
| replacement generation serves a call | stronger than exact-one publication | reconnect successor to #101 |
| cancellation between reconnect intent and consumption | needs controlled interleaving | reconnect successor to #101 |
| CLI/runtime OAuth registry parity and loaded-thread adoption | separate environment identity path | MCP authority investigation |
| typed persistence and duplicate reconciliation | needs stable operation/item identity | F83 successor plus replay/identity owners |
| rollout/SQLite fault matrix | current work is source-read | Fieldwork #390 |
| hard terminal termination | separate process lifecycle | process/terminal finding |
| Windows process containment | platform-specific owner | process finding |
| restart or remote executor reattachment | distributed lifecycle | dedicated reconnect finding |
| SDK release identity mismatch | no reproduced mismatch yet | SDK/runtime coherence audit |
| dependency vulnerability | no concrete affected behavior yet | provenance audit with exact version and reachability |
| merge, release, deployment, or public upstream contact | authority boundary | explicit exact-head authorization |

## Exact execution and receipts

| Repository/head | Workflow or review | Result | Evidence class |
| --- | --- | --- | --- |
| append carrier #80 | run `30583967538` | exact controls and `codex-thread-store` package passed | `target-executed` |
| append source #84 | review `4823945751` | bounded prerequisite accepted | complete-diff review |
| MCP publication carrier #77 | run `30584055792` | exact `5/5`; full `codex-mcp` package passed | `target-executed` |
| MCP publication source #75 | review `4823972975` | generation invariant accepted | complete-diff review |
| terminal behavior carrier | run `30587866332`; artifact `8777460316` | exact `9/9`; source archive and blobs verified | target execution plus artifact review |
| terminal source #93 | head `7f15307...` | four-file source materialized on prior public pin | source identity; current restack pending |
| terminal carrier #94 | run `30597355839` | candidate controls passed; broad package hit unrelated stack exhaustion | mixed target receipt |
| reconnect carrier #90 | run `30595049466` | exact `4/4` | `target-executed` on prior pin |
| reconnect source #101 | head `df954cf...` | clean three-file source; current restack required | source review pending current pin |
| Responses Lite #87 | run `30584165709` | client controls `2/2`; default stack diagnostic separate | bounded target execution |
| deferred runtime exposure #88 | run `30584556260` | planner controls `5/5` | bounded target execution |
| F239 carrier #292 | current exact head recorded in PR body | Fieldwork integrity renewed after every head change | canonical documentation gate |

Broad repository CI, source review, current-public overlap, carrier retirement, and merge authority remain separate gates. A green bounded workflow does not accept or merge source.

## Complete-diff and compatibility review

- Fieldwork PR #283 composes canonical findings and investigation workspaces.
- Fieldwork issue #289 is the protocol review surface.
- PR #292 carries the canonical Codex synthesis and evidence notes; it contains no product source.
- Public source moved through shell authority, environment-scoped OAuth, skills, MCP server skill delivery, and external-agent connector detection during this pass.
- Those commits overlap MCP/tool/skills surfaces and expire old current-source classifications there.
- Append, terminal, publication, Responses Lite, deferred exposure, and reconnect receipts retain historical validity for their exact source trees.
- Fieldwork #390 is the first new bounded investigation owner produced by the dependency/source pass.
- Execution carriers remain temporary and are never merge candidates.
- Source PRs require exact-head compatibility, current tests, complete diff, review, and explicit merge authorization.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `RESTACK, EXECUTE, SPLIT, and COMPARE`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: finish #390's state matrix; restack reconnect and terminal source fences on the current public pin; execute the two stronger reconnect controls and terminal raised-stack broad gate; refresh package/runtime coherence and dependency-owner records.
- Clearing condition: every active packet has a current-source disposition, exact receipt, canonical finding or stopped record, source review state, and carrier retirement state.
- Required subgates: current-source overlap, exact tests, complete diff, compatibility, source-only publication, independent criticism, integrity, and carrier cleanup.
- Autonomous work remaining: source reading, controlled fixtures, restacks, reviews, synthesis, and disposable-carrier cleanup.
- Non-delegable human decision: merge, release, deployment, credentials, public upstream contact, or any other explicitly reserved authority action.

## Issue and proposal packaging

Issue #239 remains the portfolio synthesis and routing surface.

Existing issues #23, #83, #84, #85, #134, and #390 own bounded technical questions. A new issue is appropriate when a packet lacks an owner and has one implementation or independently reviewable proposal question. Fieldwork #390 meets that threshold because rollout/SQLite reconciliation has separate source owners, failure controls, and recovery decisions.

No public proposal should claim full Codex lifecycle continuity. A future proposal should present one bounded invariant, exact source owner, alternatives, compatibility limits, tests, and evidence.

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-31 | PR #283 | composed the canonical-findings and investigation protocol |
| 2026-07-31 | PR #292 initial stack | recorded CI prerequisites and split F83/F84/F23 |
| 2026-07-31 | terminal source #93/#94 | materialized prior-pin source and separated candidate controls from unrelated broad-stack failure |
| 2026-07-31 | reconnect #90/#101 | exact `4/4` receipt transferred into a clean three-file source carrier |
| 2026-07-31 | public `ef293f7...` and `164b3b...` | added first-party environment-qualified tool and credential authority precedent |
| 2026-07-31 | dependency boundary map | added Rust, Node, Python, native, exact, Git, and generated package lanes without speculative defect claims |
| 2026-07-31 | Fieldwork #390 and state-owner map | separated rollout JSONL, metadata SQLite, and history SQLite reconciliation into a bounded owner |
| 2026-07-31 | public `5548c95...` | refreshed current source through MCP skills and external-agent connector detection |

## References

- Fieldwork issues #23, #83, #84, #85, #134, #239, #289, #390.
- Fieldwork PRs #283 and #292.
- Owned Codex PRs #75, #84, #87, #88, #90, #93, #94, and #101.
- `targets/codex/map.md`.
- `findings/F83-codex-append-acknowledgement/finding.md`.
- `findings/F84-codex-mcp-publication-generation/finding.md`.
- `findings/F23-codex-terminal-producer-retention/finding.md`.
- `findings/F85-codex-responses-lite-first-generated-request/finding.md`.
- `findings/F239-codex-upstream-convergence/evidence/20260731-codex-ci-prerequisites.md`.
- `findings/F239-codex-upstream-convergence/evidence/20260731-codex-dependency-and-boundary-map.md`.
- `findings/F239-codex-upstream-convergence/evidence/20260731-rollout-sqlite-state-owner-map.md`.
- Public Codex source through `5548c95d66e29aeb994a982db8a378d9453694b0`, read-only.
- Public upstream interaction: none.
