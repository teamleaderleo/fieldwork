# Reviewing and Promotion

## In simple words

A passing test or a convincing pull-request description is not the same thing as an accepted result. Review must identify the work class, exact code and coordination inputs, what evidence actually ran, what remains uncertain, who may accept it, and which branch is the real delivery surface.

Issue state, finding state, workspace phase, and output status are different inputs. Temporary execution machinery, stale descriptions, whole-record evidence rankings, and green checks must not be mistaken for a transition decision.

## Classify the work before reviewing it

Every review item should identify one primary class:

1. **Owned product delivery** — a candidate intended to merge into an owned repository. It needs current-main relation, exact-head product validation, authority and safety review, and independent final disposition.
2. **Upstream-fork research** — a reproduction, source map, compatibility investigation, issue draft, or candidate patch in an owned fork. It remains research until precedent, duplicate search, target-native evidence, compatibility, and contribution policy are understood.
3. **Execution carrier** — a temporary branch, pull request, or workflow used only to run code or produce a receipt. It is never the canonical merge candidate and should close after evidence transfer.
4. **Evidence or documentation** — a benchmark, finding, workspace, policy packet, synthesis, or decision record. It must distinguish facts, executed observations, interpretation, and unresolved questions.
5. **Blocked or security-sensitive work** — a candidate whose required safety, authority, identity, or recovery primitive is absent. Green CI does not clear the block.

When one pull request contains more than one class, split it or name one canonical surface and treat the others as supporting evidence.

## Preserve evidence class per claim

Use the narrowest accurate evidence class for every claim that affects the disposition:

- `source-read` — implementation, tests, history, or contracts were inspected;
- `model-executed` — an isolated model or dependency-free probe ran;
- `target-test-prepared` — a target-native test exists but has no retained execution receipt;
- `target-executed` — the target package or repository test ran at an exact head;
- `integration-executed` — a real owned integration, browser, process, provider, or platform path ran;
- `full-gate` — the named repository-declared gate ran at the exact candidate head, with material coverage limits stated.

A record may list `Evidence classes present`. It must not assign one “strongest evidence class” to the whole pull request or finding, because a stronger row cannot upgrade weaker rows.

| Claim | Evidence class | Limit |
| --- | --- | --- |
| implementation marks cleanup complete before the final await | `source-read` | source ordering only |
| isolated failure model preserves the original error | `model-executed` | no package runtime |
| target regression exists | `target-test-prepared` | not executed |
| named package test passed | `target-executed` | one runtime and one package path |

Do not upgrade evidence during synthesis. A model is not package execution; a prepared test is not a failing test; one platform is not cross-platform evidence; a focused test is not a full gate; full CI is not proof of an untested authority property; one testbed is not ecosystem impact.

Fields that do not apply say `not applicable`. Do not invent a run, gate, issue generation, authority decision, or current-main relation.

## Version issue state and finding state separately

When coordination state affects a disposition, the review records independent inputs:

- **Issue-body generation** — body digest or explicit revision marker.
- **Live issue-state generation** — exact `state:*` label and accepted metadata snapshot marker.
- **Canonical finding generation** — path, branch, and exact head.
- **Finding state** — exact `FINDINGS.md` transition in the canonical finding.
- **Other decision inputs** — exact path, digest, or revision marker.

The issue-body `Issue state:` field must agree with the live label. The issue-body `Finding state:` field must agree with the canonical finding when one exists. There is no required one-to-one mapping between the two vocabularies.

GitHub `updated_at` may be recorded as an explicitly accepted coarse snapshot marker, but it is not a body-specific generation and may expire after unrelated activity.

## Self-review before handoff

Self-review prepares work for independent judgment; it does not replace independent acceptance.

Before asking another reviewer to inspect a result:

1. Trace every disposition-relevant claim to the exact artifact, source path, or receipt supporting it.
2. Confirm the intended assertion ran. A setup, installation, timeout, fixture, or unrelated precondition failure is a harness result, not product evidence.
3. Inspect the exact failure rather than relying on a red summary.
4. Rewrite the candidate when execution disproves the theory or reveals a different mechanism.
5. Preserve negative controls and rejected designs that distinguish the retained direction.
6. Split findings that have different owners, result models, compatibility risks, or implementation boundaries.
7. State missing platform coverage, unmeasured frequency, inferred consequence, and every material uncertainty.
8. Synchronize issue state, finding state, canonical finding, PR front page, execution receipt, and queue or Delivery Desk entry.
9. Run Fieldwork integrity and external-reference checks on the final Fieldwork head.
10. Confirm upstream contact remains unauthorized unless the user approved that exact interaction.
11. Complete `templates/review.md` or explicitly record why a field is not applicable.

## Execution workflow

When prepared work needs retained target evidence:

1. Keep the product test or candidate source on one canonical owned-fork branch.
2. Use a separate execution-only branch or pull request for temporary CI when practical.
3. Follow the target repository's own installation, build, test, lint, and platform sequence.
4. Run the smallest discriminating test first, then add compatibility or platform coverage only after the premise survives.
5. Record exact source head, workflow run, job, environment, command, assertion, and result.
6. Classify setup failures and incorrect premises as harness findings rather than target defects.
7. When the result changes the theory, update the canonical finding, issue, test, PR description, and queue card before promotion.
8. Transfer the receipt to the canonical source record and remove or close temporary execution machinery.

An execution carrier is never a merge or upstream candidate merely because it produced useful evidence.

A workflow that intends to delete itself remains active until a later exact head proves the workflow absent and exposes the canonical source, tests, finding, and receipt for review. Future self-removal is not evidence transfer.

## Exact-head review receipt

A review should record:

- repository and pull request;
- canonical branch and exact head SHA;
- exact base or current-main revision;
- changed-file fence or complete-diff scope;
- work class;
- each disposition-relevant claim and evidence class;
- commands, workflow runs, platforms, artifacts, and retained results;
- unresolved failures, skipped jobs, and checks that did not run;
- dependencies, replacements, and superseded branches;
- reviewed issue-body generation;
- reviewed live issue-state generation;
- reviewed canonical finding generation and finding state;
- reviewed authority or other decision inputs;
- upstream-contact authorization;
- reviewer disposition and clearing condition.

Any code-head, reviewed-input, issue-state, or finding-state movement expires the disposition unless semantic identity is proved within the reviewed fence.

## Review dispositions

Use one of these:

- **ACCEPT** — the exact reviewed scope is suitable for its stated next transition.
- **REPAIR** — a concrete defect must be corrected before promotion.
- **HOLD** — required evidence, dependency, authority, or design primitive is missing.
- **EXECUTE** — the implementation or test is prepared, but target-native execution is still required.
- **REJECT** — the premise or direction is unsound and should not continue in its current form.

A disposition names the exact next transition. Accepting a research reproduction does not accept its candidate fix, upstream wording, or submission.

## Independent acceptance

The builder may document self-review, but should not be the sole final accepter of a consequential implementation, authority change, security boundary, or upstream packet. Independent review examines the complete current diff, not only the latest commit or PR summary.

## Review-ready is peer-facing

`review-ready` means one exact current case is prepared for an eligible independent technical reviewer. It does not mean the user must review it, every worker must review it, the work is accepted, land-ready, merged, or ready for public upstream submission.

Routine review-ready work enters Review Queue #213 or the owning issue's designated peer-review surface until an accepted generated router replaces that route. A second agent using the same GitHub author account does not by itself make a review independent; the receipt records reviewer eligibility and the exact reviewed generation. Review-ready work appears in the human-facing decision surface only when it materially changes priority, exposes risk, becomes stale, or requires non-delegable authority.

A worker who marks one item review-ready continues useful autonomous work rather than treating that label as a terminal personal state. Suitable continuation includes:

- independently reviewing another exact head;
- producing a bounded non-conflicting repair for a concrete defect;
- checking composition and current-main drift;
- synchronizing findings, receipts, and live descriptions;
- retiring obsolete carriers after evidence transfer;
- preparing a blocked lane's smallest safe next probe;
- opening a fresh investigation when local debt is controlled or the new work has clearly higher marginal value.

## Bounded continuation and review throughput

An explicit user assignment or instruction to continue authorizes bounded work in the same lane. Continue through source reading, local probes, review repairs, ordinary repository writes, cleanup, synchronization, and adjacent peer review without repeatedly asking for permission.

When a review finds a concrete defect, prefer repairing it in the same pass when the repair is bounded, validation is available, and the worker owns the current recorded lease, an explicit release, transfer, or takeover is recorded, or the repair uses a separate non-conflicting stacked branch. Observed expiry, silence, or inactivity alone never grants write authority. Do not silently rewrite another active worker's artifact. When direct repair would conflict, retain an exact repair recipe, focused regression, or non-conflicting stack.

Before substantive source or branch writes, record the bounded claim required by `COORDINATION.md`. Tiny issue-only repair recipes, review comments, and focused evidence notes may remain lighter when they create no new mutable ownership.

Seek new authorization when work would widen scope, change authority, use private or production data, create external interaction, incur material cost, or cross another explicit boundary.

When review debt grows faster than dispositions, pause creation of new review surfaces and finish, consolidate, supersede, or close existing work. Prefer concrete nearby repair, composition, exact-head execution, evidence transfer, state synchronization, carrier retirement, and independent disposition before distant exploration. Reopen promotion or create a new surface only when new execution, consequence, novelty, or a narrow correction materially improves the decision.

## Canonical branch and carrier rules

Every execution carrier identifies the canonical source branch and head, exact workflow or command, resulting receipt or artifact, and canonical PR or finding that consumes the evidence.

After evidence transfer:

- remove temporary workflows from the canonical source branch;
- close disposable carrier PRs;
- update the canonical PR and finding with the retained result;
- do not leave execution-only branches in the active merge queue;
- do not cite a synthetic merge commit without naming the contained source head.

A carrier is retired only when a later exact head proves temporary machinery gone and the canonical source diff plus retained receipt are independently reviewable.

## Staleness and description hygiene

Before marking work ready, re-read the live issue, canonical finding, PR, checks, comments, dependencies, and current main.

Repair wording that says a dependency is pending after replacement, checks are running after completion, a branch is current after supersession, a review remains valid after input movement, an execution carrier is canonical, a focused run is a full gate, a gate proves paths it does not exercise, or future self-removal has already transferred evidence.

The issue-body `Issue state:` field must agree with the live `state:*` label. The issue-body `Finding state:` field must agree with the canonical finding. A generated index must carry a validation timestamp and exact referenced inputs or remain an explicit snapshot.

## Diff quality

Reviewability is part of correctness. Repair or reject broad formatting that hides behavior, generated files without reproducible identity, one test stack requiring unrelated production fixes, cleanup code that can replace the primary error, unbounded retained evidence, compatibility claims without negative controls, and authority expansion used only to make a test pass.

Prefer the smallest implementation that makes the invariant explicit and testable without broadening unrelated semantics.

## Promotion checklist

Before moving a pull request out of draft or advancing a finding:

- [ ] work class, canonical branch, exact head, and base are explicit;
- [ ] issue-body, issue-state, finding generation, finding state, and other decision inputs are versioned when relevant;
- [ ] every disposition-relevant claim has an accurate evidence class;
- [ ] `Evidence classes present` is an inventory, not a whole-record ranking;
- [ ] self-review confirmed the intended assertion ran and classified harness failures separately;
- [ ] every `full-gate` claim names the gate and coverage limits;
- [ ] complete current diff and current-main relation were reviewed;
- [ ] checks and failures are described truthfully;
- [ ] author eligibility, dependencies, and supersession are current;
- [ ] execution carriers are closed or clearly non-canonical;
- [ ] retired carriers are absent from the reviewed exact head;
- [ ] issue state and finding state are independently synchronized;
- [ ] uncertainty and clearing conditions are visible;
- [ ] upstream-contact authorization is explicit;
- [ ] no conversation text violates `REFERENCE_POLICY.md`.

## Relationship to coordination automation

These rules are the manual contract for coordination automation. An evaluator may detect stale heads, changed issue or finding states, mismatched evidence, conflicting ownership, incomplete receipts, and invalid promotion. Automation may derive and validate a queue, but it must not silently upgrade evidence, accept work, merge, or authorize upstream contact.
