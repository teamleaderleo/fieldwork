# wgpu `release_inner` history and teardown-order hypothesis

State: source-read; controlled teardown experiment designed, not executed

Fieldwork issue: #116

Upstream contact authorized: false

## Origin

The release-without-discard path was introduced by:

[wgpu pull request 9678: fix Vulkan surface-texture drop panic](https://redirect.github.com/gfx-rs/wgpu/pull/9678)

Merged commit:

```text
d835ad3a090e5cfb4ec02e43724e2b4fc25639b1
```

The pull request fixed issue 8243, where panic unwinding dropped a public `SurfaceTexture` while a Vulkan swapchain acquire-semaphore reference remained retained.

The accepted repair deliberately distinguished two operations:

```text
ordinary unpresented drop
→ HAL discard

panic unwind
→ release the core acquired-texture reference
→ skip HAL discard
```

The stated reason was precise: dropping the core texture releases `NativeSurfaceTextureMetadata` and its `Arc<SwapchainAcquireSemaphore>`, allowing Vulkan swapchain teardown to regain unique ownership.

The change was manually tested by its author, passed the eventual repository checks, and was accepted as a deliberately small lifecycle fix.

## Relevance to issue 9277

Current open issue:

[wgpu issue 9277: Surface drop panics after device loss](https://redirect.github.com/gfx-rs/wgpu/issues/9277)

Issue 9277 reports the same retained semaphore-reference shape at a different lifecycle boundary:

```text
acquire frame
→ device becomes invalid
→ public present/discard reject before taking acquired_texture
→ Surface drop begins
→ HAL unconfigure runs while Presentation still owns acquired_texture
→ Vulkan swapchain release requires unique semaphore ownership
→ panic
```

The historical fix proves that “drop retained metadata without HAL discard” is already an accepted ownership operation. It does **not** prove that simply taking `acquired_texture` is sufficient in every device-loss case.

## Why sufficiency still needs testing

Other references may exist:

- the public texture wrapper until the failed presentation call returns;
- core tracker or submission lifetime records;
- pending or failed submission structures;
- backend-specific surface-texture metadata.

A teardown repair must therefore prove the unconfigure precondition rather than merely show that one reference was removed.

## Narrow ordering hypothesis

Current `Surface::drop` effectively performs:

```text
take Presentation from lock
→ HAL unconfigure
→ drop Presentation and acquired_texture
```

The candidate ordering is:

```text
take Presentation from lock
→ take/drop acquired_texture
→ HAL unconfigure
→ drop remaining Presentation
```

This reuses the ownership operation accepted in PR 9678 without calling device-sensitive HAL discard after device loss.

## Controlled experiment design

Use an instrumented noop surface as a lifecycle model, not platform proof.

The noop surface texture should carry explicit accounting state:

```text
acquire_count
explicit_discard_count
present_count
implicit_metadata_release_count
outstanding_count
unconfigure_count
unconfigure_with_outstanding_count
```

Its surface-texture handle decrements `outstanding_count` on implicit drop unless explicit discard or present already accounted for it.

### Baseline

1. configure noop surface;
2. acquire one frame;
3. mark the core device invalid through a test-only internal path;
4. call public/core presentation entry and require `DeviceError::Lost` before detachment;
5. drop the caller's output clone;
6. drop the surface;
7. instrumented unconfigure requires zero outstanding metadata and therefore records/panics on one outstanding reference;
8. unwind then drops the retained presentation texture and records implicit metadata release.

Expected accounting:

```text
before teardown:
acquire=1 discard=0 present=0 implicit_release=0 outstanding=1

at unconfigure:
unconfigure=1 unconfigure_with_outstanding=1 outstanding=1

after caught unwind:
implicit_release=1 outstanding=0
```

### Release-before-unconfigure control

Repeat setup through the rejected presentation, then:

1. drop the caller's output clone;
2. invoke `release_inner()` or the exact equivalent `acquired_texture.take()`;
3. require implicit metadata release and zero outstanding count;
4. drop the surface;
5. require unconfigure observes zero outstanding state and does not panic.

Expected accounting:

```text
before teardown:
acquire=1 discard=0 present=0 implicit_release=1 outstanding=0

at unconfigure:
unconfigure=1 unconfigure_with_outstanding=0 outstanding=0
```

## Platform follow-ups

### Vulkan

The real receipt must show that semaphore ownership is unique before swapchain `release_resources` drains its semaphore arrays. A controlled noop pass is insufficient.

### DX12

Dropping a retained frame without explicit discard leaves `acquired_count` stale, but teardown destroys the swapchain immediately afterward. Confirm that no intermediate path reads or relies on the count before destruction.

### Metal

Dropping the retained `CAMetalDrawable` before layer teardown is expected to return drawable-pool ownership; confirm under an actual device-loss or forced-invalid control where feasible.

### WebGL

The reusable surface-owned backing texture does not model native swapchain reservation, but teardown ordering should remain harmless.

## Repair boundary

A likely repair should remain within core `Surface::drop` ordering or a small private helper.

Do not begin with:

- public API changes;
- making discard ignore every device error;
- broad backend-specific special cases;
- silently swallowing teardown panics without fixing ownership.

## Promotion gate

Promote only after:

- baseline failure is executed;
- release-before-unconfigure control is executed;
- exact outstanding-reference accounting is captured;
- a Vulkan control confirms semaphore uniqueness;
- DX12 teardown bookkeeping is checked;
- the current upstream issue and source revision are pinned;
- independent review is tied to the exact candidate head;
- upstream contact is explicitly authorized.

## Current conclusion

PR 9678 establishes `release_inner` as a legitimate, accepted ownership primitive for dropping retained surface-texture metadata without HAL discard. Issue 9277 appears to need that primitive at surface teardown, but the lane will test the full unconfigure precondition before treating the ordering change as sufficient.