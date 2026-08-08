# Boundary-stream body DSIH — preamble marker collision

## Question

Can Fizz repair boundary-contributed body `dangerouslySetInnerHTML` by emitting the raw HTML into the existing Suspense boundary stream immediately after the current `<!--body-->` preamble contribution marker?

## Result

**Reject that implementation as currently defined.**

The idea fixes one ownership problem but introduces a control-marker collision with arbitrary raw HTML.

## Why the split looked attractive

Current Fizz behavior is asymmetric:

- managed body children stay in the Suspense boundary stream;
- body DSIH bytes are written into `preamble.bodyChunks` and escape into the root preamble.

Moving only the DSIH bytes into the boundary would let existing Suspense deletion own and retire those raw nodes naturally when a fallback boundary is discarded.

React PR 34 implemented exactly that small split as an experiment.

## Collision mechanism

React DOM's `clearHydrationBoundary()` walks the direct sibling nodes inside a Suspense/Activity boundary.

For any direct sibling comment, it compares the comment's `.data` to the static singleton contribution tokens:

- `html`
- `head`
- `body`

If one matches, React runs singleton preamble cleanup. For `head`, it additionally calls `clearHead(head)`.

These marker comments are currently safe because normal React-managed boundary output does not expose arbitrary author comments in that sibling stream.

`dangerouslySetInnerHTML`, however, is arbitrary HTML and may contain ordinary comments. If raw body DSIH is moved into the boundary stream, markup such as:

```html
<!--head--><div>content</div>
```

produces a direct sibling comment whose data is exactly `head`.

When the boundary is later cleared, React can misclassify that author comment as an internal preamble contribution marker and clear the real persistent document head even though this boundary never contributed a head.

The same namespace collision exists for raw comments equal to `html` or `body`.

## Focused falsifier

React PR 34 now carries a regression that:

1. renders a stable head attribute;
2. renders a Suspense fallback body using DSIH containing `<!--head-->`;
3. later client-renders the primary body;
4. requires the stable document-head attribute to survive.

Current source keeps the DSIH bytes outside the boundary and should preserve the head.

The PR 34 stream-split experiment moves the forged-looking comment into `clearHydrationBoundary()`'s marker namespace and is expected to fail this control.

## Design consequence

The useful principle survives: opaque fallback content should ideally live in a deletion/provenance range owned by the boundary.

The specific implementation does not.

A future protocol needs one of:

- an internal marker representation that arbitrary author HTML cannot forge;
- a per-boundary token/identity rather than static bare comment words;
- a separate opaque-content provenance channel that does not share the raw comment namespace;
- another range representation with equivalent cleanup ownership.

This also strengthens the marker-descriptor requirement that any new comment payload be provably collision-safe, not merely escaped enough for HTML syntax.

## Disposition

- PR 34: **FALSIFIED / RETAIN AS NEGATIVE EXPERIMENT**.
- Body preamble DSIH ownership: remains open research under #708.
- Do not promote the simple “redirect DSIH bytes to boundary target” patch even if ordinary happy-path tests pass.

## Evidence class

Source-read with target-test-prepared falsifier. No public upstream interaction performed.
