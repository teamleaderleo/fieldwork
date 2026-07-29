# Evidence and Review Runbook

Use this runbook when reviewing a Fieldwork candidate, preparing work for the review queue, or checking your own result before handoff.

## In simple words

A result is ready for review when another person can see exactly what ran, what the result proves, what it does not prove, which failed ideas were rejected, and which decision is still needed.

Review is not another summary pass. It is an attempt to find the narrowest supported conclusion, expose missing proof, and prevent an attractive theory from being promoted beyond its evidence.

## Evidence classes

Use the strongest class actually retained by the work:

- **Executed target or public-path reproduction** — the relevant implementation or released package ran under retained conditions.
- **Source-confirmed** — pinned implementation directly supports the mechanism.
- **Probe-reproduced model** — a controlled model demonstrates part of the mechanism without executing the exact target path.
- **Prepared target test** — a focused test exists but has no retained execution result.
- **Candidate contract** — a desired invariant is proposed; current code is not assumed to promise it.
- **Reported alignment** — public reports agree with the mechanism but are not independent reproduction evidence.

Never silently upgrade source reading into execution evidence, a model into a target result, or a prepared test into a failing regression.

## Self-review before handoff

Before asking another reviewer to inspect the work:

1. Re-read the strongest claim and identify the exact artifact that supports it.
2. Confirm the final test reached the intended assertion rather than failing during setup, installation, or an unrelated precondition.
3. Separate harness discovery from product evidence. Retain useful failed attempts, but do not count them as reproductions.
4. Check whether the experiment disproved the original theory and revealed a different mechanism. Rewrite the candidate around the observed result.
5. Preserve negative controls and rejected designs that distinguish the retained direction from easier but unsafe alternatives.
6. Split findings that have different owners, result models, compatibility risks, or implementation boundaries.
7. State uncertainty, missing platform coverage, unmeasured frequency, and any claim that remains inferred.
8. Verify that issue state, durable report, pull-request front page, execution receipt, and review card agree.
9. Run Fieldwork integrity and external-reference checks at the final head.
10. Confirm that upstream contact remains unauthorized unless the user explicitly approved that exact interaction.

## Execution workflow

When a prepared test needs retained target evidence:

1. Keep the product test or candidate change on an owned fork branch.
2. Use a separate execution-only branch or pull request for CI configuration when practical.
3. Follow the target repository's own installation, build, and test sequence.
4. Run the smallest discriminating test first, then add controls or platform coverage only when the result survives.
5. Record the exact repository head, workflow run, job, environment, command, and assertion.
6. Classify setup failures and incorrect test premises as harness findings, not target defects.
7. When a test fails, inspect the exact failure before promoting the claim.
8. When the result changes the theory, revise the test, candidate title, report, and review card rather than preserving a disproven narrative.

Execution-only pull requests remain draft and are not merge or upstream candidates.

## Independent review protocol

Take one candidate at a time. Check its source, retained run, controls, claim wording, and remaining uncertainty. Return one disposition:

- **Accept** — evidence and wording support the conclusion.
- **Revise** — the work is useful, but the claim, scope, test, or presentation needs correction.
- **Execute** — the design is reviewable, but target-native evidence is still required.
- **Hold** — the item is valid but should not advance now.
- **Authorize contact** — evidence supports the specifically described upstream interaction.
- **Reject or stop** — the premise is disproven, superseded, duplicated, or not consequential enough.

Use this review receipt:

```text
Disposition:
Evidence checked:
Strongest supported conclusion:
Overstatement or missing proof:
Required next action:
Next owner:
Upstream contact authorized: yes/no/not requested
```

A reviewer should not approve their own pull request as an independent review. Self-review is still required, but it is recorded as preparation rather than independent acceptance.

## Review-queue protocol

GitHub issues are canonical live state. The review queue is a compact bulletin board, not a replacement for issues.

A queue card should contain:

- one decision-sized candidate;
- the live issue and durable record;
- evidence class and exact retained executions;
- a plain-language summary;
- the uncertainty that must survive review;
- one explicit review ask;
- one completion condition.

Put the strongest executed and decision-ready candidates at the front. Do not place a broad scout above its narrower review candidates. Split cards when one candidate would require different owners or dispositions.

Refresh or remove stale cards when later execution, synthesis, or a completed decision changes their state. Do not leave a finished decision phrased as open work.

## Durable synchronization

After a material result or review:

1. update the live issue;
2. update the durable report or result file;
3. update the pull-request front page;
4. add or refresh the review-queue card when a decision is ready;
5. cross-link dependent Fieldwork records;
6. preserve the exact run and negative-result history.

Do not rely on chat history as the only record of a corrected theory, rejected test, review disposition, or execution result.

## Promotion boundary

A candidate is ready to advance only when its owning boundary, evidence class, consequence, negative controls, uncertainty, and next decision are explicit.

A passing prototype is not automatically an upstream patch. A failing test is not automatically a product defect. A source mechanism is not automatically consequential. Promotion requires the narrowest supported claim and the next proof appropriate to that claim.
