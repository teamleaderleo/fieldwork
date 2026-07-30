# F<issue>-<slug>: <finding title>

Finding state: `research-active | comparative-evaluation-active | review-ready | design-decision-ready | delivery-gate-ready | land-ready | stopped | closed`

Workstream: `<A-I or programme>`  
Canonical Fieldwork issue: `#<number>`  
Canonical finding path: `findings/F<issue>-<slug>/finding.md`  
Canonical implementation or alternatives: `<owned repository PRs or none>`  
Exact implementation heads: `<sha list or none>`  
Exact base or source revision: `<sha, tag, or retrieval boundary>`  
Strongest evidence class: `source-read | model-executed | target-test-prepared | target-executed | integration-executed | full-gate`  
Reviewed input generation: `<body digest, explicit revision, metadata generation, or none>`  
Current review disposition: `ACCEPT | REPAIR | HOLD | EXECUTE | REJECT | none`  
Desk routing: `not-entered | Review Queue #213 | Delivery Desk #160 D0/D1/D2/D3`  
Upstream contact authorized: `no | yes with exact authority`

Read `DECISIONS.md` whenever more than one technical direction remains plausible.

## In simple words

Explain the system and the result as though the reader has never seen the project.

- What is the component?
- Where does it sit in the larger operation?
- What happened?
- Which direction currently wins, or what work will distinguish the options?

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

## Governing goals and invariant

Record the project goals, public contracts, compatibility promises, architecture, and test expectations that govern the choice.

Governing invariant: `<one sentence>`

| Goal or contract | Primary source | Consequence for the design |
| --- | --- | --- |
| `<goal>` | `<source path, specification, or official documentation>` | `<criterion imposed>` |

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

Search current source, history, official documentation or specifications, first-party analogues, and closely related implementations before relying on secondary commentary. When no close match exists, state the repositories, terms, and date range searched.

## Decision criteria

Define criteria before selecting an implementation.

| Priority | Criterion | How it will be measured or falsified |
| --- | --- | --- |
| 1 | `<criterion>` | `<test, benchmark, source proof, or review question>` |

## Alternatives instantiated or analyzed

Give every option a stable identifier.

### Option A — <name>

- Artifact or branch: `<exact branch, PR, commit, experiment, or paper-only reason>`
- Invariant implemented: `<value>`
- Expected benefit: `<value>`
- Expected cost or failure: `<value>`
- Discriminating control: `<value>`
- Rollback boundary: `<value>`

### Option B — <name>

- Artifact or branch: `<exact branch, PR, commit, experiment, or paper-only reason>`
- Invariant implemented: `<value>`
- Expected benefit: `<value>`
- Expected cost or failure: `<value>`
- Discriminating control: `<value>`
- Rollback boundary: `<value>`

Add options as required. State why implementation would add no useful evidence when an option remains paper-only.

## Comparative results

| Criterion | Baseline | Option A | Option B | Winner or unresolved reason |
| --- | --- | --- | --- | --- |
| `<criterion>` | `<result>` | `<result>` | `<result>` | `<value>` |

Record tests that can make an option lose. Do not compare alternatives only through shared happy paths.

## Independent criticism

| Reviewer or evidence source | Counterexample or criticism | Response or new control | Effect on recommendation |
| --- | --- | --- | --- |
| `<record>` | `<criticism>` | `<response>` | `<effect>` |

## Selected direction and losing reasons

Selected direction: `<option, all rejected, or comparison still active>`

Why it wins: `<criteria and evidence>`

| Losing or deferred option | Reason it lost or moved elsewhere | Reopening trigger |
| --- | --- | --- |
| `<option>` | `<executed failure, compatibility cost, ownership error, disproportionate complexity, or separate scope>` | `<new evidence>` |

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

- complete changed-file fence for every active option;
- current-base relationship;
- temporary carrier status;
- compatibility surfaces examined;
- known source defect or routine repair remaining;
- reviewer eligibility and exact-head disposition.

## Current disposition and desk routing

- Finding state: `<explicit state>`
- Review disposition: `<value or none>`
- Review Queue entry: `<link or none>`
- Delivery lane: `D0 | D1 | D2 | D3 | not-entered`
- Exact next transition: `<one transition>`
- Clearing condition: `<one named condition>`
- Required subgates: `<list or none>`
- Autonomous work remaining: `<research, prototypes, execution, cross-review, or none>`
- Non-delegable human decision: `<none or smallest exact question>`
- Why further autonomous work cannot settle it: `<required only for design-decision-ready>`

`design-decision-ready` is valid only when `DECISIONS.md` identifies a genuine authority, value, cost, private-context, or irreversible-risk boundary. Multiple technical options alone require `comparative-evaluation-active`.

## Changes to the canonical conclusion

Summarize material revisions so a reader can understand why the current answer differs from earlier issue comments or PR descriptions.

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| `<date>` | `<record>` | `<change>` |

## References

List exact source paths, retained Fieldwork evidence, workflow receipts, specifications, project documentation, issues, pull requests, commits, and first-party comparison implementations used by the finding.