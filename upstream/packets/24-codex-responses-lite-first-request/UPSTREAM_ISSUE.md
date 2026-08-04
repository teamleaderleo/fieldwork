# Upstream issue draft — first generated Responses Lite request depends on prewarm state

Draft status: `working draft in owned repository; filing unauthorized`  
Public interaction authorized: `no`  
Current public source inspected: `openai/codex@e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`  
Current proof of concept: `teamleaderleo/codex:fix/responses-lite-first-request-e4e0c70` at `abf61e5fb8505181e071674ce224faff17e79d77`

---

# Should the first generated Responses Lite request depend on prewarm state?

## What happens

Before the first user turn, Codex can send a Responses Lite request with `generate=false`. That request sends the tool and instruction prefix and opens the WebSocket path, but it does not ask the model to produce an answer.

The server returns a response ID for that request. Codex can then send the first real model request like this:

```text
prewarm request
  generate = false
  input = [tools and instructions]
  -> response id warm-1

first generated request
  previous_response_id = warm-1
  input = [new user input]
```

The first generated request therefore depends on the server remembering everything attached to `warm-1`.

## The question

Is that dependency part of the intended Responses Lite contract?

The other option is:

```text
prewarm request
  generate = false
  input = [tools and instructions]

first generated request
  no previous_response_id
  input = [tools, instructions, and user input]
  -> response id resp-1

later generated request
  previous_response_id = resp-1
  input = [new input only]
```

In that version, prewarm prepares the connection, while the first generated response becomes the starting point for later incremental requests.

## Why it matters

Responses Lite puts tools and instructions in the input sequence. When the first generated request contains only the new suffix, its full meaning exists partly in the earlier prewarm request.

That may be fine if the service guarantees that the prewarm state remains available and is treated as part of the first turn. If that is not the intended contract, the first generated request can be made self-contained instead.

This issue does not claim that this causes a known production failure, connector timeout, or hanging tool call. It asks which request sequence Codex and the Responses service are supposed to rely on.

## How to see it

1. Enable Responses Lite and WebSocket startup prewarm.
2. Capture the `generate=false` prewarm request and return a response ID such as `warm-1`.
3. Submit the first user turn.
4. Inspect the first generated `response.create` request.

The current path can use `warm-1` as `previous_response_id` and send only the new input.

## Possible change

A proof of concept changes only the first generated Responses Lite request after prewarm:

1. Stop using the prewarm response ID.
2. Send the full current request.
3. After the first generated response succeeds, use that response ID for later incremental requests.
4. If the first generation fails, retry the same full request.

The generic non-Lite WebSocket path is unchanged.

Tests cover:

- the full first generated request after prewarm;
- the next request continuing from the first generated response;
- a failed first generation being retried without the prewarm response ID.

## Questions

1. Should a `generate=false` Responses Lite response be the parent of the first generated turn?
2. If yes, should Codex have a test that records that service contract?
3. If no, should the first generated Lite request send the full input?

I have a small proof of concept with tests available if the team wants to take this route. I am opening the issue first because external code contributions are invitation-only.

---

## Internal filing checklist

- [x] Current contribution guidance rechecked: issue first; external PRs by invitation only.
- [x] Current public source inspected at `e4e0c7070e53cf9535fd0083d8fb840b6cd410cf`.
- [x] Current one-commit proof of concept restacked at `abf61e5fb8505181e071674ce224faff17e79d77`.
- [x] Draft separates observed behavior from possible impact.
- [x] Draft does not claim that this explains connector hangs or app timeouts.
- [x] Draft contains no private execution links or Fieldwork terms in the public body.
- [ ] Current-head execution completes.
- [ ] Filing-time duplicate search refreshed.
- [ ] User authorization to file recorded.
