# Protocol-aligned wgpu status and next probes

State: active exploration; `source-read` and `target-test-prepared` evidence only

Fieldwork issue: #116

Fieldwork draft PR: #126

Owned fork draft: `teamleaderleo/wgpu#1`

Upstream contact authorized: false

## Current exact records

- released baseline: `wgpu v30.0.0`
- [pinned wgpu source revision](https://redirect.github.com/gfx-rs/wgpu/commit/2eddc8c7b2fedd4267f5004745a8bc42974e17a0)
- [current upstream source checked](https://redirect.github.com/gfx-rs/wgpu/commit/c079e55f534d713a60aef145f6df0255b7ddcdc4)
- [WebGPU editor-draft source](https://redirect.github.com/gpuweb/gpuweb/commit/d390da5f80f18e82d9535a40c6f2f1f65e6884ae)
- [WebGPU CTS source](https://redirect.github.com/gpuweb/cts/commit/dc20b8682aa71ff31f135de6ae7f8acaa2e16383)
- owned fork characterization head: `3d076485509f6b3f8381de8074bfbdef17bc4133`
- current Fieldwork head: `ab27754b3ff6aecf78707aeef506be21921750c4`
- review-contract head previously checked: Fieldwork PR #143 at `dd7f0364d5dc195b3fa651f95192cf6078810a6e`
- Delivery Desk protocol head previously checked: Fieldwork PR #161 at `b1e402ee47aa2e2842d52e8f0ab42d4ab0501916`

The protocol heads passed Fieldwork integrity and external-reference policy at those exact revisions. They remain draft process work and are not authority to promote this lane.

Current upstream is seven commits ahead of the pin. The relevant surface API, browser backend, core presentation, HAL presentation, and shared example framework paths remain unchanged; the wasm test file has unrelated macro churn.

## Claim-scoped evidence

| Claim | Evidence class | Current receipt | Important exclusion |
| --- | --- | --- | --- |
| Unsupported browser color-space mapping returns before raw configure | source-read | pinned browser backend | browser test not executed |
| Browser configure mutates canvas extent before later rejection | source-read plus target-test-prepared | fork 2×2 → rejected 7×5 assertions | no browser receipt |
| Public cache publishes rejected request | source-read plus target-test-prepared | wrapper source and fork test | no executed target result |
| Raw configuration can remain old while extent/cache change | source-read plus target-test-prepared | raw-context and dimension controls | no runtime confirmation |
| Unconfigured browser acquisition maps invalid state to `Lost` | source-read plus target-test-prepared | fork characterization | no browser receipt |
| Zero-sized browser configuration is applied with validation | CTS/source-read plus target-test-prepared | error-scope and error-texture test | no browser execution |
| Public `Success` can carry a zero-sized error texture | source-read prediction plus target-test-prepared | zero-size fork case | exact outcome unexecuted |
| Native validation can preserve earlier presentation | source-read | core configure ordering | no core-backed control |
| Public texture metadata can follow rejected cache | source-read risk | wrapper descriptor plus core ordering | wrapper/core controls unexecuted |
| Public `Queue::present` commits ownership before backend dispatch | source-read plus target-test-prepared | custom queue/drop counter tests | unit tests not compiled |
| Core detaches acquired texture before presentation preparation | source-read | core presentation ordering | no injected failure |
| Preparation can fail before HAL consumes the image | source-read | submission/clear/raw/mini-submit paths | no failure receipt |
| DX12 acquire bookkeeping is repaired only by present/discard | source-read | `acquired_count` increments/decrements | invariant not executed |
| Vulkan native discard is a no-op for an acquired image | source-read | native swapchain implementation | repeated acquisition unmeasured |
| HAL present statuses are dropped by the public core backend | source-read | core status mapping plus public dispatch | user consequence unmeasured |
| Ordinary wasm initializer does not exercise browser WebGPU | source-read | runner features and initializer | Playwright adapter unmeasured |

No claim is `target-executed`, `integration-executed`, or `full-gate`.

## Configure-state taxonomy

The lane currently requires at least:

- `Applied`;
- `AppliedWithDiagnostic`;
- `RejectedUnconfigured`;
- `RejectedPreservingPrevious`;
- `RejectedAfterPartialMutation`.

The names are provisional. The distinctions are recovery-relevant and show why a binary configure result is too weak.

## Presentation-state taxonomy

The lane currently separates:

- `Acquired`;
- `PresentationAttemptCommitted`;
- `DetachedForPreparation`;
- `PreparedForPresentation`;
- `HalConsumed`;
- `Presented`;
- `ConsumedWithStatus`;
- `PreparationFailedDetached`;
- `ConsumedWithError`.

The critical new state is `PreparationFailedDetached`: core removed the frame from surface state, but HAL never received it.

## Delivery Desk position

This lane does not belong on Delivery Desk #160.

It has no executed browser result, no compiled wrapper test, no fault-injected core result, no selected repair, no canonical source-only candidate, no accepted current-head disposition, and no bounded full gate. Issue #116, PR #126, and owned-fork PR #1 remain canonical.

## Review status

An older exact-head comment accepted the source map and test design while requiring execution. It reviewed a previous head and therefore remains historical input, not current acceptance.

## Protocol lessons

1. **Evidence must be claim-scoped.** Prepared browser tests do not upgrade DX12/Vulkan cleanup claims.
2. **A disposition needs identity.** Acceptance must name reviewed head, issue/input generation, and receipt.
3. **The clearing condition is a bundle.** Browser execution, core fault injection, candidate publication, exact-head review, and carrier cleanup remain explicit.
4. **Green Fieldwork CI is not target execution.** Repository policy checks do not compile or run wgpu.
5. **Execution carriers are not repairs.** The fork PR is a characterization carrier.
6. **Theory revision is mandatory.** Contradictory execution rewrites the model.
7. **Exact pins must resolve.** Plausible source text is not a receipt.
8. **Validation is not rejection.** WebGPU may establish state while delivering error objects and validation separately.
9. **Ownership is backend-specific.** Generic texture drop is not automatically equivalent to surface discard.
10. **Present completion is not an ordinary submission fence.** Historical review already exposed false-wait and retention risks from that simplification.

## Next probe queue

### P1 — compile public-wrapper presentation tests

Required receipts:

- exact fork head;
- `cargo fmt --check`;
- exact unit-test command;
- ordinary-drop control;
- injected-present-panic result;
- clippy for the relevant feature set.

Stop or revise if the custom test feature combination does not compile or the dispatch signatures differ from the pinned source assumptions.

### P1 — execute browser characterizations

Required receipts:

- exact fork head and generated test identities;
- browser/adapter information;
- unconfigured raw/public state;
- zero-size configure and acquisition error scopes;
- exact zero-size acquisition variant and texture metadata;
- accepted baseline and rejected partial-mutation state;
- same-surface and recreated-surface controls.

### P1 — DX12 acquired-count fault injection

Prove or disprove:

```text
successful acquisitions
- successful presents
- explicit discards
= acquired_count
```

Inject failure after core detaches the frame and before HAL present. Record:

- acquired count before and after;
- whether surface discard ran;
- whether HAL present ran;
- later selected back-buffer indices;
- successful recovery or persistent offset.

### P1 — Vulkan repeated acquisition

With known swapchain image count:

- inject the same pre-HAL failure;
- repeat bounded acquisitions;
- record image indices, timeouts, and validation diagnostics;
- compare explicit discard, successful present, and surface recreation.

### P1 — native retained-configuration metadata

Prove accepted baseline, invalid second request, captured error, retained or cleared presentation, acquisition, public metadata, and valid recovery.

### P2 — raw rejected reconfiguration

Measure:

```text
valid accepted configuration
→ synchronous rejection
→ retained configuration
→ canvas extent
→ acquired texture
```

Separate this from local wgpu pre-rejection and validation-error configuration.

### P2 — acquisition and presentation outcome matrices

Distinguish invalid state, device loss, out-of-memory/internal failure, transient browser exceptions, native present statuses, and error-sink delivery.

### P2 — example recovery audit

Use `example-recovery-outcome-audit.md`. Verify handling for every `CurrentSurfaceTexture` outcome and error textures delivered through `Success`.

### P3 — Metal and native GLES cleanup

- repeat preparation failure under drawable-pool pressure on Metal;
- inspect native EGL/WGL per-acquisition bookkeeping;
- do not infer WebGL behavior applies to native GLES.

## Promotion gate

Promote only with:

- one executed contradiction or precise documentation mismatch;
- exact source and execution receipts;
- a negative control;
- selected backend/subsystem owner;
- one narrow desired contract;
- source-only candidate branch;
- independent exact-head review tied to input generation;
- no stale carrier or base relationship;
- explicit upstream authority.

## Stops

- Do not enter Delivery Desk because the map is large.
- Do not upgrade authored tests to executed evidence.
- Do not call validation synchronous rejection.
- Do not call an error texture usable because the public variant is `Success`.
- Do not treat custom wrapper tests as native proof.
- Do not infer a leak from source lifetime alone.
- Do not equate COM/Objective-C handle drop with backend bookkeeping repair.
- Do not infer Vulkan image return from semaphore-reference drop.
- Do not use noop as platform ownership proof.
- Do not begin with breaking public configure or present APIs.
- Do not contact upstream without authorization.
