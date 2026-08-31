# Fieldwork agent hot path

These rules bind every automated worker. Load the current assignment and only the owner documents needed for the next decision.

## Always

- Work from an explicit assignment, claimed unit, requested synthesis or triage, bounded review, or bounded fork-free experiment. Fieldwork and owned `teamleaderleo/*` repositories or forks are legitimate work surfaces within that scope. GitHub issues own live coordination; repository files own durable evidence.
- Third-party upstream repositories are read-only unless a human gives a fresh bounded `upstream greenlight` for one exact destination, action, and final content. The greenlight is consumed by that interaction. Follow [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md) for every external-reference rule, exact-text preflight, authorized-write procedure, and interaction record.
- Keep secrets, tokens, private repository content, personal data, production payloads, and private transcript material out of retained or published work.

## Route by task

- Start with the current assignment or claimed unit. Open [`START_HERE.md`](START_HERE.md) only when placement, ownership, or the next contract is unclear.
- A bounded one-worker synthetic probe may use `playgrounds/EXP-YYYYMMDD-short-name/` with `templates/experiment.json`; default to synthetic inputs, no network, one question, exact command/environment/revisions, a stop condition, and `upstream_contact_authorized: false`. Open [`EXPERIMENTS.md`](EXPERIMENTS.md) when retaining or promoting it.
- Use [`CODE_FIRST.md`](CODE_FIRST.md) for investigation framing and search the matching heading in [`AGENT_PLAYBOOK.md`](AGENT_PLAYBOOK.md) for deeper method.
- Use [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md) for external references or authorized upstream interaction, [`COORDINATION.md`](COORDINATION.md) for claims and handoffs, [`REVIEWING.md`](REVIEWING.md) for review or promotion, and [`INTEGRATION_CONTEXT.md`](INTEGRATION_CONTEXT.md) before broader use or impact claims.

## Finish

Preserve exact revisions and evidence scope, distinguish prepared from executed checks, inspect the complete current diff, and finish through the handoff protocol owned by [`COORDINATION.md`](COORDINATION.md) and [`START_HERE.md`](START_HERE.md). Record any authorized upstream interaction through [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md).
