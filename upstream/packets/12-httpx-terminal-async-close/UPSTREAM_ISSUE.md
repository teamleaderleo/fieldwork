# Potential Issue discussion draft — Define async response-close state after uncertain stream cleanup

Draft status: `ready after current-main reproduction refresh`  
Public interaction authorized: `no`

---

## Summary

`Response.aclose()` delegates cleanup to a public `AsyncByteStream`. The stream may perform an irreversible cleanup step and then raise or receive cancellation. HTTPX currently marks the response closed before that delegated call finishes.

This creates three related contract questions:

1. a failed delegated close can leave `is_closed=True` even though cleanup did not confirm success;
2. another caller can return while the first close is still running;
3. blindly retrying after an escaped failure can repeat cleanup that already committed.

Would HTTPX accept an explicit terminal outcome-unknown state for this case?

## Reproduction

```python
import anyio
import httpx


class CommitThenRaiseStream(httpx.AsyncByteStream):
    def __init__(self) -> None:
        self.close_calls = 0
        self.cleanup_commits = 0

    async def __aiter__(self):
        if False:
            yield b""

    async def aclose(self) -> None:
        self.close_calls += 1
        self.cleanup_commits += 1
        raise RuntimeError("cleanup failed after commit")


async def main() -> None:
    stream = CommitThenRaiseStream()
    response = httpx.Response(200, stream=stream)

    try:
        await response.aclose()
    except RuntimeError:
        pass

    await response.aclose()
    print(response.is_closed, stream.close_calls, stream.cleanup_commits)


anyio.run(main)
```

At commit `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`, the second call returns and prints:

```text
True 1 1
```

The response reports successful closure, while the delegated cleanup outcome was an exception after an effect committed.

A retryable wrapper design was also tested with this stream family. It invoked delegated close twice and committed the synthetic cleanup effect twice, so generic retry is unsafe without an idempotency guarantee from `AsyncByteStream`.

## Expected contract for discussion

A possible contract is:

- mark close as started before delegating, which permanently blocks body reads;
- let one caller own the delegated close and let unrelated concurrent callers join it;
- publish `is_closed=True` only after delegated cleanup succeeds;
- after an escaped delegated failure or cancellation, treat the result as terminal outcome-unknown and never invoke that arbitrary stream again;
- deliver the original exception or backend cancellation object to the initiating caller;
- give concurrent and later observers fresh neutral `CloseError` instances, without retaining the original exception or traceback graph on the response;
- reject re-entry from the task already executing the stream close, so it cannot wait on its own completion event;
- keep `elapsed` unavailable after failed cleanup, and preserve its existing pre-cleanup sample after successful cleanup.

The unusual part is that failed terminal cleanup would leave `is_closed=False` while body reads and later cleanup attempts remain blocked. That preserves completion truth, but it changes the practical meaning of `is_closed` from the current implementation and deserves maintainer direction.

## Source observation

The current implementation sets `is_closed=True` immediately before awaiting `self.stream.aclose()`. There is no public `AsyncByteStream` guarantee that repeating close after an arbitrary escaped failure is safe.

A candidate state machine has been exercised under asyncio and Trio for ordinary failure, cancellation, external concurrent callers, requestless responses, traceback isolation, garbage collection, pickling, and failed elapsed publication. Additional local discriminators found that the candidate also needs explicit same-task re-entry detection and must sample elapsed before cleanup while publishing only after success.

## Compatibility and risks

- `is_closed=False` would no longer imply that body reads or cleanup retry remain available after a failed close attempt.
- A prompt `CloseError` for same-task re-entry replaces an indefinite wait.
- The owner-reentry detector needs to remain compatible with HTTPX's supported AnyIO range.
- The generic wrapper cannot prove whether a concrete transport completed, partially completed, or failed before effect.
- HTTPCore connection retirement and client-wide multi-transport shutdown require separate policies.

## Evidence limits

- No claim about production frequency or severity.
- The duplicate-effect case uses a deterministic public custom stream.
- Real HTTP/1.1 and HTTP/2 lower-layer interruption remains outside this discussion.
- The repaired re-entry and elapsed patch has local asyncio package execution; direct repository CI remains pending.

## Versions and environment

- HTTPX commit: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Python boundaries already exercised by the candidate: 3.9 and 3.13
- Async backends already exercised by the candidate's existing controls: asyncio and Trio
- New repair controls executed locally: Python 3.13.5, AnyIO 4.13.0, asyncio

## Questions

1. Is terminal outcome-unknown the preferred generic response-layer contract after arbitrary async stream cleanup escapes?
2. Should `is_closed` remain false when successful cleanup was never confirmed, even though reads and later close attempts stay blocked?
3. Is a prompt request-associated `CloseError` acceptable for same-operation re-entry?
4. Would maintainers prefer this as one focused change or separate state-settlement and re-entry changes?

---

## Filing checklist

- [ ] Repeat current upstream discussion, issue, and pull-request search immediately before filing.
- [ ] Re-run the minimal reproduction on current public `master`.
- [ ] Confirm current AnyIO support policy and `get_current_task()` compatibility.
- [ ] Keep prevalence and impact wording within the executed evidence.
- [ ] Remove internal repository, workflow, and research references.
- [ ] Follow the current Potential Issue discussion format.
- [ ] Handle AI assistance according to the project's policy at filing time.
- [ ] Record exact user authorization before posting.
