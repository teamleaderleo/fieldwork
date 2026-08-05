# F<issue>-<slug>: <finding title>

Finding state: `research-active | comparative-evaluation-active | review-ready | design-decision-ready | delivery-gate-ready | land-ready | stopped | closed`

Workstream: `<A-I or programme>`  
Canonical Fieldwork issue: `#<number>`  
Canonical finding path: `findings/F<issue>-<slug>/finding.md`  
Canonical implementation: `<owned repository PR or none>`  
Exact implementation head: `<sha or none>`  
Exact base or source revision: `<sha, tag, or retrieval boundary>`  
Strongest evidence class: `source-read | model-executed | target-test-prepared | target-executed | integration-executed | full-gate`  
Reviewed input generation: `<body digest, explicit revision, metadata generation, or none>`  
Current review disposition: `ACCEPT | REPAIR | HOLD | EXECUTE | REJECT | none`  
Desk routing: `not-entered | Review Queue #213 | Delivery Desk #160 D0/D1/D2/D3`  
Upstream contact authorized: `no | yes with exact authority`

## In simple words

Explain the system and the result as though the reader has never seen the project.

- What is the component?
- Where does it sit in the larger operation?
- What happened?
- What is the current answer or decision?

## Why we care

Name the concrete consequence. Prefer an observed or directly supported consequence:

- wrong result;
- stale state;
- lost data;
- leaked resource;
- unsafe authority;
- broken recovery;
- portability failure;
- compatibility break;
- avoidable operator or user cost.

State frequency and severity only when measured or sourced.

## What happens if we leave it alone

Describe the bounded failure mode and who or what encounters it. Distinguish:

- observed consequence;
- inferred consequence;
- unknown frequency or exposure.

## Current finding

State the narrowest supported technical conclusion.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| `<claim>` | `<class>` | `<source path, workflow, artifact, or primary source>` | `<what this does not prove>` |

## System and ownership map

Describe:

- entrypoints;
- state owner;
- control and data flow;
- side effects;
- cleanup and recovery;
- public or internal contract;
- relevant test boundary.

## Historical precedent

For each close precedent, record:

### <precedent title>

- Source: `<stable URL>`
- Revision or date: `<value>`
- Principle supported: `<why it is relevant>`
- Important difference: `<why it does not settle the current finding by itself>`

When no close match exists, state the repositories, terms, and date range searched.

## Approaches considered

Use this section for serious alternatives. When two or more technical directions still need executable comparison, use `comparative-evaluation-active` and identify the control that can make each option lose. Do not use `design-decision-ready` until autonomous technical work can no longer settle the remaining choice.

### Retained approach: <name>

Explain why this direction best matches the invariant and evidence.

### Declined: <name>

Explain the concrete downside, failed control, compatibility risk, authority expansion, or ownership error.

### Deferred: <name>

Explain why this belongs to another finding or requires a separate decision.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| `<case>` | `<test, workflow, source proof>` | `<observed result>` |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| `<case>` | `<reason>` | `<issue, finding, or condition>` |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `<repo@sha>` | `<command, run, job>` | `<environment>` | `<result>` | `<class>` |

Classify setup, harness, fixture, installation, and unrelated failures separately.

## Complete-diff and compatibility review

Record:

- complete changed-file fence;
- current-base relationship;
- temporary carrier status;
- compatibility surfaces examined;
- known source defect or routine repair remaining;
- reviewer eligibility and exact-head disposition.

## Alternatives and consequences for the decision maker

Use this section whenever the state is `design-decision-ready`.

| Option | What it does | Benefit | Cost or risk | Evidence needed after selection |
| --- | --- | --- | --- | --- |
| A | `<option>` | `<benefit>` | `<cost>` | `<gate>` |
| B | `<option>` | `<benefit>` | `<cost>` | `<gate>` |

Recommendation: `<one option and why>`

## Current disposition and desk routing

- Finding state: `<explicit state>`
- Review disposition: `<value or none>`
- Review Queue entry: `<link or none>`
- Delivery lane: `D0 | D1 | D2 | D3 | not-entered`
- Exact next transition: `<one transition>`
- Clearing condition: `<one named condition>`
- Required subgates: `<list or none>`
- Autonomous work remaining: `<technical work or none>`
- Non-delegable human decision: `<one explicit question or none>`

## Changes to the canonical conclusion

Summarize material revisions so a reader can understand why the current answer differs from earlier issue comments or PR descriptions.

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| `<date>` | `<record>` | `<change>` |

## References

List exact source paths, retained Fieldwork evidence, workflow receipts, specifications, project documentation, issues, pull requests, and commits used by the finding.
