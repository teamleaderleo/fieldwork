# wgpu portability, diagnostics, and GPU lifecycle

Issue: #116

Programme: #114

State: source reconnaissance

Upstream contact authorized: false

## Exact pins

- released baseline: `wgpu v30.0.0`
- source revision: `gfx-rs/wgpu@2eddc8c7b2fedd4267f5004745a8bc42974e17a0`
- Fieldwork base: `teamleaderleo/fieldwork@d535799f8a9349498687c09211f6aa0fe791330c`

No released binary or browser probe has been executed yet. Findings below are source-confirmed unless stated otherwise.

## In simple words

wgpu has a clear layered architecture:

```text
public Rust API (`wgpu`)
→ validation and resource ownership (`wgpu-core`)
→ native graphics backends (`wgpu-hal`)
→ Vulkan / Metal / DX12 / GLES
```

The same public Rust crate can compile to WebAssembly and delegate to the browser's WebGPU implementation instead of `wgpu-core`. Naga owns shader parsing, validation, and translation. Deno has separate bindings and is also used for WebGPU conformance testing.

The first promising seam is not a confirmed runtime defect. It is a public-contract and diagnostics question around failed browser surface configuration:

- public `Surface::configure` documentation says unsupported formats panic;
- the browser WebGPU adapter deliberately catches browser configuration rejection because a wasm panic would be an unrecoverable abort;
- the adapter stores `configure_failed = true` and makes the next `get_current_texture` return `Lost`;
- a later successful `configure` clears the flag;
- this can preserve application recovery while collapsing “browser rejected this configuration” into the same public status used for an actually lost surface.

That behavior may be the best possible compatibility choice. The research question is whether the public docs, status, logs, examples, and tests make it truthful enough for applications to recover correctly.

## Repository architecture

Source: `AGENTS.md` at the pinned revision.

### `wgpu-hal`

Implements supported native graphics APIs. Backend-specific differences and raw safety contracts live here.

### `wgpu-core`

Implements the WebGPU API model, validation, resource management, and backend-independent ownership. It delegates native operations to `wgpu-hal` and shader translation to Naga.

### `wgpu`

Provides the public Rust API. Native builds generally route through `wgpu-core`. WebAssembly builds can use the browser WebGPU backend directly.

### `naga`

Parses and validates WGSL, GLSL, and SPIR-V and emits backend shader languages or intermediate formats. The project instructions explicitly require checking the WebGPU and WGSL specifications rather than treating conformance-suite expectations as automatically correct.

### `deno_webgpu`

Provides Deno bindings. Project guidance says cross-client problems should usually be fixed in core rather than only in Deno.

### Test surfaces

The repository expects:

- `cargo build`;
- `cargo fmt`;
- `cargo clippy --tests`;
- `cargo xtask test`;
- `cargo xtask cts --backend <backend>` for full validation;
- WebGPU/WGSL specification review alongside CTS.

This is a strong contribution environment: the project has explicit architecture guidance, backend test commands, CTS bookkeeping, changelog rules, and a regular release cadence.

## Public surface lifecycle

Source: `wgpu/src/api/surface.rs` and `wgpu/src/api/surface_texture.rs`.

### Surface ownership

`Surface` stores:

- the dispatched backend surface;
- the latest successful public `SurfaceConfiguration` in a mutex;
- an optional source window/canvas handle retained until after backend surface cleanup.

The handle-source field is explicitly ordered to drop after other fields because some platform surfaces become invalid when the source window is dropped.

### Configuration

Public `Surface::configure`:

1. calls the backend `configure` implementation;
2. then stores a clone of the requested configuration.

The documentation states:

- reconfiguration waits for GPU idle;
- concurrent submissions can cause the internal wait to fail with validation;
- configuration panics when an earlier surface texture remains alive;
- unsupported format or color space panics;
- zero width or height panics.

Because the configuration cache is updated only after the backend call returns, a native panic or nonlocal failure should not publish the new cached configuration. The browser backend is different because it returns normally after recording failure.

### Acquisition result

`Surface::get_current_texture` now returns `CurrentSurfaceTexture`, not a simple `Result`. The public states are:

- `Success(texture)`;
- `Suboptimal(texture)`;
- `Timeout`;
- `Occluded`;
- `Outdated`;
- `Lost`;
- `Validation`.

The API gives applications separate recovery guidance:

- skip `Timeout` and `Occluded`;
- reconfigure `Outdated` or `Suboptimal`;
- recreate surface, or the device when device loss is separately reported, for `Lost`;
- attend to an error scope or uncaptured error for `Validation`.

A successful or suboptimal acquisition constructs the public texture descriptor from the cached configuration. If the backend supplies no texture despite a status that passed the earlier match, the public layer returns `Lost`.

### Unpresented texture cleanup

`SurfaceTexture` tracks whether it was presented.

On drop while unpresented:

- during Rust unwinding, it calls backend `texture_release` as best effort;
- otherwise it calls backend `texture_discard`.

The distinction exists because destroying a swapchain acquisition semaphore during panic cleanup previously caused a failure. This is a useful fault-injection seam: unwinding, ordinary frame abandonment, explicit reconfigure, and process abort have different cleanup opportunities.

## Browser WebGPU surface adapter

Source: `wgpu/src/backend/webgpu.rs`.

### Browser context ownership

`WebSurface` stores:

- an optional browser `GPU` object;
- the canvas or offscreen canvas;
- `GPUCanvasContext`;
- `configure_failed: Cell<bool>`;
- an internal identifier.

The browser backend must operate on a main thread or dedicated worker capable of accessing WebGPU. Surface creation from raw web handles can still panic when the expected canvas cannot be found or the handle type is wrong.

### Failed configuration policy

The adapter treats some browser failures as recoverable application-visible state rather than Rust panic:

- unsupported color spaces that are not advertised by capabilities set `configure_failed = true`, log an error, and return;
- exceptions from `GPUCanvasContext.configure` also set the flag and log an error;
- successful configuration clears the flag.

The source comments give the reason: wasm has no usable `catch_unwind` for this path, so unwrapping a JavaScript configuration exception would cause an uncatchable abort. The code also records a real compatibility case where a browser may advertise a format and still reject it at configuration time.

### Acquisition after failed configuration

When `configure_failed` is set, browser `get_current_texture` returns:

```text
texture: none
status: Lost
```

A JavaScript exception from `getCurrentTexture` is also logged and mapped to `Lost`.

This means `Lost` currently covers at least three distinct application situations:

1. an actual underlying surface loss;
2. a rejected browser configuration;
3. an exception while acquiring the current browser texture.

Logs preserve some distinction, but the typed public status does not.

### Texture discard on the web

Browser `texture_discard` and `texture_release` are no-ops. The source states that the web backend cannot really discard the texture. Therefore ordinary unpresented drop and panic-unwind drop have the same backend effect on browser WebGPU even though native backends may distinguish them.

This is probably browser-owned behavior, not a defect. It should still be included in the lifecycle matrix because an owned application cannot assume native discard semantics in a browser build.

## Historical intent

The changelog records that `Surface::configure` and `Surface::get_current_texture` were changed from fatal behavior to non-fatal behavior in an earlier release.

The merged change that introduced that direction explicitly aimed to let applications recover through error scopes and nonfatal statuses. Review discussion noted an unresolved design tension: some failures are dynamic surface conditions an application should handle, while validation errors should normally indicate application-author mistakes.

The current API has evolved from the earlier generic unknown/other status into richer `CurrentSurfaceTexture` variants. The browser-specific rejected-configuration path still maps to `Lost`.

## Initial candidate questions

### C1 — public documentation versus browser behavior

**Status:** source-confirmed mismatch candidate; not reproduced.

Public `Surface::configure` documentation states unsupported format/color space panics. Browser WebGPU intentionally returns normally, records failure, logs, and later returns `Lost`.

Possible dispositions:

- documentation should state the browser exception and recovery path;
- browser behavior is already documented elsewhere and no change is needed;
- the public API should expose configuration rejection more directly in a future breaking release;
- tests/examples should cover the distinction without changing the API.

This is the first executable probe because it is narrow, user-visible, and clearly intentional in source.

### C2 — `Lost` conflates configuration rejection and loss

**Status:** intentional source behavior; consequence unmeasured.

An application following the public guidance for `Lost` may recreate a surface or device when the actual problem is an unsupported browser configuration that should be changed. Logs provide a clue, but typed state does not.

The key question is whether this causes consequential bad recovery in realistic code or whether ordinary reconfiguration logic already handles it safely.

### C3 — browser capability advertisement can disagree with configure

**Status:** source comment; needs exact browser reproduction.

The backend contains compatibility handling for browsers that advertise a canvas format and later reject it. The lane should determine:

- which released browsers still do this;
- whether it affects only HDR/fp16 formats;
- whether capability re-query changes after failure;
- whether a successful fallback configuration fully clears state;
- whether the logs and statuses are deterministic enough for automation.

### C4 — unpresented surface-texture drop differs by backend

**Status:** source-confirmed architecture difference; no contract gap identified.

Native backends may discard or release an acquired frame; browser WebGPU does neither explicitly. Tests should ensure an application can safely skip frames, unwind, reconfigure, and recover without assuming identical resource behavior.

### C5 — configuration cache after browser rejection

**Status:** source inference; needs probe.

The public `Surface::configure` caches the requested configuration after the backend call returns. The browser backend returns normally even when the browser rejects configuration. Therefore the public surface may cache a configuration that was not accepted by the browser while `configure_failed` forces acquisition to `Lost`.

A later successful fallback configure replaces the cache. Before that fallback, `get_configuration` may report the rejected request as the current configuration.

This may be intentional “last requested configuration” behavior: the public docs say `get_configuration` returns the configuration passed to `configure`, including unresolved automatic values. The probe should determine whether callers can mistake rejected requested state for active state and whether documentation is explicit enough.

## First executable probe

### Browser matrix

Create a minimal wasm application pinned to the released baseline.

For each available Chrome, Firefox, and Safari/WebKit environment:

1. request an adapter and enumerate surface capabilities;
2. select a known supported baseline format/color space;
3. configure and acquire/present a frame;
4. request an unsupported or browser-rejected format/color-space combination;
5. capture panic/abort, logs, error scopes, uncaptured errors, `get_configuration`, and `get_current_texture` result;
6. reconfigure with the supported baseline;
7. acquire and present again;
8. repeat through canvas resize, detach/reattach, and visibility changes where supported.

### Native negative control

Run the equivalent invalid/unsupported configuration against one native backend. Record whether it panics, emits validation, or returns another public state. The purpose is not to demand identical backend mechanics; it is to document the public contract difference precisely.

### Additional negative controls

- supported configuration must remain successful;
- zero-size must remain an application guard case rather than being confused with browser rejection;
- timeout/occlusion must stay distinguishable;
- true device loss, where inducible in a controlled adapter or mock, must remain separate from rejected configuration;
- successful fallback reconfiguration must clear the browser failure state.

## Evidence required before promotion

- released reproduction on at least one browser;
- exact browser and wgpu versions;
- logs, typed status, error-scope behavior, and `get_configuration` result;
- successful-reconfigure negative control;
- public-doc and example inventory;
- current-tree confirmation;
- narrow documentation, test, diagnostic, or API repair shape;
- explicit upstream authorization.

## Rejected claims so far

- No evidence yet that mapping failed browser configuration to `Lost` is incorrect.
- No evidence yet that browser no-op discard leaks resources or violates WebGPU.
- No evidence yet that capability advertisement mismatch is owned by wgpu rather than the browser.
- No evidence yet that a device must be recreated after this `Lost`; public guidance already permits surface-only recreation when the device is not lost.

## Next work

1. Inventory current public surface documentation, examples, and tests for failed browser configuration.
2. Build the released-browser probe.
3. Re-run against the exact source revision.
4. Decide whether C1 or C5 survives as a documentation/test candidate.
5. Expand to native surface-texture abandonment only after the first seam is resolved.
