# Proposal Packets and Upstream Handoffs

## In simple words

A deep investigation may uncover several real problems that belong to different packages or maintainers. Do not turn that into one enormous issue or pull request. Split the work into reviewable proposals, make every proposal understandable on its own, and keep one optional Fieldwork synthesis link for readers who want the full investigation.

## Purpose

Fieldwork proposal packets translate durable evidence into possible upstream work without creating premature upstream contact. A packet can contain issue drafts, pull-request drafts, design questions, reproductions, cross-language precedent, negative results, and a recommended submission order.

A packet is still quiet research until the exact upstream interaction is explicitly authorized.

## When to create a proposal packet

Create or promote a packet when the evidence establishes:

1. a concrete current behaviour;
2. a demonstrated consequence or violated contract;
3. the likely owning package or abstraction layer;
4. a minimal reproduction or source invariant;
5. a bounded proposed direction;
6. meaningful alternatives and compatibility risks;
7. a clear statement of what remains unknown.

Do not create a proposal merely because suspicious code or an old issue exists.

## Split by review unit

Prefer separate proposals when findings differ in any of these ways:

- owning package or maintainer group;
- public contract being changed;
- compatibility risk;
- test harness or reproduction;
- implementation layer;
- need for design agreement before code;
- ability to land independently.

Typical decomposition:

1. small evidenced correctness fix;
2. separate failure-path cleanup;
3. lower-level provider or runtime contract issue;
4. lower-level resource or transactionality issue;
5. umbrella design discussion for ownership, replacement, restart, or disposal.

Do not hide several independent defects inside one mega-issue or mega-PR merely because one scout discovered them together.

## Every upstream issue must stand alone

A proposed issue should include enough information for a maintainer who never opens Fieldwork:

- plain-language summary;
- affected package and pinned revision;
- minimal reproduction;
- expected and actual behaviour;
- consequence;
- likely owning boundary;
- proposed behaviour or decision questions;
- alternatives considered;
- compatibility and scope boundaries;
- validation plan;
- uncertainty and negative results.

A source-backed claim should point to the smallest relevant source location. A reproduced claim should point to the retained test or output.

## Historical and cross-language references

Use historical issues, pull requests, specifications, and other language SDKs as supporting context—not as substitutes for reproducing the target behaviour.

Good uses include:

- showing that users repeatedly encounter a lifecycle or integration pattern;
- identifying earlier design decisions;
- showing how another implementation made an explicit contract choice;
- finding tests, terminology, or compatibility concerns;
- distinguishing a target-specific defect from a broader ecosystem pressure.

Do not claim that another language has the same bug without reproducing or reading its implementation. State whether a reference is precedent, analogous pressure, contrary evidence, or an exact match.

All quiet external GitHub references must follow `REFERENCE_POLICY.md`.

## Deep-dive links

A future upstream issue may include one optional link to a Fieldwork synthesis when that materially helps reviewers.

The link must be described as supplemental evidence. The upstream report must remain independently understandable without it.

Prefer linking the synthesis or proposal index rather than scattering links to every probe, branch, and note. The synthesis should then link to exact reproductions, source maps, decision records, and fork trials.

A direct backlink-producing upstream interaction still requires explicit authorization. Preparing the link in a draft does not authorize posting it.

## Top-level visibility inside Fieldwork

When a scout produces substantial proposal candidates:

1. retain a proposal index beside the scout report;
2. link it from the target map;
3. update the target hub issue with the current candidate set;
4. link the target hub from the programme hub or programme progress thread;
5. add a compact entry to the root README only when the work is active and consequential enough to deserve repository-wide visibility;
6. keep detailed evidence in the owned report and artifacts rather than expanding hub issues indefinitely.

Use the existing target or programme thread when one already exists. Do not create a duplicate top-level issue solely for visibility.

## Candidate ordering

Order proposals so that small, well-evidenced changes can land before broad design work:

1. independently safe fixes;
2. cleanup of concrete failure paths;
3. lower-level contract corrections;
4. transactionality or ownership infrastructure;
5. broad replacement, restart, or disposal design.

The ordering should explain dependencies. It should also state which proposals must not be combined.

## Fork trials

A user-owned fork may hold isolated draft pull requests before upstream contact. Keep characterization and fixes separate when that improves falsifiability:

- characterization branch: preserves and demonstrates current behaviour;
- narrow fix branch: changes one contract or failure path;
- broader design branch: only after the contract is agreed.

Do not claim tests passed unless they ran successfully. Record missing dependencies, absent CI, and source-only review honestly.

## After authorization and submission

After an authorized upstream interaction:

- record the exact issue or pull request in the proposal index;
- mark the interaction as intentional under `REFERENCE_POLICY.md`;
- update the target hub and relevant programme thread;
- preserve upstream feedback and changed assumptions;
- revise or close sibling proposals when the upstream decision affects them;
- keep the Fieldwork synthesis as the durable research record rather than copying the full upstream conversation.

## Stop conditions

Stop or retain a finding without submission when:

- the behaviour is documented and coherent;
- the consequence is application-specific;
- another active upstream proposal already covers the same bounded problem;
- the proposed cleanup cannot establish ownership safely;
- cross-language precedent conflicts and the target contract remains unspecified;
- the review burden would exceed the demonstrated benefit;
- the evidence cannot distinguish library behaviour from misuse or runtime behaviour.

## Contact boundary

Proposal packets, fork trials, issue drafts, and cross-language research do not authorize upstream contact. No external issue, pull request, comment, review, reaction, or direct backlink may be created without explicit authority for that exact interaction.