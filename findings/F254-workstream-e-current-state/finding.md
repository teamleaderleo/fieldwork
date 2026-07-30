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

Workstream E has four kinds of branch:

1. **Source** — code that may become the repair.
2. **Test rig** — temporary workflow machinery used to execute or publish source.
3. **Photograph** — retained evidence of old behavior, a failed assertion, or a rejected direction.
4. **Old map** — an exact historical pin or description replaced by a newer owner.

This file answers one question: **where should a reviewer look now?**

It does not choose every technical design again. Individual canonical findings own those decisions:

- F22 owns Gemini execution termination;
- F84 owns Codex MCP call authority and cancellation certainty;
- F239 owns Codex convergence families;
- campaign #71 owns the T3/OpenCode V2 transfer and composition gate.

Several reasonable technical options are active work, not a reason to ask the user. Human escalation begins only at merge, public upstream contact, private context, material cost, product values absent from the repository, or irreversible risk.

## Why we care

A mixed portfolio list creates predictable review errors:

- a reproduction is reviewed as the fix;
- a carrier failure is treated as product evidence;
- an old exact pin is mistaken for the current candidate;
- a closed evidence branch is mistaken for discarded evidence;
- an implementation comparison is presented as a human preference question before discriminating work is exhausted;
- temporary workflow code enters the merge queue.

A current map removes those errors while keeping the technical findings small and independently reviewable.

## One-page answer

### Care now

#### Gemini CLI

- **Discovered-tool cancellation — PR #1:** target-executed helper-wiring evidence. Build a clean process-tree repair and run a real parent/descendant matrix.
- **Approval affinity — PR #6:** the five focused authority controls passed at source head `789ffb3e7af0ec2f25d65e22062c4284f3e44477` in run `30585861453`. Three adjacent failures came from a legacy mock that never reflected the real `Validating → AwaitingApproval` state transition. Carrier head `59e5534e208c3ae7882ddcd4787b926e10cb0b3a` makes the fixture stateful, runs focused and adjacent controls together, typechecks, and publishes a clean three-file source branch through run `30591785562`.
- **Waiting ownership — PRs #7/#8:** staged repair passed formatting, `16/16`, build, and core typecheck in run `30581298716`. Publisher #8 is repaired at `108d60a1b2c5fc89d89065c70fb2e95afb5cd37e`; run `30591032786` owns clean-source publication.
- **Execution termination — PR #4 / F22:** Fieldwork PR #299 selects a synchronous cancellation request returning one idempotent, non-rejecting termination receipt. `ExecutionHandle.result` remains the authoritative final execution result. Source materialization and real-process execution remain.

No Gemini technical API choice currently requires human judgment.

#### Codex

F239 is the portfolio owner. Reconciliation PR #297 records the bounded evidence and received repair review `4824116632`. Public source advanced to `4642370542739d5dd080b0c87a9de06a6435d3db`; the new commit changes generated app-server protocol export archives and requires an explicit freshness/compatibility update in F239.

- **Receipts and replay:** append source #84 has a clean target-executed successor; replay and compaction retain separate owners.
- **MCP authority:** F84 PR #290 selects captured-first execution plus an authority-checked cached-startup fallback. Exact-head review `4824047587` accepted the decision record. Always-live/full-`ToolInfo` equality is a losing direction.
- **MCP reconnect:** direct controls passed `2/2`; corrected public app-server route rerun remains under the reconnect owner.
- **Deferred exposure:** source #81 and transferred exact `4/4` receipt remain independently owned.
- **Terminal output:** Fieldwork execution passed nine exact controls and compile gates, exported source commit `8c7ea38419d790032db459816980e6b4dd38f574`, and moved to materialization PR #85 at carrier head `ea58829ef55e8a264e318a75b91d4f6d8514ef34`, run `30590059844`.
- **Responses Lite, stack pressure, process recovery, timeout settlement:** remain separate findings because their authority, recovery, and compatibility boundaries differ.

Codex MCP has no active D3 human design item. Implementation, execution, restacking, source transfer, and independent review remain autonomous.

#### T3 Code and OpenCode

Legacy production work is stopped by the completed V2 transfer decision.

- interruption ownership moves to V2;
- idle-release ownership moves to V2;
- restart uses explicit cancel-on-restart;
- pending requests still need direct terminal cancellation, late-response rejection, cleanup ordering, and one composed V2 head.

The remaining work is a composed execution gate, not a user preference question.

### Keep as evidence

- Gemini #2/#3: closed defect evidence; implementation moved to #6/#7/#8.
- Gemini #4: current termination defect evidence; source decision moved to F22 PR #299.
- Gemini #5: closed matrix rig; receipts transferred.
- Codex historical exact-pin and carrier branches whose front pages name a newer source or finding owner.
- Codex MCP authority carrier #79: retired losing implementation/harness record; zero source behavior executed.
- T3 legacy PR `teamleaderleo/t3code#1`: retained evidence after the V2 decision.

### Safe to leave out of ordinary review

A closed execution-only branch with transferred receipts and a named successor leaves the active queue. Reopen it only when:

- a receipt is challenged;
- the successor loses required evidence;
- current source movement invalidates the comparison;
- a rejected direction gains new evidence against the selected criteria.

## Current ownership map

| Family | Canonical technical owner | Current transition | Human decision |
| --- | --- | --- | --- |
| Gemini process-tree abort | issue #22 / PR #1 successor | source repair plus real process execution | none |
| Gemini approval affinity | PR #6 | clean source publication, complete diff, concurrent integration control | none |
| Gemini waiting ownership | PR #7 source, PR #8 carrier | clean source publication and review | none |
| Gemini termination | F22 PR #299 | source candidate and lifecycle/process matrix | none |
| Codex convergence | F239 PR #297 and issue #239 | freshness repair, independent execution, and materialization | none |
| Codex MCP authority | F84 PR #290 | captured-first source candidate and six-case matrix | none |
| T3/OpenCode V2 | campaign #71 | composed pending-request gate | none |

## Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Gemini waiting repair passes staged behavior and type gates | `target-executed` | PR #7, run `30581298716` | clean source publication remains |
| Gemini waiting publisher failures are carrier defects | harness evidence | runs `30581445734` and `30585074506` | current repaired run `30591032786` still controls publication |
| Gemini affinity authority controls pass | `target-executed` focused source evidence | PR #6 head `789ffb3e...`, run `30585861453`, five focused controls passed | adjacent fixture repair and clean publication remain |
| Gemini affinity adjacent failures came from impossible mock state | `target-executed` compatibility evidence plus source-read fixture audit | run `30585861453`; `confirmation.test.ts` mock returned `Validating` after `updateStatus` | repaired carrier `30591785562` remains queued |
| Gemini current termination path settles before async hook completion | `target-executed` fixed-input contract | PR #4 head `e33c6715...`, run `30504716033` | no real process tree |
| termination receipt is the selected API direction | comparative source/API analysis | F22 PR #299 | source caller/type execution remains |
| Codex terminal source passed exact controls and compile gates | `target-executed` | F239 PR #297, run `30587866332`, source `8c7ea384...` | materialization and current-head review remain |
| Codex captured-first MCP rule preserves two first-party intents | `source-read` plus exact comparison review | F84 PR #290, review `4824047587` | source successor and integration matrix remain |
| T3 ownership transfers to V2 | target-executed plus recorded decision | runs `30556506779`, `30557111582`, review #234 | one composed head remains |

## Decision discipline

### Selected patterns

- one readable portfolio map plus independently owned technical findings;
- autonomous comparison for technical alternatives;
- exact source/result owner separated from execution carriers;
- request certainty separated from final execution certainty;
- clean source heads required before delivery promotion.

### Declined patterns

- **Ask the user to choose internal APIs before caller and execution comparison:** technical evidence can settle those choices.
- **Treat every open PR as active product work:** many are evidence, diagnostics, or rigs.
- **Close every old-looking branch without retaining its result:** some branches carry the only exact failure or losing comparison.
- **Combine all E repairs:** approval authority, process termination, MCP publication, persistence, output retention, and restart policy have different owners.

## Execution-carrier rule

A rig never becomes the canonical implementation.

Retirement requires:

1. exact source and receipt identity transferred to the canonical record;
2. later exact source head proving temporary workflows absent;
3. complete-diff review of the clean source;
4. carrier closure or explicit historical status.

A workflow that plans to delete itself remains active machinery until a later head proves the deletion.

## Current disposition

- Finding state: `research-active`
- Role: portfolio navigation
- Review disposition: `none — technical dispositions live in F22, F84, F239, and campaign #71`
- Delivery lane: `not-entered`
- Exact next transition: classify Gemini runs `30591785562` and `30591032786`, review their clean source branches after publication, apply the four-field F239 freshness repair, continue current Codex materialization and authority matrices, and execute the T3/OpenCode composed gate
- Clearing condition: every active E family has one current technical owner, one exact next gate, and every rig has a retained receipt plus successor or closure
- Non-delegable technical decision: `none`
- Human authority retained: merge, release, deployment, credentials, public upstream interaction, and explicit high-impact actions

## Changes to the conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-31 | initial finding | Replaced the runner-blocked snapshot with source, rig, evidence, and successor classes. |
| 2026-07-31 | composed protocol PR #283 | Reclassified technical alternatives as autonomous comparative work. |
| 2026-07-31 | F84 PR #290 | Selected captured-first MCP authority; removed false D3 request. |
| 2026-07-31 | F22 PR #299 | Selected termination receipt ownership; removed open Gemini API question. |
| 2026-07-31 | F239 PR #297 | Reconciled current Codex source, terminal, append, publication, reconnect, and exposure evidence; exact review requested four freshness repairs. |
| 2026-07-31 | Gemini #8 | Classified second publisher failure and repaired staged workflow availability. |
| 2026-07-31 | Gemini #6 | Five focused affinity controls passed; converted stale adjacent fixture failure into a stateful clean-source publication gate. |

## References

- Fieldwork issues #14, #22, #71, #213, #239, #254.
- Fieldwork PRs #250, #268, #283, #290, #297, #299.
- `DECISIONS.md`, `REVIEWING.md`, `FINDINGS.md`, and `templates/finding.md` from PR #283.
- Owned Gemini CLI PRs #1–#8.
- Owned Codex convergence branches referenced by F239 and F84.
- T3 Code legacy PR #1 and exact V2 heads retained by campaign #71.
- Public upstream interaction: none.
