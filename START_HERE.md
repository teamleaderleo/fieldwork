# Start Here

Use this runbook whenever a person or agent is told to investigate something through Fieldwork.

## In simple words

Find the programme and target hub, claim one bounded scout or lane, read the code, explain the system simply, reproduce or model the important behaviour, and use an owned application as a controlled testbed when realistic use adds evidence. Report what was established, what remains unknown, and which branches are actually worth opening.

## 1. Read the rules

Read, in order:

1. `AGENTS.md`
2. `CHARTER.md`
3. `CODE_FIRST.md`
4. `PLAIN_LANGUAGE.md`
5. `METHOD.md`
6. `REFERENCE_POLICY.md`
7. `PROGRAMMES.md`
8. `TARGET_HUBS.md`
9. `EXPERIMENTS.md` for a fork-free local test
10. `TESTBEDS.md` for realistic use in an owned repository
11. `INTEGRATION_CONTEXT.md` when making claims about wider use or consequence
12. `COORDINATION.md` for shared or parallel work
13. `BATCHES.md` when the assignment belongs to a batch
14. `REVIEWING.md` before asking for acceptance, execution, promotion, merge, or upstream preparation
15. the relevant programme hub, target hub, map, experiment, trial, context, manifest, campaign, lane, and issue

Tool-specific instruction files point back to `AGENTS.md`; they do not replace it.

## 2. Identify the programme, target, and assigned unit

Search `programmes/registry.yml`, `targets/hubs.yml`, open Fieldwork issues, active batches, existing playgrounds, testbeds, contexts, and campaign folders before creating a record.

Apply the correct `programme:<slug>` and `target:<slug>` labels. Link the stable programme and target hubs when they exist. If an owned repository will exercise the target, apply `testbed:<slug>` only when the trial actually begins.

Choose the smallest correct unit:

- **Programme hub** — stable cross-target direction and branching surface.
- **Target hub** — stable orientation and discovery issue for recurring work.
- **Scout lane** — bounded reconnaissance that maps a target or boundary and returns branch candidates.
- **Experiment** — bounded one-worker local test requiring no upstream fork or issue.
- **Integration trial** — realistic use in an owned repository.
- **Context dossier** — sourced explanation of how a mechanism participates in a larger workflow.
- **Batch** — controlled temporary dispatch across many assignments.
- **Finding** — retained observation with no approved campaign.
- **Lead** — possible investigation awaiting triage.
- **Campaign** — bounded parent question promoted from evidence.
- **Lane** — coordinated independently owned campaign unit.
- **Probe** — one-shot assignment recorded in a batch manifest.
- **Decision** — coordinator or human choice.
- **Synthesis** — combination and closeout work.

Do not create work merely because an external repository has an available issue.

## 3. Establish ownership and claim scope

Never silently begin work another assignment may already own.

For every durable record, begin with `## In simple words` and answer:

- What is this?
- Where does it sit?
- What is wrong, uncertain, or being tested?
- Why could anyone care?
- What is the current answer or next step?

For a scout or lane, record:

- worker identity;
- programme and target hubs;
- exact question;
- expected deliverable;
- owned output path;
- dependencies;
- target source revision or retrieval boundary;
- intended claim scope;
- stop condition;
- upstream-contact authorization, normally `false`.

A scout must return code and test maps, at least one runnable probe or explicit reason none is feasible, ranked branch candidates, and a recommendation to stop, retain a finding, open a campaign, or run another scout.

For an experiment, record in `experiment.json`:

- worker identity;
- one bounded question;
- claim scope: mechanism, interface, integration, operational, or ecosystem;
- exact command and environment;
- source revisions or retrieval boundary;
- distinguishing outcomes;
- integration-context path when required;
- stop condition;
- upstream-contact authorization, normally `false`.

For an integration trial, record:

- target and target hub;
- owned testbed or neutral identifier;
- exact target and testbed revisions;
- dedicated branch and owner;
- realistic scenario;
- baseline and candidate behaviour;
- rollback and cleanup;
- claim scope and limitations.

One worker may edit only the owned scout, experiment, trial branch, or assignment path. Coordinators own registries, manifests, status, synthesis, decision, and closeout files.

## 4. Protect external projects before writing

Before creating or editing any Fieldwork issue, PR, comment, review, report, experiment note, integration trial, context dossier, or data record:

- convert external GitHub issue, PR, discussion, and commit links to `redirect.github.com`;
- remove external shorthand cross-references;
- use the intentional marker only after explicit authorization for that interaction.

The CI detector runs after GitHub receives interaction text. It is a safety net, not permission to post a direct reference first.

## 5. Read the code and form a change thesis

Follow `CODE_FIRST.md`.

Before proposing implementation:

1. map entrypoints, control flow, data flow, state ownership, side effects, failure paths, cleanup, public contracts, and tests;
2. use recent issues and pull requests only as supplementary context;
3. state competing hypotheses;
4. identify what evidence would distinguish them;
5. state the change thesis: current behaviour, consequence, proposed improvement, evidence, and boundary.

Prioritize consequential correctness, security, recovery, performance, compatibility, integration, ergonomics, and meaningful refactors. Do not hunt documentation, lint, wording, or style work by default.

## 6. Reproduce, model, or try realistic use

For small local tests, prefer synthetic fixtures and `playgrounds/cases/`. Default to no network access.

Use an owned testbed when the question depends on application lifecycle, integration, deployment, or API ergonomics that a toy model cannot reveal. Choose a repository that naturally exercises the target. Keep the trial reversible and off production systems.

A testbed trial may become a useful owned-project feature. It does not by itself prove general ecosystem demand or an upstream contract.

## 7. Work quietly and preserve evidence

Fieldwork itself and explicitly selected owned testbeds may be updated as part of the assignment. External upstream interaction remains prohibited unless the user explicitly authorizes that exact interaction.

Preserve:

- exact repository and revision;
- retrieval date;
- commands and environment;
- baseline and candidate behaviour;
- evidence supporting each factual claim;
- source title, URL, version, section, and limitations;
- evidence label: Normative, Documented, Observed, Inferred, Illustrative, or Unknown;
- competing hypotheses and alternative architectures;
- ergonomics observations grounded in actual use;
- negative results and uncertainty;
- rollback, safety, and data-handling boundaries.

## 8. Connect the small test to the larger system

A mechanism-only experiment may stop after validating its bounded question.

When claiming wider usefulness, downstream dependence, user impact, operational risk, or ecosystem importance:

1. identify where the mechanism sits in the workflow;
2. identify actual callers, state owners, operators, and affected users where evidence exists;
3. map side effects, retries, ordering, persistence, recovery, and observability;
4. distinguish documented use from inferred or illustrative use;
5. state what the toy model or testbed preserves and omits;
6. create or link `templates/integration-context.md`.

For substantial context research, separate mechanism, usage, contract, operations, and adversarial lanes rather than asking one worker to blur them together.

## 9. Put evidence in the correct place

Preferred durable outputs:

- programme hub plus `programmes/<programme>/scouts/<scout>/report.md`
- target hub issue plus `targets/<target>/map.md`
- `playgrounds/EXP-YYYYMMDD-short-name/`
- `templates/integration-trial.md` retained with the relevant programme, campaign, batch, or context
- `contexts/patterns/<pattern>.md`
- `contexts/systems/<system>.md`
- `campaigns/<campaign>/lanes/<lane>/report.md`
- `batches/<batch>/results/<assignment>.md`
- retained artifacts beside the report

Use the templates under `templates/`. Avoid several agents editing one shared report, context dossier, experiment directory, or testbed branch.

## 10. Self-review before handoff

Follow `REVIEWING.md` and complete `templates/review.md` before asking another reviewer to accept, execute, promote, merge, or prepare work for upstream use.

At minimum:

1. trace every claim that affects the requested transition to an exact source path, artifact, test, workflow receipt, or retained result;
2. record evidence class per claim rather than assigning one strongest class to the whole pull request;
3. separate harness, setup, fixture, installation, and product failures;
4. inspect the complete current diff and current-main relation;
5. synchronize the issue, report, pull-request description, receipts, and queue or Delivery Desk entry;
6. mark non-applicable fields instead of inventing evidence;
7. prove temporary workflows or execution carriers are absent from the final canonical head before calling them retired.

Self-review prepares the handoff. It does not replace eligible independent acceptance.

## 11. Report completion visibly

A standalone experiment does not require an issue comment. Finish its `README.md` or report, update `experiment.json`, and promote it when other work depends on the result.

For coordinated work, post a completion comment on the relevant scout, lane, campaign, programme, or batch issue:

```text
FIELDWORK HANDOFF
State: ready-for-synthesis | blocked | negative-result | complete
Programme: <programme slug and hub>
Target: <target slug and hub>
Testbed: <slug, neutral id, or none>
Batch: <batch id or none>
Campaign: <campaign id or none>
Assignment: <scout, lane, or probe id>
Claim scope supported: mechanism | interface | integration | operational | ecosystem
Integration context: <path or none>
Durable artifacts: <paths or Fieldwork PR>
In simple words: <compact result>
Finding: <one-paragraph technical result>
Branch candidates: <ranked candidates or none>
Evidence labels used: <labels>
Uncertainty: <remaining uncertainty>
Dependencies discovered: <none or exact records>
Decision needed: <none or exact decision>
Upstream contact authorized: no | yes, with explicit authority
```

If repository writes are unavailable, place the full handoff in the issue and apply `needs:materialization`.

## 12. Close through acceptance and synthesis

A scout is finished when its revision, code and test map, runnable evidence or explicit feasibility limit, branch candidates, negative results, uncertainty, and recommendation are durable.

An experiment is finished when its question, claim scope, command, result, uncertainty, context requirements, and disposition are durable.

An integration trial is finished when its target and testbed revisions, scenario, baseline, candidate, result, limitations, rollback, and disposition are durable.

Coordinated work is finished only when:

- evidence is durable or explicitly queued for materialization;
- the issue carries a handoff;
- programme, target, and testbed labels are correct;
- blockers, uncertainty, dependencies, and evidence labels are visible;
- the coordinator can discover the result;
- broader claims have supporting context or remain explicitly provisional;
- the assignment is accepted, revised, promoted, or retained as a negative result.

The coordinator owns shared state transitions, branching, and synthesis.