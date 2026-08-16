## In simple words

Current primary provider documentation does not establish a Kimi-family token-accounting rule strong enough to widen the retained Baseten/Kimi incident into a generic Kimi converter. Baseten promises OpenAI-compatible Model APIs across a heterogeneous hosted catalog and also supports arbitrary dedicated deployments. Kimi's current Chat Completions reference documents the ordinary prompt/completion/total usage triplet but does not document the `completion_tokens_details.reasoning_tokens` relationship that would prove reasoning is additive, included, or separately billable across current Kimi models.

The retained Kimi-K3 incident remains valid observed evidence for that response. It is insufficient evidence for all Baseten models or all Kimi generations.

## Evidence identity

- Fieldwork lane: #888
- Parent campaign: #794
- Retrieval date: 2026-08-12
- Evidence class: Documented for provider docs; Observed for the retained Kimi-K3 response already recorded by #794
- Upstream contact authorized: `false`

## Baseten Model APIs

Primary source: Baseten, **Model APIs**  
URL: https://docs.baseten.co/inference/model-apis/overview

Supported claims:

- Model APIs expose hosted LLMs through endpoints compatible with OpenAI Chat Completions and Anthropic Messages.
- The hosted catalog spans multiple model families; Baseten manages serving behind one endpoint.
- Pricing is per million tokens, with cached input billed at a cache-input rate.
- Reasoning support varies by model.

Limitation: this overview does not define a provider-wide arithmetic relationship among `prompt_tokens`, cached input, `completion_tokens`, `completion_tokens_details.reasoning_tokens`, and `total_tokens`.

## Baseten Chat Completions reference

Primary source: Baseten, **Chat Completions**  
URL: https://docs.baseten.co/reference/inference-api/chat-completions

Supported claims:

- The endpoint is explicitly described as OpenAI-compatible.
- `usage` is documented as token usage statistics.
- Streaming usage is returned when `stream_options.include_usage` is enabled.

Limitation: the retrieved reference does not document a Kimi-specific reasoning-token partition or say that a contradictory completion/detail pair should be reconciled by `total - prompt`, by `max`, or by addition.

## Baseten dedicated deployments

Primary source: Baseten, **Call your model**  
URL: https://docs.baseten.co/inference/calling-your-model

Supported claims:

- Custom servers can expose a `/sync/v1/chat/completions` OpenAI-compatible endpoint.
- Dedicated deployments can use arbitrary served model names and custom serving implementations.

Implication: the same Baseten SDK path can receive OpenAI-shaped usage from independently controlled serving stacks. A Baseten-wide usage rewrite has no single provider contract to rely on.

## Kimi Chat Completions

Primary source: Kimi API Platform, **Create Chat Completion**  
URL: https://platform.kimi.ai/docs/api/chat

Supported claims from the retrieved current documentation:

- Kimi exposes an OpenAI-compatible Chat Completions API.
- The documented response usage object contains `prompt_tokens`, `completion_tokens`, and `total_tokens`.
- `max_completion_tokens` describes the expected generated output length; reaching it yields finish reason `length`.

Limitation: the retrieved current reference does not document `reasoning_tokens` inside usage or define whether reasoning is included in `completion_tokens`, additive to it, or represented only in a provider-specific detail field.

## Kimi current model surface

Primary source: Kimi API Platform homepage  
URL: https://platform.kimi.ai/

Retrieved current model information identifies Kimi K3 as the flagship model and advertises separate cache-hit, input, and output pricing. This confirms K3 is current, but it still does not define the response-counter partition needed for an adapter rule.

## Consequence for #794

The exact retained Baseten/Kimi response can still support an incident-specific interpretation because its capture includes:

```text
prompt=951
completion=6000
reasoning=6001
total=6952
finish=length
text output=none
```

and the original provider-fix record says the model exhausted its output budget in reasoning before emitting text.

Current provider docs do not establish that the same accounting applies to all current Kimi K3 requests, to Kimi K2/K2.6, or to arbitrary Baseten-hosted Kimi deployments.

## Clearing evidence for a model-family repair

Any one of these would materially strengthen a Kimi-family adapter rule:

1. primary Baseten or Kimi documentation defining the reasoning/completion relationship;
2. a current retained provider response for the intended model family plus generated text/reasoning evidence that distinguishes subset from additive accounting;
3. several current Baseten/Kimi fixtures showing the same relationship across generate and stream paths;
4. provider source/schema evidence that explicitly constructs the counters with stable membership semantics.

Until then, a model-family implementation should remain held. The observed incident can be retained as a narrow provider finding and regression input without turning its arithmetic into a universal rule.

No third-party repository was modified.