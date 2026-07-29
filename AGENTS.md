# Agent Instructions

These instructions apply to every AI system and automated worker operating in this repository.

## Entry protocol

- Start with `START_HERE.md`.
- Read `CHARTER.md`, `METHOD.md`, `REFERENCE_POLICY.md`, `COORDINATION.md`, `BATCHES.md`, and `EXPERIMENTS.md` before modifying research material.
- Search open Fieldwork issues, active batches, existing experiments, and campaign folders before creating work.
- Treat GitHub issues as live coordination and repository files as durable evidence.
- Work only from an explicit assignment, claimed lane, requested synthesis, user-directed triage task, or bounded fork-free experiment.

## External-reference rule

Before creating or editing any Fieldwork issue, pull request, comment, review, Markdown file, JSON record, or research report:

- never write a direct external GitHub issue, pull-request, discussion, or commit URL;
- use the equivalent `redirect.github.com` URL;
- never use external owner/repository number shorthand;
- use the intentional-upstream marker only when the user explicitly authorized that exact external interaction;
- remember that creating a Fieldwork record never authorizes upstream contact.

The interaction workflow is a last-resort detector. It cannot reliably stop GitHub from processing a direct reference at the instant an issue or comment is created. Prevention by the worker is mandatory.

## Fork-free experiments

- Small one-worker experiments may be created under `playgrounds/` without an upstream fork or Fieldwork issue.
- Use a stable `EXP-YYYYMMDD-short-name` directory and `templates/experiment.json`.
- State one bounded question, exact command, environment, source revisions, stop condition, and upstream-contact authorization.
- Reuse `playgrounds/cases/` where those inputs can distinguish the hypotheses.
- Default to synthetic inputs and no network access.
- One experiment has one owner; parallel variants use separate directories.
- Retain a human-readable result when another worker, report, or decision may rely on it.
- Promote the experiment to a finding, batch probe, campaign lane, or regression fixture when it stops being disposable.
- A playground never authorizes upstream contact.

## Default behaviour

- Treat external observation as quiet research.
- Never open, comment on, react to, or modify upstream work without an explicit user instruction for that interaction.
- Never manufacture contribution volume, low-value cleanup, or speculative patches.
- Do not claim a reproduction, test result, benchmark, policy, or maintainer position without evidence.
- Preserve exact source revisions, retrieval dates, environments, and commands.
- Record uncertainty, contradictions, and negative results.
- Do not rely on chat history as the only record of work.
- A target map is not required before quietly examining an assigned public repository.

## Batch and parallel work

- Read the batch manifest or parent issue before beginning.
- Use the exact assignment ID, deliverable, owned path, dependencies, source revision, and stop condition.
- One lane or probe has one owner and one owned output path.
- Do not edit another worker's result, campaign status, batch manifest, synthesis, or closeout.
- For one-shot probes, write only the assigned result file or post a complete handoff marked `needs:materialization`.
- For coordinated lanes, claim the lane before substantial work.
- When evidence affects another assignment, report the dependency in both relevant Fieldwork records.
- Finish with the handoff protocol in `START_HERE.md` and `COORDINATION.md`.

## Write modes

1. **Fieldwork PR** — preferred when an agent can create a branch and durable files. One PR should contain one lane or a coherent group of tiny probes.
2. **Issue handoff** — use when repository writes are unavailable. Include the complete result and apply `needs:materialization`.
3. **Coordinator materialization** — a coordinator may combine several issue-only handoffs into one repository change.
4. **Playground experiment** — use for bounded local tests that require no shared coordination or upstream modification.

Never have multiple workers push shared files directly to `main`.

## AI-assisted implementation

- Generated code is a candidate until tested and reviewed.
- A human remains responsible for every upstream claim and submitted line.
- Follow each target project's current contribution and AI-disclosure policy.
- Keep changes bounded to the assigned question.
- Do not rewrite unrelated files for style or convenience.

## External interactions

A target map, batch, campaign, lane, playground, repository note, or Fieldwork issue does not authorize upstream contact. Direct upstream interaction requires a specific user instruction and must be recorded in the campaign closeout or upstream packet.

## Safety

Do not retain secrets, access tokens, private repository content, personal data, or production payloads. Use synthetic fixtures or redacted evidence whenever possible.
