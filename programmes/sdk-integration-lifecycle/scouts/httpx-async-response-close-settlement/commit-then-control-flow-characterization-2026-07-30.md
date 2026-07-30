# HTTPX async response close after committed cleanup and control-flow abort

## In simple words

The accepted HTTPX experiment lets another caller retry response cleanup after the first close caller is cancelled or otherwise interrupted.

That is safe when the first close attempt stopped before cleanup happened. It is not automatically safe when a custom stream completes a non-idempotent cleanup action and then raises a cancellation or another control-flow exception before returning.

In that case HTTPX cannot tell whether cleanup happened. The current retry policy calls the stream's `aclose()` method again. A waiting caller can therefore perform the cleanup effect twice.

This note records the missing public custom-stream contract before any direct source branch is selected.

## Exact inputs

- HTTPX source base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`;
- executed predecessor experiment: `teamleaderleo/httpx#1` at `04e2da580eea759e712df1656323ae0dd7d26bff`;
- current characterization head: `teamleaderleo/httpx#1` at `b3083e7ce6a6ace1756d3cf1e4ec5371663c2c55`;
- current focused workflow: `30550892544` — queued at the latest check;
- current ordinary Test Suite: `30550886069` — queued at the latest check;
- work class: upstream-fork research;
- upstream contact authorized: `false`.

## Previously accepted result

The predecessor candidate is target-executed for the exercised wrapper contract:

- one caller owns a close attempt;
- concurrent callers wait on one AnyIO event;
- only successful wrapped-stream cleanup publishes `is_closed == True`;
- ordinary failures are shared with current waiters;
- later calls may retry ordinary failure;
- owner cancellation and other control-flow `BaseException` values stay owner-scoped;
- a waiter may acquire the next attempt after owner interruption;
- body reads remain permanently blocked after close begins;
- elapsed time is published only after successful cleanup;
- transient attempt state is not pickled;
- one deterministic pre-delegation retry releases a default HTTPCore pool slot.

Those results do not define whether arbitrary public `AsyncByteStream` implementations tolerate repeated close after an ambiguous interruption.

## New discriminating stream

The new custom stream has a deliberately non-idempotent synthetic cleanup counter.

First call:

1. enters `aclose()`;
2. waits while a second response-close caller joins;
3. increments `cleanup_commits`;
4. raises `ControlFlowAbort` to the owner.

Second call:

1. the waiting response-close caller becomes the new owner;
2. invokes the same stream's `aclose()` again;
3. increments `cleanup_commits` again;
4. returns successfully.

The characterization expects the current candidate to finish with:

```text
owner observed ControlFlowAbort
waiter completed
response.is_closed == true
stream.close_calls == 2
stream.cleanup_commits == 2
```

A passing test proves the current policy duplicates a committed custom cleanup effect. It does not mean that duplication is accepted.

## Why the default pool control is insufficient

The existing default-transport test interrupts before the bound stream delegates into HTTPCore and then retries. That is a useful integration result for one safe interruption point.

HTTPCore's tested stream also has internal close guards and cancellation shielding. Those implementation details cannot silently become the contract for every third-party `AsyncByteStream` accepted by HTTPX.

## Competing contracts

### Contract A — retry-tolerant public streams

HTTPX retries after ambiguous control-flow interruption. Custom streams are expected to make repeated `aclose()` safe even if an earlier call partly or fully committed cleanup.

Advantages:

- preserves the current per-attempt state machine;
- later callers can recover when the first attempt truly stopped early;
- simple wrapper implementation.

Costs:

- the public stream interface does not currently state this requirement;
- existing custom streams may perform non-idempotent release, accounting, commit, or notification work;
- retry can duplicate an effect after cancellation arrived too late.

This contract requires documentation and compatibility evidence across representative custom transports.

### Contract B — shield authoritative cleanup

Once wrapped-stream cleanup begins, HTTPX owns it to completion under cancellation shielding. Caller cancellation is re-observed only after cleanup settles.

Advantages:

- one underlying cleanup attempt;
- no duplicate custom-stream close effect;
- completion state can reflect authoritative cleanup.

Costs:

- cancellation latency can exceed the caller's expectation;
- a stuck custom stream can hold the caller indefinitely unless cleanup has its own bound;
- AnyIO asyncio and Trio cancellation semantics need exact testing;
- waiter behavior and error ownership change.

### Contract C — ambiguous terminal failure

If the owner is interrupted after cleanup began, HTTPX does not automatically retry. It records that body use is closed and cleanup outcome is unknown or failed.

Advantages:

- avoids blind repeated cleanup;
- represents uncertainty honestly.

Costs:

- current public response state has only `is_closed` and exceptions;
- resource recovery may require transport retirement or a new private/public state;
- later callers cannot safely repair a genuinely incomplete close without a stronger stream contract.

## Required next matrix

After the current characterization executes, compare at least:

1. commit then ordinary `Exception`;
2. commit then owner cancellation;
3. commit then custom control-flow `BaseException`;
4. one waiting caller and several waiting callers;
5. no waiter followed by a later explicit retry;
6. underlying cleanup that is idempotent;
7. underlying cleanup that rejects a second call;
8. bounded shielded cleanup under asyncio and Trio;
9. stuck shielded cleanup and caller deadline behavior;
10. default HTTPCore before-delegation and after-delegation controls.

For each case record:

- number of underlying close calls;
- number of committed cleanup effects;
- owner and waiter settlements;
- `is_closed`;
- body-read state;
- elapsed availability;
- retained exception/task/event graphs;
- whether connection or stream capacity is reusable, retired, or unknown.

## Current disposition

**ACCEPT the predecessor wrapper and default-pool receipts. EXECUTE this commit-then-control-flow characterization. HOLD clean direct source integration until one public custom-stream rule is selected.**

Do not describe automatic retry as generally safe before that decision. Keep synchronous response close, delegated HTTPCore close, and multi-transport client shutdown in their separate lanes.

## Stop condition

Stop this contract pass when one rule can answer both questions without contradiction:

1. Who owns underlying cleanup after caller control-flow interruption?
2. When may HTTPX call a public custom stream's `aclose()` again?

The selected rule must pass the committed-effect matrix under asyncio and Trio and state its cancellation-latency tradeoff.

No public upstream interaction occurred.