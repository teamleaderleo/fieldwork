# Unit 12 source-materialization attempt — 2026-08-01

## Scope

Only unit 12 from `teamleaderleo/fieldwork#435` was touched. No public upstream issue, discussion, pull request, review, or comment was created.

## Existing owned fork and clean source

- Owned fork: `teamleaderleo/httpx`
- Canonical source branch: `fieldwork/171-terminal-close-source`
- Clean source head before and after this attempt: `18256f10d1b306bdf87a1bab24b214c15839147b`
- Base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Source PR: `teamleaderleo/httpx#6`
- Current clean fence: five files

The user already had the HTTPX fork. No new fork was created.

## Exact reconstruction and repaired blobs

The candidate production files were reconstructed exactly from HTTPX 0.28.1 plus the post-release wording correction at `4189b7f051c6c51ce74c3bee1a5f269f9c50c6b2`.

Exact current blobs:

- `httpx/_models.py`: `3ccb5290ceb95d96e24047bcec2897c52de16176`
- `httpx/_client.py`: `79934d050cd77414fb6f9c1024f42f6029c924e0`

Exact locally repaired blobs:

- `httpx/_models.py`: `781977bec302ab67921fb9024cc14a9f97f756f4`
- `httpx/_client.py`: `510b41959383dcf78bd311a236afc44dd92d010a`
- `tests/client/test_async_client_terminal_close_elapsed.py`: `c3a27b2f65f04c723a4fc330f25215dcc6565e1c`
- `tests/models/test_async_response_close_reentry.py`: `f6ede0c73350224c563cab85786463b7cbb07bcf`

The repaired model and both repaired/new test blobs were uploaded through the owned fork's Git object API. The repaired client blob could not be safely attached through the available whole-file write surface during this run. The retained patch remains the authoritative complete repair artifact.

## Tests executed

Exact current production reconstruction:

```text
PYTHONPATH=/tmp/httpx-current pytest -q \
  tests/models/test_async_response_close_reentry.py \
  tests/client/test_async_client_terminal_close_elapsed.py

4 failed, 1 passed in 3.28s
```

Failures were the two request-bound/requestless owner re-entry timeouts, the caught re-entry/external-waiter timeout, and elapsed `10.0` rather than `2.0`.

Exact repaired local package:

```text
PYTHONPATH=/tmp/httpx-exact-repaired pytest -q \
  tests/models/test_async_response_close_reentry.py \
  tests/client/test_async_client_terminal_close_elapsed.py

5 passed in 0.12s
```

`python -m py_compile` passed for repaired `httpx/_models.py` and `httpx/_client.py`.

Limits: Python 3.13 with asyncio locally; Trio was unavailable. The complete repaired source did not receive a canonical GitHub commit or full repository gate in this attempt.

## Temporary carrier history

Three temporary owned-fork commits attempted patch application and target execution:

- `abcf1858cc958ac75c3a879c284056fcc3a2d147` — first workflow carrier; patch extraction defect found before product modification.
- `f30f2fc48ad7e5945ddee5523821cd0c6db6f655` — simplified workflow carrier using the Fieldwork packet patch.
- `70e3efa6819efc06e46f9ec0df66336a6924d60a` — trigger commit after the workflow existed on the branch.

The hosted jobs did not start during the working session. That history is preserved on `fieldwork/171-terminal-close-repair-carrier`. The canonical source ref was force-restored to `18256f10d1b306bdf87a1bab24b214c15839147b`, leaving no workflow machinery in the source candidate.

## Current blocker and continuation

Disposition remains `REPAIR`.

Next worker should use a patch-capable checkout of `teamleaderleo/httpx`, apply `patches/0001-fix-reentrant-close-and-elapsed-sampling.patch` to clean head `18256f10d1b306bdf87a1bab24b214c15839147b`, verify the exact six-file fence, then run focused asyncio/Trio tests on Python 3.9 and 3.13 plus `scripts/check`, full tests, 100% coverage, package build, and strict docs build.

The exact same-task identity repair does not establish descendant-task provenance; retain that as an explicit review question.
