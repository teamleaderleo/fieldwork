# Coordination Profile

Kernel: [`KERNEL.md`](../KERNEL.md)

## Use this profile when

The assignment coordinates parallel workers, initiatives, batches, shared findings, cross-repository dependencies, handoffs, or synthesis.

## Open problem space, single mutable writer

- Problem ownership is non-exclusive.
- Any worker may inspect, review, reproduce, or contribute evidence through a unique path.
- One mutable branch, shared status file, manifest, canonical finding edit, or other shared artifact has one active writer lease.
- A lease records current mutation responsibility. It is not permanent ownership, competence, or authority.
- Transfer, release, staleness, or supersession must be durable.
- Takeover preserves existing evidence and records why the lease changed.

## Durable surfaces

Use distinct surfaces for distinct jobs:

- canonical finding — current technical interpretation and selected direction;
- unique evidence files — parallel-safe source maps, experiments, comparisons, and receipts;
- implementation PR — exact source diff and checks;
- owning issue — live assignment, authority, and routing events;
- generated read models — current review, delivery, execution, risk, and archive views;
- chat — temporary interaction only.

Do not make one issue thread carry every layer.

## Material event rule

Post to a global initiative only when one of these changes materially:

- phase;
- canonical path;
- source head or reviewed-input generation;
- active carrier or carrier purpose;
- evidence level or exact receipt;
- selected direction;
- blocker or dependency;
- writer lease;
- authority;
- retirement, supersession, or closeout.

Do not post routine instruction intake, unchanged safety confirmations, repeated summaries, or every low-level workflow phase globally.

## Parallel work

Split by independently answerable question, evidence type, target boundary, platform, or implementation alternative. Do not split arbitrary file ranges when every worker must reconstruct the same context.

When work overlaps:

1. stop competing edits to the same mutable artifact;
2. retain both evidence sets;
3. identify the narrower artifact and question boundaries;
4. select one current integration writer;
5. reconcile the canonical finding explicitly;
6. preserve losing conclusions and reopening triggers.

## Cross-assignment effects

When evidence changes another assignment's premise, update both owning records with a compact pointer. Do not assume the other worker will read the global initiative or chat.

## Synthesis

Synthesis distinguishes:

- established findings;
- plausible but unconfirmed interpretations;
- contradictions;
- missing evidence;
- selected and rejected alternatives;
- campaign candidates;
- genuinely non-delegable decisions.

Synthesis never upgrades evidence or hides disagreement.

## Human attention

Default user-facing output should contain only:

- priority;
- material changes;
- why they matter;
- waiting or blocked work;
- risks;
- exact questions requiring human authority;
- next autonomous action.

Everything else remains linked one layer down.
