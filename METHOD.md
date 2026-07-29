# Method

## In simple words

Start with a concrete system question. Understand the code and explain it simply. Reproduce the important behaviour. Try it in a realistic owned application when that adds evidence. Propose change only when the consequence and improvement are demonstrated.

Fieldwork is organised around bounded **campaigns**. A campaign can end in a patch, an issue, a design proposal, a published finding, an owned-project improvement, a local workaround, or a negative result.

## 1. Target and question

Identify the target hub and apply the correct `target:<slug>` label.

State one falsifiable question or concrete failure.

Good:

- Why does streamed tool state diverge after reconnection?
- Which lifecycle transition loses the successful result when cleanup fails?
- Can a generated declaration preserve receiver requirements without widening user-defined types?
- Does this SDK encourage a caller to retry a side effect without preserving logical request identity?

Weak:

- Improve the SDK.
- Find something to contribute.
- Make the project more robust.
- Clean up the codebase.

## 2. Plain-language model

Before detailed investigation, write `## In simple words` following `PLAIN_LANGUAGE.md`:

- what the system or component is;
- where it sits;
- what responsibility or boundary is under study;
- why failure or improvement could be useful;
- the current answer or next step.

Update the explanation as understanding changes.

## 3. Code reconnaissance

Follow `CODE_FIRST.md`. Before implementation, record:

- target repository and exact source revision;
- relevant entrypoints, modules, and call sites;
- control and data flow;
- state ownership and side effects;
- error, cancellation, retry, cleanup, and recovery paths;
- public contract and generated boundaries;
- relevant tests and uncovered conditions;
- contribution and AI-assistance policies;
- recent issues, discussions, and prior patches as supplementary context;
- current behaviour and expected behaviour;
- suspected failure boundary;
- what would disprove the hypothesis.

External issue and pull-request references remain quiet under [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md).

## 4. Change thesis

Before promoting implementation, state:

1. current behaviour;
2. concrete consequence;
3. proposed improvement;
4. evidence required;
5. evidence boundary.

Prefer security, correctness, data integrity, lifecycle, recovery, performance, compatibility, integration, demonstrated ergonomics, and meaningful refactors.

Documentation, spelling, lint, style, and cosmetic cleanup are not active research goals. They may support a substantive change or resolve confusion that blocks correct use.

## 5. Reproduction

Reduce the observation to the smallest useful case. A reproduction should state:

- environment and versions;
- exact setup and invocation;
- expected and actual results;
- whether it is deterministic;
- retained fixtures or synthetic inputs;
- safety constraints and excluded live systems;
- what realistic property the reduction preserves;
- what it omits.

## 6. Hypotheses

List competing explanations before committing to a patch. Rank them by plausibility and define the experiment that distinguishes them.

## 7. Experiments

Prefer tests that isolate one claim. Useful evidence includes:

- failing regression tests;
- reduced fixtures;
- compatibility matrices;
- benchmarks with baselines and variance;
- traces and protocol transcripts;
- fault injection;
- deterministic replay;
- source-level instrumentation;
- adversarial inputs;
- lifecycle models;
- generated candidates tested against explicit invariants.

Use fork-free playgrounds when no upstream modification is required.

Do not retain secrets, personal data, production credentials, or proprietary upstream content.

## 8. Owned-repository integration trial

When isolated evidence cannot answer application-lifecycle, integration, deployment, or ergonomics questions, select an owned repository under `TESTBEDS.md`.

Record:

- target and target hub;
- `target:*` and `testbed:*` labels;
- exact target and testbed revisions;
- one owned trial branch;
- realistic scenario;
- baseline and candidate behaviour;
- correctness and ergonomics observations;
- measured performance where relevant;
- failure and recovery paths;
- cleanup and rollback;
- what the trial proves and does not prove.

A successful trial may become a feature in the owned project even when no upstream change follows.

## 9. Integration context

When claiming wider use, downstream dependence, operational consequence, or ecosystem importance, follow `INTEGRATION_CONTEXT.md`.

Separate:

- documented use;
- directly observed behaviour;
- inference;
- illustrative scenarios;
- unknowns.

Use primary sources and record exact claims, versions, retrieval dates, sections, and limitations.

## 10. Decision gate

Choose one outcome:

- **continue research** — evidence remains insufficient;
- **retain owned-project improvement** — the trial is useful locally regardless of upstream action;
- **local workaround** — the problem matters locally but upstream work is unjustified;
- **publish finding** — useful result, no code change needed;
- **seek upstream direction** — design or policy input is required;
- **prepare patch** — scope, consequence, and acceptance criteria are understood;
- **stop** — low value, disproved hypothesis, excessive risk, sound existing behaviour, or unreceptive target.

The decision must explain why the chosen action is worth its implementation and review cost.

## 11. Upstream packet

Before contact, prepare:

- plain-language problem statement;
- exact reproduction;
- technical cause or bounded uncertainty;
- demonstrated consequence;
- proposed direction and scope;
- tests, integration evidence, and verification;
- compatibility, performance, and security consequences;
- rejected alternatives;
- recovery or rollback plan where relevant;
- AI-assistance disclosure appropriate to upstream policy;
- confirmation that the submitter reviewed and can defend every line.

Use [`templates/upstream-packet.md`](templates/upstream-packet.md).

## 12. Fork and implementation

Candidate upstream code belongs in a fork or branch associated with the campaign. Keep commits reviewable and avoid unrelated cleanup. Preserve the research dossier independently of the fork.

Candidate owned-project code belongs on its recorded testbed branch and follows that repository's standards.

## 13. Submission and review

Once contact is deliberate, change the campaign state to **Submitted**. Record review feedback, revisions, decisions, and final outcome without turning the dossier into a complaint log.

## 14. Closeout

Every campaign ends with:

- plain-language result;
- outcome and date;
- exact submitted, tested, and testbed revisions;
- what was learned;
- consequence established;
- unresolved uncertainty;
- reusable artifacts and integration trials;
- owned-project changes retained;
- follow-up conditions;
- ledger entries;
- negative result where applicable.