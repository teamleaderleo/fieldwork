# Testbeds

This directory records owned repositories that can support realistic Fieldwork integration trials.

`registry.yml` is an orientation index, not an exhaustive inventory and not permission to modify every listed repository without an assignment. Any accessible owned repository may be considered when it naturally fits the question.

## States

- `candidate` — plausible place for a future controlled trial.
- `active` — currently used by at least one Fieldwork trial.
- `retained` — contains a lasting example, regression, or integration produced by Fieldwork.
- `dormant` — no longer suitable without reassessment.

## Publicness

Only public repositories should be named in this public registry by default. Private repositories use neutral identifiers in public Fieldwork records unless the user explicitly approves disclosure.

## Labels

Create `testbed:<slug>` lazily when the first real trial begins. The corresponding Fieldwork work item should also carry the `target:*` label for the system being studied.

See `TESTBEDS.md` and `templates/integration-trial.md`.