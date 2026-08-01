# Tests and receipts — Unit 27 cancellation-request receipt

## In simple words

The retained candidate passed focused and complete TypeScript and Python gates at exact historical source. The artifact is complete and its hash matches. Deeper review now defines the missing complete-path matrix precisely: real pending agent-stream reads, cancellation-specific rejection with `detached`, timeout preservation, both race orders, later controller replacement, same-ID wrapper scope, and explicit command/code stream boundaries.

No new target execution ran during this context pass. Current disposition remains `REPAIR`.

## Identity

- Executed upstream base: `b55d832d6e3ae0156e32d21ea3863e231dfff9cd`
- Current upstream inspected: `9f7533c645f6b519f612aa977f6f4acf86655db7`
- Open CLI compatibility head inspected: `fce8c8cfc269bc09d07eb991ee39d0433029027e`
- Target-executed carrier head: `1e7909da440ab631fcea11d4d3777d2bce107277`
- Workflow-free carrier head: `ccaa28e40c5689aec7ad78c7f18c354e9966d7fd`
- Historical test date: `2026-07-31`
- Context/repair-plan date: `2026-08-01`
- Environment: Ubuntu 24.04.4; Node 22.23.1; pnpm 10.34.5; Python 3.12.13
- Network: local mocked requests; no hosted provider call or credential

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| Baseline publishes unconfirmed `cancelled` and duplicates requests | `target-executed` | Fieldwork #329, PRs #332/#337 | characterized | mocked target paths |
| Receipt APIs share one operation per run object | `target-executed` | focused TS/Python controls in run `30642924979` | pass | one object/process |
| Legacy return types preserved | `target-executed` | focused and native tests | pass | target base `b55d832...` |
| Async waiter cancellation is isolated | `target-executed` | retained Python control | pass | Python async only |
| Generated sync output is deterministic | `target-executed` | generate twice and `cmp` | pass | one Python/runtime |
| Complete TS agent-stream lifecycle preserves authoritative status | `target-test-prepared` | exact matrix below | pending | source repair absent |
| Cancellation keeps CLI catch control flow | `source-read` | Box PR #82 head `fce8c8c...` | supported | open PR, not accepted contract |
| Command/code stream local abort matches agent stream | `source-read` | current constructors | false at inspected source | no controller attached |
| Current source continuity | `source-read` | compare `b55d832...9f7533c...` | relevant paths unchanged | no current-head rerun |
| Retained artifact integrity | `model-executed` | local SHA/JSON/path/stat checks | pass | patch receipt only |

## Historical baseline characterization

- Workflow `30622339900`: exact target characterization.
- Workflow `30623393254`: composed wording/control refinement.
- Result: request failure suppressed, local `cancelled` published, concurrent callers issue separate requests, TypeScript attached observer abort precedes settlement, and a later internal update can replace local status.
- Limit: hosted continuation, remote termination, and cost remain unknown.

## Historical candidate-focused tests

### TypeScript focused controls

```text
pnpm --filter @upstash/box exec prettier --write \
  src/client.ts \
  src/types.ts \
  src/index.ts \
  src/__tests__/run.test.ts \
  src/__tests__/fieldwork-cancel-receipt-repair.test.ts

pnpm --filter @upstash/box exec vitest run \
  src/__tests__/run.test.ts \
  src/__tests__/fieldwork-cancel-receipt-repair.test.ts
```

Result: 2 files and 21 tests passed.

Covered accepted/failure receipts, frozen values, shared Promise identity, later-call no replay, legacy void return, direct status preservation, authoritative updates, and observer abort on an isolated `Run`.

Coverage limit: the real agent-stream body-reader catch path did not run.

### TypeScript complete package gates

```text
pnpm --filter @upstash/box test
pnpm --filter @upstash/box build
pnpm --filter @upstash/box ci:lint
```

Result: 29 files, 385 tests, TypeScript compile, and Prettier check passed.

### Python deterministic generation

```text
python box/packages/python-sdk/scripts/generate_sync.py
git -C box diff -- packages/python-sdk/upstash_box/_sync > /tmp/fieldwork-sync-first.diff
python box/packages/python-sdk/scripts/generate_sync.py
git -C box diff -- packages/python-sdk/upstash_box/_sync > /tmp/fieldwork-sync-second.diff
cmp /tmp/fieldwork-sync-first.diff /tmp/fieldwork-sync-second.diff
test -s /tmp/fieldwork-sync-first.diff
```

Result: byte-identical, non-empty generated sync diff.

### Python focused controls

```text
pytest -q \
  tests/_async/test_run.py \
  tests/test_cancel_receipt_repair.py
```

Result: 7 passed.

Assertions include one async request and receipt across callers, cancelled-waiter survival, one sync request across threads, fixed failure prose, frozen receipt, legacy `None`, no replay, and later authoritative status.

### Python complete package gates

```text
pytest -q
python scripts/check_parity.py
ruff check \
  upstash_box \
  tests/_async/test_run.py \
  tests/_sync/test_sync_client.py \
  tests/test_cancel_receipt_repair.py \
  scripts/generate_sync.py
ruff format --check \
  upstash_box \
  tests/_async/test_run.py \
  tests/_sync/test_sync_client.py \
  tests/test_cancel_receipt_repair.py \
  scripts/generate_sync.py
mypy \
  upstash_box/_async/client.py \
  upstash_box/_sync/client.py \
  upstash_box/_cancellation.py \
  upstash_box/types.py
```

Result: 185 passed, 12 deselected; parity, Ruff, and MyPy passed.

## Prepared TypeScript repair controls

### Test fixture

Add one target-native helper or inline `Response` whose `ReadableStream`:

- emits a `run_start` event and optional partial text;
- leaves the next `reader.read()` pending;
- exposes a test handle that can close or error the stream;
- is returned by the real mocked `fetch`, so the production `box.agent.stream()` iterator and abort signal execute.

Do not test by directly assigning an arbitrary controller to an isolated `Run` for the decisive lifecycle claim.

### 1. Cancellation before receipt settlement

Setup:

- create `box.agent.stream()` with the pending body response;
- start consuming the iterator until it reaches the pending read;
- make the cancel POST return a deferred response;
- call `run.requestCancel()`.

Required observations before settling the POST:

- the real stream fetch/body read aborts;
- iterator rejects with cancellation-request-specific prose, not `Stream timed out`;
- `run.status === "detached"`;
- partial output is retained;
- receipt Promise remains pending if the POST remains pending;
- exactly one cancellation POST has started.

After settling the POST:

- receipt is frozen and reports the selected request state plus remote outcome `unknown`;
- status remains `detached` until an authoritative update.

### 2. Timeout-only control

Use fake timers or a short deterministic timeout with a pending body read.

Required observations:

- timeout owner records first;
- iterator rejects with existing `Stream timed out` prose;
- current timeout status behavior remains unchanged for this bounded repair;
- no cancellation POST occurs.

This control prevents the fix from turning every abort into local detachment.

### 3. Cancellation-first race

- schedule cancellation first and timeout second against one pending stream;
- verify the first owner remains `cancel-request` after the timer fires;
- iterator uses cancellation-specific rejection and `detached`;
- one shared POST executes.

### 4. Timeout-first race

- fire timeout before calling `requestCancel()`;
- verify timeout classification remains stable;
- later cancellation call still sends/joins the cancellation POST receipt;
- it cannot relabel the already-aborted stream as cancellation-request shutdown.

### 5. Later controller after receipt settlement

- settle one cancellation receipt;
- attach a fresh controller through the internal test boundary;
- call legacy `cancel()` again;
- fresh controller aborts with cancellation-request ownership;
- cancellation POST count does not increase;
- legacy return remains `undefined`.

### 6. Same remote ID, two wrappers

- construct two `Run` objects with the same box and run ID;
- call `requestCancel()` concurrently on both;
- observe two POSTs and two independent receipt identities;
- document single-flight as per in-memory object, not per remote run.

### 7. Later authoritative status

After cancellation-request detachment, apply authoritative internal updates for both `completed` and `cancelled` cases. Each must replace `detached` and retain its server-derived result.

### 8. Stream-type boundary

Add source-level or target-native controls showing:

- agent stream receives local abort through its attached controller;
- command/code stream currently do not receive equivalent local abort from `Run.cancel()`.

Choose one of two honest outcomes before upstream submission:

1. narrow documentation and tests to agent-stream local shutdown; or
2. deliberately add controllers to command/code streams and execute the same ownership matrix there.

The second outcome is wider and should be selected only with a target consistency decision.

### 9. CLI compatibility control

At minimum, model the open PR #82 flow:

- caller records cancellation intent;
- `run.cancel()` is invoked;
- iterator rejects;
- caller can distinguish cancellation from ordinary error;
- no ordinary completion event is emitted.

This can be a small SDK-level control; the open CLI branch itself need not be modified in this unit.

## Ordinary repository gates after repair

Run at one exact current target head:

```text
pnpm install --frozen-lockfile
pnpm --filter @upstash/box exec vitest run \
  src/__tests__/run.test.ts \
  src/__tests__/box-agent-run.test.ts \
  <renamed receipt test>
pnpm --filter @upstash/box test
pnpm --filter @upstash/box build
pnpm --filter @upstash/box ci:lint

python packages/python-sdk/scripts/generate_sync.py
# repeat generation and compare outputs
pytest -q packages/python-sdk/tests/_async/test_run.py \
  packages/python-sdk/tests/_sync/test_sync_client.py \
  <renamed receipt test>
pytest -q packages/python-sdk/tests
python packages/python-sdk/scripts/check_parity.py
ruff check <changed Python paths>
ruff format --check <changed Python paths>
mypy <changed Python source paths>
```

Record exact package-manager bootstrap commands from current repository instructions rather than assuming the historical environment is still sufficient.

## Historical ordinary-gate receipt

| Gate | Result | Notes |
| --- | --- | --- |
| TypeScript format | pass | package Prettier check |
| TypeScript focused | 21/21 | includes retained isolated execution control |
| TypeScript complete | 385/385 | 29 files |
| TypeScript compile | pass | `tsc` |
| Python generation | pass | non-empty identical diff |
| Python focused | 7/7 | async/native plus retained control |
| Python complete | 185 passed, 12 deselected | integration excluded by environment |
| Python parity | pass | public symbols |
| Python lint/format | pass | selected source/tests |
| Python typecheck | pass | four source files |
| Hosted integration | not run | authority and credentials absent |
| Platform matrix | not run for candidate | one Ubuntu runner |

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Action |
| --- | --- | --- | --- | --- |
| artifact `8797603134` | untracked new files absent from plain `git diff` | runner/evidence packaging | replayability only | repaired with intent-to-add and exact inventory |
| early current-head receipt | live test moved beyond tested head | evidence currentness | yes | rerun as `30642924979` |
| packet-session clone | container DNS blocked public Git clone | setup/network | no historical claim | source and related repositories read through GitHub; no new execution claimed |

## Checks prepared but not executed

- first-owner `WeakMap` source repair;
- real agent-stream pending-read controls;
- timeout and both race-order controls;
- same-ID/two-wrapper boundary test;
- stream-type boundary control;
- CLI compatibility control;
- current-head full target rerun;
- hosted integration.

## Packet-session verification

```text
sha256sum upstash-box-cancel-receipt.patch
python -c 'import json; json.load(open("upstash-box-cancel-receipt.json"))'
git apply --stat upstash-box-cancel-receipt.patch
grep '^diff --git ' upstash-box-cancel-receipt.patch
```

Historical retained result:

- patch SHA-256 matches receipt: `d30874c96f8e39350b9d725c58a6034554c561b073cb04969849ff2778c09e88`;
- JSON parsed;
- 15 paths and 15 unique paths;
- 471 additions, 27 deletions.

## Cleanup receipt

- Temporary workflow removed from workflow-free carrier: `yes`
- Clean target-source branch: `unavailable — owned fork admission required`
- Generated residue checked: `yes` in historical execution
- Immediate rerun performed: `yes` historically
- Remaining carrier: PR #389 remains the canonical research record

## Current test judgment

`REPAIR`

Reason: historical execution is strong and the retained patch is complete, but the first-owner source repair and real stream-path controls remain unmaterialized and unexecuted.

Clearing condition: implement the weak controller-owner repair, settle receipt naming, add the real agent-stream/race/wrapper/boundary controls, run focused and complete current target gates, and retain a new exact patch/receipt.
