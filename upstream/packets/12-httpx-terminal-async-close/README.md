# Unit 12 — Preserve terminal async-response state after uncertain close

## Current disposition

`READY`

Last verified: `2026-08-03`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Public upstream contact authorized: `no`

## In simple words

HTTPX delegates asynchronous response cleanup to public `AsyncByteStream` code. That code can perform an irreversible effect and then fail or receive cancellation. Automatic retry can duplicate the effect, while retaining the original exception can retain arbitrary traceback and application-object graphs.

The selected contract attempts arbitrary cleanup once. The initiating caller receives its original failure or cancellation; observers receive fresh neutral `CloseError` objects; reads remain blocked after close begins; successful close is published only after cleanup succeeds; and no arbitrary owner traceback graph is retained.

Direct, descendant-task, and nested response-close cycles are detected with an inherited `ContextVar` stack of active close-state markers. Successful elapsed time is sampled before delegated cleanup and published only after cleanup succeeds.

## Exact source

- Public upstream: `encode/httpx`
- Public base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Owned fork: `teamleaderleo/httpx`
- Canonical source PR: [`teamleaderleo/httpx#6`](https://github.com/teamleaderleo/httpx/pull/6)
- Canonical branch: `fieldwork/171-terminal-close-source`
- Exact source head: [`d5f9e3dffce3342d8c02ec2c1d3ed9588a83b803`](https://github.com/teamleaderleo/httpx/commit/d5f9e3dffce3342d8c02ec2c1d3ed9588a83b803)
- Execution carrier: [`teamleaderleo/httpx#9`](https://github.com/teamleaderleo/httpx/pull/9), closed without merge

## Exact six-file fence

1. `httpx/_client.py`
2. `httpx/_models.py`
3. `tests/client/test_async_client_terminal_close_elapsed.py`
4. `tests/models/test_async_response_close_reentry.py`
5. `tests/models/test_async_response_close_terminal_cancellation.py`
6. `tests/models/test_async_response_close_terminal_unknown.py`

No workflow, packet, dependency, generated, or adjacent-lane file is present.

## Exact repaired blobs

| File | Blob |
| --- | --- |
| `httpx/_models.py` | `0533a7324d0ed45ffb1087570551efcdaed02fa5` |
| `httpx/_client.py` | `510b41959383dcf78bd311a236afc44dd92d010a` |
| `tests/client/test_async_client_terminal_close_elapsed.py` | `67545aede0ba92364f70dc9f37c5c2e0a010c836` |
| `tests/models/test_async_response_close_reentry.py` | `0be56b2cb9a9a2e7fabc1a6bc107bbcca520fd67` |

These published blobs exactly match the independently reviewed and executed packet patch.

## Exact execution

Final run `30752805069`:

- Python 3.9 focused job `91509719800`: passed under asyncio and Trio;
- Python 3.13 focused job `91509719821`: passed under asyncio and Trio;
- Python 3.13 full job `91509719767`: exact source identity, exact six-file fence, Ruff formatting and lint, mypy across 64 source files, package/Twine checks, documentation build, complete suite (`1445 passed, 1 skipped`), and complete coverage (`8210` statements, `0` missed).

Independent complete-diff review accepted the repair. Because the published source uses the same immutable blobs and fence, that review and execution evidence transfer semantically to `d5f9e3df...`.

The automatic Test Suite event on the published head, run `30755566581`, concluded `action_required` before creating jobs. This is workflow-admission evidence, not a product-test failure. The exact full-gate receipt is run `30752805069`.

## Duplicate, policy, and limits

- Current duplicate and overlap searches found no equivalent terminal async-close re-entry implementation.
- HTTPX contribution guidance prefers a Potential Issue discussion before a public behavioral change PR.
- The remaining decision is the public policy: attempt uncertain arbitrary cleanup once and never retry automatically.
- Synchronous close, HTTPCore retirement, socket reuse/capacity, and multi-transport shutdown remain separate work.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue/discussion draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Independent review](./REVIEW.md)
- [Source publication receipt](./receipts/source-publication-2026-08-03.md)
- [Final executor receipt](./receipts/final-executor-run-30752805069.md)
- [Authoritative patch](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)

## Current next action

The technical unit is ready. Surface the policy decision through the Human Review Desk. After explicit authorization, begin with an HTTPX Potential Issue discussion; do not file or comment publicly before that authority exists.
