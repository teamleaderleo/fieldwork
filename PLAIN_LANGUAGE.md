# Plain-Language Check

## In simple words

Every durable Fieldwork record should prove that its author understands the subject well enough to explain it without hiding behind source paths, jargon, or a wall of detail.

Plain language doesn't mean prose-only, and it doesn't mean writing for a non-technical audience. Code, pseudocode, state diagrams, traces, equations, and compact tables are often the clearest plain language available for a computing concept.

`## In simple words` is a useful default entry point because readers recognize it across the repository. A clearer audience-specific heading, proposal sentence, question, diagram, or table can serve the same purpose. Use the exact heading when a validator or assignment depends on it; elsewhere optimize for comprehension.

## Lead with the proposal or question

When a record recommends a change, begin with a sentence shaped like:

> I propose changing X so that Y will remain true when Z happens.

When the work is still investigative, begin with the concrete question:

> Does X still publish stale state after Y transfers authority to Z?

Don't make the reader reconstruct the actual proposal from a long history section.

## Voice and tense

Write like a technically literate person talking to another technically literate person. Contractions are welcome: use “doesn't,” “won't,” “we'll,” and “it's” when they're the natural phrasing. Don't expand them merely to sound formal.

Preserve the author's voice while improving accuracy, clarity, and consequence. A house style should help readers navigate; it should never flatten every report into the same rhythm.

Use tense to keep the timeline clear:

```text
current behaviour   → present tense
proposed effect     → future tense
completed evidence  → past tense
remaining work      → future tense
```

For example:

> Vite currently stops after the first `buildEnd` failure. This change will let the remaining teardown hooks settle before `close()` reports failure. The focused regression passed on the accepted head. We'll replay the patch on current `main` before any public submission.

Don't force every sentence into one tense. Use the tense that tells the reader whether something happens now, will happen after the proposal, already happened in verification, or still needs to happen.

## Avoid template voice

Headings are navigation, not a script for how every thought should sound. A record can contain every expected section and still read like a form somebody filled in.

Prefer the sentence that says the thing over a stock announcement such as “The key insight is,” “This matters because,” “There are three reasons,” or “The following section explains.” Use an explicit signpost when the reader genuinely needs orientation; otherwise begin with the mechanism, consequence, question, or decision.

Don't manufacture symmetry. If there are two relevant cases, write two. If there are five, write five. A diagram followed by one sentence may be complete. A result that has landed doesn't need a recap paragraph merely because the template has reached its end.

Let technical prose keep some human cadence. Contractions, semicolons, short reactions, and an occasional longer sentence are fine when they make the explanation easier to follow. Accuracy comes from exact nouns, verbs, identities, evidence, and boundaries—not from sounding ceremonial.

During revision, protect the passage that already works. Fix the vague noun, canned transition, duplicated caveat, or padded ending instead of rewriting the whole record into a new house voice.

## Choose the clearest representation

Use prose for motivation, uncertainty, tradeoffs, and consequences. Use code-shaped notation for control flow, state transitions, data shape, and invariants.

For example:

```ts
// Current
await buildEnd()      // rejects
await closeBundle()   // never reached

// Proposed
const errors = [
  ...await settleAll(buildEndHooks),
  ...await settleAll(closeBundleHooks),
]
throwIfAny(errors)
```

Or:

```text
old authority ──replaced──▶ new authority
      │
      └── late completion must not publish
```

Prefer one compact representation over several paragraphs that merely narrate the same mechanics.

Bullet lists are optional. Don't use them by reflex. A paragraph, code block, arrow diagram, truth table, before/after diff, or small sequence trace may communicate the model better.

## Required understanding

Near the top of a target hub, finding, campaign, lane report, retained experiment, integration context, synthesis, issue draft, or pull-request draft, make these answers easy to recover:

```text
What is being proposed or tested?
Where does it sit in the system?
What happens now?
What will happen instead?
Why does the difference matter?
What remains uncertain or blocked?
```

The answers may be expressed as prose, code, diagrams, or a mixture. The format should match the subject. One compact passage can carry several answers; use separate sections only when they help the reader.

## Purpose

This is an understanding test, not an executive summary and not marketing. It should let a technically literate reader decide whether to continue into the detailed evidence.

## Rules

Explain the current model before implementation detail. Prefer concrete nouns and verbs over broad claims such as “improves robustness.” Separate established behaviour from suspicion. State when a consequence is illustrative rather than documented. Don't claim that a small reproduction models an entire production system. Update the explanation when the underlying conclusion changes. Keep caveats near the claim they qualify.

Don't over-explain an obvious control-flow repair after the invariant is visible. Once code or a diagram makes the mechanism clear, spend prose on the non-obvious judgment: compatibility, ownership, policy, risk, or alternatives.

State stable facts once and link to them from supporting records. Repetition is useful when a record must stand alone; ritual restatement across a packet usually hides the current answer.

## Examples

Weak:

> This module handles complex asynchronous state and may have edge cases.

Stronger:

> I'm testing whether reconnecting after a partial provider event will append the same tool arguments twice.
>
> ```text
> partial event ──disconnect──▶ reconnect ──replay──▶ duplicate append?
> ```
>
> Duplicate arguments could invoke a tool with input different from the model output. The local reproduction is incomplete; next I'll trace the reconnect path in a real agent session.

Weak:

> Refactor the parser for maintainability.

Stronger:

> I propose one recovery function for two parser paths that currently disagree on the same malformed token.
>
> ```text
> malformed token ──path A──▶ recover as X
>                 └─path B──▶ recover as Y
> ```
>
> The change will be worthwhile only if one implementation can preserve the intended cases and make the difference explicit in tests.

## Synthesis check

Before closing work, confirm that a new reader can recover the system, established result, consequence, remaining uncertainty, and next transition without reconstructing the entire investigation.
