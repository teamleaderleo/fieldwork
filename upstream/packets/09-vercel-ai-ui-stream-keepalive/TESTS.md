# Tests and receipts — Unit 09 UI-stream SSE keep-alive

## In simple words

The owned candidate passed its complete fork CI and changeset gate at the exact final source head. A separate execution carrier proved a real Node response sends an opening byte before UI data and a controlled forwarding proxy stays open during silence. The final candidate also ran a 100-cycle cancellation/timer soak inside the AI test matrix.

The current public replacement reports broader local execution and adds SDK-parser coverage, yet its hosted public workflows require approval and contain zero executed jobs. Its direct cancellation test omits an active persistence tee, and its response tests omit invalid-option ordering before tee/callback side effects.

## Identity

- Exact historical base: `2b872b0db3769decf69945830c66a897c1e37347`
- Exact candidate head: `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`
- Exact behavior-executed head: `7c8b95b12e7a47e0f614ff949b645e546488eea7`
- Exact execution carrier head: `e89ff00f9f9a0a3badc8a249562a27cc88107114`
- Public replacement head inspected: `21cd681724103701c3596770d7252a7ef0ad18db`
- Test dates: `2026-07-30` through `2026-08-01`
- Environment: GitHub-hosted Ubuntu; AI matrix Node 22/24/26; transport carrier Ubuntu 24.04, Node `v22.23.1`, pnpm `10.33.4`

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| immediate opening comment before source data | `integration-executed` | run `30506032517`, job `90755875694` | pass | Node HTTP server |
| periodic comments preserve controlled proxy liveness | `integration-executed` | 450 ms cutoff, 1,050 ms silence, 75 ms interval | pass | synthetic forwarding proxy |
| canonical completion remains present | `integration-executed` | same carrier | pass | exact behavior head `7c8b95b...` |
| comments stay out of `consumeSseStream` | `target-executed` | owned response test at `b4b572...`; CI `30592239115` | pass | target test topology |
| invalid intervals cause no lock, tee, or callback | `target-executed` | owned Fetch and Node tests | pass | zero, negative, infinity, NaN |
| client cancellation resolves with live persistence branch | `target-executed` | owned response test | pass | Web Streams test implementation |
| 100 repeated open/cancel cycles leave zero timers and one source cancel | `full-gate` for named CI | AI test matrix in `30592239115` | pass | fake timers, one process |
| all public helper layers forward the option | `target-executed` | Fetch, Node, streamText, create-agent, pipe-agent tests | pass | owned fork |
| format/type/build/docs/examples/AI tests pass | `full-gate` | CI `30592239115` | pass | named fork workflow only |
| patch changeset is valid | `full-gate` | Verify Changesets `30592239084` | pass | exact candidate head |
| SDK parser ignores comments in public replacement | `source-read`; contributor reports local execution | public response test patch at `21cd6817...` | prepared in public PR | hosted public CI has no jobs |

## Baseline characterization

### Command or workflow

The retained baseline mechanism was characterized through source review and the execution carrier's negative premise: an idle source produces no body byte through the unmodified helper before source data or close.

### Assertions

- an idle source remains open without body output;
- a body byte is required for the tested Node client to observe response progress;
- a deliberately short-idle forwarding proxy closes silent traffic.

### Result

- status: baseline mechanism confirmed for the controlled Node/proxy path;
- test count: one first-byte scenario plus one idle-proxy scenario;
- workflow and job: `30506032517` / `90755875694` executes the candidate against the same controlled boundary;
- observed candidate behavior: opening byte and proxy liveness pass.

## Candidate-focused tests

### UI response lifecycle and persistence

- Exact source head: `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`
- Test: [`create-ui-message-stream-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/create-ui-message-stream-response-keep-alive.test.ts)
- Assertions: immediate comment; idle comment; interval reset after data; canonical data and `[DONE]`; timer retirement; eventual source cancellation; 100-cycle soak; client cancellation independent of persistence; persistence byte isolation; invalid-option pre-side-effect ordering.
- Result: passed in AI test shards within CI `30592239115`.
- Coverage limit: target-native streams with fake timers.

### Node response helper

- Exact source head: `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`
- Test: [`pipe-ui-message-stream-to-response-keep-alive.test.ts`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/ui-message-stream/pipe-ui-message-stream-to-response-keep-alive.test.ts)
- Assertions: opening comment precedes canonical data; invalid option leaves source unlocked and callback untouched.
- Result: pass in CI `30592239115`.
- Coverage limit: mock response; real Node path covered separately by carrier.

### Wrapper propagation

- Exact source head: `b4b572631f6f288f296d1dcbb6d69e5e848cd9fb`
- Tests: [`streamText`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/generate-text/stream-text-ui-response-keep-alive.test.ts), [`createAgent`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/agent/create-agent-ui-stream-response-keep-alive.test.ts), [`pipeAgent`](https://github.com/teamleaderleo/ai/blob/b4b572631f6f288f296d1dcbb6d69e5e848cd9fb/packages/ai/src/agent/pipe-agent-ui-stream-to-response-keep-alive.test.ts)
- Assertions: the first emitted client chunk proves `keepAliveMs` reaches the common helper.
- Result: pass in CI `30592239115`.
- Coverage limit: option propagation rather than separate lifecycle implementation.

### Real HTTP and controlled proxy

- Exact source head: `7c8b95b12e7a47e0f614ff949b645e546488eea7`
- Workflow: execution carrier [`teamleaderleo/ai#6`](https://github.com/teamleaderleo/ai/pull/6), run `30506032517`, job `90755875694`
- Assertions: exact SHA; opening comment before UI data; canonical completion; proxy remains open more than twice its idle cutoff; one opening comment and at least five periodic comments.
- Result: pass.
- Coverage limit: one self-hosted Node configuration and one deterministic forwarding proxy.

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | CI `30592239115`, `Lint & Format` | pass | `ultracite check` and docs property validation |
| lint/consistency | `Code Consistency` | pass | `konsistent` |
| typecheck | `TypeScript` | pass | repository workflow |
| focused package tests | AI shards Node 22/24/26 | pass | includes unit-09 tests |
| complete target-declared suite | CI `30592239115` | pass | every visible job succeeded |
| build | `Build Packages`, docs and example builds | pass | multiple example groups |
| platform matrix | AI shards on Node 22/24/26 | pass | OS matrix remains GitHub Ubuntu |
| changeset | Verify Changesets `30592239084` | pass | job `91036855917` |

## Reversing controls

- baseline silence versus candidate opening byte;
- disabled option preserves byte-for-byte canonical response output;
- persistence branch receives no synthetic comments;
- invalid configuration produces no ownership side effects;
- client cancel settles independently while persistence remains active;
- repeated lifecycle cycles retire all fake timers.

## Soak, leak, and cleanup controls

- iterations: `100`;
- resources observed: source cancellation call count and Vitest timer count;
- required result per iteration: one source cancel, zero retained timers;
- cancellation behavior: client reader cancellation settles, then eventual source cancellation is observed;
- independent persistence: separate test retains the other tee branch and requires immediate client settlement;
- immediate rerun result: covered within the same completed AI test shard.

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| candidate predecessor CI `30494247717` | one cancellation assertion expected source cancel too early; two files failed format | test expectation plus format | no final product claim | separate client settlement from eventual source cancel; formatter correction |
| carrier run `30503203332` | pnpm version absent | setup | no | pin pnpm `10.33.4` and rerun |
| formatter successor runs `30591830160` and `30591830161` | `action_required`, zero jobs | trigger/authority | no | use formatter-authored source and ordinary candidate CI |
| public replacement runs `30609897348` and `30609897346` | `action_required`, zero jobs | upstream workflow approval | public replacement execution remains unverified by hosted CI | await upstream action; no Fieldwork contact |

## Checks prepared or contributor-reported outside retained execution

Public PR `vercel/ai#17921` states:

- `packages/ai`: 3,297 tests pass in node and edge configurations;
- `pnpm check` and `pnpm type-check:full` pass;
- SDK `parseJsonEventStream` ignores comments;
- Node example receives immediate headers and periodic comments through a 10-second idle interval;
- an equivalent production wrapper has run behind Cloudflare.

These claims come from the public PR author. Fieldwork inspected the code and test patches but has no retained hosted execution receipt for that head.

## Platform and integration gaps

- named Cloudflare, nginx, HAProxy, browser, Next.js adapter, and HTTP/3 matrices were not executed by Fieldwork;
- Fieldwork did not access the public reporter's Railway/Cloudflare deployment;
- public replacement is 80 upstream commits behind current `main` and one commit ahead of its merge base at the inspection point;
- final maintainer API choice remains open.

## Cleanup receipt

- Temporary workflows removed from canonical source head: `yes`
- Publisher or execution-only files removed: `yes`
- Generated residue checked: `yes`, through clean 13-file changed-file fence and passing CI
- Immediate rerun performed: `yes`, final exact-head CI and changeset workflows
- Remaining temporary branches or PRs: closed execution carrier PR/branch retained as historical receipt; owned candidate branch retained read-only for validation

## Current test judgment

`ACCEPT` for the `SUPERSEDED — validation only` disposition.

Reason: the owned candidate has sufficient exact-head execution to preserve its technical findings, while an active public issue and pull request remove the case for a duplicate submission. The packet records the public replacement's current execution gap and the two lifecycle controls that distinguish the owned candidate.

Clearing condition for any revival: the public replacement closes without an equivalent accepted fix, followed by current-main rebase, rerun, independent review, and explicit upstream-contact authority.
