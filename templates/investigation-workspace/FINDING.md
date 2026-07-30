# <Workspace evidence note title>

Owner: <worker or transferred owner>  
Parent workspace: <path>  
Canonical Fieldwork finding: `<findings/F<issue>-<slug>/finding.md | parent finding | none yet>`  
Exact question: <one bounded question>  
Claim scope: `<mechanism | interface | integration | operational | ecosystem>`  
Source or retrieval boundary: `<revision, version, and date>`  
Canonical transition state: `<research-active | comparative-evaluation-active | review-ready | design-decision-ready | delivery-gate-ready | land-ready | stopped | closed>`  
Workspace-note status: `<draft | active | retained | superseded>`  
Upstream contact authorized: `<no | yes with exact authority>`

## In simple words

<Explain the component, responsibility, question, consequence, and current answer.>

## Relationship to the canonical finding

State whether this file:

- supplies evidence to an existing canonical `findings/F<issue>-<slug>/finding.md`;
- compares several canonical findings;
- records a bounded subquestion that still needs its own canonical finding;
- preserves a superseded or negative result.

A workspace note never replaces the canonical finding for a retained investigation. Link the canonical file and keep transition state, desk routing, current disposition, selected direction, and reopening trigger there.

When several technical directions remain plausible, follow `DECISIONS.md`. Keep the work active as `comparative-evaluation-active` while source research, prototypes, discriminating execution, or adversarial review can still distinguish the options.

## Boundary examined

- entrypoints: <paths>;
- state owner: <owner>;
- inputs and outputs: <boundary>;
- side effects: <effects>;
- failure and cleanup paths: <paths>;
- relevant tests: <tests>.

## Competing explanations or approaches

1. <hypothesis or option and distinguishing evidence>;
2. <hypothesis or option and distinguishing evidence>.

## Governing invariant and criteria

Governing invariant: <what must remain true>.

Ordered criteria:

1. <criterion that can make an option lose>;
2. <compatibility, ownership, performance, observability, or maintenance criterion>.

## Evidence

| Claim | Evidence class | Exact source or receipt | Limit |
| --- | --- | --- | --- |
| <claim> | `<source-read | model-executed | target-test-prepared | target-executed | integration-executed | full-gate>` | <path, revision, command, workflow, artifact> | <limit> |

## Comparative results

| Option | Exact implementation or analysis | Discriminating control | Result | Current disposition |
| --- | --- | --- | --- | --- |
| A | <branch, commit, artifact, or paper-only reason> | <test or comparison> | <outcome> | <active, selected, rejected, deferred> |
| B | <branch, commit, artifact, or paper-only reason> | <test or comparison> | <outcome> | <active, selected, rejected, deferred> |

## Findings

### <Finding>

<Reasoning and evidence links.>

## Independent criticism

- <counterexample, missing caller, disputed criterion, or reversing test>;
- <review receipt and response>.

## Negative results

- <failed hypothesis, absorbed behavior, or infeasible path>.

## Alternatives

- <serious alternative and tradeoff>.

## Dependencies and overlap

- <canonical finding, workspace note, campaign, issue, source candidate, or prior art>.

## Uncertainty

- <unknown>;
- <evidence that would resolve it>.

## Recommendation

Selected direction: <winner, all rejected, or comparison still active>.  
Losing reasons: <evidence that defeated each losing option>.  
Reopening trigger: <new evidence that changes the result>.  
Non-delegable human decision: <none or the smallest exact authority/value/cost/risk question>.  
Exact next transition: <destination and clearing condition>.
