## In simple words

This lane investigates a distinct OpenAI-compatible compatibility gap discovered while following #794: providers can put reasoning token usage at `usage.reasoning_tokens`, while AI SDK's generic normalization currently reads only `completion_tokens_details.reasoning_tokens`.

Current state: source-backed finding with an owned-fork characterization prepared next. No production repair has been selected.

## Files

- `report.md` — mechanism, consequence, repair boundaries, stop condition.
- `evidence-map.md` — source/provider evidence and claim classes.
- `characterization-plan.md` — exact target-native test plan.

## Current source pins

- Vercel AI: `8e9028317de6a72973971356283271aff44bba74`
- SGLang: `b3bffef70aa17733b48af91e4b529e72c913bc6e`
- Retrieved: 2026-08-12

Upstream contact authorized: `false`.
