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
- owned fork test head: `455a8711984b0166533fa3441d65a9e58777d9ca`
- review-contract head: Fieldwork PR #143 at `dd7f0364d5dc195b3fa651f95192cf6078810a6e`
- Delivery Desk protocol head: Fieldwork PR #161 at `b1e402ee47aa2e2842d52e8f0ab42d4ab0501916`

Both protocol heads passed Fieldwork integrity and external-reference policy. They remain draft because process acceptance requires independent review, not only green CI.

An earlier invalid WebGPU specification SHA has been removed from the canonical report.

## Claim-scoped evidence

| Claim | Evidence class | Current receipt | Important exclusion |
| --- | --- | --- | --- |
| Unsupported browser color-space mapping returns before raw configure | source-read | pinned browser backend | browser test not executed |
| Browser configure mutates canvas extent before later rejection | source-read plus target-test-prepared | fork 2×2 → rejected 7×5 assertions | no browser receipt |
| Public cache publishes rejected request | source-read plus target-test-prepared | wrapper source and fork test | no executed target result |
| Raw configuration can remain old while extent/cache change | source-read plus target-test-prepared | raw-context and dimension controls | no runtime confirmation |
| Unconfigured browser acquisition maps invalid state to `Lost` | source-read plus target-test-prepared | fork characterization | no browser receipt |
| Native unconfigured/error acquisition uses validation/fatal handling | source-read | native core dispatch | no cross-backend execution |
| Zero-sized browser configuration is applied with validation, not synchronously rejected | CTS/source-read plus target-test-prepared | error-scope and error-texture fork characterization | no browser execution |
| Public `Success` can carry a zero-sized error texture while validation is delivered separately | source-read prediction plus target-test-prepared | zero-size fork case | exact status unexecuted |
| Native validation can preserve earlier presentation | source-read | core configure ordering | no core-backed control |
| Public texture metadata can follow rejected cache | source-read risk | wrapper descriptor plus core ordering | wrapper/core controls unexecuted |
| Ordinary wasm initializer does not exercise browser WebGPU | source-read | runner features and initializer | Playwright adapter unmeasured |

No claim is `target-executed`, `integration-executed`, or `full-gate`.

## Configure-state taxonomy exposed by the lane

The tests now require at least these states:

- `RejectedUnconfigured`;
- `RejectedPreservingPrevious`;
- `RejectedAfterPartialMutation`;
- `AppliedWithDiagnostic`;
- `Applied`.

This taxonomy is provisional, but it demonstrates why a binary success flag would erase recovery-relevant state.

## Delivery Desk position

This lane does not belong on Delivery Desk #160 yet.

It has no executed browser result, no core-backed control, no selected repair, no canonical source-only candidate, no accepted disposition, and no bounded full gate. Issue #116, PR #126, and owned-fork PR #1 remain canonical.

## Protocol lessons

1. **Evidence must be claim-scoped.** A prepared zero-size error-scope test does not upgrade native metadata claims.
2. **A disposition needs identity.** Acceptance must name reviewed head, issue/input generation, and receipt.
3. **The clearing condition is a bundle.** Browser execution, native control, candidate publication, exact-head review, and carrier cleanup must be explicit.
4. **Green CI is not acceptance.** Fieldwork checks do not execute target tests.
5. **Execution carriers are not repairs.** The fork PR is a characterization carrier.
6. **Theory revision is mandatory.** Contradictory execution rewrites the model.
7. **Exact pins must resolve.** Plausible text is not a source receipt.
8. **Validation is not rejection.** WebGPU may establish configuration and return error objects while reporting validation separately.

## Next probe queue

### P1 — execute browser characterizations

Required receipts:

- exact fork head and generated test identities;
- format and clippy commands;
- browser/adapter information;
- unconfigured raw/public state;
- zero-size configure and acquisition error scopes;
- exact zero-size public acquisition variant and texture metadata;
- accepted baseline and rejected partial-mutation state;
- same-surface and recreated-surface controls.

Stop or revise if browser WebGPU is unavailable, selected capabilities differ, error scope timing differs, error textures map to another public outcome, or direct raw acquisition violates ownership assumptions.

### P1 — public-wrapper metadata characterization

Use a private `surface.rs` unit test with a noop device and minimal custom surface/texture/output detail. Assert backend accepted state, public cache, and public texture metadata separately. Use a safe complete-file or tree edit.

### P1 — core-backed validation control

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

Separate this from local wgpu pre-rejection and from validation-error configuration.

### P2 — acquisition exception matrix

Distinguish invalid state, device loss, out-of-memory/internal failure, and transient browser exceptions before changing status variants.

### P2 — example recovery audit

Use `artifacts/example-recovery-outcome-audit.md`. Verify handling for every `CurrentSurfaceTexture` outcome and for error textures delivered through `Success`.

### P3 — frame cleanup, presentation, and custom backends

Measure present success/error, unpresented discard, unwind release, browser no-op cleanup, reconfiguration with live frames, and custom-backend compatibility.

## Promotion gate

Promote only with executed contradiction or precise documentation mismatch, exact receipts, negative control, selected owner/contract, source-only candidate, independent exact-head review tied to input generation, and explicit upstream authority.

## Stops

- Do not enter Delivery Desk because the map is large.
- Do not upgrade authored tests to executed evidence.
- Do not call validation a synchronous rejection.
- Do not call a returned error texture usable because the public variant is `Success`.
- Do not describe prior state as fully preserved when canvas extent mutated.
- Do not treat a custom wrapper test as native proof.
- Do not begin with a breaking public API redesign.
