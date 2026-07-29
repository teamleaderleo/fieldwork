# Contributing to Fieldwork

Fieldwork welcomes corrections, reproductions, experiments, target knowledge, campaign review, and process improvements that increase the quality and truthfulness of the research.

## Before proposing a change

- Read `START_HERE.md`, `REVIEWING.md`, the charter, and the method.
- Keep external references quiet under `REFERENCE_POLICY.md`.
- Search the live issues, active pull requests, owned forks, and durable records before creating another lane or branch.
- Separate observed evidence from interpretation.
- Identify exact source revisions where claims depend on code.
- Classify the work as owned product delivery, upstream-fork research, execution carrier, evidence/documentation, or blocked/security-sensitive work.
- Avoid opening a campaign solely to create an upstream contribution.

## Useful contributions

- a smaller or more deterministic reproduction;
- a competing hypothesis with a distinguishing test;
- a corrected source map or stale coordination record;
- an adversarial case, portability result, or negative control;
- a documented negative result;
- a policy or governance correction with a current source;
- a clearer upstream packet that lowers reviewer effort;
- a review that finds a missing safety, authority, lifecycle, or evidence boundary;
- automation that detects stale heads, contradictory states, or evidence upgrades without silently changing canonical records.

## Pull requests

A Fieldwork pull request should state:

- the question, programme, campaign, or issue advanced;
- the work class and canonical delivery surface;
- the exact branch, head, base, and changed-file fence;
- the evidence added or changed and its accurate evidence class;
- validation commands, workflow runs, platforms, skipped checks, and failures;
- claims that remain uncertain;
- dependencies, superseded branches, and execution carriers;
- whether the author is eligible to accept or merge the work;
- external interactions created, if any;
- upstream-contact authorization;
- AI assistance used and how the output was verified.

Keep the pull-request description current. Remove stale claims about running checks, pending dependencies, current-main relation, or canonical branches after the head changes.

Passing CI confirms only the checks that actually ran at the tested revision. It does not validate research claims, uninvoked tests, security properties, authority boundaries, ecosystem impact, or final acceptance.

## Review and promotion

Use the dispositions and exact-head receipt in `REVIEWING.md`. Builders may document self-review, but consequential implementation, security, authority, and upstream packets should receive independent complete-diff review before promotion.

Temporary execution pull requests must identify the canonical source head and should close after their evidence is transferred. A focused result must not be described as a full repository gate, and a model or prepared target test must not be described as target execution.