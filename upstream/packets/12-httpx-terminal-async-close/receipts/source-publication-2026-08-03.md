# Source publication receipt — Unit 12

Date: `2026-08-03`  
Disposition: `READY`

## Published source

- repository: `teamleaderleo/httpx`
- branch: `fieldwork/171-terminal-close-source`
- exact head: `d5f9e3dffce3342d8c02ec2c1d3ed9588a83b803`
- base: `b5addb64f0161ff6bfe94c124ef76f6a1fba5254`
- source PR: `teamleaderleo/httpx#6`
- changed files: exactly six

## Identity verification

- `httpx/_models.py`: `0533a7324d0ed45ffb1087570551efcdaed02fa5`
- `httpx/_client.py`: `510b41959383dcf78bd311a236afc44dd92d010a`
- elapsed test: `67545aede0ba92364f70dc9f37c5c2e0a010c836`
- re-entry test: `0be56b2cb9a9a2e7fabc1a6bc107bbcca520fd67`

All four blobs match the independently reviewed patch executed by run `30752805069`.

## Execution evidence

- Python 3.9 focused asyncio/Trio: passed;
- Python 3.13 focused asyncio/Trio: passed;
- Python 3.13 full gates: passed;
- complete suite: `1445 passed, 1 skipped`;
- coverage: `8210/8210`, 100%.

## Workflow classification

The automatic source-head Test Suite event `30755566581` concluded `action_required` before creating jobs. It produced no product-test result and is classified as workflow admission. The exact full-gate receipt remains run `30752805069`.

## Cleanup

Execution PR #9 is closed without merge. The canonical source fence contains no temporary workflow or Fieldwork-only file. No public upstream interaction occurred.
