# Plain-Language Check

## In simple words

Every durable Fieldwork record should prove that its author understands the subject well enough to explain it without hiding behind source paths, jargon, or a wall of detail.

Plain language does not mean prose-only and does not mean writing for a non-technical audience. Code, pseudocode, state diagrams, traces, equations, and compact tables are often the clearest plain language available for a computing concept.

## Lead with the proposal or question

When a record recommends a change, begin with a sentence shaped like:

> I propose changing X so that Y remains true when Z happens.

When the work is still investigative, begin with the concrete question:

> Does X publish stale state after Y transfers authority to Z?

Do not make the reader reconstruct the actual proposal from a long history section.

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

Bullet lists are optional. Do not use them by reflex. A paragraph, code block, arrow diagram, truth table, before/after diff, or small sequence trace may communicate the model better.

## Required understanding

Near the top of a target hub, finding, campaign, lane report, retained experiment, integration context, synthesis, issue draft, or pull-request draft, make these answers easy to recover:

```text
What is being proposed or tested?
Where does it sit in the system?
What happens now?
What should happen instead?
Why does the difference matter?
What remains uncertain or blocked?
```

The answers may be expressed as prose, code, diagrams, or a mixture. The format should match the subject.

## Purpose

This is an understanding test, not an executive summary and not marketing. It should let a technically literate reader decide whether to continue into the detailed evidence.

## Rules

Explain the current model before implementation detail. Prefer concrete nouns and verbs over broad claims such as “improves robustness.” Separate established behaviour from suspicion. State when a consequence is illustrative rather than documented. Do not claim that a small reproduction models an entire production system. Update the explanation when the underlying conclusion changes. Keep caveats near the claim they qualify.

Do not over-explain an obvious control-flow repair after the invariant is visible. Once code or a diagram makes the mechanism clear, spend prose on the non-obvious judgment: compatibility, ownership, policy, risk, or alternatives.

## Examples

Weak:

> This module handles complex asynchronous state and may have edge cases.

Stronger:

> I am testing whether reconnecting after a partial provider event appends the same tool arguments twice.
>
> ```text
> partial event ──disconnect──▶ reconnect ──replay──▶ duplicate append?
> ```
>
> Duplicate arguments could invoke a tool with input different from the model output. The local reproduction is incomplete; the next step is tracing the reconnect path in a real agent session.

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
> The change is worthwhile only if one implementation can preserve the intended cases and make the difference explicit in tests.

## Synthesis check

Before closing work, confirm that a new reader can recover the system, established result, consequence, remaining uncertainty, and next transition without reconstructing the entire investigation.