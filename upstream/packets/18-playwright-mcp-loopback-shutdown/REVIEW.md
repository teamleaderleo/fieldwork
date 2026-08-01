# Review — Unit 18 Playwright MCP shutdown authority

## In simple words

The candidate removes a test-only process termination route from MCP HTTP and preserves the graceful lifecycle test through the spawning parent's private IPC channel. The complete final three-file diff has been self-reviewed. Exact current-head execution is green on macOS and Windows; Ubuntu is queued before runner allocation. The remaining technical review questions concern compatibility of removing the route, placement of the private listener in the CLI entrypoint, strict message validation, and behavior in non-test parent embeddings.

## Review subject

- Work class: `upstream-fork research`
- Target repository: `teamleaderleo/playwright`; proposed destination `microsoft/playwright`
- Proposed upstream base: `15b1aec478d90f0293dae7b7b6dafd494d9f0154`
- Canonical source branch/head: `fix/mcp-parent-ipc-shutdown@e99e97da2acfc6c1a67749bc749e1d0cb71b5607`
- Owned source PR: [`teamleaderleo/playwright#40`](https://github.com/teamleaderleo/playwright/pull/40)
- Packet branch: `p0/435-unit-18-playwright-mcp-shutdown`
- Packet PR: [`teamleaderleo/fieldwork#451`](https://github.com/teamleaderleo/fieldwork/pull/451)
- Complete changed-file fence: `mcp.ts`, `http.ts`, `http.spec.ts`
- Upstream-contact authority: none

## Reading order

1. [`README.md`](./README.md)
2. [`CURRENT_SOURCE.md`](./CURRENT_SOURCE.md)
3. [`CURRENT_EXECUTION.md`](./CURRENT_EXECUTION.md)
4. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
5. [`APPROACHES.md`](./APPROACHES.md)
6. [`TESTS.md`](./TESTS.md)
7. [complete source compare](https://github.com/teamleaderleo/playwright/compare/fieldwork/435-unit-18-base-15b1aec...fix/mcp-parent-ipc-shutdown)
8. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
9. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact source links

- [`mcp.ts@e99e97d`](https://github.com/teamleaderleo/playwright/blob/e99e97da2acfc6c1a67749bc749e1d0cb71b5607/packages/playwright-core/src/entry/mcp.ts)
- [`http.ts@e99e97d`](https://github.com/teamleaderleo/playwright/blob/e99e97da2acfc6c1a67749bc749e1d0cb71b5607/packages/playwright-core/src/tools/utils/mcp/http.ts)
- [`http.spec.ts@e99e97d`](https://github.com/teamleaderleo/playwright/blob/e99e97da2acfc6c1a67749bc749e1d0cb71b5607/tests/mcp/http.spec.ts)
- generated, lock, dependency, workflow, or evidence files: none

## Complete-diff self-review

### Production entrypoint

The listener is installed only when `process.send` exists. `isTestSigintMessage` rejects null, primitives, arrays, non-ordinary prototypes, inherited-only properties, extra own string or symbol keys, wrong values, and missing keys. The listener removes itself before emitting SIGINT, making duplicate valid delivery one-shot. IPC deserialization is expected to deliver ordinary data; a final reviewer should still judge whether getter/proxy concerns deserve an explicit comment or are outside the reachable transport model.

### HTTP transport

The `/killkillkill` branch and fixed header check are removed. Host validation and ordinary SSE/streamable handling remain unchanged. The compatibility question is whether any intended use outside the native test harness depends on this undocumented test route.

### Native tests

The fixture adds an IPC channel to spawned children and exposes send/disconnect controls. The shutdown test proves the old HTTP request is not accepted and the client remains live; wrong string/version, extra-field, and inherited-property messages are inert; the valid message sent twice produces one graceful-close record. A separate test proves IPC disconnect is inert. The rest of the 18-test MCP HTTP file exercises ordinary lifecycle paths.

### Source cleanliness

- [x] Net diff is exactly three intended files.
- [x] No Fieldwork-only files, temporary workflows, receipts, publishers, generated files, locks, snapshots, or dependency changes.
- [x] Incidental test comment rewrite and missing final newline were removed.
- [x] Public base remains `15b1aec...`; candidate paths are current.
- [ ] Source history is seven commits and must be squashed before authorized submission.

## Current exact-head execution

Carrier [`teamleaderleo/fieldwork#455@0323aea`](https://github.com/teamleaderleo/fieldwork/pull/455), workflow [`30690674059`](https://github.com/teamleaderleo/fieldwork/actions/runs/30690674059):

- macOS 15 ARM64 / Node 22.23.1: exact identity and diff fence, locked install, complete build, Chromium, 18/18 native tests, focused ESLint, clean tree, and exact diff all passed. Artifact `8815562250`; digest `sha256:80a6f32f6b8a560924af3a562c0af5bcc16ee4993cd2fdf05306b3bc67bd2d54`.
- Windows Server 2025 x64 / Node 22.23.1: the same gates all passed. 18/18 in 34.0s. Artifact `8815574235`; digest `sha256:804ed03b8a52765366cdec5737cc0f9b3d7f90714b9939b8e613cb39af20bdf4`.
- Ubuntu 24.04: job `91344705054` remains queued before allocation; no product execution or failure.

Historical hardened predecessor run `30659762667` passed the same 18-test file and declared gates on Ubuntu, macOS, and Windows, but its validator accepted extension fields. That history is supporting evidence, not a silent substitute for the queued current Ubuntu job.

## Claims requiring independent judgment

| Claim or choice | Evidence | Reviewer question |
| --- | --- | --- |
| Parent IPC is narrower authority than HTTP | characterization, proxy discriminator, current diff | Is any supported external use of `/killkillkill` being removed? |
| Listener belongs in `mcp.ts` | source ownership and native spawn path | Is there a more test-local existing hook that preserves packaging and Windows behavior? |
| Strict own-property validation is appropriate | current source and exact macOS/Windows execution | Is the protocol clear and fail-closed without unnecessary complexity? |
| Duplicate delivery is one-shot | listener removal before SIGINT and current tests | Could queued Node IPC events invoke a removed listener? |
| Ubuntu predecessor can support a carry-forward decision | historical 18/18 plus current macOS/Windows 18/18 | Is explicit carry-forward acceptable, or must the queued exact-head Ubuntu job complete? |

## Evidence limits

- Ubuntu exact-current-head execution has not started.
- Full Playwright repository CI has not run.
- Node versions outside 22 have not run.
- Parent embeddings outside the native Playwright test harness have not run.
- Same-account self-review does not satisfy independent final acceptance.
- Playwright issue approval/assignment is absent.
- Public upstream contact is unauthorized.

## Test review checklist

- [x] Baseline behavior and authority boundary characterized.
- [x] Losing loopback approach disproved by a proxy discriminator.
- [x] Setup, packaging, runner, and product outcomes classified separately.
- [x] Exact current-head macOS and Windows focused gates passed.
- [x] Strict extra-field and inherited-property controls executed on those platforms.
- [ ] Exact current-head Ubuntu gate completed or explicit carry-forward accepted.
- [ ] Full repository CI, if maintainers request it.

## Draft review

- [x] Issue draft avoids unsupported prevalence and severity claims.
- [x] PR draft describes the actual three-file direction.
- [x] Playwright terminology and issue-first policy are represented.
- [x] Fieldwork workflow language is excluded from public drafts.
- [ ] AI disclosure requirement must be checked again at filing time.

## Reviewer disposition

`EXECUTE`

Reviewed source head: `e99e97da2acfc6c1a67749bc749e1d0cb71b5607`  
Reason: complete self-review and two-platform exact-head execution are green; Ubuntu is still queued.  
Clearing condition: exact Ubuntu success or explicit independent carry-forward judgment, followed by independent complete-diff acceptance.  
Next route after clearing: `ISSUE FIRST`.  
Reviewer eligibility: self-review only.

## Final human inspection guide

Focus on:

1. compatibility of deleting the route;
2. whether `mcp.ts` is the clearest owner for the private test-parent listener;
3. whether the strict plain-object validator accurately matches Node IPC data;
4. whether the exact current macOS/Windows results plus historical Ubuntu result justify carry-forward if the current Ubuntu runner remains unavailable;
5. whether the seven-commit branch is squashed to an equivalent one-commit tree before any authorized submission.
