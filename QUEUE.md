# Actual Queue

**Start here when reviewing Fieldwork:** [issue #213 — Actual review queue](https://github.com/teamleaderleo/fieldwork/issues/213)

That issue is the canonical ordered list of work needing human judgment. It states the exact decision, the evidence to inspect, and the disposition that moves each card.

## Current review order

1. [PR #174](https://github.com/teamleaderleo/fieldwork/pull/174) — receipt schema enforcement.
2. [PR #166](https://github.com/teamleaderleo/fieldwork/pull/166) — Wasmtime interruption result.
3. [PR #173](https://github.com/teamleaderleo/fieldwork/pull/173) — HTTPX async response close ownership.
4. [PR #172](https://github.com/teamleaderleo/fieldwork/pull/172) — Zustand undefined option preservation.
5. [PR #159](https://github.com/teamleaderleo/fieldwork/pull/159) — Zustand explicit rehydrate failure settlement.
6. [PR #182](https://github.com/teamleaderleo/fieldwork/pull/182) — Tantivy worker-generation fencing.
7. [PR #163](https://github.com/teamleaderleo/fieldwork/pull/163) — Codex MCP cancellation packet.
8. [PR #91](https://github.com/teamleaderleo/fieldwork/pull/91) — Supabase refresh notification ownership.

The detailed asks live in issue #213. Keep this file compact and update it only when the ordered top-level set changes.

## Other queues

- [Issue #160 — Delivery Desk](https://github.com/teamleaderleo/fieldwork/issues/160): implementation, final gates, clean application, landing, and closeout.
- [Open issues](https://github.com/teamleaderleo/fieldwork/issues): full live workboard.
- [Open pull requests](https://github.com/teamleaderleo/fieldwork/pulls): evidence and implementation surfaces, including broad histories that are outside the immediate review queue.

## Rules

- At most eight items belong in the immediate review list.
- Each item needs one bounded decision.
- Remove disposed work immediately.
- Move implementation chores to the Delivery Desk.
- A changed head or changed evidence input expires the review.
- Broad scouts, execution carriers, and historical PRs stay outside this list.
- This queue grants no upstream-contact authority.
