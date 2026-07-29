# Method

Fieldwork is organised around bounded **campaigns**. A campaign can end in a patch, an issue, a design proposal, a published finding, a local workaround, or a negative result.

## 1. Question

State one falsifiable question or concrete failure.

Good:

- Why does streamed tool state diverge after reconnection?
- Which lifecycle transition loses the successful result when cleanup fails?
- Can a generated declaration preserve receiver requirements without widening user-defined types?

Weak:

- Improve the SDK.
- Find something to contribute.
- Make the project more robust.

## 2. Reconnaissance

Before implementation, record:

- target repository and exact source revision;
- relevant modules and execution path;
- existing documentation, issues, discussions, and prior patches;
- contribution and AI-assistance policies;
- current behaviour and expected behaviour;
- suspected failure boundary;
- what would disprove the hypothesis.

External issue and pull-request references remain quiet under [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md).

## 3. Reproduction

Reduce the observation to the smallest useful case. A reproduction should state:

- environment and versions;
- exact setup and invocation;
- expected and actual results;
- whether it is deterministic;
- retained fixtures or synthetic inputs;
- safety constraints and excluded live systems.

## 4. Hypotheses

List competing explanations before committing to a patch. Rank them by plausibility and define the experiment that distinguishes them.

## 5. Experiments

Prefer tests that isolate one claim. Useful evidence includes:

- failing regression tests;
- reduced fixtures;
- compatibility matrices;
- benchmarks with baselines and variance;
- traces and protocol transcripts;
- fault injection;
- deterministic replay;
- source-level instrumentation;
- adversarial inputs.

Do not retain secrets, personal data, production credentials, or proprietary upstream content.

## 6. Decision gate

Choose one outcome:

- **continue research** — evidence remains insufficient;
- **local workaround** — the problem matters locally but upstream work is unjustified;
- **publish finding** — useful result, no code change needed;
- **seek upstream direction** — design or policy input is required;
- **prepare patch** — scope and acceptance criteria are understood;
- **stop** — low value, disproved hypothesis, excessive risk, or unreceptive target.

The decision must explain why the chosen action is worth its review cost.

## 7. Upstream packet

Before contact, prepare:

- concise problem statement;
- exact reproduction;
- technical cause or bounded uncertainty;
- proposed direction and scope;
- tests and verification;
- compatibility and security consequences;
- rejected alternatives;
- recovery or rollback plan where relevant;
- AI-assistance disclosure appropriate to upstream policy;
- confirmation that the submitter reviewed and can defend every line.

Use [`templates/upstream-packet.md`](templates/upstream-packet.md).

## 8. Fork and implementation

Candidate code belongs in a fork or branch associated with the campaign. Keep commits reviewable and avoid unrelated cleanup. Preserve the research dossier independently of the fork.

## 9. Submission and review

Once contact is deliberate, change the campaign state to **Submitted**. Record review feedback, revisions, decisions, and final outcome without turning the dossier into a complaint log.

## 10. Closeout

Every campaign ends with:

- outcome and date;
- exact submitted or tested revision;
- what was learned;
- unresolved uncertainty;
- reusable artifacts;
- follow-up conditions;
- ledger entries;
- negative result where applicable.
