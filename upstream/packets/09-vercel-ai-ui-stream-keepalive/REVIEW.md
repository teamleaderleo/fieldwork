# Review — Unit 09 UI-stream SSE keep-alive

## In simple words

The owned candidate is technically credible, fully green in its fork, and supported by a real Node and controlled proxy execution receipt. An active public issue and pull request now cover the same contribution. The correct transition is to retire duplicate submission work while preserving the owned candidate as independent validation and lifecycle review input.

A final reviewer should challenge the two exact differences between the owned and public implementations: validation ordering before persistence side effects, and client cancellation while an independent persistence tee branch remains active.

## Review subject

- Work class: `upstream-fork research; superseded validation candidate`
- Target repository: `vercel/ai`
- Public upstream inspected: `main` at `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0`
- Canonical source branch: `teamleaderleo/ai:fieldwork/ui-message-stream-keepalive`
- Exact source head: `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`
- Historical base: `2b872b0db3769decf69945830c66a897c1e37347`
- Public replacement: `vercel/ai#17921` at `21cd681724103701c3596770d7252a7ef0ad18db`
- Fieldwork packet branch: `p0/435-unit-09-vercel-ai-ui-stream-keepalive`
- Exact packet head: latest unit-09 handoff on `teamleaderleo/fieldwork#435`
- Upstream-contact authority: `none`

## Complete changed-file fence

| Path | Role | Keep in historical candidate? |
| --- | --- | --- |
| `.changeset/ui-stream-keep-alive.md` | patch changeset | yes |
| `content/docs/07-reference/02-ai-sdk-ui/41-create-ui-message-stream-response.mdx` | public option documentation | yes |
| `packages/ai/src/ui-message-stream/create-sse-keep-alive-stream.ts` | production liveness pump | yes |
| `packages/ai/src/ui-message-stream/create-ui-message-stream-response.ts` | Fetch response integration | yes |
| `packages/ai/src/ui-message-stream/pipe-ui-message-stream-to-response.ts` | Node response integration | yes |
| `packages/ai/src/ui-message-stream/ui-message-stream-response-init.ts` | public option type | yes |
| `packages/ai/src/agent/create-agent-ui-stream-response.ts` | option propagation | yes |
| `packages/ai/src/agent/pipe-agent-ui-stream-to-response.ts` | option propagation | yes |
| `packages/ai/src/ui-message-stream/create-ui-message-stream-response-keep-alive.test.ts` | lifecycle, persistence, cancellation, soak | yes |
| `packages/ai/src/ui-message-stream/pipe-ui-message-stream-to-response-keep-alive.test.ts` | Node output and validation ordering | yes |
| `packages/ai/src/generate-text/stream-text-ui-response-keep-alive.test.ts` | streamText propagation | yes |
| `packages/ai/src/agent/create-agent-ui-stream-response-keep-alive.test.ts` | agent Fetch propagation | yes |
| `packages/ai/src/agent/pipe-agent-ui-stream-to-response-keep-alive.test.ts` | agent Node propagation | yes |

No workflow, publisher, receipt, lockfile, unrelated formatting, or dependency file remains in this fence.

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. [owned complete diff](https://github.com/teamleaderleo/ai/pull/4/files)
6. [owned core implementation](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-sse-keep-alive-stream.ts)
7. [owned lifecycle test](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-ui-message-stream-response-keep-alive.test.ts)
8. [public replacement diff](https://github.com/vercel/ai/pull/17921/files)
9. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
10. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact diff links

- owned complete compare: [`2b872b0...b4b5726`](https://github.com/teamleaderleo/ai/compare/2b872b0db3769decf69945830c66a897c1e37347...b4b572631f6f288f296d1dcbb6d69e5e848cd9fb)
- owned core production file: [`create-sse-keep-alive-stream.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-sse-keep-alive-stream.ts)
- owned core test: [`create-ui-message-stream-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-ui-message-stream-response-keep-alive.test.ts)
- public replacement implementation: [`create-keep-alive-sse-stream.ts`](https://github.com/vercel/ai/blob/21cd681724103701c3596770d7252a7ef0ad18db/packages/ai/src/ui-message-stream/create-keep-alive-sse-stream.ts)
- public replacement parser test: [`create-ui-message-stream-response.test.ts`](https://github.com/vercel/ai/blob/21cd681724103701c3596770d7252a7ef0ad18db/packages/ai/src/ui-message-stream/create-ui-message-stream-response.test.ts)

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| duplicate submission should stop | public issue `#17805` and PR `#17921` | Is any proposed Fieldwork submission distinct enough to justify parallel review? Current answer: no. |
| comments belong after persistence tee | owned and public source, persistence byte tests | Could any supported persistence consumer require client comments? Current evidence says canonical storage should remain untouched. |
| invalid option must fail before side effects | owned tests and source ordering | Should API validation permit a persistence callback to start before the response throws? |
| client cancel must settle independently | owned active-persistence test and tee cancellation semantics | Can the public `return reader.cancel()` wait on the sibling tee branch and delay HTTP cancellation? |
| one option should cover prelude and heartbeat | both implementations and public issue ask | Would maintainers prefer always-on prelude or split controls? |
| interval guidance remains deployment-specific | controlled carrier and public operational report | Does any documentation imply a universal timeout value? |

## Known risks

- The public replacement is 80 commits behind inspected current `main` and may require rebase repairs.
- Its hosted CI and changeset runs are `action_required` with zero jobs.
- Its direct cancellation test has no active persistence sibling.
- Its invalid-argument tests exercise the wrapper, while response-helper validation occurs after potential tee/callback side effects.
- The owned candidate uses a different opening comment string (`stream-open`) from the public replacement's single `keep-alive` comment. Both are ignorable SSE comments; exact spelling remains maintainer preference.
- Independent final acceptance of a revived submission remains absent.

## Evidence limits

- Fieldwork executed one Node runtime and one controlled proxy design.
- Public production context belongs to the reporter and was not independently accessed.
- Hosted public-PR tests have not executed.
- No claim covers every browser, proxy, CDN, framework adapter, or deployment timeout.
- No authority exists to send review findings to public upstream.

## Staleness check

- Current upstream head checked: `e84b8bc8154030cdb7469b0e0b8cd8b9354f19a0` on `2026-08-01`
- Owned candidate relation: historical base; no rebase attempted because duplicate public work is active
- Public replacement relation: diverged; current `main` is 80 commits ahead, PR contains one commit beyond merge base `e29788dd545f8bf2300db0885658e639b4fd91bd`
- Relevant source paths changed upstream since owned execution: `unclear without a fresh rebase; replacement PR supplies current-path evidence`
- Duplicate/overlap search date: `2026-08-01`
- Open replacement work found: `yes`
- Packet and owned target PR synchronization: packet is current; owned PR should be marked superseded and closed without merge

## Source cleanliness

- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers.
- [x] No stale execution artifacts.
- [x] No unrelated formatting or generated churn.
- [x] Required changeset is explained.
- [x] Commit-pinned links resolve to the reviewed head.

## Test review

- [x] Intended opening-byte and idle-liveness assertions ran.
- [x] Baseline/candidate relationship is clear.
- [x] Setup and product failures are separated.
- [x] Failure and cleanup paths are covered in the owned candidate.
- [x] Disabled and persistence compatibility controls are present.
- [x] Platform and integration limits are explicit.
- [x] Ordinary target gates are named accurately.

## Draft review

- [x] Duplicate issue result replaces a filing draft.
- [x] Duplicate PR result retires a parallel submission.
- [x] Target terminology and current contribution policy were inspected.
- [x] Internal process text remains in Fieldwork only.
- [x] Current public contribution policy was checked at `e84b8bc...`.

## Reviewer disposition

`ACCEPT` the packet's `SUPERSEDED — validation only` outcome.

Reviewed source head: `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`  
Reviewed public replacement head: `21cd681724103701c3596770d7252a7ef0ad18db`  
Reviewed packet head: latest unit-09 handoff on `teamleaderleo/fieldwork#435`  
Reason: exact-head owned evidence is strong, yet active equivalent public work makes a second submission wasteful. The owned edge controls remain worth preserving.  
Clearing condition: public replacement closes without an equivalent accepted fix, followed by current-main rebase, execution, independent review, and explicit authority.  
Reviewer eligibility: `self-review only`

## Human deep-dive guide

The final human reviewer should focus on:

1. whether `reader.cancel()` can delay client cancellation when wrapping a live tee branch;
2. whether invalid configuration should be allowed to start `consumeSseStream` before throwing;
3. whether the public replacement's broader docs and parser test make it the preferred carrier despite those gaps;
4. whether any future contribution should be a tiny lifecycle repair after maintainer direction instead of reviving the full duplicate patch.

Suggested response:

`Unit 09 supersession accepted; retain the owned lifecycle controls as validation.`

—or—

`Unit 09 concern: <specific cancellation, validation, source, test, or overlap issue>.`
