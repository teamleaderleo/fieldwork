# Integration Trial: <short name>

## In simple words

- **Target:**
- **Testbed:**
- **Question:**
- **Why this realistic use adds evidence:**
- **Current answer or next step:**

## Identity

- Trial ID:
- Owner:
- Date:
- Related target hub:
- Related experiment, finding, campaign, or lane:
- Target label: `target:<slug>`
- Testbed label: `testbed:<slug>`

## Revisions

- Target repository, package, or system:
- Exact target version or commit:
- Testbed repository or neutral identifier:
- Exact testbed revision:
- Trial branch:
- Environment:
- Installation or build command:

## Change thesis

### Current behaviour

### Consequence

### Candidate improvement

### Evidence needed

### Evidence boundary

## Realistic scenario

Describe the user or system workflow. Explain why this testbed naturally exercises the target path.

## Baseline

- exact setup:
- command or interaction:
- observed behaviour:
- retained evidence:

## Candidate

- exact setup or change:
- command or interaction:
- observed behaviour:
- retained evidence:

## Correctness observations

## Ergonomics observations

Record confusing defaults, extra ceremony, misleading types, error clarity, recoverability, and whether the API encourages correct use.

## Performance and resource observations

Record only when measured or directly observed.

## Failure and recovery paths

- cancellation:
- timeout:
- retry:
- partial success:
- cleanup:
- rollback:

## Regressions and negative results

## What this trial preserves

## What this trial omits

## Wider context

- integration-context dossier:
- documented usage:
- inferred usage:
- illustrative usage:

## Cleanup

- destructive operations performed:
- rollback command or commit:
- retained branch or artifact:
- secrets or private data retained: `no`

## Disposition

Choose one:

- discard;
- repeat;
- retain as a regression or example;
- keep as an owned-project feature;
- promote to a finding;
- open or extend a campaign;
- prepare a human-facing upstream packet for manual submission;
- negative result.

## Upstream boundary

Automated third-party upstream contact: `prohibited`

Human-performed upstream interaction recorded: `none`

An agent must never perform the upstream write, even when explicitly asked. If a human later submits or comments manually, record that already-existing interaction here.
