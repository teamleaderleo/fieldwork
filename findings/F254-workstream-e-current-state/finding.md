# F254-workstream-e-current-state: What still needs care in agents and CLIs

Finding state: `research-active`

Workstream: `E`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-workstream-e-current-state/finding.md`  
Canonical implementation: `none — portfolio navigation finding`  
Exact implementation head: `none`  
Exact protocol base: `Fieldwork PR #283@23ef5d6e1d955eb7a8984a0491dc99a5e08a1d81`  
Strongest evidence class: claim-specific; individual findings own exact classification  
Reviewed input generation: `live issue, PR, source, and workflow audit on 2026-07-31`  
Current review disposition: `none — navigation only`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

Workstream E contains four different things that should never share one review queue:

1. **Source** — code that may become a repair.
2. **Test rig** — temporary machinery that executes or publishes source.
3. **Photograph** — retained evidence of old behavior or a rejected direction.
4. **Old map** — a historical pin or description replaced by a current owner.

This file tells a reviewer where to look now. Individual findings own the technical decisions:

- F22 owns Gemini execution termination;
- F84 owns Codex MCP call authority and cancellation certainty;
- F239 owns Codex convergence families;
- campaign #71 owns T3/OpenCode V2 composition.

Technical alternatives remain autonomous work while evidence can distinguish them. Human escalation is reserved for merge, release, deployment, public upstream contact, private context, material cost, product values absent from repository evidence, and irreversible risk.

## Why we care

A mixed portfolio list creates predictable errors:

- a reproduction is reviewed as the fix;
- a carrier failure is treated as product evidence;
- an old exact pin is mistaken for the current candidate;
- a closed evidence branch is mistaken for discarded evidence;
- an implementation comparison is presented as a user preference question;
- temporary workflow code enters the delivery queue.

The map prevents those errors and keeps technical findings independently reviewable.

## One-page answer

### Gemini CLI

#### Discovered-tool cancellation

Owned evidence PR #1 proves that invocation abort does not reach the process-group termination helper. The selected transition is a clean process-tree source repair plus real parent/descendant, launch-race, natural-exit, escalation, partial-output, listener, sandbox-cleanup, and rerun controls.

#### Approval call affinity

PR #6 staged head `59e5534e208c3ae7882ddcd4787b926e10cb0b3a` binds modification to the exact call and revalidates approval after the modifier await.

Run `30585861453` passed all five focused authority controls and exposed an impossible adjacent mock state. Publisher run `30591785562` has since passed source formatting, the focused and adjacent suites, core typecheck, and clean-tree validation; clean branch publication is the remaining step at this update.

#### Approval waiting ownership

PR #7 staged head `9d257f565fa42c88bed519038a789dff81668b35` passed formatting, `16/16`, build, and core typecheck in run `30581298716`.

PR #8 is publication machinery. Three harness-only failures successively exposed:

1. missing exact base state in a shallow checkout;
2. missing staged workflow input during source extraction;
3. missing reviewed `confirmation.waiting-state.test.ts` in the detached source checkout.

Current carrier head `ccd85e92c267109294e5596f9a8f16813c838bfd` copies the complete reviewed six-file source/test input. Run `30594684917` owns the current publication attempt.

#### Execution termination ownership

F22 PR #299 selected the API family: `kill()` remains a synchronous request and returns one non-rejecting receipt per active termination attempt; `ExecutionHandle.result` remains final execution authority.

Review `4824456392` keeps that family and requires a bounded finding repair before source work:

- use `research-active` after selection;
- use one review disposition;
- keep final `ExecutionResult` out of a second receipt value;
- define a new receipt after `request_failed` clears the prior attempt.

The next source slice widens hooks to sync-or-async, joins repeated requests, lets natural exit win, keeps request failure retryable, and executes real process controls. No Gemini technical API choice currently requires user judgment.

### Codex

F239 canonical authoring now lives in PR #292 at `b587c58e495a9cbfe5b11d460ef4e045f0496b6a`. PR #297 is superseded as an authoring surface; its useful reconciliation intent is incorporated in #292.

Current bounded owners include:

- **Append acknowledgement:** source #84, target-executed receipt `30583967538`; current-head packaging and cleanup remain.
- **MCP publication generation:** source #75, run `30584055792`, exact `5/5`; one slow-old/fast-new runtime fixture remains.
- **MCP call authority:** F84 PR #290 selects captured prepared bindings for ordinary calls and an authority-checked cached-startup fallback. The always-live/full-`ToolInfo` direction is retired.
- **MCP reconnect:** source #89 at `51883318c606bfb60444032d16e500d51ff71da0`; run `30589313367` passed exact `3/3`, focused module, and V8 canary. Quiet-period and failed-planning controls remain.
- **Deferred runtime exposure:** source #88 passed exact planner controls; Code Mode stays independently owned.
- **Terminal output retention:** run `30587866332` passed nine exact controls and bounded compile gates, exporting source `8c7ea38419d790032db459816980e6b4dd38f574`. Git materialization and source PR review remain.
- **Responses Lite, receipt replay, typed identity, stack pressure, process recovery, and timeout settlement:** remain separate because they have different authority and recovery boundaries.

Current public Codex source fence: `4642370542739d5dd080b0c87a9de06a6435d3db`. The observed drift is file-disjoint from the declared active source fences, subject to each bounded finding's own renewal rule.

Codex MCP has no D3 human design item. Source work, execution, restacking, materialization, and review continue autonomously.

### T3 Code and OpenCode

Legacy production work is stopped by the V2 transfer decision:

- interruption ownership moves to V2;
- idle-release ownership moves to V2;
- restart uses explicit cancel-on-restart.

The remaining gate is one composed V2 head proving direct pending-request cancellation, late-response rejection, cleanup ordering, and restart behavior. This is execution work, not a user preference question.

## Keep as evidence

- Gemini #2/#3: closed defect evidence; implementation moved to #6/#7/#8.
- Gemini #4: termination defect evidence; the selected API family moved to F22 PR #299.
- Gemini #5: closed matrix rig; receipts transferred.
- Codex historical pins and carriers whose front pages name a current source or finding owner.
- Codex failed full-live MCP authority carrier: retained losing implementation and harness evidence; no source behavior executed.
- T3 legacy PR #1: retained evidence after the V2 decision.

A closed evidence branch remains useful. It leaves ordinary review when its receipt and rejection or successor are durable.

## Current ownership map

| Family | Canonical technical owner | Current transition | Human technical decision |
| --- | --- | --- | --- |
| Gemini process-tree abort | issue #22 / PR #1 successor | source repair plus real-process execution | none |
| Gemini approval affinity | PR #6 | clean publication, complete diff, parallel integration control | none |
| Gemini waiting ownership | PR #7 source, PR #8 carrier | clean publication, review, carrier retirement | none |
| Gemini termination | F22 PR #299 | finding repair, source candidate, lifecycle/process matrix | none |
| Codex convergence | F239 PR #292 and issue #239 | bounded source gates, materialization, review | none |
| Codex MCP authority | F84 PR #290 | captured-first source candidate and authority matrix | none |
| T3/OpenCode V2 | campaign #71 | composed pending-request gate | none |

## Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Gemini waiting repair passes staged behavior and type gates | `target-executed` | PR #7, run `30581298716` | clean publication remains |
| Gemini waiting publisher failures are carrier defects | harness evidence | runs `30581445734`, `30585074506`, `30591032786` | run `30594684917` controls current publication |
| Gemini affinity authority controls pass | `target-executed` focused source evidence | run `30585861453`, five focused controls | clean branch publication and integration control remain |
| Gemini affinity clean publisher passes source gates | `target-executed` current carrier | run `30591785562` through focused/adjacent tests, typecheck, clean tree | publication completion and source review remain |
| Gemini termination settles before async hook completion | `target-executed` fixed-input contract | PR #4, run `30504716033` | no real process tree |
| termination receipt is the selected API family | source/API comparison plus review | F22 PR #299, review `4824456392` | finding repair and source execution remain |
| Codex terminal source passes exact controls and bounded compile gates | `target-executed` | run `30587866332`, source `8c7ea384...` | Git materialization and current-head review remain |
| Codex captured-first MCP rule preserves both current intents | `source-read` plus exact comparison | F84 PR #290 | source successor and integration matrix remain |
| T3 ownership transfers to V2 | target-executed plus recorded decision | runs `30556506779`, `30557111582`, review #234 | one composed head remains |

## Decision discipline

### Selected patterns

- one portfolio map plus independently owned technical findings;
- autonomous comparison for technical alternatives;
- canonical source separated from execution carriers;
- request certainty separated from final execution certainty;
- clean source heads required before delivery promotion.

### Declined patterns

- asking the user to choose internal APIs before caller and execution comparison;
- treating every open PR as active product work;
- discarding closed evidence before its receipt and losing reason are retained;
- combining approval authority, process termination, MCP publication, persistence, output retention, and restart policy into one implementation.

## Execution-carrier rule

A rig never becomes the canonical implementation.

Retirement requires:

1. exact source and receipt identity transferred to the canonical record;
2. a later exact source head proving temporary workflows absent;
3. complete-diff review of the clean source;
4. carrier closure or explicit historical status.

A workflow that plans to delete itself remains active machinery until a later head proves the deletion.

## Current disposition

- Finding state: `research-active`
- Role: portfolio navigation
- Review disposition: `none — technical dispositions live in F22, F84, F239, and campaign #71`
- Delivery lane: `not-entered`
- Exact next transition: classify Gemini runs `30591785562` and `30594684917`; review and retire their clean publication carriers; repair F22 PR #299; continue bounded Codex source/materialization gates through F239 PR #292; execute the T3/OpenCode composed gate
- Clearing condition: every active E family has one current technical owner and exact next gate, and every rig has a retained receipt plus successor or closure
- Non-delegable technical decision: `none`
- Human authority retained: merge, release, deployment, credentials, public upstream interaction, and explicit high-impact actions

## Changes to the conclusion

| Date | Change |
| --- | --- |
| 2026-07-31 | Replaced the runner-blocked snapshot with source, rig, evidence, and successor classes. |
| 2026-07-31 | Applied PR #283 autonomous-decision semantics. |
| 2026-07-31 | F84 selected captured-first MCP authority and removed the false D3 request. |
| 2026-07-31 | F22 selected termination-receipt ownership; review narrowed its remaining model repairs. |
| 2026-07-31 | F239 canonical authoring moved from superseded PR #297 to PR #292. |
| 2026-07-31 | Gemini waiting publication classified a third harness defect and restored the complete reviewed six-file input. |
| 2026-07-31 | Gemini affinity passed focused and adjacent source gates through clean publication machinery. |

## References

- Fieldwork issues #14, #22, #71, #213, #239, #254.
- Fieldwork PRs #250, #283, #290, #292, #299.
- `DECISIONS.md`, `REVIEWING.md`, `FINDINGS.md`, and `templates/finding.md` from PR #283.
- Owned Gemini CLI PRs #1–#8.
- Owned Codex convergence branches referenced by F239 and F84.
- T3 Code legacy PR #1 and exact V2 heads retained by campaign #71.
- Public upstream interaction: none.
