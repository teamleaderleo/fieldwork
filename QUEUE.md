# Review and delivery entry points

## In simple words

You should have one place to look when Fieldwork needs something from you: [Human Review Desk #387](https://github.com/teamleaderleo/fieldwork/issues/387).

Pin or bookmark that issue. Assistants should service finished, current decision cards onto it and remove them after disposition. You should not need to search programme hubs, target issues, execution carriers, packet pull requests, workflow logs, or old issue comments to discover what needs your attention.

Everything else stays in the assistant-facing technical review and delivery desks until it is genuinely ready.

## The three-desk system

### 1. Human Review Desk — #387

[Issue #387](https://github.com/teamleaderleo/fieldwork/issues/387) is the canonical user-facing desk.

A card belongs there only when it contains:

- one exact current source or proposal;
- the behavior or authority decision in plain language;
- the strongest completed evidence and material limits;
- an assistant recommendation;
- one concise reply that records the user's decision.

Routine technical alternatives, queued CI, source restacks, stale-head repair, carrier cleanup, and independent-review plumbing do not belong on the human desk.

A decision on #387 does not silently authorize merge, release, deployment, spending, credentials, private-data access, or public upstream contact. Those authorities remain explicit.

### 2. Peer Review Queue — #213

[Issue #213](https://github.com/teamleaderleo/fieldwork/issues/213) is the assistant and eligible-peer technical review queue.

An item enters only after its exact head, complete fence, governing inputs, completed tests and receipts, classified failures, review lens, author eligibility, clearing transition, and public-contact state are current.

A successful technical review may:

- return the item to #160 for final execution or closeout;
- move a genuinely non-delegable decision to #387;
- stop, repair, reject, or supersede the item without involving the user.

### 3. Internal Delivery Desk — #160

[Issue #160](https://github.com/teamleaderleo/fieldwork/issues/160) is the assistant-owned repair, execution, composition, landing-preparation, and closeout desk.

It owns work such as:

- exact-head tests and ordinary gates;
- clean direct-source publication;
- current-main reconciliation;
- receipt transfer and carrier retirement;
- bounded source or packet polish;
- synchronization of issues, pull requests, findings, and review records.

## Default flow

```text
#160 assistant servicing
  -> #213 eligible technical review
  -> #160 final technical cleanup when needed
  -> #387 only for a real user decision
  -> #160 authorized execution, filing preparation, or closeout
```

Some work stops or closes before reaching #387. A technically accepted candidate does not become a user task merely because it is review-ready.

## User rule

Pin or bookmark **#387 only**.

- When #387 has cards, those are the current decisions worth your attention.
- When #387 is empty, no current Fieldwork decision is being asked of you.
- The issue body should remain short enough to scan on a phone.
- Each card should offer one direct reply rather than asking you to reconstruct project history.

## Agent servicing rule

Before changing a desk:

1. update the canonical issue, source pull request, packet, finding, and receipts first;
2. refresh the live desk body immediately before editing it;
3. make the smallest exact synchronization change and preserve other workers' current cards;
4. remove stale, superseded, queued, red, or already disposed entries from the wrong desk;
5. never duplicate full evidence when a concise card and exact links are enough;
6. keep public-interaction authority separate from technical readiness.

Repository files explain the routing contract. The three GitHub issues hold current live state; this file must not become another copied card list.

## Other work surfaces

- [P0 upstream packet backlog #435](https://github.com/teamleaderleo/fieldwork/issues/435) — unit inventory and convergence work.
- [Open Fieldwork issues](https://github.com/teamleaderleo/fieldwork/issues) — complete live workboard.
- [Open pull requests](https://github.com/teamleaderleo/fieldwork/pulls) — implementation, evidence, packet, and coordination surfaces.

No desk, queue, packet, label, or repository document grants public upstream-contact authority by itself.
