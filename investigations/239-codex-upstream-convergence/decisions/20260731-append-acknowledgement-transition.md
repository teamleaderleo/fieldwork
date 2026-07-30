# Decision: route Codex append acknowledgement to a direct-current-head delivery gate

Question: Has the append acknowledgement packet become independently actionable?  
Governing invariant: live conversation insertion and durable rollout append are separate facts, and later recovery must receive the canonical append acknowledgement.  
Selected direction: `delivery-gate-ready` direct-current-head materialization.  
Exact selected implementation: `teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`.  
Current public source inspected: `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`.  
Upstream contact authorized: `no`.

## In simple words

The portfolio comparison has done enough to select one append-acknowledgement implementation. The exact source, tests, current-public relation, and independent review all agree. Remaining work is a bounded restack and renewed review, so this packet leaves the undifferentiated meta-analysis queue and enters Delivery Desk D2.

The later typed persistence model stays separate. The append source returns a prerequisite fact; it does not decide retry, replay, compaction, or remote-effect certainty.

## Criteria

1. one bounded invariant and one source owner;
2. source-only exact diff;
3. exact target-native controls;
4. complete current-public relation;
5. independent complete-diff review;
6. explicit exclusions and successor gate;
7. reversible delivery step.

## Evidence

- source PR `teamleaderleo/codex#84`, head `d8299b7f...`;
- exact three-file fence;
- carrier `teamleaderleo/codex#80`, head `401c2e5...`;
- workflow `30583967538`, four exact controls and complete thread-store package passed;
- independent review `4823945751`, bounded prerequisite accepted;
- complete compare through `413492...`, zero source-fence overlap.

## Alternatives

- Keep the packet under general comparative evaluation: rejected because one implementation and one next gate now lead clearly.
- Expand immediately into typed persistence and replay: deferred because those paths have different owners and open repair work.
- Treat file-disjoint ancestry as final proposal packaging: declined in favor of a direct-current-head child with one exact review base.

## Decision

Move the append acknowledgement finding to `delivery-gate-ready` and route it to Delivery Desk #160 D2.

Clearing action:

1. create a direct child of `413492...` with the exact three-file source;
2. run the four exact controls and complete thread-store package;
3. receive fresh independent complete-diff review;
4. transfer receipts and retire old source/carrier lineage.

Reopening trigger: relevant public source drift, changed append contract, failed direct-head execution, or an upstream typed outcome that absorbs the prerequisite.

Non-delegable human decision: none.
