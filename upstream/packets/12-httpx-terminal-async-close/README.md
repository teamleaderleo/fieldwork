# Unit 12 — Preserve terminal async-response state after uncertain close

## In simple words

HTTPX responses delegate asynchronous cleanup to a public `AsyncByteStream`. That cleanup can commit an effect and then raise or receive cancellation. Retrying can repeat irreversible work; declaring success can hide an uncertain result.

The current source candidate correctly makes an escaped delegated-close failure terminal, invokes arbitrary cleanup once, gives the initiating caller the original exception, gives observers fresh neutral errors, and avoids retaining the owner's traceback graph. Two deterministic defects remain at its exact head:

- same-task re-entry waits on the owner's event and deadlocks until cancellation;
- successful client elapsed time is sampled after delegated cleanup, so arbitrary cleanup latency changes the existing measurement.

A retained four-file repair patch adds owner-task detection, request-bound/requestless/external-waiter regressions, and pre-cleanup elapsed sampling with post-success publication. Exact reconstructed current source fails four of five new controls; the repaired local package passes all five.

## Current disposition

`REPAIR`

Last verified: `2026-08-01`  
Worker: `chatgpt:gpt-5.6-thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `encode/httpx`
- Proposed upstream destination: `encode/httpx:master`
- Proposed title: `Preserve terminal async response state after uncertain close`
- Contribution synopsis: represent an escaped arbitrary async stream-close attempt as terminal outcome-unknown, preserve the owner's original exception without retaining it on the response, issue fresh neutral observer failures, prevent the owning task from waiting on itself, and preserve elapsed's pre-cleanup sample while publishing only after successful cleanup.
- Work class: `upstream-fork research`
- Proposed route after repair: `Potential Issue` discussion first, following HTTPX's current contribution guide.

## Exact identities

- Public upstream base inspected: [`b5addb64f0161ff6bfe94c124ef76f6a1fba5254`](https://github.com/encode/httpx/commit/b5addb64f0161ff6bfe94c124ef76f6a1fba5254)
- Current public `master` inspected on 2026-08-01: same SHA
- Owned target fork: `teamleaderleo/httpx`
- Canonical source branch: `fieldwork/171-terminal-close-source`
- Canonical source head: [`18256f10d1b306bdf87a1bab24b214c15839147b`](https://github.com/teamleaderleo/httpx/commit/18256f10d1b306bdf87a1bab24b214c15839147b)
- Canonical source PR: [`teamleaderleo/httpx#6`](https://github.com/teamleaderleo/httpx/pull/6)
- Retained repair patch: [`patches/0001-fix-reentrant-close-and-elapsed-sampling.patch`](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)
- Fieldwork packet branch: `upstream/12-httpx-terminal-async-close`
- Fieldwork packet base: `920f87cb25dd0cc7901d59ea2019cd4b4a193b94`
- Exact packet head: recorded in the latest `#435` handoff
- Execution carrier: [`teamleaderleo/httpx#4`](https://github.com/teamleaderleo/httpx/pull/4), closed without merge
- Superseded research carriers: [`teamleaderleo/httpx#1`](https://github.com/teamleaderleo/httpx/pull/1), Fieldwork PR [`#173`](https://github.com/teamleaderleo/fieldwork/pull/173)
- Adjacent separate work: [`teamleaderleo/httpx#2`](https://github.com/teamleaderleo/httpx/pull/2), [`teamleaderleo/httpx#3`](https://github.com/teamleaderleo/httpx/pull/3), Fieldwork [`#177`](https://github.com/teamleaderleo/fieldwork/issues/177)

## Current code and tests

### Product code

- [`httpx/_models.py`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_models.py) — close admission, one-attempt coordination, terminal-failure state, read barrier, observer errors, and pickle reset; current in-flight state lacks owner identity.
- [`httpx/_client.py`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/httpx/_client.py) — publishes elapsed after successful delegated close, but currently samples after that close and includes its latency.

### Target-native tests

- [`tests/models/test_async_response_close_terminal_unknown.py`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/tests/models/test_async_response_close_terminal_unknown.py) — ordinary/control-flow failure, concurrent observers, fresh errors/causes, GC release, requestless responses, successful joining, reads, and pickling.
- [`tests/models/test_async_response_close_terminal_cancellation.py`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/tests/models/test_async_response_close_terminal_cancellation.py) — backend-native cancellation identity and terminal observers.
- [`tests/client/test_async_client_terminal_close_elapsed.py`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/tests/client/test_async_client_terminal_close_elapsed.py) — failed client-bound stream cleanup leaves elapsed unavailable and later close terminal.
- Proposed repair test: `tests/models/test_async_response_close_reentry.py` in the retained patch.
- Proposed elapsed compatibility control: appended to the existing elapsed test in the retained patch.

### Required generated or dependency files

- Not applicable.

## Changed-file fence

### Current exact source

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `httpx/_models.py` | production | yes |
| `httpx/_client.py` | production | yes |
| `tests/models/test_async_response_close_terminal_unknown.py` | regression | yes |
| `tests/models/test_async_response_close_terminal_cancellation.py` | regression | yes |
| `tests/client/test_async_client_terminal_close_elapsed.py` | regression | yes |

The exact current source is 16 commits ahead of the current base, zero commits behind.

### Proposed repaired source

The retained patch modifies the two production files, updates the elapsed regression, and adds `tests/models/test_async_response_close_reentry.py`. The complete repaired fence would contain six files.

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Blind retry can duplicate cleanup that committed before raising | `target-executed` | source-research PR #1, runs `30550892544` and `30550886069` | public custom stream model; lower-layer retirement is separate |
| Current candidate invokes delegated cleanup once and gives observers fresh neutral failures | `target-executed` | executor run `30631155839`, jobs `91157545025` and `91157545125` | current five-file head only |
| Current candidate avoids retaining the owner traceback graph | `target-executed` | GC regression in exact source run `30631155839` | arbitrary application prevalence unmeasured |
| Current candidate passes its direct repository Test Suite | `full-gate` | run `30631127167` | suite lacks the new discriminators |
| Current candidate's production blobs are reconstructed exactly | `source-read` | `_models.py` blob `3ccb5290...`; `_client.py` blob `79934d05...` | exact production files, not full checkout |
| Current candidate deadlocks on same-task re-entry | `target-executed` on exact reconstructed production blobs | new pytest run: three timeout failures | asyncio/Python 3.13 local |
| Current candidate includes cleanup latency in successful elapsed | `target-executed` on exact reconstructed production blobs | deterministic control: `10.0`, expected `2.0` | synthetic transport |
| Retained repair passes the five new/retained controls | `target-executed` on repaired local package | `5 passed in 0.12s` | asyncio/Python 3.13; branch unchanged |
| Public base is current | `source-read` | `encode/httpx:master` and owned fork `master` both at `b5addb64...` on 2026-08-01 | recheck immediately before contact |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue/discussion draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)
- [Original reentrant close model](./receipts/reentrant-close-probe.md)
- [Retained repair patch](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issue, pull-request, and discussion searches checked: `Response.aclose`, `async response close`, `CloseError`, `aclose cancellation`, re-entry, deadlock, cleanup, and elapsed.
- Equivalent implementation found: `no`
- Adjacent public record: HTTPX Discussion [`#2370`](https://github.com/encode/httpx/discussions/2370) concerns cancellation being translated during requests; it does not define terminal response-close settlement or same-owner re-entry.
- Relationship to prior owned work: this packet consolidates and corrects the selected source candidate; it does not revive the retryable predecessor.

## Remaining work

Complete in this order:

1. Apply the retained repair patch to `fieldwork/171-terminal-close-source` in a patch-capable checkout.
2. Verify the resulting exact six-file diff and commit history.
3. Run the focused controls, `scripts/check`, full target suite, build/docs, coverage, and Python 3.9/3.13 asyncio/Trio matrix.
4. Renew complete-diff review and synchronize source PR #6, issue #171, and this packet.
5. Repeat duplicate/current-main/policy checks, then request separate authority for any public discussion.

## Blockers and limits

- The exact source head deadlocks on same-task re-entry until cancellation breaks the cycle.
- The exact source head changes elapsed semantics by including delegated cleanup latency.
- The retained repair has no canonical GitHub source head or full target receipt.
- Local repaired execution covered Python 3.13/asyncio only; Trio was unavailable.
- The patch detects the exact same-task cycle; descendant-task provenance remains a review question.
- The public contract intentionally allows `is_closed == False` while reads and later close attempts remain blocked after failed cleanup. Maintainer direction should confirm this terminal-unknown representation.
- HTTPX's contribution guide prefers a discussion before implementation submission.
- The connected GitHub write surface offered full-file replacement but no safe patch application; the source branch remained unchanged to avoid rewriting large target files through an error-prone transport.
- Public upstream contact remains unauthorized.

## Latest handoff

State: `REPAIR`  
Exact source head: `18256f10d1b306bdf87a1bab24b214c15839147b`  
Exact packet head: see latest `teamleaderleo/fieldwork#435` unit-12 handoff  
Tests: old exact five-file full gate passed; exact reconstructed current production fails 4/5 new controls; retained repair passes 5/5 locally  
Temporary machinery remaining: none in canonical source; execution PR #4 is closed without merge  
Next worker action: apply the retained patch to the canonical source branch and trigger target CI  
Public upstream interaction: none
