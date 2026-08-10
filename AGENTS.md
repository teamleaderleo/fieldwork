# Agent Instructions

These instructions apply to every AI system and automated worker operating in this repository.

## Hard upstream-write prohibition

Third-party upstream repositories are permanently **read-only** to every Fieldwork agent and automated worker.

- Never perform a state-changing action against a third-party upstream repository. This includes creating or updating issues, pull requests, discussions, comments, reviews, reactions, labels, assignments, milestones, branches, files, commits, releases, workflow runs, merges, or any other repository state.
- This prohibition is unconditional. A user request, explicit authorization, campaign state, issue field, marker, target contribution policy, apparent intent, or available tool permission does **not** override it.
- If a user asks an agent to file, open, post, submit, reply, review, react, label, merge, rerun, push, or otherwise change upstream, stop at preparation. Produce the draft, patch, reproduction, test evidence, links, and exact manual steps the human needs, but do not invoke the upstream mutation.
- Agents may freely read and search public upstream material and may create or modify Fieldwork artifacts, owned repositories, and owned forks according to the rest of these instructions.
- Only a human may perform an upstream interaction, manually and outside Fieldwork automation. Agents may record that already-existing human interaction afterward.
- Any `upstream-contact authorization` field for an automated worker is always `false`. It is a status record, not a permission switch.

This rule takes precedence over any older Fieldwork text that could be read as permitting automated upstream contact.

## Entry protocol

- Start with `START_HERE.md`.
- Read `CHARTER.md`, `CODE_FIRST.md`, `PLAIN_LANGUAGE.md`, `METHOD.md`, `REFERENCE_POLICY.md`, `PROGRAMMES.md`, `TARGET_HUBS.md`, `EXPERIMENTS.md`, `TESTBEDS.md`, `INTEGRATION_CONTEXT.md`, `COORDINATION.md`, `REVIEWING.md`, and `BATCHES.md` before modifying research material.
- Search programme hubs, target hubs, open Fieldwork issues, active pull requests, active batches, existing experiments, contexts, testbeds, campaign folders, and owned-fork branches before creating work.
- Treat GitHub issues as live coordination and repository files as durable evidence.
- Work only from an explicit assignment, claimed scout or lane, requested synthesis, user-directed triage task, bounded review task, or bounded fork-free experiment.

## Activity refresh and autonomous continuation

- At the beginning of each work pass, refresh the live state of the relevant owned issues, pull requests, branches, reviews, workflows, queues, and any already-authorized upstream surface before choosing the next action.
- Refresh again after every material transition, including a push, head movement, CI completion, review arrival, superseding patch, duplicate discovery, or evidence transfer.
- Reconcile new activity immediately: inspect completed runs, classify failures, repair owned work, retire duplicates, update stale descriptions, and move evidence to the canonical branch or record.
- Queued CI or awaited review is not a stopping condition. Use that time for complete-diff review, adjacent bounded investigation, harness repair, evidence preservation, or another already-owned lane.
- Do not stop merely to report that work is queued, needs review, or needs repair when the authorized review or repair can be performed. Perform the work and report only a completed result, a genuine blocker, a safety or authority boundary, or a decision that actually requires the user.
- Before every handoff, perform one final activity refresh and make the durable record match the current exact head and live result.
- This loop never expands upstream-contact authority. New public interaction still requires the exact authorization described below.

## Programme, target, and testbed indexing

- Every long-lived cross-target direction carries `programme:<slug>` and links to the programme hub recorded in `programmes/registry.yml`.
- Every issue about a recurring repository, project, protocol, or system must carry the appropriate `target:<slug>` label.
- Link the work to the stable target hub recorded in `targets/hubs.yml` when one exists.
- Create a target hub only when recurring work justifies one; do not turn every registry entry into an issue.
- When an owned repository is used to exercise another target, apply `testbed:<slug>` only after the real trial begins and follow `TESTBEDS.md`.
- If the owned repository itself is under investigation, use it as the target rather than the testbed.
- Programme, target, and testbed registries are discovery surfaces, not automatic permission to work. They never authorize third-party upstream writes.

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

- Begin every durable programme hub, target hub, scout report, finding, campaign, lane report, retained experiment, integration trial, context dossier, synthesis, and review packet with `## In simple words`.
- State what the system is, where it sits, what is wrong or uncertain, why the result could be useful, and the current answer or next step.
- Keep the block short enough to reveal whether the underlying model is actually understood.
- Update it when the conclusion changes.
- Do not use a simplified explanation to omit a caveat that changes the meaning.

## Code-first investigation

- Read the actual implementation, tests, call sites, configuration, generated boundaries, and failure paths before proposing a change.
- Map entrypoints, control and data flow, state ownership, side effects, cleanup, public contracts, invariants, and test blind spots.
- Use recent issues and pull requests for context, not as a substitute for source understanding or as a menu of work.
- Before promoting work, state a change thesis: current behaviour, consequence, proposed improvement, evidence, and boundary.
- Prefer correctness, security, data integrity, lifecycle, recovery, performance, compatibility, interoperability, and demonstrated ergonomics work.
- This preference order is a value filter, not a preset research checklist.
- A refactor must simplify or protect a consequential path, make an invariant testable, enable a demonstrated fix, or produce a measurable benefit.
- Do not actively hunt documentation edits, spelling, style-only cleanup, generic lint rules, speculative abstractions, or unmeasured micro-optimizations.
- Documentation may accompany substantive work or resolve confusion that blocks correct use.
- A deep investigation may correctly end with no proposed change. Record the negative result.

## External-reference rule

Follow `REFERENCE_POLICY.md`.

Before creating or editing a Fieldwork or owned-fork issue, pull request, comment, review, inline review comment, or discussion containing third-party GitHub work:

- use the equivalent `redirect.github.com` URL unless recording an already-existing human-performed upstream interaction;
- remove external owner/repository item and commit shorthand where the policy requires it;
- use the intentional-upstream marker only to record an already-existing human-performed interaction;
- remember that the marker never authorizes an automated upstream write.

Repository notes, reports, maps, JSON records, and other tracked files may use ordinary direct links. They do not need the interaction preflight or an automated external-reference scan.

The interaction workflow is a last-resort detector. It cannot reliably stop GitHub from processing a direct reference at the instant an issue or comment is created. Prevention by automated writers is mandatory for interaction text.

## Fork-free experiments

- Small one-worker experiments may be created under `playgrounds/` without an upstream fork or Fieldwork issue.
- Use a stable `EXP-YYYYMMDD-short-name` directory and `templates/experiment.json`.
- State one bounded question, exact command, environment, source revisions, claim scope, stop condition, and upstream-contact authorization `false`.
- Reuse `playgrounds/cases/` only when those inputs can distinguish hypotheses already grounded in the assignment.
- Do not select research topics merely because a case pack or example exists.
- Default to synthetic inputs and no network access.
- One experiment has one owner; parallel variants use separate directories.
- Retain a human-readable result when another worker, report, or decision may rely on it.
- Promote the experiment to a finding, batch probe, campaign lane, regression fixture, integration trial, or integration-context dossier when it stops being disposable.
- A playground never authorizes upstream contact.

## Owned-repository integration trials

- Use an owned repository when realistic application lifecycle, cross-component behaviour, or API ergonomics cannot be judged from a toy test alone.
- Choose a testbed that naturally exercises the target; do not manufacture unrelated integrations.
- Work on a dedicated branch with one owner and record exact target and testbed revisions.
- Compare baseline and candidate behaviour, including correctness, ergonomics, failure recovery, and measured performance where relevant.
- Keep trials reversible and off production systems.
- Do not publish private repository names or content by default; use neutral identifiers and redacted evidence.
- A useful trial may become a real feature in the owned repository even when no upstream work follows.
- A testbed result does not prove ecosystem demand or an upstream contract.
- Use `templates/integration-trial.md`.

## Integration context and citations

- Name the widest claim supported by the evidence: `mechanism`, `interface`, `integration`, `operational`, or `ecosystem`.
- Do not describe a toy example or one owned testbed as proof of general adoption, production impact, or ecosystem need.
- When claiming wider usefulness, failure consequence, downstream dependence, or upstream importance, create or link an integration-context dossier under `contexts/`.
- Label consequential statements as `Normative`, `Documented`, `Observed`, `Inferred`, `Illustrative`, or `Unknown`.
- Prefer primary sources and record title, stable URL, version or revision, retrieval date, exact supported claim, section or path, and limitations.
- Distinguish actual callers and deployments from plausible examples.
- State what the small model or testbed preserves and what it omits.
- A context pattern is optional supporting material, never an automatic hypothesis for a target.
- A broader context may be researched in separate mechanism, usage, contract, operations, and adversarial lanes when the work warrants parallelization.

## Review, evidence, and promotion

- Read and apply `REVIEWING.md` before reviewing, promoting, marking ready, accepting, or merging work.
- Classify every review item as owned product delivery, upstream-fork research, execution carrier, evidence/documentation, or blocked/security-sensitive work.
- Name the canonical branch and exact head. Do not treat a temporary workflow branch or execution pull request as the merge candidate.
- Preserve the narrowest accurate evidence class: source-read, model-executed, target-test-prepared, target-executed, integration-executed, or full-gate.
- Never describe a prepared test as executed, a focused run as a full gate, one platform as cross-platform, or green CI as proof of an untested security or authority property.
- Review the complete current diff. Any head movement expires a disposition unless semantic identity is proved within the reviewed fence.
- Builders may record self-review, but consequential implementation, security, authority, and human-facing upstream packets should receive independent final review.
- Keep pull-request descriptions current. Remove stale dependency, branch, current-main, supersession, and running-check language after state changes.
- Issue-body `State:` text and live `state:*` labels must agree before promotion.
- Close or clearly retire execution carriers after evidence reaches the canonical branch.
- Use explicit `ACCEPT`, `REPAIR`, `HOLD`, `EXECUTE`, or `REJECT` dispositions and name the exact next transition.

## Default behaviour

- Treat external observation as quiet research.
- Never open, update, close, comment on, review, react to, label, assign, merge, rerun, push to, or otherwise mutate third-party upstream work. Explicit user instruction does not override this rule.
- Never manufacture contribution volume, low-value cleanup, or speculative patches.
- Do not claim a reproduction, test result, benchmark, policy, maintainer position, use case, or integration consequence without evidence.
- Preserve exact source revisions, retrieval dates, environments, and commands.
- Record uncertainty, contradictions, alternative architectures, and negative results.
- Do not rely on chat history as the only record of work.
- A target map is not required before quietly examining an assigned public repository.

## Batch and parallel work

- Read the programme, batch, campaign, or parent issue before beginning.
- Use the exact assignment ID, programme label, target label, deliverable, owned path, dependencies, source revision, claim scope, and stop condition.
- One scout, lane, probe, experiment, or integration trial has one owner and one owned output path or branch.
- Do not edit another worker's result, testbed branch, programme state, campaign status, batch manifest, synthesis, or closeout.
- For one-shot probes, write only the assigned result file or post a complete handoff marked `needs:materialization`.
- Claim coordinated work before substantial investigation.
- When evidence affects another assignment, report the dependency in both relevant Fieldwork records.
- Finish with the handoff protocol in `START_HERE.md` and `COORDINATION.md`.

## Write modes

1. **Fieldwork PR** — preferred when an agent can create a branch and durable files. One PR should contain one scout, lane, or coherent group of tiny probes.
2. **Issue handoff** — use when repository writes are unavailable. Include the complete result and apply `needs:materialization`.
3. **Coordinator materialization** — a coordinator may combine several issue-only handoffs into one repository change.
4. **Playground experiment** — use for bounded local tests that require no shared coordination or upstream modification.
5. **Integration trial** — use an owned repository for realistic lifecycle, integration, or ergonomics evidence.
6. **Context dossier** — use when isolated evidence needs sourced integration, operational, or ecosystem interpretation.
7. **Execution carrier** — temporary evidence-producing branch or pull request in an owned repository; it must identify and return evidence to a canonical source branch, then close.

Never have multiple workers push shared files directly to `main`.

## AI-assisted implementation

- Generated code is a candidate until tested and reviewed.
- A human remains responsible for every upstream claim and submitted line, and must perform any upstream submission manually outside Fieldwork automation.
- Follow each target project's current contribution and AI-disclosure policy when preparing material for human submission.
- Keep changes bounded to the assigned question.
- Do not rewrite unrelated files for style or convenience.

## External interactions

Third-party upstream repositories are read-only to agents and automated workers. No Fieldwork record, programme, target hub, target map, batch, campaign, lane, playground, testbed trial, context dossier, repository note, user instruction, authorization field, marker, or target-project policy can authorize an automated upstream mutation.

Agents may prepare human-facing upstream packets, issue drafts, pull-request drafts, patches, reproductions, review notes, and manual submission steps in Fieldwork or owned repositories. If a human later performs an upstream interaction manually, agents may record that already-existing interaction in Fieldwork.

## Safety

Do not retain secrets, access tokens, private repository content, personal data, or production payloads. Use synthetic fixtures or redacted evidence whenever possible.
