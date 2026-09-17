# WebGPU canvas resize control for rejected wgpu configuration

State: pinned CTS source-read; owned browser execution queued

Fieldwork issue: #116

Upstream contact authorized: false

## Exact records

- WebGPU CTS pin: [gpuweb CTS source](https://redirect.github.com/gpuweb/cts/commit/dc20b8682aa71ff31f135de6ae7f8acaa2e16383)
- relevant CTS file: `src/webgpu/web_platform/canvas/getCurrentTexture.spec.ts`
- owned wgpu browser characterization head: `teamleaderleo/wgpu@3e058e5d4b6d94631d28c2242a02bd1163888db5`
- focused browser runtime run: `30556640792`

## Why this control matters

The owned browser rejection test starts from an accepted 2×2 WebGPU canvas configuration, then asks wgpu to apply a 7×5 configuration using `ExtendedSrgbLinear`.

The browser backend performs these steps in order:

```text
set canvas width = 7
set canvas height = 5
reject ExtendedSrgbLinear locally
set configure_failed = true
return before GPUCanvasContext.configure
```

Therefore the raw browser context retains its earlier accepted configuration dictionary while the canvas dimensions have changed.

The test predicts that raw `GPUCanvasContext.getCurrentTexture()` remains usable and returns a 7×5 texture.

## CTS requirement

The pinned WebGPU CTS contains a dedicated `getCurrentTexture` resize test.

It configures a canvas once, acquires a current texture, changes the canvas width or height, and requires:

```text
previous texture becomes destroyed
next getCurrentTexture returns a different texture
new texture width = current canvas width
new texture height = current canvas height
```

No second `GPUCanvasContext.configure()` call occurs between the canvas resize and the new acquisition.

This establishes the relevant standards control:

> Canvas extent is live acquisition state, not a fixed copy of the dimensions that existed when the configuration dictionary was installed.

## Consequence for the wgpu partial-mutation state

After the locally rejected 7×5 request, the predicted state is coherent with WebGPU's canvas model:

```text
raw configuration dictionary = prior accepted baseline
canvas width/height = rejected request
raw next texture size = rejected request extent
wgpu public configuration cache = rejected request
wgpu public acquisition = Lost because configure_failed is set
```

The raw browser context is not simply “unchanged.” Its configuration dictionary remains accepted, but the drawing-buffer extent follows the new canvas dimensions.

This is why the lane describes the outcome as `RejectedAfterPartialMutation`, not `RejectedPreservingPrevious`.

## Browser execution gate

The owned focused workflow now runs the project-native Playwright harness against the `create_surface_error` module.

The runtime receipt must record:

- the Playwright/Chromium GPU report;
- explicit BrowserWebGpu adapter selection;
- accepted 2×2 baseline;
- rejected 7×5 public cache and canvas extent;
- public `Lost` result;
- raw 7×5 texture acquisition;
- same-surface supported recovery;
- recreated-surface retry and supported fallback.

A runtime contradiction must revise the model even though the CTS resize rule is clear. Possible contradiction sources include ownership restrictions on mixing raw and wrapper acquisition, browser implementation differences, or test-harness lifecycle behavior.

## Stops

- Do not describe the raw context as fully preserving the 2×2 baseline after canvas mutation.
- Do not require a second raw configure merely to resize the current texture.
- Do not upgrade CTS source-read to owned browser execution.
- Do not treat public `Lost` as proof that the raw browser context is lost.
- Do not contact upstream without authorization.

## Current conclusion

The 7×5 raw acquisition assertion is not speculative. It is directly supported by the pinned WebGPU CTS rule that configured canvas textures immediately track canvas dimension changes without reconfiguration. The remaining uncertainty is wgpu/browser integration behavior under the exact owned runtime test.