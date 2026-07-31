# Agent Instructions

These instructions apply to every AI system and automated worker operating in this repository.

## Entry protocol

- `START_HERE.md` is the current transitional repository entry point. When that runbook sends you here, continue with these rules and do not restart the entry sequence.
- Apply the universal agent rules in this file. Use the assignment and current phase to select the deeper research, execution, review, coordination, finding, decision, workspace, batch, testbed, or integration manuals indexed by `START_HERE.md`; do not treat this file as a second mandatory reading list.
- Search programme hubs, target hubs, open Fieldwork issues, active pull requests, canonical findings, investigation workspaces, active batches, existing experiments, contexts, testbeds, campaign folders, and owned-fork branches before creating work.
- Treat GitHub issues as live coordination, canonical findings as the current technical answer, workspaces as orientation, and repository files as durable evidence.
- Work only from an explicit assignment, claimed scout or lane, requested synthesis, user-directed triage task, bounded review task, or bounded fork-free experiment.
- This transitional protocol does not define dispatch, typed lease or authority state, lifecycle status, effective currentness, or controller-observed currentness. Those semantics remain outside S0 until an exact structured-state generation is independently accepted; a later clean kernel successor must reference the architecture under review in #306 or its accepted successor rather than copy those fields into another prose payload.

## Programme, target, and testbed indexing

- Every long-lived cross-target direction carries `programme:<slug>` and links to the programme hub recorded in `programmes/registry.yml`.
- Every issue about a recurring repository, project, protocol, or system carries the appropriate `target:<slug>` label and links the stable target hub when one exists.
- Create a target hub only when recurring work justifies one; do not turn every registry entry into an issue.
- Apply `testbed:<slug>` only after a real owned-repository trial begins and follow `TESTBEDS.md`.
- If the owned repository itself is under investigation, use it as the target rather than the testbed.
- Programme, target, testbed, finding, workspace, review, and desk indexes are discovery surfaces, not automatic permission to work, merge, or contact upstream.

## Issue state, finding state, workspace phase, and output status

Do not collapse these concepts.

- `Issue state:` is the live `state:*` GitHub label and must agree with the issue metadata.
- `Finding state:` is the technical transition from `FINDINGS.md` and lives in the canonical finding.
- Workspace phase describes coordinator activity only.
- Canonical output status describes one audience-specific presentation artifact only.

An issue may be `state:claimed` while its finding is `comparative-evaluation-active`. Review and automation must version and validate issue state and finding state separately.

## Canonical findings

- Materialize one `findings/F<issue>-<slug>/finding.md` when an investigation has a retained conclusion, implementation candidate, comparison, review state, or decision boundary.
- Begin with `## In simple words` and keep the current answer, consequence, invariant, system map, claim table, alternatives, edge cases, precedent, exact receipts, transition, clearing condition, and reopening trigger current.
- Workers own unique evidence, artifact, and review paths. The canonical finding is a shared reviewed integration surface; only one edit merges at a time.
- Issue comments are short routing notices. They do not replace the finding.
- Synchronize the issue, finding, implementation PR, execution receipt, Review Queue, and Delivery Desk whenever a disposition-relevant conclusion changes.

## Investigation workspaces

- Use a workspace only when several findings, alternatives, source candidates, workers, or audience-specific outputs need one front door.
- The workspace `README.md` is coordinator-owned orientation. It does not replace findings, issues, implementation PRs, reviews, or delivery authority.
- Workers write unique files under workspace evidence, alternatives, precedent, artifacts, or reviews.
- Preserve explicit disagreements until evidence or a decision resolves them.
- Target-specific workspace adoptions should remain separable from the stable workspace protocol so target drift does not expire protocol review.

## Autonomous technical decisions

Follow `DECISIONS.md` when several technical approaches remain.

- Recover project goals and public contracts.
- Research primary precedent and state important differences.
- Derive decision criteria before choosing.
- Instantiate useful alternatives when practical.
- Run controls that can make an option lose.
- Seek adversarial cross-review.
- Select the best-supported provisional winner, retain losing reasons, and name a reopening trigger.

Use `comparative-evaluation-active` while autonomous technical work can still distinguish options. Use `design-decision-ready` only when the remaining choice depends on authority, values, private context, material cost, irreversible risk, credentials, legal commitment, or an explicit human reservation.

## Scout lanes

- A scout maps the lay of the land without assuming a specific bug, mechanism, patch, or failure class already exists.
- A programme thesis defines broad responsibility; it is not a checklist of expected findings.
- Pin the target revision at claim time and use the exact programme, target hub, question, owned path, and stop condition from the issue.
- Read implementation, tests, call sites, configuration, generated boundaries, recent changes, and relevant issue context.
- Map architecture, public contracts, control and data flow, state ownership, side effects, tests, and actual or representative use before selecting a narrow hypothesis.
- A worked example, context pattern, canonical case pack, previous campaign, or familiar bug class must not become the default lens for unrelated research.
- Reusable fixtures are tools for testing a discovered question, not a method for choosing the question.
- Produce at least one runnable probe, adversarial case, realistic testbed scenario, or explicit reason none is feasible after the map identifies a useful property.
- Return ranked branch candidates with consequence, likely owning boundary, evidence needed, and a recommendation to stop, retain a finding, open a campaign, or run another scout.
- A code tour or repository summary alone is not a completed scout.
- Do not create child campaigns without a concrete current behavior or missing capability, consequence, likely code boundary, falsifiable evidence path, and bounded next question.

## Plain-language check

Begin every durable programme hub, target hub, scout report, canonical finding, workspace front door, campaign, lane report, retained experiment, integration trial, context dossier, synthesis, and review packet with `## In simple words`.

State what the system is, where it sits, what is wrong or uncertain, why the result could be useful, and the current answer or next step. Keep the block short enough to reveal whether the model is understood, update it when the conclusion changes, and do not omit a caveat that changes the meaning.

## Code-first investigation

- Read the actual implementation, tests, call sites, configuration, generated boundaries, and failure paths before proposing a change.
- Map entrypoints, control and data flow, state ownership, side effects, cleanup, public contracts, invariants, and test blind spots.
- Use recent issues and pull requests for context, not as a substitute for source understanding or as a menu of work.
- Before promoting work, state a change thesis: current behaviour, consequence, proposed improvement, evidence, and boundary.
- Prefer correctness, security, data integrity, lifecycle, recovery, performance, compatibility, interoperability, and demonstrated ergonomics work. This is a value filter, not a preset checklist.
- A refactor must simplify or protect a consequential path, make an invariant testable, enable a demonstrated fix, or produce a measurable benefit.
- Do not actively hunt documentation edits, wording, spelling, style-only cleanup, generic lint rules, speculative abstractions, or unmeasured micro-optimizations.
- Documentation may accompany substantive work or resolve confusion that blocks correct use.
- A deep investigation may correctly end with no proposed change. Retain the negative result.

## External-reference rule

Follow `REFERENCE_POLICY.md`.

Before creating or editing Fieldwork conversation text containing third-party GitHub work, use the equivalent `redirect.github.com` URL, remove external shorthand, and use the intentional-upstream marker only for the specifically authorized interaction.

Tracked repository notes, findings, reports, maps, JSON records, and other files may use ordinary direct links. The interaction workflow is a last-resort detector; prevention by automated writers is mandatory.

## Experiments and integration trials

- Small one-worker experiments may be created under `playgrounds/` with a stable `EXP-YYYYMMDD-short-name` directory and `templates/experiment.json`.
- State one bounded question, exact command, environment, source revisions, claim scope, stop condition, and upstream-contact authorization.
- Reuse `playgrounds/cases/` only when those inputs distinguish hypotheses already grounded in the assignment. Do not select a research topic merely because a case pack exists.
- Default to synthetic inputs and no network access.
- One experiment has one owner; parallel variants use separate directories.
- Retain a human-readable result when another worker, finding, report, or decision may rely on it.
- Promote a disposable experiment to a finding, probe, lane, regression fixture, integration trial, or context dossier when another record depends on it.
- A playground never authorizes upstream contact.
- Use an owned repository when realistic lifecycle, cross-component behaviour, or API ergonomics cannot be judged from a toy model. Choose a testbed that naturally exercises the target; do not manufacture an unrelated integration.
- Work on a dedicated branch with one owner and record exact target and testbed revisions, baseline, candidate, correctness, ergonomics, failure recovery, and measured performance where relevant.
- Keep trials reversible and off production systems. Do not publish private repository names or content by default; use neutral identifiers and redacted evidence.
- A useful trial may become an owned-project feature even when no upstream work follows.
- One model or one testbed does not prove ecosystem demand or an upstream contract.
- Use `templates/integration-trial.md`.

## Integration context and citations

- Name the widest claim supported: `mechanism`, `interface`, `integration`, `operational`, or `ecosystem`.
- Do not describe a toy model or one owned testbed as proof of general adoption, production impact, or ecosystem need.
- When claiming wider consequence or importance, create or link an integration-context dossier under `contexts/`.
- Label consequential statements as `Normative`, `Documented`, `Observed`, `Inferred`, `Illustrative`, or `Unknown`.
- Prefer primary sources and record title, stable URL, version or revision, retrieval date, exact supported claim, section or path, and limitations.
- Distinguish actual callers and deployments from plausible examples.
- State what the small model or testbed preserves and what it omits.
- A context pattern is optional support, never an automatic hypothesis for a target.
- When warranted, split broader context into mechanism, usage, contract, operations, and adversarial lanes rather than blurring them together.

## Review, evidence, and promotion

- Read and apply `REVIEWING.md` before reviewing, promoting, marking ready, accepting, or merging work.
- Classify every item as owned product delivery, upstream-fork research, execution carrier, evidence/documentation, or blocked/security-sensitive work.
- Name the canonical branch and exact head. Never treat a temporary workflow branch or execution PR as the merge candidate.
- Classify each disposition-relevant claim separately as `source-read`, `model-executed`, `target-test-prepared`, `target-executed`, `integration-executed`, or `full-gate`.
- A record may list `Evidence classes present`; it must not assign one strongest class to the whole work.
- Never describe a prepared test as executed, a focused run as a full gate, one platform as cross-platform, or green CI as proof of an untested authority property.
- Review the complete current diff. Any code-head or reviewed-input movement expires a disposition unless semantic identity is proved.
- Builders may record self-review, but consequential implementation, security, authority, and upstream packets should receive independent final review.
- Keep PR descriptions, issue state, finding state, dependencies, supersession, and check status current.
- Close or clearly retire execution carriers after evidence reaches the canonical source record and a later exact head proves temporary workflows absent.
- Use explicit `ACCEPT`, `REPAIR`, `HOLD`, `EXECUTE`, or `REJECT` dispositions and name the exact next transition.

## Default behaviour

- Treat external observation as quiet research.
- Never open, comment on, react to, or modify upstream work without an explicit user instruction for that interaction.
- Never manufacture contribution volume, low-value cleanup, or speculative patches.
- Do not claim a reproduction, test result, benchmark, policy, maintainer position, use case, or consequence without evidence.
- Preserve exact source revisions, retrieval dates, environments, commands, uncertainty, contradictions, alternative architectures, and negative results.
- Do not rely on chat history as the only record of work.
- A target map is not required before quietly examining an assigned public repository.

## Batch, parallel work, and write modes

- Read the programme, batch, campaign, parent issue, finding, and workspace before beginning.
- Use the exact assignment ID, programme label, target label, deliverable, owned path, dependencies, source revision, claim scope, and stop condition.
- One scout, lane, probe, experiment, integration trial, mutable branch, or shared output path has one owner. Parallel variants use separate branches or unique evidence paths.
- Do not edit another worker's result, testbed branch, registry, manifest, status, synthesis, decision, workspace front door, or closeout without an explicit ownership handoff.
- For one-shot probes, write only the assigned result file or post a complete handoff marked `needs:materialization`.
- Claim coordinated work before substantial investigation.
- When evidence changes another assignment's premise, report the dependency in both records.
- Finish with the handoff protocol in `START_HERE.md` and `COORDINATION.md`.

Write modes:

1. **Fieldwork PR** — preferred for a durable scout, lane, finding, workspace, or coherent result set.
2. **Issue handoff** — use when repository writes are unavailable; include the complete result and apply `needs:materialization`.
3. **Coordinator materialization** — combine accepted issue-only handoffs without changing their evidence class.
4. **Playground experiment** — bounded local test with no shared coordination or upstream modification.
5. **Integration trial** — owned repository used for realistic lifecycle or integration evidence.
6. **Context dossier** — sourced integration, operational, or ecosystem interpretation.
7. **Canonical finding** — current retained technical answer and transition.
8. **Investigation workspace** — orientation across several findings or outputs.
9. **Execution carrier** — temporary evidence-producing branch or PR that identifies the canonical source, returns a receipt, and then closes.

Never have multiple workers push shared files directly to `main`.

## AI-assisted implementation and safety

Generated code is a candidate until tested and reviewed. A human remains responsible for every upstream claim and submitted line. Follow each target project's current contribution and AI-disclosure policy. Keep changes bounded and do not rewrite unrelated files for convenience.

Do not retain secrets, access tokens, private repository content, personal data, or production payloads. Use synthetic fixtures or redacted evidence whenever possible.

No Fieldwork record, workspace, finding, playground, testbed, or owned fork authorizes public upstream contact. Direct interaction requires a specific user instruction and a durable authority record.
