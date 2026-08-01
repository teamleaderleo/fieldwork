# Unit 12 — Preserve terminal async-response state after uncertain close

## Current disposition

`REPAIR`

Last verified: `2026-08-01`  
Worker: `chatgpt:gpt-5.6-thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Public upstream contact authorized: `no`

## In simple words

HTTPX responses delegate asynchronous cleanup to a public `AsyncByteStream`. Cleanup can commit an effect and then raise or receive cancellation. Retrying can repeat irreversible work; declaring success can hide an uncertain result.

The selected candidate correctly makes an escaped delegated-close failure terminal, invokes arbitrary cleanup once, gives the initiating caller the original exception, gives observers fresh neutral errors, blocks reads after close begins, and avoids retaining the owner's traceback graph.

Two deterministic defects remain at the exact clean source head:

- same-task re-entry waits on the owner's event and deadlocks until cancellation;
- successful client elapsed time is sampled after delegated cleanup, so arbitrary cleanup latency changes the existing measurement.

A retained repair patch adds owner-task detection, request-bound/requestless/external-waiter regressions, and pre-cleanup elapsed sampling with post-success publication. Exact reconstructed current source fails four of five new controls; the exact repaired local package passes all five.

## Exact identities

- Public upstream base inspected: [`b5addb64f0161ff6bfe94c124ef76f6a1fba5254`](https://github.com/encode/httpx/commit/b5addb64f0161ff6bfe94c124ef76f6a1fba5254)
- Owned fork: [`teamleaderleo/httpx`](https://github.com/teamleaderleo/httpx)
- Canonical source branch: `fieldwork/171-terminal-close-source`
- Canonical clean source head: [`18256f10d1b306bdf87a1bab24b214c15839147b`](https://github.com/teamleaderleo/httpx/commit/18256f10d1b306bdf87a1bab24b214c15839147b)
- Canonical source PR: [`teamleaderleo/httpx#6`](https://github.com/teamleaderleo/httpx/pull/6)
- Repair carrier branch: `fieldwork/171-terminal-close-repair-carrier`
- Repair carrier head: [`70e3efa6819efc06e46f9ec0df66336a6924d60a`](https://github.com/teamleaderleo/httpx/commit/70e3efa6819efc06e46f9ec0df66336a6924d60a)
- Retained repair patch: [`patches/0001-fix-reentrant-close-and-elapsed-sampling.patch`](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)
- Fieldwork packet branch: `upstream/12-httpx-terminal-async-close`
- Exact packet head: recorded in the latest `#435` handoff

The user already had the HTTPX fork. No new fork was created.

## Clean source fence

The canonical source remains clean and contains exactly five changed files relative to the pinned base:

1. `httpx/_models.py`
2. `httpx/_client.py`
3. `tests/models/test_async_response_close_terminal_unknown.py`
4. `tests/models/test_async_response_close_terminal_cancellation.py`
5. `tests/client/test_async_client_terminal_close_elapsed.py`

The proposed repaired source has a six-file fence by adding `tests/models/test_async_response_close_reentry.py` and modifying the two production files plus the elapsed regression.

No temporary workflow file remains on the canonical source branch.

## Exact source and repair blobs

Exact current production reconstruction:

- `_models.py`: `3ccb5290ceb95d96e24047bcec2897c52de16176`
- `_client.py`: `79934d050cd77414fb6f9c1024f42f6029c924e0`

Exact locally repaired blobs:

- `_models.py`: `781977bec302ab67921fb9024cc14a9f97f756f4`
- `_client.py`: `510b41959383dcf78bd311a236afc44dd92d010a`
- elapsed test: `c3a27b2f65f04c723a4fc330f25215dcc6565e1c`
- re-entry test: `f6ede0c73350224c563cab85786463b7cbb07bcf`

The repaired model and both repaired/new test blobs were uploaded through the owned fork's Git object API. The available whole-file write surface could not safely attach the repaired 65 KB client blob during this run. The retained patch is the authoritative complete repair artifact.

## Tests and receipts

### Exact current source receipts

Direct source Test Suite run `30631127167` passed.

Execution run `30631155839` passed at clean head `18256f10...`:

- Python 3.13 job `91157545025`: exact fence, dependencies, `scripts/check`, package/docs build, full suite, 100% coverage, 16 focused tests, and hygiene;
- Python 3.9 job `91157545125`: exact fence, dependencies, 16 focused tests, and hygiene.

Those receipts predate the new re-entry and successful-elapsed discriminators.

### New exact controls

Exact reconstructed current production:

```text
4 failed, 1 passed in 3.28s
```

Failures:

- requestless same-task re-entry timed out;
- request-bound same-task re-entry timed out;
- caught re-entry with an unrelated waiter timed out;
- successful elapsed was `10.0` seconds rather than the pre-cleanup `2.0` sample.

Exact repaired local package:

```text
5 passed in 0.12s
```

`python -m py_compile` passed for repaired `_models.py` and `_client.py`.

Limit: Python 3.13 with asyncio locally; Trio was unavailable. The complete repaired source has no canonical GitHub head or complete repository gate yet.

See [`receipts/materialization-attempt-2026-08-01.md`](./receipts/materialization-attempt-2026-08-01.md) for exact carrier commits, reconstruction details, and restoration of the clean source ref.

## Contribution route

- Target project: `encode/httpx`
- Proposed destination: `encode/httpx:master`
- Proposed title: `Preserve terminal async response state after uncertain close`
- Work class: `upstream-fork research`
- Proposed route after repair: HTTPX `Potential Issue` discussion first
- Public upstream interaction: none
- Public-contact authority: absent

## Prior art and adjacent work

Duplicate and prior-art searches on `2026-08-01` found no equivalent implementation. HTTPX Discussion `#2370` is adjacent cancellation work but does not define terminal response-close settlement or same-owner re-entry.

Excluded adjacent lanes:

- synchronous response close: Fieldwork `#185`;
- HTTPCore retirement: Fieldwork `#227`;
- multi-transport client shutdown: Fieldwork `#177`;
- same-socket/capacity behavior: separate records.

## Remaining blockers

1. Apply the retained patch to clean head `18256f10d1b306bdf87a1bab24b214c15839147b` in a patch-capable checkout.
2. Verify the exact six-file fence and clean commit history.
3. Run focused asyncio and Trio controls on Python 3.9 and 3.13.
4. Run `scripts/check`, complete tests, 100% coverage, package build, and strict docs build.
5. Complete an independent whole-diff review at the unchanged repaired head.
6. Recheck current base, duplicate records, and contribution policy immediately before any authorized contact.
7. Obtain explicit authorization before creating an upstream discussion or PR.

Review question retained: task-ID comparison detects the exact owning task; descendant-task provenance remains unproven.

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue/discussion draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review guide](./REVIEW.md)
- [Original reentrant-close model](./receipts/reentrant-close-probe.md)
- [Exact repair execution](./receipts/repair-execution-2026-08-01.md)
- [Source materialization attempt](./receipts/materialization-attempt-2026-08-01.md)
- [Retained repair patch](./patches/0001-fix-reentrant-close-and-elapsed-sampling.patch)

## Continuation

Start from the clean canonical source head and the retained patch. Do not resume from the carrier branch. Preserve the six-file fence, renew all target gates, update source PR `#6`, Fieldwork issue `#171`, this packet, and parent issue `#435`, and keep public upstream untouched until separate authority is recorded.
