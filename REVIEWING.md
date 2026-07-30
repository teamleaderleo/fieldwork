# Reviewing and Promotion

## In simple words

A passing test or a convincing pull-request description is not the same thing as an accepted result. Review must identify what kind of work is being examined, which exact revision was tested, what evidence actually ran, what remains uncertain, who is eligible to accept it, and which branch is the real delivery surface. Temporary execution machinery, stale descriptions, and green checks must not be mistaken for a merge decision.

## Classify the work before reviewing it

Every review item should identify one primary class:

1. **Owned product delivery** — a candidate change intended to merge into an owned repository. It needs current-main relation, exact-head product validation, authority and safety review, and an independent final disposition.
2. **Upstream-fork research** — a reproduction, source map, compatibility investigation, issue draft, or candidate patch in an owned fork. It remains research until precedent, duplicate search, target-native evidence, compatibility, and contribution policy are understood.
3. **Execution carrier** — a temporary branch, pull request, or workflow used only to run code or produce a receipt. It is never the canonical merge candidate and should be closed or removed after its evidence is transferred.
4. **Evidence or documentation** — a benchmark, provider finding, policy packet, synthesis, or decision record. It must distinguish documented facts, executed observations, interpretation, and unresolved questions.
5. **Blocked or security-sensitive work** — a candidate whose required safety, authority, identity, or recovery primitive is absent. Green CI does not clear the block.

When one pull request contains more than one class, split it or name one canonical delivery surface and treat the others as supporting evidence.

## Preserve evidence class per claim

Use the narrowest accurate evidence description for each claim that affects the disposition. Recommended classes are:

- `source-read` — implementation, tests, history, or contracts were inspected;
- `model-executed` — an isolated model or dependency-free probe ran;
- `target-test-prepared` — a target-native test exists but has no retained execution receipt;
- `target-executed` — the target package or repository test ran at an exact head;
- `integration-executed` — a real owned integration, browser, process, provider, or platform path ran;
- `full-gate` — the named repository-declared gate ran at the exact candidate head. The receipt must name that gate or command set and state important integration, platform, provider, authority, recovery, or ecosystem paths it does not exercise. `full-gate` does not imply coverage outside the named gate.

Do not assign one strongest evidence class to an entire pull request when its claims have different support. A single review can legitimately record, for example:

| Claim | Evidence class | Limit |
| --- | --- | --- |
| current implementation marks cleanup complete before the final await | `source-read` | source ordering only |
| isolated failure model preserves the original error | `model-executed` | no package runtime |
| target regression exists | `target-test-prepared` | not executed |
| named package test passed | `target-executed` | one runtime and one package path |

Do not upgrade evidence during synthesis. In particular:

- a model is not package execution;
- a prepared test is not a failing test;
- one platform run is not a cross-platform result;
- a focused test is not a full gate;
- a named full gate is not proof of behavior outside the paths that gate exercises;
- full CI is not proof of an untested security, authority, or lifecycle property;
- one owned testbed is not ecosystem impact.

Fields that do not apply should say `not applicable`. Do not invent a run, gate, issue generation, authority decision, or current-main relation merely to fill a template.

## Self-review before handoff

Self-review prepares work for independent judgment; it does not replace independent acceptance.

Before asking another reviewer to inspect a result:

1. Re-read the strongest claim and identify the exact artifact, source path, or execution receipt supporting it.
2. Confirm the intended assertion ran. A setup, installation, timeout, fixture, or unrelated precondition failure is a harness result, not product evidence.
3. Inspect the exact failure rather than relying on a red job summary.
4. Rewrite the candidate when execution disproves the original theory or reveals a different mechanism.
5. Preserve negative controls and rejected designs that distinguish the retained direction from easier but unsafe alternatives.
6. Split findings that have different owners, result models, compatibility risks, or implementation boundaries.
7. State missing platform coverage, unmeasured frequency, inferred consequence, and every material uncertainty.
8. Synchronize the live issue, durable report, pull-request front page, execution receipt, and queue or Delivery Desk entry.
9. Run Fieldwork integrity and external-reference checks on the final Fieldwork head.
10. Confirm that upstream contact remains unauthorized unless the user approved that exact interaction.
11. Complete `templates/review.md` as a self-review receipt or explicitly record why a field is not applicable.

## Execution workflow

When prepared work needs retained target evidence:

1. Keep the product test or candidate source on one canonical owned-fork branch.
2. Use a separate execution-only branch or pull request for temporary CI configuration when practical.
3. Follow the target repository's own installation, build, test, lint, and platform sequence.
4. Run the smallest discriminating test first, then add compatibility or platform coverage only after the premise survives.
5. Record the exact source head, workflow run, job, environment, command, assertion, and result.
6. Classify setup failures and incorrect premises as harness findings rather than target defects.
7. When the result changes the theory, update the test, issue, report, pull-request description, and queue card before promotion.
8. Transfer the retained receipt to the canonical source record and remove or close temporary execution machinery.

An execution carrier is never a merge or upstream candidate merely because it produced a useful result.

A workflow that intends to delete itself remains an active execution carrier until a later exact head proves that the workflow is absent and exposes the resulting source, tests, report, and retained receipt for review. Future self-removal is not evidence transfer.

## Exact-head review receipt

A promotion review should record:

- repository and pull request;
- canonical branch and exact head SHA;
- exact base or current-main revision used for comparison;
- changed-file fence or complete-diff scope;
- work class;
- each disposition-relevant claim and its evidence class;
- validation commands, workflow runs, platforms, and retained results;
- unresolved failures, skipped jobs, and checks that did not run;
- dependencies, replacements, and superseded branches;
- reviewed coordination inputs when they affect the decision, including the issue number and a body digest or explicit body revision marker;
- live labels, state, assignees, or other metadata generations separately when they affect the disposition;
- whether upstream contact remains unauthorized;
- reviewer disposition and clearing condition.

A code head is not the only possible review input. When the invariant, review ask, state, clearing condition, authority boundary, or promotion request comes from an issue or decision record, the receipt must version that input too. GitHub `updated_at` may be recorded as an explicitly accepted coarse snapshot marker, but it is not a body-specific generation and can expire a receipt after unrelated activity.

Any code-head movement or reviewed-input generation change expires the disposition unless the reviewer explicitly proves the new input is semantically identical within the reviewed fence.

## Review dispositions

Use one of these dispositions:

- **ACCEPT** — the exact reviewed scope is suitable for its stated next transition.
- **REPAIR** — a concrete defect must be corrected before promotion.
- **HOLD** — required evidence, dependency, authority, or design primitive is missing.
- **EXECUTE** — the implementation or test is prepared, but target-native execution is still required.
- **REJECT** — the premise or proposed direction is unsound and should not continue in its current form.

A disposition must name the exact next transition. Accepting a research reproduction does not automatically accept its candidate fix, upstream wording, or submission.

## Independent acceptance

The builder may perform and document self-review, but should not be the sole final accepter of a consequential implementation, authority change, security boundary, or upstream packet. The final handoff must state whether the author is eligible to accept or merge the work.

Independent review should examine the complete current diff, not only the latest commit or the pull-request summary.

## Bounded continuation and review throughput

An explicit user assignment or instruction to continue authorizes bounded work in the same lane. Continue through source reading, local probes, review repairs, and ordinary repository writes without repeatedly asking for permission.

Seek new authorization when the work would widen scope, change authority, use private or production data, create a new external interaction, incur material cost, or cross another explicit boundary.

When review debt grows faster than dispositions, pause creation of new review surfaces and finish, consolidate, supersede, or close existing work. Reopen promotion only when new execution, consequence, novelty, or a narrow correction materially improves the decision.

## Canonical branch and execution-carrier rules

Every execution carrier must identify:

- the canonical source branch and head it tested;
- the exact workflow or command run;
- the resulting receipt or artifact;
- the canonical pull request that consumes the evidence.

After evidence transfer:

- remove temporary workflows from the canonical source branch;
- close disposable carrier pull requests;
- update the canonical pull-request description with the retained result;
- do not leave execution-only branches in the active merge queue;
- do not cite a synthetic merge commit as the source revision without also naming the contained source head.

A carrier is retired only when a later exact head proves the temporary workflow or branch is gone and the canonical source diff plus retained receipt are independently reviewable.

## Staleness and description hygiene

Before marking work ready, re-read the live issue, pull request, checks, comments, dependencies, and current main branch.

Repair or remove wording that says:

- a dependency is pending when it has merged or been replaced;
- checks are still running after they completed;
- a branch is current when it is behind or superseded;
- a review is valid after the reviewed head changed;
- a review is valid after its issue invariant, review ask, state, clearing condition, or authority input changed;
- an execution carrier is the canonical implementation;
- a full gate passed when only focused or model evidence ran;
- a named full gate proves integrations or properties it did not exercise;
- a workflow has transferred evidence merely because it contains future self-removal instructions.

Issue-body `State:` text and live `state:*` labels must agree. A generated queue or review index must carry a validation timestamp and exact referenced states; otherwise it is a snapshot, not a current queue.

## Diff quality

Reviewability is part of correctness work.

Reject or repair:

- broad formatting changes hiding a narrow behavioral change;
- generated files without a reproducible generator or source identity;
- one test stack that requires multiple unrelated production fixes;
- reporting or cleanup code that can replace the primary error it promises to preserve;
- unbounded retained evidence, logs, receipts, or state;
- compatibility claims without a negative control;
- changes that widen authority merely to make a test pass.

Prefer the smallest implementation that makes the invariant explicit and testable without broadening unrelated semantics.

## Promotion checklist

Before moving a pull request out of draft or advancing a Fieldwork issue:

- [ ] work class is explicit;
- [ ] canonical branch and exact head are named;
- [ ] reviewed issue or decision inputs are versioned when they affect the disposition;
- [ ] self-review confirmed the intended assertion ran and classified harness failures separately;
- [ ] each disposition-relevant claim has an accurate evidence class;
- [ ] every `full-gate` claim names the gate and its material coverage limits;
- [ ] non-applicable receipt fields are marked instead of invented;
- [ ] current-main relation is known or explicitly not applicable;
- [ ] complete current diff was reviewed;
- [ ] checks and failures are described truthfully;
- [ ] author eligibility is explicit;
- [ ] dependencies and supersession are current;
- [ ] execution carriers are closed or clearly non-canonical;
- [ ] retired carriers are absent from the reviewed exact head;
- [ ] issue state text and labels agree;
- [ ] uncertainty and clearing conditions are visible;
- [ ] upstream-contact authorization is explicit;
- [ ] no direct third-party reference violates `REFERENCE_POLICY.md`.

## Relationship to coordination automation

The rules in this file are the manual contract for generated coordination work. A future evaluator may detect stale heads, changed dependencies, mismatched evidence classes, conflicting ownership, incomplete receipts, and invalid promotion states. Automation may derive and validate a queue, but it must not silently upgrade evidence, issue acceptance, merge work, or authorize upstream contact.
