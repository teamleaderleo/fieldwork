# Autonomous Design Decision Closure

## In simple words

Several reasonable-looking repairs are a reason to compare them, not a reason to stop and ask a person who has not yet built the same context.

The default Fieldwork response is to learn enough to choose: read the code and project goals, find precedent, build the useful alternatives when practical, run discriminating tests, invite independent criticism, and retain the best-supported direction. A human decision is required only when the choice depends on authority, values, irreversible risk, private context, material cost, or another fact that workers cannot discover or safely exercise.

## Default rule

Do not classify work as blocked merely because:

- more than one implementation is plausible;
- the codebase does not state the answer directly;
- compatibility consequences require investigation;
- maintainers could prefer a different internal representation;
- reviewers disagree before the alternatives have been executed;
- a user has not supplied a design preference.

Treat those conditions as an autonomous comparative-evaluation assignment.

## Decision closure sequence

Continue through the following steps until one direction is selected, all directions are rejected, or a genuine authority boundary appears.

### 1. Recover the governing goals

Read the applicable charter, contribution instructions, architecture, public contracts, tests, recent changes, and adjacent implementations. State:

- the user-visible or operator-visible problem;
- the invariant the repair must preserve;
- compatibility promises;
- performance, safety, and maintenance constraints;
- which project goals outrank local convenience.

### 2. Research precedent

Search primary material first:

- earlier source changes and retained commit history;
- current tests and comments that encode intent;
- official specifications and project documentation;
- implementations of the same boundary elsewhere in the codebase;
- closely related first-party projects;
- prior issue and pull-request discussions as supplementary evidence.

Secondary explanations, technical articles, and talks may help form hypotheses. They must not silently replace current source or primary contracts.

For every precedent, record both the supported principle and the important difference from the current case.

### 3. Derive decision criteria before choosing

Write the criteria that distinguish the options. Typical criteria include:

- correctness under normal and adversarial ordering;
- preservation of current public behavior;
- ownership of state and cleanup;
- compatibility with existing integrations;
- failure observability and recovery;
- performance and memory cost;
- implementation complexity and future testability;
- reversibility;
- consistency with the project's own architecture.

Do not choose an implementation first and invent criteria afterward.

### 4. Instantiate competing approaches

When practical, create concrete alternatives on separate owned branches, commits, artifacts, or experiment directories.

Each alternative must name:

- the exact invariant it implements;
- changed-file fence;
- expected advantage;
- expected failure or cost;
- discriminating test or benchmark;
- source and base revisions;
- rollback boundary.

A paper design is acceptable when implementation would be unsafe, disproportionately expensive, impossible with available tools, or incapable of adding evidence. Record that reason.

### 5. Execute distinguishing controls

Run tests that can make one option lose. A useful comparison includes positive and negative controls rather than several implementations that all pass the same happy path.

Depending on the claim, compare:

- baseline and each candidate;
- common behavior and edge behavior;
- compatibility with old callers;
- failure, cancellation, retry, cleanup, and interruption paths;
- platform or runtime variation;
- latency, throughput, allocation, or retained state;
- source-map, diagnostic, and observability behavior;
- composed behavior with adjacent subsystems.

Record exact heads, commands, environments, workflow runs, jobs, results, and evidence limits.

### 6. Seek adversarial cross-review

Give reviewers concrete targets. Ask them to:

- identify a counterexample;
- find a caller or precedent the comparison missed;
- explain which criterion is wrong or incomplete;
- propose the smallest test that would reverse the recommendation;
- inspect the complete diff and current base;
- verify that the winning result did not widen authority or silently drop compatibility.

Conflicting reviews trigger reconciliation in the canonical finding, additional execution, or a narrower split. They do not automatically trigger a user question.

### 7. Select a provisional winner

The coordinator or current worker may select a direction when the evidence establishes a clear winner under the recorded criteria.

Record:

- the winning option and why;
- losing options and the evidence that defeated them;
- remaining uncertainty;
- exact next implementation or execution gate;
- the condition that would reopen the decision.

A provisional selection may advance to implementation, execution, or review without asking the user to restate the technical judgment.

### 8. Escalate only a non-delegable decision

A human decision is justified when the remaining choice depends on one or more of:

- authorization for public upstream interaction;
- merge, release, deployment, or production authority;
- access to private, personal, regulated, or production data;
- material spending or resource commitment;
- product values, business priority, acceptable risk, or compatibility policy absent from repository evidence;
- an irreversible or high-impact action;
- credentials, secrets, legal commitments, or identity-bound approval;
- an explicit instruction reserving the decision to a person.

The escalation must say why further source research, prototypes, or execution cannot settle the choice. Present the smallest possible question and preserve the best autonomous recommendation.

## States and routing

### `comparative-evaluation-active`

Use when several plausible approaches remain and research, prototypes, or discriminating execution can still reduce uncertainty. This is active work, not a human blocker.

### `review-ready`

Use when one preferred direction or bounded conclusion is ready for independent exact-head examination. Reviewers may accept, repair, execute, hold for missing evidence, or reject it.

### `design-decision-ready`

Use sparingly. It means the comparative packet is complete and the remaining decision is genuinely non-delegable under the escalation rule above. It must never mean only that multiple technical implementations exist.

### `delivery-gate-ready`

Use when one canonical implementation exists and bounded execution, cleanup, restacking, or final review remains.

### `land-ready`

Use only under the existing exact-head acceptance and delivery rules. Autonomous technical selection does not grant merge or upstream authority.

## Multiple prototypes and canonical findings

Competing implementations may exist concurrently.

- Keep each implementation on a separate owned branch or clearly separated commit series.
- Keep evidence in unique paths under the canonical finding directory.
- Give every option a stable identifier such as `A`, `B`, or `C`.
- Use one comparison file or section to apply the same criteria to all options.
- Do not merge several alternatives into one ambiguous implementation PR.
- Close or archive losing carriers only after their evidence and rejection reason are retained.
- Reconcile the winning candidate against exact current canonical inputs after selection. Rebase or restack when movement overlaps the candidate, changes governing protocol, material configuration or generated inputs, indirect dependencies, promotion or mergeability requirements, or when a current-base promotion package is required.
- A prior disposition may carry forward without fresh review only when every disposition-relevant reviewed path is byte-identical across old and new generations and every governing-input generation named by the receipt is unchanged. Record exact old/new generations, old/new blob identities for every reviewed path, governing-input equality, and `changed reviewed paths: none`. File-disjoint movement alone is not sufficient.
- Any changed reviewed byte or changed governing input requires a fresh review receipt, even when the new reviewer concludes that the change is semantically equivalent. Renew only the receipts and controls whose input or execution identity changed; never present an expired receipt as current.

## Decision record requirements

A design comparison must include:

```text
Question: <bounded choice>
Governing invariant: <what must remain true>
Project goals and contracts: <sources>
Options instantiated: <branches, commits, artifacts, or reason paper-only>
Decision criteria: <ordered list>
Discriminating controls: <tests, benchmarks, adversarial cases>
Results by option: <exact receipts>
Historical precedent: <primary sources and differences>
Independent criticism: <reviews and counterexamples>
Selected direction: <winner or all rejected>
Reopening trigger: <new evidence that changes the result>
Non-delegable human decision: <none or smallest exact question>
Upstream contact authorized: no | exact authority
```

## Stop conditions

Stop autonomous comparison when:

- one option clearly wins and the next gate is implementation or validation;
- all options fail and the finding becomes a retained negative result;
- the question splits into independently owned findings;
- the remaining uncertainty is immaterial to the bounded transition;
- a non-delegable decision is precisely identified;
- further work would exceed an explicit safety, privacy, authority, or cost boundary.

Do not stop merely because thinking is hard, the precedent is mixed, or the first candidate passed.
