# Current Fieldwork Publication Pass

Snapshot date: 2026-07-30

This page answers one question: **what can move toward publication or landing now, and what still needs another pass?**

Live coordination remains in [issue #213](https://github.com/teamleaderleo/fieldwork/issues/213) and the [Delivery Desk, issue #160](https://github.com/teamleaderleo/fieldwork/issues/160). This file is the readable repository snapshot. Refresh it whenever a candidate head, execution result, or disposition changes.

## Closest to landing

### 1. Playground validator primitive strictness — PR #238 / issue #237

Current source-and-test head: `3151710ad9eae2e004bc62da0805990aafe9ad2c`.

The branch now validates pack defaults and case overrides independently, contains bounded huge-integer handling, covers boolean-versus-number JSON comparison, and has removed its temporary repair workflow.

Remaining gate:

- complete Playground/context and Fieldwork integrity runs on the exact head;
- perform one fresh exact-head diff review;
- mark ready and merge when both pass.

### 2. Receipt boolean schema-version repair — PR #231

Current finalizer head: `7564622af0c75899b5e84fb55d7718949d4fa119`.

The intended durable change is two files: the receipt classifier and its focused tests. The branch finalizer applies exact primitive-integer checks for document and receipt schema versions, verifies semantic output, removes itself, and publishes the source-only result.

Remaining gate:

- obtain the source-only head;
- confirm the workflow file is gone;
- run focused and repository integrity checks;
- review and merge the two-file diff.

### 3. Workerd receiver-aware generated types — PR #232 / issue #230

The repaired candidate has a bounded lexical-heritage resolution rule and regression coverage. Exact focused and ordinary target receipts still own the decision.

Remaining gate:

- focused generator tests;
- repository tests, lint, coverage, and complete-diff review;
- removal of fork-only workflow material before any proposal packet.

### 4. OpenTelemetry provider shutdown and delayed reentry — issue #194

The provider candidate, delayed-reentry stack, and pre-existing-span experiment now form one coherent lifecycle question.

Remaining gate:

- settle the provider matrix;
- restack delayed reentry linearly;
- decide attempt-all processor fanout and pre-existing-span completion before delivery.

## Implementation underway

### HTTPX async response close ownership — issue #171 / PR #173

The generic public-stream contract is selected: delegated cleanup failure becomes a shared terminal outcome whose arbitrary custom stream runs once. The owned direct candidate lives in `teamleaderleo/httpx#4` and still needs its source-only finalization and target execution.

### Zustand explicit hydration settlement — issue #158 / PR #159

The observer matrix distinguishes hydration-source failure from callback and listener failure. The direct rejection patch remains held until the finalized tests pass ordinary repository gates and the terminal ownership rule is explicit.

### Jotai JSON storage key isolation — issue #235 / PR #236

Released cross-key object aliasing is reproduced. The candidate scopes parsed-object identity by storage key. Execution and the dynamic-key cache-retention decision remain.

### Supabase refresh notification ownership — issue #148 / PR #91

Generation-five evidence handles distinct-token overlap. Same-token distinct-result ownership, session invalidation, and executed SSR evidence still need repair and classification.

### Codex current-upstream convergence — issue #239

Four bounded source candidates remain active. Exact-name/count receipts, the boxed-future discriminator, append-outcome prerequisite, and upstream drift reconciliation control proposal readiness.

## Durable research packets already in good condition

These results already carry useful evidence and can be cited, synthesized, or turned into editorial material:

- broad-spectrum ecosystem round 001 and its ranked candidate queue;
- Wasmtime interruption and host-effect ownership;
- Tantivy mixed-generation `prepare_commit` finding;
- OpenTelemetry delayed lifecycle reentry model;
- Jotai released cross-key identity reproduction;
- Zustand undefined-option preservation closeout;
- Codex MCP timeout outcome model.

Their next steps are synthesis, a separate production candidate, or deliberate proposal preparation. Their research result itself is durable.

## Work that needs more passes

- DataFusion/Polars publication cancellation: bind executed package bytes to inspected source, commit a lockfile, use locked installation, then execute the real cancellation barriers.
- wgpu portability and GPU lifecycle: requires browser/native environment coverage before a narrow candidate can be ranked.
- Tantivy production repair: create a separate candidate that joins old workers, owns cleanup, retires or rebuilds the writer after failure, and preserves the initiating error.
- Gemini confirmation call affinity: complete the exact-call snapshot and adjacent state-manager fixtures.
- Linux and privileged systems probes: continue in `teamleaderleo/linux-fieldwork` with VM or environment receipts.

## Editorial and podcast inventory

The indexed Fieldwork tree currently contains no podcast draft, transcript, episode outline, or audio-production packet. The strongest editorial source material is the durable research list above. A podcast lane should begin by selecting one result, writing a listener-facing thesis, and separating confirmed behavior from proposed repairs.

## Maintenance rule

Keep this page short enough to scan. Preserve detailed evidence in canonical issues, PRs, reports, and receipts. Move completed items into the durable-results section, move clean direct candidates to the top, and record the exact remaining gate in one sentence.
