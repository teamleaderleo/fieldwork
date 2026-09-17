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
- owned fork test head: `teamleaderleo/wgpu@455a8711984b0166533fa3441d65a9e58777d9ca`

An earlier WebGPU specification SHA did not resolve and has been removed. The CTS pin remains valid.

No compile, browser, native GPU, Playwright, or target test execution is claimed. Evidence is `source-read` or `target-test-prepared` unless stated otherwise.

## Core question

One public operation crosses several independently meaningful states:

```text
caller request
→ local mapping and validation
→ canvas/window mutation
→ raw backend configuration
→ public configuration cache
→ acquisition object/status
→ separately delivered validation/error
→ recovery guidance
```

Public `Surface::configure` calls backend dispatch returning `()`, then caches the request. The wrapper cannot know whether the request was accepted, rejected, partially applied, or applied with a diagnostic.

## Architecture

```text
public Rust API (`wgpu`)
→ native validation and ownership (`wgpu-core`)
→ native graphics interface (`wgpu-hal`)
→ Vulkan / Metal / DX12 / GLES
```

On WebAssembly, the public crate can dispatch directly to browser WebGPU. The goal is truthful public state and recovery across these paths, not identical mechanics.

## Claim-scoped status

| Claim | Evidence class | Exclusion |
| --- | --- | --- |
| Public cache is not acceptance-bound | source-read | no executed reproduction |
| Unsupported browser color space rejects before raw configure | source-read plus target-test-prepared | test unexecuted |
| Canvas extent mutates before later rejection | source-read plus target-test-prepared | test unexecuted |
| Unconfigured browser acquisition maps invalid state to `Lost` | source-read plus target-test-prepared | test unexecuted |
| Zero-sized browser configure is applied with validation | CTS/source-read plus target-test-prepared | test unexecuted |
| Public `Success` may carry a zero-sized error texture | source prediction plus target-test-prepared | exact variant unexecuted |
| Native validation can preserve an earlier presentation | source-read | no core-backed control |
| Public texture metadata can follow rejected cache | source-read risk | wrapper/core controls unexecuted |
| Ordinary wasm initializer does not execute browser WebGPU | source-read | headless adapter unmeasured |

No claim is `target-executed`, `integration-executed`, or `full-gate`.

## Public wrapper state

`Surface` stores a dispatched backend surface and a mutex-protected `SurfaceConfiguration` cache. Public `configure`:

1. invokes backend configure;
2. receives no disposition;
3. stores the request.

`get_configuration()` is therefore last published request state, not demonstrably accepted state.

Successful or suboptimal acquisition constructs the public texture descriptor from this cache. Width, height, format, and usage can diverge from the actual backend texture when accepted state differs.

## Browser configure ordering

Browser WebGPU performs:

1. write requested width and height to HTML/offscreen canvas;
2. validate present mode and alpha mode;
3. map format, usage, color space, and view formats;
4. reject locally unrepresentable values or invoke raw `GPUCanvasContext.configure`;
5. set or clear `configure_failed`.

The canvas can therefore mutate before rejection or panic.

## Browser state A — unconfigured acquisition

Raw WebGPU throws `InvalidStateError` when `getCurrentTexture` is called before configure. The browser backend catches the exception and returns `CurrentSurfaceTexture::Lost`.

Public `Lost` guidance says surface recreation, although configuration is the missing operation.

Native core differs:

- configured surfaces route acquisition errors to their retained device error sink and return `Validation`;
- before successful configuration, no surface error sink exists and the error is fatal by default.

This is a source-confirmed backend difference in public recovery semantics.

## Browser state B — applied with diagnostic

The WebGPU CTS treats zero canvas size as validation, not synchronous rejection.

Raw sequence:

```text
canvas extent has zero dimension
→ configure emits validation
→ configuration dictionary remains installed
→ repair canvas extent without another raw configure
→ getCurrentTexture can work
```

A zero-sized acquisition returns an error texture and emits validation.

Current wgpu source predicts:

```text
Surface::configure returns
validation error scope captures configure error
public cache = zero-sized request
raw context = configured
public acquisition = Success or Suboptimal(error texture)
public texture descriptor = zero-sized request
validation error scope captures acquisition error
```

This contradicts the public documentation's unconditional “zero width or height panics” description on the browser path.

It also proves why validation cannot be equated with rejection: configuration may be installed and later become usable when extent is repaired.

## Browser state C — rejected after partial mutation

For unsupported `ExtendedSrgbLinear`, wgpu rejects locally before raw configure, but only after applying canvas dimensions.

After an accepted 2×2 baseline, a rejected 7×5 request can produce:

```text
raw WebGPU configuration = earlier accepted baseline
canvas extent = 7×5 rejected request
public cache = 7×5 rejected request
configure_failed = true
public acquisition = Lost
raw acquisition = usable at 7×5 extent
```

The prior state is not fully preserved. Configuration dictionary, drawable extent, public cache, and typed status disagree.

A supported same-surface configure clears the failure flag and realigns state. Recreating the surface while retrying the same unsupported request fails again.

## Browser acquisition exceptions

Every thrown raw `getCurrentTexture` exception is logged and mapped to `Lost`. The typed result does not preserve whether the exception represented:

- invalid state;
- device loss;
- out-of-memory or internal failure;
- transient implementation failure;
- another browser exception.

An exception matrix is required before proposing new public variants.

## Native/core state

Core validates before removing an existing `Presentation`.

### Validation rejection

A rejected second configuration can preserve the earlier presentation while the public wrapper caches the request:

```text
core presentation = accepted baseline
public cache = rejected request
core acquisition = baseline
public Texture descriptor = rejected request
```

This can corrupt observable metadata without losing the underlying presentation.

### HAL configuration failure

The old presentation is removed before HAL configure. If HAL fails, the prior presentation is not restored.

Thus rejected configure can mean either:

- previous accepted state remains;
- no accepted state remains.

Both look like returned `()` to the public wrapper.

## Provisional configure taxonomy

Execution may revise the names, but the source already requires more than a boolean:

- `Applied`;
- `AppliedWithDiagnostic`;
- `RejectedUnconfigured`;
- `RejectedPreservingPrevious`;
- `RejectedAfterPartialMutation`.

A public `Result` is not the first step. First measure and choose the smallest internal truth needed by cache, texture metadata, examples, and recovery.

## Frame ownership

Unpresented `SurfaceTexture` drop:

- calls discard normally;
- calls release during Rust unwinding.

Browser discard and release are no-ops. Native backends can perform real cleanup.

`Queue::present` marks the public frame presented before backend present. Native present errors are routed to the error sink instead of returned. Backend outcome and public ownership transfer are therefore separate lifecycle states.

## Shared example framework

The feature-example framework stores its local configuration immediately after `surface.configure` and mutates it before resize configure. It has no accepted-state record.

Outcome policy:

- `Timeout`/`Occluded`: skip;
- `Suboptimal(texture)`: drop usable texture, reconfigure stored request, retry once;
- `Outdated`: reconfigure stored request, retry once;
- `Validation`: unreachable assumption;
- `Lost`: recreate surface, apply stored request, retry once, panic if retry is not success/suboptimal.

Rejected-configuration loop:

```text
configure request is rejected nonfatally
→ example stores request
→ acquisition reports Lost
→ example recreates surface
→ reapplies same request
→ rejection repeats
→ example panics
```

See `artifacts/example-recovery-outcome-audit.md`.

## WebGPU and CTS gaps

Verified CTS covers:

- unconfigured context;
- successful configure;
- synchronous initial rejection;
- validation-error configuration;
- zero-size before and after configure;
- resize invalidating current texture.

The inspected suite does not cover:

```text
valid accepted configuration
→ synchronous rejected reconfiguration
→ inspect retained configuration
→ inspect canvas extent
→ inspect acquired texture
```

Color-space and tone-mapping canvas coverage is also listed as unfinished in the inspected configure suite.

## Wasm test infrastructure

The ordinary wasm runtime job builds with `webgl,exhaust`. The shared initializer removes `BROWSER_WEBGPU` when WebGL is enabled.

The owned-fork cases remain in the normal wasm binary but create an explicit browser-WebGPU instance and assert the adapter backend. Actual execution must prove headless adapter availability.

## Owned-fork cases

Current head: `455a8711984b0166533fa3441d65a9e58777d9ca`

File:

```text
tests/tests/wgpu-gpu/create_surface_error.rs
```

Prepared cases:

1. existing unusable-canvas creation error;
2. unconfigured acquisition maps to `Lost`;
3. zero-sized configure/acquire emits validation while returning configuration/error texture;
4. accepted 2×2 baseline followed by rejected 7×5 partial-mutation path;
5. same-surface supported recovery;
6. recreated-surface invalid retry negative control;
7. recreated-surface supported recovery.

These are characterization assertions, not selected permanent regression semantics.

## Durable artifacts

- `surface-config-rejection-test-plan.md`
- `fork-characterization-log.md`
- `surface-lifecycle-contract-matrix.md`
- `native-public-cache-characterization-plan.md`
- `protocol-aligned-status-and-next-probes.md`
- `example-recovery-outcome-audit.md`
- `zero-size-applied-with-validation.md`

## Next probes

### P1

Execute the three browser cases with exact test identities, error scopes, adapter/browser receipts, raw/public state, and recovery controls.

### P1

Add private public-wrapper metadata characterization using noop device and minimal custom surface/texture/output detail through a safe complete-file edit.

### P1

Build real core-backed validation control for retained presentation, cache, metadata, acquisition, and recovery.

### P2

Measure raw valid-baseline followed by synchronous rejection and separate it from both local pre-rejection and validation-error configuration.

### P2

Inject acquisition exception classes and audit example recovery for every outcome and error texture.

### P3

Measure frame discard/release, present errors, live-frame reconfiguration, and custom-backend compatibility.

## Protocol position

This lane remains outside Delivery Desk #160. There is no target-executed receipt, selected repair, canonical source-only implementation, accepted disposition, or bounded final gate.

## Promotion gate

Promote only after an executed contradiction or precise documentation mismatch, exact receipts, a negative control, selected owner and desired contract, source-only candidate, independent exact-head review tied to input generation, and explicit upstream authority.

## Stops

- Do not call validation synchronous rejection.
- Do not call an error texture usable merely because public acquisition says `Success`.
- Do not describe prior state as fully preserved when extent mutated.
- Do not upgrade authored tests to executed evidence.
- Do not use a custom wrapper test as native proof.
- Do not begin with a breaking public API redesign.
- Do not contact upstream without explicit authorization.
