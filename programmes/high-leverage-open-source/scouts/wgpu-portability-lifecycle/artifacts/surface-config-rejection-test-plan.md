# Proposed wgpu surface-configuration rejection test packet

State: source design only; not executed

Target source: `gfx-rs/wgpu@2eddc8c7b2fedd4267f5004745a8bc42974e17a0`

Fieldwork issue: #116

Upstream contact authorized: false

## Why this belongs in the repository test harness

wgpu already provides:

- browser-executed GPU tests under `tests/tests/wgpu-gpu/`;
- wasm-only test gating through `#![cfg(wasm_test)]`;
- `wgpu_test::initialize_instance` and `initialize_html_canvas`;
- panic forwarding to the browser test controller;
- `cargo xtask test-wasm` for headless browser execution;
- an existing wasm-only surface creation error test in `tests/tests/wgpu-gpu/create_surface_error.rs`.

The first regression should therefore be a normal wgpu wasm GPU test, not an external application or an addition to the upstream WebGPU CTS. The behavior under investigation is the Rust wrapper's publication and recovery semantics, not raw WebGPU conformance.

## Suggested file

```text
tests/tests/wgpu-gpu/surface_configure_rejection.rs
```

Add the module to the same generated/manual test registration surface used by neighbouring `wgpu-gpu` tests.

## Deterministic failure path

Use the browser WebGPU backend and request a configuration that wgpu itself declares unrepresentable on a WebGPU canvas:

```text
SurfaceColorSpace::ExtendedSrgbLinear
```

The browser backend's current source handles this before calling the browser:

1. sets `configure_failed = true`;
2. logs an error;
3. returns from backend `configure`;
4. later reports `SurfaceStatus::Lost`.

This is more deterministic than depending on a browser that still advertises and rejects `rgba16float`.

## Setup

1. Initialize an instance restricted to `Backends::BROWSER_WEBGPU`.
2. Create an HTML canvas through the existing test helper.
3. Create a surface from the canvas.
4. Request a compatible adapter.
5. Request a device and queue.
6. Obtain a supported baseline configuration through `get_default_config`.
7. Configure the baseline and acquire one successful frame.
8. Present or drop the frame according to the smallest stable test path.

## Current-behavior assertions

Clone the supported baseline and change only:

```text
color_space = SurfaceColorSpace::ExtendedSrgbLinear
```

Then record these outcomes rather than assuming the desired repair:

1. `Surface::configure` returns without wasm abort.
2. `Surface::get_configuration()` after rejection.
3. `Surface::get_current_texture()` after rejection.
4. Recreating the surface and applying the same rejected configuration.
5. Applying the original supported baseline to the original or recreated surface.
6. Successful acquisition after supported fallback.

Source predicts:

```text
configure returns
get_configuration == Some(rejected_request)
get_current_texture == Lost
same-config recreation == Lost again
supported fallback clears failure and succeeds
```

The first two lines are the acceptance/publication question. The final line is the mandatory recovery control.

## Test split

Prefer two tests if the harness makes log capture or surface recreation cumbersome.

### Test A — publication after rejection

Proves the state immediately after a deterministic rejected browser configuration:

- no abort;
- cached configuration result;
- acquisition status.

### Test B — recovery and shared-example control

Proves:

- repeating the rejected configuration does not recover;
- supported fallback does recover;
- the device remains usable;
- surface recreation is not sufficient when the configuration remains invalid.

## Native control

The browser test alone establishes the deterministic wrapper behavior. A separate native or core-level test should then inject a recoverable `surface_configure` failure and answer:

- does the public cache also publish the rejected request on the core backend;
- does the earlier accepted configuration remain usable;
- does the error scope receive the failure;
- can another surface or adapter recover.

This may require a mock/noop or targeted core test rather than a hardware-specific integration test. Do not block the browser regression on a portable native injection mechanism.

## Likely patch tiers after execution

### Minimal accepted packet

- add the wasm regression test;
- document the browser nonfatal rejection path;
- document whether `get_configuration` is last requested or last accepted;
- update `Lost` recovery guidance or the shared example framework.

### Internal semantic repair

Change the dispatch boundary so the public wrapper can update its cache only when configuration establishes usable state.

The internal result must distinguish at least:

- applied;
- rejected/not configured;
- diagnostic emitted but configured where WebGPU semantics permit that;
- fatal/unrecoverable.

Do not assume a boolean is sufficient.

### Larger public API discussion

Only after the regression and internal semantics are established, consider:

- `Surface::configure -> Result`;
- a dedicated rejected-configuration acquisition state;
- richer surface error classification.

## Expected test command

Use the repository's wasm test runner and narrow to the new test name, following current `cargo xtask test-wasm` filtering conventions. Confirm the exact filter syntax in the generated test list before recording a final command.

Full relevant validation for a candidate patch should include:

```text
cargo fmt
cargo clippy --tests
cargo xtask test-wasm -- <narrow test filter>
```

Run broader wasm tests only after the narrow regression is stable.

## Stop conditions

- Stop if the source revision no longer produces the predicted rejected-config state.
- Stop an API redesign if documentation and example recovery fully resolve the practical consequence.
- Do not report raw browser behavior as a wgpu defect.
- Do not add this behavior to WebGPU CTS; the raw WebGPU CTS already distinguishes failed configuration state.
- Do not contact upstream without explicit authorization.
