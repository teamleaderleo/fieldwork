# wgpu surface lifecycle contract matrix

State: source-, history-, specification-, and test-design evidence; browser characterization authored but not executed

Fieldwork issue: #116

Fieldwork PR: #126

Owned fork draft: `teamleaderleo/wgpu#1`

Fork test head: `teamleaderleo/wgpu@38c9498bdae8f0ddfdc6a04c6d763ce889f3f5ad`

Upstream source pin: `gfx-rs/wgpu@2eddc8c7b2fedd4267f5004745a8bc42974e17a0`

Upstream contact authorized: false

## Why a matrix is necessary

Surface configuration currently crosses six distinct layers:

1. the configuration requested by the Rust caller;
2. local wgpu validation or mapping;
3. backend configuration or retained backend state;
4. the public `Surface::config` cache;
5. the typed result of `get_current_texture`;
6. the recovery action described to the caller.

The current API often collapses those layers. In particular, public `Surface::configure` calls a backend method returning `()`, then stores the requested configuration unconditionally. The wrapper can observe only that dispatch returned, not whether the configuration was accepted.

The matrix below keeps requested, accepted, published, and recoverable state separate.

## Contract matrix

| Case | Backend operation | Actual backend state after operation | Public cache today | Acquisition today | Documented or example recovery | More truthful interpretation |
| --- | --- | --- | --- | --- | --- | --- |
| First supported configuration | Applied | Configured with request | Request | `Success` or `Suboptimal` | Render/present | Aligned |
| Supported reconfiguration | Applied after idle/rebuild | Configured with new request | New request | `Success` or `Suboptimal` | Render/present | Aligned |
| Browser-only color-space mapping rejection after a valid baseline | Raw `GPUCanvasContext.configure` is not called | Raw canvas remains configured with the earlier baseline | Rejected request | `Lost` while `configure_failed` is set | Recreate surface and retry cached request | Wrapper-local rejected request; same-surface valid reconfiguration clears it |
| Browser-only color-space mapping rejection before first configuration | Raw configure is not called | Raw canvas remains unconfigured | Rejected request | `Lost` | Recreate surface and retry cached request | Rejected/not configured; a supported configuration is required |
| Browser `GPUCanvasContext.configure` throws synchronously | Browser call attempted and rejected | Initial state or prior accepted state depends on browser/WebGPU semantics and exact failure | Rejected request | `Lost` | Recreate surface and retry cached request | Rejected configuration; preserve and expose whether a prior accepted state remains |
| Browser validation diagnostic where WebGPU still configures the context | Browser call may establish configured state while reporting a validation error | Potentially configured with requested fields | Request | Potentially usable | Error-scope guidance plus acquisition status | Applied-with-diagnostic must remain distinct from rejected |
| Browser `getCurrentTexture` throws | Configure state may still be valid | Unknown from wrapper; raw exception is logged | Last requested configuration | `Lost` | Recreate surface | Acquisition failure, not necessarily surface loss or configuration rejection |
| Native/core validation failure before HAL configuration | HAL configure is not called | Existing core `Presentation` remains intact when one existed | Rejected request | Core may still acquire using the old accepted configuration | Public status depends on acquisition; cache says rejected request | Old accepted presentation plus rejected latest request; cache and texture metadata may diverge |
| Native/core validation failure before first configuration | HAL configure is not called | Unconfigured | Rejected request | Core reports not configured through error handling | Cache says configured | Rejected/not configured |
| Native HAL configure failure after validation | Old core `Presentation` is removed before HAL configure; HAL call fails | Core becomes unconfigured | Rejected request | Error/validation path on acquisition | Error scope or surface recovery | Rejected and no accepted presentation remains |
| Native actual surface loss during acquisition | HAL reports `Lost` | Surface genuinely needs recreation | Last accepted/requested cache, normally aligned | `Lost` | Recreate surface | Aligned when cache was accepted |
| Native device loss | Device validity check fails | Device and dependent resources invalid | Existing cache remains | Device error/loss path | Recreate device/resources | Device lifecycle, not configuration lifecycle |
| `Outdated` | HAL says configuration no longer matches surface | Existing surface can be reconfigured | Last accepted cache | `Outdated` | Reconfigure | Aligned |
| `Suboptimal` | Texture is usable but does not exactly match current surface properties | Usable for current frame | Last accepted cache | `Suboptimal(texture)` | Present current texture, then reconfigure | Requires examples not to discard or misuse the returned texture |
| `Timeout` or `Occluded` | No usable new frame now | Configuration remains meaningful | Last accepted cache | `Timeout` or `Occluded` | Skip and retry later | Aligned |

## Browser pre-rejection finding

The deterministic browser test uses `SurfaceColorSpace::ExtendedSrgbLinear`, which the browser backend declares unrepresentable. The backend returns before invoking `GPUCanvasContext.configure`.

After a supported baseline, source predicts this state:

```text
raw GPUCanvasContext configuration = supported baseline
raw GPUCanvasContext acquisition = usable
wgpu public Surface::get_configuration = rejected request
wgpu get_current_texture = Lost
wgpu same-surface supported configure = recovery
surface recreation + same rejected request = Lost again
```

This is stronger than a generic status-label complaint. In this path, the underlying browser surface is not lost. `Lost` is a wrapper-owned sentinel for a rejected request.

The owned-fork characterization now holds the raw context and checks both `getConfiguration()` and raw `getCurrentTexture()` after wgpu reports `Lost`. It also separates same-surface supported recovery from recreation with the same unsupported request.

## Native/core validation consequence

`wgpu-core::Surface::configure` validates the proposed configuration before taking the existing `Presentation`. A validation failure therefore preserves the earlier accepted core presentation.

The public wrapper nevertheless stores the rejected request because dispatch returns `()` after routing the error to the device error sink.

This creates a potentially more consequential mismatch than the browser sentinel:

```text
core presentation config = earlier accepted baseline
public Surface cache = rejected request
core acquisition = based on baseline
public SurfaceTexture descriptor = built from public cache
```

If the rejected request changes width, height, format, usage, or view expectations, public texture metadata may describe the rejected request while the backend texture was acquired under the earlier accepted configuration.

This remains source reasoning until an executable surface fixture confirms it. It deserves a dedicated control because it can affect more than `get_configuration()` wording.

## Native HAL-failure consequence

The core path removes the existing `Presentation` immediately before calling HAL configure. If HAL configuration then fails, the former presentation is not restored.

That state differs from validation failure:

- validation failure can leave an old accepted presentation alive;
- HAL failure leaves core unconfigured;
- both currently cause the public wrapper to cache the rejected request.

A future acceptance result therefore cannot be only `true` or `false` if recovery guidance needs to preserve whether an earlier accepted presentation remains.

## Historical alignment

### Nonfatal surface errors

The move away from fatal surface errors deliberately accepted that fallout would need to be handled incrementally. Maintainer discussion explicitly raised the difficulty of deciding whether failures are application errors, driver/end-user conditions, unknown surface state, or recoverable dynamic conditions.

### `get_configuration`

`get_configuration()` was introduced later as a direct accessor for the wrapper cache, with no tests. Its similarity to WebGPU `getConfiguration()` was the stated motivation, but accepted-versus-requested semantics were not established.

### Typed acquisition outcomes

`CurrentSurfaceTexture` was introduced to make recovery harder to ignore. `Lost` was documented and reviewed as a recreation signal. The browser rejected-configuration sentinel was added later by the HDR/color-space work to prevent an uncatchable wasm abort.

The present mismatch is therefore an interaction among individually reasonable changes rather than evidence that any one change was careless.

## Test-infrastructure finding

The repository's automated wasm runtime job executes `cargo xtask test-wasm`.

That runner:

- builds the GPU test binary with `webgl,exhaust`;
- exports the browser test entry point under the WebGL feature;
- uses the shared initializer, which deliberately removes `BROWSER_WEBGPU` whenever `webgl` is enabled;
- launches Chromium with SwiftShader enabled.

Consequently, browser WebGPU receives compile checks in CI but no ordinary runtime path through the shared initializer.

The owned-fork characterization now avoids silently disappearing from the runner:

- it remains registered in the existing wasm test binary;
- it constructs a separate instance explicitly restricted to `BROWSER_WEBGPU`;
- it asserts that the selected adapter is `Backend::BrowserWebGpu`;
- the surrounding harness may still use its ordinary WebGL context for orchestration.

Execution is still required to prove that the Playwright/SwiftShader environment supplies a browser-WebGPU adapter.

## Candidate internal models

### Model A — accepted-state result

```text
SurfaceInterface::configure(...) -> ConfigureDisposition
```

Possible dispositions:

- `Applied`;
- `AppliedWithDiagnostic`;
- `RejectedPreservingPrevious`;
- `RejectedUnconfigured`.

The public cache updates only for an applied disposition. Recovery and acquisition classification can use the rejection state.

Advantages:

- models browser and core differences;
- can preserve old accepted state;
- avoids immediate public signature change.

Costs:

- touches core, browser, and custom dispatch implementations;
- requires deciding whether the disposition is stable enough for custom backends;
- may duplicate error information already routed elsewhere.

### Model B — backend-owned accepted configuration query

The public wrapper stops owning authoritative configuration state and asks the backend for accepted state.

Advantages:

- closest to raw backend truth;
- avoids publishing a request merely because dispatch returned.

Costs:

- core, browser, and custom backends must expose configuration state;
- resolved-versus-requested values need a defined contract;
- browser raw configuration cannot represent all wgpu abstractions identically.

### Model C — retain requested cache, rename and document

Treat `get_configuration()` as `last_requested_configuration` and leave typed status unchanged.

Advantages:

- smallest implementation change;
- no dispatch compatibility cost.

Costs:

- does not fix misleading `Lost` recovery;
- does not prevent public texture descriptors from using rejected metadata;
- weakens the stated similarity to WebGPU `getConfiguration()`;
- requires applications to infer acceptance indirectly.

### Model D — browser-only status refinement

Replace the browser `configure_failed` boolean with a typed internal reason and map pre-rejection to `Validation` or a new outcome rather than `Lost`.

Advantages:

- fixes the clearest recovery lie;
- can keep raw browser failure detail.

Costs:

- does not fix unconditional public caching;
- does not address native/core validation mismatch;
- `Validation` currently implies an error scope or uncaptured error was raised, which local browser mapping rejection does not presently do.

## Current preference

Do not start with a public `Surface::configure -> Result` redesign.

Proceed in layers:

1. execute the browser characterization;
2. add an executable core/public-cache control for validation failure preserving an old presentation;
3. determine whether public texture metadata diverges after that failure;
4. distinguish HAL failure, browser pre-rejection, browser thrown rejection, and acquisition exception;
5. prototype a private disposition only after those states are measured;
6. align documentation and examples regardless of whether dispatch changes;
7. request explicit authorization before upstream contact.

## Stop conditions

- Do not label every contained browser exception as an upstream defect.
- Do not claim raw browser conformance failure where wgpu rejected before calling the browser.
- Do not replace one overloaded boolean with another overloaded boolean.
- Do not make custom backends carry a new compatibility burden without proving the public-state benefit.
- Do not promote the fork draft until it is compiled and run through a browser-WebGPU adapter.
