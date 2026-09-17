# Pre-HAL presentation failure backend matrix

State: source-read; wrapper characterization prepared; no core or backend execution

Fieldwork issue: #116

Owned fork head: `teamleaderleo/wgpu@3d076485509f6b3f8381de8074bfbdef17bc4133`

Upstream contact authorized: false

## Question

After native core removes an acquired frame from surface state, `prepare_surface_texture_for_present` can fail before the raw texture reaches HAL `present`.

At that point the generic core texture is dropped, but the surface-specific `discard_texture` operation was not called.

The consequence depends on the backend. This matrix records the first backend-specific source pass.

## Shared core sequence

```text
surface presentation state contains acquired_texture
→ core Queue::present takes acquired_texture
→ prepare_surface_texture_for_present begins
→ failure occurs before HAL Queue::present
→ local Arc<Texture> drops
→ TextureInner::Surface raw object drops as a field
→ no Surface::discard_texture call occurred
```

The core `Texture::drop` implementation destroys a surface clear view, but only explicitly destroys an ordinary raw texture for `TextureInner::Native`. Surface-image return or release remains backend-specific.

## DX12

### Acquisition bookkeeping

DX12 acquisition:

1. reads `GetCurrentBackBufferIndex()`;
2. computes an index using `base_index + acquired_count`;
3. increments `acquired_count`;
4. returns a clone of the swapchain buffer resource.

### Normal completion paths

Both explicit surface discard and HAL present decrement `acquired_count`.

```text
acquire → acquired_count += 1
explicit discard → acquired_count -= 1
present → acquired_count -= 1 before IDXGISwapChain::Present
```

### Pre-HAL failure consequence

Dropping the detached texture releases the COM resource clone, but it does not reach the surface and therefore cannot decrement `acquired_count`.

Source-supported state:

```text
actual outstanding public/core frame = gone
swapchain acquired_count = still elevated
next chosen resource index = offset by stale count
```

This is an observable bookkeeping-risk candidate, not merely a resource-lifetime concern.

### Required DX12 probe

- acquire one frame;
- inject core preparation failure before HAL present;
- inspect `acquired_count` through a test-only hook or repeated acquisition behavior;
- prove HAL present was not called;
- prove surface discard was or was not called;
- acquire and present enough later frames to detect stale indexing, underflow, duplicate selection, or recovery;
- compare with explicit discard and successful present controls.

A narrow invariant test could also place a guard around the acquired-count transition, but it should not lock in a repair before runtime behavior is measured.

## Vulkan

### Acquired object

Vulkan surface texture contains:

- swapchain image index;
- external texture wrapper;
- acquire and present semaphore metadata.

Dropping the object releases Rust references to semaphore metadata. It does not call `vkQueuePresentKHR`.

### Explicit discard

The current native Vulkan swapchain `discard_texture` implementation is explicitly a no-op.

Therefore the generic pre-HAL drop and the explicit discard path have materially similar source behavior:

```text
acquired image index was returned by vkAcquireNextImageKHR
→ texture object and semaphore references drop
→ image is not presented
→ no explicit Vulkan operation returns the image to the presentation engine
```

The source comments already say Vulkan discard does not really work in the current implementation.

### Risk

Vulkan does not provide a simple operation to cancel an acquired swapchain image. An image generally becomes available again after presentation or swapchain teardown.

The first likely symptom is not a Rust memory leak; it is swapchain-image availability or semaphore-state failure after repeated pre-HAL preparation failures.

### Required Vulkan probe

- use a swapchain with known image count;
- acquire one frame;
- inject preparation failure before HAL present;
- repeat acquisition with bounded timeouts;
- record when acquisition times out or images stop cycling;
- validate semaphore and swapchain diagnostics;
- compare explicit discard, successful present, and surface recreation;
- confirm whether device/surface teardown is the only recovery.

Do not call this a Vulkan defect until the repeated-acquisition control executes. The current explicit discard path may already define abandonment as best-effort/no-op.

## Metal

### Acquired object

Metal acquisition retains:

- a `CAMetalDrawable`;
- its texture;
- presentation mode metadata.

Explicit discard is a no-op, but dropping the retained drawable releases the Objective-C retain count.

### Likely consequence

A pre-HAL preparation failure drops the retained drawable object. That is plausibly the intended release mechanism for an unpresented Metal frame.

The risk is lower than DX12 or Vulkan, but should still be verified under autorelease and drawable-pool pressure.

### Required Metal control

- repeatedly acquire and abandon frames through injected preparation failure;
- verify `nextDrawable()` continues to succeed;
- record drawable-pool pressure and timeouts;
- compare ordinary drop, panic-unwind release, and successful present;
- run while visible and occluded because Metal acquisition has separate occlusion handling.

## WebGL

### Acquired object

The WebGL HAL surface returns a wrapper around a surface-owned reusable texture/backing framebuffer rather than reserving a platform swapchain image per acquisition.

Explicit discard is a no-op.

### Likely consequence

Dropping the wrapper does not need to return a distinct platform image. A pre-present failure should leave the surface-owned backing texture reusable.

The relevant risk is state restoration, not image availability:

- stale framebuffer bindings;
- partially executed automatic clear/transition work;
- presentation blit failure;
- context loss.

This is lower priority than DX12 and Vulkan for the detached-frame cleanup probe.

## Browser WebGPU

The browser WebGPU backend bypasses native `wgpu-core` and `wgpu-hal` presentation. Its queue present operation is a no-op because browser canvas presentation is controlled by the user agent.

The pre-HAL core failure seam does not apply to this backend.

Browser lifecycle remains covered by the separate configuration/acquisition characterizations.

## Native GLES/EGL/WGL

Not yet fully source-audited in this pass.

These surfaces generally present through swap-buffer operations rather than exposing an acquired image index like Vulkan. The current source still needs a direct check of:

- whether acquisition reserves any backend state;
- whether explicit discard changes that state;
- whether failed preparation leaves an offscreen/default framebuffer or swap interval state inconsistent.

Keep this row open rather than inferring WebGL behavior applies to native EGL/WGL.

## Noop

The noop backend is not a fidelity model for platform surface ownership. Do not use it as the only proof that detached-frame cleanup is safe.

It may still be useful to test generic state transitions or an internal cleanup guard, but not swapchain-image return.

## Priority order

### P1 — DX12 acquired-count invariant

The source exposes a deterministic counter that both discard and present repair. This is the cheapest concrete proof of missing surface cleanup after pre-HAL failure.

### P1 — Vulkan repeated acquisition

The source exposes the highest platform risk: acquired images have no functioning discard operation. Use bounded timeouts and exact image-count receipts.

### P2 — Metal drawable-pool pressure

Confirm retained-object drop is sufficient under repeated failure.

### P2 — native GLES surface-state audit

Determine whether there is hidden per-acquisition bookkeeping.

### P3 — WebGL state restoration

Only after native image-availability paths are understood.

## Candidate internal repair shapes

Do not select one yet. Plausible shapes include:

### Guarded detach

Keep a guard owning the surface and raw acquired texture. If preparation returns before HAL consumes it, the guard calls backend discard.

Problem: Vulkan discard is currently a no-op, so this may repair DX12 bookkeeping without solving Vulkan image availability.

### Prepare before detach

Perform preparation while the surface presentation state still owns the acquired texture, then detach only immediately before HAL consumption.

Problem: preparation needs access to the texture and may submit work; lock duration, reentrancy, and deadlock rules must be checked.

### Backend disposition

Have preparation return an ownership disposition that says whether the frame remains attached, was submitted, or must be abandoned by surface teardown.

Problem: larger internal contract and custom/backend compatibility cost.

### Failure-forces-surface-reset

When a backend cannot discard an acquired image, mark the surface unconfigured/lost and require recreation.

Problem: potentially expensive and must preserve device-error semantics.

## Promotion gate

A cleanup candidate requires:

- exact failure injection point;
- proof HAL present did not run;
- proof whether surface discard ran;
- backend-specific state after failure;
- successful-present and explicit-discard controls;
- subsequent acquisition behavior;
- at least DX12 and Vulkan execution;
- no claim that Metal/WebGL semantics generalize;
- current-source reconciliation;
- independent exact-head review;
- explicit upstream authorization.

## Stops

- Do not call generic raw-object drop equivalent to surface discard on every backend.
- Do not infer Vulkan image return from semaphore-reference drop.
- Do not treat DX12 COM-resource release as acquired-count repair.
- Do not use noop as platform-lifetime proof.
- Do not force one identical recovery mechanism across all backends.
- Do not contact upstream without authorization.

## Current decision

The first implementation probe should target DX12 bookkeeping because the expected invariant is explicit:

```text
number of successful acquisitions
- number of presents
- number of discards
= acquired_count
```

A pre-HAL preparation failure currently appears to remove the public/core frame without contributing either a present or discard decrement. Prove or disprove that invariant break before designing cleanup.
