# Method

## In simple words

Start with a concrete system question. Understand the code and explain it simply. Reproduce the important behaviour. Try it in a realistic owned application when that adds evidence. Propose change only when the consequence and improvement are demonstrated.

Fieldwork is organised around bounded **campaigns**. A campaign can end in a patch, an issue draft, a design proposal, a published finding, an owned-project improvement, a local workaround, or a negative result.

Third-party upstream repositories are permanently read-only to Fieldwork agents. Agents may prepare upstream-facing material; a human must perform any actual upstream interaction manually.

## 1. Target and question

Identify the target hub and apply the correct `target:<slug>` label.

State one falsifiable question or concrete failure. A useful question names the operation, boundary, and disputed outcome. “Improve the SDK,” “find something to contribute,” and “make the project more robust” are not research questions.

Record the current search lens when one is active. A lifecycle-error season may intentionally emphasize settlement, cleanup ownership, cancellation, or stale publication. That emphasis is temporary, not a universal ranking of defect classes. Periodically sample outside the active lens and rotate toward compatibility, protocol identity, parsing, type boundaries, security, performance, data integrity, integration, or demonstrated ergonomics when the current stream becomes repetitive.

## 2. Plain-language model

Before detailed investigation, write `## In simple words` following `PLAIN_LANGUAGE.md`.

Lead with either:

> I propose changing X so that Y remains true when Z happens.

or:

> Does X still own the right to publish after Y transfers authority to Z?

Then show the current and proposed mechanics using the clearest representation available. For computing concepts, code, pseudocode, an arrow diagram, a state table, or a sequence trace may be plainer than several paragraphs. Bullet lists are optional rather than the default.

Update the explanation as understanding changes.

## 3. Code reconnaissance

Follow `CODE_FIRST.md`. Before implementation, establish the target repository and exact source revision; relevant entrypoints, modules, and call sites; control and data flow; state ownership and side effects; error, cancellation, retry, cleanup, and recovery paths; public contracts and generated boundaries; relevant tests and uncovered conditions; contribution and AI-assistance policies; current behaviour and expected behaviour; the suspected failure boundary; and what would disprove the hypothesis.

Recent issues, discussions, and prior patches are supplementary context. External references remain quiet under [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md).

## 4. Change thesis

Before promoting implementation, make this transition visible:

```text
current behaviour
      │
      ├── concrete consequence
      ▼
proposed behaviour
      │
      ├── invariant to preserve
      └── evidence required
```

Prefer security, correctness, data integrity, lifecycle, recovery, performance, compatibility, integration, demonstrated ergonomics, and meaningful refactors.

Documentation, spelling, lint, style, and cosmetic cleanup are not active research goals. They may support a substantive change or resolve confusion that blocks correct use.

## 5. Reproduction

Reduce the observation to the smallest useful case. Record the environment and versions, exact setup and invocation, expected and actual results, determinism, retained fixtures or synthetic inputs, safety constraints, the realistic property preserved by the reduction, and what it omits.

A reproduction may be easier to inspect as executable code or a compact trace than as prose.

## 6. Hypotheses

State competing explanations before committing to a patch. Rank them by plausibility and define the experiment that distinguishes them.

Separate **causal diagnosis** from **repair ownership**. Proving where bad state becomes visible, or which mechanism produces the failure, does not prove that the same location owns the repair. Before promoting a candidate, ask which layer established or violated the relevant invariant, whether an earlier owner can prevent the bad state instead of repairing it downstream, and what adjacent implementation, history, or contract would make the local fix lose. Use a discriminator capable of leaving the diagnosis intact while showing that the proposed repair belongs somewhere else.

## 7. Experiments

Prefer tests that isolate one claim. Useful evidence includes failing regression tests, reduced fixtures, compatibility matrices, benchmarks with baselines and variance, traces, protocol transcripts, fault injection, deterministic replay, source-level instrumentation, adversarial inputs, lifecycle models, and generated candidates tested against explicit invariants.

### Evidence and hardening loop

A productive candidate often moves through this sequence:

```text
observed anomaly
      ↓
source-level ownership/state model
      ↓
target-native FAIL on the relevant baseline
      ↓
small repair
      ↓
target-native PASS
      ↓
adjacent boundary probes
      ↓
relevant CI and compatibility checks
      ↓
clean hold-ready candidate
```

Treat each step as an evidence gate rather than a ritual. A source suspicion is not a candidate until the disputed behaviour is reproduced or otherwise demonstrated. A nearby hypothesis suggested by one finding is useful, but it should be isolated and tested independently before being promoted.

Record invalid probes as invalid instead of quietly replacing their history. If timing, setup, middleware mode, caching, or another experimental condition made a test answer the wrong question, preserve that explanation and rerun a corrected experiment.

When broad CI fails, classify the failure before changing the candidate: distinguish the target regression, an unrelated product test, a platform-specific signal, and formatting or other hygiene. Rerun a failed job only when the evidence makes a transient or unrelated failure plausible, and retain the original and rerun receipts.

Once the behaviour, repair, and compatibility story are stable, preserve the exploratory history separately and prepare one minimal reviewable branch or commit. Further research should not force a proven candidate to carry experiment history.

Use fork-free playgrounds when no upstream modification is required. Do not retain secrets, personal data, production credentials, or proprietary upstream content.

## 8. Owned-repository integration trial

When isolated evidence cannot answer application-lifecycle, integration, deployment, or ergonomics questions, select an owned repository under `TESTBEDS.md`.

Record the target and target hub, exact target and testbed revisions, one owned trial branch, the realistic scenario, baseline and candidate behaviour, correctness and ergonomics observations, measured performance where relevant, failure and recovery paths, cleanup and rollback, and what the trial proves and does not prove.

A successful trial may become a feature in the owned project even when no upstream change follows.

## 9. Integration context

When claiming wider use, downstream dependence, operational consequence, or ecosystem importance, follow `INTEGRATION_CONTEXT.md`.

Separate documented use, directly observed behaviour, inference, illustrative scenarios, and unknowns. Use primary sources and record exact claims, versions, retrieval dates, sections, and limitations.

## 10. Decision gate

Choose one outcome: continue research, retain an owned-project improvement, keep a local workaround, publish a finding, prepare a human-facing upstream packet, prepare a patch in an owned fork, or stop.

The decision must explain why the chosen action is worth its implementation and review cost.

## 11. Upstream packet

Prepare the problem, reproduction, demonstrated cause or bounded uncertainty, proposed direction, invariant, scope, evidence, compatibility and security consequences, rejected alternatives, recovery path, required AI-assistance disclosure, and confirmation that the human submitter reviewed and can defend every line.

Start with the proposal. Use code-shaped explanation for mechanics and prose for judgment. Do not force a maintainer to excavate the requested change from a dossier.

Use [`templates/upstream-packet.md`](templates/upstream-packet.md).

An upstream packet is preparation-only. It never authorizes an automated write to the third-party repository.

## 12. Fork and implementation

Candidate upstream code belongs in an owned fork or branch associated with the campaign. Keep commits reviewable and avoid unrelated cleanup. Preserve the research dossier independently of the fork.

Candidate owned-project code belongs on its recorded testbed branch and follows that repository's standards.

## 13. Human submission and review

If a human decides to contact upstream, the human performs that interaction manually outside Fieldwork automation. Agents must not create, update, comment on, review, react to, label, merge, rerun, push to, or otherwise mutate the third-party upstream repository, even when explicitly asked.

After a human-performed interaction exists, Fieldwork may record the submitted state, exact link, review feedback, revisions, decisions, and final outcome. Recording a human action is not permission for the agent to continue the upstream conversation.

## 14. Closeout

Every campaign ends with a plain-language result, outcome and date, exact submitted and tested revisions where a human submission exists, what was learned, consequence established, unresolved uncertainty, reusable artifacts, owned-project changes retained, follow-up conditions, ledger entries, and a negative result where applicable.
