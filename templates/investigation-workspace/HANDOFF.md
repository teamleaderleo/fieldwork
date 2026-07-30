# Investigation workspace handoff

Workspace: <path>  
Parent issue: <issue>  
Coordinator: <owner>  
Workspace phase: `<orient | collect | compare | synthesize | decide | handoff>`  
Current transition state: `<research-active | comparative-evaluation-active | review-ready | design-decision-ready | delivery-gate-ready | land-ready | stopped | closed>`  
Snapshot date: <date>  
Current source or retrieval boundary: `<exact identity>`  
Workspace branch and exact head: `<repository, branch, SHA>`  
Canonical finding index: `<links>`  
Upstream contact authorized: `<no | yes with exact authority>`

## In simple words

<Explain the current answer, any active comparison, the remaining blocker or non-delegable decision, and the exact next action.>

## Work completed

- <finding, evidence, alternative, precedent, decision, or canonical output>;
- <finding, evidence, alternative, precedent, decision, or canonical output>.

## Canonical findings and transitions

| Canonical finding | State | Selected direction or active comparison | Disposition | Desk routing | Exact next transition |
| --- | --- | --- | --- | --- | --- |
| `findings/F<issue>-<slug>/finding.md` | <canonical state> | <winner or A/B still active> | <value> | <queue or desk> | <one transition> |

## Comparative decisions

| Question | Governing invariant | Options executed or analyzed | Selected direction | Reopening trigger | Non-delegable human decision |
| --- | --- | --- | --- | --- | --- |
| <bounded choice> | <invariant> | <branches, commits, artifacts, or paper-only reason> | <winner or active> | <new evidence> | <none or exact question> |

Use `comparative-evaluation-active` while additional autonomous source work, prototypes, execution, or criticism can distinguish the options. Use `design-decision-ready` only for the remaining authority, private-context, material-cost, product-value, or irreversible-risk question defined by `DECISIONS.md`.

## Current canonical outputs

| Output | Status | Audience | Exact inputs | Limit |
| --- | --- | --- | --- | --- |
| <path> | `<candidate | accepted | disputed | superseded | retired | held>` | <audience> | <revisions and receipts> | <limit> |

Output status applies to the presentation artifact. It never substitutes for a finding's transition state.

## Exact external and owned source state

| Repository or record | Branch or item | Exact head or generation | State |
| --- | --- | --- | --- |
| <repository> | <branch, issue, PR, or workflow> | `<identity>` | <state> |

## Executed evidence

| Command or workflow | Exact source head | Outcome | Evidence class | Limit |
| --- | --- | --- | --- | --- |
| <command or run> | `<SHA>` | <result> | <class> | <limit> |

## Active disagreements or criticism

- Proposition: <exact disagreement or counterexample>.
- Evidence or judgment needed: <distinguishing control or genuine non-delegable fact>.
- Files preserving each position: <paths>.

## Blockers

1. <blocker and retained evidence>;
2. <blocker and retained evidence>.

## Exact next actions

1. <one bounded action, owner, and destination>;
2. <one bounded action, owner, and destination>.

## Expiry conditions

This handoff expires when:

- <relevant source head moves>;
- <carrier or workflow completes>;
- <issue, comparison, or decision input changes>;
- <canonical output is accepted, superseded, or retired>.

## Public interaction

Public upstream interaction performed: `<no | exact authorized interaction>`.
