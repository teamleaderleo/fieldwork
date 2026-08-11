# Tokio foundational-systems scout — 2026-08-11

## In simple words

`tokio::fs::ReadDir` appears able to hang forever after its runtime has begun shutting down, once its initial directory-entry chunk is exhausted and it needs to refill.

The refill path moves the live `std::fs::ReadDir` into ordinary `spawn_blocking`. Tokio's blocking pool deliberately returns a join handle that will never resolve when a non-mandatory blocking task is submitted during shutdown. `ReadDir::poll_next_entry` then stores that handle in `State::Pending` and waits on it. The public method returns `io::Result`, and its poll documentation says a `Pending` result schedules the latest waker for a future wakeup, but this shutdown path has no future worker that can run the refill and resolve the handle.

This is distinct from the already-open `tokio::fs::File` shutdown failure (#8182), whose write path uses mandatory blocking and can receive an explicit spawn failure. No open or closed Tokio issue or open PR matching `ReadDir` + blocking-pool shutdown/refill was found in the overlap screen performed for this scout.

Evidence state is intentionally narrow: `source-read` plus `target-test-prepared`. Exact-checkout target execution remains required before promotion to an implementation candidate.

## Scout identity

- Programme: `open-source-ecosystems`
- Parent lane: Fieldwork #211 / foundational systems
- Target: `tokio-rs/tokio`
- Exact target revision: `625954f365727668cb02d04172b34f1149637728`
- Target subject: `sync: add blocking_acquire methods to Semaphore (#8269)`
- Owned path: `programmes/open-source-ecosystems/scouts/foundational-systems/tokio-20260811/`
- Claim scope: `mechanism`
- Upstream-contact authorization: `false`
- Third-party upstream remained read-only

## Code and ownership map

### Public path

`tokio/src/fs/read_dir.rs`

```text
fs::read_dir(path)
  -> blocking initial std::fs::read_dir
  -> ReadDir(State::Idle(Some((buf, std_read_dir, remain))))

ReadDir::next_entry()
  -> poll_next_entry()
  -> consume buffered entries
  -> when buffer empty and remain == true:
       data.take()
       State::Pending(spawn_blocking(move || next_chunk(...)))
  -> poll JoinHandle until refill completes
```

The initial construction preloads up to `CHUNK_SIZE` entries. The candidate is therefore only exercised when the directory contains enough entries to require a second chunk.

### Blocking-pool behavior

`tokio/src/runtime/blocking/pool.rs` distinguishes mandatory and non-mandatory work. For ordinary `spawn_blocking`, `Spawner::spawn_blocking` handles a shutdown result this way:

```text
Err(SpawnError::ShuttingDown) => join_handle
```

with an inline compatibility comment stating that the returned join handle will never resolve.

That behavior is reasonable for the public non-mandatory `spawn_blocking` compatibility contract, but it becomes problematic when an `io::Result`-returning Tokio filesystem state machine internally treats that handle as guaranteed future progress.

### Existing fs test surface

`tokio/tests/fs_dir.rs` covers ordinary directory creation/removal, iteration, and entry metadata. The inspected file has no test that:

1. creates a `ReadDir` while the blocking pool is alive;
2. consumes the preloaded chunk;
3. shuts down the runtime;
4. polls the same `ReadDir` for the next entry.

## Candidate invariant

Once `ReadDir::poll_next_entry` returns `Poll::Pending`, either a wakeup must remain possible for the stored operation or the method should synchronously return an error instead of entering an unresolvable pending state.

A stronger user-facing formulation is:

> A directory stream that still owns unread synchronous iterator state should not become permanently unwakeable merely because its runtime's blocking pool has shut down.

This scout does not yet claim which repair is preferable.

## Prepared discriminator

`prepared-regression.rs` contains a target-native test shape for `tokio/tests/fs_dir.rs`.

The test deliberately creates more entries than the internal initial chunk can hold, obtains `ReadDir` while the runtime is alive, drains the initial entries, shuts the runtime down, re-enters the handle, and polls one more `next_entry` behind a manually driven future. The expected current behavior is that the refill transitions to a non-resolving blocking join handle.

The clean controls are:

- a directory small enough to fit in the initial chunk should finish without needing a refill;
- the same large directory should finish normally while the runtime remains alive.

The exact target run should use the repository's own test harness and confirm the prepared threshold against current `CHUNK_SIZE` rather than assuming a historical value.

## Overlap screen

Current open Tokio issues reviewed during this scout included active work around `tokio_test::io::Mock` hangs (#8329), io_uring submission lifetime (#8255), `tokio::fs::File` post-error state (#8182), timers/livelock (#7883), and other scheduler/channel boundaries. These were treated as occupied and not reused as scout findings.

Focused searches for open issues, closed issues, and open PRs matching `read_dir`, `next_entry`, `blocking pool`, `shutdown`, and refill/hang terminology returned no matching ownership for this candidate at scout time.

A fresh overlap search is still required immediately before any human-facing upstream packet or owned-fork implementation.

## Competing explanations and discriminators

### H1 — permanent hang after shutdown

The internal ordinary blocking spawn receives `ShuttingDown`; Tokio returns a join handle that never resolves; `ReadDir` stores it in `State::Pending`; no worker can execute the refill.

Discriminator: exact target test reaches the refill after shutdown and remains pending without any possible task source.

### H2 — runtime shutdown semantics intentionally permit this

Tokio may consider any continued use of such an object after runtime shutdown outside its supported progress contract.

Discriminator: find an explicit project/runtime contract establishing that filesystem objects retained across shutdown may permanently pend, rather than returning an error or panic. No such contract was established in this pass.

### H3 — refill is already complete before shutdown

The initial async constructor preloads enough directory state that the later call never needs blocking work.

Discriminator: use strictly more entries than one internal chunk and verify the transition from buffered `Idle` state to refill.

## Negative results

- The first directory chunk is populated during `fs::read_dir`; a tiny directory is not a useful reproducer.
- This is not the same path as #8182: `File` writes use the mandatory blocking spawn mechanism and have a different failure state transition.
- No separate channel/timer/io_uring finding was promoted from the first pass because the obvious consequential cases are already publicly occupied.
- No claim is made that normal runtime operation hangs; the candidate depends specifically on retaining and polling `ReadDir` across runtime shutdown.

## Repair directions to evaluate only after execution

1. Use a mandatory blocking spawn for `ReadDir` refill and convert failure into an `io::Error`, preserving the iterator state or moving it into an explicit terminal state.
2. Introduce a filesystem-internal blocking helper whose shutdown behavior is error-returning rather than non-resolving.
3. Document retained-after-shutdown behavior only if maintainers consider permanent pending intentional; this would need strong contract evidence because the current `poll_next_entry` wording promises a future wakeup when pending.

Direction 1 appears locally smallest, but this scout does not promote implementation until target execution proves the mechanism and a source/history pass checks why `ReadDir` uses ordinary rather than mandatory blocking.

## Required next gate

Run the prepared discriminator on exact Tokio revision `625954f365727668cb02d04172b34f1149637728` in target-native tests, then inspect history for the blocking refill choice. If the exact test confirms the permanent pending state and no intentional contract explains it, promote a focused `fs_dir` regression plus minimal state-machine repair in an owned fork.

Disposition: **EXECUTE**.
