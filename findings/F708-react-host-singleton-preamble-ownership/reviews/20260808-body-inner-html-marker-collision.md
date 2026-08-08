# Boundary-stream body DSIH — control-comment namespace collision

## Question

Can Fizz repair boundary-contributed body `dangerouslySetInnerHTML` by emitting the raw HTML into the existing Suspense boundary stream immediately after the current `<!--body-->` preamble contribution marker?

## Result

**Reject that implementation as currently defined.**

The idea fixes one ownership problem but introduces a collision between arbitrary raw HTML comments and React's internal boundary-control comment namespace.

## Why the split looked attractive

Current Fizz behavior is asymmetric:

- managed body children stay in the Suspense boundary stream;
- body DSIH bytes are written into `preamble.bodyChunks` and escape into the root preamble.

Moving only the DSIH bytes into the boundary would let existing Suspense deletion own and retire those raw nodes naturally when a fallback boundary is discarded.

React PR 34 implemented exactly that small split as an experiment.

## Collision mechanism

React DOM's `clearHydrationBoundary()` walks the direct sibling nodes inside a Suspense/Activity boundary.

For direct sibling comments, the walker interprets static comment data as control tokens. The namespace includes at least:

### Boundary depth / termination

- `$`
- `$?`
- `$~`
- `$!`
- `&`
- `/$`
- `/&`

These increment/decrement boundary depth or terminate the cleanup when an end marker is observed at depth zero.

### Singleton preamble contributions

- `html`
- `head`
- `body`

These trigger singleton preamble cleanup; `head` additionally triggers `clearHead(head)`.

These comments are safe in the current managed boundary stream because ordinary React rendering does not expose arbitrary author comments as direct sibling control nodes.

`dangerouslySetInnerHTML`, however, is arbitrary HTML and may contain ordinary comments with any of these exact data strings.

If body DSIH is moved directly into the boundary stream, author markup can therefore become indistinguishable from React control comments.

## Singleton cleanup example

Markup such as:

```html
<!--head--><div>content</div>
```

produces a direct sibling comment whose data is exactly `head`.

When the boundary is later cleared, React can misclassify that author comment as an internal preamble contribution marker and clear the real persistent document head even though this boundary never contributed a head.

## Boundary-parser examples

The problem is broader than singleton cleanup.

Raw comments such as:

```html
<!--$-->
<!--&-->
<!--/$-->
<!--/&-->
```

can alter the cleanup walk's nested-boundary depth accounting or satisfy its end-marker condition.

A forged-looking end marker at depth zero can make cleanup return before reaching the real boundary end, leaving later nodes behind and retrying as though the boundary had been fully removed.

A forged-looking start marker can increase depth and make the real end marker look nested, changing how far the scanner walks.

So there is no safe subset where static preamble words are merely renamed: arbitrary raw HTML cannot share this unescaped direct-sibling comment channel with React's boundary protocol.

## Focused falsifier

React PR 34 now carries a regression that:

1. renders a stable head attribute;
2. renders a Suspense fallback body using DSIH containing `<!--head-->`;
3. later client-renders the primary body;
4. requires the stable document-head attribute to survive.

Current source keeps the DSIH bytes outside the boundary and should preserve the head.

The PR 34 stream-split experiment moves that author comment into `clearHydrationBoundary()`'s control namespace and is expected to fail this control.

One representative collision is enough to reject the implementation; additional `$`/`/$` controls can be added if a future design attempts to reuse the same raw sibling channel.

## Design consequence

The useful principle survives: opaque fallback content should ideally have deletion/provenance ownership associated with the boundary.

The specific direct-stream implementation does not.

A future protocol needs one of:

- an internal marker representation that arbitrary author HTML cannot forge;
- a per-boundary unforgeable/random identity with parsing rules that author comments cannot accidentally satisfy;
- a separate opaque-content provenance channel that does not share raw author comment nodes with the boundary scanner;
- another range representation with equivalent cleanup ownership.

Merely changing `<!--body-->` to a longer static string is insufficient: DSIH can contain that string too.

This also strengthens the marker-descriptor requirement that any new comment payload be both HTML-comment-safe **and control-namespace-safe**.

## Disposition

- PR 34: **FALSIFIED / RETAIN AS NEGATIVE EXPERIMENT**.
- Body preamble DSIH ownership: remains open research under #708.
- Do not promote the simple “redirect DSIH bytes to boundary target” patch even if ordinary happy-path tests pass.

## Evidence class

Source-read with target-test-prepared falsifier. No public upstream interaction performed.
