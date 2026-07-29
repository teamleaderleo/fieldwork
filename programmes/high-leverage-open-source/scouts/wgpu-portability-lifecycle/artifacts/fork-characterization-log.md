# wgpu fork characterization log

State: browser characterization authored and repeatedly self-reviewed; not executed

Fieldwork issue: #116

Fieldwork PR: #126

Upstream contact authorized: false

## Exact pins

- upstream/fork base: `gfx-rs/wgpu@2eddc8c7b2fedd4267f5004745a8bc42974e17a0`
- owned fork: `teamleaderleo/wgpu`
- fork branch: `fieldwork/surface-config-rejection-state`
- fork draft PR: `teamleaderleo/wgpu#1`
- fork test head: `38c9498bdae8f0ddfdc6a04c6d763ce889f3f5ad`
- `get_configuration` introduction: [wgpu pull request 8664](https://redirect.github.com/gfx-rs/wgpu/pull/8664), merge `90db08157ccd5a5a25564219f294d023d4253d5a`
- unified acquisition result: [wgpu pull request 9257](https://redirect.github.com/gfx-rs/wgpu/pull/9257), merge `e4dae053c05c849fc56e923d0cbf23c3730c33e6`
- nonfatal surface errors: [wgpu pull request 6253](https://redirect.github.com/gfx-rs/wgpu/pull/6253), merge `ebdd958d4b0d9fc3f8c7324ad2db4cd7eb8041d5`
- HDR/browser rejection containment: [wgpu pull request 9658](https://redirect.github.com/gfx-rs/wgpu/pull/9658), merge `3fb225a9c6240bd7e9db3d202410db6d894368ec`

The owned fork's `trunk` exactly matched the source revision already pinned by this lane when the branch was created.

## What was added

The characterization remains in the existing wasm-only surface-error module:

```text
tests/tests/wgpu-gpu/create_surface_error.rs
```

No new top-level test module or standalone external harness was retained.

The current test now deliberately runs inside the repository's ordinary wasm test binary while constructing a second, explicit browser-WebGPU instance for the characterization.

It does not use the shared `initialize_instance` helper for the subject under test because that helper removes `BROWSER_WEBGPU` whenever the runner's `webgl` feature is enabled.

The test asserts that the selected adapter is exactly `Backend::BrowserWebGpu`; a WebGL fallback must fail rather than produce misleading evidence.

## Characterized scenario

The test performs this sequence:

1. create an explicit browser-WebGPU instance;
2. create a 2×2 canvas and retain its raw `GPUCanvasContext`;
3. create a wgpu surface over that canvas;
4. request a compatible browser-WebGPU adapter, device, and queue;
5. assert the adapter backend is `BrowserWebGpu`;
6. obtain and apply the supported default configuration;
7. acquire and present a baseline frame;
8. confirm both public `get_configuration()` and raw `getConfiguration()` report configured state;
9. clone the baseline and set `SurfaceColorSpace::ExtendedSrgbLinear`;
10. prove that color space is absent from browser surface capabilities;
11. call `Surface::configure` with the unsupported request;
12. record that public `get_configuration()` publishes the rejected request;
13. record that wgpu acquisition returns `CurrentSurfaceTexture::Lost`;
14. confirm the raw browser context remains configured;
15. acquire and destroy a raw browser canvas texture, proving the underlying context remains usable;
16. apply the supported baseline to the same wgpu surface and present successfully;
17. create another surface and prove that repeating the unsupported request remains `Lost`;
18. apply the supported baseline to the recreated surface and present successfully.

The test currently asserts existing behavior. It is a characterization test, not yet the desired regression assertion for an accepted repair.

## Why the raw-context control matters

The selected unsupported color space is rejected inside wgpu's browser mapping before `GPUCanvasContext.configure` is called.

After a valid baseline, the raw browser context therefore remains configured with the baseline. The current wgpu result is still `Lost` because the backend's `configure_failed` flag overrides acquisition.

The predicted state is:

```text
raw browser configuration = earlier accepted baseline
raw browser acquisition = usable
wgpu public cache = rejected request
wgpu typed acquisition = Lost
same-surface supported configuration = recovery
surface recreation + same rejected request = failure again
```

This distinguishes wrapper-owned failure state from actual browser surface loss.

## Self-review corrections

The branch has gone through several correction passes:

1. Removed a separate `surface_configure_rejection.rs` module and folded the case into the existing surface-error module.
2. Added explicit 2×2 canvas dimensions.
3. Added successful baseline and fallback presentations.
4. Added a capability negative control.
5. Added a recreated-surface control.
6. Added raw `GPUCanvasContext.getConfiguration()` and `getCurrentTexture()` controls.
7. Added same-surface supported recovery, distinct from surface recreation.
8. Removed an unnecessary canvas clone that could have triggered clippy.
9. Discovered that compile-time `not(feature = "webgl")` gating would silently exclude the test from `cargo xtask test-wasm`.
10. Removed that gate and added a local display-handle shim plus an explicit `BROWSER_WEBGPU` instance.
11. Added an adapter-backend assertion so the test cannot silently run against WebGL.

## Wasm runner finding

The repository's CI `wasm-test` job executes:

```text
cargo xtask test-wasm
```

The runner builds `wgpu-test` for `wasm32-unknown-unknown` with `webgl,exhaust`. The shared test initializer then subtracts `BROWSER_WEBGPU` whenever `webgl` is enabled as a workaround for Cargo feature propagation.

The test macro exports the browser test entry point in that same WebGL-enabled build, and Playwright launches Chromium with `--enable-unsafe-swiftshader`.

The practical result before this branch was:

- browser WebGPU code received wasm clippy/build coverage;
- the shared runtime initializer selected WebGL;
- no ordinary repository-native browser-WebGPU runtime test exercised the public Rust backend path.

The current characterization works around the initializer demotion locally rather than introducing a second runner. Actual execution must still prove that headless Chromium supplies a browser-WebGPU adapter in this environment.

## Execution status

The test has **not** been executed.

For fork head `38c9498bdae8f0ddfdc6a04c6d763ce889f3f5ad`:

- GitHub has not produced pull-request workflow runs or commit statuses;
- Actions appear unavailable or disabled on the fork;
- the available local container has no Rust toolchain;
- the container also cannot resolve GitHub for cloning or dependency installation;
- no compile, rustfmt, clippy, wasm-runner, Playwright, or browser result is claimed.

The next valid commands in a runnable checkout are:

```text
cargo fmt --check
cargo clippy --target wasm32-unknown-unknown --tests --features glsl,spirv
cargo xtask test-wasm --list
cargo xtask test-wasm -- <exact nextest filter for rejected_browser_configuration_is_published_and_recoverable>
```

The exact filter should be copied from `--list`, not guessed.

## Historical precedent

### `get_configuration` was introduced as a cache accessor

[wgpu pull request 8664](https://redirect.github.com/gfx-rs/wgpu/pull/8664) added `Surface::get_configuration()` in December 2025 to better match WebGPU. The change simply returned `self.config.lock().clone()` and listed testing as `None`.

That pull request did not establish semantics for:

- requested versus accepted configuration;
- failed nonfatal configuration;
- prior accepted configuration followed by rejection;
- backend-specific failure containment.

### `Lost` was designed as a recreation signal

[wgpu pull request 9257](https://redirect.github.com/gfx-rs/wgpu/pull/9257) replaced the former `Result<SurfaceTexture, SurfaceError>` API with `CurrentSurfaceTexture` in March 2026 because surface errors were easy to ignore and recovery guidance was unclear.

The merged docs define `Lost` as requiring surface recreation, or device/resource recreation when the device itself is lost. Review discussion explicitly states that `Lost` recovery is by creating rather than reconfiguring.

The browser rejected-configuration sentinel added later therefore reuses a status whose recovery contract does not fit the failure.

### Nonfatal surface errors anticipated fallout

[wgpu issue 3586](https://redirect.github.com/gfx-rs/wgpu/issues/3586) and [wgpu pull request 6253](https://redirect.github.com/gfx-rs/wgpu/pull/6253) deliberately moved configuration and acquisition errors away from unconditional fatal handling.

Maintainer discussion already identified unresolved distinctions among:

- application validation mistakes;
- driver or end-user conditions;
- a known operation failure with unknown resulting surface state;
- failures that applications should handle dynamically;
- errors appropriate for an error sink versus a typed result.

The current lane is concrete fallout from that earlier, explicit tradeoff.

## Stronger native/core finding

The native core path validates a proposed configuration before removing the existing accepted `Presentation`.

A validation failure can therefore leave the old core presentation active while the outer public wrapper caches the rejected request.

Public `get_current_texture` later builds its exposed `SurfaceTexture` descriptor from the public cache, while core acquisition is based on the older accepted presentation.

This creates a source-supported risk that public texture metadata can describe the rejected request rather than the actual acquired surface texture.

The cases to test include rejected changes to:

- width or height;
- format;
- usage;
- color space;
- view formats.

This is now the highest-value native control. It is distinct from native HAL configuration failure, where core removes the old presentation before the HAL call and does not restore it after failure.

## Architecture consequence

The public wrapper cannot acceptance-bind its cache locally because `dispatch::SurfaceInterface::configure` returns `()`.

Any repair may affect:

- native core dispatch;
- browser WebGPU dispatch;
- custom backend implementations;
- public texture descriptor construction;
- `get_configuration()` semantics;
- `CurrentSurfaceTexture` recovery guidance.

A binary success value is probably insufficient. At minimum, measured states may include:

- applied normally;
- applied with a validation diagnostic;
- rejected while preserving a previous accepted configuration;
- rejected with no accepted configuration remaining;
- fatal or non-returning control flow.

## Current decision

Do not begin with a public `Surface::configure -> Result` redesign.

Proceed in this order:

1. execute the browser characterization;
2. add a native/core public-metadata control for validation failure preserving the old presentation;
3. confirm whether texture metadata diverges after that failure;
4. add a separate HAL-failure control if an injectable surface seam is practical;
5. decide whether documentation/example alignment alone can resolve the user-facing consequence;
6. otherwise prototype a private dispatch disposition;
7. convert characterization assertions into desired regression assertions only after semantics are chosen;
8. request explicit upstream-contact authorization before opening anything against the upstream wgpu repository.

## Adjacent wgpu work worth examining

- custom backend compatibility when dispatch contracts change;
- browser `getCurrentTexture` exceptions currently collapsed into `Lost`;
- error-scope routing for locally detected browser validation failures;
- capability-probe lifecycle when `OffscreenCanvas` is unavailable;
- `Suboptimal` and `Outdated` example correctness;
- accepted state after failed reconfiguration;
- surface-texture discard/release differences across browser and native backends;
- device-loss versus surface-loss recovery;
- the absence of routine browser-WebGPU runtime coverage in the current wasm harness.

These remain research leads, not separate defect claims or upstream proposals.
