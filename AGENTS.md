# Fieldwork agent hot path

These rules bind every automated worker. Do not preload the whole repository manual.

## Always

- Third-party upstream repositories are read-only by default. Before any state-changing upstream
  interaction, show the exact destination, action, and final content, then obtain a fresh bounded
  human `upstream greenlight`. It authorizes only that exact interaction and is consumed once.
- Before an authorized GitHub write, refresh the destination and run the exact final text through
  [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md). Verify that no private transcript content, local
  path or identifier, secret, or unsupported claim will be published. After the write, record the
  URL, exact text or digest, time, and consumed-greenlight scope in the owning Fieldwork record.
  Automated workers must use literal
  `redirect.github.com` URLs for third-party GitHub issue, pull-request, and discussion references,
  including drafts, tracked files, commit messages, and owned-fork interaction text. Owned
  `teamleaderleo/*` references and repository/source/documentation/release/commit links are exempt.
- Work only from an explicit assignment, claimed unit, requested synthesis or triage, bounded
  review, or bounded fork-free experiment. Issues own live coordination; repository files own
  durable evidence. Never retain secrets, tokens, private repository content, personal data, or
  production payloads.

## Route by task

- Start with the current assignment or claimed unit. Open [`START_HERE.md`](START_HERE.md) only when
  ownership, placement, or the next contract is unclear; never load its whole reading list by
  default.
- A bounded one-worker synthetic probe needs no fork or Fieldwork issue. Use
  `playgrounds/EXP-YYYYMMDD-short-name/` with `templates/experiment.json`; record one question,
  exact command and environment, source revisions, claim scope, stop condition, and
  `upstream_contact_authorized: false`. Default to synthetic inputs and no network. Open
  [`EXPERIMENTS.md`](EXPERIMENTS.md) only when retaining or promoting the result.
- For deeper research method, evidence classes, write modes, integration trials, or review
  procedure, search headings in [`AGENT_PLAYBOOK.md`](AGENT_PLAYBOOK.md) and open only the matching
  section plus the specific owner it names.
- Use [`REFERENCE_POLICY.md`](REFERENCE_POLICY.md) for external references or contact,
  [`COORDINATION.md`](COORDINATION.md) for claims and handoffs,
  [`REVIEWING.md`](REVIEWING.md) for promotion or merge decisions, and
  [`INTEGRATION_CONTEXT.md`](INTEGRATION_CONTEXT.md) before making broader use or impact claims.

## Finish

Preserve exact revisions and evidence scope, distinguish prepared from executed checks, review the
complete current diff, and finish through the handoff protocol owned by `START_HERE.md` and
`COORDINATION.md`.
