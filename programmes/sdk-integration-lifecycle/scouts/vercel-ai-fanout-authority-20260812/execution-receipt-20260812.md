# Execution receipt — aggregate fanout failure authority

Issue: #868  
Durable report: `report.md`  
Exact public Vercel AI base: [`59d6defd09f1855ccd95687dcccb1dd0122815d8`](https://redirect.github.com/vercel/ai/commit/59d6defd09f1855ccd95687dcccb1dd0122815d8)  
Target characterization: `teamleaderleo/ai#117`  
Characterization head: `7d045b26946a1f56e9e3ffb9c802581ab80f8b8f`  
Execution carrier: `teamleaderleo/ai#118`  
Carrier head: `530467dbac8354b207de8eb670676ab8f362aaed`  
Run: `31557162595`  
Job: `93991826927`  
Runner: Ubuntu 24.04 / Node 22  
Evidence class: `target-executed`

## Gates

The dedicated target-native workflow completed successfully and reached every requested gate:

1. frozen-lockfile workspace install — passed;
2. formatting for both focused characterization files — passed;
3. `ai` package type-check — passed;
4. `ai` package build — passed;
5. both focused Fieldwork fanout controls — passed;
6. existing `generate-image` and `generate-video` Node suites — passed.

## Executed image result

The focused image control uses one public `generateImage()` call with `n = 2` and `maxImagesPerCall = 1`.

Both child model calls start. Child A is then released to reject with the selected aggregate error while child B remains deliberately pending. The public `generateImage()` promise rejects from child A while child B is still unfinished. After aggregate rejection, the test releases child B and observes that child B completes successfully.

Executed conclusion:

> A sibling image-generation child retains local execution authority after another child has already made the aggregate public operation reject.

The test does not claim that this policy is wrong.

## Executed video result

The focused video control uses one public `experimental_generateVideo()` call with `n = 2`, `maxVideosPerCall = 1`, and the start/status flow.

Two distinct remote-operation identities are acknowledged and both status flows begin. Child A then returns a terminal provider error while child B remains deliberately pending. The public aggregate promise rejects from child A while child B is still unfinished. After aggregate rejection, the test releases child B and observes that its status flow reaches completion.

Executed conclusion:

> A sibling asynchronous video child retains local status/polling authority after another child has already made the aggregate public operation reject.

The model is mocked; no live remote job or provider charge is claimed.

## What this proves

The source-level fanout question is now target-executed for both current core paths:

- image multi-call generation;
- asynchronous video start/status generation.

Current semantics are fail-fast at the public aggregate promise while already-started siblings may continue their own local work afterward unless the caller's abort signal independently retires them.

## What this does not prove

- It does not prove that sibling continuation is an SDK defect.
- It does not prove a real remote provider accepts or bills late sibling work in every adapter.
- It does not imply that best-effort local abort can cancel a remote task already accepted by a provider.
- It does not establish that all-settled behavior would be preferable.
- It does not establish a partial-result API requirement.

The remaining research question is normative: which aggregate failure policy best matches the public API and provider constraints?

## Next comparison

Compare only three serious directions:

1. current fail-fast + independent sibling lifetime;
2. fail-fast + best-effort local sibling retirement;
3. all-settled aggregate failure.

Keep partial-result API redesign as a losing/high-cost alternative unless real use cases require it.

No third-party upstream interaction occurred.
