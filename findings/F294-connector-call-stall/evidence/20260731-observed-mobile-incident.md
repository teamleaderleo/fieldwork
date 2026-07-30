# Observed ChatGPT mobile connector-call incident — 2026-07-31

## In simple words

A read-only connector search did not finish normally. The mobile conversation displayed the beginning of the connector's internal JSON arguments, stayed in `Thinking`, and later ended as `Stopped thinking` without a normal result or typed error.

This note retains only the privacy-safe observation. It does not identify the owning defect boundary.

## Observation boundary

- Observer: user and current GPT-5.6 Thinking session.
- Surface: ChatGPT mobile interface.
- Local time: approximately `2026-07-31 07:06 +08:00`.
- Triggering work: Workstream I source and workflow review for Fieldwork #254.
- Intended internal action: search within a previously fetched GitHub connector response for a text fragment.
- Intended action class: read-only; no repository mutation and no public upstream interaction.

## Visible sequence

1. The interface showed normal assistant progress commentary.
2. It showed a connector activity label for fetching Node job logs.
3. It showed `Thinking`.
4. It displayed raw text beginning with this unterminated payload:

```text
{"uri":"/response/turn242","query":"partial
```

5. It did not display a normal connector result, typed tool error, timeout notice, or assistant recovery answer.
6. It later displayed `Stopped thinking`.

## What is established

| Claim | Evidence class | Support | Limit |
| --- | --- | --- | --- |
| A partial internal-looking connector payload became user-visible. | observed | User-provided screenshot and live conversation sequence | Does not identify whether the model, host, connector runtime, or mobile client produced the presentation event. |
| The visible payload was unterminated JSON. | observed | Exact privacy-safe prefix retained above | Does not establish whether the underlying invocation envelope was also malformed or only its presentation was truncated. |
| The turn did not produce a normal result before ending as `Stopped thinking`. | observed | Screenshot and conversation sequence | Does not establish backend duration, cancellation cause, or whether a hidden typed error existed. |
| The intended action was read-only. | observed | Current session tool intent | Does not establish whether any runtime began executing the action. |
| No public upstream write occurred. | observed | Current session action history | Does not prove absence of unrelated platform telemetry. |

## What is deliberately not retained

- no screenshot binary;
- no access token, credential, cookie, private repository content, or complete connector arguments;
- no claim about frequency or severity beyond this one incident;
- no attribution to public Codex, ChatGPT host infrastructure, the GitHub connector, or the mobile client.

## Initial hypotheses

- incomplete model-to-tool serialization;
- host/client fallback rendered an unrecognized partial invocation event as text;
- a tool future or connector read did not settle under cancellation or timeout;
- backend termination and mobile presentation state diverged;
- more than one of these occurred in sequence.

The canonical finding owns comparison and next steps.