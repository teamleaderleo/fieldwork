# Shared-example surface recovery outcome audit

State: source-read; no example execution

Fieldwork issue: #116

Source: `examples/features/src/framework.rs` at the pinned wgpu revision

Upstream contact authorized: false

## Why this matters

The shared feature-example framework is repository-owned user guidance expressed as executable code. Its recovery choices are likely to be copied by applications and influence how API status documentation is interpreted.

The framework owns a `SurfaceWrapper` with two independent fields:

```text
surface: Option<Surface>
config: Option<SurfaceConfiguration>
```

The wrapper stores its own configuration immediately after calling public `Surface::configure`. It has no acceptance receipt from the backend.

## Configuration ownership

### Resume

On resume, the framework:

1. computes nonzero window dimensions;
2. creates or reuses a surface;
3. asks for default capabilities-based configuration;
4. adjusts format/view format and frame latency;
5. calls `surface.configure`;
6. stores the request in `self.config`.

If browser configuration is contained as a nonfatal rejection, step 6 still makes the rejected request the framework's authoritative local configuration.

### Resize

On resize, the framework mutates `self.config.width` and `.height` in place before calling `surface.configure`.

If reconfiguration fails:

- the local configuration remains the requested new extent;
- the public surface cache also publishes the request;
- native core may preserve an older accepted presentation;
- browser WebGPU may already have mutated canvas extent before rejecting another field.

The example therefore has no retained accepted configuration distinct from last requested configuration.

## Acquisition outcome table

| Public outcome | Framework action | Immediate consequence | Risk or question |
| --- | --- | --- | --- |
| `Success(frame)` | return frame | render and present | aligned |
| `Timeout` | skip frame | retry on future redraw | aligned |
| `Occluded` | skip frame | event loop waits for visibility/redraw | aligned |
| `Suboptimal(frame)` | drop usable frame, configure stored request, acquire again | current frame is discarded; retry must be success/suboptimal or example panics | legal but may waste a usable frame; browser discard is no-op |
| `Outdated` | configure stored request, acquire again | retry must be success/suboptimal or panic | depends on stored request being valid and previously accepted |
| `Validation` | `unreachable!` | process panics if the variant reaches this code | assumes no error scope means validation cannot be returned normally |
| `Lost` | recreate surface, configure stored request, acquire again | retry must be success/suboptimal or panic | wrong recovery when stored configuration itself caused `Lost` |

## Rejected-configuration loop

The source-predicted browser sequence is:

```text
configure(request) is rejected without abort
→ framework stores request
→ public acquisition returns Lost
→ framework recreates surface
→ framework reapplies stored request
→ request is rejected again
→ acquisition returns Lost again
→ framework panics
```

Surface recreation is useful for actual surface loss with a still-valid configuration. It cannot make an unsupported format, color space, alpha mode, present mode, or invalid extent request valid.

## Unconfigured browser acquisition

The framework normally calls configure during resume before drawing. However, nonfatal startup rejection can leave the browser context effectively unconfigured while the framework believes it has completed configuration.

The new owned-fork characterization checks the lower-level state directly:

```text
public config = None
raw context config = null
public acquisition = Lost
```

This demonstrates why `Lost` cannot by itself tell the example whether to configure, select a fallback, recreate, or rebuild the device.

## Suboptimal handling

`Suboptimal` carries a usable `SurfaceTexture`. The framework immediately drops it, which invokes the public unpresented-frame cleanup path, then reconfigures and retries.

Questions for execution and review:

- Is dropping the current frame preferable to presenting it and reconfiguring afterward?
- Does immediate reconfiguration after browser no-op discard produce any observable warning or invalidation issue?
- Can repeated suboptimal results create a retry panic even though each returned texture is usable?
- Should examples demonstrate both latency-sensitive and continuity-sensitive policies rather than one universal branch?

No defect is claimed here; this is an example-policy decision.

## Validation assumption

The framework marks `Validation` unreachable because it registers no error scope and expects validation errors to panic through the default handler.

That assumption is true for the inspected native core path when an error reaches the default sink. It is not a general statement about every backend implementation or future error-routing change.

If browser acquisition classification becomes more truthful and begins returning `Validation`, this example branch must be updated simultaneously.

## Presentation outcome

After rendering, the framework calls `Queue::present` and does not receive a result.

Public `Queue::present` marks the frame presented before backend present. Native present errors are routed to the device error sink. Therefore:

```text
public frame ownership transferred
backend present may fail
error delivered separately
frame drop does not run discard/release
```

This appears consistent with core consuming the acquired presentation texture before HAL present, but it deserves a fault-injection control if presentation errors become part of a repair.

## Candidate example repairs

Do not apply these before execution selects semantics.

### A — accepted configuration record

Retain last accepted configuration separately from the latest requested candidate. Use the accepted configuration for actual surface-loss recreation.

### B — capability revalidation

Before reapplying a stored request after `Lost`, query capabilities and confirm the request is still valid. Select an explicit fallback or terminate with a diagnostic when it is not.

### C — typed internal rejection reason

If public or private surface state can distinguish rejected configuration from actual loss, route configuration rejection to correction rather than recreation.

### D — bounded retry without panic

After one recovery attempt, return a structured terminal outcome to the example shell instead of panicking with only the second acquisition status.

### E — document policy choices

Keep the code small but explicitly state that it is an example policy, not universal recovery guidance.

## Test matrix

### Startup

- supported configuration;
- unsupported manually requested color space;
- raw browser configure exception;
- no browser-WebGPU adapter;
- device loss during initial setup.

### Resize

- normal resize;
- resize to zero and framework clamping;
- rejected reconfiguration after accepted baseline;
- canvas extent mutation before another field rejects;
- rapid successive sizes.

### Acquisition

- timeout;
- occlusion;
- suboptimal usable frame;
- outdated;
- actual surface loss;
- unconfigured invalid state;
- device loss;
- injected raw acquisition exception.

### Presentation

- successful present;
- no rendering before present;
- unpresented drop;
- present failure routed to error scope;
- panic after acquisition before presentation.

## Current disposition

This artifact strengthens the user-facing consequence of the configuration-acceptance seam, but remains source-only.

Do not patch all examples yet. First execute the browser characterization and core-backed metadata control, then select whether the narrowest useful contribution is:

- tests and documentation;
- example recovery alignment;
- internal accepted-state tracking;
- typed failure classification;
- no change after clarified intended semantics.
