# Reviewing and Promotion

## In simple words

Review exists to answer a decision that deterministic evidence cannot answer alone. It should identify the exact work being considered, the claims that affect the decision, the evidence that actually ran, the uncertainty that remains, and the next permitted transition.

Do not maintain parallel copies of live branch, check, review, queue, delivery, or submission state. Keep each mutable fact on its canonical surface and derive current views from GitHub or repository-owned machinery when needed.

Third-party upstream repositories are permanently read-only to Fieldwork agents. Review may prepare material for human submission, but it can never authorize an automated upstream mutation.

## Classify the work before reviewing it

Every review item should identify one primary class:

1. **Owned product delivery** — a candidate intended to merge into an owned repository.
2. **Upstream-fork research** — a reproduction, source map, compatibility investigation, issue draft, or candidate patch in an owned fork. It remains research; any upstream interaction is human-only.
3. **Execution carrier** — temporary machinery used only to produce evidence. It is never the canonical merge candidate.
4. **Evidence or documentation** — a benchmark, provider finding, policy packet, synthesis, or decision record.
5. **Blocked or security-sensitive work** — work missing a required safety, authority, identity, recovery, or validation primitive.

When one pull request mixes classes, split it or name one canonical delivery surface and treat the rest as supporting evidence.

## Preserve evidence class per claim

Use the narrowest accurate evidence description for each claim that affects the disposition:

- `source-read` — implementation, tests, history, or contracts were inspected;
- `model-executed` — an isolated model or dependency-free probe ran;
- `target-test-prepared` — a target-native test exists without a retained execution receipt;
- `target-executed` — the target package or repository test ran at an exact head;
- `integration-executed` — a real owned integration, browser, process, provider, or platform path ran;
- `full-gate` — the named repository-declared gate ran at the exact candidate head.

Do not upgrade evidence during synthesis. A prepared test is not an executed test. A focused run is not a full gate. One platform is not cross-platform evidence. Green CI is not proof of an untested security, authority, lifecycle, or ecosystem property.

Fields that do not affect the decision may be omitted. Do not invent or copy a run, timestamp, head, queue state, label, or authority field merely to satisfy a template.

## Self-review before handoff

Self-review prepares work for independent judgment when independent judgment is warranted.

Before handoff:

1. Re-read the strongest claim and identify its exact supporting source, artifact, or execution receipt.
2. Confirm the intended assertion ran. Setup, installation, timeout, fixture, or unrelated precondition failures are harness evidence.
3. Inspect the exact failure instead of relying on a red summary.
4. Rewrite the candidate when execution disproves the theory or identifies a different mechanism.
5. Preserve negative controls and rejected designs that distinguish the retained direction.
6. State material uncertainty and missing coverage.
7. Update the canonical owner of every fact that changed. Do not copy current status into a parallel desk, queue card, or journal. Invalidate dependent receipts and regenerate derived views when their inputs change.
8. Run Fieldwork integrity and external-reference checks on the final Fieldwork head.
9. Confirm automated third-party upstream contact remained prohibited.

Use `templates/review.md` only when its fields help another worker reconstruct the decision. `not applicable` is preferable to fabricated completeness.

## Execution workflow

When prepared work needs retained target evidence:

1. Keep the candidate source or product test on one canonical owned-fork branch.
2. Use separate temporary execution machinery only when the target requires it.
3. Follow the target repository's own install, build, test, lint, and platform sequence through non-upstream-mutating mechanisms.
4. Run the smallest discriminating test first. Add wider compatibility or platform coverage only after the premise survives.
5. Retain the exact source head, command/workflow, environment, assertion, and result needed to support the claim.
6. Classify setup failures and incorrect premises as harness findings.
7. When a result changes the theory, update the canonical source record and any decision-bearing issue or pull-request text. Derived queues should regenerate; do not hand-maintain matching status copies.
8. Transfer useful receipts to the canonical source record and retire temporary execution machinery.

A carrier is retired only when the canonical source diff and retained evidence remain reviewable without it.

## Exact reviewed inputs

A promotion review should record only the inputs needed to reconstruct and invalidate its decision:

- repository and canonical work item;
- exact candidate head and relevant base/current-main coordinate;
- complete-diff or explicit changed-file fence;
- work class;
- disposition-relevant claims and evidence classes;
- executed validation and its exact result identity;
- material failures, skipped required checks, uncertainty, dependencies, or authority boundaries;
- any issue/decision input whose exact wording changes the disposition;
- reviewer disposition and clearing condition.

Repository metadata that GitHub can reconstruct at decision time—routine labels, assignees, queue position, a copied CI status, a copied current-main SHA, or a refresh timestamp—does not belong in the receipt unless that exact value is itself a reviewed input.

A head or reviewed-input change expires the disposition when it can change the reviewed meaning. Byte-identical or semantically proven-equivalent inputs may retain the earlier review within its explicit fence.

## Review dispositions

Use one of:

- **ACCEPT** — the exact reviewed scope is suitable for its stated next transition.
- **REPAIR** — a concrete defect must be corrected.
- **HOLD** — required evidence, dependency, authority, or design primitive is missing.
- **EXECUTE** — implementation or test is prepared and target-native execution is still required.
- **REJECT** — the premise or direction should stop in its current form.

A disposition names one exact next transition. It never upgrades another evidence class or authorizes an automated third-party upstream write.

## Independent review by consequence

Independent review is valuable when a fresh discriminator can exist. Require or strongly prefer it for:

- consequential implementation or merge candidates;
- security, authority, destructive-operation, durability, or recovery boundaries;
- broad or novel semantic changes whose failure would escape ordinary deterministic checks;
- human-facing upstream packets before a human submission decision;
- disputes where author self-review and deterministic evidence leave material uncertainty.

Bounded reversible work may use careful self-review when repository policy permits it and deterministic gates already own the relevant defect class. A tiny mechanical repair should not receive a full independent review merely because a larger parent once required one.

Independent review should inspect the complete current diff and the evidence relevant to its consequence. A reviewer who adds no new discriminator should not trigger another review layer.

## Bounded continuation and escalation

An explicit user assignment or instruction to continue authorizes bounded work in the same lane through source reading, probes, review repairs, and ordinary writes in Fieldwork, owned repositories, and owned forks.

Escalate when the next decision crosses a real authority boundary, requires destructive or production-impacting action, changes a shared schema/identity contract outside the lane, exposes sensitive material, or leaves a merge/disposition conflict that lower-level evidence cannot settle.

Ordinary test failures, stale heads, mechanical restacks, evidence refresh, and review corrections are lane work.

Third-party upstream mutation always remains human-only.

## Review debt and duplicate surfaces

When review debt grows faster than dispositions, stop creating review surfaces. Finish, consolidate, supersede, or close existing work first.

A review desk, status journal, filing packet, target hub, or queue should carry only information that cannot be reconstructed cheaply from its canonical owners. Generated views should be regenerated from those owners. Hand-maintained copies should expire when the underlying facts become queryable.

Reopen a closed process question only after a concrete failure shows the smaller path loses a decision-relevant fact.

## Staleness and description hygiene

Before marking work ready, read the live candidate, checks, decision-bearing dependencies, and current target state.

Repair wording that says a dependency is pending after it landed, a branch is current after replacement, a review still applies after a meaningful input changed, an execution carrier is canonical, or a named gate proves something it did not exercise.

A generated queue or review view is a projection. Its authority comes from the exact source state it re-reads, not from a manually copied validation timestamp.

## Diff quality

Reviewability is part of correctness work. Repair or reject:

- broad formatting changes hiding a narrow behavior change;
- generated files without reproducible source identity;
- one test stack that requires unrelated product repairs;
- reporting or cleanup code that can replace the primary outcome it promises to preserve;
- unbounded retained logs, receipts, evidence, or state;
- compatibility claims without a negative control;
- authority expansion introduced merely to make a test pass.

Prefer the smallest implementation that makes the invariant explicit and testable.

## Promotion check

Before advancing work, the answer should be recoverable for these questions:

- What exact work and head are being considered?
- What transition is requested?
- Which claims decide that transition?
- What evidence actually supports each claim?
- What required gate or uncertainty remains?
- Did a meaningful reviewed input change?
- Does the author have authority for the next owned-repository action?
- Did automated third-party upstream contact remain prohibited?

If those answers are available from the canonical work item and exact receipts, another checklist copy adds no value.

## Relationship to coordination automation

Automation should derive stale-head state, checks, changed dependencies, review applicability, queue membership, and other mechanical facts wherever possible. It may validate or regenerate views, but it must not silently upgrade evidence, issue acceptance, merge work, authorize upstream contact, or mutate a third-party upstream repository.

The intended lifecycle is:

```text
new failure
-> temporary procedure
-> repeated evidence
-> deterministic check or better default
-> delete the procedure where the check now owns the failure
```
