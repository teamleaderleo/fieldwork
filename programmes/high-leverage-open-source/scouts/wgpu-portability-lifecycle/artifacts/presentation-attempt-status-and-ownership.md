# wgpu presentation attempt, status, and ownership audit

State: source-read plus target-test-prepared; focused execution queued

Fieldwork issue: #116

Fieldwork draft PR: #126

Owned fork draft: `teamleaderleo/wgpu#1`

Upstream contact authorized: false

## Exact records

- pinned source tree: [pinned wgpu source](https://redirect.github.com/gfx-rs/wgpu/commit/2eddc8c7b2fedd4267f5004745a8bc42974e17a0)
- current upstream tree checked: [current wgpu source checked](https://redirect.github.com/gfx-rs/wgpu/commit/c079e55f534d713a60aef145f6df0255b7ddcdc4)
- owned-fork characterization head: `teamleaderleo/wgpu@33d307cbe7acea21d23d561c72d270404a47bde4`
- focused workflow: `.github/workflows/fieldwork-characterization.yml`
- historical presentation rewrite: [wgpu queue-owned presentation rewrite](https://redirect.github.com/gfx-rs/wgpu/pull/9222)

The checked upstream tree is seven commits ahead of the pin. The relevant public queue and surface-texture API, browser surface backend, core presentation implementation, HAL presentation contract, and shared example recovery framework remain unchanged. The fork still requires current-target reconciliation and executed receipts.

## State machine under investigation

Presentation is not one event:

```text
application gives SurfaceTexture to Queue::present
→ public wrapper marks the value presented
→ backend dispatch begins
→ core removes the acquired texture from surface state
→ core may clear and transition the texture
→ HAL consumes the raw surface texture
→ HAL returns a status or error
→ core classifies the outcome
→ public backend reports errors separately and discards non-error statuses
```

The central question is:

> At which boundary is ownership irreversibly transferred, and which cleanup path owns the frame when failure occurs between boundaries?

## Public ownership commit

Public `Queue::present` takes a `SurfaceTexture` by value, marks it presented, calls backend dispatch, and returns `()`.

`SurfaceTexture::drop` calls:

- `texture_discard` for an ordinary unpresented drop;
- `texture_release` while unwinding;
- neither after the internal presented flag is set.

The public API therefore commits ownership before backend dispatch. That is not automatically wrong: the HAL contract also consumes the raw surface image by value. The observable consequence is that the caller cannot retry or inspect the frame and receives no immediate presentation result.

## Prepared public-wrapper characterization

The owned fork contains two private custom-backend unit tests beside `wgpu/src/api/surface_texture.rs`.

### Ordinary drop control

```text
construct custom SurfaceTexture
→ drop without present
→ texture_discard = 1
→ texture_release = 0
```

### Injected backend panic

```text
construct custom Queue and SurfaceTexture
→ Queue::present marks frame presented
→ custom backend records one call and panics
→ catch unwind outside Queue::present
→ texture_discard = 0
→ texture_release = 0
```

This characterizes the public ownership boundary. It does not prove a native leak or establish that ownership should be rolled back after dispatch begins.

## Core detachment before HAL consumption

Native core has another transition. Its presentation path:

1. locks surface presentation state;
2. removes `acquired_texture` with `take()`;
3. calls `prepare_surface_texture_for_present`;
4. snatches the raw surface-texture handle;
5. passes that handle by value to HAL presentation.

Preparation can fail while:

- allocating a submission;
- encoding an automatic clear;
- translating a clear failure into device loss;
- retrieving the raw texture handle;
- submitting the clear and transition work.

The resulting source-supported state is:

```text
surface acquired_texture = removed
public SurfaceTexture = consumed
public presented flag = true
HAL present = not called
ordinary discard and unwind release = suppressed
```

The generic core texture destructor cleans up the internal clear view but does not itself invoke the surface-specific discard operation.

This creates the executable question:

> When preparation fails after detachment but before HAL consumption, is the platform surface image correctly returned, and can the surface acquire again without teardown?

No leak or defect is claimed until that path is executed.

## Backend-specific consequences

### DX12

Acquisition increments internal `acquired_count`. Both explicit discard and presentation decrement it. A pre-HAL failure appears to skip both operations, creating a precise bookkeeping hypothesis:

```text
successful acquisitions
- successful presents
- explicit discards
= acquired_count
```

The first DX12 experiment should inject preparation failure and then measure the counter and later back-buffer selection.

### Vulkan

The raw surface texture carries a swapchain-image index and semaphore metadata. Native discard is currently a no-op. The decisive experiment is repeated bounded acquisition after a pre-HAL failure using a known swapchain image count.

### Metal

Discard is a no-op, but the surface texture retains a `CAMetalDrawable`; dropping the retained handle may return drawable-pool ownership. This requires a control rather than inference.

### WebGL

Acquisition wraps a reusable surface-owned backing texture rather than reserving a distinct platform swapchain image. Its ownership model should not be generalized to native swapchains.

## Presentation status loss

HAL and core initially preserve presentation outcomes including timeout, occlusion, lost, and outdated. The public core backend discards those non-error statuses and returns `()`; only errors reach the separate error sink.

This may intentionally align with WebGPU fire-and-forget presentation. A public `Queue::present -> Result` redesign is not justified without an application-actionable consequence.

## Historical evidence

- [unpresented-frame cleanup report](https://redirect.github.com/gfx-rs/wgpu/issues/4056)
- [presentation without submitted work report](https://redirect.github.com/gfx-rs/wgpu/issues/2635)
- [unused-frame synchronization report](https://redirect.github.com/gfx-rs/wgpu/issues/6748)
- [panic-unwind release report](https://redirect.github.com/gfx-rs/wgpu/issues/8243)
- [backend presentation failure report](https://redirect.github.com/gfx-rs/wgpu/issues/5259)
- [queue-owned presentation rewrite](https://redirect.github.com/gfx-rs/wgpu/pull/9222)

The queue-owned rewrite and its review show that presentation completion is not equivalent to an ordinary fence-signaled submission. Naive lifetime indices can produce impossible waits or retained frames.

## Provisional states

- `Acquired`: surface still records the acquired texture.
- `PresentationAttemptCommitted`: public frame consumed and drop cleanup suppressed.
- `DetachedForPreparation`: core removed the acquired texture; HAL has not consumed it.
- `PreparedForPresentation`: required clear and transition work succeeded.
- `HalConsumed`: raw texture passed to HAL.
- `Presented`: HAL accepted presentation.
- `ConsumedWithStatus`: HAL consumed the frame and returned timeout, occlusion, lost, or outdated.
- `PreparationFailedDetached`: core detached the frame and failed before HAL consumption.
- `ConsumedWithError`: HAL or device processing consumed ownership and returned an error.

The names are provisional. The required distinction is failure before versus after HAL consumes the raw image.

## Execution programme

### Focused public and browser checks

Exact owned-fork head `33d307cbe7acea21d23d561c72d270404a47bde4` queues:

- formatting;
- minimal-feature custom-backend unit tests;
- wasm characterization compilation and clippy.

The inherited repository CI also contains a browser Playwright runner. Results must be reported per job and exact head rather than as one undifferentiated CI verdict.

### Core preparation-failure probe

The preferred first deterministic trigger is:

```text
configure surface
→ acquire frame
→ destroy device
→ present consumed frame
```

This should force submission allocation or preparation to fail before HAL presentation. A controlled HAL or instrumented noop surface must record:

- acquisition count;
- discard count;
- HAL presentation count;
- outstanding image count;
- subsequent acquisition behavior.

A separate experiment branch, `fieldwork/pre-hal-present-failure-noop`, exists to investigate a deterministic instrumented-noop carrier without contaminating the browser characterization branch.

## Promotion gate

Do not promote a presentation finding until it has:

- a compiled and executed public-wrapper characterization;
- an executed core preparation-failure control;
- a successful-presentation negative control;
- proof of whether HAL present and surface discard ran;
- subsequent acquisition behavior;
- exact pinned and current-source receipts;
- a narrow repair owner;
- independent exact-head review;
- explicit upstream authority.

## Stops

- Do not call consume-on-attempt semantics defective merely because presentation returns no result.
- Do not assume every HAL error leaves the platform image retryable.
- Do not infer a resource leak from source lifetime alone.
- Do not conflate pre-HAL preparation failure with a HAL-consumed status.
- Do not treat noop behavior as platform ownership proof.
- Do not begin with a breaking public API redesign.
- Do not contact upstream without authorization.

## Current decision

Keep the browser and wrapper branch characterization-only. Use the separate noop experiment to answer `PreparationFailedDetached` deterministically, then validate the surviving hypothesis on DX12 and Vulkan.