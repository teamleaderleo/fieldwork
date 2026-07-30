# Protocol-aligned wgpu status and next probes

State: active exploration; source-read and target-test-prepared evidence only

Fieldwork issue: #116

Fieldwork draft PR: #126

Owned fork draft: `teamleaderleo/wgpu#1`

Upstream contact authorized: false

## Current exact records

- released baseline: `wgpu v30.0.0`
- pinned source revision: [wgpu source revision](https://redirect.github.com/gfx-rs/wgpu/commit/2eddc8c7b2fedd4267f5004745a8bc42974e17a0)
- owned fork test head: `38c9498bdae8f0ddfdc6a04c6d763ce889f3f5ad`
- review-contract head: Fieldwork PR #143 at `dd7f0364d5dc195b3fa651f95192cf6078810a6e`
- Delivery Desk protocol head: Fieldwork PR #161 at `b1e402ee47aa2e2842d52e8f0ab42d4ab0501916`

Both protocol heads have passed Fieldwork integrity and external-reference policy checks. They remain draft because process acceptance requires independent review, not only green CI.

## Claim-scoped evidence

| Claim | Evidence class | Current receipt | Important exclusion |
| --- | --- | --- | --- |
| Browser-only `ExtendedSrgbLinear` mapping rejection occurs before raw `GPUCanvasContext.configure` | source-read | pinned browser backend source and fork characterization | browser test has not executed |
| The raw browser canvas should retain the earlier accepted baseline after that local rejection | source-read plus target-test-prepared | raw-context assertions authored in owned fork PR #1 | no Playwright/browser receipt |
| Public `Surface::get_configuration()` publishes the rejected request | source-read plus target-test-prepared | public wrapper source and fork characterization | no executed target result |
| wgpu reports `Lost` for the local rejection while a supported same-surface reconfiguration should recover | source-read plus target-test-prepared | browser failure flag and authored recovery controls | no browser adapter receipt |
| Native/core validation can preserve the earlier accepted presentation | source-read | core configure ordering | no core-backed runtime control |
| Public texture metadata can follow rejected cache values while acquisition uses earlier accepted state | source-read risk | wrapper descriptor construction plus core ordering | wrapper unit test and core-backed control are not implemented |
| Ordinary wasm runtime initialization does not exercise browser WebGPU | source-read | test runner feature and initializer paths | availability under the actual Playwright image remains unmeasured |

No claim is `target-executed`, `integration-executed`, or `full-gate`.

## Delivery Desk position

This lane does not belong on Delivery Desk #160 yet.

The Delivery Desk is for selected implementations, bounded final gates, clean application, receipt transfer, merge, or closeout. This lane still has:

- more than one plausible repair boundary;
- no executed browser characterization;
- no native/core runtime control;
- no accepted implementation disposition;
- no canonical direct repair branch;
- no named full repository gate for a selected candidate.

The correct routing is to keep #116 and PR #126 as the canonical exploration record. A future desk entry becomes appropriate only after the browser and native controls select one bounded implementation or documentation/example correction.

## Protocol lessons from this lane

This case supports the current protocol repairs:

1. **Evidence must be claim-scoped.** The browser source mechanism, authored target test, native source risk, and unexecuted integration implications are different evidence classes.
2. **A disposition needs identity.** Any acceptance must name the reviewed head, reviewed issue/input generation, and durable receipt.
3. **The clearing condition is a bundle.** Browser execution, native control, source-only candidate publication, exact-head review, and carrier cleanup may be inseparable but must remain explicit.
4. **Green CI is not acceptance.** Fieldwork protocol checks validate repository hygiene; they do not execute the wgpu browser test.
5. **Execution carriers are not canonical repairs.** The owned fork PR is currently a characterization carrier, not a landing-ready source fix.
6. **Theory revision is mandatory.** A real browser result that contradicts the source prediction must rewrite the candidate rather than be explained away.

## Next probe queue

### P1 — Execute the browser characterization

Required receipts:

- exact fork head;
- listed test identity from the repository runner;
- build and lint commands actually executed;
- Chromium/WebGPU adapter information;
- raw canvas configuration before and after rejection;
- raw texture acquisition after rejection;
- wgpu typed acquisition result;
- same-surface valid recovery;
- recreated-surface invalid retry control.

Stop or revise if browser WebGPU is unavailable in the runner, the selected color space is unexpectedly supported, or raw context access changes the surface ownership assumptions.

### P1 — Add the public-wrapper characterization safely

Preferred location: a private unit-test module beside `wgpu/src/api/surface.rs`.

Use a noop device and a minimal custom surface/texture/output-detail implementation. The fake accepts a baseline, ignores a second request, and returns a texture. Assert separately:

- backend accepted state;
- public configuration cache;
- public texture width, height, format, and usage.

Do not replace a large source file from truncated connector content. Use a safe checkout, complete-file edit, or tree/commit patch path.

### P1 — Build a core-backed validation control

After the wrapper characterization compiles, prove the real core ordering with the smallest available fixture:

- accepted baseline presentation;
- intentionally invalid second configuration;
- captured validation error;
- old presentation retained;
- subsequent acquisition outcome;
- public metadata compared with actual accepted configuration;
- later valid recovery.

### P2 — Measure raw rejected reconfiguration semantics

The current WebGPU CTS covers synchronous rejection from an initially unconfigured context but not:

```text
valid accepted configuration
→ rejected reconfiguration
→ inspect retained configuration
→ inspect texture acquisition
```

Measure this separately from wgpu's local color-space pre-rejection. A browser-thrown rejection may preserve, clear, or otherwise alter prior state differently.

### P2 — Split acquisition exceptions from configuration rejection

Trace and test the browser path where raw `getCurrentTexture` throws. Determine whether every exception should become `Lost`, or whether validation, out-of-memory, device loss, and transient acquisition failures can be preserved more truthfully.

### P2 — Audit example recovery by outcome

Build an outcome table for `Success`, `Suboptimal`, `Timeout`, `Occluded`, `Outdated`, `Lost`, and `Validation` across shared examples. Check that examples:

- present usable `Suboptimal` textures before reconfiguration when appropriate;
- do not recreate for configuration rejection while retrying the same invalid request;
- distinguish device loss from surface-only loss;
- avoid dropping useful diagnostics.

### P3 — Surface-texture release and discard

Compare browser and native ownership when a frame is:

- presented;
- dropped without presentation;
- released during unwinding;
- invalidated by reconfiguration;
- retained across device or surface loss.

Look for duplicate release, missing discard, stale output detail, and backend-specific cleanup assumptions.

### P3 — Custom-backend compatibility

Before changing `SurfaceInterface::configure`, inventory custom implementations and downstream construction patterns. A private disposition should not become a public compatibility tax until the measured state benefit is clear.

## Promotion gate

A repair candidate may be promoted only when it has:

- one reproduced contradiction or one precise documentation/example mismatch;
- exact source and execution receipts;
- at least one negative control;
- a selected owning subsystem;
- one narrow desired contract;
- a source-only candidate branch;
- independent exact-head review;
- no upstream contact without explicit authority.

## Stops

- Do not put this lane on the Delivery Desk merely because the source map is extensive.
- Do not upgrade authored tests to executed evidence.
- Do not call the raw browser surface lost when wgpu rejected before calling the browser.
- Do not treat a wrapper-level custom test alone as proof of native core behavior.
- Do not begin with a breaking public `Surface::configure -> Result` redesign.
- Do not manufacture a production integration to justify the work.
