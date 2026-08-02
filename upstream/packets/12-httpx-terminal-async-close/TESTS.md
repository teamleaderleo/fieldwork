# Tests and receipts — Unit 12 terminal async-response close

## Current judgment

`ACCEPT — exact executed patch is published`

## Exact identities

- HTTPX base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Pre-repair source: `18256f10d1b306bdf87a1bab24b214c15839147b`
- Published source: `d5f9e3dffce3342d8c02ec2c1d3ed9588a83b803`
- Source branch: `fieldwork/171-terminal-close-source`
- Source PR: `teamleaderleo/httpx#6`
- Execution PR: `teamleaderleo/httpx#9`, closed without merge
- Final exact run: `30752805069`

## Baseline and design correction

Exact reconstructed pre-repair production blobs produced:

```text
4 failed, 1 passed in 3.28s
```

Direct re-entry timed out and successful elapsed included cleanup latency. A first task-ID repair fixed direct re-entry but timed out when delegated cleanup spawned and awaited a descendant task. That disproved task identity as the ownership boundary.

The selected inherited `ContextVar` stack passed direct, descendant, nested outer/inner/outer, unrelated-waiter, failure, cancellation, terminal-unknown, and elapsed controls.

## Exact published blobs

| File | Blob |
| --- | --- |
| `httpx/_models.py` | `0533a7324d0ed45ffb1087570551efcdaed02fa5` |
| `httpx/_client.py` | `510b41959383dcf78bd311a236afc44dd92d010a` |
| `tests/client/test_async_client_terminal_close_elapsed.py` | `67545aede0ba92364f70dc9f37c5c2e0a010c836` |
| `tests/models/test_async_response_close_reentry.py` | `0be56b2cb9a9a2e7fabc1a6bc107bbcca520fd67` |

The published PR file list is exactly six files, including the unchanged terminal-unknown and cancellation tests.

## Final hosted execution

Run `30752805069` applied the exact packet patch to pre-repair head `18256f10...` and verified the staged six-file fence before executing.

### Python 3.9 focused — job `91509719800`

Passed exact source and repaired hashes, asyncio and Trio controls, and diff hygiene.

### Python 3.13 focused — job `91509719821`

Passed the same exact identity, backend, and hygiene controls.

### Python 3.13 full — job `91509719767`

```text
Ruff format: 64 files already formatted
Mypy: no issues found in 64 source files
Ruff lint: all checks passed
Package and Twine checks: passed
Documentation build: passed
Complete suite: 1445 passed, 1 skipped in 16.86s
Coverage: 8210 statements, 0 missed, 100%
```

## Evidence transfer to published head

Published head `d5f9e3df...` has the exact reviewed and executed production/test blob hashes and exact six-file fence. No product byte changed between execution and publication. The target-executed and full-gate evidence therefore transfers semantically within that immutable fence.

The automatic Test Suite event on the published head, run `30755566581`, concluded `action_required` before creating jobs. It provides no product result and is classified as workflow admission. It does not supersede run `30752805069`.

## Claim-to-evidence summary

- at-most-once arbitrary cleanup: target-executed, passed;
- original owner failure/cancellation: target-executed under asyncio and Trio, passed;
- fresh neutral observer errors and traceback-graph release: target-executed, passed;
- direct, descendant, and nested cycle detection: target-executed under Python 3.9/3.13 and asyncio/Trio, passed;
- unrelated waiter settlement: target-executed, passed;
- elapsed compatibility: deterministic target control, passed;
- repository compatibility: named full gate, `1445 passed, 1 skipped`, 100% coverage.

## Historical harness corrections

The executor corrected an untracked-file fence omission, Ruff formatting, a mypy-invalid monkeypatch target, and unreachable defensive test branches. Every correction was rerun through the exact gates without weakening a product assertion.
