## In simple words

This round inspected current Tokio for a small, deterministic foundational-library defect and found three useful boundaries, but none should become an independent Fieldwork implementation from this pass.

The first suspicion was `LengthDelimitedCodec`: a short length field might have accepted a payload whose encoded length could not fit, producing a truncated wire prefix. Current Tokio already prevents that. The codec reduces its effective maximum frame length to what the configured length field can represent, including positive and negative length adjustments, and current tests cover the boundary and the first rejected byte.

The second boundary is a real `tokio::fs::File` state bug after mandatory blocking-task spawn failure. A first failed write can leave the idle buffer absent, and a second write can panic. That problem already has a public report and an active upstream pull request covering both scalar and vectored writes, so Fieldwork should avoid competing with the existing owner.

The third boundary, all-empty vectored writes on the new `tokio-util` simplex channel, was repaired on current master one day before this scout. Current source checks the all-empty case before backpressure and returns `Ok(0)`, matching scalar writes.

Disposition: **STOP this Tokio round as fresh implementation work; retain the negative/overlap map and move OE-05 effort to another target.**

## Target and evidence

- target: `tokio-rs/tokio`
- exact source revision read: `625954f365727668cb02d04172b34f1149637728`
- branch: `master`
- retrieval date: `2026-08-11` UTC+8
- upstream permissions observed through the connector: read-only for this agent
- upstream contact authorization: `false`
- evidence classes used: `source-read`, `model-executed`
- target-native execution: pending; this pass did not check out or execute the pinned Tokio tree

The model probe is `probe.py`. It mirrors only the length-field capacity arithmetic and is not a substitute for Tokio's own test suite.

## Candidate 1 — LengthDelimitedCodec field-width truncation

### Question

Can encoding accept a frame whose adjusted length exceeds the configured length-field width, causing the emitted prefix to truncate while the payload is still appended?

### Source map

Current source:

- `tokio-util/src/codec/length_delimited.rs`
- `LengthDelimitedCodec::encode`
- `Builder::adjust_max_frame_len`
- `Builder::max_allowed_frame_len`
- `Builder::max_length_field_value`

Pinned source:

- https://github.com/tokio-rs/tokio/blob/625954f365727668cb02d04172b34f1149637728/tokio-util/src/codec/length_delimited.rs

The encoder checks `data.len()` against the codec's effective `max_frame_len` before serializing the adjusted length. The builder computes the maximum representable length-field value, applies the configured signed adjustment with saturation, converts that result to `usize`, and clamps `max_frame_len` to that value.

For a one-byte field, current behavior allows these maximum payload lengths:

| adjustment | maximum payload |
| --- | ---: |
| `-1` | 254 |
| `0` | 255 |
| `+1` | 256 |

The `+1` case is valid because encoding subtracts the positive adjustment before writing the field, so a 256-byte payload serializes the representable value 255.

### Test map

Current `tokio-util/tests/length_delimited.rs` contains direct controls:

- `frame_does_not_fit`
- `runtime_max_frame_len_respects_length_field`
- `neg_adjusted_frame_does_not_fit`
- `pos_adjusted_frame_does_not_fit`
- `max_allowed_frame_fits`
- `smaller_frame_len_not_adjusted`
- `max_allowed_length_field`

Pinned test file:

- https://github.com/tokio-rs/tokio/blob/625954f365727668cb02d04172b34f1149637728/tokio-util/tests/length_delimited.rs

`runtime_max_frame_len_respects_length_field` is especially decisive: after asking for a runtime maximum of 1000 with a one-byte field, it verifies the adjusted effective maxima `254/255/256`, successfully encodes the exact maximum, rejects one byte more with `InvalidInput`, and checks that the destination buffer remains unchanged on rejection.

### Model probe

Run:

```text
python programmes/open-source-ecosystems/scouts/foundational-systems/tokio-20260811/probe.py
```

The model reproduces the source arithmetic for one- and two-byte fields. Local model execution produced the expected one-byte values `254`, `255`, and `256` for adjustments `-1`, `0`, and `+1`.

### Result

**STOP — current source and tests already defend the suspected boundary.**

A future revisit only makes sense after relevant source movement or a distinct discrepancy between encoder and decoder semantics.

## Candidate 2 — File write state after blocking-spawn failure

### Question

Can a recoverable write error leave `tokio::fs::File` in an invalid internal state that panics on the next write?

### Public ownership

Public issue:

- https://github.com/tokio-rs/tokio/issues/8182

Active implementation:

- https://github.com/tokio-rs/tokio/pull/8183

Issue #8182 gives a deterministic reproduction: create a Tokio file while the runtime is alive, shut down the runtime's blocking pool, enter the retained runtime handle, poll a write so mandatory blocking spawn fails, then poll a second write on the same file. The report identifies `State::Idle(Some(buf))` losing its buffer before the failed spawn path returns.

PR #8183 remains open as of this scout. Its stated fix restores a valid idle buffer on spawn failure and adds repeated-write regression coverage for both `poll_write` and `poll_write_vectored`.

### Source family

Current source use of `spawn_mandatory_blocking` is concentrated in the filesystem file implementation plus blocking runtime support. A focused code search did not expose an independent sibling consumer with the same move-before-spawn state transition.

### Result

**STOP — confirmed public problem with an active equivalent implementation owner.**

Fieldwork should monitor or review only if separately requested. Recheck ownership before any future implementation work.

## Candidate 3 — simplex all-empty vectored write under backpressure

### Question

Does the new `tokio-util` simplex sender return `Pending` for an all-empty vectored write when its in-memory buffer is full, while scalar empty writes return `Ok(0)`?

### Current source

Pinned file:

- https://github.com/tokio-rs/tokio/blob/625954f365727668cb02d04172b34f1149637728/tokio-util/src/io/simplex.rs

Current `poll_write_vectored` checks whether all `IoSlice`s are empty immediately after the closed-channel check and before testing available capacity. It therefore returns `Ready(Ok(0))` even at the backpressure boundary, while preserving `BrokenPipe` after close.

### Recent ownership

Merged upstream PR:

- https://github.com/tokio-rs/tokio/pull/8353

The PR explicitly repaired this scalar/vectored mismatch and added a full-buffer regression. It merged as commit `af9376300907dd187e0fdca793ccda2fa62de5ec` on `2026-08-10`.

### Result

**STOP — absorbed into current master before this scout.**

## Candidate 4 — new Semaphore blocking acquire API

### Question

Do the new synchronous `Semaphore::blocking_acquire*` methods introduce a new runtime-context blocking path with weaker guarding than Tokio's existing synchronous wrappers?

### Source map

Pinned source:

- https://github.com/tokio-rs/tokio/blob/625954f365727668cb02d04172b34f1149637728/tokio/src/sync/semaphore.rs
- https://github.com/tokio-rs/tokio/blob/625954f365727668cb02d04172b34f1149637728/tokio/src/future/block_on.rs

The new methods delegate to `crate::future::block_on(...)`. With runtime support enabled, that helper calls `try_enter_blocking_region()` and panics with the established "Cannot block the current thread from within a runtime" guard if invoked from an asynchronous runtime-driving context. The public method documentation states this panic contract and describes synchronous / `spawn_blocking` use.

### Result

**PARK — no contract contradiction isolated in source.**

A useful future discriminator would need a context where another Tokio blocking wrapper behaves differently under the same runtime state, or a documented supported synchronous context that this helper rejects.

## Negative results retained

1. The apparent short length-field truncation path is blocked by effective-max clamping and explicit boundary tests.
2. The File repeated-write panic is real but already owned by public issue #8182 and open PR #8183.
3. The simplex empty-vectored-write mismatch was repaired by merged PR #8353 before the pinned revision.
4. The new semaphore blocking APIs use the established blocking-context guard; source review found no separate state/lifecycle defect.
5. Focused Fieldwork search found no existing Tokio foundational scout duplicating this exact round.

## Ranked recommendation

1. **STOP Tokio implementation work from this round.** The strongest live defect already has an active equivalent upstream implementation.
2. **Retain this report as an overlap/negative-result index.** It prevents another worker from re-opening the codec-width and simplex branches from stale intuition.
3. **Move OE-05 discovery to another foundational target**, preferably one without active upstream ownership on the first deterministic boundary.
4. Revisit Tokio only after source drift, a new deterministic unsupported-by-current-tests boundary, or a review request against an existing owned/public candidate.

## Authority

This scout performed read-only inspection of `tokio-rs/tokio`. No upstream issue, pull request, review, comment, reaction, branch, email, or other public interaction was created or changed.
