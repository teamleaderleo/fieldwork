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

> Vite currently skips `closeBundle` when `buildEnd` rejects. This change will pass that error to `closeBundle`, then rethrow it after the hook runs. The focused regression passed on the accepted head. Any broader settle-all change remains separate.

Don't force every sentence into one tense. Use the tense that tells the reader whether something happens now, will happen after the proposal, already happened in verification, or still needs to happen.

## Write for the next decision

Internal evidence and maintainer communication serve different purposes.

The internal record may need exact heads, execution receipts, rejected alternatives, carrier history, current-main analysis, and review state. A maintainer normally needs enough information to decide the next technical question without reconstructing the investigation.

For a public-facing draft, make these easy to recover:

```text
What concrete behaviour is wrong or uncertain?
What project contract or assumption governs it?
What is the smallest proposed change?
What test distinguishes the proposed behavior from the current one?
What important nearby thing is intentionally not changing?
```

Once those answers are clear, stop unless the target's template asks for more. Do not export Fieldwork's internal taxonomy merely because the evidence exists.

## Distinguish project contract from abstract correctness

A language specification, protocol, or general design principle may say one thing while a target project intentionally accepts a narrower assumption for compatibility, performance, historical behavior, or parity with another implementation.

Treat those as different claims.

Before arguing that behavior is a bug, ask:

```text
Is this behavior forbidden by the target's own contract?
Is it an inherited compatibility assumption?
Is the proposal repairing an implementation bug, or asking the project to change policy?
```

If the project intentionally accepts the behavior, the next question may be whether that assumption should change—not whether the implementation failed to follow it.

This matters especially in optimizers, parsers, compatibility layers, runtimes, and protocol adapters. A technically correct observation can still miss the actual maintainer decision if it doesn't identify the project's chosen contract.

## Treat feedback as new evidence

Reviewer or maintainer feedback can change the governing premise. When it does, revise the thesis rather than defending the old framing by inertia.

A useful response shape is:

> You're right about X. I was optimizing for Y, but the existing contract is Z. I've narrowed the change to A; B remains separate.

This is not a ritual apology. It tells the reviewer exactly what premise changed and what the new patch claims.

If disagreement remains, reduce it to one proposition that can be discussed directly:

```text
maintainer assumption: X is intentionally allowed
contributor claim:     case Y falls outside that assumption because Z
next decision:         keep X, narrow Y, or revise the contract?
```

Do not hide an unresolved contract disagreement behind a vague sentence such as “other behavior is unchanged.” Name the disputed boundary.

## Tone in maintainer conversations

Prefer a tone that is calm, specific, collaborative, and technically confident.

- Own mistakes plainly without groveling.
- State established facts without needless hedging.
- Mark real uncertainty explicitly instead of making every sentence tentative.
- Avoid sales language such as “comprehensive,” “robust,” or “production-ready” when a concrete property can be named instead.
- Don't perform expertise. Show it through the reproduction, model, diff, and test.
- Don't narrate every branch rewrite, temporary CI state, or internal coordination step unless it changes the maintainer's decision.
- Avoid all-caps holding messages or stream-of-consciousness corrections in durable public threads. Edit first when possible, then leave one concise correction if the conversation needs a receipt.
- A short “thanks” is fine when natural, but it should not replace a substantive reply when the patch or thesis changed.

The goal is not to sound maximally formal. The goal is to make technical cooperation easy.

## Separate issue and pull-request jobs

A useful issue usually establishes the problem or contract question:

```text
small reproduction
expected or disputed behavior
observable consequence
scope boundary
```

A useful pull request usually establishes the proposed implementation:

```text
smallest change
why that boundary is sufficient
important non-goal
regression or validation
repository-required checklist
```

Do not duplicate the whole issue in the pull request unless the target expects a standalone explanation. Do not make a maintainer infer the bug from the implementation diff either.

Target repository conventions always win. Some projects want three short paragraphs; some want a structured checklist; some want explicit end-to-end verification. Match the local style while preserving the technical invariant.

## Preserve contribution history without self-effacement or inflation

Pull-request mechanics and substantive authorship are separate facts.

A target may squash, cherry-pick, move tests, remove reproduction-only files, use a factory branch, or land a target-managed successor. Those actions do not by themselves prove that the original contribution was independently replaced.

When recording outcomes, prefer evidence-backed language:

- `landed directly` when the contribution itself is merged;
- `landed via target-managed successor, contribution lineage retained` when the successor materially incorporates the submitted work;
- `independently displaced` only when the successor is substantively independent.

Record formal author or co-author metadata plainly when it exists. When only material incorporation can be established, describe the incorporated implementation, tests, reproduction, or design boundary without inventing ownership percentages or sole-authorship claims.

Accuracy includes giving the work its due credit.

## Choose the clearest representation

Use prose for motivation, uncertainty, tradeoffs, and consequences. Use code-shaped notation for control flow, state transitions, data shape, and invariants.

For example:

```ts
// Current
await buildEnd()      // rejects
await closeBundle()   // never reached

// Proposed
let error
try {
  await buildEnd()
} catch (caught) {
  error = caught
}
await closeBundle(error)
if (error) throw error
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

Weak maintainer reply:

> I still think the current behavior is wrong and the tests prove it.

Stronger:

> The reproduction establishes the language-level behavior. Your comment makes the remaining question narrower: whether this optimizer intentionally accepts the inherited compatibility assumption in this case. I'll keep the implementation change out unless we decide that assumption should change.

## Synthesis check

Before closing work, confirm that a new reader can recover the system, established result, consequence, remaining uncertainty, and next transition without reconstructing the entire investigation.

Before sending maintainer-facing text to a human for manual submission, also ask:

```text
Can the maintainer see the next decision in under a minute?
Does the text distinguish target policy from abstract correctness?
Did later feedback change the thesis without the top-level description changing?
Is any internal process detail competing with the technical point?
Is contribution history described accurately without either downplaying or inflating it?
```
