# Zero-size browser surface configuration

State: specification/CTS- and source-supported; owned-fork test prepared; not executed

Fieldwork issue: #116

Owned fork head: `teamleaderleo/wgpu@455a8711984b0166533fa3441d65a9e58777d9ca`

Upstream contact authorized: false

## Public documentation expectation

Public `Surface::configure` documentation states that zero width or height panics.

That describes native validation/default-fatal behavior, but it does not match the inspected browser-WebGPU path.

## Raw WebGPU rule

The verified CTS canvas configuration case treats a zero-sized canvas as a validation error rather than a synchronous configuration rejection.

The tested raw sequence is:

```text
canvas dimension = 0
→ GPUCanvasContext.configure emits validation
→ configuration dictionary remains installed
→ canvas dimension is repaired without another configure call
→ getCurrentTexture works
```

A zero-sized texture acquisition itself produces a validation error and an error texture whose zero dimension remains observable.

This is not `RejectedUnconfigured`. It is closer to `AppliedWithDiagnostic` plus an unusable current extent.

## Current wgpu browser source prediction

The browser backend:

1. writes `config.width` and `config.height` to the canvas;
2. maps the configuration;
3. calls raw `GPUCanvasContext.configure`;
4. sees no JavaScript exception for this validation-error case;
5. clears `configure_failed`;
6. returns `()`;
7. allows the public wrapper to cache the zero-sized request.

On acquisition, raw `getCurrentTexture` can return an error texture while the validation error is delivered through the browser device error channel. Since the JavaScript call returned a texture rather than throwing, wgpu can report `Success` and construct its public descriptor from the zero-sized cache.

Predicted public state:

```text
Surface::configure returns
validation error scope captures configure error
Surface::get_configuration = zero-sized request
raw context = configured
Surface::get_current_texture = Success(error texture)
public texture width/height = zero-sized request
validation error scope captures acquisition error
```

## Owned-fork characterization

The wasm test added to `tests/tests/wgpu-gpu/create_surface_error.rs` performs:

1. explicit browser-WebGPU instance and adapter;
2. 1×1 canvas and default supported configuration;
3. clone configuration and set width to zero;
4. push validation error scope;
5. call public `Surface::configure`;
6. pop and require a configure validation error;
7. assert public cache contains the zero-sized request;
8. assert canvas is 0×1;
9. assert raw context still reports configured state;
10. push a second validation scope;
11. acquire through public wgpu;
12. require `Success` or `Suboptimal` carrying a public 0×1 texture;
13. pop and require an acquisition validation error;
14. drop the error texture;
15. restore 1×1 and apply the supported baseline;
16. present successfully.

## Why this matters

### Documentation

A backend-dependent panic promise is inaccurate. Browser applications may continue after the call with:

- validation delivered asynchronously or through an error scope;
- public configuration cache set;
- raw context configured;
- unusable/error texture until extent is repaired.

### Internal configure result

A binary result is insufficient:

- configuration produced validation;
- it was not synchronously rejected;
- it retained useful configuration state;
- current acquisition is invalid only because the canvas extent is zero;
- resizing can repair raw state without another raw configure call.

### Public acquisition result

A `Success` variant can carry an error texture when validation is delivered separately. `Success` therefore means a texture object was returned, not necessarily that the texture can be used successfully.

This is consistent with WebGPU's error-object model but easy for Rust callers to misunderstand.

### Native comparison

Native core validates zero area before HAL configuration. The failure is routed to the device error sink, and the outer public wrapper still caches the request.

Before any prior accepted configuration, a later native acquisition can become fatal because the core surface has no configured error sink. After a prior accepted configuration, the earlier presentation can remain while public metadata follows the zero-sized request.

The same public request therefore has materially different backend state and acquisition consequences.

## Candidate corrections after execution

Do not select a patch yet. Plausible narrow outcomes include:

1. document backend-dependent validation and WebGPU error-texture behavior;
2. prevalidate zero size in the public wrapper for consistent Rust semantics;
3. keep browser semantics but distinguish accepted configuration from usable current extent;
4. teach examples to clamp/skip zero size before calling configure;
5. retain `AppliedWithDiagnostic` in any internal configure disposition.

Prevalidating publicly would improve consistency but could diverge from raw WebGPU's repair-by-resize behavior. That tradeoff needs execution and maintainer preference.

## Execution risks

The prepared test still needs to confirm:

- error scope timing in the repository browser harness;
- whether the returned error texture reaches `Success` or `Suboptimal` exactly as source predicts;
- whether public texture dimensions are exposed as 0×1;
- whether dropping the browser error texture creates additional validation;
- whether supported reconfiguration and presentation recover cleanly.

## Stops

- Do not call this a synchronous rejection.
- Do not assume validation means no configuration was established.
- Do not claim the public texture is usable merely because acquisition returned `Success`.
- Do not change the public panic contract before running browser and native controls.
