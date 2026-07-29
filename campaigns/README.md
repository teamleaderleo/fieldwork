# Campaigns

A campaign is a bounded investigation with one primary question and an explicit closeout.

## Naming

Use a stable numeric identifier and short descriptive slug:

```text
campaigns/0002-stream-reconnect-state/
```

## Minimum contents

- `question.md` — question, motivation, scope, and stop conditions;
- `investigation.md` — source map, reproduction, hypotheses, and findings;
- `decision.md` — chosen outcome and rationale;
- `upstream.md` — only when upstream contact is being prepared or has occurred;
- `reproduction/` or `experiments/` — when retained artifacts are useful.

## Rules

- One campaign, one primary question.
- External references stay quiet until submission is deliberate.
- Exact source revisions are required for source-dependent claims.
- A campaign can close without an upstream artifact.
- Every conclusion states remaining uncertainty.
- Record dead ends that could save future work.
