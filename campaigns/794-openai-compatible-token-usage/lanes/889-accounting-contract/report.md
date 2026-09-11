## In simple words

AI SDK presents normalized token totals as counts of tokens actually used. Provider V4 calls `outputTokens.total` the total output/completion tokens used; AI core exposes that number directly, adds it to normalized input to create public `totalTokens`, sums those totals across calls, and OpenTelemetry exports the same public output count as `gen_ai.usage.output_tokens`.

That contract makes a compatibility envelope semantically expensive. Keeping literal provider counters in `raw` preserves evidence, but it does not turn a synthesized normalized total into a mere hint. The normalized field is externally visible accounting data.

## Lane identity

- Fieldwork lane: #889
- Parent campaign: #794
- Programme: #13
- Target hub: #2
- Public Vercel AI source pin: `8e9028317de6a72973971356283271aff44bba74`
- Retrieved: 2026-08-12
- Claim scope: interface and integration
- Evidence class: source-read
- Upstream contact authorized: `false`

## Provider V4 contract

`packages/provider/src/language-model/v4/language-model-v4-usage.ts` documents:

```text
inputTokens.total      = total input (prompt) tokens used
inputTokens.noCache    = non-cached input tokens used
inputTokens.cacheRead  = cached input tokens read
inputTokens.cacheWrite = cached input tokens written

outputTokens.total     = total output (completion) tokens used
outputTokens.text      = text tokens used
outputTokens.reasoning = reasoning tokens used

raw                    = usage in the provider's own shape, including extra data
```

The normalized aggregate fields are described as actual usage counts. No wording marks `outputTokens.total` as a lower bound, upper bound, reconciliation estimate, or best-effort envelope.

## Public projection

`packages/ai/src/types/usage.ts` maps V4 provider usage into public `LanguageModelUsage`:

```text
inputTokens  = usage.inputTokens.total
outputTokens = usage.outputTokens.total

totalTokens = addTokenCounts(
  usage.inputTokens.total,
  usage.outputTokens.total,
)
```

Detailed cache/text/reasoning counters are projected separately.

This means an adapter-level output overcount also changes public `totalTokens`.

## Aggregation

`addLanguageModelUsage` sums:

- input aggregate;
- each input detail;
- output aggregate;
- each output detail;
- public all-in total.

These fields are intentionally independent during aggregation. Therefore the SDK does not require `text + reasoning == output total` as a universal identity.

That independence supports incomplete detail classification, but it does not license arbitrary aggregate synthesis. A useful invariant is category fidelity rather than detail-sum equality.

## Raw provider evidence

Per-call `raw` survives the provider-to-public projection. It can contain counters omitted from standardized usage and is the right place to retain contradictory source values.

Aggregated usage does not construct a corresponding aggregate raw record. A caller reading multi-step `outputTokens` or `totalTokens` cannot recover a corrected aggregate merely because every individual provider call once carried raw fields.

Raw preservation is therefore necessary evidence retention and insufficient semantic qualification for a misleading standardized count.

## OpenTelemetry propagation

`packages/otel/src/open-telemetry.ts` writes normalized public usage directly to GenAI span attributes:

```text
gen_ai.usage.input_tokens  = event.usage.inputTokens
gen_ai.usage.output_tokens = event.usage.outputTokens
```

The same mapping appears on language-model and operation spans. A number chosen by a generic max envelope becomes externally observable as the standard output-token telemetry count.

## Harness propagation

`packages/harness/src/agent/internal/turn-telemetry.ts` accepts V4-shaped usage and normalizes it to public `LanguageModelUsage` by copying `output.total` into public `outputTokens` and recomputing `totalTokens` from normalized input + output. It then dispatches that usage through the telemetry lifecycle.

This is another current path where the normalized aggregate is treated as the canonical SDK-facing count.

## Spend/cost boundary

`packages/gateway/src/gateway-spend-report.ts` exposes input/output/cache/reasoning token dimensions alongside actual cost in the gateway reporting API. This source is a server report reader; it does not prove that provider-adapter normalized usage feeds gateway billing.

Supported claim: token counts are user-visible accounting dimensions adjacent to spend data in the SDK ecosystem.

Unsupported claim: changing `convertOpenAICompatibleChatUsage` directly changes gateway bills. No such causal path was established in this lane.

## Consequence ladder

### Documented/source-read

A wrong normalized output aggregate changes:

1. provider V4 `outputTokens.total`;
2. public `LanguageModelUsage.outputTokens`;
3. public `totalTokens`;
4. multi-call aggregate usage;
5. OpenTelemetry `gen_ai.usage.output_tokens`.

### Inferred caller consequences

Applications may use these public fields for quota enforcement, cost approximation, displays, dashboards, validation, or alerts. Those are reasonable interface-level uses, but a claim about actual deployed callers requires separate integration evidence.

## Unknown-value design check

`LanguageModelV4Usage.outputTokens.total` permits `undefined`, which initially looks useful for contradictory provider usage. AI core's `addTokenCounts` returns the known side when one side is undefined, however. Therefore:

```text
inputTokens = 951
outputTokens = undefined
```

would currently produce public `totalTokens = 951`, a partial total that can look complete.

A broad "mark ambiguous output unknown" policy would need a wider public-total composition decision before it becomes semantically clean. That is a larger change than the Baseten/Kimi incident requires.

## Contract conclusion

The strongest source-supported reading is:

```text
Normalized aggregate fields are accounting claims made by the provider
adapter. Raw provider fields are retained evidence. Detail fields may be
incomplete, but a normalized aggregate should contain only tokens whose
category membership the adapter can defend.
```

This makes the rejected `max(completion, reasoning, total-prompt)` policy too strong for the evidence: the maximum can be numerically conservative while being categorically false.

## Current repair implication

Prefer provider/model-aware conversion for known divergent dialects while leaving the generic converter aligned with OpenAI-compatible semantics. A future explicit ambiguous/unknown representation remains possible, but it requires revisiting public total composition and downstream telemetry semantics.

## Remaining work

- Inspect user-facing documentation and devtools presentation for any stronger promise around totals and detail partitioning.
- Seek real downstream callers only if an integration-impact claim is needed for promotion.
- Coordinate with #888 and #890 before any new implementation generation.

No third-party repository was modified.