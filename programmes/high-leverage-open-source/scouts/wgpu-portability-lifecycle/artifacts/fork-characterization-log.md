# wgpu fork characterization log

State: test authored and self-reviewed; not executed

Fieldwork issue: #116

Fieldwork PR: #126

Upstream contact authorized: false

## Exact pins

- upstream/fork base: `gfx-rs/wgpu@2eddc8c7b2fedd4267f5004745a8bc42974e17a0`
- owned fork: `teamleaderleo/wgpu`
- fork branch: `fieldwork/surface-config-rejection-state`
- fork draft PR: `teamleaderleo/wgpu#1`
- fork test head: `af7df0b4011d6e54b75575fe87be885ca2dc87ba`
- `get_configuration` introduction: `gfx-rs/wgpu#8664`, merge `90db08157ccd5a5a25564219f294d023d4253d5a`
- unified acquisition result: `gfx-rs/wgpu#9257`, merge `e4dae053c05c849fc56e923d0cbf23c3730c33e6`

The owned fork's `trunk` exactly matched the source revision already pinned by this lane when the branch was created.

## What was added

The characterization was folded into the existing wasm-only test module:

```text
tests/tests/wgpu-gpu/create_surface_error.rs
```

No new top-level test module or registration file was retained.

The test is registered only when the `webgl` feature is not enabled, because the repository's wasm initializer deliberately removes `BROWSER_WEBGPU` in WebGL test builds.

Both canvases are explicitly sized to 2×2 before surface creation so public configuration dimensions and browser canvas dimensions agree.

## Characterized scenario

The test performs this sequence using the browser WebGPU backend:

1. create a 2×2 canvas and surface;
2. request a compatible adapter, device, and queue;
3. obtain and apply the supported default configuration;
4. acquire and present a baseline frame;
5. clone the baseline and set `SurfaceColorSpace::ExtendedSrgbLinear`;
6. prove that color space is absent from the browser surface capabilities;
7. call `Surface::configure` with the unsupported request;
8. record that public `get_configuration()` publishes the rejected request;
9. record that acquisition returns `CurrentSurfaceTexture::Lost`;
10. create another surface and prove that repeating the same unsupported request remains `Lost`;
11. apply the supported baseline to the new surface;
12. acquire and present successfully, proving that the device and browser implementation remain usable.

The test currently asserts existing behavior. It is a characterization test, not yet the desired regression assertion for an accepted repair.

## Self-review corrections

The first draft used a separate `surface_configure_rejection.rs` module. That was removed because `create_surface_error.rs` is already the repository's wasm-only home for surface failures and already has the correct registration gate.

The second review added:

- explicit `not(feature = "webgl")` registration and compilation gates;
- explicit canvas dimensions;
- a successful baseline presentation before rejection;
- a successful fallback presentation after rejection;
- a capability negative control proving the chosen color space is unsupported;
- a recreated-surface control proving that recreation alone cannot correct an invalid configuration.

## Execution status

The test has **not** been executed.

After opening fork draft PR #1 at head `af7df0b4011d6e54b75575fe87be885ca2dc87ba`:

- GitHub reported no pull-request workflow runs for the head;
- GitHub reported no commit statuses for the head;
- the available local container could not resolve GitHub to clone the repository;
- no compile, clippy, wasm-runner, or browser result is claimed.

The next valid evidence step is an actual repository runner execution, preferably:

```text
cargo fmt --check
cargo clippy --target wasm32-unknown-unknown --tests --features glsl,spirv
cargo xtask test-wasm -- <exact generated test filter>
```

The exact `test-wasm` filter must be obtained from the repository test listing rather than guessed.

## Historical precedent

### `get_configuration` was introduced as a cache accessor

`gfx-rs/wgpu#8664` added `Surface::get_configuration()` in December 2025 to better match WebGPU. The change simply returned `self.config.lock().clone()` and listed testing as `None`.

That PR did not establish semantics for:

- requested versus accepted configuration;
- failed nonfatal configuration;
- prior accepted configuration followed by rejection;
- backend-specific failure containment.

The later HDR work documented requested-versus-resolved values, but the acceptance question remains distinct.

### `Lost` was designed as a recreation signal

`gfx-rs/wgpu#9257` replaced the former `Result<SurfaceTexture, SurfaceError>` API with `CurrentSurfaceTexture` in March 2026 because surface errors were easy to ignore and recovery guidance was unclear.

The merged docs define `Lost` as requiring surface recreation, or device/resource recreation when the device itself is lost. In review, the author stated that on `Lost` recovery is by creating rather than reconfiguring.

The same change introduced the shared example behavior that recreates a surface and reapplies the same stored configuration.

Therefore mapping a rejected configuration to `Lost` crosses two independently introduced contracts:

1. `get_configuration()` presents the wrapper cache as current configuration;
2. `Lost` tells callers that surface recreation is the corrective action.

For an unsupported configuration, neither statement is sufficient:

- the cached request was not applied;
- recreating the surface does not make the request supported.

## Architecture consequence

The public wrapper cannot fix publication locally because `dispatch::SurfaceInterface::configure` returns `()`.

Any acceptance-bound repair at the dispatch boundary touches:

- the native core implementation;
- the browser WebGPU implementation;
- the custom-backend interface and its implementors.

This raises the bar above a browser-only boolean patch. The internal result needs to distinguish at least:

- configuration applied normally;
- configuration applied while a validation diagnostic is emitted where permitted;
- configuration rejected with no usable configured state;
- fatal/unrecoverable control flow.

A simple success boolean may erase WebGPU's distinction between synchronous rejection and validation-error configuration.

## Current decision

Do not begin with a public `Surface::configure -> Result` redesign.

Proceed in this order:

1. execute the characterization on the owned fork;
2. confirm the exact state after supported configuration followed by rejection;
3. add a native/core injected-failure control if a portable seam is available;
4. decide whether a documentation/example-only patch is sufficient;
5. otherwise prototype a private dispatch acceptance classification;
6. convert the characterization assertion into the desired regression assertion;
7. request explicit upstream-contact authorization before opening anything against `gfx-rs/wgpu`.

## Adjacent wgpu work worth examining

Without diluting this first packet, the lane should continue source/history reconnaissance around:

- custom backend compatibility when dispatch contracts change;
- configuration recovery after device loss versus surface-only failure;
- `Suboptimal` and `Outdated` example correctness;
- browser `getCurrentTexture` exceptions currently collapsed into `Lost`;
- capability-probe lifecycle when `OffscreenCanvas` is unavailable;
- surface-texture discard/release differences across browser and native backends;
- tests for accepted state after a failed reconfiguration, not only failure before first configuration.

These remain research leads, not claimed defects or separate campaigns.
