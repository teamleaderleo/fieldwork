# Tests and receipts — unit 07 backgroundFetchSize snapshot

## In simple words

The released-package probe executed the corruption on Node 22, 24, and 26. Earlier candidate heads then passed the focused behavior and broad repository suite while test repairs chased complete cross-platform coverage. The current canonical source head removes all dependency and lockfile churn. Its ordinary CI and benchmark workflows are the controlling receipts.

## Identity

- Exact upstream base: `16b3a916662ab449d496b7b4b4f04132565d1d28`
- Exact candidate head: `0f4a357a9bc0b09ad413e99fa566317bf4ce283c`
- Exact execution carrier head, if any: candidate head itself; historical Fieldwork carrier `bfca6f1d495136640634e24bda197b4c6b4990c1`
- Test date: `2026-07-29` through `2026-08-01`
- Environment and platform: released probe Node 22/24/26 on Ubuntu; native CI Node 24/25 on Ubuntu, macOS, Windows bash, Windows PowerShell; benchmarks Node 22/24/25 on Ubuntu, macOS, Windows

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| released invalid values corrupt accounting | `target-executed` | Fieldwork run `30491292307` and retained probe | pass: negative controls reproduced on Node 22/24/26 | synthetic values |
| zero remains coherent | `target-executed` | released probe and native zero-size test | pass on prior executions | current clean head still needs controlling receipt |
| invalid mutation rejects before dispatch | `target-executed` | focused native suite on prior candidate heads | pass; zero provider calls and unchanged state | earlier heads |
| callback mutation cannot alter current charge | `target-executed` | focused native suite on prior candidate heads | pass; pending size stays 2, settlement becomes 5 | earlier heads |
| internal missing/corrupt receipt is rejected | `target-executed` | direct internal control added after coverage failure | pass on prior head | exact current head pending |
| complete repository suite and coverage | `target-executed` | runs `30580263075`, `30580879839` | behavior passed; coverage findings drove test repair | earlier heads |
| current two-file candidate passes declared gate | `target-test-prepared` | CI `30674355332`, Benchmarks `30674355680` | queued at packet creation | controlling result pending |

## Baseline characterization

### Command or workflow

```text
cd programmes/data-durable-workflows/scouts/lru-cache-background-fetch-size/probe
npm install --ignore-scripts
npm run probe
```

### Assertions

- valid one preserves one provisional unit and one same-key provider call
- negative and fractional values enter live accounting
- `NaN` remains in calculated size after insertion and settlement
- infinity prevents provisional caching and causes two provider calls
- runtime string `'2'` creates string arithmetic, negative public count, entry loss, and `Invalid array length` rejections
- zero remains cached and coalesced

### Result

- status: `passed`
- test count: assertion-driven probe across seven value families
- workflow and job: Fieldwork `30491292307`, Node 22, 24, and 26
- artifact or receipt: PR #135 probe and report
- observed behavior: all negative and compatibility controls matched the retained assertions

## Candidate-focused tests

### Historical patch-carrier matrix

- Exact source head: patch content carried by owned PR #1 and Fieldwork PR #135; final carrier head `bfca6f1d495136640634e24bda197b4c6b4990c1`
- Command or workflow: apply patch, `npm run prepare`, `npx tap --disable-coverage test/background-fetch-size.ts`, OXLint, Prettier
- Tests and assertions: constructor families, pre-dispatch mutation, synchronous callback mutation, zero coalescing, stale/no-size behavior, settlement
- Result: 70/70 focused assertions on Node 22, 24, and 26; build/declarations, OXLint, and Prettier passed after title formatting repair
- Failure classification, if red: earlier overlong titles were formatting-only
- Coverage limit: patch carrier, earlier test revision, focused test with repository coverage disabled

### Direct-head internal receipt control

- Exact source head: `96ecc21a5860f40e79a584fdc887354736c4bbd8`
- Command or workflow: native repository CI and Benchmarks
- Tests and assertions: obtain the stored internal promise through `unsafeExposeInternals`, corrupt only `__size`, verify reinsertion rejects while original accounting and settlement remain coherent
- Result: behavior passed; a new complete-coverage run followed
- Failure classification, if red: first attempt used the public async wrapper instead of the internal promise; test-model error repaired
- Coverage limit: earlier head

### Cross-platform coverage sequence

- Exact source heads: `ee9dd98552d894e2c730a66b30507ecbc411b213`, `cc11ee69b25e0b10f0dc50b2cd66d6fd3aaeef18`, `f9dcd66cda9fffbe9612e6053634853dfde30e25`
- Command or workflow: repository `CI` and `Benchmarks`
- Tests and assertions: focused file, full suite, complete coverage, autopurge reschedule branch
- Result: run `30580263075` reported 80 focused assertions and 29 suites / 19,591 assertions; Ubuntu complete coverage; macOS/Windows behavior passed with one uncovered existing autopurge line. Run `30580879839` reported 83 focused assertions and 29 suites / 19,546 assertions; behavior passed while the attempted clock control still missed the intended branch. Later repair used the actual stored timer and bounded condition polling.
- Failure classification, if red: coverage/test timing and branch reachability, separate from product behavior
- Coverage limit: earlier heads

### Current clean candidate

- Exact source head: `0f4a357a9bc0b09ad413e99fa566317bf4ce283c`
- Command or workflow: target repository CI `30674355332`; Benchmarks `30674355680`
- Tests and assertions: complete target-declared `npm test -- -c -t0` matrix and `npm run benchmark` matrix
- Result: queued at packet creation
- Failure classification, if red: pending
- Coverage limit: pending

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | Prettier through historical carrier and repository test lifecycle | passed on prior final test content | current CI controls final status |
| lint | OXLint through historical carrier; repository lifecycle | passed on prior source/test content | no standalone current run |
| typecheck or compile | `npm run prepare` | passed on historical carrier | current `npm test` runs pretest/prepare |
| focused package tests | `npx tap --disable-coverage test/background-fetch-size.ts` | 70/70 on Node 22/24/26 historical carrier; 80/83 counts on later native revisions | exact current file participates in full CI |
| complete target-declared suite | `npm test -- -c -t0` | behavior passed on earlier direct heads | current CI `30674355332` queued |
| build or generated output | `npm run prepare` | passed historically | generated output stays uncommitted |
| platform matrix | CI Node 24/25 on four OS/shell variants | queued | run `30674355332` |
| benchmarks | `npm run benchmark` Node 22/24/25 on three platforms | queued | run `30674355680`; earlier `30580263012` passed |

## Reversing controls

- baseline invalid values reach accounting; candidate constructor rejects them
- zero-size coalescing passes on baseline and candidate
- synchronous callback mutation leaves the current provisional charge unchanged on candidate
- corrupted internal receipt is rejected at the accounting boundary
- stale refresh and no-size caches preserve unrelated behavior

## Soak, leak, and cleanup controls

- iterations: ordinary suite-defined repetitions only
- resources observed: cache entries, size arrays, provider call counts, promise settlement, autopurge timers
- timers/tasks/processes/files/listeners before and after: autopurge control clears the cache; no new production timer or task
- cancellation or interruption behavior: existing replacement and eviction controls remain in the focused file
- immediate rerun result: prior matrices reran after each test repair; current exact-head result pending

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| `60beee938bb25b8aa765563ae2e9e0a22ab3692c` | complete coverage missed defensive `__size` branch | harness coverage | no | add internal receipt control |
| first internal receipt control | public `fetch()` result was the wrapper, not stored internal promise | test model | no | use `unsafeExposeInternals()` |
| `30580263075` | macOS/Windows missed existing autopurge reschedule line | coverage timing | no | add direct branch control |
| first autopurge repair | `updateAgeOnGet` replaced the original timer, making intended branch unreachable | test model | no | adjust exposed start receipt without replacing timer |
| head with inherited `t.clock` | Windows attempted unavailable `@tapjs/clock` plugin | dependency/setup | no | use injected `perf.now` and real timer |
| `fef8328c9431b656c0ee48547250e37d6caeabef` | workflows ended `action_required` before jobs | runner/approval | no | publish clean head, trigger new runs |

## Checks prepared but not executed

- none beyond the current target CI and benchmark workflows already queued

## Platform and integration gaps

- production prevalence and configuration sources remain unmeasured
- no browser-specific integration path; project CI covers supported Node environments
- benchmark output is treated as a regression gate, without a performance claim

## Cleanup receipt

- Temporary workflows removed from canonical source head: `yes`
- Publisher or execution-only files removed: `yes`
- Generated residue checked: `yes`; changed-file fence is exactly two files
- Immediate rerun performed: `yes`; CI and Benchmarks triggered on clean head
- Remaining temporary branches or PRs: historical PR #1 and Fieldwork PR #135 remain as evidence carriers; closure can follow receipt transfer and independent review

## Current test judgment

`EXECUTE`

Reason: the product design and native controls have passed substantial earlier execution, and the canonical branch is now clean. Exact-head CI and benchmarks are the controlling gate because every earlier green receipt belongs to another revision.

Clearing condition: both target workflows pass at `0f4a357a9bc0b09ad413e99fa566317bf4ce283c`, followed by fresh complete-diff review.
