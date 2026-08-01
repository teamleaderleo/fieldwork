# Tests and receipts — Unit 12 terminal async-response close

## In simple words

The current five-file candidate has strong exact-head execution: direct repository CI passed, and a separate executor ran the complete suite, static checks, build/docs, coverage, and 16 focused controls across Python 3.9 and 3.13. Those tests establish the terminal-unknown behavior they exercise.

A source-equivalent asyncio model then reproduced same-owner re-entry waiting on its own event. This is the largest current gap and changes the test judgment to `REPAIR`.

## Identity

- Exact upstream base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- Exact candidate head: `18256f10d1b306bdf87a1bab24b214c15839147b`
- Exact execution carrier head: `b0d72d521aa88c32f5ae48d5ce8943c1eb8ba8f5`
- Test dates: `2026-07-31` target execution; `2026-08-01` re-entry model
- Target platforms: GitHub Actions Python 3.9 and 3.13; local model Python 3.13.5
- Target dependency set: repository `requirements.txt` during exact executor; source metadata requires AnyIO and `httpcore==1.*`
- Local model: AnyIO 4.13.0, asyncio backend

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| arbitrary retry can duplicate committed cleanup | `target-executed` | owned PR #1, focused `30550892544`, suite `30550886069` | passed characterization; duplicate effect observed | custom stream model |
| one owner and external waiters share one successful attempt | `target-executed` | `test_concurrent_close_waits_for_successful_cleanup` in terminal-unknown file | passed in exact executor | excludes same-owner call |
| owner ordinary/control-flow failure stays original; observers are fresh neutral errors | `target-executed` | terminal-unknown focused controls | passed | exact candidate head only |
| backend cancellation identity stays with owner | `target-executed` | terminal cancellation file | passed under executor matrix | exact backend/dependency set |
| owner traceback graph is not retained | `target-executed` | frame-local weakref/GC control | passed | one synthetic frame-local object |
| requestless terminal observer failure remains valid | `target-executed` | requestless control | passed | response model only |
| failed client-bound cleanup leaves elapsed unavailable | `target-executed` | client elapsed failure test | passed | one custom transport |
| candidate passes direct source Test Suite | `full-gate` | run `30631127167` | success | current suite omits re-entry |
| candidate passes exact executor matrix | `full-gate` and `target-executed` | run `30631155839` | success | Python 3.9 full suite excluded after unrelated base warning; focused passed |
| same-owner re-entry waits on its own event | `source-read`, `model-executed` | retained re-entry probe | timeout reproduced | asyncio model, no HTTPX import |

## Baseline characterization

### Command or workflow

Owned research PR #1 carried target-native controls against the pinned base and retryable candidate. Exact workflow identifiers:

```text
focused: 30550892544
repository Test Suite: 30550886069
```

### Assertions

- owner enters custom stream close;
- cleanup commits a synthetic effect;
- owner receives a custom `BaseException`;
- waiter becomes retry owner under the retryable design;
- delegated close and cleanup commit counts are observed.

### Result

- status: passed characterization
- observed behavior: two close calls and two cleanup commits
- interpretation: a generic retry contract can repeat arbitrary effects
- limit: this does not establish real socket duplication or every HTTPCore failure point

## Candidate-focused tests

### Terminal unknown — ordinary and control-flow failures

- Exact source head: `18256f10d1b306bdf87a1bab24b214c15839147b`
- File: [`tests/models/test_async_response_close_terminal_unknown.py`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/tests/models/test_async_response_close_terminal_unknown.py)
- Tests and assertions:
  - at-most-once delegated cleanup;
  - original owner exception identity;
  - distinct observer exception, cause, and traceback objects;
  - terminal later calls;
  - close-start read barrier;
  - successful concurrent join;
  - requestless response;
  - frame-local object collection;
  - pickle reset.
- Result: included in 16 focused controls, passed Python 3.9 and 3.13.
- Coverage limit: no owner-task re-entry.

### Terminal unknown — real backend cancellation

- Exact source head: same
- File: [`tests/models/test_async_response_close_terminal_cancellation.py`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/tests/models/test_async_response_close_terminal_cancellation.py)
- Tests and assertions:
  - AnyIO backend-native cancellation object reaches owner unchanged;
  - observers get fresh neutral errors/causes;
  - stream close runs once;
  - reads stay blocked;
  - public `is_closed` remains false after uncertain cleanup.
- Result: passed exact focused matrix.
- Coverage limit: owner is cancelled externally; delegated stream does not re-enter response close.

### Client elapsed publication

- Exact source head: same
- File: [`tests/client/test_async_client_terminal_close_elapsed.py`](https://github.com/teamleaderleo/httpx/blob/18256f10d1b306bdf87a1bab24b214c15839147b/tests/client/test_async_client_terminal_close_elapsed.py)
- Tests and assertions:
  - first close failure reaches owner;
  - second close is terminal and does not re-run stream cleanup;
  - elapsed remains unavailable after failed cleanup.
- Result: passed exact focused matrix.
- Coverage limit: the successful blocking-close/pre-cleanup sample control was reviewed in source history; confirm its exact retained location when repairing the branch.

### Same-owner re-entry model

- Exact source modeled: same
- Receipt: [`receipts/reentrant-close-probe.md`](./receipts/reentrant-close-probe.md)
- Command:

```text
python /tmp/reentrant_probe.py
```

- Environment: Python 3.13.5, AnyIO 4.13.0, asyncio
- Result:

```text
TIMEOUT 1 False True
```

- Failure classification: product-design blocker demonstrated at mechanism scope
- Coverage limit: dependency-free model; target-native asyncio/Trio tests still required

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format/lint/typecheck | executor run `30631155839`, Python 3.13 job `91157545025`, repository-native `scripts/check` | passed | exact five-file fence |
| focused package tests | same run, both jobs | 16 passed | Python 3.9 and 3.13 |
| complete target-declared suite | same run, Python 3.13 | passed | Python 3.9 full-suite predecessor hit unrelated Trio async-generator warning |
| direct source Test Suite | run `30631127167` | passed | current PR head |
| coverage | executor Python 3.13 | 100% | repository coverage gate |
| package build | executor Python 3.13 | passed | target packaging |
| documentation build | executor Python 3.13 | passed | target docs |
| clean diff/tree | executor both jobs | passed | five-file source fence |
| Python 3.9 compatibility | executor job `91157545125` | focused passed | full suite omitted after isolated base/candidate warning classification |
| Python 3.10–3.12 | direct Test Suite `30631127167` | passed through repository matrix | exact job details remain in GitHub Actions |

## Reversing controls

- baseline retry characterization duplicates cleanup; terminal candidate runs it once
- successful concurrent external close callers join one attempt
- ordinary, control-flow, and cancellation owner outcomes preserve original identity
- observer exceptions and causes are distinct and neutral
- GC control releases delegated-frame local objects while response remains reachable
- requestless response path avoids invented request association
- re-entry model times out on current logic and must return promptly on repair

## Soak, leak, and cleanup controls

- iterations: no broad soak retained for this unit
- resources observed: weak-referenceable delegated-frame local; response remains reachable
- cancellation behavior: owner cancellation terminalizes uncertain cleanup and wakes observers
- immediate rerun: direct source Test Suite and executor focused matrix completed at exact head
- missing: repeated target-native re-entry loop, task/event collection after repaired re-entry, Trio re-entry execution

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| predecessor executor run `30624543942` | cancelled after source generation advanced | runner/staleness | no | superseded by exact run |
| earlier Python 3.9 full suite | Trio async-generator `ResourceWarning` in unrelated `test_write_timeout` | repository/dependency | no for focused candidate claims | exact focused Python 3.9 retained; Python 3.13 full gate passed |
| local re-entry Trio attempt | `ModuleNotFoundError: No module named 'trio'` | setup | no | target executor must run repaired test under Trio |
| local repository clone | environment DNS unavailable | setup | no | GitHub source and exact prior CI used; no local target claim added |

## Checks prepared but not executed

- request-bound same-owner re-entry target test — absent from current source
- requestless same-owner re-entry target test — absent from current source
- external waiter plus owner re-entry target test — absent from current source
- delegated stream catches re-entry error and completes — absent
- delegated stream raises a later distinct cleanup error after catching re-entry — absent
- repaired-source Python 3.9/3.13 matrix — awaits source repair

## Platform and integration gaps

- repaired behavior under AnyIO asyncio and Trio
- minimum supported AnyIO version for owner task identity
- arbitrary custom transports beyond deterministic streams
- real HTTPCore post-delegation HTTP/1.1/HTTP/2 interruption
- same-socket reuse and capacity recovery
- multi-transport client shutdown
- production prevalence

## Cleanup receipt

- Temporary workflows removed from canonical source head: `yes`
- Publisher or execution-only files removed: `yes`
- Generated residue checked: `yes`, by exact executor clean-tree gate
- Immediate rerun performed: `yes`, on current source head before re-entry finding
- Remaining temporary branches or PRs: closed executor PR #4 and historical research PRs remain as evidence; none are canonical delivery surfaces

## Current test judgment

`REPAIR`

Reason: the exact candidate has strong focused and full-gate evidence for its tested contract, while the in-flight event lacks owner provenance. Source inspection and an executed model show same-task re-entry waits on an event only the suspended owner can set. Green existing CI cannot cover an absent discriminator.

Clearing condition: advance the clean source branch with cycle-free owner-reentry handling, add target-native request-bound/requestless/external-waiter controls, and pass the complete exact-head matrix plus renewed independent complete-diff review.