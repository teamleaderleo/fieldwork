# Vercel AI SDK Pi inline extension failure visibility

## State

`COMPLETE — source-read + model-executed + target-test-prepared`

Owner: `chatgpt:gpt-5.6-sol`  
Created: `2026-08-11`  
Claim scope: interface  
Target: `target:vercel-ai`  
Target hub: #2  
Programme: #13  
Owned target carrier: `teamleaderleo/ai#69`  
Public upstream contact authorized: `no`

## In simple words

Current Vercel AI SDK Pi support lets callers supply trusted inline extension factories. Those factories can register hooks and tools that the caller deliberately expects to be present in the Pi session.

Pi's resource loader treats a factory exception as a load diagnostic: it records the failure in `extensionsResult.errors` and continues with the successfully loaded extension subset. Pi's `createAgentSession()` returns that `extensionsResult` to its caller so the caller can decide how to present or enforce those diagnostics.

The Vercel harness currently reloads the resource loader, then later calls `createAgentSession()` and destructures only `{ session }`. It never inspects the loader's extension errors. Pi's `AgentSession` likewise constructs its runtime from the successful `extensions` and `runtime` fields and does not automatically consume the errors.

Current answer: a caller-supplied trusted inline extension can fail to initialize and the harness can still start/run without that extension while dropping the only diagnostic carrier that explains its absence.

## Question

When a caller-supplied trusted inline Pi extension factory fails to initialize, does `@ai-sdk/harness-pi` surface the failure instead of quietly starting without that extension?

At public main `ed658ac86670f826b73f812d0d48ff7648a9b7ce`, source evidence says **no**.

## Source map

### Vercel harness

The inline extension feature landed in `c20a3153ad58ecc42a1c97442a6dafba60821e73` and is current at `ed658ac86670f826b73f812d0d48ff7648a9b7ce`.

`packages/harness-pi/src/pi-session.ts`:

1. copies `settings.extensionFactories`;
2. passes them to Pi's `DefaultResourceLoader`;
3. calls `await resourceLoader.reload()`;
4. later calls `createAgentSession(...)`;
5. destructures only `{ session }`;
6. subscribes to the resulting Pi session.

There is no inspection of `resourceLoader.getExtensions().errors` or the `extensionsResult` returned by `createAgentSession()`.

### Pi loader contract

Pi's `DefaultResourceLoader.loadExtensionFactories()` catches each inline factory exception and appends a diagnostic entry to `errors`; loading continues.

This is materially different from a thrown `reload()` failure. A factory can fail while `reload()` itself succeeds.

### Pi session contract

Pi's `createAgentSession()` returns both the created `session` and `extensionsResult`.

`AgentSession._buildRuntime()` uses:

```text
extensionsResult.extensions
extensionsResult.runtime
```

for the extension runner. It does not consume `extensionsResult.errors`.

So the diagnostic remains caller-owned information.

## Why it could matter

The Vercel feature describes these as explicitly caller-supplied **trusted inline extensions**, intended to observe Pi provider/inference events and potentially register extension behavior. A caller selecting such a factory has made it part of the intended session configuration.

Silent partial startup can produce a believable but different run:

```text
caller configures extension
        ↓
factory throws
        ↓
Pi records diagnostic + loads successful subset
        ↓
Vercel ignores diagnostic
        ↓
session starts without requested extension
```

The consequence is configuration integrity and observability: the caller may believe hooks/tools/telemetry are active when that extension never initialized.

No claim is made that every extension failure should make Pi itself fatal. The narrow Vercel question is whether its harness should surface failure of an explicitly requested inline dependency instead of dropping the diagnostic.

## Competing explanations

### H1 — Pi automatically emits extension load errors through AgentSession events

**Weakened by source.** `AgentSession` builds its runner from successful extensions/runtime and does not consume `extensionsResult.errors` in the reviewed runtime path.

### H2 — `resourceLoader.reload()` throws when an inline factory throws

**Rejected by Pi source.** Factory exceptions are caught and stored as extension diagnostics.

### H3 — partial startup is intentional and callers can inspect the errors elsewhere

Pi exposes the errors to the direct `createAgentSession()` caller. Vercel's harness does not expose that returned object or another extension-load diagnostic API in the reviewed path.

### H4 — the extension is optional, so silence is acceptable

The API accepts explicitly caller-supplied trusted factories. Optional configuration still needs an observable failure contract when the selected component cannot initialize. Whether the final API rejects startup or reports a structured diagnostic is a design choice; silent loss is the disputed behavior.

## Executable model

Run:

```sh
python3 playgrounds/EXP-20260811-vercel-pi-inline-extension-errors/run.py
```

Observed:

```json
{
  "current_harness_can_return_session_without_extension": true,
  "current_harness_handoff_contains_error": false,
  "factory_error_recorded_by_loader": true,
  "negative_control_success_has_no_errors": true,
  "pi_can_build_from_successful_subset": true
}
```

The successful-factory case is the negative control. Evidence class: `model-executed`.

## Target-native discriminator

Owned PR: `teamleaderleo/ai#69`  
Exact base: `ed658ac86670f826b73f812d0d48ff7648a9b7ce`

The focused test models Pi's real loader behavior: the factory exception is converted to an extension diagnostic rather than thrown by `reload()`. It then requires the Vercel harness `doStart()` path to surface that caller-supplied extension failure.

Current source is expected to return a harness session instead, failing the assertion for the product-level reason under investigation.

Evidence remains `target-test-prepared` until owned CI executes.

## Change thesis

Current behavior:

```text
explicit trusted inline factory
        ↓
Pi loader records factory error
        ↓
Vercel ignores extension errors
        ↓
session remains usable with extension missing
```

Candidate improvement: make extension load diagnostics observable at the harness boundary. The smallest initial policy is to reject session start when an explicitly supplied inline factory fails, including the Pi diagnostic message. A structured harness diagnostic could be considered if the package already has a suitable startup-warning surface.

The repair should preserve Pi's partial-load implementation internally; Vercel owns the decision about whether its explicit inline extension contract accepts partial startup.

## Candidate tests

1. successful inline factory still starts normally;
2. throwing inline factory produces a visible harness failure or explicit diagnostic;
3. failure message retains enough Pi diagnostic information to identify the extension;
4. multiple factories preserve caller order and report the failing member without hiding successful ones;
5. routine between-turn resource reload still does not re-run factories;
6. genuine Pi session rebuild still creates a fresh extension runtime;
7. no filesystem extension discovery is re-enabled;
8. latest package tests/build/type-check remain green.

## Negative results

- The earlier theory that a factory throw directly rejects `resourceLoader.reload()` is false for Pi's real loader; it catches the factory error.
- The earlier theory that a failed reload necessarily strands Vercel after disposing a Pi session is therefore unsupported for inline factory exceptions.
- Routine resource reload handling already carefully preserves the active extension runtime.

## Evidence classes

| Claim | Evidence class | Limit |
| --- | --- | --- |
| inline factories are explicit caller configuration | `source-read` | Vercel feature/API |
| factory exceptions become Pi extension diagnostics | `source-read` | Pi loader revision |
| createAgentSession returns extensionsResult | `source-read` | Pi SDK revision |
| AgentSession ignores extension errors when building runtime | `source-read` | Pi AgentSession revision |
| Vercel discards the diagnostic carrier | `source-read` | current Pi adapter |
| reduced handoff reproduces silent partial startup | `model-executed` | dependency-free model |
| latest Vercel harness surfaces factory error | `target-test-prepared` | owned #69 queued |

## Recommendation

Retain as a finding and promote to a bounded campaign after target execution confirms the expected current behavior.

The implementation question is:

> What is the smallest harness-owned failure contract that prevents an explicitly requested trusted inline Pi extension from disappearing silently when its factory fails?

## Boundaries

- Third-party upstream remained read-only.
- No provider credentials, production data, or paid calls were used.
- The finding is about caller-visible configuration failure, not malicious extension behavior.
