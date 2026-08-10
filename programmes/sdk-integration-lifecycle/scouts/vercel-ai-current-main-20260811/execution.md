## In simple words

The scout probe executed cleanly against a small transcription of the pinned current-main branches. It confirms the arithmetic consequence of the OpenAI-compatible usage clamp, the current bridge-token resume-state contract, and the xAI image-generation self-managed-history gap.

This is model execution. The OpenAI-compatible usage candidate also has a separate target-native test prepared on `teamleaderleo/ai#48`; that carrier has no registered CI result at this receipt, so it remains `target-test-prepared`.

## Source pin

- Vercel AI: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`
- Probe: `programmes/sdk-integration-lifecycle/scouts/vercel-ai-current-main-20260811/probe.mjs`

## Command

```text
node programmes/sdk-integration-lifecycle/scouts/vercel-ai-current-main-20260811/probe.mjs
```

## Result

Exit status: `0`

```text
usage-invariant: {"internal":{"total":6000,"text":0,"reasoning":6001},"publicTotalTokens":6951,"rawTotalTokens":6952,"delta":1}
bridge-secret-redaction: {"attachUsesPersistedToken":true,"redactedStateValidation":"bridge.token required by lifecycle state schema","derivationAvailableOutsideState":true}
xai-image-history: {"convertedItems":0,"requiresPreviousResponseIdForRoundTrip":true}
```

## Evidence class

- OpenAI-compatible usage consistency: `source-read + model-executed + target-test-prepared`
- deterministic bridge-token redaction/attach: `source-read + model-executed`
- xAI image-generation self-managed history: `source-read + model-executed`

No target-executed, integration-executed, or full-gate claim is made from this receipt.
