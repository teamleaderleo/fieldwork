# Actual Queue

**Start here when reviewing Fieldwork:** [issue #213 — Actual review queue](https://github.com/teamleaderleo/fieldwork/issues/213)

That issue is the canonical ordered list of work needing human judgment. It states the exact decision, the evidence to inspect, and the disposition that moves each card. The queue grows whenever another bounded decision becomes reviewable; priority controls order, not inclusion.

## Current review order

1. [PR #174](https://github.com/teamleaderleo/fieldwork/pull/174) — receipt schema enforcement.
2. [PR #166](https://github.com/teamleaderleo/fieldwork/pull/166) — Wasmtime interruption result.
3. [PR #173](https://github.com/teamleaderleo/fieldwork/pull/173) — HTTPX async response close ownership.
4. [PR #172](https://github.com/teamleaderleo/fieldwork/pull/172) — Zustand undefined option preservation.
5. [PR #159](https://github.com/teamleaderleo/fieldwork/pull/159) — Zustand explicit rehydrate failure settlement.
6. [PR #182](https://github.com/teamleaderleo/fieldwork/pull/182) — Tantivy worker-generation fencing.
7. [PR #163](https://github.com/teamleaderleo/fieldwork/pull/163) — Codex MCP cancellation packet.
8. [PR #91](https://github.com/teamleaderleo/fieldwork/pull/91) — Supabase refresh notification ownership.

The detailed asks live in issue #213. Keep this file readable, preserve the complete ordered set, and update it when a card enters, moves, is disposed, or returns for re-examination.

## Other queues

- [Issue #160 — Delivery Desk](https://github.com/teamleaderleo/fieldwork/issues/160): implementation, final gates, clean application, landing, and closeout.
- [Open issues](https://github.com/teamleaderleo/fieldwork/issues): full live workboard.
- [Open pull requests](https://github.com/teamleaderleo/fieldwork/pulls): evidence and implementation surfaces, including broad histories that are outside the immediate review queue.

## Rules

- Include every bounded decision that is ready for human judgment; do not hide lower-priority cards to keep the list short.
- Use ordering and headings to manage a large pile rather than deleting valid review debt.
- Each item needs one clear decision and named evidence.
- Remove disposed work after the decision and next action are durable.
- Move implementation chores to the Delivery Desk without erasing their review history.
- A changed head or changed evidence input expires the review.
- Re-open or add a re-examination card when later source movement, execution evidence, or adjacent findings weaken an earlier disposition.
- Broad scouts, execution carriers, and historical PRs stay outside this list unless they present a current bounded decision.
- This queue grants no upstream-contact authority.