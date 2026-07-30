# Fieldwork Task Profiles

Status: draft implementation for #301  
Kernel: [`KERNEL.md`](../KERNEL.md)

## In simple words

The kernel contains rules every worker must follow. A dispatch packet names only the profiles needed for the current assignment.

## Resolution order

1. current explicit user authority and safety boundaries;
2. `KERNEL.md`;
3. assignment dispatch packet;
4. named profiles in this directory;
5. target-specific instructions;
6. canonical finding, owning issue, implementation PR, and exact receipts;
7. optional background manuals and historical records.

A lower layer may add detail. It may not weaken a higher-layer authority, privacy, evidence, or safety rule.

## Available profiles

- [`research.md`](research.md) — source-first investigation, experiments, prior art, and bounded findings;
- [`execute.md`](execute.md) — target-native execution, carriers, exact receipts, and failure classification;
- [`review.md`](review.md) — complete-diff review, evidence scope, freshness, and dispositions;
- [`coordinate.md`](coordinate.md) — parallel work, writer leases, canonical findings, material events, and handoffs;
- [`integrate.md`](integrate.md) — composed-state construction and validation across accepted components;
- [`upstream.md`](upstream.md) — quiet external research and the explicit interaction boundary.

A packet may name several profiles. For example, a worker repairing and validating a source candidate may use `[research, execute, review]`.

## Profile discipline

- Do not load every profile by default.
- Do not copy a profile into an initiative issue and create a second normative version.
- A target may add stricter build, test, disclosure, or safety rules.
- When a recurring rule does not fit any profile, route it to #301 instead of scattering another copy.
- Material contradictions must be recorded; instruction intake itself is not a progress milestone.
