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

## Preserve evidence class

Use the narrowest accurate evidence description. Recommended classes are:

- `source-read` — implementation, tests, history, or contracts were inspected;
- `model-executed` — an isolated model or dependency-free probe ran;
- `target-test-prepared` — a target-native test exists but has no retained execution receipt;
- `target-executed` — the target package or repository test ran at an exact head;
- `integration-executed` — a real owned integration, browser, process, provider, or platform path ran;
- `full-gate` — the named repository-declared gate ran at the exact candidate head. The receipt must name that gate or command set and state important integration, platform, provider, authority, recovery, or ecosystem paths it does not exercise. `full-gate` does not imply coverage outside the named gate.

Do not upgrade evidence during synthesis. In particular:

- a model is not package execution;
- a prepared test is not a failing test;
- one platform run is not a cross-platform result;
- a focused test is not a full gate;
- a named full gate is not proof of behavior outside the paths that gate exercises;
- full CI is not proof of an untested security, authority, or lifecycle property;
- one owned testbed is not ecosystem impact.

## Exact-head review receipt

A promotion review should record:

- repository and pull request;
- canonical branch and exact head SHA;
- exact base or current-main revision used for comparison;
- changed-file fence or complete-diff scope;
- work class and evidence class;
- validation commands, workflow runs, platforms, and retained results;
- unresolved failures, skipped jobs, and checks that did not run;
- dependencies, replacements, and superseded branches;
- reviewed coordination inputs when they affect the decision, including the issue number and an accepted issue-body generation such as `updated_at`, body digest, or explicit revision marker;
- whether upstream contact remains unauthorized;
- reviewer disposition and clearing condition.

A code head is not the only possible review input. When the invariant, review ask, state, clearing condition, authority boundary, or promotion request comes from an issue or decision record, the receipt must version that input too.

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
- a named full gate proves integrations or properties it did not exercise.

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
- [ ] evidence class is accurate;
- [ ] every `full-gate` claim names the gate and its material coverage limits;
- [ ] current-main relation is known;
- [ ] complete current diff was reviewed;
- [ ] checks and failures are described truthfully;
- [ ] author eligibility is explicit;
- [ ] dependencies and supersession are current;
- [ ] execution carriers are closed or clearly non-canonical;
- [ ] issue state text and labels agree;
- [ ] uncertainty and clearing conditions are visible;
- [ ] upstream-contact authorization is explicit;
- [ ] no direct third-party reference violates `REFERENCE_POLICY.md`.

## Relationship to coordination automation

The rules in this file are the manual contract for generated coordination work. A future evaluator may detect stale heads, changed dependencies, mismatched evidence classes, conflicting ownership, incomplete receipts, and invalid promotion states. Automation may derive and validate a queue, but it must not silently upgrade evidence, issue acceptance, merge work, or authorize upstream contact.
