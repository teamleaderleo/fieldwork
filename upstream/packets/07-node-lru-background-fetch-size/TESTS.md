# Tests and receipts — unit 07 backgroundFetchSize snapshot

## In simple words

The released-package probe executed the corruption on Node 22, 24, and 26. Earlier candidate heads passed focused behavior and broad repository suites while review repaired callback ordering, complete coverage, cross-platform timer reachability, and exported typing. The current canonical head adds the final hostile, `undefined`, and stale usage-bound controls while keeping the target diff to two files.

Three exact-head gates now control promotion: native CI, native benchmarks, and the existing Fieldwork execution carrier running build, focused tests, OXLint, and Prettier on Node 22/24/26.

## Identity

- Exact upstream base: `16b3a916662ab449d496b7b4b4f04132565d1d28`
- Exact candidate head: `70a9e62b0555e6bb68763fb9d32458fa82fd2a70`
- Exact focused execution carrier head: `a6768dc743d572e422d6e16a21f8b856fc7f2e7c`
- Superseded clean candidate: `0f4a357a9bc0b09ad413e99fa566317bf4ce283c`
- Historical patch carrier head: `bfca6f1d495136640634e24bda197b4c6b4990c1`
- Test date: `2026-07-29` through `2026-08-01`
- Environment and platform: released probe Node 22/24/26 on Ubuntu; native CI Node 24/25 on Ubuntu, macOS, Windows bash, Windows PowerShell; benchmarks Node 22/24/25 on Ubuntu, macOS, Windows; focused carrier Node 22/24/26 on Ubuntu

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| released invalid values corrupt accounting | `target-executed` | Fieldwork run `30491292307` and retained probe | pass: negative controls reproduced on Node 22/24/26 | synthetic values |
| primitive validation avoids hostile conversion | `target-test-prepared` | hostile object in current native test | prepared at `70a9e62b...` | current focused/native runs queued |
| constructor `undefined` defaults while mutated `undefined` rejects when consumed | `target-test-prepared` | separate constructor and mutation controls | prepared at `70a9e62b...` | current focused/native runs queued |
| zero remains coherent | `target-executed` | released probe and native zero-size test | pass on prior executions | current clean head still needs controlling receipt |
| invalid mutation rejects before dispatch | `target-executed` | focused native suite on prior candidate heads | pass; zero provider calls and unchanged state | final invalid matrix expanded on current head |
| callback mutation cannot alter current charge | `target-executed` | focused native suite on prior candidate heads | pass; pending size stays 2, settlement becomes 5 | current exact-head receipt pending |
| invalid field remains irrelevant for stale refresh and no-size cache | `target-test-prepared` | two usage-bound controls | no-size passed earlier; stale invalid-field control new | current exact-head receipt pending |
| internal missing/corrupt receipt is rejected | `target-executed` | direct internal control added after coverage failure | pass on prior head | exact current head pending |
| complete repository suite and coverage | `target-executed` | runs `30580263075`, `30580879839` | behavior passed; coverage findings drove test repair | earlier heads |
| current two-file candidate passes declared gate | `target-test-prepared` | CI `30674843003`, Benchmarks `30674842990` | queued | controlling result pending |
| current changed files pass build, focused, lint, and format | `target-test-prepared` | Fieldwork carrier `30674901995` | queued | controlling result pending |

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

- Exact source head: patch content carried by owned PR #1 and Fieldwork PR #135; final historical carrier head `bfca6f1d495136640634e24bda197b4c6b4990c1`
- Command or workflow: apply patch, `npm run prepare`, `npx tap --disable-coverage test/background-fetch-size.ts`, OXLint, Prettier
- Tests and assertions: constructor families, pre-dispatch mutation, synchronous callback mutation, zero coalescing, stale/no-size behavior, settlement
- Result: 70/70 focused assertions on Node 22, 24, and 26; build/declarations, OXLint, and Prettier passed after title formatting repair
- Failure classification, if red: earlier overlong titles were formatting-only
- Coverage limit: patch carrier and earlier test revision

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

### First clean two-file candidate

- Exact source head: `0f4a357a9bc0b09ad413e99fa566317bf4ce283c`
- Command or workflow: target CI `30674355332`; Benchmarks `30674355680`
- Tests and assertions: complete source/test diff after dependency and lockfile removal
- Result: jobs queued; head superseded before completion after complete historical review exposed missing test controls
- Failure classification, if red: no product failure observed; generation superseded
- Coverage limit: superseded head

### Final adversarial controls

- Exact source head: `70a9e62b0555e6bb68763fb9d32458fa82fd2a70`
- Tests and assertions:
  - labeled invalid values avoid diagnostic coercion;
  - hostile object throws from `Symbol.toPrimitive`, `valueOf`, and `toString` if any conversion occurs;
  - constructor `backgroundFetchSize: undefined` keeps default semantics;
  - post-construction `undefined` rejects before dispatch;
  - invalid public field is ignored for stale refresh because existing entry size is reused.
- Result: prepared; controlling executions queued
- Failure classification, if red: pending
- Coverage limit: pending

### Current native candidate

- Exact source head: `70a9e62b0555e6bb68763fb9d32458fa82fd2a70`
- Command or workflow: target repository CI `30674843003`; Benchmarks `30674842990`
- Tests and assertions: complete target-declared `npm test -- -c -t0` matrix and `npm run benchmark` matrix
- Result: queued at this packet revision
- Failure classification, if red: pending
- Coverage limit: pending

### Current focused build/lint/format carrier

- Exact source head: `70a9e62b0555e6bb68763fb9d32458fa82fd2a70`
- Exact carrier head: `a6768dc743d572e422d6e16a21f8b856fc7f2e7c`
- Command or workflow: Fieldwork `30674901995`
- Tests and assertions: clean checkout, `git diff --check`, `npm install`, `npm run prepare`, `npx tap --disable-coverage test/background-fetch-size.ts`, OXLint, Prettier
- Result: queued on Node 22, 24, and 26
- Failure classification, if red: pending
- Coverage limit: Ubuntu only; native workflows supply cross-platform matrix

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | `npx prettier --check src/index.ts test/background-fetch-size.ts` | queued | carrier `30674901995` |
| lint | `npx oxlint src/index.ts test/background-fetch-size.ts` | queued | carrier `30674901995` |
| typecheck or compile | `npm run prepare` | queued | carrier plus native pretest |
| focused package tests | `npx tap --disable-coverage test/background-fetch-size.ts` | queued on Node 22/24/26 | historical revisions passed; final content expanded |
| complete target-declared suite | `npm test -- -c -t0` | queued | native CI `30674843003` |
| build or generated output | `npm run prepare` | queued | generated output stays uncommitted |
| platform matrix | CI Node 24/25 on four OS/shell variants | queued | run `30674843003` |
| benchmarks | `npm run benchmark` Node 22/24/25 on three platforms | queued | run `30674842990`; earlier `30580263012` passed |

## Reversing controls

- baseline invalid values reach accounting; candidate constructor rejects them
- hostile object conversion hooks remain unreachable
- constructor `undefined` defaults while mutated `undefined` rejects at consumption
- zero-size coalescing passes on baseline and candidate
- synchronous callback mutation leaves the current provisional charge unchanged on candidate
- corrupted internal receipt is rejected at the accounting boundary
- invalid field remains irrelevant for stale refresh and no-size caches

## Soak, leak, and cleanup controls

- iterations: ordinary suite-defined repetitions only
- resources observed: cache entries, size arrays, provider call counts, promise settlement, autopurge timers
- timers/tasks/processes/files/listeners before and after: autopurge control clears the cache; no new production timer or task
- cancellation or interruption behavior: existing replacement and eviction controls remain in the focused file
- immediate rerun result: final clean head triggered all three controlling workflows

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| `60beee938bb25b8aa765563ae2e9e0a22ab3692c` | complete coverage missed defensive `__size` branch | harness coverage | no | add internal receipt control |
| first internal receipt control | public `fetch()` result was the wrapper, not stored internal promise | test model | no | use `unsafeExposeInternals()` |
| `30580263075` | macOS/Windows missed existing autopurge reschedule line | coverage timing | no | add direct branch control |
| first autopurge repair | `updateAgeOnGet` replaced the original timer, making intended branch unreachable | test model | no | adjust exposed start receipt without replacing timer |
| head with inherited `t.clock` | Windows attempted unavailable `@tapjs/clock` plugin | dependency/setup | no | use injected `perf.now` and real timer |
| `fef8328c9431b656c0ee48547250e37d6caeabef` | workflows ended `action_required` before jobs | runner/approval | no | publish clean head, trigger new runs |
| `0f4a357a9bc0b09ad413e99fa566317bf4ce283c` | complete prior-art review found three missing native controls | test completeness | no source defect | add controls and supersede head |

## Checks prepared but not executed

- native CI `30674843003`
- native Benchmarks `30674842990`
- focused build/OXLint/Prettier carrier `30674901995`

## Platform and integration gaps

- production prevalence and configuration sources remain unmeasured
- no browser-specific integration path; project CI covers supported Node environments
- benchmark output is treated as a regression gate, without a performance claim

## Cleanup receipt

- Temporary workflows removed from canonical source head: `yes`
- Publisher or execution-only files removed from canonical source head: `yes`
- Generated residue checked: `yes`; changed-file fence is exactly two files
- Immediate rerun performed: `yes`; native and carrier workflows triggered on final head
- Remaining temporary branches or PRs: Fieldwork PR #135 execution workflow remains until current receipt transfer; historical owned PR #1 remains as a superseded evidence carrier

## Current test judgment

`EXECUTE`

Reason: the product design and main native controls passed substantial earlier execution, and the canonical branch is clean. The final test generation adds material adversarial and usage-bound controls, so exact-head native CI, benchmarks, and focused lint/format remain controlling.

Clearing condition: runs `30674843003`, `30674842990`, and `30674901995` pass at source head `70a9e62b0555e6bb68763fb9d32458fa82fd2a70`, followed by fresh complete-diff review.
