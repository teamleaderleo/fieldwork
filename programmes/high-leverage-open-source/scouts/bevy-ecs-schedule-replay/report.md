# Bevy deferred-command visibility after system failure

State: `target-test-prepared`

Fieldwork issue: #124  
Programme: #114  
Stable release: Bevy `0.19.0` at `c6f634ca9f406d68ba5109d921247b654cb42c10`  
Development source: `25368b78ce5e9b15dc770cdf2af4595602cc8a7b`  
Relevant merged development change: `bevyengine/bevy#24240`, merge `18d106d26a0dd1cf86f84695fcb6599a773f0f3e`  
Worker: GPT-5.6 Thinking / workstream F  
Upstream contact authorized: `false`

## In simple words

A Bevy system can queue commands and then fail. Those commands run later, after the system has finished.

The schedule executor currently decides whether the queued commands become visible. The answer can change when the application switches between Bevy's single-threaded and multithreaded executors, even when the system and fallback error policy are otherwise identical.

That makes a failed system's world changes harder to explain and replay. The first task is to characterize the exact behavior, not to assume that failure should be transactional.

## Question

Under the same system outcome and fallback error handler, does executor selection change whether commands queued before failure become visible?

## Source map

### Development source

`crates/bevy_ecs/src/schedule/executor/single_threaded.rs`

- runs a system without applying deferred buffers;
- handles a returned error or caught panic through the fallback handler;
- registers the system in `unapplied_systems` only after the handler returns;
- applies registered buffers at an `ApplyDeferred` boundary or at schedule completion.

A handler that returns permits the failed system's deferred buffers to be registered. A handler that panics unwinds before registration.

`crates/bevy_ecs/src/schedule/executor/multi_threaded.rs`

- converts the system outcome into a completion event;
- records every completed system in `unapplied_systems` without carrying success or failure in `SystemResult`;
- stores a panic payload separately;
- applies final deferred buffers;
- rethrows the stored panic only after application.

A handler panic therefore does not prevent the failed system's deferred buffers from being registered and applied.

`crates/bevy_ecs/src/error/handler.rs`

- the fallback handler defaults to `match_severity`;
- `Severity::Panic` invokes the panic handler;
- the panic handler marks the panic as originating from the error handler.

`crates/bevy_ecs/src/schedule/schedule.rs`

- `Schedule::run` selects the world's fallback error handler once;
- the same handler function is passed to either executor;
- final deferred application is enabled by default.

### Stable release difference

Bevy `0.19.0` predates merged PR `bevyengine/bevy#24240`.

- Returned errors already pass through the fallback handler and can commit queued commands when the handler returns.
- A system panic in the stable single-threaded executor immediately resumes unwinding before registering deferred buffers.
- The stable multithreaded executor applies registered deferred buffers before rethrowing its stored panic payload.

The development change intentionally makes system panics configurable through the fallback handler. Its added tests verify handler invocation, not command visibility.

The PR description lists command-buffer continuation after command panic as future work. The present question differs: commands queued successfully by a system before that system itself fails or panics.

## Source-predicted development matrix

| System outcome | Fallback policy | Single-threaded | Multithreaded |
| --- | --- | --- | --- |
| success | default | command visible; returns | command visible; returns |
| returned `Ignore` error | default | command visible; returns | command visible; returns |
| panic | custom handler returns | command visible; returns | command visible; returns |
| returned `Panic` error | default handler panics | command absent; unwinds | command visible; unwinds |
| panic | default handler panics | command absent; unwinds | command visible; unwinds |

This matrix is a source prediction until the native probe executes.

## Prepared native probe

Probe path:

`programmes/high-leverage-open-source/scouts/bevy-ecs-schedule-replay/probes/deferred-failure-visibility`

The crate expects an exact Bevy checkout at:

`.fieldwork/bevy`

Execution recipe:

```bash
git clone --no-checkout <read-only Bevy source> .fieldwork/bevy
git -C .fieldwork/bevy checkout 25368b78ce5e9b15dc770cdf2af4595602cc8a7b
cargo test --manifest-path programmes/high-leverage-open-source/scouts/bevy-ecs-schedule-replay/probes/deferred-failure-visibility/Cargo.toml
cargo run --manifest-path programmes/high-leverage-open-source/scouts/bevy-ecs-schedule-replay/probes/deferred-failure-visibility/Cargo.toml
```

The test asserts the five source-predicted cells under both executors and prints every receipt.

Local execution in the current worker environment was blocked because no Rust toolchain was installed, the package mirror lacked valid Release metadata, and direct toolchain download could not resolve its host. This is environment evidence only.

## Existing overlap check

Targeted current issue and pull-request searches found related work on command ordering, command application failures, system-result plumbing, and panic-to-error conversion. No exact open or closed record was found that classifies deferred command visibility from a failed producer across both executors.

The closest overlap is merged PR `bevyengine/bevy#24240`. It changes panic handling and therefore creates the development half of this matrix, but it does not test or state the deferred visibility contract.

## Candidate invariants

These are alternatives for review, not selected repair claims.

### A. Commands survive producer failure

A queued command is independent work once accepted by `Commands`. Apply it regardless of the producer system's later outcome.

This matches current non-panicking-handler behavior and the multithreaded panic path. It requires the single-threaded executor to retain buffers before invoking a potentially panicking handler.

### B. Commands are discarded when the producer fails

A system's deferred buffers commit only when the system completes successfully.

This gives a transaction-like boundary but may break applications that intentionally queue cleanup or reporting before returning an error. It requires retaining outcome in executor completion state and clearing failed buffers safely.

### C. Error handling chooses apply or discard

The failure disposition explicitly includes deferred-buffer authority.

This is the most expressive option and the widest API change. It may require an RFC-level design rather than an ordinary patch.

## Evaluation criteria

- identical visibility under both built-in executors for the same policy;
- explicit behavior for returned error, system panic, handler panic, and deferred-command panic;
- compatibility with custom `Deferred` parameters, not only `Commands`;
- no loss of successful unrelated systems' buffers;
- truthful diagnostics and replay receipts;
- predictable behavior at explicit `ApplyDeferred` boundaries;
- `std` and `no_std` differences stated rather than implied.

## Evidence boundary

- stable and development mechanisms: `source-read`;
- merged panic-handling intent: `source-read`;
- development result matrix: `target-test-prepared`;
- native execution: blocked by local toolchain availability;
- production defect classification: held;
- repair selection: held;
- performance impact: unmeasured;
- public upstream interaction: absent.

## Current disposition

**RETAIN the executor-parity question and execute the prepared matrix. Do not select apply-versus-discard policy from source inspection alone.**

A passing matrix would establish current behavior and support a documentation or diagnostics decision. A mismatch would first be classified as probe error or source drift. Any repair requires explicit policy selection and an independent complete-diff review.
