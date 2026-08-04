# Unit 24 draft working notes

This file is the place to revise the public framing before any upstream contact.

## Current surfaces

- Issue draft: `UPSTREAM_ISSUE.md`
- Conditional PR draft: `UPSTREAM_PR.md`
- Code review surface: `teamleaderleo/codex#143`
- Source branch: `teamleaderleo/codex:fix/responses-lite-first-request-e4e0c70`

The issue draft is the expected first public step. The PR draft is held unless a Codex maintainer invites a contribution.

## Voice

- Start with what the program sends and receives.
- Use common words when they are accurate.
- Do not add adjectives to make the issue sound more important.
- Avoid words such as `narrow`, `deliberately`, `explicitly`, `semantic`, `ownership`, and `invariant` unless they carry information that cannot be stated more plainly.
- Separate what the code does from what might happen in production.
- Do not claim that this explains connector hangs, app timeouts, or stalled tool calls.
- Assume the reader can follow the code once the request sequence is clear.
- Keep internal process, receipts, and Fieldwork terminology out of the public body.

## Plain-language explanation

Responses Lite is a way for Codex to send model requests over a WebSocket while reusing earlier request state.

At startup, Codex can send tools and instructions with `generate=false`. This is prewarm. The server returns a response ID even though no answer was generated.

Today, the first real model request can point to that response ID and send only the new user input. Our proposed change makes the first real request send the whole input. Later requests can still reuse the first generated response.

## What this may affect

This sits in the model-request transport, before the model produces the first answer in a prewarmed Responses Lite session.

A bad state handoff here could make the first request depend on server-side prewarm data. We have not shown that this causes a user-visible failure in the Codex app.

This does not control:

- GitHub connector HTTP requests;
- tool-call execution;
- connector timeout policy;
- cancellation of a stuck connector call;
- UI timeout behavior;
- retry policy for a connector operation.

Those are separate paths and may be better candidates for the hanging-tool problem described by the user.

## Open questions

1. Does the Responses service promise that a `generate=false` response can be used as the parent of the first generated Lite request?
2. Is this path enabled for the user-facing Codex app, or only for selected models and environments?
3. Does the first generated request ever fail because prewarm state is missing, stale, or interpreted differently?
4. Should the public issue lead with the contract question or with retry behavior?
5. Is there a smaller user-visible reproduction than the mock WebSocket test?

## Current position

The source change is prepared and the same three file blobs passed the earlier focused run. A run tied to the current commit SHA remains queued.

Do not file or submit anything publicly without the user reviewing the current draft and authorizing the contact.
