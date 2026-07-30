# wgpu presentation attempt, status, and ownership audit

State: source-read plus target-test-prepared; not compiled or executed

Fieldwork issue: #116

Fieldwork draft PR: #126

Owned fork draft: `teamleaderleo/wgpu#1`

Upstream contact authorized: false

## Exact records

- pinned source tree: [gfx-rs/wgpu@2eddc8c7b2fedd4267f5004745a8bc42974e17a0](https://redirect.github.com/gfx-rs/wgpu/commit/2eddc8c7b2fedd4267f5004745a8bc42974e17a0)
- current upstream tree checked: [gfx-rs/wgpu@c079e55f534d713a60aef145f6df0255b7ddcdc4](https://redirect.github.com/gfx-rs/wgpu/commit/c079e55f534d713a60aef145f6df0255b7ddcdc4)
- current upstream distance from the pin: seven commits
- owned-fork characterization head: `teamleaderleo/wgpu@3d076485509f6b3f8381de8074bfbdef17bc4133`
- historical presentation rewrite: [gfx-rs/wgpu#9222](https://redirect.github.com/gfx-rs/wgpu/pull/9222)

The current upstream changes between the pinned and checked trees do not alter the public queue/surface-texture API, browser surface adapter, core presentation implementation, HAL presentation contract, or shared example recovery framework. The source questions below therefore remain live on the checked current tree. The existing wasm test file has unrelated test-macro churn, so the fork patch still needs rebasing and execution before it can be called current-target evidence.

## In simple words

Presentation is not one event.

The current path crosses at least these boundaries:

```text
application gives SurfaceTexture to Queue::present
→ public wrapper marks the value as presented
→ backend dispatch begins
→ core removes the acquired texture from Surface presentation state
→ core may clear an unused texture and transition it to PRESENT
→ HAL queue consumes the raw surface texture
→ HAL returns success or a surface/device failure
→ core classifies the result
→ public backend wrapper reports errors through an error sink and discards non-error statuses
```

The important question is not merely whether `present` can fail. It is:

> At which boundary is ownership irreversibly transferred, which later outcomes remain observable, and which cleanup path owns a frame when failure occurs between boundaries?

## Public ownership commit

Public `Queue::present` currently:

1. takes a `SurfaceTexture` by value;
2. sets its internal `presented` flag to `true`;
3. calls backend `QueueInterface::present`;
4. returns `()`.

`SurfaceTexture::drop` calls:

- `texture_discard` for an ordinary unpresented drop;
- `texture_release` during unwinding;
- neither path once `presented` is true.

The public API therefore commits ownership before backend dispatch. This is not automatically wrong: the HAL queue contract also consumes the raw surface texture by value even when HAL presentation returns an error. A failed presentation attempt may still consume the platform image.

The observable public consequence is stricter:

- the caller cannot retry or inspect the same frame;
- the caller receives no presentation result;
- drop cleanup is suppressed even if custom dispatch panics;
- any recovery information must arrive through a separate error or device/surface channel.

## Prepared public-wrapper characterization

The owned fork now adds two private unit tests beside `wgpu/src/api/surface_texture.rs`.

### Ordinary drop control

```text
construct custom SurfaceTexture
→ drop without present
→ custom texture_discard count = 1
→ custom texture_release count = 0
```

### Injected present panic

```text
construct custom Queue and SurfaceTexture
→ Queue::present marks frame presented
→ custom QueueInterface::present records one call and panics
→ catch unwind outside Queue::present
→ texture_discard count = 0
→ texture_release count = 0
```

This test characterizes the public ownership boundary. It does not prove a native leak or establish that ownership should be rolled back after dispatch begins.

Execution status: authored and source-self-reviewed only. No `cargo test`, rustfmt, clippy, or compile receipt exists.

## Core ownership transition

Native core has an additional transition before HAL consumption.

`Queue::present` in core:

1. locks surface presentation state;
2. removes `acquired_texture` with `take()`;
3. calls `prepare_surface_texture_for_present`;
4. snatches the raw surface texture handle;
5. passes the raw texture by value to HAL `present`.

The acquired texture is therefore no longer attached to the surface before preparation begins.

That matters because preparation can fail before HAL receives the frame.

## Pre-HAL failure classes

`prepare_surface_texture_for_present` can fail while:

- allocating a submission;
- encoding the automatic clear for a never-used frame;
- translating a clear failure into device loss;
- retrieving the raw texture handle;
- submitting the clear/transition mini-submission.

In those paths:

```text
surface acquired_texture = already removed
HAL present = not called yet
public SurfaceTexture = already consumed
public presented flag = true
ordinary discard/release = suppressed
```

The core `Texture` drop implementation destroys the internal clear view for a surface texture, but only calls ordinary `destroy_texture` for native non-surface textures. Surface discard is a distinct operation on the `Surface`, not a generic `TextureInner::Surface` drop action.

This creates a source-supported cleanup question:

> When preparation fails after the surface's acquired texture has been taken but before HAL consumes it, which operation returns or discards the platform surface image?

This is not yet a leak claim. A backend-owned raw texture destructor, pending-write ownership, device-loss teardown, or platform contract may still make the state safe. The current source path needs an executable fault-injection control.

## HAL and core result classification

HAL presentation can return:

- success;
- timeout;
- occluded;
- lost;
- outdated;
- device error;
- another backend-specific failure.

Core preserves those distinctions initially:

- success becomes `Good`;
- timeout, occluded, lost, and outdated remain typed statuses;
- device failure becomes an error;
- an unclassified backend failure is logged and becomes `SurfaceError::Invalid`.

The public core backend then discards every successful status from `surface_present` and returns `()` from `QueueInterface::present`. Only errors are routed into the device error sink.

Consequences:

```text
HAL timeout / occluded / lost / outdated at present
→ core knows the status
→ public Queue::present returns ()
→ application receives no typed presentation outcome
```

This differs from acquisition, where the public API gives explicit `Timeout`, `Occluded`, `Outdated`, and `Lost` variants with recovery instructions.

The status loss may be intentional because WebGPU presentation itself is fire-and-forget and browser presentation dispatch is effectively a no-op. The question is whether native-only status information should remain internal, enter diagnostics, or inform a later acquisition result. Do not infer that `Queue::present` must immediately return `Result`.

## Historical evidence

Presentation and surface-image ownership have caused real failures before.

### Unpresented-frame cleanup

[wgpu issue 4056](https://redirect.github.com/gfx-rs/wgpu/issues/4056) reported Vulkan resources surviving device destruction when a surface frame was dropped without presentation. That issue was completed after cleanup changes.

### Presenting with no submitted work

[wgpu issue 2635](https://redirect.github.com/gfx-rs/wgpu/issues/2635) reported swapchain exhaustion after presenting frames without rendering work.

[wgpu issue 6748](https://redirect.github.com/gfx-rs/wgpu/issues/6748) later reported Vulkan synchronization hazards when presenting an acquired-but-unused image.

### Panic cleanup

[wgpu issue 8243](https://redirect.github.com/gfx-rs/wgpu/issues/8243) motivated the current release-during-unwind path so panic cleanup would not trigger a second panic while destroying an in-use acquire semaphore.

### Driver/backend presentation failure

[wgpu issue 5259](https://redirect.github.com/gfx-rs/wgpu/issues/5259) records a GL presentation failure when a window is hidden or minimized.

### Queue-owned presentation redesign

[wgpu pull request 9222](https://redirect.github.com/gfx-rs/wgpu/pull/9222) moved presentation onto `Queue`, added automatic clear/transition for unused frames, and attempted to retain surface textures until presentation completion.

Its review exposed a key fact: presentation completion cannot be modeled naively as an ordinary fence-signaled submission. Review found risks around synthetic presentation indices, waits that could target fence values never signaled by a submission, multiple pending presents, and failure to drain retained frames after queue-idle waits.

That history argues for exact state and lifetime tests before changing the public API.

## Current state model

Presentation now needs its own state vocabulary, separate from configuration disposition.

Provisional states:

### `Acquired`

The surface still owns an acquired texture record and the public frame has not entered presentation.

### `PresentationAttemptCommitted`

The public frame has been consumed and drop cleanup is suppressed. Backend dispatch may not yet have completed.

### `DetachedForPreparation`

Core has removed the acquired texture from surface state, but HAL has not yet consumed it.

### `PreparedForPresentation`

Automatic clear and PRESENT transition, if needed, have succeeded.

### `HalConsumed`

The raw texture has been passed by value to HAL presentation.

### `Presented`

HAL accepted the present operation.

### `ConsumedWithStatus`

HAL consumed the frame but returned timeout, occlusion, lost, or outdated.

### `PreparationFailedDetached`

Core detached the frame, then failed before HAL consumption.

### `ConsumedWithError`

HAL or device processing consumed ownership and returned an error routed to the error sink.

The names are provisional. The key distinction is between failure before and after HAL consumes the raw image.

## Core-level executable probe

A useful test must inject failure at the exact preparation boundary rather than only panic a custom public backend.

### Required controls

1. Configure a fake or controlled core surface and acquire one frame.
2. Prove the surface records one acquired texture.
3. Trigger a selected preparation failure after core takes `acquired_texture`.
4. Record whether HAL `present` was called.
5. Record whether HAL surface discard was called.
6. Record whether a later acquisition succeeds, returns `AlreadyAcquired`, times out, or exposes another state.
7. Record clear-view and raw surface-texture destruction.
8. Repeat with successful preparation plus injected HAL statuses.

### Failure injection priority

Prefer, in order:

1. an existing fake/dynamic HAL surface and queue fixture;
2. a narrow test-only hook around `prepare_surface_texture_for_present`;
3. a custom core backend fixture with counters;
4. a real backend fault only when deterministic injection is impossible.

Do not broaden the noop backend into a full presentation simulator unless several independent tests need it.

### Matrix

| Injection point | HAL present called | Expected ownership question |
| --- | --- | --- |
| submission allocation failure | no | who releases the acquired platform image? |
| automatic clear failure | no | does pending-write or texture drop release it? |
| raw texture lookup failure | no | is the surface left reusable? |
| mini-submit failure | no | is partially prepared work retained safely? |
| HAL timeout | yes | is status intentionally discarded publicly? |
| HAL occluded | yes | does next acquisition reveal recovery state? |
| HAL lost/outdated | yes | is the later typed acquisition sufficient? |
| HAL device error | yes | does the device-loss channel fully explain ownership? |
| backend panic | unknown/custom | public wrapper suppresses discard/release after commit |

## Public/API questions after execution

Only after the core control runs:

- Is public fire-and-forget presentation intentional across native and browser backends?
- Should native presentation status influence the next acquisition result rather than the immediate call?
- Should error-sink delivery name that a frame was consumed?
- Does preparation failure need a dedicated cleanup guard before `acquired_texture.take()` becomes irreversible?
- Should the internal dispatch method return a presentation disposition while public `Queue::present` stays `()`?
- Can custom backends preserve compatibility without implementing a new public status contract?

## Promotion gate

Do not promote a presentation finding until it has:

- one compiled public-wrapper characterization;
- one executed core preparation-failure control;
- one successful-present negative control;
- explicit proof of whether HAL present and surface discard were called;
- subsequent acquisition behavior;
- exact pinned and current-source receipts;
- a narrow owner in public wrapper, core preparation, HAL contract, diagnostics, or documentation;
- independent exact-head review;
- explicit authorization before any upstream contact.

## Stops

- Do not call consume-on-attempt semantics a defect merely because `present` returns no result.
- Do not assume every HAL presentation error leaves the platform image retryable.
- Do not infer a resource leak from source lifetime alone.
- Do not conflate pre-HAL preparation failure with a HAL-consumed present status.
- Do not add a public `Queue::present -> Result` API before proving an application-actionable consequence.
- Do not claim the wrapper unit test is a native/core reproduction.
- Do not contact upstream without authorization.

## Current decision

Retain the new wrapper tests as a characterization carrier and build the next probe around `PreparationFailedDetached`.

The most valuable executable question is:

> After core removes an acquired surface texture and preparation fails before HAL presentation, does the backend surface image receive a correct release/discard operation, and can the surface acquire again without teardown?
