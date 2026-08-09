# High-value bug lenses

## In simple words

Some defects are valuable to learn to see because they hide behind code that looks locally reasonable. Use these lenses after the first code map, when deciding where to probe and what invariants deserve explicit tests.

This is a search aid, not a preset bug checklist. The target's code, tests, contracts, and actual use decide which lenses apply.

## Start with the invariant

Before hunting a line-level mistake, write the property that must survive every relevant path.

Examples:

- one logical operation produces at most one durable effect;
- an unauthorized caller can never cause an authorized side effect;
- cancellation leaves no owned child, lock, lease, file, or partial publication behind;
- a retry cannot duplicate a completed write;
- a cache entry becomes visible only after it is complete;
- a state transition cannot skip required validation;
- an API response, stored record, and downstream event agree on identity and version.

Then ask: **what sequence of events could make this property false while each local component still appears reasonable?**

That question is often more productive than searching for suspicious syntax.

## 1. Concurrency, ordering, and partial failure

Look for behavior whose correctness depends on time or interleaving:

- read-modify-write sequences without a single owner;
- duplicate delivery, retry, replay, and timeout paths;
- cancellation racing completion;
- cache fill and invalidation overlap;
- lock acquisition and release across error paths;
- work acknowledged before its durable effect exists;
- cleanup racing a successor operation;
- two components with different ideas of "done".

Useful probes deliberately reorder events, duplicate them, interrupt between phases, delay one owner, and rerun immediately.

## 2. State and lifecycle

Model important components as states and transitions, even when the code does not call them a state machine.

Ask:

- who owns the current state;
- which transitions are legal;
- what initializes and tears down each resource;
- whether teardown is idempotent;
- whether stale callbacks, handles, sessions, or workers can act after replacement;
- whether failure can strand a half-transitioned object;
- whether reuse begins from a genuinely clean state.

High-yield cases include reconnect, restart, cancellation, repeated execution, exception during setup, partial teardown, and replacement while old work is still completing.

## 3. Data integrity and reconciliation

Prefer defects that can silently create a believable wrong answer.

Trace:

- uniqueness and identity;
- atomicity and publication boundaries;
- lost updates and double writes;
- truncation and partial serialization;
- schema and migration assumptions;
- rounding, units, time zones, and representation conversions;
- idempotency keys and replay handling;
- reconciliation between primary records, caches, indexes, queues, and derived views.

A useful test asks whether two independently derived views of the same fact can disagree and which one wins.

## 4. Trust and authority boundaries

Map every place where one component acts with authority on behalf of another.

Ask:

- who authenticated the identity;
- who authorized this exact operation;
- whether identity is rebound between check and use;
- whether a path, object, tenant, account, capability, or resource can change after validation;
- whether a downstream component assumes an upstream check already happened;
- whether parsing, normalization, decoding, or aliasing changes what object the check referred to.

The valuable bugs often live in gaps between individually reasonable checks.

## 5. Cross-layer contract drift

Trace one operation end to end: caller → public API → internal representation → persistence or remote boundary → async work → returned result or later observation.

Compare what each layer believes about:

- identity;
- ordering;
- completeness;
- nullability and absence;
- retries and duplicates;
- ownership;
- error semantics;
- versioning;
- metadata;
- visibility and durability.

A defect can survive for a long time when every layer is internally consistent and their contracts disagree.

## 6. Nonlinear performance and resource collapse

Look beyond slow individual calls. Search for variables whose cost compounds with load:

- nested scans and accidental quadratic work;
- fan-out per request;
- lock contention and serialized hot paths;
- unbounded queues;
- retry amplification;
- cache stampedes;
- hot partitions or single-owner bottlenecks;
- per-item allocations retained across batches;
- descriptors, sockets, tasks, subprocesses, or buffers whose lifetime exceeds the request.

Measure across increasing input size or concurrency. A useful performance investigation explains the scaling variable and the resource that saturates.

## 7. Specification and semantic disagreement

Sometimes the implementation faithfully performs the wrong contract.

Compare:

- public documentation;
- types and schemas;
- tests;
- implementation;
- examples;
- downstream assumptions;
- protocol or standard text when applicable;
- realistic integration behavior.

When these disagree, identify the invariant the system should preserve before choosing a patch. Updating code to match a mistaken test can deepen the defect.

## Predict where future bugs will cluster

Before a defect is known, rank areas where several of these conditions meet:

1. state has more than one apparent owner;
2. correctness spans asynchronous phases;
3. retries, interruption, or cleanup exist;
4. identity or representation changes across a boundary;
5. one layer trusts a property established elsewhere;
6. data is duplicated into caches, queues, indexes, or derived views;
7. compatibility depends on invisible metadata;
8. load changes ordering, batching, or resource ownership;
9. tests assert symptoms while the underlying invariant stays implicit.

These are strong scout candidates because a small local implementation can carry a much larger behavioral contract.

## Turn a lens into evidence

For any chosen lens, record:

1. **Invariant** — the property that should hold.
2. **Owners** — components responsible for preserving it.
3. **Failure sequence** — the smallest event sequence that could violate it.
4. **Distinguishing probe** — a test with at least two plausible outcomes.
5. **Negative control** — evidence that the probe can also recognize correct behavior.
6. **Surviving state** — files, records, processes, locks, messages, caches, metadata, or external effects left afterward.
7. **Repair boundary** — the smallest owner that can enforce the invariant cleanly.
8. **Reopen trigger** — the exact new condition that would make the conclusion incomplete.

The goal is to move from "this code looks suspicious" to "this invariant fails under this sequence, at this owner, with this durable consequence."