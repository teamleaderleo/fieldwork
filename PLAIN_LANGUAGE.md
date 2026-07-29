# Plain-Language Check

## In simple words

Every durable Fieldwork record should prove that its author understands the subject well enough to explain it without hiding behind source paths, jargon, or a wall of detail.

## Required block

Near the top of a target hub, finding, campaign, lane report, retained experiment, integration context, or synthesis, include:

```text
## In simple words

- What is this?
- Where does it sit in the larger system?
- What is wrong, uncertain, or being tested?
- Why could anyone care?
- What is the current answer or next step?
```

Use direct language. Five short bullets or one compact paragraph is usually enough.

## Purpose

The block is an understanding test, not an executive summary and not marketing. It should help a reader decide whether to continue into the detailed evidence.

A good explanation names:

- the component or workflow;
- its responsibility;
- the important boundary or failure;
- the consequence;
- the current research state.

## Rules

- Explain the current model before listing implementation details.
- Prefer concrete nouns and verbs over broad claims such as “improves robustness.”
- Separate established behaviour from suspicion.
- State when the consequence is illustrative rather than documented.
- Do not claim that a small reproduction models an entire production system.
- Update the block when the underlying conclusion changes.
- Keep important caveats in the block when omitting them would mislead.

## Examples

Weak:

> This module handles complex asynchronous state and may have edge cases.

Stronger:

> This module turns streamed provider events into one tool-call result. We are testing whether reconnecting after a partial event can append the same arguments twice. Duplicate arguments could invoke a tool with different input than the model produced. The local reproduction is incomplete; the next step is tracing the reconnect path and running it in a real agent session.

Weak:

> Refactor the parser for maintainability.

Stronger:

> Two parser paths recover from the same malformed token differently. The duplication makes fixes easy to apply to only one path. We are testing whether one shared recovery function can preserve both behaviours and make the invariant testable.

## Synthesis check

Before closing work, ask whether a new reader can answer:

1. What system did we study?
2. What did we actually establish?
3. Why might the result be useful?
4. What remains unknown?
5. What happens next?

If those answers require reconstructing the entire investigation, the plain-language block is not finished.