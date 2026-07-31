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

### 8. Resolve a genuine technical tie autonomously

A tie exists only when all of the following are true:

- the decision is one bounded question and a single answer is actually required;
- the options are specified well enough to implement or execute;
- the same predeclared criteria have been applied to every option;
- no new technical point remains unexplored;
- available prototypes, controls, precedent, and cross-review do not establish a material winner.

Preference, repetition, review volume, branch age, author identity, and the order in which options were proposed do not create or resolve a technical tie.

#### Blocking-objection rule

A technical objection blocks selection only when it identifies:

- the violated invariant or criterion;
- the exact source, precedent, counterexample, or executed receipt supporting the objection;
- the smallest control that could confirm or reverse it;
- a repair, alternative, or explicit reason no safe alternative exists.

An unsupported `-1`, aesthetic preference, or repeated concern whose technical substance has already been answered is retained as dissent but does not block progress. A reviewer may narrow the next transition or require a control without becoming the permanent owner of the decision.

#### Tiebreak ladder

Apply these steps in order and record the first step that resolves the choice.

1. **Make the objection executable.** Build the smallest prototype, benchmark, model, compatibility fixture, or failure injection that can make one option lose. Cheap code is the default response to cheap uncertainty.
2. **Call rough consensus on the objections, not on vote count.** A worker who did not author the competing candidates reviews the frozen packet and determines whether every material objection has been answered. Dissent may remain after its technical concern is addressed. The consensus caller records the objections, answers, unresolved limits, and selected direction.
3. **Advance multiple options when coexistence is safe.** When no single interoperable answer is required, retain both behind an experiment, read-only shadow path, feature flag, compatibility adapter, or separately owned deployment-neutral probe. Define the observation that will later choose or retire an option.
4. **Use ordered engineering defaults when one option is required.** Prefer, in order: satisfaction of the governing invariant; preservation of public compatibility; least authority and smallest irreversible effect; best rollback, observability, and failure containment; strongest target precedent; lower operational and maintenance burden; then the smaller reviewable diff. Do not reorder these criteria after seeing the result.
5. **Use a neutral arbiter for a residual unresolved tie.** Select one eligible reviewer who did not author any candidate and holds no affected writer lease. Freeze the complete comparison packet before selection. The arbiter reads that exact generation and may request one final discriminator. A requested discriminator produces new evidence: add it to the packet, freeze a new exact generation, and restart this step before any selection. Only a frozen packet that proves the remaining options materially equivalent and reversible permits the arbiter to make an explicitly arbitrary choice rather than inventing a technical distinction. The arbiter publishes the selected option, the equivalence and reversibility basis, retained limits, and reopening trigger. The choice is recorded once for that frozen generation and is not retried merely to obtain another option. Any later packet change expires the choice and returns the work to the applicable earlier ladder step. The receipt records a public-safe worker-instance identity and eligibility basis; a shared GitHub login alone is insufficient. The arbiter cannot grant merge, release, deployment, spending, credential, data, or upstream-contact authority.

For low-risk internal work that is reversible and has an explicit rollback, the active owner may proceed under lazy execution after recording the candidate, controls, and absence of a live unanswered technical objection. A later objection may reopen or reverse the choice with new evidence; it does not erase the exact evidence already produced.

#### Appeals and reopening

A settled technical choice reopens only for:

- new source or executed evidence;
- a previously omitted governing criterion;
- a counterexample that invalidates the selected invariant;
- target, dependency, or compatibility movement that changes the comparison;
- failure of an assumption named in the decision record.

Restating a preference, changing reviewer identity, or disliking an explicitly arbitrary choice between verified materially equivalent reversible options is not a reopening trigger.

### 9. Escalate only a non-delegable decision

A human decision is justified when the remaining choice depends on one or more of:

- authorization for public upstream interaction;
- merge, release, deployment, or production authority;
- access to private, personal, regulated, or production data;
- material spending or resource commitment;
- product values, business priority, acceptable risk, or compatibility policy absent from repository evidence;
- an irreversible or high-impact action;
- credentials, secrets, legal commitments, or identity-bound approval;
- an explicit instruction reserving the decision to a person.

The escalation must say why further source research, prototypes, execution, neutral review, or the tiebreak ladder cannot settle the choice. Present the smallest possible question and preserve the best autonomous recommendation.

## Decision-process precedent

This protocol adapts established project-governance patterns rather than treating any one process as universal:

- IETF RFC 7282 treats rough consensus as resolution of technical objections rather than a vote count and gives running engineering evidence substantial weight: https://www.rfc-editor.org/rfc/rfc7282
- IETF RFC 3929 describes external review, preference review, qualified neutral selection, and random assignment for the narrow case where ordinary consensus is blocked; random assignment is reserved for choices with no remaining technical distinction: https://www.rfc-editor.org/rfc/rfc3929
- Apache uses do-ocracy and lazy consensus for ordinary progress while requiring a technically justified negative vote and an explanation or alternative: https://www.apache.org/foundation/how-it-works/ and https://www.apache.org/foundation/voting.html
- Python PEP 13 prefers consensus and standard processes, keeps a steering council as a final appeal mechanism, and permits random resolution for a residual election tie: https://peps.python.org/pep-0013/

Fieldwork differs because workers can cheaply instantiate several technical alternatives. Therefore prototype-and-control evidence comes before neutral arbitration. For a residual materially equivalent and reversible choice, Fieldwork records one neutral non-author arbiter's explicitly arbitrary selection instead of pretending chooser-controlled hashing creates neutrality.

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
- Give every option a descriptive stable identifier such as `A`, `B`, or `C` before executing the comparison.
- Use one comparison file or section to apply the same criteria to all options.
- Do not merge several alternatives into one ambiguous implementation PR.
- Close or archive losing carriers only after their evidence and rejection reason are retained.
- Reconcile the winning candidate against exact current canonical inputs after selection. Rebase or restack when movement overlaps the candidate, changes a governing protocol or other named input, changes promotion or mergeability requirements, or a current-base promotion package is required. A prior disposition may carry forward without fresh review only when every disposition-relevant reviewed path is byte-identical across the old and new generations and every governing input generation named by the prior receipt is unchanged, including governing protocol, material configuration or generated inputs, indirect dependencies, and promotion or mergeability requirements. Record the old and new exact generations, old/new blob identities for every reviewed path, governing-input equality, changed reviewed paths (`none` for carry-forward), and the exact controls and review identities renewed. File-disjoint movement is supporting evidence only. Any changed reviewed byte or governing input requires a fresh review, even when that fresh review later concludes semantic equivalence. Never present an expired receipt as current.

## Decision record requirements

A design comparison must include:

```text
Question: <bounded choice>
Decision record generation: <exact file head or issue body revision>
Comparison base: <exact SHA fixed before candidate execution>
Governing invariant: <what must remain true>
Project goals and contracts: <sources>
Options instantiated: <branches, commits, artifacts, or reason paper-only>
Stable option IDs and complete option set in the frozen packet: <IDs>
Decision criteria: <ordered list fixed before results>
Discriminating controls: <tests, benchmarks, adversarial cases>
Results by option: <exact receipts>
Historical precedent: <primary sources and differences>
Blocking objections: <objection, evidence, reversing control, alternative>
Independent criticism: <reviews and counterexamples>
Rough-consensus caller or neutral arbiter: <public-safe worker identity, eligibility, non-authorship, no affected lease>
Tiebreak ladder step used: <none or exact step>
Residual-equivalence selection: <not applicable or frozen generation, equivalence/reversibility finding, arbiter, one recorded choice>
Selected direction: <winner or all rejected>
Retained dissent: <answered concern that did not block>
Reopening trigger: <new evidence that changes the result>
Non-delegable human decision: <none or smallest exact question>
Upstream contact authorized: no | exact authority
```

## Stop conditions

Stop autonomous comparison when:

- one option clearly wins and the next gate is implementation or validation;
- the tiebreak ladder selects a reversible direction and records its reopening trigger;
- all options fail and the finding becomes a retained negative result;
- the question splits into independently owned findings;
- the remaining uncertainty is immaterial to the bounded transition;
- a non-delegable decision is precisely identified;
- further work would exceed an explicit safety, privacy, authority, or cost boundary.

Do not stop merely because thinking is hard, the precedent is mixed, reviewers disagree, or the first candidate passed.
