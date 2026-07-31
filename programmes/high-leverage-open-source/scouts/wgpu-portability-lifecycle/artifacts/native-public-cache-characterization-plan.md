# Native/public surface-cache characterization plan

State: source-confirmed design; not implemented or executed

Fieldwork issue: #116

Owned fork: `teamleaderleo/wgpu`

Upstream contact authorized: false

## Question

Can public `Surface` state and public `SurfaceTexture` metadata follow a rejected configuration while the backend retains and acquires from an earlier accepted configuration?

The source path supports that possibility:

1. public `Surface::configure` dispatches to the backend;
2. native core validates the proposed configuration before removing its existing accepted presentation;
3. a validation failure returns through the device error sink while preserving the old presentation;
4. the dispatch method returns `()`;
5. public `Surface::configure` caches the rejected request unconditionally;
6. core acquisition can still use the old accepted presentation;
7. public `Surface::get_current_texture` constructs the exposed texture descriptor from the public cache.

This can affect observable texture width, height, format, and usage, not only the wording of `get_configuration()`.

## Preferred test location

Add a private unit test beside the public surface wrapper:

```text
wgpu/src/api/surface.rs
```

Gate it to test builds with the custom and noop features available.

Why this location:

- the test needs to construct `Surface` from its private fields;
- it needs direct access to the public cache and dispatch boundary;
- public custom APIs do not expose a small `Surface::from_custom` constructor;
- an external integration test would require implementing an unrelated custom instance, adapter, and device stack;
- the unit test can use `Device::noop()` while keeping only the surface and returned texture custom.

## Minimal fake objects

### Rejecting surface

Implement only `SurfaceInterface`.

State:

- accepted configuration or accepted width/height;
- configure call count;
- optional record of the latest rejected request.

Behavior:

- first configure call records the baseline as accepted;
- second configure call records the request but deliberately leaves accepted state unchanged;
- acquisition returns `SurfaceStatus::Good` plus a custom texture;
- capabilities are irrelevant to this wrapper-level control and may return a minimal value.

The fake does not claim to reproduce native core validation. It characterizes the public dispatch contract: a backend can return after not accepting the request, and the wrapper has no acceptance signal.

### Custom texture

Implement the minimal `TextureInterface` methods.

The custom texture carries identity only. Public `Surface::get_current_texture` supplies its descriptor from the wrapper cache, which is the behavior under test.

### Surface-output detail

Implement `SurfaceOutputDetailInterface` with no-op discard and release. This permits the returned frame to drop safely without requiring a compatible custom queue.

### Device

Use `Device::noop()`.

The fake surface ignores device internals, so a custom device implementation is unnecessary.

## Characterization sequence

Use a baseline such as:

```text
width = 2
height = 2
format = Bgra8Unorm
usage = RENDER_ATTACHMENT
```

Then:

1. configure the surface with the baseline;
2. assert fake backend accepted state is the baseline;
3. assert public `get_configuration()` is the baseline;
4. create a rejected request that changes width, height, format, or usage;
5. configure with the rejected request;
6. assert fake backend accepted state remains the baseline;
7. assert public `get_configuration()` is the rejected request;
8. acquire a successful public surface texture;
9. assert `texture.width()`, `height()`, `format()`, and `usage()` follow the rejected request;
10. assert fake backend state still reports the baseline.

Expected current behavior:

```text
backend accepted state = baseline
public configuration cache = rejected request
public texture descriptor = rejected request
```

## Why this is only a characterization

A custom backend is allowed to define its own failure reporting. The unit test therefore proves the public wrapper's inability to acceptance-bind its cache; it does not by itself prove a native-core defect.

The native-core source path supplies the reason to run the same semantic control against core later:

- validation failure can preserve the old presentation;
- HAL configure failure does not preserve it;
- public caching currently treats both returns alike.

## Native/core follow-up

After the wrapper test compiles, add the smallest executable core-backed fixture available.

Priority order:

1. an existing real surface test environment with an intentionally invalid second configuration and an error scope;
2. a focused core test with injectable surface capabilities;
3. a dedicated fake HAL surface only if the first two are impossible.

Required assertions:

- baseline presentation remains accepted after validation rejection;
- error scope receives the expected validation error;
- public cache changes or does not change;
- subsequent acquisition succeeds or fails;
- returned public texture metadata matches the actual accepted presentation;
- a later valid reconfiguration recovers cleanly.

## Rejected approach: expand the noop HAL surface

The noop backend currently supports resource validation but does not provide meaningful surface capabilities or presentation.

Adding surface creation, capabilities, configuration, acquisition, and output-detail behavior merely for this test would:

- broaden a deliberately minimal backend;
- affect unrelated tests and backend assumptions;
- create a second surface simulation whose fidelity would itself need review;
- obscure the small public-wrapper contract being measured.

Do not expand noop unless multiple independent surface tests justify that infrastructure.

## Desired regression after semantics are chosen

The final regression should not permanently assert misleading state.

Once maintainers choose the contract, convert the characterization to one of these desired outcomes:

### Acceptance-bound cache

```text
rejected configure
→ backend accepted state remains baseline
→ public get_configuration remains baseline
→ public texture metadata remains baseline
```

### Explicit requested-state contract

```text
public API clearly names the value as last requested
→ acquisition and texture metadata use separately retained accepted state
→ rejected request cannot corrupt texture descriptors
```

### Rejection clears usable state

```text
rejected configure
→ public accepted configuration becomes None
→ acquisition cannot manufacture a texture descriptor from rejected state
→ typed result explains the required corrective action
```

The browser and native measurements should determine which contract is viable.

## Stop conditions

- Do not treat the custom wrapper test alone as proof of native-core runtime behavior.
- Do not implement a full custom device stack when `Device::noop()` is sufficient.
- Do not expand noop surface support for one test.
- Do not lock current misleading behavior into a permanent regression after a repair is selected.
- Do not propose public API changes before browser and core-backed controls execute.
