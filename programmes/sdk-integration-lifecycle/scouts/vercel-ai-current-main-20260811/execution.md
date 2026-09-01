## In simple words

The scout now has target-native execution for both retained fresh boundaries.

The OpenAI-compatible package confirms two inconsistent normalized usage outcomes on the target's own captured provider incident: output total can be smaller than reasoning alone, and normalized input plus output can be one token lower than the same response's parsed raw total. That work is promoted to campaign #794.

The Codex harness also confirms that deterministic bridge-token minting remains a caller-side reconstruction primitive: redacted live-bridge state is rejected by `HarnessAgent.createSession()` before sandbox resume, while caller-rehydrated state passes validation. That work is retained as finding #805.

The xAI self-managed image-history gap remains explicit maintainer prior art.

## Source pin and currency

- Vercel AI scout pin: `fc3baaf1ff547efdfcc5cb5a5ee35ed72b8a284c`
- latest public head checked: `cfc587bdfd8fd1996dd902edd14143be6e034baf`
- current-head delta from pin: one commit, confined to Claude Code built-in tool catalog files
- probe: `programmes/sdk-integration-lifecycle/scouts/vercel-ai-current-main-20260811/probe.mjs`

The one intervening public commit does not touch the OpenAI-compatible converter, Baseten provider path, Codex lifecycle schema, or HarnessAgent resume validation used by these findings.

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
Retired execution carrier: `teamleaderleo/ai#50`  
Split-control run: `31423425063`  
Runner: Ubuntu 24.04, Node `22.23.1`

The original test generation crossed a TypeScript project boundary and failed before its assertion. That was retained as a harness failure and repaired by keeping the characterization package-local.

The split-control generation ran both claims independently:

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

Both claims are `target-executed`:

1. normalized `outputTokens.total` can be smaller than normalized `outputTokens.reasoning`;
2. normalized `inputTokens.total + outputTokens.total` can disagree with the same parsed response's `total_tokens` on the retained incident payload.

The generic OpenAI-compatible response schema already parses `total_tokens`. Its default converter does not use that field when choosing normalized output total. The affected Baseten chat provider uses this default converter with no provider-specific `convertUsage` override.

### Comparative repair

Campaign: #794.  
Candidate A: `teamleaderleo/ai#53` — reasoning becomes a lower bound for normalized output total only when completion undercounts it.  
Execution carrier: `teamleaderleo/ai#54`.

The candidate deliberately changes the incident regression expectation from output total `6000` to `6001`. Its current carrier runs OpenAI-compatible type-check and Node/Edge suites plus Baseten type-check and Node/Edge suites. Execution is pending at this receipt.

## Bridge-token target execution

Finding: #805.  
Canonical characterization: `teamleaderleo/ai#51@c40f7b2a5de2a6ad6dcddee8f7b3864a00fc5358`  
Retired execution carrier: `teamleaderleo/ai#52@b51060b709b14967e8ae4d4c0f89b54bbbe276c4`  
Run: `31423683026`  
Runner: Ubuntu 24.04, Node `22.23.1`

The test uses the real Codex lifecycle schema, deterministic `mintBridgeToken`, public `HarnessAgent.createSession()`, and a sentinel sandbox provider.

Observed contract:

```text
redacted live bridge state
  -> lifecycle validation rejects
  -> sandbox resume not reached
  -> mint callback not invoked

same state + caller-rehydrated token
  -> lifecycle validation passes
  -> sandbox resume sentinel reached
```

Exact package receipt:

```text
@ai-sdk/harness-codex type-check: PASS
ordinary tests beside the characterization: 83 PASS
Fieldwork characterization: 1 PASS
84 / 84 total PASS
```

The introducing change's examples configure deterministic minting but still retain and pass the unmodified lifecycle state returned by `detach()`. Current `doDetach()` and `doSuspendTurn()` both serialize `bridge.token`. The feature therefore enables caller-owned secret redaction/rehydration but does not provide that public transformation itself.

Evidence class: `target-executed` for the public resume-state validation/rehydration contract.

## xAI prior-art disposition

The xAI Responses image-generation implementation emits provider-executed tool call/results while self-managed input conversion omits those items. The introducing change explicitly records round-trip support as future work and directs current multi-turn editing through `previousResponseId`.

Disposition: retain as target-map prior art; no duplicate campaign.

## Evidence class

- OpenAI-compatible usage consistency: `source-read + model-executed + target-executed`
- reasoning-floor repair candidate: `source-read + target-test-prepared`; execution pending
- deterministic bridge-token redaction/attach: `source-read + model-executed + target-executed`
- xAI image-generation self-managed history: `source-read + model-executed`; explicit maintainer prior art

No integration-executed or full-gate claim is made from this receipt.
