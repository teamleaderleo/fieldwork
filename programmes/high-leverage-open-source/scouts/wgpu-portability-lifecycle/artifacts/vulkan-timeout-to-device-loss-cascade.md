# Vulkan acquisition timeout to device-loss cascade

State: current-source verified; upstream reports corroborate; no owned execution yet

Fieldwork issue: #116

Upstream contact authorized: false

## Exact source records

- pinned wgpu source: [wgpu v30 source pin](https://redirect.github.com/gfx-rs/wgpu/commit/2eddc8c7b2fedd4267f5004745a8bc42974e17a0)
- current wgpu source checked: [current wgpu source](https://redirect.github.com/gfx-rs/wgpu/commit/c079e55f534d713a60aef145f6df0255b7ddcdc4)
- acquisition-timeout report: [wgpu issue 9029](https://redirect.github.com/gfx-rs/wgpu/issues/9029)
- retained-frame teardown report: [wgpu issue 9277](https://redirect.github.com/gfx-rs/wgpu/issues/9277)

## Current source chain

The Vulkan native swapchain acquisition path performs a bounded fence wait before acquiring the next image.

Current behavior:

```text
vkWaitForFences(..., timeout_ns)
→ Err(VK_TIMEOUT)
→ map_host_device_oom_and_lost_err
→ map_host_device_oom_err
→ DeviceError::Unexpected
```

The mapping helper recognizes only:

- out-of-host-memory;
- out-of-device-memory;
- device-lost.

Every other Vulkan result becomes an unexpected device error.

Core then handles every HAL `DeviceError::Unexpected` by invalidating the device through `Device::lose`.

Therefore the source-supported classification is:

```text
surface fence wait exceeded the frame timeout
→ HAL unexpected device error
→ core device invalidated
→ public acquisition returns a device error rather than SurfaceStatus::Timeout
```

This is still present in the checked current source.

## Corroborating upstream reports

Issue 9029 reports the exact timeout-to-device-loss mapping on Windows/Vulkan/Intel Arc under a long-running shader.

A second user reports seeing the same behavior on Ubuntu/Vulkan while running Burn ML inference inside a Bevy application.

This matters because the trigger is not necessarily a dead GPU. Heavy but valid GPU work may exceed the one-second surface wait budget.

## Cascade into surface ownership

Once the device is invalid, surface operations take different early exits.

### Before a frame is acquired

The failed acquisition returns before core stores a new `Presentation::acquired_texture`. The immediate effect is an unnecessary full device-loss callback and failed recovery path.

### After a prior frame remains acquired

A separate frame may already be retained when the misclassification invalidates the device.

Public/native presentation and discard both check device validity before taking the retained frame. They can therefore return `DeviceError::Lost` while `Presentation::acquired_texture` remains populated.

Current surface teardown then calls HAL unconfigure before dropping that retained texture. On Vulkan, issue 9277 reports a panic because swapchain acquire-semaphore metadata is still referenced.

The combined cascade is:

```text
long but nonfatal GPU work
→ Vulkan fence wait returns TIMEOUT
→ timeout mapped to Unexpected
→ core marks device lost
→ retained acquired frame cannot be presented or discarded
→ Surface drop unconfigures before retained metadata release
→ Vulkan swapchain teardown can panic
```

These are independently fixable boundaries. The earliest correct repair is preferable.

## Narrow repair boundary A — timeout classification

At the Vulkan swapchain acquisition call site, `VK_TIMEOUT` is a surface acquisition outcome, not a device error.

The narrow candidate behavior is:

```text
Err(VK_TIMEOUT) → SurfaceError::Timeout
Err(ERROR_DEVICE_LOST) → SurfaceError::Device(DeviceError::Lost)
OOM results → SurfaceError::Device(DeviceError::OutOfMemory)
other results → existing unexpected-device handling
```

This keeps the mapping contextual. Globally changing `map_host_device_oom_and_lost_err` to map every timeout would be wrong because other Vulkan operations may not have a surface-timeout interpretation.

## Narrow repair boundary B — teardown ownership

Even with correct timeout classification, genuine device loss can still occur while a frame is retained.

The separate teardown hypothesis remains:

```text
release retained surface-texture metadata
→ then HAL unconfigure
```

The owned draft teardown experiment tests whether that ordering satisfies the full outstanding-resource precondition in a controlled noop model.

## Experiment design for timeout classification

A deterministic test should avoid a real long-running shader initially.

### Pure mapping control

Extract or wrap the fence-wait result classification at the Vulkan swapchain call site and assert:

```text
VK_TIMEOUT                  → SurfaceError::Timeout
VK_ERROR_DEVICE_LOST        → SurfaceError::Device(Lost)
VK_ERROR_OUT_OF_HOST_MEMORY → SurfaceError::Device(OutOfMemory)
VK_ERROR_OUT_OF_DEVICE_MEMORY → SurfaceError::Device(OutOfMemory)
```

This is a source-level contract test, not a driver execution receipt.

### Controlled core propagation

Use a test surface whose acquisition returns `SurfaceError::Timeout` and assert:

```text
CurrentSurfaceTexture / core status = Timeout
device valid = true
device-lost callback = not invoked
```

Negative control:

```text
acquisition returns DeviceError::Lost
device valid = false
device-lost callback is scheduled
```

### Real Vulkan follow-up

Only after the mapping and core propagation controls:

- inject or reproduce a fence wait timeout under Vulkan;
- prove the device remains valid;
- prove a later acquisition succeeds;
- record adapter, driver, OS, timeout duration, and validation output.

## Promotion gate

Promote only with:

- an exact source pin and current-source check;
- executed mapping tests;
- executed core device-validity control;
- a successful later-acquisition negative control;
- clear separation from genuine device loss;
- independent exact-head review;
- explicit upstream authority.

## Stops

- Do not treat every slow frame as device loss.
- Do not globally reinterpret Vulkan timeout results outside the surface acquisition context.
- Do not merge timeout classification and teardown ordering into one oversized repair.
- Do not claim a real-driver reproduction from pure mapping tests.
- Do not contact upstream without authorization.

## Current conclusion

The timeout misclassification is a live, source-verified upstream bug with reports from more than one workload. It can plausibly manufacture the device-loss state that exposes the retained-frame teardown panic. The lane should test and repair the classification boundary first, while keeping the teardown ownership fix independently valid for genuine device loss.