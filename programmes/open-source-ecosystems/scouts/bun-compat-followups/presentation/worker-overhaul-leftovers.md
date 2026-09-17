# Worker overhaul follow-up breadcrumbs

Fieldwork #709 opportunistic follow-up pass. Prepared 2026-08-09 from Bun main commit `9d519e8ca9f63a19f94790c47019bd7b6752c27a` (worker / worker_threads overhaul).

Automated upstream contact: **none**.

## Why inspect this merge

The worker overhaul is unusually broad and its merge description explicitly records several remaining limitations/follow-ups. Those are useful scout inputs, but only after ownership de-duplication: a “known follow-up” in a merged PR may already have a separate RoboBun branch open.

## Already owned / do not duplicate

### UDP receive-loop starvation

The merge notes say a UDP socket whose receive buffer never drains can monopolize its event loop, including preventing worker exit.

This is already directly owned by:

https://redirect.github.com/oven-sh/bun/pull/37103

`udp: bound one readable dispatch at 32 datagrams to prevent event-loop starvation`

That PR implements the same 32-datagram per-dispatch bound used by libuv and includes a starvation regression.

**Disposition:** occupied. Do not scout as an independent contribution.

### General concurrent-task/timer fairness

The merge notes also mention file-stream/event-loop fairness. A broad ownership search finds active work in the same fairness family:

https://redirect.github.com/oven-sh/bun/pull/36479

`event_loop: yield mid-tick thread-pool re-drain to due timers and pending setImmediate`

That PR explicitly covers chained thread-pool completions and POSIX `fs.read` starvation. It may not cover every file-stream fairness case alluded to by the worker merge, but the overlap is strong enough that no independent candidate should be claimed until the exact remaining file-stream mechanism is identified.

**Disposition:** occupied/overlapping; park.

## Apparently unowned research leads

Ownership searches below are first-pass only; absence of a search result is not proof that no maintainer has private/in-progress work.

### 1. Concurrent-worker peak RSS is not returned to the OS

The merge notes distinguish:

- sequential worker churn plateaus;
- a burst of concurrent workers leaves the process resident near the concurrent peak after those workers exit;
- this is described as an allocator thread-exit policy follow-up.

Searches for the specific concurrent-worker/allocator-thread-exit symptom did not find a direct open PR or issue. There are many adjacent worker-memory PRs (blob URL ownership, queued cross-thread task leaks, resource limits), so this needs a mechanism probe before it is useful.

Questions for an internal probe:

1. Does committed/resident memory stay high because mimalloc thread heaps/pages migrate to a global cache on worker thread exit?
2. Does `Bun.gc(true)` change the plateau after every worker is joined?
3. Does the retained amount scale with worker count, per-worker peak, or only the maximum aggregate concurrent allocation?
4. Is the memory reusable by later workers in the same process even if RSS is not returned to the OS?
5. Does `MIMALLOC_PURGE_DELAY=0` / relevant mimalloc purge settings distinguish “retained cache” from a real lost allocation?

**Disposition:** interesting performance/memory lead, but not yet a small fix. Prepare a measurement probe before reading allocator code deeply.

### 2. `worker_threads` MessagePort throughput regression

The merge notes report worker_threads message throughput through the restored real `MessagePort` path at roughly 0.8x the previous ad-hoc path, while round-trip latency and Web Worker messaging are unchanged.

Searches for the exact throughput follow-up found no direct open PR/issue.

Useful internal comparison:

- parent → worker one-way flood throughput;
- worker → parent one-way flood;
- ping-pong latency;
- batched payload sizes (small scalar, 1 KiB, 64 KiB transferables);
- `node:worker_threads` versus Web `Worker` in the same Bun build;
- Node reference where the API permits a meaningful comparison.

The goal is to localize whether the 20% loss comes from serialization, MessagePort queue bookkeeping, task scheduling/budgeting, or extra JS wrapper dispatch.

**Disposition:** research lead, not contribution-sized yet.

### 3. Windows concurrent `localhost` connects can leave one connect stuck

The merge notes call this pre-existing and associate it with DNS coalescing on the connect path.

Searches for the exact `localhost` + concurrent-connect + Windows symptom did not find a direct open owner. There are many nearby Windows socket/DNS PRs, so this is easy to misclassify.

A useful internal probe would force `localhost` to produce both A/AAAA candidates and launch synchronized concurrent connects against a loopback server, recording which stage stalls: DNS waiter, candidate launch, socket poll, or JS promise settlement.

**Disposition:** keep as a medium-priority Windows-only research lead. It needs Windows execution to become actionable.

## Lower priority

### Never-settling top-level-await worker start semantics

The merge says remaining start semantics are tracked separately. Do not claim this without finding that tracker first.

### Diagnostics-only fuzzing leftovers

The merge says several diagnostics-only items are tracked separately. Treat as occupied unless a specific breadcrumb proves otherwise.

## Current conclusion

The worker merge is a good example of why the scout needs an ownership pass. A raw reading yields several tempting leftovers; at least one (UDP starvation) already has an exact active RoboBun PR, and another (file/event-loop fairness) overlaps active work heavily.

The two best genuinely open research leads from this merge are therefore:

1. concurrent-worker peak RSS retention;
2. MessagePort throughput regression.

Neither should outrank the current correctness/compatibility candidates (`Bun.connect` synchronous errno, JSX scan dependency fidelity, Request precedence, WebSocket TLS error fidelity) until a small mechanism is found.