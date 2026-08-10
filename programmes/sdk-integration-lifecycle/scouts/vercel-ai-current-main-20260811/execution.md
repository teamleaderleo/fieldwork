## In simple words

The scout now has target-native execution for both usage inconsistencies on its strongest finding. The OpenAI-compatible package itself confirms that the captured provider incident normalizes to an output total smaller than its reasoning component and that normalized input plus output is one token lower than the response's parsed raw total.

A separate Codex-harness characterization is executing the deterministic bridge-token resume-state question. The xAI self-managed image-history gap remains explicit maintainer prior art.

## Source pin

- Vercel AI: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`
- Probe: `programmes/sdk-integration-lifecycle/scouts/vercel-ai-current-main-20260811/probe.mjs`

## Local scout probe

Command:

```text
node programmes/sdk-integration-lifecycle/scouts/vercel-ai-current-main-20260811/probe.mjs
```

Exit status: `0`

```text
usage-invariant: {"internal":{"total":6000,"text":0,"reasoning":6001},"publicTotalTokens":6951,"rawTotalTokens":6952,"delta":1}
bridge-secret-redaction: {"attachUsesPersistedToken":true,"redactedStateValidation":"bridge.token required by lifecycle state schema","derivationAvailableOutsideState":true}
xai-image-history: {"convertedItems":0,"requiresPreviousResponseIdForRoundTrip":true}
```

## OpenAI-compatible target execution

Canonical characterization: `teamleaderleo/ai#48`  
Canonical source head: `bd1cc54e7449024f4820f280a798bcf9e079ffb9`  
Execution carrier: `teamleaderleo/ai#50`  
Latest carrier head: `4577ad998abb98cb78cd1e5687ca65b304f68b16`  
Split-control run: `31423425063`  
Runner: Ubuntu 24.04, Node `22.23.1`

The original test generation crossed a TypeScript project boundary and failed before its assertion. That was retained as a harness failure and repaired by keeping the characterization package-local.

The first corrected generation (`31423115164`) established the component invariant in both Node and Edge. The split-control generation (`31423425063`) then ran both claims independently:

```text
Package type check: PASS

Node ordinary package tests: 238 PASS
Node Fieldwork control 1: FAIL
  expected 6000 to be greater than or equal to 6001
Node Fieldwork control 2: FAIL
  expected 6951 to be 6952

Edge ordinary package tests: 238 PASS
Edge Fieldwork control 1: FAIL
  expected 6000 to be greater than or equal to 6001
Edge Fieldwork control 2: FAIL
  expected 6951 to be 6952
```

Both claims are therefore `target-executed` at the pinned source family:

1. normalized `outputTokens.total` can be smaller than normalized `outputTokens.reasoning`;
2. normalized `inputTokens.total + outputTokens.total` can disagree with the same parsed response's `total_tokens` on the retained incident payload.

The target's generic OpenAI-compatible response schema already parses `total_tokens`. Its default converter does not use that field when choosing normalized output total. The affected Baseten chat provider uses this default converter with no provider-specific `convertUsage` override.

## Comparative repair execution

Campaign: Fieldwork #794.  
Candidate A: `teamleaderleo/ai#53` — reasoning becomes a lower bound for normalized output total only when completion undercounts it.  
Execution carrier: `teamleaderleo/ai#54`.

This candidate deliberately changes the incident regression expectation from output total `6000` to `6001`. Package and downstream compatibility execution is pending at this receipt.

## Bridge-token target characterization

Canonical characterization: `teamleaderleo/ai#51`  
Execution carrier: `teamleaderleo/ai#52`.

The test uses the real Codex lifecycle schema and public `HarnessAgent.createSession()` boundary with a sentinel sandbox provider. It distinguishes redacted state rejected before `resumeSession` from caller-rehydrated state that passes validation and reaches the resume sentinel. Target execution is pending at this receipt.

## Evidence class

- OpenAI-compatible usage consistency: `source-read + model-executed + target-executed` for both retained invariants
- reasoning-floor repair candidate: `source-read + target-test-prepared`; execution pending
- deterministic bridge-token redaction/attach: `source-read + model-executed + target-test-prepared`; execution pending
- xAI image-generation self-managed history: `source-read + model-executed`; introducing maintainers explicitly record the limitation as future work

No integration-executed or full-gate claim is made from this receipt.
