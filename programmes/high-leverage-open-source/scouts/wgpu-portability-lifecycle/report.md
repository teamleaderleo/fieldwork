# wgpu portability, diagnostics, and GPU lifecycle

Issue: #116

Programme: #114

State: active source reconnaissance with owned-fork target tests prepared; no target execution

Upstream contact authorized: false

## Exact pins

- released baseline: `wgpu v30.0.0`
- [wgpu source revision](https://redirect.github.com/gfx-rs/wgpu/commit/2eddc8c7b2fedd4267f5004745a8bc42974e17a0)
- [nonfatal-surface merge](https://redirect.github.com/gfx-rs/wgpu/commit/ebdd958d4b0d9fc3f8c7324ad2db4cd7eb8041d5)
- [`get_configuration` merge](https://redirect.github.com/gfx-rs/wgpu/commit/90db08157ccd5a5a25564219f294d023d4253d5a)
- [unified acquisition-result merge](https://redirect.github.com/gfx-rs/wgpu/commit/e4dae053c05c849fc56e923d0cbf23c3730c33e6)
- [HDR/browser-surface merge](https://redirect.github.com/gfx-rs/wgpu/commit/3fb225a9c6240bd7e9db3d202410db6d894368ec)
- [WebGPU editor-draft source](https://redirect.github.com/gpuweb/gpuweb/commit/d390da5f80f18e82d9535a40c6f2f1f65e6884ae)
- [WebGPU CTS source](https://redirect.github.com/gpuweb/cts/commit/dc20b8682aa71ff31f135de6ae7f8acaa2e16383)
- owned fork test head: `teamleaderleo/wgpu@77c46ce89efab608b1d377b3d6cecf18b006fb72`

### Pin correction

An earlier draft named `134c29d8ac3e4fb20c96028de95cf1e92d1a5192` as the WebGPU specification revision. GitHub does not resolve that value as a commit in the specification repository. It has been replaced with the verified editor-draft source commit above. The CTS pin was independently verified and remains valid.

No released binary, browser, native GPU, Playwright, or repository test execution is claimed below. Evidence is explicitly scoped as `source-read` or `target-test-prepared`.

## In simple words

The main seam is no longer merely “browser configuration can fail.” It is that one public operation crosses several different pieces of state without an acceptance receipt:

```text
caller request
→ local mapping and validation
→ canvas/window mutation
→ raw backend configuration
→ public configuration cache
→ typed acquisition outcome
→ recovery guidance
```

`Surface::configure` calls a dispatch method returning `()`, then caches the request. Native and browser implementations can return after not applying the complete request. The public wrapper cannot tell accepted state from rejected or partially applied state.

## Claim-scoped status

| Claim | Evidence class | Important exclusion |
| --- | --- | --- |
| Public configuration caching is not tied to backend acceptance | source-read | no executed reproduction |
| Browser unsupported color-space mapping returns before raw canvas configuration | source-read plus target-test-prepared | browser test not executed |
| Browser configuration mutates canvas width and height before later rejection | source-read plus target-test-prepared | raw runtime state not observed yet |
| Browser unconfigured acquisition maps raw invalid state to `Lost` | source-read plus target-test-prepared | browser test not executed |
| Browser raw acquisition exceptions are all collapsed to `Lost` | source-read | exception families not injected |
| Native validation can preserve an earlier presentation while public cache changes | source-read | no core-backed runtime control |
| Public surface-texture metadata can follow rejected cache values | source-read risk | wrapper and core controls not executed |
| Ordinary wasm runtime initialization selects WebGL rather than browser WebGPU | source-read | actual headless adapter availability unmeasured |

No claim is `target-executed`, `integration-executed`, or `full-gate`.

## Architecture

```text
public Rust API (`wgpu`)
→ native validation and ownership (`wgpu-core`)
→ native graphics interface (`wgpu-hal`)
→ Vulkan / Metal / DX12 / GLES
```

On WebAssembly, the same public API can dispatch directly to the browser WebGPU implementation instead of `wgpu-core`. Naga owns shader parsing, validation, and translation. This split is intentional; the goal is truthful cross-layer state and recovery, not identical backend mechanics.

## Public surface wrapper

`Surface` stores:

- a dispatched backend surface;
- a mutex-protected configuration cache;
- an optional source handle retained for backend lifetime.

Public `Surface::configure`:

1. invokes backend `configure`;
2. receives no acceptance result;
3. stores a clone of the requested configuration.

`get_configuration()` therefore returns last published request state, not demonstrably accepted backend state.

A successful or suboptimal acquisition constructs the public `Texture` descriptor from this cache. Width, height, format, and usage can therefore be wrong if the cache and accepted backend state diverge.

## Browser WebGPU configuration ordering

The browser backend performs operations in this order:

1. set HTML or offscreen canvas width and height from the request;
2. validate web-only present mode;
3. validate web-only alpha mode;
4. map format, usage, color space, and view formats;
5. reject locally unrepresentable color spaces or call raw `GPUCanvasContext.configure`;
6. set or clear `configure_failed`.

This ordering creates a new partial-state case.

### Rejected request after an accepted baseline

For `ExtendedSrgbLinear`, wgpu rejects locally before raw `GPUCanvasContext.configure`. However, canvas dimensions were already changed.

Source predicts:

```text
raw GPUCanvasContext configuration = earlier accepted configuration
canvas width/height = rejected request
public Surface cache = rejected request
wgpu configure_failed = true
wgpu acquisition = Lost
raw acquisition = potentially usable at resized canvas extent
```

This is not simply “the previous configuration remains.” Configuration ownership is split: raw WebGPU configuration can remain old while the drawing-buffer extent and Rust cache already reflect the rejected request.

The owned-fork characterization now changes a 2×2 baseline to a rejected 7×5 request and checks the canvas and raw texture dimensions separately.

## Browser acquisition classification

### Before any successful configuration

Raw WebGPU reports invalid state when `getCurrentTexture` is called on an unconfigured context. The browser wgpu backend catches the exception and returns `CurrentSurfaceTexture::Lost`.

The public `Lost` documentation says to recreate the surface, or device and resources when device loss is involved. For an unconfigured context, the missing action is configuration, not recreation.

Native core does not use the same classification:

- after a successful configuration, acquisition errors are routed to the retained device error sink and returned as `Validation`;
- before any successful configuration, no retained error sink exists and the core path treats the error as fatal by default.

This is a source-confirmed backend difference in public recovery semantics. It may be acceptable, but it must be documented or refined rather than treated as one uniform notion of surface loss.

### Raw acquisition exceptions after configuration

Any JavaScript exception from `GPUCanvasContext.getCurrentTexture` is logged and mapped to `Lost`. The typed result does not preserve whether the raw exception represented:

- invalid state;
- device loss;
- out-of-memory or internal failure;
- an implementation-specific transient failure;
- another browser exception.

A focused injection or browser matrix is needed before proposing new public variants.

## Browser output cleanup

`SurfaceTexture` calls backend discard when dropped normally without presentation and release during Rust unwinding.

Browser WebGPU implements both operations as no-ops because it cannot explicitly discard the browser canvas texture. Native backends can perform real cleanup.

This is likely platform-owned behavior, not a defect. It does mean tests and applications must not infer native discard semantics from the public drop path on web.

## Native/core configuration state

Core validates a proposed configuration before removing an existing `Presentation`.

### Validation rejection

A validation failure can preserve the earlier accepted presentation. The outer Rust wrapper still caches the rejected request.

Possible state:

```text
core presentation = accepted baseline
public configuration cache = rejected request
core acquisition = baseline presentation
public Texture descriptor = rejected request
```

This can affect observable width, height, format, and usage.

### HAL configuration failure

Later in the core path, the previous presentation is removed before calling HAL configure. If HAL fails, the previous presentation is not restored.

Thus two rejected configure calls can leave different backend states:

- rejection preserving previous accepted presentation;
- rejection leaving the surface unconfigured.

Both currently look like a returned `()` to the public wrapper and publish the request. A future internal result cannot safely be only a success boolean if recovery needs to distinguish these states.

## Presentation and frame ownership

`Queue::present` marks the public `SurfaceTexture` as presented before calling backend present. Backend present also returns `()` at the dispatch boundary; native present errors are routed to the error sink.

Consequently, a present failure does not cause the public texture drop path to discard or release the frame—the public object has already transferred ownership. This appears intentional, but it is another lifecycle point where operation outcome and public ownership state are separate.

Future tests should distinguish:

- successful present;
- present error routed to an error scope;
- ordinary unpresented drop;
- panic-unwind release;
- reconfigure with a live frame;
- surface or device loss after acquisition.

## WebGPU and CTS comparison

The verified CTS source distinguishes:

- unconfigured context: `getConfiguration()` is null and `getCurrentTexture()` throws;
- successful configuration: configuration and texture are observable;
- synchronous type rejection from an initially unconfigured context: configuration remains null;
- validation-error configuration where a context can still become configured.

The inspected canvas configure suite does not cover this sequence:

```text
valid accepted configuration
→ synchronously rejected reconfiguration
→ inspect retained configuration
→ inspect acquired texture
```

It also lists color-space and tone-mapping coverage as unfinished. The wgpu raw-context controls therefore answer wrapper and prior-state questions rather than duplicating a settled CTS case.

## Wasm test infrastructure

The ordinary wasm runtime job builds the GPU test binary with `webgl,exhaust`. The shared initializer removes `BROWSER_WEBGPU` when `webgl` is enabled.

Before this branch:

- browser-WebGPU source received wasm build and clippy coverage;
- runtime initialization selected WebGL;
- no ordinary shared-initializer path executed browser WebGPU through the public Rust backend.

The owned-fork tests remain registered in the ordinary wasm binary but construct a separate explicit `BROWSER_WEBGPU` instance and assert the selected adapter backend. Actual execution must still prove that the Playwright/SwiftShader environment supplies a suitable adapter.

## Owned-fork characterization

File:

```text
tests/tests/wgpu-gpu/create_surface_error.rs
```

Current head: `77c46ce89efab608b1d377b3d6cecf18b006fb72`

Prepared cases:

1. existing unusable-canvas surface-creation error;
2. unconfigured browser surface acquisition returns `Lost` while raw context stays unconfigured;
3. accepted 2×2 baseline presents;
4. rejected 7×5 unsupported color-space request is published publicly;
5. canvas extent mutates to 7×5 before rejection;
6. wgpu reports `Lost`;
7. raw context remains configured and raw acquisition follows resized extent;
8. supported same-surface reconfiguration restores 2×2 and presents;
9. recreated surface plus the same rejected request remains `Lost`;
10. supported configuration on the recreated surface presents.

These assertions characterize source-predicted current behavior. They are not desired permanent regression semantics yet.

## Candidate internal contracts

### Accepted-state disposition

```text
SurfaceInterface::configure(...) -> ConfigureDisposition
```

Potential states:

- `Applied`;
- `AppliedWithDiagnostic`;
- `RejectedPreservingPrevious`;
- `RejectedUnconfigured`.

### Backend-owned accepted configuration

The wrapper could query accepted state instead of publishing an unconditional request cache. This is closer to backend truth but complicates requested-versus-resolved semantics and custom backends.

### Explicit requested and accepted state

Retain a clearly named last-requested value but use separately retained accepted state for texture metadata and recovery. This avoids corrupting descriptors without pretending the request vanished.

### Browser-only typed failure reason

Replace `configure_failed: bool` with a private typed reason. This can improve browser recovery but does not solve native cache divergence by itself.

Do not begin with a public `Surface::configure -> Result` redesign. Browser and core-backed execution should select the smallest viable contract.

## Next probes

### P1 — execute browser tests

Required receipts:

- exact fork head and test identity;
- format and clippy commands;
- browser and adapter information;
- raw and public state before and after each operation;
- same-surface and recreated-surface controls.

### P1 — public-wrapper metadata test

Add a private `surface.rs` unit characterization using a noop device and minimal custom surface, texture, and output-detail implementations. Prove backend accepted state, public cache, and public texture metadata separately.

Do not replace the large source file from truncated content. Use a safe checkout or complete tree/commit edit path.

### P1 — core-backed validation control

Prove with a real core path:

- accepted baseline;
- invalid second request;
- error-scope result;
- retained or cleared presentation;
- acquisition result;
- public metadata;
- later valid recovery.

### P2 — raw rejected reconfiguration

Measure valid baseline followed by raw synchronous rejection. Record whether prior configuration survives and whether resizing or other dictionary processing mutates related state first.

### P2 — acquisition exception matrix

Separate unconfigured invalid state, device loss, out-of-memory/internal errors, and transient implementation exceptions before changing public status variants.

### P2 — examples

Audit `Success`, `Suboptimal`, `Timeout`, `Occluded`, `Outdated`, `Lost`, and `Validation`. Ensure examples do not retry an invalid configuration merely because the typed outcome is `Lost`.

### P3 — cleanup and custom backends

Map discard, release, present failure, unwinding, and custom-backend compatibility before changing dispatch contracts.

## Protocol position

This lane remains outside Delivery Desk #160.

There is no target-executed receipt, selected repair, canonical source-only implementation, accepted disposition, or bounded final gate. Issue #116, Fieldwork PR #126, and owned-fork PR #1 remain the canonical exploration records.

## Promotion gate

Promote only after:

- an executed contradiction or precise documentation/example mismatch;
- exact source and execution receipts;
- at least one negative control;
- one selected owning subsystem and desired contract;
- a source-only candidate branch;
- independent exact-head review tied to issue/input generation;
- explicit authority before upstream contact.

## Stops

- Do not call raw browser conformance failure where wgpu rejected before calling the browser.
- Do not describe the browser state as complete preservation when canvas extent already mutated.
- Do not upgrade authored tests to executed evidence.
- Do not treat a custom wrapper test as proof of native core behavior.
- Do not add a public API compatibility burden before measuring the state benefit.
- Do not contact upstream without explicit authorization.
