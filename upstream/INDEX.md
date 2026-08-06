# Priority-zero upstream contribution index

## In simple words

This file gives every contribution in issue #435 a stable number and one owned packet path. A new worker can be told only the number, resolve the complete assignment here, and preserve all work under that path.

The number identifies the proposed upstream contribution, not an internal execution carrier or stacked evidence pull request.

## Status vocabulary

- `DIRECT` — a focused owned target-source candidate exists.
- `MATERIALIZE` — the selected candidate exists as a retained patch, Fieldwork repair, or older source branch and needs a clean current target branch.
- `READY` — current clean source, tests, drafts, and review packet are complete.
- `ISSUE FIRST` — technical result is coherent, but maintainer direction should precede a source PR.
- `REPAIR`, `HOLD`, `SUPERSEDED`, and `RETIRE` have the meanings defined in issue #435.

Only the coordinator should reorder or renumber this file. Unit workers own their assigned packet directories and target-source branches.

## Units

| No. | Initial state | Target | Proposed contribution | Assigned packet path | Primary current source |
| ---: | --- | --- | --- | --- | --- |
| 01 | DIRECT | Vite | `fix(dev): continue invalidation after watchChange errors` | `upstream/packets/01-vite-watchchange-errors/` | [`teamleaderleo/vite#4`](https://github.com/teamleaderleo/vite/pull/4) |
| 02 | RETIRE | uv | `fix: make relocatable launchers compatible with BusyBox realpath` | `upstream/packets/02-uv-busybox-realpath/` | [closed uv PR](https://redirect.github.com/astral-sh/uv/pull/20943); [BusyBox handoff](https://redirect.github.com/vda-linux/busybox_mirror/issues/26) |
| 03 | DIRECT | DuckDB | `fix(window): saturate ROWS FOLLOWING overflow at partition end` | `upstream/packets/03-duckdb-rows-following-overflow/` | [`teamleaderleo/duckdb#8`](https://github.com/teamleaderleo/duckdb/pull/8) |
| 04 | DIRECT | DuckDB | `fix(parquet): preserve literal Hive default-partition marker` | `upstream/packets/04-duckdb-hive-partition-marker/` | [`teamleaderleo/duckdb#7`](https://github.com/teamleaderleo/duckdb/pull/7) |
| 05 | DIRECT | Gemini CLI | `fix(core): transfer background shell cleanup ownership atomically` | `upstream/packets/05-gemini-background-ownership/` | [`#11`](https://github.com/teamleaderleo/gemini-cli/pull/11), [`#13`](https://github.com/teamleaderleo/gemini-cli/pull/13), [`#17`](https://github.com/teamleaderleo/gemini-cli/pull/17) |
| 06 | DIRECT | Vercel AI SDK | `fix(ai): make explicit abort settlement nonblocking` | `upstream/packets/06-vercel-ai-explicit-abort/` | [`teamleaderleo/ai#7`](https://github.com/teamleaderleo/ai/pull/7) |
| 07 | DIRECT | node-lru-cache | `fix: snapshot backgroundFetchSize before invoking user code` | `upstream/packets/07-node-lru-background-fetch-size/` | [`teamleaderleo/node-lru-cache#2`](https://github.com/teamleaderleo/node-lru-cache/pull/2) |
| 08 | DIRECT | Playwright Python | `fix: shield shared async shutdown from caller cancellation` | `upstream/packets/08-playwright-python-shared-shutdown/` | [`teamleaderleo/playwright-python#3`](https://github.com/teamleaderleo/playwright-python/pull/3) |
| 09 | DIRECT | Vercel AI SDK | `feat(ai): add opt-in SSE keepalive comments to UI streams` | `upstream/packets/09-vercel-ai-ui-stream-keepalive/` | [`teamleaderleo/ai#4`](https://github.com/teamleaderleo/ai/pull/4) |
| 10 | DIRECT | workerd | `fix(types): generate receiver-aware TypeScript declarations` | `upstream/packets/10-workerd-receiver-types/` | [`teamleaderleo/workerd#1`](https://github.com/teamleaderleo/workerd/pull/1) |
| 11 | DIRECT | OpenTelemetry JS | `fix: snapshot lifecycle targets before concurrent fanout` | `upstream/packets/11-opentelemetry-lifecycle-fanout/` | [`teamleaderleo/opentelemetry-js#6`](https://github.com/teamleaderleo/opentelemetry-js/pull/6) |
| 12 | DIRECT | HTTPX | `fix: preserve terminal AsyncClient state after uncertain close` | `upstream/packets/12-httpx-terminal-async-close/` | [`teamleaderleo/httpx#6`](https://github.com/teamleaderleo/httpx/pull/6) |
| 13 | DIRECT | mmdebstrap | `fix: cancel backend process groups during interruption` | `upstream/packets/13-mmdebstrap-process-group-cancellation/` | [`teamleaderleo/linux-fieldwork#313`](https://github.com/teamleaderleo/linux-fieldwork/pull/313) |
| 14 | DIRECT | DuckDB | `fix(arrow): map sparse union type IDs to child indices` | `upstream/packets/14-duckdb-arrow-union-type-ids/` | [`teamleaderleo/duckdb#14`](https://github.com/teamleaderleo/duckdb/pull/14) |
| 15 | MATERIALIZE | Workers SDK / Miniflare | `fix(miniflare): dispose the runtime before awaited teardown hooks` | `upstream/packets/15-miniflare-runtime-first-disposal/` | [`teamleaderleo/workers-sdk#1`](https://github.com/teamleaderleo/workers-sdk/pull/1) |
| 16 | MATERIALIZE | Gemini CLI | `fix(scheduler): bind confirmation modification to the correlated call` | `upstream/packets/16-gemini-confirmation-call-affinity/` | [`teamleaderleo/gemini-cli#6`](https://github.com/teamleaderleo/gemini-cli/pull/6) |
| 17 | MATERIALIZE | Gemini CLI | `fix(scheduler): balance confirmation waiting ownership` | `upstream/packets/17-gemini-confirmation-waiting/` | [`teamleaderleo/gemini-cli#7`](https://github.com/teamleaderleo/gemini-cli/pull/7) |
| 18 | MATERIALIZE | Playwright MCP | `fix: restrict the shutdown route to loopback peers` | `upstream/packets/18-playwright-mcp-loopback-shutdown/` | [`teamleaderleo/playwright#37`](https://github.com/teamleaderleo/playwright/pull/37), Fieldwork #404 |
| 19 | MATERIALIZE | Context7 | `fix: omit optional client-IP metadata when encryption fails` | `upstream/packets/19-context7-omit-client-ip/` | Fieldwork PR #397 |
| 20 | MATERIALIZE | Jotai | `fix(utils): isolate JSON storage cache identity by key` | `upstream/packets/20-jotai-key-scoped-json-cache/` | Fieldwork PR #252, issue #235 |
| 21 | MATERIALIZE | Jotai | `fix(utils): fence stale async JSON reads by per-key generation` | `upstream/packets/21-jotai-async-read-generation/` | Fieldwork PR #317, issue #282 |
| 22 | MATERIALIZE | Nixpkgs | `gomarkdoc: restore checks without leaking Nix GOFLAGS` | `upstream/packets/22-nixpkgs-gomarkdoc-checks/` | Fieldwork PR #265, issue #241 |
| 23 | MATERIALIZE | Codex | `fix: return durable append acknowledgement from session writes` | `upstream/packets/23-codex-append-acknowledgement/` | [`teamleaderleo/codex#84`](https://github.com/teamleaderleo/codex/pull/84) |
| 24 | MATERIALIZE | Codex | `fix: send the full first generated Responses Lite request after prewarm` | `upstream/packets/24-codex-responses-lite-first-request/` | [`teamleaderleo/codex#87`](https://github.com/teamleaderleo/codex/pull/87) |
| 25 | MATERIALIZE | Playwright MCP | `docs(cli): document remote and shared-browser authority` | `upstream/packets/25-playwright-mcp-remote-authority-help/` | Fieldwork PR #374, issue #371 |
| 26 | MATERIALIZE | Codex | `fix: retain terminal completion bytes before best-effort broadcast` | `upstream/packets/26-codex-terminal-completion-retention/` | [`teamleaderleo/codex#53`](https://github.com/teamleaderleo/codex/pull/53) |
| 27 | MATERIALIZE | Upstash Box | `fix: share one cancellation-request receipt without inventing terminal state` | `upstream/packets/27-upstash-box-cancellation-receipt/` | Fieldwork PR #389, issues #329 and #388 |

## Issue-first parking lot

These are promising and remain linked from #435, but they do not have unit numbers until a sufficiently complete source candidate exists:

- Vite late import/HMR reconciliation and graph transaction work;
- uv corrupted extracted-wheel cache reuse;
- Workers SDK configuration selection and deployment receipts;
- Gemini discovered-tool abort and execution-termination receipt work;
- Context7 loopback-default and trusted-proxy HTTP policy;
- DuckDB secondary ART checkpoint corruption validation;
- uv PEP 723 symlink lock authority.

Do not renumber the 27 units when one of these becomes ready. Assign the next unused number.

## Claim and handoff

A worker taking unit `<NN>` should:

1. create or update the assigned packet path from `upstream/templates/`;
2. post a compact claim on #435 naming the unit, packet branch, target branch, and exact initial source heads;
3. avoid editing another unit's packet;
4. preserve every material result in the packet, target pull request, or owning issue;
5. finish with a #435 handoff naming disposition, exact heads, tests, packet path, source branch, remaining blockers, and public-contact state.

The packet remains incomplete while a material observation exists only in a conversation.
