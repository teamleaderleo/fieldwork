# Upstream issue draft — Responses Lite first generated turn can inherit a `generate=false` prewarm response

Draft status: `preferred first public route — ready for human review, filing unauthorized`  
Public interaction authorized: `no`  
Current public source inspected: `openai/codex@e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`  
Current clean proof-of-concept: `teamleaderleo/codex:fix/responses-lite-first-request-e4e0c70` at `abf61e5fb8505181e071674ce224faff17e79d77`

---

# Responses Lite first generated turn can inherit a `generate=false` prewarm response

## Summary

Responses Lite startup prewarm sends the tool and instruction prefix over the WebSocket with `generate=false`. Codex itself treats that operation as connection setup rather than an inference attempt, but the first real generated request can still use the prewarm response ID as `previous_response_id` and send only an incremental suffix.

That makes the first generated turn depend on server-side state created by a request that intentionally generated no turn.

Is that the intended Responses Lite contract? A simpler invariant would be:

- prewarm remains connection/setup work;
- the first generated Lite request is complete and has no prewarm `previous_response_id`;
- incremental reuse begins after the first generated response;
- a failed first generation retries the same complete request;
- generic non-Lite WebSocket warmup behavior remains unchanged.

## Current request sequence

A simplified startup sequence is:

```text
1. prewarm
   generate = false
   input = [Lite tool/instruction prefix]
   -> response id warm-1

2. first generated request
   previous_response_id = warm-1
   input = [new suffix]
```

The prewarm response is deliberately omitted from inference tracing, while the first generated request may still use it as transport ancestry.

For Responses Lite, tools and instructions are represented inside the input sequence. The complete first generated request is therefore not visible on the wire unless the server correctly and durably associates the full prewarm prefix with `warm-1`.

## Why this is worth clarifying

This may be an intentional server-side caching contract. If so, documenting and directly testing that contract would make the dependency clear.

If it is not intentional, the current transition creates an avoidable state boundary:

- a non-generating setup response becomes the parent of generated conversation state;
- first-generation retry behavior depends on whether that setup state is still valid;
- client-side request identity and wire-visible request identity differ at the first real turn.

This report does not claim a measured production failure or a confirmed backend contract violation. It asks whether the current ownership transition is deliberate.

## Reproduction against a mock Responses WebSocket

1. Enable `use_responses_lite` and startup WebSocket prewarm.
2. Capture the `generate=false` prewarm request and return a response ID such as `warm-1`.
3. Submit the first user turn.
4. Inspect the first generated `response.create` request.

Current behavior can produce a request that continues from `warm-1` rather than carrying the complete current Lite input independently.

## Proposed invariant

The first non-warmup request should use the full-request path when:

```text
Responses Lite is enabled
and the retained response came from untraced startup prewarm
```

The resulting sequence would be:

```text
1. prewarm
   generate = false
   input = [Lite tool/instruction prefix]

2. first generated request
   no previous_response_id
   input = [same Lite prefix, user input]
   -> response id resp-1

3. later generated request
   previous_response_id = resp-1
   input = [new suffix]
```

A failed first generated request would retry step 2 rather than inheriting prewarm ancestry.

## Candidate implementation direction

A narrow proof-of-concept does the following only for the first generated Responses Lite request after untraced prewarm:

1. discard the retained prewarm response receiver;
2. skip incremental request preparation;
3. use the existing full-request serializer.

After a generated response succeeds, the existing incremental continuation path resumes normally. No API or wire schema changes are required, and generic non-Lite warmup compression is unchanged.

Focused mock-WebSocket controls cover:

- complete first generation after prewarm;
- incremental continuation from the first generated response;
- complete retry after a failed first generation.

## Questions for maintainers

1. Is a `generate=false` Responses Lite response intended to be a valid semantic parent for the first generated turn?
2. If yes, should that server-state dependency be documented and tested explicitly in Codex?
3. If no, would making the first generated Lite request complete be the preferred invariant?

I have a small one-production-hunk proof-of-concept with focused tests available if maintainers want to pursue this direction. I am opening the issue first because external code contributions are invitation-only.

---

## Internal filing checklist

- [x] Current contribution guidance rechecked: issue-first; external PRs by invitation only.
- [x] Current public source inspected at `e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`.
- [x] Current one-commit proof-of-concept restacked at `abf61e5fb8505181e071674ce224faff17e79d77`.
- [x] Draft avoids claims of measured prevalence, confirmed production impact, or a known server-contract violation.
- [x] Draft contains no private execution links or Fieldwork terminology.
- [ ] Corrected exact-head current-source execution completes.
- [ ] Filing-time duplicate search refreshed.
- [ ] Exact user authorization to file recorded.
