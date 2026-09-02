## In simple words

The crash finding survives review, but the first synchronous `InputAck` patch should be treated as a correctness baseline rather than the final design.

The local terminal-host channel already supports many simultaneously outstanding control requests: every request gets a unique `request_id`, `ControlResponses` stores independent waiters in a hash map, and the socket writer lock is held only while a frame is written. The first patch accidentally defeats that concurrency one layer higher by holding the PTY runtime mutex while it blocks for `InputAck`.

The next bounded candidate should therefore keep the targeted owner acknowledgement but split **send** from **wait**:

1. under the short PTY runtime lock, register one input waiter and write the `Input(request_id=N)` frame;
2. release the PTY runtime lock immediately;
3. wait for `InputAck(N)` outside that lock;
4. let other receipted writes register and enter the terminal-host socket while earlier callers are waiting;
5. keep ordinary interactive input on request id zero with the existing fire-and-forget behavior.

This preserves the exact correctness boundary proved by the crash scout — success follows authoritative PTY write/flush — without turning the entire terminal runtime into a stop-and-wait lane.

Current design disposition: **REPAIR the synchronous candidate into split-phase targeted ACK before considering a new cumulative local protocol.**

## Current source and evidence

Current upstream at this review is `6044a8b3f43152d2e6fc17f771fd4b277b393118`.

The original crash audit ran at `eaa899cb20bd411019744fbd2bdedeb397f3070b`. The relevant terminal-host/resource owners remain source-continuous through current upstream; the intervening current-main changes do not touch those owners.

The retained false-success reproduction is target-executed: a frozen terminal host let the mux commit a successful `terminal.input.write` receipt while an independent PTY-child oracle showed zero delivered bytes, after which killing mux + host made the queued bytes permanently disappear.

The first `InputAck` candidate's focused refinement carrier also executed successfully through its relevant gates:

- terminal-host-focused core tests: 119 passed, 0 failed;
- resource-router content tests: 18 passed, 0 failed;
- the full core-library gate then failed on nine unrelated agent-hook, snapshot, and browser-view schema tests after 1,172 tests passed.

That broad failure is not promoted as a candidate regression, but the branch must still receive a clean exact-head full gate before any final acceptance.

## Why not immediately copy the remote cumulative-ACK protocol?

Current remote PTY already demonstrates the stronger pattern:

- input writes receive monotonically increasing sequence numbers when sequence ACKs are enabled;
- up to 256 writes / 4 MiB may remain pending;
- the daemon emits cumulative `pty.input_ack(seq)` events;
- an ACK drains all pending writes through that sequence and releases buffered input/backpressure.

That is strong precedent for bounded asynchronous owner acknowledgement.

It does **not** imply that local terminal-host input needs a second sequence domain immediately. The local channel already has targeted request IDs and concurrent waiter infrastructure. A new cumulative local sequence would add framing, ordering, rollover, compatibility, waiter-drain, and protocol-violation rules before evidence shows ACK-frame count is the bottleneck.

The useful lesson to copy first is the remote design's **bounded outstanding window**, not necessarily its wire shape.

## Latency model

`cmux-terminal-input-owner-ack-latency-model.py` is a dependency-free deterministic queueing model. It keeps every timing assumption explicit and compares:

- `accepted`: return after local submission;
- `stop_wait`: submit one write, wait for delivery + ACK, then submit the next;
- `pipelined_ack`: targeted ACK per write, with multiple writes outstanding;
- `cumulative_ack`: bounded pipeline where one ACK covers several writes.

Illustrative run only — **not a cmux performance claim**:

```text
writes=5000
submit_us=5
ipc_rtt_us=100
owner_us=15
window=256
ack_every=16

accepted        ~25.000 ms total   ~200,000 writes/s     0 ACK frames
stop_wait      ~600.000 ms total     ~8,333 writes/s  5,000 ACK frames
pipelined_ack   ~75.105 ms total    ~66,573 writes/s  5,000 ACK frames
cumulative_ack  ~75.105 ms total    ~66,573 writes/s    313 ACK frames
```

The structural result matters more than the numbers:

- one durable write cannot truthfully complete before the owner-delivery evidence exists, so its minimum completion latency includes the owner acknowledgement under every truthful design;
- a sequential caller that waits for each API call before issuing the next also gets no throughput win from cumulative ACKs;
- stop-and-wait becomes RTT-limited when many writes could otherwise be outstanding;
- split-phase targeted ACK removes that unnecessary serialization;
- cumulative ACK mainly reduces ACK traffic once writes are already pipelined.

A scratch Python `socket.socketpair()` echo characterization on the investigation Linux environment measured 20,000 one-byte round trips at roughly 18.1 microseconds median and 38.2 microseconds p95. This is **model-supporting host characterization only**: Python scheduling, interpreter overhead, kernel, and runner load all contribute. It is not target-native cmux performance evidence.

## Additional correctness repair: exited hosted terminals

The first candidate copied `PtyRuntime::ExitedHosted => Ok(())` into `write_bytes_confirmed`.

That behavior is intentional for ordinary human input: a keep-on-exit terminal displays its final screen and silently ignores later keystrokes instead of surfacing an error for every keypress.

It is the wrong contract for a receipted API mutation. If there is no live PTY owner, a new durable input mutation must fail **known-before-effect**, not commit success for bytes that were deliberately dropped.

The split-phase candidate should therefore preserve silent drop only in `write_bytes`; `write_bytes_confirmed` should return a known pre-effect error for `ExitedHosted`.

## Candidate shape

Smallest next implementation:

- retain additive `InputAck` and `supports_input_ack` from the first candidate;
- add an input-ack receipt/ticket that owns the registered waiter and can wait after the PTY runtime lock is released;
- register/write the targeted `Input` under the short runtime/socket-writer critical sections;
- wait for the targeted response outside the PTY runtime lock;
- bound pending receipted input, preferably using the existing remote precedent of a finite outstanding-write window rather than permitting unbounded waiter growth;
- classify legacy unsupported hosts, an exhausted local pending window, and an exited hosted terminal as known pre-effect failures;
- retain ambiguous classification for a write/ACK timeout after bytes may have crossed the socket;
- keep request-id-zero interactive input behavior unchanged.

## Gates

Before selecting this over the simpler synchronous contender:

1. target test proving `InputAck` still follows PTY write/flush;
2. legacy-host pre-effect control;
3. exited-host pre-effect control;
4. concurrency discriminator proving write B can enter the host channel while write A is awaiting its ACK;
5. bounded-window control proving overload fails before sending the excess write;
6. focused resource-router tests;
7. focused terminal-host tests;
8. full `cmux-tui-core` gate, with unrelated current-main failures classified separately rather than silently ignored;
9. target-native local IPC/ACK characterization if the remaining question is whether one ACK per receipted write is expensive enough to justify cumulative local ACKs.

## Decision boundary

Do **not** weaken `terminal.input.write` to "accepted for delivery" silently. It is a public mutation with idempotent durable-effect machinery, so replaying a committed success currently carries stronger meaning than mere queue admission.

If maintainers explicitly want best-effort accepted semantics instead, that is a legitimate alternative design, but it should be a contract-level change: the durable result must say accepted/queued rather than external effect succeeded.

For the existing durable-mutation contract, owner-backed delivery remains the better invariant. The design question is how to obtain that evidence without needless serialization; split-phase targeted ACK is now the smallest promising answer.
