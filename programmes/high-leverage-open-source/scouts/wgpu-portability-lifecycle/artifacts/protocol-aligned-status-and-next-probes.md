# Protocol-aligned wgpu status and next probes

State: active exploration; `source-read` and `target-test-prepared` evidence only

Fieldwork issue: #116

Fieldwork draft PR: #126

Owned fork draft: `teamleaderleo/wgpu#1`

Upstream contact authorized: false

## Current exact records

- released baseline: `wgpu v30.0.0`
- [wgpu source revision](https://redirect.github.com/gfx-rs/wgpu/commit/2eddc8c7b2fedd4267f5004745a8bc42974e17a0)
- [WebGPU editor-draft source](https://redirect.github.com/gpuweb/gpuweb/commit/d390da5f80f18e82d9535a40c6f2f1f65e6884ae)
- [WebGPU CTS source](https://redirect.github.com/gpuweb/cts/commit/dc20b8682aa71ff31f135de6ae7f8acaa2e16383)
- owned fork test head: `77c46ce89efab608b1d377b3d6cecf18b006fb72`
- review-contract head: Fieldwork PR #143 at `dd7f0364d5dc195b3fa651f95192cf6078810a6e`
- Delivery Desk protocol head: Fieldwork PR #161 at `b1e402ee47aa2e2842d52e8f0ab42d4ab0501916`

Both protocol heads passed Fieldwork integrity and external-reference policy. They remain draft because process acceptance requires independent review, not only green CI.

An earlier invalid WebGPU specification SHA has been removed from the canonical report and replaced with the verified editor-draft commit above.

## Claim-scoped evidence

| Claim | Evidence class | Current receipt | Important exclusion |
| --- | --- | --- | --- |
| Browser-only unsupported color-space mapping returns before raw `GPUCanvasContext.configure` | source-read | pinned browser backend | browser test not executed |
| Browser configure mutates canvas extent before later rejection | source-read plus target-test-prepared | fork 2×2 → rejected 7×5 assertions | no browser receipt |
| Public configuration cache publishes the rejected request | source-read plus target-test-prepared | wrapper source and fork test | no executed target result |
| Raw browser configuration can remain accepted while canvas extent and public cache change | source-read plus target-test-prepared | raw-context and dimension controls | no runtime confirmation |
| Unconfigured browser acquisition maps raw invalid state to `Lost` | source-read plus target-test-prepared | new fork characterization | no browser receipt |
| Native unconfigured/error acquisition uses validation or fatal handling instead of browser `Lost` | source-read | native core dispatch path | no cross-backend execution |
| Native validation can preserve an earlier accepted presentation | source-read | core configure ordering | no core-backed runtime control |
| Public texture metadata can follow rejected cache values | source-read risk | wrapper descriptor construction plus core ordering | wrapper and core controls unexecuted |
| Ordinary wasm runtime initialization does not exercise browser WebGPU | source-read | runner features and initializer | actual Playwright adapter unavailable/unmeasured |

No claim is `target-executed`, `integration-executed`, or `full-gate`.

## Delivery Desk position

This lane does not belong on Delivery Desk #160 yet.

The desk is for selected implementations, bounded final gates, clean application, receipt transfer, merge, or closeout. This lane still has:

- multiple plausible repair boundaries;
- no executed browser characterization;
- no native/core runtime control;
- no accepted implementation disposition;
- no canonical source-only repair branch;
- no named full repository gate for a selected candidate.

Issue #116, Fieldwork PR #126, and owned-fork PR #1 remain the canonical exploration records.

## Protocol lessons

1. **Evidence must be claim-scoped.** Browser source behavior, authored tests, native source risk, and unexecuted integration implications are different evidence classes.
2. **A disposition needs identity.** Acceptance must name reviewed head, reviewed issue/input generation, and durable receipt.
3. **The clearing condition is a bundle.** Browser execution, native control, candidate publication, exact-head review, and carrier cleanup may be inseparable but must remain explicit.
4. **Green CI is not acceptance.** Fieldwork protocol checks do not execute wgpu’s browser tests.
5. **Execution carriers are not canonical repairs.** The fork PR is a characterization carrier.
6. **Theory revision is mandatory.** Contradictory browser execution must rewrite the model.
7. **Exact pins must resolve.** A syntactically plausible commit value is not a receipt until the source host resolves it.

## Next probe queue

### P1 — Execute browser characterizations

Required receipts:

- exact fork head and generated test identities;
- format and clippy commands;
- Chromium and browser-WebGPU adapter information;
- unconfigured raw/public acquisition state;
- accepted baseline state;
- rejected request, canvas extent, raw configuration, raw texture dimensions, and typed status;
- same-surface recovery;
- recreated-surface invalid retry control.

Stop or revise if browser WebGPU is unavailable, the selected color space is supported, raw texture properties are unavailable, or direct raw acquisition violates browser ownership assumptions.

### P1 — Add public-wrapper characterization safely

Preferred location: a private unit-test module beside `wgpu/src/api/surface.rs`.

Use a noop device and minimal custom surface, texture, and output-detail implementations. Assert independently:

- backend accepted state;
- public configuration cache;
- public texture width, height, format, and usage.

Use a safe checkout or complete tree/commit edit. Do not replace the large source file from truncated connector content.

### P1 — Build core-backed validation control

Prove:

- accepted baseline presentation;
- intentionally invalid second request;
- captured validation error;
- retained or cleared presentation;
- subsequent acquisition outcome;
- public metadata versus accepted state;
- later valid recovery.

### P2 — Measure raw rejected reconfiguration semantics

The inspected CTS covers initial rejection but not:

```text
valid accepted configuration
→ synchronously rejected reconfiguration
→ inspect retained configuration
→ inspect canvas extent
→ inspect texture acquisition
```

Measure separately from wgpu’s local pre-rejection.

### P2 — Split acquisition exceptions

Distinguish unconfigured invalid state, device loss, out-of-memory/internal failure, and transient browser exceptions before changing public status variants.

### P2 — Audit recovery examples

Build an outcome table for `Success`, `Suboptimal`, `Timeout`, `Occluded`, `Outdated`, `Lost`, and `Validation`. Verify that examples do not retry an invalid configuration merely because the typed result is `Lost`.

### P3 — Frame cleanup and presentation

Compare:

- present success and error;
- ordinary unpresented discard;
- panic-unwind release;
- browser no-op cleanup;
- reconfiguration with a live frame;
- device/surface loss after acquisition.

### P3 — Custom-backend compatibility

Inventory custom implementations before changing `SurfaceInterface::configure`. Do not create a compatibility tax without measured public-state benefit.

## Promotion gate

Promote only with:

- one executed contradiction or precise documentation/example mismatch;
- exact source and execution receipts;
- at least one negative control;
- selected owning subsystem and desired contract;
- source-only candidate branch;
- independent exact-head review tied to input generation;
- explicit authority before upstream contact.

## Stops

- Do not enter Delivery Desk because the source map is large.
- Do not upgrade authored tests to executed evidence.
- Do not call the raw browser surface lost when rejection occurred before the raw configure call.
- Do not describe prior state as fully preserved when canvas extent already mutated.
- Do not treat a wrapper custom test as proof of native core behavior.
- Do not begin with a breaking public API redesign.
