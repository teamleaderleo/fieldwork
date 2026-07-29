# Continuous coordination: operational, cache, and postmortem lessons

Date: **2026-07-30**  
State: **research addendum**  
Related: Fieldwork #138, PR #154, `teamleaderleo/stensibly#566`  
Upstream contact authorized: **false**

## In simple words

Even a correct coordination graph can become dangerous if its incremental cache, evaluator rollout, or operational signals are wrong.

The system therefore needs a reliability discipline around the compiler itself:

- reproducible clean rebuilds;
- observable cache decisions;
- canary evaluation of compiler changes;
- conservative fallback when currentness is uncertain;
- incident records for incorrect invalidation, false reuse, or projection drift;
- and regression fixtures derived from every consequential evaluator failure.

## Release-engineering lesson

Google's [Site Reliability Engineering release-engineering chapter](https://sre.google/sre-book/release-engineering/) argues that reliable services require reproducible and automated release processes, and that changes to the release process should be intentional rather than accidental.

For continuous coordination, the evaluated queue is itself a released artifact. The coordination compiler therefore needs:

- a pinned evaluator revision;
- a pinned graph schema and policy revision;
- deterministic canonical output;
- a reproducible clean-evaluation command;
- a retained summary of inputs and outputs;
- intentional rollout of rule changes.

A changed evidence policy is equivalent to changing a compiler or build rule. It must participate in invalidation and should not be deployed as an invisible configuration edit.

## Launch-coordination lesson

The SRE chapter on [reliable product launches at scale](https://sre.google/sre-book/reliable-product-launches/) describes dedicated launch coordination and reusable launch checklists.

The relevant design lesson is not to encode every checklist answer as automation. It is to make recurring coordination questions explicit, reviewable inputs:

- Is the exact revision known?
- Is the evidence executed, source-confirmed, modelled, or merely prepared?
- Is an independent review required?
- Has the reviewed subject changed?
- Does the decision authorize an effect, or only recommend one?
- Is rollback or recovery defined?

A checklist item should become one of:

- a deterministic validation rule;
- an explicit human-gate node;
- an informational warning;
- or a documented non-goal.

Avoid a checkbox that appears satisfied merely because a workflow completed.

## Reliable-build lesson: undeclared resources are correctness defects

[A model and framework for reliable build systems](https://arxiv.org/abs/1203.2704) focuses on invalid outputs and nondeterminism caused by incorrectly declared dependencies and models the resources accessed by build tasks.

The corresponding coordination rule is:

> A current result is reusable only when every consequential input is either declared or explicitly classified as untracked.

Consequential resources include more than files:

- source and target revisions;
- live issue state;
- PR head;
- workflow definition and tested command;
- environment and fixture identity;
- evidence and reference policy;
- reviewer scope;
- authority generation;
- private context that materially affected a judgement.

Private context does not need to be copied into the public graph. It does need a bounded presence marker or a result such as `incomplete_input_set`, preventing unsafe cache reuse.

## CI-cache lesson: performance state requires maintenance

A 2026 preprint, [The Promise and Reality of Continuous Integration Caching](https://arxiv.org/abs/2601.19146), analyzed a large Travis CI dataset. It reports uneven performance benefits, ongoing cache-maintenance work, and stale cached artifacts in a substantial share of cache-enabled projects.

This is empirical evidence from one platform and should not be generalized mechanically to Fieldwork. It still reinforces a sound operational conclusion: caching is a managed subsystem, not a free optimization.

The coordination compiler should record for each reuse decision:

```text
cache key or prior receipt identity
complete input fingerprint
evaluator and policy revision
reason reuse was accepted
age and freshness boundary
last clean confirmation
fallback taken when reuse was rejected
```

Required cache controls:

- manual and scheduled cache-bypass mode;
- periodic clean rebuild comparison;
- cache schema/version fencing;
- bounded retention;
- visible hit, miss, invalidated, and ambiguous counters;
- no cache hit when an input is untracked or a provider observation is degraded;
- easy deletion and reconstruction from durable facts.

Do not optimize before collecting full-evaluation and affected-evaluation measurements. At the first Fieldwork scale, correctness is worth far more than avoiding a few graph traversals.

## Canary lesson: evaluate evaluator changes against a control

The [Site Reliability Workbook chapter on canarying releases](https://sre.google/workbook/canarying-releases/) emphasizes representative, attributable metrics and warns against weak before/after inference.

A compiler or policy change should first run in shadow or canary mode:

1. keep the accepted evaluator as the control;
2. run the candidate evaluator over the same immutable graph inputs;
3. compare normalized node values, queue order, blockers, affected sets, and explanations;
4. classify every difference as expected, defect, or unresolved;
5. require review for evidence, authority, or eligibility changes;
6. promote only after fixture and live-shadow results agree.

Candidate evaluation must not mutate live issues or dispatch work. A performance improvement does not justify unexplained semantic differences.

## Postmortem lesson: evaluator correctness incidents need durable learning

The [Google SRE book](https://sre.google/sre-book/table-of-contents/) treats postmortems, data integrity, launch coordination, and automation as connected reliability practices.

A coordination incident includes:

- a stale result reused after a consequential input changed;
- an unaffected node invalidated because of an overbroad dependency;
- a current node left valid because of a missing dependency;
- incremental and clean evaluation disagreement;
- evidence-class promotion;
- an authorization applied to the wrong generation or scope;
- a notification storm caused by unstable derived state;
- a provider or workflow result accepted without durable output.

Each consequential incident should retain:

```text
incident identity and severity
first incorrect graph revision
last known correct revision
input and evaluator revisions
observed projection
correct projection
causal and contributing conditions
why existing checks did not catch it
repair and recovery actions
new regression fixture
whether existing accepted decisions were affected
```

The purpose is not blame. It is to convert hidden evaluator assumptions into explicit dependencies, invariants, or tests.

## Proposed operational conditions

Every accepted graph revision should expose:

- `evaluation_mode`: `clean`, `incremental`, or `shadow`;
- `input_completeness`: `complete`, `bounded_partial`, or `unknown`;
- `provider_condition`: `current`, `stale`, `degraded`, or `ambiguous`;
- `cache_condition`: `not_used`, `hit`, `miss`, `invalidated`, or `bypassed`;
- `projection_condition`: `matching`, `drifted`, or `unpublished`;
- `authority_condition`: `not_required`, `missing`, `current`, `stale`, or `mismatched`;
- `clean_confirmation_revision` and time;
- `evaluator_revision` and policy revision.

These conditions should be machine-readable and summarized in the human output. They should not all become blocking errors.

## Failure severity

Suggested severity treatment:

### Compiler-blocking

- malformed graph or duplicate identity;
- hard readiness cycle;
- nondeterministic clean evaluation;
- clean and incremental semantic disagreement;
- evidence-class promotion by the evaluator;
- authority granted or consumed outside its exact scope.

### Projection-blocking

- generated queue drift;
- stale reviewed subject;
- missing required receipt;
- unresolved exclusive producer conflict;
- provider observation too degraded for a currentness claim.

The graph remains inspectable, but the affected projection must not claim current readiness.

### Warning or measured debt

- conservative over-invalidation;
- cache miss;
- low durability or old clean confirmation;
- optional source temporarily unavailable;
- ranking changed while validity remained equal.

## Metrics worth collecting

Correctness first:

- incremental/clean mismatch count;
- false reuse incidents;
- over-invalidation fixtures;
- nodes with untracked inputs;
- stale human decisions detected;
- evidence-class invariant failures.

Then performance and signal quality:

- full versus incremental evaluation duration;
- nodes visited and recomputed;
- semantic change-pruning rate;
- cache hit rate by node type;
- time from source change to accurate queue projection;
- number of material versus unchanged notifications;
- human review time attributable to explanation quality.

Do not optimize for raw cache hit rate. A lower hit rate with trustworthy currentness is better than fast stale coordination.

## Additional implementation requirements

Add to the recommended first slices:

1. a `--clean` mode that ignores all prior evaluation state;
2. a `--compare-incremental` mode that fails on semantic differences;
3. golden fixtures for stale reuse, missing dependency, and over-invalidation;
4. explicit cache and provider conditions in evaluation receipts;
5. a shadow-mode report for future evaluator and policy changes;
6. a lightweight evaluator-incident template;
7. a scheduled cache-bypass reconciliation run once live observations are added.

## Recommendation

Treat the first coordination compiler as a correctness-sensitive compiler and controller, not as a dashboard generator.

The operational acceptance gate should be:

> The same bounded durable inputs produce the same semantic graph under clean and incremental evaluation, and every reuse, invalidation, human gate, and degraded state has an attributable explanation.

Upstream contact authorized: `false`.
