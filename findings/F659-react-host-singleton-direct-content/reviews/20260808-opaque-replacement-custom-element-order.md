# Body opaque replacement — custom-element lifecycle ordering constraint

## Question

Can a body opaque-content repair insert the replacement contribution before retiring the previous React-owned contribution, then remove the old nodes afterward?

## Answer

**No. Treat insert-new-then-retire-old as a rejected implementation order.**

This matters for the current disposable client experiment because its non-empty replacement mechanics currently use that order for both opaque -> opaque and managed -> opaque transitions.

## React commit ordering

Owned-fork baseline and current public source both establish the existing ordering for managed -> `dangerouslySetInnerHTML`:

1. HostSingleton mutation effects recursively process child deletions first.
2. HostSingleton reconciliation effects run.
3. `commitHostUpdate` runs afterward.
4. The DOM `dangerouslySetInnerHTML` setter then performs the opaque replacement.

So old managed child nodes are physically gone before new direct-HTML content is installed.

For direct-HTML -> direct-HTML, the browser `innerHTML` setter itself parses a replacement fragment and then runs the DOM replace-all operation on the target.

## Browser lifecycle semantics

The WHATWG HTML Standard defines `element.innerHTML = value` by parsing a fragment and then replacing all target children with that fragment.

Custom-element reactions are wrapped by CE-reaction queues and invoked after the DOM operation's processing, in the order their triggering mutations occurred.

Therefore the current whole-target `innerHTML` operation does not expose a state where a newly connected replacement custom element runs author callback code while the previous target child list is still intentionally retained for a later React cleanup step.

## Why the prototype order differs

The current PR 32 experiment:

- parses replacement HTML in a detached body;
- inserts each new top-level node into the live body before the old contribution / old managed subtree;
- only afterward retires the previous React-owned nodes.

A custom element in the new contribution can receive `connectedCallback` when inserted into the live body and observe old React-owned nodes that current managed -> DSIH ordering would already have deleted.

The same issue exists for direct-HTML -> direct-HTML because the new contribution is connected before the old contribution is removed.

This is externally observable author code, not merely a MutationObserver record-count difference.

## Required repair ordering

A complete design should instead:

1. capture a stable logical insertion slot;
2. retire the previous React-owned contribution/subtree;
3. install the replacement at that captured slot.

For a non-empty previous contribution the slot can potentially be represented by the first surviving outside node after the old contribution.

For an empty previous contribution there may be no physical owned node or right-hand outside sibling, so the already-identified empty-capable position token requirement still applies. A live in-memory DOM Range remains one possible representation to investigate.

## Candidate disposition impact

- PR 32 remains a disposable architecture experiment only.
- A green happy-path PR 32 run would not justify promotion without fixing this lifecycle order.
- The placement-unit concept remains viable; the current insert-before-retire implementation order is rejected.

## Evidence class

- React ordering: source-read, revalidated against current public main `2042572329425f9ebf35ae6287ea5bab72b2c497`.
- DOM/custom-element ordering: standards-read from the WHATWG HTML Standard's dynamic markup insertion and custom-element reactions algorithms.
- No public upstream interaction performed.
