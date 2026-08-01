# Upstream pull-request result — Add opt-in SSE keep-alive comments

Draft status: `retired — directly overlapping public pull request`  
Historical proposed head: `teamleaderleo/ai:fieldwork/ui-message-stream-keepalive` at `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`  
Historical proposed base: `vercel/ai:main` at `2b872b0db3769decf69945830c66a897c1e37347`  
Public interaction authorized: `no`

## Current result

A new pull request must not be opened. Public PR [`vercel/ai#17921`](https://github.com/vercel/ai/pull/17921) already proposes the same `keepAliveMs` API, immediate and idle SSE comments after the persistence tee, helper propagation, a patch changeset, parser compatibility coverage, reference documentation, troubleshooting guidance, and a Node HTTP example.

Public replacement head inspected: `21cd681724103701c3596770d7252a7ef0ad18db`. It was open, non-draft, mergeable, and had no reviews or discussion at the inspection point. Its hosted CI and changeset runs were `action_required` with no executed jobs.

## Historical candidate summary

- Add optional `keepAliveMs` to UI-message response initialization.
- Emit `: stream-open\n\n` immediately on the client branch.
- Emit `: keep-alive\n\n` after idle intervals while downstream demand exists.
- Keep synthetic comments out of persistence and replay data.
- Reuse one pending source read.
- Clear timer state on close, error, and cancellation.
- Forward the option through Fetch, Node, `streamText`, and agent helpers.

## Historical candidate tests

- complete owned-fork CI `30592239115`: success;
- Verify Changesets `30592239084`: success;
- real Node and controlled proxy carrier `30506032517`, job `90755875694`: success;
- 100-cycle open/cancel soak: success inside the AI test matrix;
- persistence isolation and disabled output: success;
- invalid-option pre-side-effect ordering: success;
- client cancellation with an independent persistence branch: success.

## Exact relationship to the public replacement

Shared design:

- additive `keepAliveMs` option;
- comment bytes at the encoded SSE layer;
- wrapper after the persistence tee;
- immediate opening byte and periodic idle bytes;
- single pending source read;
- source close/error propagation;
- Fetch, Node, streamText, and agent propagation;
- patch changeset and documentation.

Public replacement strengths:

- tests the SDK's own `parseJsonEventStream` parser;
- updates more public reference pages and troubleshooting guidance;
- includes a runnable Node example;
- ties the change to the public reporter's operational context.

Owned candidate strengths retained for review:

- validates before source lock, tee, and `consumeSseStream` callback;
- client cancellation requests reader cancellation without awaiting a sibling tee branch;
- explicit active-persistence cancellation test;
- 100-iteration cancel/timer soak;
- retained hosted exact-head CI and controlled proxy receipt.

## Submission checklist

- [x] Current duplicate and overlap search complete on `2026-08-01`.
- [x] Directly overlapping public work found.
- [x] New submission retired.
- [x] Owned source diff contains no temporary workflow or Fieldwork-only files.
- [x] Exact owned candidate head passed its named gates.
- [ ] Fresh rebase onto current public `main` — intentionally skipped while duplicate public work is active.
- [ ] Signed-commit verification for an upstream submission — irrelevant while retired.
- [ ] Exact authority to open or comment on public upstream — absent.

## Revival condition

Revive only after all of the following:

1. public PR `#17921` closes without an equivalent accepted change;
2. current public `main` still needs the capability;
3. duplicate search is repeated;
4. the owned source is rebased or rebuilt as a clean child of current `main`;
5. focused and ordinary gates rerun at the new head;
6. independent complete-diff review accepts the new generation;
7. exact upstream-contact authority is recorded.

Until then, the owned branch is a read-only validation record rather than a submission candidate.
