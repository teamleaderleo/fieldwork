# Continuous coordination: research landscape and design direction

Date: **2026-07-30**  
State: **candidate synthesis**  
Fieldwork issue: **#138**  
Stensibly product issue: **teamleaderleo/stensibly#566**  
Upstream contact authorized: **false**

## In simple words

The useful idea is not merely to put a dependency graph inside CI.

The stronger direction is to treat current coordination state as an incrementally maintained, reconstructible projection over durable facts: source revisions, issues, claims, evidence, workflow receipts, reviews, decisions, policies, deployments, and authority records.

When an input changes, the system should explain:

- what actually changed;
- which current conclusions or actions depend on it;
- which prior results remain valid;
- which results became stale or ambiguous;
- which work is now eligible;
- which human decision is required;
- and which durable receipt supports every answer.

Build systems, self-adjusting computation, dataflow systems, asset orchestrators, GitOps controllers, durable workflow engines, provenance standards, and large-scale CI each solve part of this problem. None of the examined systems directly combines Fieldwork-style evidence classes, cross-repository coordination, human review, explicit authority, and recoverable agent work. The design should therefore adapt proven mechanisms without pretending an existing product already provides the complete contract.

## Question

What existing research and production systems should inform a CI-backed coordination graph for Fieldwork and a reusable continuous-coordination engine for Stensibly?

## Strongest conclusion

The first implementation should be a **read-only coordination compiler** with four defining properties:

1. **One versioned graph core, several projections.** Durable observations and explicit typed edges feed human queues, machine-readable status, affected-work reports, and later Stensibly views.
2. **Two relationship layers.** Hard readiness dependencies form an acyclic graph per generation; causal and historical relationships remain a separate event graph.
3. **Incremental evaluation with clean-rebuild equivalence.** Changed inputs invalidate only affected descendants, but periodic from-scratch evaluation remains the correctness oracle.
4. **Receipts, policy, and authority are inputs.** CI success is not truth by itself. A result is reusable only when its complete declared input fingerprint, evaluator identity, policy revision, and authority boundary still match.

The initial Fieldwork implementation should not assign workers, edit issues, request reviews, merge code, deploy, or contact upstream.

---

## Landscape

### 1. Build systems: dependency graphs, invalidation, and rebuild correctness

The most direct technical lineage comes from incremental build systems.

[Build Systems à la Carte](https://www.microsoft.com/en-us/research/publication/build-systems-a-la-carte/) separates two concerns that are often fused: the scheduling strategy and the rebuilding strategy. That distinction is directly useful here. Coordination policy should decide *whether* a node is valid or eligible; a scheduler should separately decide *when and where* eligible work runs.

[Bazel Skyframe](https://bazel.build/reference/skyframe) models evaluation as immutable keyed values in a dependency graph. Its incremental strategy invalidates the reverse transitive closure of changed inputs and uses **change pruning**: if reevaluation produces the same value, downstream nodes may remain valid. This is a strong model for changes that alter a provider revision or observation metadata without changing the semantic coordination result.

[Buck2's design account](https://engineering.fb.com/2023/04/06/open-source/buck2-open-source-large-scale-build-system/) argues for one persistent incremental dependency graph instead of several phase-specific graphs. The relevant lesson is not that Fieldwork should have one undifferentiated relationship type. It is that parsing, validation, projection, and execution eligibility should share one keyed evaluation substrate rather than repeatedly reconstructing incompatible graphs.

[Shake](https://shakebuild.com/manual) demonstrates dynamic dependency discovery while retaining explicit tracking, and emphasizes that build-rule changes themselves must participate in invalidation. Fieldwork therefore needs policy and evaluator revisions in the input fingerprint; changing evidence rules must be able to invalidate prior derived states.

[Salsa's red-green algorithm](https://salsa-rs.github.io/salsa/reference/algorithm.html) and [durability model](https://salsa-rs.github.io/salsa/reference/durability.html) suggest two useful implementation ideas:

- distinguish “input revision changed” from “derived value changed”;
- avoid repeatedly traversing dependencies whose inputs are known to change rarely.

Salsa also names **untracked dependencies** explicitly. That is a valuable failure category for coordination. A review based partly on an undocumented chat, local file, or unstated policy cannot be safely reused because the evaluator cannot know when that input changes.

#### Adopt

- stable keys and immutable versioned values;
- reverse-reachability invalidation;
- change pruning based on semantic value;
- explicit rule, policy, and toolchain versions;
- clean rebuild as a correctness oracle;
- separate rebuilding decisions from scheduling decisions.

#### Do not copy blindly

A source build normally has a single desired output for a target. Coordination may have competing candidates, partial evidence, human judgement, revocation, and authority boundaries. The evaluator needs typed states rather than a binary built/not-built result.

### 2. Self-adjusting computation: demand, traces, and affected work

[Adapton](https://www.cs.umd.edu/~mwh/papers/hammer13adapton.html) adds demand-driven incremental computation: changed inputs need not trigger recomputation of outputs nobody currently requests. This argues for supporting both:

- bottom-up invalidation when provider events arrive;
- top-down validation when a human or agent asks for a particular queue, decision, or target.

The system should not eagerly materialize every possible cross-project projection after every event.

Work on [self-adjusting computation](https://csd.cs.cmu.edu/academics/doctoral/degrees-conferred/umut-a-acar) emphasizes dependency traces and change propagation that remain equivalent to from-scratch execution. That equivalence is the right standard for Fieldwork's generated queue: the incremental result must match a clean evaluation over the same accepted inputs.

#### Adopt

- an evaluation trace sufficient to explain why a node was read and why it changed;
- demand-driven projection for interactive views;
- incremental and clean evaluation differential tests.

#### Limit

Do not dynamically infer authority, review requirements, or causal relationships merely because the evaluator observed a read. Dynamic reads can help discover technical dependencies, but consequential coordination edges require an explicit durable declaration.

### 3. Differential dataflow and incremental view maintenance: projections as maintained views

[Differential dataflow](https://www.microsoft.com/en-us/research/publication/differential-dataflow/) generalizes incremental computation to iterative graph calculations. It is relevant because useful coordination queries include transitive blockers, strongly connected components, critical paths, and recursive ancestry.

[Materialize's account of incremental view maintenance](https://materialize.com/blog/freshness/) frames derived results as continuously maintained views rather than repeated batch queries. Its recent description of [self-correcting materialized views](https://materialize.com/blog/self-correcting-materialized-views/) adds an especially useful idea: compare desired derived output with durably persisted output and write the difference so the projection converges after drift or version changes.

This suggests treating `REVIEW_QUEUE.md` as a materialized view:

- the normalized graph is the evaluated desired result;
- the committed generated file is the persisted result;
- CI compares them and reports the exact correction;
- the first slice fails on drift rather than silently rewriting the branch.

#### Adopt

- projections as derived views, not manually authoritative records;
- delta output between graph revisions;
- recursive graph queries without flattening them into procedural workflow code;
- self-correction checks between evaluated and persisted projections.

#### Defer

A full differential-dataflow runtime is unnecessary for the first Fieldwork graph. The first dataset is small enough for straightforward deterministic graph algorithms. Preserve an event and schema model that could later support incremental view infrastructure without prematurely adopting distributed streaming machinery.

### 4. Asset orchestration: reason about outputs, not only jobs

[Dagster's software-defined asset model](https://dagster.io/blog/software-defined-assets) argues that task-oriented orchestration often tells operators which jobs ran but not whether the assets they care about are current. Its declarative automation can materialize assets when upstream data changes, and its newer [virtual asset](https://dagster.io/blog/dagster-1-13-octopuss-garden) distinction recognizes outputs that update through their parents without requiring a separate materialization action.

This is highly applicable:

- a review packet or executed reproduction is a durable asset;
- a review disposition is a human-produced asset;
- the current queue entry is a **virtual derived asset** over those inputs;
- a workflow job is an action that may produce a receipt, not the thing whose currentness humans ultimately care about.

Dagster's asset-first framing also supports decentralized ownership: repositories own their local assets, while the combined graph exposes lineage and stale state.

#### Adopt

- first-class currentness and staleness for evidence, reviews, and decisions;
- asset-level explanations rather than only workflow-run status;
- virtual derived projections for queues and blocker views;
- independent asset checks that can gate downstream eligibility.

#### Avoid

Do not map every GitHub workflow job directly to a permanent coordination node. Jobs are executions; the durable output and its provenance matter more.

### 5. Controllers and GitOps: reconciliation, ownership, and drift

[Kubernetes controllers](https://kubernetes.io/docs/concepts/architecture/controller/) repeatedly compare desired and actual state and act to reduce the difference. Kubernetes deliberately uses many focused controllers rather than one controller that owns every aspect of the cluster.

[Argo CD](https://argo-cd.readthedocs.io/en/stable/) keeps Git as desired state, compares it with live state, reports drift, and allows manual or automatic synchronization. Its architecture separates repository rendering, API/status, and application reconciliation.

The corresponding Stensibly and Fieldwork lesson is:

- GitHub and repository files remain independently usable sources;
- the evaluator observes and projects;
- specialized adapters own narrow provider observations;
- a later mutation controller must declare exactly which fields or transitions it owns;
- drift is a normal explicit state, not evidence that one side should be overwritten blindly.

Recent Kubernetes work on controller-cache staleness reinforces that a cached observation needs visible freshness and cannot be treated as current merely because the controller is running.

#### Adopt

- desired/current separation;
- visible `synchronized`, `stale`, `degraded`, and `ambiguous` conditions;
- focused controllers or adapters with explicit ownership;
- idempotent reconciliation from current observations;
- periodic full reconciliation in addition to event-driven updates.

#### Reject for the first slice

Automatic convergence through issue edits, label changes, review requests, or dispatch. First establish trustworthy read-only evaluation and drift reporting.

### 6. Durable workflow engines: event history, replay, and human signals

Temporal's workflow model stores an event history and reconstructs workflow state through deterministic replay. Its determinism contract is that the same history and workflow definition must produce the same command sequence. A signal, including a human action, becomes part of durable history rather than an ephemeral in-memory callback.

This is useful for later Stensibly execution, but it should not replace the current-state graph:

- the causal event history explains how work reached the present;
- the readiness graph computes what is currently valid and eligible;
- a human approval is a durable event and a versioned decision asset;
- changing the reviewed input set creates a new decision generation rather than retroactively editing history.

#### Adopt

- append-only event identities;
- deterministic replay tests for coordination transitions;
- durable human signals bound to one workflow and generation;
- explicit versioning when evaluator logic changes.

#### Avoid

Do not force the current queue to be recovered only by replaying an unbounded event history. Retain compact accepted snapshots and projections with links to causal history.

### 7. Provenance and attestations: receipts need subjects, inputs, and producers

[SLSA provenance](https://slsa.dev/spec/v1.2/provenance) describes where, when, and how an artifact was produced. Its build-provenance model separates the build definition, external parameters, resolved dependencies, builder identity, run metadata, subjects, and useful byproducts.

The [in-toto Attestation Framework](https://in-toto.io/) supplies a general statement structure that binds a predicate to a subject. [Tekton Chains](https://tekton.dev/docs/chains/slsa-provenance/) demonstrates generating provenance from task executions, while Tekton's result documentation exposes an important warning: declaring an expected result does not necessarily mean the task produced it unless the consumer or controller enforces that requirement.

For coordination receipts, the important fields are:

- subject: the exact evidence, review, decision, projection, or action output;
- predicate type: what kind of claim the receipt makes;
- input materials: exact source, policy, dependency, fixture, and prior receipt revisions;
- evaluator or builder identity;
- invocation and environment identity;
- result state and semantic value hash;
- byproducts: logs, reports, graph diffs, or diagnostic artifacts;
- authority boundary: what the receipt explicitly does **not** authorize.

#### Adopt

- an attestation-shaped envelope rather than ad hoc workflow-status parsing;
- cryptographic digests for subjects and declared inputs;
- explicit evaluator identity and build type;
- verification separate from generation.

#### Do not overclaim

A signed or platform-generated attestation proves origin and integrity only to the strength of its trust model. It does not prove that the test was well designed, the evidence class was correct, or the human conclusion was sound.

### 8. Policy engines: decisions are outputs with policy revisions

[Open Policy Agent decision logs](https://www.openpolicyagent.org/docs/management-decision-logs) attach a decision ID, input, result, policy bundle revision, and trace context. OPA bundles permit policy and data to change independently from application deployment.

Fieldwork should similarly treat an evidence or authority policy evaluation as a durable derived decision:

- exact policy revision;
- bounded input document;
- allow, deny, warn, or unknown result;
- explanation or violated rule IDs;
- separate log and redacted public projection.

#### Adopt

- policy bundle revisions in every affected receipt;
- attributable decision IDs;
- redaction and bounded decision logging;
- policy evaluation as a pure input/output boundary.

#### Defer

Embedding OPA itself is optional. A small deterministic TypeScript or Python policy layer may be clearer initially, provided the policy identity and decision record remain explicit.

### 9. Selective CI: affected work, two-speed validation, and risk scheduling

[Nx affected](https://nx.dev/docs/features/ci-features/affected) combines Git history with a project graph to select affected tasks. [Pants](https://www.pantsbuild.org/stable/docs/using-pants/advanced-target-selection) similarly uses changed files and transitive dependency knowledge.

Google's published work on [regression-test selection](https://research.google/pubs/techniques-for-improving-regression-testing-in-continuous-integration-development-environments/) and [post-submit breakage scheduling](https://research.google/pubs/what-breaks-google/) shows why large systems split fast pre-submit selection from broader post-submit validation. More recent Google work uses prediction to prioritize likely novel failures, but prediction changes ordering rather than the underlying correctness contract.

Fieldwork should use a similar two-speed structure:

1. **PR/event fast path** — schema, changed records, local graph validity, affected entries, generated-output drift.
2. **Scheduled/manual full reconciliation** — all live records, current heads, current workflow receipts, broken evidence links, cross-branch drift, and clean-rebuild comparison.

Later, risk scoring may order the review queue, but must not suppress mandatory structural or policy checks.

#### Adopt

- affected-subgraph evaluation;
- explicit baseline identity, preferably the last accepted graph revision rather than merely `main`;
- fast and comprehensive validation tiers;
- culprit and explanation traces for newly broken graph states.

#### Reject

Git diff alone as the change model. Issue labels, workflow conclusions, approvals, policy revisions, external repository heads, and expired authority can change without a Fieldwork source diff.

### 10. GitHub Actions: useful transport, weak canonical store

GitHub Actions provides event triggers, workflow artifacts, job summaries, environments, required reviewers, custom deployment protection rules, and concurrency groups. These are useful execution and notification primitives.

However:

- concurrency groups are queue-management tools, not durable leases;
- workflow ordering and cancellation semantics must not be treated as causal truth;
- environment approval is scoped to a workflow job, not automatically to a Fieldwork evidence or upstream-contact decision;
- workflow artifacts expire unless copied into durable storage;
- workflow definitions are executable privileged code and require their own revision and security boundary;
- cross-repository dispatch is at-least-once style transport and needs an idempotency identity and read-after-write reconciliation.

Recent empirical studies of GitHub Actions report that larger, more complex workflows correlate with greater failure and maintenance burden. That supports keeping the evaluator core independent from YAML and making workflows thin adapters.

#### Adopt

- Actions for event intake, bounded execution, summaries, annotations, and artifact transport;
- concurrency keys as a local duplicate-work optimization;
- environments for later protected effects such as deployment;
- minimal permissions and pinned action revisions.

#### Reject

- workflow runs as the canonical graph database;
- a giant generated workflow with one job per coordination node;
- automatic mutation simply because a status check passed;
- using a cancelled run as proof that its underlying work was superseded safely.

---

## Design decisions

### D1. The queue is a virtual materialized view

`REVIEW_QUEUE.md` and dashboard views are generated projections. They are not independent sources. A committed generated file is useful for review and offline recovery, but CI must compare it to the evaluated graph and fail on drift.

### D2. Use one evaluation substrate with typed relationship classes

Use one keyed graph store and evaluation engine, but do not collapse all edges into readiness dependencies.

Required classes:

- hard readiness;
- evidence consumption;
- review and decision requirements;
- authority requirements;
- production/output;
- supersession and generation;
- causal/history;
- related-only.

Only hard readiness edges participate in cycle rejection and topological eligibility.

### D3. Every current result has a generation and semantic value

A node should retain:

- stable identity;
- generation or exact revision;
- raw observation fingerprint;
- semantic value fingerprint;
- evaluator and policy revision;
- current condition;
- prior accepted result, if any.

A raw input revision may change while the semantic value remains equal. In that case change pruning can preserve descendants while recording the new observation.

### D4. Support bottom-up invalidation and top-down validation

- Provider events and repository changes invalidate the reverse reachable subgraph.
- Interactive reads validate only the requested projection and dependencies.
- Scheduled reconciliation performs a full clean evaluation.

### D5. Add durability tiers

Suggested tiers:

- **high:** schema definitions, evidence taxonomy, reference policy, stable project instructions;
- **medium:** pinned research reports, accepted decisions, merged revisions;
- **low:** open issue labels, PR heads, workflow runs, active claims, current blockers;
- **ephemeral:** notifications and UI caches.

Durability is an optimization hint, never permission to ignore a known change.

### D6. Model undeclared inputs explicitly

An evaluation may return `untracked_input` or `incomplete_input_set`. Such a result cannot be cached as accepted. The report should name what was missing without importing unrestricted private content.

### D7. Human decisions are versioned assets

A review or authorization binds to:

- exact subject and scope;
- exact input fingerprint;
- policy revision;
- reviewer identity and independence class;
- disposition;
- expiry or invalidation rules.

Changed consequential inputs create a stale decision and require a new generation. Historical approval remains visible but no longer gates the current action.

### D8. Keep correctness and prioritization separate

The evaluator determines validity, staleness, eligibility, and blockers deterministically. A separate ranking function may order eligible items by risk, review cost, age, critical path, or expected information gain.

Heuristic ranking must not:

- upgrade evidence;
- remove mandatory tests;
- authorize effects;
- claim that low-ranked work is unaffected.

### D9. Use attestation-shaped receipts

Do not invent a signature format in the first slice. Define a JSON receipt that can later be expressed as an in-toto statement or SLSA-style predicate.

Minimum receipt groups:

```text
identity and schema
subject and semantic result
resolved declared inputs
policy and evaluator revision
execution environment
causal and correlation identifiers
public explanation
private/redacted byproduct references
authority boundary
```

### D10. Make “why?” a first-class query

For any queue state, the evaluator should return an explanation path such as:

```text
RQ-002 is execution-gated
because review input biome-report@A depends on workflow-receipt@B
and current PR head C differs from tested head D.
```

The explanation should distinguish the first invalidating cause from additional downstream consequences.

---

## Proposed architecture

```text
GitHub/repository observations       Stensibly accepted records
               \                         /
                -> bounded source adapters
                           |
                    normalized facts
                           |
               explicit graph declarations
                           |
                coordination evaluator core
                 /          |            \
        clean evaluator  incremental     policy
                         evaluator       decisions
                 \          |            /
                  accepted graph revision
                  /        |            \
          queue view   affected set   receipt set
             |             |              |
       Markdown/UI      CI summary     artifacts/API
```

### Core boundary

The evaluator core should be a pure library over bounded JSON-like records. It should not call GitHub, edit files, or dispatch workflows.

### Source adapters

Adapters convert provider observations into normalized facts and preserve:

- provider identity;
- observation revision;
- fetched-at and provider-updated timestamps;
- synchronization condition;
- raw-content digest where permitted;
- bounded fields used by evaluation.

### Graph declaration layer

The first graph can remain explicit in repository YAML. Later, some edges may be derived from typed Fieldwork records, but the generated edge must state its derivation rule and source revision.

### Evaluation store

The store retains:

- accepted input revisions;
- node semantic values;
- dependency reads;
- evaluation receipts;
- graph generation;
- supersession and invalidation causes.

The persisted store is a cache and audit aid. A clean rebuild from durable inputs must recover the same current projection.

---

## CI topology

### Workflow A — pull-request validation

Trigger on coordination schema, graph, generator, and generated-view changes.

Run:

1. schema and policy validation;
2. reference-policy validation;
3. local graph construction;
4. hard-cycle and duplicate-producer checks;
5. changed-node and affected-entry calculation against the accepted base graph;
6. generated projection comparison;
7. unit and golden tests;
8. concise job summary.

No network mutation and no secrets.

### Workflow B — live reconciliation

Trigger manually and on a bounded schedule. Later it may also respond to signed/provider events.

Run:

1. fetch current issues, PR heads, checks, and workflow receipts;
2. create immutable observation records;
3. evaluate the full graph cleanly;
4. compare with the most recent incremental projection;
5. report stale observations, missing receipts, and drift;
6. publish bounded artifacts and attestable receipt data.

Initially read-only.

### Workflow C — repository-native execution

Each target repository owns its native tests. A Fieldwork or Stensibly workflow may request execution later, but the target repository publishes the receipt.

The request and receipt require:

- stable request ID;
- target repository and exact ref;
- action type and declared inputs;
- expected output schema;
- caller and authority scope;
- idempotent replay behavior;
- current result readback.

Do not implement this in the first slice.

### Workflow D — periodic clean-rebuild canary

Rebuild the graph without incremental cache and compare normalized outputs. A difference is an evaluator correctness incident, not an ordinary stale queue entry.

---

## Candidate data model

### Node declaration

```yaml
id: review:mcp-reconnect-ownership
generation: 3
kind: technical_review
workspace: default
project: fieldwork
subject:
  type: fieldwork_pr
  id: teamleaderleo/fieldwork#82
inputs:
  - id: evidence:mcp-reconnect-public-path
    required_state: executed_reproduction
  - id: policy:fieldwork-evidence
    revision: 2
requires:
  - edge: requires_independent_review
    node: evidence:mcp-reconnect-public-path
produces:
  - review_disposition
  - upstream_contact_recommendation
authority:
  grants_upstream_contact: false
```

### Evaluation receipt

```yaml
schema: stensibly.coordination-evaluation/v0
receipt_id: eval_...
graph_generation: 14
subject:
  node_id: review:mcp-reconnect-ownership
  node_generation: 3
result:
  condition: ready_for_human_review
  semantic_digest: sha256:...
resolved_inputs:
  - id: evidence:mcp-reconnect-public-path
    generation: 2
    digest: sha256:...
evaluator:
  id: fieldwork-coordination-compiler
  revision: git:...
policy:
  id: fieldwork-evidence
  revision: 2
explanation:
  rule_ids:
    - evidence.executed-reproduction-present
    - review.independence-required
  first_blocker: null
authority:
  effects_performed: []
  effects_authorized: []
```

Names and schemas remain provisional.

---

## Failure taxonomy

Retain these distinct conditions:

- `invalid_structure` — malformed record, missing endpoint, duplicate identity;
- `readiness_cycle` — hard dependency cycle;
- `duplicate_exclusive_producer` — conflicting owner or output without explicit competition;
- `stale_input` — current provider/source revision differs;
- `changed_semantics` — reevaluation produced a different value;
- `changed_observation_same_semantics` — change-pruned result;
- `missing_receipt` — required output absent;
- `incomplete_receipt` — execution ended without required result;
- `untracked_input` — consequential undeclared dependency;
- `policy_drift` — policy revision changed;
- `authority_mismatch` — approval or grant does not bind current generation;
- `ambiguous_external_effect` — provider mutation outcome unresolved;
- `degraded_observation` — source unavailable or cache freshness uncertain;
- `nondeterministic_evaluation` — clean and incremental outputs disagree;
- `projection_drift` — committed generated view differs from evaluated output.

Only structural contradictions and evaluator nondeterminism should necessarily fail the entire compiler. Ordinary incomplete research should produce a valid blocked or execution-gated graph state.

---

## Negative results and rejected shortcuts

### One giant DAG is insufficient

Review/revision loops, retries, recovery, and supersession are causal history. Encoding them as readiness edges either creates false cycles or destroys history.

### A workflow engine alone is insufficient

Durable workflow replay is valuable for one execution, but the current portfolio spans many independently owned records and repositories. Currentness and evidence validity require an asset/readiness projection beyond workflow history.

### A project-management board alone is insufficient

A board can display state but ordinarily cannot prove which source revision, test receipt, evidence class, policy version, and authority generation support it.

### Signatures alone are insufficient

Attestation integrity does not validate the underlying scientific or engineering claim.

### Git diff alone is insufficient

Provider state and authority can change without a repository diff.

### Fully inferred dependencies are unsafe

Hidden technical reads may be discovered dynamically, but review, authority, and causal edges must remain explicit.

### Risk prediction is not correctness

Prediction can prioritize work but must not erase deterministic mandatory checks or represent untested descendants as valid.

### Immediate automatic mutation is premature

A read-only evaluator will expose schema and invalidation mistakes without creating issue churn, duplicate dispatch, or unsafe authority transitions.

---

## Recommended implementation sequence

### Slice 0 — settle the research contract

- Review this landscape against #138 and Stensibly #566.
- Choose the initial terminology: recommended working term **continuous coordination**; implementation component **coordination compiler**.
- Record explicit non-goals and mutation boundary.

### Slice 1 — pure graph compiler

Implement in Fieldwork or a small shared package:

- schema parser;
- stable canonical JSON;
- node and edge validation;
- readiness cycle detection;
- duplicate producer and path detection;
- deterministic topological evaluation;
- queue generation;
- explanation traces;
- clean rebuild mode.

Use static fixtures only.

### Slice 2 — convert PR #105 seed data

- Replace duplicated human/machine queue maintenance with one source graph.
- Generate both `REVIEW_QUEUE.md` and normalized graph JSON.
- Add golden tests for all eight queue entries.
- Fail on generated drift.

### Slice 3 — live read-only GitHub observations

- Fetch bounded issue labels/state, PR head/state, and workflow receipts.
- Store exact observation identity and freshness.
- Reconcile the current queue without mutating GitHub.
- Add a manual full-reconciliation workflow.

### Slice 4 — incremental evaluator

- persist accepted graph revision and dependency reads;
- bottom-up invalidation;
- semantic change pruning;
- top-down requested projections;
- affected-entry report;
- clean-versus-incremental differential test.

### Slice 5 — Stensibly ingestion and dashboard

- ingest graph and receipt projections;
- preserve Fieldwork as independently usable;
- expose currentness, explanation, synchronization, and causal references;
- do not add dispatch or mutation yet.

### Slice 6 — federated target receipts

- define request and receipt envelopes;
- run target-native tests in target repositories;
- add idempotency and readback;
- evaluate provenance and trust requirements.

### Slice 7 — protected effects

Only after the prior slices survive dogfood:

- human-gated dispatch;
- claim or reviewer proposals;
- custom deployment/action protection;
- limited fix-forward actions;
- explicit upstream-contact node that cannot be satisfied by CI alone.

---

## Evaluation plan

### Correctness

- incremental result equals clean rebuild;
- deterministic output across Node/Bun and operating systems;
- no evidence-class promotion;
- exact affected-descendant sets for fixture changes;
- historical decisions remain but stop gating changed inputs;
- policy and authority revisions invalidate correctly.

### Performance

- graph parse and full evaluation time;
- incremental evaluation time by changed node class;
- number of visited and recomputed nodes;
- change-pruning rate;
- artifact and API request volume;
- queue notification reduction.

### Operability

- explanation usefulness to a fresh reviewer;
- recovery after cache loss;
- degraded-provider behavior;
- CI workflow complexity and maintenance burden;
- false structural failures versus useful blocked states.

### Security and privacy

- bounded untrusted provider fields;
- no issue prose execution;
- minimal workflow permissions;
- protected secrets absent from read-only jobs;
- redacted public receipts;
- workspace and project isolation;
- no authority inferred from provider or CI status.

---

## Open research questions

1. Which changes should use semantic change pruning versus conservative descendant invalidation?
2. Should the accepted graph revision be committed, stored by Stensibly, or both?
3. What is the minimum interoperable coordination receipt predicate?
4. How should independent human review be represented without overexposing identity or private deliberation?
5. Which graph edges may be derived mechanically from Fieldwork issue forms and which must remain authored?
6. How should a cross-repository request prove that the target workflow definition and ref match the request?
7. When a provider observation is degraded, which read-only projections may remain usable and which effects must fail closed?
8. Can recursive affected-work and critical-path queries remain simple graph algorithms at expected scale, or does Stensibly eventually benefit from incremental view infrastructure?
9. What clean-rebuild cadence catches evaluator bugs without creating pointless CI load?
10. What is the smallest useful human-facing explanation format that remains stable across adapters?

## Recommendation

Proceed with Slices 0–2 now.

Do **not** start with distributed execution, signed receipts, risk prediction, or automatic issue mutation. The highest-value next proof is that one source graph can deterministically generate the existing Fieldwork review queue, preserve evidence categories, detect stale inputs, and explain affected work while matching a clean rebuild.

If that works, Stensibly gains a concrete product primitive rather than another abstract orchestration proposal. If it fails, the failure will reveal whether the problem is schema ambiguity, undeclared dependencies, unstable semantics, or insufficient source records before those defects are multiplied across repositories and agents.

## Source index

The machine-readable companion is [`source-map.yml`](source-map.yml). It records the sources, concepts, and current adopt/adapt/reject disposition used in this synthesis.
