# wgpu portability, diagnostics, and GPU lifecycle

Issue: #116

Programme: #114

State: source and standards reconnaissance

Upstream contact authorized: false

## Exact pins

- released baseline: `wgpu v30.0.0`
- source revision: `gfx-rs/wgpu@2eddc8c7b2fedd4267f5004745a8bc42974e17a0`
- nonfatal-surface merge: `gfx-rs/wgpu@ebdd958d4b0d9fc3f8c7324ad2db4cd7eb8041d5`
- HDR/browser-surface merge: `gfx-rs/wgpu@3fb225a9c6240bd7e9db3d202410db6d894368ec`
- WebGPU specification source: `gpuweb/gpuweb@134c29d8ac3e4fb20c96028de95cf1e92d1a5192`
- WebGPU CTS source: `gpuweb/cts@dc20b8682aa71ff31f135de6ae7f8acaa2e16383`
- Fieldwork base: `teamleaderleo/fieldwork@d535799f8a9349498687c09211f6aa0fe791330c`

No released binary or browser probe has been executed yet. Findings below are source-, history-, specification-, or CTS-confirmed unless stated otherwise.

## In simple words

wgpu has a clear layered architecture:

```text
public Rust API (`wgpu`)
→ validation and resource ownership (`wgpu-core`)
→ native graphics backends (`wgpu-hal`)
→ Vulkan / Metal / DX12 / GLES
```

The same public Rust crate can compile to WebAssembly and delegate to the browser's WebGPU implementation instead of `wgpu-core`. Naga owns shader parsing, validation, and translation. Deno has separate bindings and is also used for WebGPU conformance testing.

The first seam is now narrower than a generic browser-error question:

> `Surface::configure` publishes the requested configuration into public wrapper state even though the dispatched backend returns no success value proving that configuration was accepted.

That matters because both current native error handling and the browser WebGPU compatibility path can report configuration failure without unwinding out of `Surface::configure`:

- the native core backend routes some failures through the device error sink and returns;
- the browser backend catches a JavaScript configuration exception, records `configure_failed = true`, logs, and returns;
- the public wrapper then stores `Some(config.clone())` unconditionally;
- `Surface::get_configuration()` can therefore describe requested state that was not applied;
- browser acquisition then reports `CurrentSurfaceTexture::Lost` until a successful reconfiguration.

The browser behavior prevents an unrecoverable wasm abort and is intentionally useful. The likely gap is not “make it panic again.” The question is whether acceptance, published configuration state, typed terminal status, examples, and tests agree well enough for correct recovery.

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
- a public configuration cache in a mutex;
- an optional source window/canvas handle retained until after backend surface cleanup.

The handle-source field is explicitly ordered to drop after other fields because some platform surfaces become invalid when the source window is dropped.

### Configuration publication

Public `Surface::configure` currently:

1. calls the backend `configure` implementation, whose dispatch contract returns `()`;
2. stores a clone of the requested configuration in the public cache.

The wrapper therefore knows only that the backend call returned. It does not know that the backend applied the configuration.

The documentation states:

- reconfiguration waits for GPU idle;
- concurrent submissions can cause the internal wait to fail with validation;
- configuration panics when an earlier surface texture remains alive;
- unsupported format or color space panics;
- zero width or height panics.

Those statements no longer describe every backend path. Native nonfatal error routing and browser exception containment can both return control after a failed configure.

### Configuration observation

`Surface::get_configuration()` returns the wrapper cache and describes it as the current configuration. It also correctly notes that automatic values are returned as requested rather than resolved.

The unresolved semantic question is different:

- **requested values versus resolved values** is documented;
- **requested configuration versus accepted configuration** is not.

The public cache is not currently acceptance-bound.

### Acquisition result

`Surface::get_current_texture` returns `CurrentSurfaceTexture` with:

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
- recreate the surface, or the device when device loss is separately reported, for `Lost`;
- attend to an error scope or uncaptured error for `Validation`.

A successful or suboptimal acquisition constructs the public texture descriptor from the cached configuration. If a backend supplies no texture despite a status that passed the earlier match, the public layer returns `Lost`.

### Unpresented texture cleanup

`SurfaceTexture` tracks whether it was presented.

On drop while unpresented:

- during Rust unwinding, it calls backend `texture_release` as best effort;
- otherwise it calls backend `texture_discard`.

The distinction exists because destroying a swapchain acquisition semaphore during panic cleanup previously caused a failure. This remains a later fault-injection seam: unwinding, ordinary frame abandonment, explicit reconfigure, and process abort have different cleanup opportunities.

## Native nonfatal history

Sources: wgpu issue 3586, wgpu issue 5382, and the nonfatal-surface merge pinned above.

The project explicitly moved away from unconditional fatal surface errors because real applications could not recover from:

- device loss during configuration or acquisition;
- drivers that advertised presentation support but failed swapchain creation;
- surface failures where trying another adapter or surface was reasonable.

Maintainer discussion favored making errors nonfatal and then addressing fallout incrementally. Review also identified an unresolved classification problem:

- a validation error usually means application-author error;
- a surface failure can be a dynamic platform condition that the application must handle;
- the implementation may know the immediate error while the public status does not preserve it;
- after some failures, the actual state of the surface may still be unknown.

The merged native implementation routes configure errors through the device error sink and returns from the backend `configure` method. Because the public dispatch signature has no acceptance result, the outer `Surface::configure` then caches the requested configuration even on this nonfatal failure path.

This means the configuration-publication question is not browser-only. The browser path makes it easier to reproduce, but the architectural seam is shared.

## Browser WebGPU surface adapter

Source: `wgpu/src/backend/webgpu.rs` and the HDR/browser-surface merge pinned above.

### Browser context ownership

`WebSurface` stores:

- an optional browser `GPU` object;
- the canvas or offscreen canvas;
- `GPUCanvasContext`;
- `configure_failed: Cell<bool>`;
- an internal identifier.

The browser backend must operate on a main thread or dedicated worker capable of accessing WebGPU. Surface creation from raw web handles can still panic when the expected canvas cannot be found or the handle type is wrong.

### Empirical capability probe

The browser backend now probes `rgba16float` canvas support using a throwaway 1×1 `OffscreenCanvas` after device creation.

This was added because a browser could list the format but throw when asked to configure it. The result is cached process-wide, and unsupported browsers stop advertising `Rgba16Float` after the probe.

That is a strong compatibility design:

- it tests capability rather than sniffing browser versions;
- it automatically begins advertising support when the browser implementation improves;
- it prevents a known unrecoverable wasm panic path for ordinary capability-driven callers.

### Failed configuration policy

The adapter treats some browser failures as recoverable application-visible state rather than Rust panic:

- unsupported color spaces that are not advertised by capabilities set `configure_failed = true`, log an error, and return;
- exceptions from `GPUCanvasContext.configure` also set the flag and log an error;
- successful configuration clears the flag.

The source comments give the reason: wasm has no usable `catch_unwind` for this path, so unwrapping a JavaScript configuration exception would cause an uncatchable abort.

### Acquisition after failed configuration

When `configure_failed` is set, browser `get_current_texture` returns:

```text
texture: none
status: Lost
```

A JavaScript exception from `getCurrentTexture` is also logged and mapped to `Lost`.

`Lost` therefore covers at least three distinct situations:

1. an actual underlying surface loss;
2. a rejected browser configuration;
3. an exception while acquiring the current browser texture.

Logs preserve some distinction, but the typed public status does not.

### Texture discard on the web

Browser `texture_discard` and `texture_release` are no-ops. The source states that the web backend cannot really discard the texture. Therefore ordinary unpresented drop and panic-unwind drop have the same backend effect on browser WebGPU even though native backends may distinguish them.

This is probably browser-owned behavior, not a defect. It remains part of the lifecycle matrix because an application cannot assume native discard semantics in a browser build.

## WebGPU specification and CTS comparison

Sources: the pinned `gpuweb/gpuweb` and `gpuweb/cts` revisions.

The raw WebGPU canvas contract distinguishes several cases that the wgpu wrapper currently combines.

### Before configuration

The CTS asserts:

- `getConfiguration()` returns `null`;
- `getCurrentTexture()` throws `InvalidStateError`.

### Successful configuration

After a valid configure:

- `getConfiguration()` returns a populated configuration;
- defaults are observable in the returned value;
- `getCurrentTexture()` succeeds.

### Synchronous rejected configuration

For a format rejected with `TypeError`, the CTS asserts:

- `configure()` throws;
- `getConfiguration()` remains `null`;
- `getCurrentTexture()` remains invalid.

This provides the key reference point: raw WebGPU does not publish a rejected synchronous configuration as current state.

### Validation-error configuration

The CTS also distinguishes invalid usages that generate a device validation error rather than a synchronous type error. In those cases, the canvas may still become configured and expose the requested usage.

Therefore a future wgpu repair must not reduce all diagnostics to a single boolean without preserving this distinction. The useful question is whether the backend established usable configured state, not merely whether any error was reported.

### `getConfiguration()` values

The WebGPU contract returns originally supplied supported-member values after successful configuration. This supports wgpu returning `Auto` or other requested values rather than resolved backend values.

It does **not** establish that rejected requested values should be reported as current configuration.

## Current shared example behavior

Source: `examples/features/src/framework.rs` at the pinned wgpu revision.

The shared example wrapper handles `CurrentSurfaceTexture::Lost` by:

1. recreating the surface;
2. configuring it with the same locally cached `SurfaceConfiguration`;
3. immediately acquiring again;
4. panicking if the second acquisition is not `Success` or `Suboptimal`.

This is reasonable for actual surface loss when the configuration remains valid.

It is not a recovery strategy for rejected configuration:

- browser configure rejects the configuration;
- acquisition returns `Lost`;
- the example recreates the surface;
- it retries the same rejected configuration;
- the backend records failure again;
- acquisition returns `Lost` again;
- the example panics.

The recent HDR/browser-surface change updated the example's configuration shape but did not adjust this recovery branch.

This establishes a concrete user-facing consequence in repository-owned example code. It is still source reasoning until executed, but it is stronger than a documentation-only mismatch.

## Refined candidate findings

### F1 — configuration publication is not tied to backend acceptance

**Status:** source-, history-, specification-, and CTS-supported; runtime reproduction required.

The public wrapper caches requested configuration after a `()` backend call. Native and browser backends can report failure nonfatally and return. Public `get_configuration()` may then report requested-but-unapplied state as current.

This is the strongest candidate because it spans:

- the public API wrapper;
- native nonfatal error routing;
- browser exception containment;
- WebGPU canvas semantics;
- example recovery behavior.

### F2 — public configure documentation does not describe the nonfatal browser path

**Status:** source-confirmed documentation mismatch; consequence now identified.

The docs promise panic for unsupported format/color space. The browser path intentionally returns, logs, and defers visible failure to `Lost`.

Documentation should at least describe the backend-specific nonfatal path if the implementation remains unchanged.

### F3 — `Lost` conflates rejected configuration and actual loss

**Status:** intentional source behavior; recovery consequence identified in shared examples.

A new public status variant may eventually be useful, but it is not the first repair. A smaller change can first align configuration publication, documentation, tests, and example recovery.

### F4 — shared examples retry a rejected configuration as though the surface were lost

**Status:** source-confirmed control-flow consequence; execution required.

The example should not blindly repeat the same configuration for every `Lost` unless it can prove that configuration was accepted previously or remains capability-valid.

Possible minimal responses include:

- re-query capabilities and select a supported fallback before retrying;
- distinguish startup/configuration rejection from later surface loss in wrapper state;
- emit a terminal diagnostic instead of a misleading recreation loop;
- use a purpose-built browser regression example rather than changing every shared example immediately.

### F5 — browser capability advertisement can still disagree with configure

**Status:** historical real-browser evidence and defensive current code; current-browser reproduction required.

The empirical fp16 probe substantially reduces this problem. The remaining path is still needed for:

- unavailable `OffscreenCanvas` probe environments;
- unsupported manually requested color spaces;
- future browser/configuration disagreements;
- exceptions from `getCurrentTexture` itself.

## What should be done

### Tier 1 — execute and lock the contract

Build a minimal wgpu wasm fixture and one native negative control.

The browser fixture must record:

1. a supported baseline configure and successful frame;
2. public `get_configuration()` after success;
3. an intentionally unsupported browser color-space request that bypasses capability selection;
4. whether `configure()` returns or aborts;
5. logs and any error callbacks;
6. public `get_configuration()` after rejection;
7. `get_current_texture()` result;
8. recreation plus same-config retry result;
9. fallback supported reconfiguration;
10. successful acquisition after fallback.

Use the unsupported web color-space path first because it is deterministic in wgpu source and does not depend on a particular browser still misadvertising fp16 support.

The native control should force or inject a recoverable `surface_configure` failure under an error scope and inspect the public cache before and after.

### Tier 2 — likely narrow repair

If F1 reproduces, prefer an internal acceptance signal before a breaking public API redesign.

Candidate shape:

```text
dispatch backend configure
→ returns applied / rejected classification internally
→ public Surface cache updates only when applied
→ existing public configure signature can remain unchanged initially
```

The exact return type must preserve the distinction between:

- applied with no diagnostic;
- applied while a validation diagnostic is emitted where WebGPU semantics allow it;
- rejected and not configured;
- fatal/unrecoverable paths.

A simple `bool` may be insufficient. The first patch can be test/documentation-only if maintainers prefer to settle semantics before touching dispatch.

### Tier 3 — documentation and example alignment

Independently of an internal acceptance change:

- document that browser configuration rejection can be contained and surfaced later as `Lost`;
- clarify whether `get_configuration()` means last requested or last accepted configuration;
- document that `Lost` can arise from rejected browser configuration;
- add a browser regression test covering successful fallback reconfiguration;
- prevent the shared example framework from presenting same-config recreation as a universal `Lost` recovery strategy.

### Tier 4 — larger API discussion only with evidence

Do not begin with:

- changing public `Surface::configure` to return `Result`;
- adding several new public `CurrentSurfaceTexture` variants;
- redesigning all surface errors;
- requiring identical native and browser mechanics.

Those may be valid future directions, but the project already has historical design tension around validation sinks, dynamic platform failure, and unknown surface state. A minimized reproduction plus narrow tests should lead the API discussion.

## Probe matrix

### Browser matrix

Run the released baseline and exact source revision in available Chrome, Firefox, and Safari/WebKit environments.

For each:

1. request an adapter and enumerate surface capabilities;
2. configure a supported baseline and present one frame;
3. record `get_configuration()`;
4. request an unsupported web color space;
5. record return/abort, logs, callbacks, cache, and acquisition status;
6. recreate and retry the same rejected config as the shared example does;
7. reconfigure with the supported baseline;
8. acquire and present again;
9. repeat after resize, detach/reattach, and visibility changes where supported.

### Native negative control

Run one backend with an injected or artificial recoverable configure failure. Record:

- error-scope or uncaptured-error delivery;
- whether the surface remains configured with an earlier valid configuration;
- what `get_configuration()` reports;
- whether acquisition can continue from the earlier configuration;
- whether another adapter or recreated surface succeeds.

### Additional controls

- supported configuration must remain successful;
- zero-size remains an application guard case;
- timeout and occlusion remain distinguishable;
- true device loss remains separate from rejected configuration;
- successful fallback reconfiguration clears browser failure state;
- a validation diagnostic that still yields configured WebGPU state must not be misclassified as rejection.

## Promotion gate

A campaign or candidate upstream packet requires:

- released reproduction on at least one browser or native backend;
- exact browser, OS, adapter, backend, and wgpu versions;
- source-tree confirmation;
- logs, typed status, error-scope behavior, and configuration-cache result;
- successful-fallback negative control;
- minimized fixture using generated content;
- likely owner in public API, dispatch, browser backend, core backend, examples, or docs;
- regression-test location and command;
- explicit upstream authorization.

## Useful negative outcomes

Retain any of:

- evidence that public cache semantics are deliberately “last requested” and docs are sufficient;
- a browser compatibility matrix showing fallback recovery is already reliable;
- proof that the shared example path cannot encounter configuration-rejection `Lost` in supported usage;
- a Botany Sim adapter rule to retain its own accepted renderer configuration;
- a documentation-only correction;
- evidence that the target is healthy and application-owned state is the right repair.

## Rejected claims so far

- No executed evidence yet proves `get_configuration()` returns a rejected config, though source control flow strongly predicts it.
- No evidence yet that mapping failed browser configuration to `Lost` is itself incorrect.
- No evidence yet that browser no-op discard leaks resources or violates WebGPU.
- No evidence yet that current browsers still misadvertise fp16 after the new empirical probe.
- No evidence yet that a public breaking API change is needed.
- No evidence yet that a device must be recreated after configuration-rejection `Lost`.

## Current decision

Proceed with F1/F4 as the first executable unit:

> Prove whether requested configuration is published after backend rejection, then prove whether the repository's documented/example recovery path can distinguish and recover from it.

The expected first upstream-sized result, if reproduced, is a narrow regression-test and documentation packet, possibly followed by an internal dispatch acceptance signal. It is not yet a public API redesign or defect report.

## Next work

1. Add the minimal released-baseline wasm fixture.
2. Execute the deterministic unsupported-color-space path.
3. Capture cache and `Lost` behavior before and after supported fallback.
4. Add a native injected-failure control.
5. choose among no change, docs/tests, example recovery, internal acceptance signal, or broader API discussion.
