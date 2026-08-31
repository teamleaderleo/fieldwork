# Code-First Investigation

## In simple words

Understand the actual program, make the important behaviour fail or succeed under controlled conditions, and explain why a change would improve something real. Do not default to linting, documentation, cosmetic cleanup, or issue-volume work.

## Purpose

Fieldwork exists to do consequential engineering research. The goal is not to prove that every large repository contains a patch for us. The goal is to understand systems deeply enough that useful changes become visible and defensible.

A valid investigation may end with:

- a correctness, security, data-integrity, or recovery fix;
- a measurable performance or resource improvement;
- a compatibility or interoperability correction;
- a better API or workflow demonstrated in realistic use;
- a meaningful refactor that makes a consequential path safer to change;
- a local feature or integration improvement in one of our own repositories;
- a negative result showing that no change is justified.

## Change thesis

Before promoting work beyond exploration, state:

1. **Current behaviour** — what the code actually does.
2. **Consequence** — what user, operator, dependant, or system property is affected.
3. **Proposed improvement** — what becomes safer, faster, clearer, more compatible, or easier to maintain.
4. **Evidence** — reproduction, test, benchmark, integration trial, source invariant, or failure analysis.
5. **Boundary** — what the evidence does not establish.

A change without a consequence and evidence is not ready.

## Priority order

Prefer work in roughly this order:

1. security, correctness, data loss, corruption, privilege, and trust boundaries;
2. state lifecycle, concurrency, cancellation, retry, recovery, and partial failure;
3. performance, allocation, latency, throughput, and resource exhaustion;
4. compatibility, protocol behaviour, deployment, and cross-component integration;
5. API and workflow ergonomics demonstrated through real use;
6. refactors that materially simplify or protect a consequential path;
7. documentation only when unresolved confusion blocks correct use or hides an important contract.

The order is guidance, not a quota. A small fix can be valuable when its consequence is real and verified.

## Investigation loop

### 1. Map the code

Read the implementation, tests, configuration, generated boundaries, and call sites. Identify:

- entrypoints;
- control and data flow;
- state ownership;
- side effects;
- failure and cleanup paths;
- public contracts;
- existing invariants;
- test blind spots.

Recent issues and pull requests can provide context, but they do not replace source understanding.

### 2. State the plain-language model

Explain what the component is, where it sits, what it is responsible for, and what could go wrong. Follow `PLAIN_LANGUAGE.md`.

### 3. Create competing hypotheses

Do not jump directly from suspicious code to a patch. State what behaviour would distinguish the likely explanations.

### 4. Reproduce or model

Use the smallest test that preserves the important property. This may be:

- an existing upstream test harness;
- a fork-free Fieldwork playground;
- a reduced fixture;
- a benchmark;
- a fault-injection or lifecycle model;
- a controlled integration trial in an owned repository.

### 5. Test realistic use when useful

For SDKs, libraries, runtimes, build tools, observability systems, and developer tools, isolated tests often miss ergonomics and cross-component behaviour. Use `TESTBEDS.md` to try the path in one of our repositories when that adds meaningful evidence.

### 6. Decide whether change is justified

Choose among continue research, keep a local improvement, publish a finding, prepare a human-facing upstream proposal, or stop.

## Meaningful refactors

A refactor is useful when it does at least one of the following:

- removes duplicated state machines or competing sources of truth;
- makes an important invariant explicit and testable;
- isolates a security, concurrency, recovery, or compatibility boundary;
- enables a demonstrated fix that would otherwise be unsafe;
- reduces measurable complexity or resource cost on a consequential path;
- makes realistic integration materially easier without hiding behaviour.

Renaming, reformatting, file movement, abstraction for its own sake, and speculative generalization are insufficient.

## Low-priority work

Do not actively search for:

- spelling and wording changes;
- style-only cleanup;
- additional lint rules with no demonstrated defect;
- generic test-count increases;
- dead-code claims without proving reachability and consequence;
- speculative micro-optimizations without measurement;
- documentation changes detached from an observed usability or correctness problem.

Such work may accompany a substantive change when it directly supports review or correct use.

## Honest stopping

Deep reading does not guarantee a patch. Record negative results, expected behaviour, already-covered cases, and ideas that fail under realistic use. Fieldwork is allowed to conclude that the code is sound or that a change would not justify its review cost.

## Upstream boundary

Third-party upstream repositories are read-only to Fieldwork agents and automated workers by default. Reading, modeling, testing, source inspection, and packet preparation are allowed. A bounded human greenlight may authorize one clearly scoped interaction under `AGENTS.md`; otherwise stop at preparation.
