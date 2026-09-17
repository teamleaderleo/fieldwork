# wgpu fork characterization log

State: browser and public-wrapper characterizations authored and source-self-reviewed; not compiled or executed

Fieldwork issue: #116

Fieldwork PR: #126

Owned fork draft: `teamleaderleo/wgpu#1`

Upstream contact authorized: false

## Exact records

- [upstream/fork base](https://redirect.github.com/gfx-rs/wgpu/commit/2eddc8c7b2fedd4267f5004745a8bc42974e17a0)
- [current upstream source checked](https://redirect.github.com/gfx-rs/wgpu/commit/c079e55f534d713a60aef145f6df0255b7ddcdc4)
- owned fork: `teamleaderleo/wgpu`
- branch: `fieldwork/surface-config-rejection-state`
- exact characterization head: `3d076485509f6b3f8381de8074bfbdef17bc4133`
- changed files:
  - `tests/tests/wgpu-gpu/create_surface_error.rs`
  - `wgpu/src/api/surface_texture.rs`

The branch remains a characterization carrier, not a selected repair or upstream-ready patch.

Current upstream is seven commits ahead of the fork base. The relevant surface API, browser backend, core presentation, HAL presentation, and shared example framework paths remain unchanged; the wasm test file has unrelated macro churn. Reconciliation and execution are still required for current-target evidence.

## Prepared browser tests

### Existing creation error

Retains the unusable-canvas control where a prior 2D context makes surface creation fail with the expected error.

### Unconfigured browser acquisition

```text
public Surface::get_configuration = None
raw GPUCanvasContext.getConfiguration = null
public Surface::get_current_texture = Lost
raw GPUCanvasContext remains unconfigured
```

Raw invalid state is contained as `Lost`, although configuration—not surface recreation—is the missing operation.

Native core does not expose the same recovery semantics: acquisition errors are routed as validation when a configured error sink exists and are fatal by default before a successful configuration establishes that sink.

### Zero-sized configuration applied with validation

Prepared sequence:

1. create an explicit browser-WebGPU adapter and 1×1 canvas;
2. obtain a supported default configuration;
3. set request width to zero;
4. push a validation error scope;
5. call public `Surface::configure`;
6. require a captured validation error;
7. assert public cache contains the zero-width request;
8. assert canvas is 0×1;
9. assert raw context still reports configured state;
10. push another validation scope;
11. acquire through public wgpu;
12. require `Success` or `Suboptimal` carrying a 0×1 public texture;
13. require a captured acquisition validation error;
14. drop the error texture;
15. restore and configure the supported 1×1 baseline;
16. present successfully.

This characterizes WebGPU's error-object model rather than synchronous rejection. Validation can coexist with installed configuration state, and public `Success` can carry an unusable error texture while the diagnostic arrives separately.

### Rejected configuration after an accepted baseline

Prepared sequence:

1. configure and present a supported 2×2 baseline;
2. create a 7×5 request with unsupported `ExtendedSrgbLinear`;
3. prove the color space is absent from capabilities;
4. call public `Surface::configure`;
5. assert public cache publishes the rejected 7×5 request;
6. assert canvas extent changed to 7×5;
7. assert wgpu acquisition reports `Lost`;
8. assert raw context still reports configured state;
9. acquire a raw browser texture and assert 7×5 dimensions;
10. apply the supported 2×2 baseline to the same surface and present;
11. recreate a surface, retry the rejected request, and observe `Lost` again;
12. apply the baseline to the recreated surface and present.

## Prepared public presentation tests

A private test module beside `wgpu/src/api/surface_texture.rs` uses custom texture, queue, and surface-output-detail implementations.

### Ordinary drop control

```text
construct custom SurfaceTexture
→ drop without Queue::present
→ discard calls = 1
→ release calls = 0
```

### Injected backend panic

```text
construct custom Queue and SurfaceTexture
→ Queue::present consumes the frame
→ public wrapper marks frame presented
→ custom QueueInterface::present records one call and panics
→ catch unwind outside Queue::present
→ discard calls = 0
→ release calls = 0
```

This records the public ownership-commit boundary. It does not claim consume-on-attempt semantics are wrong. The HAL presentation contract also consumes a raw surface texture by value even when presentation returns an error.

## Configuration-state distinctions

The prepared browser tests distinguish:

### `RejectedUnconfigured`

No accepted configuration exists and acquisition is invalid. Browser wgpu currently reports `Lost`.

### `AppliedWithDiagnostic`

Zero-sized raw canvas configuration emits validation but remains installed. Repairing canvas extent can make raw acquisition usable without another raw configure call.

### `RejectedAfterPartialMutation`

Local color-space rejection occurs before raw configure but after canvas extent mutation. Raw configuration can remain old while canvas and public Rust cache reflect the rejected request.

This is why a binary internal configure result is likely insufficient.

## Presentation-state distinctions

Source and wrapper characterization now separate:

### `Acquired`

Surface presentation state still owns the acquired frame.

### `PresentationAttemptCommitted`

Public wrapper has consumed the frame and suppresses drop cleanup.

### `DetachedForPreparation`

Native core has removed `acquired_texture`, but HAL has not consumed the raw image.

### `HalConsumed`

Raw surface texture has been passed by value to HAL presentation.

### `PreparationFailedDetached`

Core detached the frame and failed before HAL consumption.

The public wrapper test reaches `PresentationAttemptCommitted`. It does not reproduce the native `PreparationFailedDetached` state.

## Backend cleanup consequence

The first backend matrix shows that detached-frame drop cannot be treated uniformly.

- **DX12:** acquisition increments `acquired_count`; both explicit discard and present decrement it. A pre-HAL preparation failure appears to leave stale acquired-count bookkeeping.
- **Vulkan:** raw object carries an acquired image index, while explicit native discard is a no-op. Repeated bounded acquisition is required to determine whether images become unavailable.
- **Metal:** the raw object retains `CAMetalDrawable`; dropping it plausibly releases drawable-pool ownership.
- **WebGL:** acquisition wraps a reusable surface-owned backing texture rather than reserving a platform image.

See:

- `presentation-attempt-status-and-ownership.md`
- `pre-hal-presentation-failure-backend-matrix.md`

## Runner strategy

The ordinary wasm runtime runner builds with `webgl,exhaust`. The shared initializer removes `BROWSER_WEBGPU` when WebGL is enabled.

The browser tests remain registered in the normal wasm binary but construct a separate explicit browser-WebGPU instance and assert the selected adapter backend. No second top-level runner or external application was added.

The presentation tests are native/private unit tests gated to `test + custom + std` and do not require a GPU.

## Source self-review

Completed checks:

- existing wasm-only module retained;
- browser cases have distinct responsibilities;
- explicit browser-WebGPU backend assertions used where a device is requested;
- validation error scopes retained by value and popped in order;
- baseline and fallback presentation controls retained;
- unsupported capability proved before rejection;
- raw and public state asserted independently;
- same-surface recovery separated from recreation;
- zero-size validation separated from synchronous rejection;
- public presentation test includes an ordinary-drop negative control;
- presentation panic is caught outside the API call;
- custom discard, release, and present calls are independently counted;
- no direct upstream interaction added.

Potential compile/runtime risks still requiring execution:

- custom-interface signature drift or missing test feature combination;
- rustfmt/clippy on the custom test module;
- browser-WebGPU adapter availability under Playwright/SwiftShader;
- exact generated browser test filters;
- error-scope timing around raw canvas configure and acquisition;
- whether the error texture reaches `Success` or `Suboptimal` exactly as predicted;
- raw `GPUTexture.width` and `height` bindings;
- console-error treatment by test orchestration;
- direct raw texture acquisition alongside the wrapper.

## Execution status

**Not executed.**

For exact head `3d076485509f6b3f8381de8074bfbdef17bc4133`:

- no fork workflow runs or commit statuses are known;
- the available environment has no Rust toolchain;
- no compile, unit-test, rustfmt, clippy, wasm build, Playwright, browser, GPU, DX12, or Vulkan result is claimed.

Expected first validation sequence:

```text
cargo fmt --check
cargo test -p wgpu --features custom present_panic_does_not_discard_or_release_after_ownership_commit
cargo clippy --target wasm32-unknown-unknown --tests --features glsl,spirv
cargo xtask test-wasm --list
cargo xtask test-wasm -- <exact listed unconfigured-browser filter>
cargo xtask test-wasm -- <exact listed zero-size filter>
cargo xtask test-wasm -- <exact listed rejected-configuration filter>
```

Filters must come from `--list`; they must not be guessed.

## Next implementation probes

### P1 — DX12 acquired-count invariant

Prove or disprove:

```text
successful acquisitions
- successful presents
- explicit discards
= acquired_count
```

Inject preparation failure after core detachment and before HAL present.

### P1 — Vulkan repeated acquisition

Use known swapchain image count and bounded acquisition timeouts after injected preparation failure. Record image cycling, semaphore diagnostics, and recreation recovery.

### P1 — Native retained-configuration metadata

Execute the separate core validation-rejection control where an earlier presentation is preserved but public cache and texture metadata follow the rejected request.

## Current decision

Keep the fork PR draft and characterization-only.

Do not:

- claim target execution;
- promote it to Delivery Desk;
- infer a leak from source lifetime alone;
- convert current behavior into permanent desired regressions before semantics are selected;
- redesign public configure or present APIs first;
- contact upstream without explicit authority.
