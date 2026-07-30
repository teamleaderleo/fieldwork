# wgpu fork characterization log

State: browser characterizations authored and source-self-reviewed; not compiled or executed

Fieldwork issue: #116

Fieldwork PR: #126

Owned fork draft: `teamleaderleo/wgpu#1`

Upstream contact authorized: false

## Exact records

- [upstream/fork base](https://redirect.github.com/gfx-rs/wgpu/commit/2eddc8c7b2fedd4267f5004745a8bc42974e17a0)
- owned fork: `teamleaderleo/wgpu`
- branch: `fieldwork/surface-config-rejection-state`
- exact test head: `455a8711984b0166533fa3441d65a9e58777d9ca`
- changed file: `tests/tests/wgpu-gpu/create_surface_error.rs`

The fork branch started from the exact pinned upstream tree. It remains a characterization carrier, not a selected repair or upstream-ready patch.

## Current prepared tests

### Existing creation error

Retains the unusable-canvas control where a prior 2D context makes surface creation fail with the expected error.

### Unconfigured browser acquisition

Prepared assertions:

```text
public Surface::get_configuration = None
raw GPUCanvasContext.getConfiguration = null
public Surface::get_current_texture = Lost
raw GPUCanvasContext remains unconfigured
```

Raw invalid state is therefore contained as `Lost`, although configuration—not surface recreation—is the missing operation.

Native core does not expose the same recovery semantics: acquisition errors are routed as validation when a configured error sink exists and are fatal by default before a successful configuration establishes that sink.

### Zero-sized configuration applied with validation

Prepared sequence:

1. create an explicit browser-WebGPU adapter and 1×1 canvas;
2. obtain a supported default configuration;
3. set request width to zero;
4. push a validation error scope;
5. call public `Surface::configure`;
6. require a captured validation error;
7. assert public cache contains the zero-width request;
8. assert canvas is 0×1;
9. assert raw context still reports configured state;
10. push another validation scope;
11. acquire through public wgpu;
12. require `Success` or `Suboptimal` carrying a 0×1 public texture;
13. require a captured acquisition validation error;
14. drop the error texture;
15. restore and configure the supported 1×1 baseline;
16. present successfully.

This characterizes WebGPU's error-object model rather than a synchronous rejection. Validation can coexist with installed configuration state, and public `Success` can carry an unusable error texture while the diagnostic arrives separately.

### Rejected configuration after an accepted baseline

Prepared sequence:

1. configure and present a supported 2×2 baseline;
2. create a 7×5 request with unsupported `ExtendedSrgbLinear`;
3. prove the color space is absent from capabilities;
4. call public `Surface::configure`;
5. assert public cache publishes the rejected 7×5 request;
6. assert canvas extent changed to 7×5;
7. assert wgpu acquisition reports `Lost`;
8. assert raw context still reports configured state;
9. acquire a raw browser texture and assert 7×5 dimensions;
10. apply the supported 2×2 baseline to the same surface and present;
11. recreate a surface, retry the rejected request, and observe `Lost` again;
12. apply the baseline to the recreated surface and present.

## Three distinct configure states

The prepared tests now distinguish:

### Rejected/unconfigured

No accepted configuration exists, and acquisition is invalid. Browser wgpu currently reports `Lost`.

### Applied with diagnostic

Zero-sized raw canvas configuration emits validation but remains installed. Repairing the canvas extent can make raw acquisition usable without another raw configure call.

### Rejected while other state mutates

Local color-space rejection occurs before raw configure but after canvas extent mutation. Raw configuration can remain old while canvas and public Rust cache reflect the rejected request.

This is why a binary internal configure result is likely insufficient.

## Partial-state finding

For the locally rejected color-space path, source predicts:

```text
raw accepted configuration = earlier baseline
canvas extent = rejected request
public configuration cache = rejected request
configure_failed = true
public acquisition = Lost
raw acquisition = usable at resized extent
```

The state is not complete preservation of the prior configuration.

## Runner strategy

The ordinary wasm runtime runner builds with `webgl,exhaust`. The shared initializer removes `BROWSER_WEBGPU` when WebGL is enabled.

The tests remain registered in the normal wasm binary but construct a separate explicit browser-WebGPU instance and assert the selected adapter backend. No second top-level runner or external application was added.

## Source self-review

Completed checks:

- existing wasm-only module retained;
- three new cases have distinct names and responsibilities;
- explicit browser-WebGPU backend assertions used where a device is requested;
- canvases explicitly sized;
- validation error scopes retained by value and popped in order;
- baseline and fallback presentation controls retained;
- unsupported capability proved before rejection;
- raw and public state asserted independently;
- same-surface recovery separated from recreation;
- zero-size validation separated from synchronous rejection;
- canvas extent mutation made observable;
- no direct upstream interaction added.

Potential compile/runtime risks still requiring execution:

- browser-WebGPU adapter availability under Playwright/SwiftShader;
- exact generated test filters;
- error-scope timing around raw canvas configure and acquisition;
- whether the error texture reaches `Success` or `Suboptimal` exactly as source predicts;
- raw `GPUTexture.width` and `height` bindings;
- console-error treatment by test orchestration;
- formatting and clippy;
- direct raw texture acquisition alongside the wrapper.

## Execution status

**Not executed.**

For exact head `455a8711984b0166533fa3441d65a9e58777d9ca`:

- no fork workflow runs or commit statuses are known;
- the available container has no Rust toolchain;
- no compile, rustfmt, clippy, wasm build, Playwright, browser, or GPU result is claimed.

Expected first validation sequence:

```text
cargo fmt --check
cargo clippy --target wasm32-unknown-unknown --tests --features glsl,spirv
cargo xtask test-wasm --list
cargo xtask test-wasm -- <exact listed unconfigured-browser test filter>
cargo xtask test-wasm -- <exact listed zero-size test filter>
cargo xtask test-wasm -- <exact listed rejected-configuration test filter>
```

The filters must come from `--list`; they must not be guessed.

## Related source consequences

### Native public metadata

Native core can preserve an earlier presentation after validation rejection while the public wrapper caches the request. Public texture descriptors are built from that cache. A private wrapper characterization and a real core-backed control remain necessary.

### Acquisition exception classification

The browser backend maps every thrown raw acquisition exception to `Lost`. Tests must distinguish invalid state, device loss, internal/out-of-memory failure, and transient browser exceptions.

### Public success and error textures

The zero-size path demonstrates that successful object return and successful use are different. Any documentation or example repair must preserve WebGPU's validation/error-object model.

### Presentation outcome

Public `Queue::present` marks a frame presented before backend present, while native errors are routed separately. Presentation failure and public ownership transfer are separate states worth later fault injection.

## Current decision

Keep this PR draft and characterization-only.

Do not:

- claim target execution;
- promote it to Delivery Desk;
- convert current behavior into permanent desired regressions before semantics are selected;
- redesign the public API first;
- contact upstream without explicit authority.
