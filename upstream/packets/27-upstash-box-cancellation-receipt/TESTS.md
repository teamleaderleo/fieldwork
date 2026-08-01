# Tests and receipts — Unit 27 cancellation-request receipt

## In simple words

The retained candidate passed focused and complete TypeScript and Python gates at exact historical source. The artifact is complete and its hash matches. A later exact-source review found one missing complete-path test: the real TypeScript stream iterator still converts cancellation-request observer abort into terminal `cancelled`. Current disposition remains `REPAIR`.

## Identity

- Executed upstream base: `b55d832d6e3ae0156e32d21ea3863e231dfff9cd`
- Current upstream inspected: `9f7533c645f6b519f612aa977f6f4acf86655db7`
- Target-executed carrier head: `1e7909da440ab631fcea11d4d3777d2bce107277`
- Workflow-free carrier head: `ccaa28e40c5689aec7ad78c7f18c354e9966d7fd`
- Historical test date: `2026-07-31`
- Packet verification date: `2026-08-01`
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
| Complete TS stream lifecycle preserves authoritative status | `target-test-prepared` | review `4830012327` required test | pending | source repair absent |
| Current source continuity | `source-read` | compare `b55d832...9f7533c...` | relevant paths unchanged | no current-head rerun |
| Retained artifact integrity | `model-executed` | local SHA/JSON/path/stat checks | pass | patch receipt only |

## Baseline characterization

- Workflow `30622339900`: exact target characterization.
- Workflow `30623393254`: composed wording/control refinement.
- Result: request failure suppressed, local `cancelled` published, concurrent callers issue separate requests, TypeScript observer abort precedes settlement, and a later internal update can replace local status.
- Limit: hosted continuation, remote termination, and cost remain unknown.

## Candidate-focused tests

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

Coverage limit: the real agent stream body-reader catch path did not run.

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

## Ordinary repository gates

| Gate | Result | Notes |
| --- | --- | --- |
| TypeScript format | pass | package Prettier check |
| TypeScript focused | 21/21 | includes retained execution control |
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

## Reversing controls

Executed:

- baseline failure assigns `cancelled`; candidate isolated method leaves status unchanged;
- baseline concurrent calls duplicate requests; candidate callers within one object share one;
- legacy returns pass;
- provider detail is injected and absent from receipt output.

Required:

- real `box.agent.stream()` pending read;
- cancellation-request abort before receipt settlement yields local detachment, not remote cancellation;
- same after settlement with a newly attached observer;
- timeout abort remains separately classified;
- two wrappers with the same run ID prove per-object scope.

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Action |
| --- | --- | --- | --- | --- |
| artifact `8797603134` | untracked new files absent from plain `git diff` | runner/evidence packaging | replayability only | repaired with intent-to-add and exact inventory |
| early current-head receipt | live test moved beyond tested head | evidence currentness | yes | rerun as `30642924979` |
| packet-session clone | container DNS blocked public Git clone | setup/network | no historical claim | artifact verified locally; no current execution claimed |

## Checks prepared but not executed

- real TypeScript stream-path reversing test;
- timeout-origin compatibility test;
- same-ID/two-wrapper boundary test;
- current-head full target rerun;
- hosted integration.

## Packet-session verification

```text
sha256sum upstash-box-cancel-receipt.patch
python -c 'import json; json.load(open("upstash-box-cancel-receipt.json"))'
git apply --stat upstash-box-cancel-receipt.patch
grep '^diff --git ' upstash-box-cancel-receipt.patch
```

Result:

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

Reason: historical execution is strong and the patch is complete, yet TypeScript cancellation-request observer abort still reaches timeout handling and can publish terminal `cancelled`.

Clearing condition: repair abort-origin ownership, add the real stream-path and two-wrapper controls, run focused and complete current target gates, and retain a new exact patch/receipt.
