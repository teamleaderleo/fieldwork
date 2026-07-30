# Integration Profile

Kernel: [`KERNEL.md`](../KERNEL.md)

## Use this profile when

The assignment composes several accepted findings, source candidates, repositories, packages, or lifecycle repairs into one current system state.

## Integration ownership

- Keep one current integration writer for the composed branch or shared integration record.
- Component owners and reviewers may continue contributing through separate branches and evidence paths.
- Integration ownership does not grant acceptance, merge, release, or upstream authority.

## Procedure

1. List every component source head, accepted receipt, unresolved review disposition, and current base relationship.
2. Identify shared state owners, call paths, cleanup paths, authority boundaries, retries, persistence, ordering, and failure settlement.
3. Detect overlapping diffs and semantically adjacent changes even when files are disjoint.
4. State the composed invariant and the failure modes independent green tests cannot exclude.
5. Build one reproducible composition from exact source heads.
6. Run the smallest controls that distinguish composition behavior from component behavior.
7. Preserve compatibility, negative, interruption, retry, cleanup, and rollback controls relevant to the shared boundary.
8. Classify failures by component, composition, harness, environment, or stale premise.
9. Re-run after source cleanup, restacking, or carrier removal.
10. Update the canonical finding and generated review or delivery view with the exact composed head and remaining boundary.

## Promotion boundary

Independently green patches are not composed-state evidence when they share:

- state ownership;
- lifecycle or cleanup;
- persistence or retry semantics;
- authority or capability selection;
- protocol generation or publication;
- filesystem or output destination;
- ordering or cancellation behavior.

A composed candidate must name which interactions it exercises and which remain outside the gate.

## Outputs

Record:

- component and composed heads;
- integration writer lease;
- exact construction method;
- changed-file fence;
- component receipts and composed receipts;
- conflicts and resolution;
- rollback boundary;
- one next transition or retained stop.
