## In simple words

The scout now has target-native execution for its strongest finding. The OpenAI-compatible package itself confirms that the captured provider incident can normalize to an output total smaller than its reasoning component. The deterministic bridge-token and xAI history results remain source/model evidence while their separate dispositions continue.

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
Canonical repaired source head: `46f5c91633148de3cdddf5ba205428c9d9a751cf` for the first executed generation  
Execution carrier: `teamleaderleo/ai#50`  
Carrier run: `31423115164`  
Runner: Ubuntu 24.04, Node `22.23.1`

The first attempt on earlier source head `ba9328997cd3a200c8bc4cec8df74320c7662b18` failed TypeScript before the intended assertion because the test imported AI core source across the `openai-compatible` TypeScript project boundary. That was a harness failure. The characterization was repaired to stay package-local before target execution.

Run `31423115164` reached the intended package behavior:

```text
Package type check: PASS
Node ordinary package tests: 238 PASS
Node Fieldwork discriminator: FAIL
  AssertionError: expected 6000 to be greater than or equal to 6001
Edge ordinary package tests: 238 PASS
Edge Fieldwork discriminator: FAIL
  AssertionError: expected 6000 to be greater than or equal to 6001
```

This establishes at `target-executed` evidence class that the current default OpenAI-compatible normalization can publish `outputTokens.total < outputTokens.reasoning` for the target's own retained incident payload.

The canonical source test was then split into two independent controls at head `bd1cc54e7449024f4820f280a798bcf9e079ffb9` so a second generation can separately prove the all-in normalized count (`951 + 6000 = 6951`) disagrees with the same response's parsed `total_tokens = 6952`. That second execution generation is pending at this receipt.

## Evidence class

- OpenAI-compatible usage consistency: `source-read + model-executed + target-executed` for `output total >= reasoning`; second raw-total control pending
- deterministic bridge-token redaction/attach: `source-read + model-executed`; target characterization prepared separately
- xAI image-generation self-managed history: `source-read + model-executed`; introducing maintainers explicitly record the limitation as future work

No integration-executed or full-gate claim is made from this receipt.
