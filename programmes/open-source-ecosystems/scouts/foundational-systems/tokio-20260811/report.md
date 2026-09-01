# Tokio boundary scout — 2026-08-11

State: `ready-for-synthesis`

Parent: fieldwork #211 / OE-05 foundational systems

Target: `tokio-rs/tokio`

Pinned upstream revision: `af9376300907dd187e0fdca793ccda2fa62de5ec`

Upstream contact authorized/performed: `false` / `false`

## Question

Across Tokio I/O, sync, task, time, process, signal, and runtime lifecycle paths, which concrete boundary can violate a correctness, cancellation, wakeup, resource, or ordering invariant under partial progress, shutdown, reuse, or failure?

## Source map

The strongest surviving cluster is `PollEvented` plus Unix process/pipe adapters.

- `tokio/src/io/poll_evented.rs`: `poll_read` clears readiness after a successful short read on epoll/kqueue targets, and clears readiness after `WouldBlock`; `poll_write` mirrors the short-write rule. On the forced Mio `poll` backend the short-read optimization is compiled out, but `WouldBlock` still only clears Tokio's readiness state.
- `tokio/src/process/unix/mod.rs`: `ChildStdio` wraps `PollEvented<Pipe>`; its `AsyncRead` delegates directly to `PollEvented::poll_read`. `Pipe` implements Mio `Source` through raw `SourceFd` registration/reregistration/deregistration.
- `tests-integration/tests/process_stdio.rs`: existing process stdio integration coverage exercises large concurrent streams, capture, EOF, and pipe chaining. It does not pin packet-mode `O_DIRECT` behavior or the Mio `poll` backend re-arm boundary.
- `tokio/src/net/unix/pipe.rs`: public Tokio pipe ends use `PollEvented<mio::unix::pipe::{Sender,Receiver}>`, providing an adjacent comparison surface where Mio owns the pipe source type.

## Ranked candidates

### 1. PROMOTE — Linux packet-mode pipe short-read starvation (#7051)

Issue #7051 remains open, unassigned, labeled `C-bug`, and has no matching PR in the overlap search performed for this scout.

Mechanism is still present on pinned master: `PollEvented::poll_read` treats any successful short read (`0 < n < len`) as proof that an epoll/kqueue source was drained and clears readiness. Linux `O_DIRECT` packet-mode pipes deliberately return one packet per read, capped at `PIPE_BUF`, even when more packets are queued. A 64 KiB read can therefore return 4 KiB while more data remains immediately readable; Tokio clears the readiness it already has and can sleep waiting for an edge that never arrives.

The maintainer response on #7051 already confirms the short-read optimization as the cause and flags the dynamic `O_DIRECT` bit as the design complication. The current pinned source still contains the same optimization.

Why this is a good branch candidate:

- deterministic Linux-only fixture;
- correctness/liveness failure rather than performance-only behavior;
- bounded owner in `PollEvented` / process-pipe handling;
- existing reproducer and a crisp negative control: ordinary pipe vs packet-mode pipe, or 4096-byte buffer vs 65536-byte buffer;
- no active PR found by searches for `7051` and `O_DIRECT`.

Design constraint: caching `O_DIRECT` at registration time is weak because `F_SETFL` can change it later. A useful implementation experiment should preserve the socket short-read optimization while exempting packet-mode pipes through a source-aware path, or prove a cheaper safe discriminator.

### 2. PROMOTE TO CROSS-REPO PROBE — Mio poll-backend process-pipe re-arm failure (#8042)

Issue #8042 remains open, unassigned, labeled `C-bug`, with no matching Tokio PR found by searches for `8042`, `poll backend SourceFd`, or process-pipe re-registration.

The reporter reduced the behavior to Mio alone and reproduced it on Cygwin, Solaris, and Linux with `RUSTFLAGS='--cfg mio_unsupported_force_poll_poll'`. Broken mode sees the first byte and times out on the second; explicit `Registry::reregister` after `WouldBlock` restores delivery.

Tokio's pinned `ChildStdio` uses a raw-`SourceFd` `Pipe` and direct reads through `PollEvented`. On `WouldBlock`, `PollEvented` clears Tokio readiness. The issue's Mio reduction says the `poll` backend also needs source re-registration because delivered interests are removed. This makes the likely ownership boundary Tokio↔Mio rather than a Tokio-only one.

Recommended discriminator:

1. exact pinned Tokio checkout;
2. Linux current CI host;
3. run a process-stdio two-burst test normally as the epoll control;
4. rerun with `RUSTFLAGS='--cfg mio_unsupported_force_poll_poll'`;
5. compare `tokio::process::ChildStdout` against `tokio::net::unix::pipe` / Mio pipe source behavior;
6. instrument whether an explicit reregister at the raw-SourceFd boundary restores the second burst.

This is especially valuable because the same synthetic Linux job can exercise a backend otherwise associated with Cygwin/Solaris.

### 3. PARK / REVIEW HELP — io_uring submit-error UAF (#8255)

Severity is high, but overlap is occupied. Issue #8255 has an explicit maintainer comment pointing to PR #8185 as the existing fix. Fieldwork should treat this as review territory unless that PR is abandoned and ownership is refreshed.

### 4. STOP AS IMPLEMENTATION — repeated `File::poll_write` panic (#8182)

PR #8183 explicitly fixes #8182 with regression coverage. Occupied.

### 5. STOP AS IMPLEMENTATION — `tokio_test::io::Mock` unexpected-write hang (#8329)

PR #8347 explicitly fixes #8329 and adds the relevant interleaving coverage. Occupied.

### 6. STOP / CONTRACT LANE — mpsc permit send after receiver drop (#7714)

PR #8278 records the chosen semantics as documentation/tests after discussion rejected the behavioral change as too invasive. This is a contract clarification lane, not a clean bug-fix branch.

### 7. PARK — AsyncFd EPOLLERR wake semantics (#7938)

The failure is real for SocketCAN interface deletion, but maintainer discussion frames explicit `Interest::ERROR` as current semantics and explores API tradeoffs. This needs interface design evidence, not a quick implementation branch.

## Negative results

- `tokio::fs::File` disk-full flush data-loss issue #6325 has PR #6330 attached; occupied.
- io_uring #8255 has PR #8185; occupied.
- recent mock-I/O lost-wakeup reports are already paired with active PR work.
- scheduler and runtime-shutdown searches produced broad design issues without a comparably bounded, unoccupied, current-CI discriminator in this pass.

## Recommended execution order

1. **#7051 exact-checkout Linux reproduction.** Preserve the issue's large-buffer packet-pipe case, add an ordinary-pipe control, and pin whether current master still stalls after the first 4096-byte packet.
2. **#8042 forced-poll Tokio reproduction.** Convert the reporter's Mio-only proof into a Tokio integration discriminator using current master and `mio_unsupported_force_poll_poll`.
3. If #8042 reproduces in Tokio, split ownership by comparing raw `SourceFd` process stdio against `mio::unix::pipe`-backed Tokio pipes and by testing explicit re-registration.
4. Only after fresh overlap checks, decide whether #7051 or #8042 deserves an implementation carrier.

## Evidence labels

- `source-read`: pinned Tokio revision and project contribution instructions.
- `reported-reproduction`: upstream issue fixtures and maintainer discussion.
- `overlap-searched`: open issues/PRs queried during this scout.
- `target-executed`: pending; this connector session does not provide a target checkout runner.

## Return

Disposition: `INVESTIGATE`.

Best first branch: #7051 because it is a confirmed owning mechanism, unassigned, unoccupied in the searches performed, and has a deterministic Linux fixture with a small source surface.

Best research bender: #8042 because Linux can emulate the relevant Mio poll backend, making a cross-platform readiness bug testable in ordinary CI and potentially exposing a reusable Tokio↔Mio re-arm invariant.