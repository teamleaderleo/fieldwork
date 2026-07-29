# Host Capability and MCP Catalogue Lifecycle Reconciliation

## In simple words

Campaign #84 has one compiled owned-Codex source slice and one compiled official-Rust-SDK reproduction.

The Codex slice gives explicit host MCP config reload fresh-client behavior while ordinary runtime reconciliation keeps its existing ready-client reuse contract. The SDK reproduction proves that concurrent tool-list-change relists can leave the SDK cache on the newest catalogue while a naive application publisher rolls its own catalogue back to an older successful result.

A second Codex boundary is now source-confirmed: one model request can advertise cached catalogue A and later approve and execute the same tool name through live binding B. Equality of A and B is currently assumed rather than verified.

- Campaign issue: #84
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- Priority: P0 after #83
- State: `investigating — first source slice compiled`
- Worker: GPT-5.6 Thinking
- Fieldwork branch: `campaign/84-host-mcp-lifecycle-reconciliation`
- Owned Codex branch: `fieldwork/31-mcp-config-reload-reconnect`
- Owned draft Codex PR: `teamleaderleo/codex#5`
- Public Codex recheck: `openai/codex@85c082ccccf6b5ac4d6c31d14f960057348b78f4`
- Official Rust SDK pin: `modelcontextprotocol/rust-sdk@cb50ae7890d8a5daacae1a4ad95f395f06733c07`
- Owned fork base: `teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf`
- Upstream contact: unauthorized and unused

## Completed

- consumed accepted L01, L04, and L06 evidence from Campaign #31;
- separated ordinary low-latency reconciliation from explicit host refresh;
- confirmed that `Op::RefreshMcpServers` already requests reconnect;
- confirmed that `CodexThread::refresh_mcp_config` previously applied config without requesting reconnect;
- committed the bounded reconnect candidate and focused regression in owned Codex PR #5;
- passed Rust formatting;
- passed `host_mcp_config_refresh_reconnects_ready_clients`;
- passed `reconciliation_reuses_connection_without_relisting_regular_tools`;
- classified unrelated repository formatter prerequisites as `harness_unavailable`;
- classified the existing app-server `ItemCompletedEvent.started_at_ms` compile failure as `baseline_compile_blocker`;
- confirmed that Codex logs `notifications/tools/list_changed` without relisting or publishing a new catalogue revision;
- compiled a real official-SDK reproduction with two overlapping callback relists;
- confirmed that the SDK cache retains newer catalogue C while a naive application publisher can roll back to older B;
- retained the SDK fixture, `Cargo.lock`, exact log, and validation record on L01 amendment PR #74;
- traced the Codex request-authority history through PRs #34588, #34930, and #35590;
- confirmed that cached catalogue A can supply model planning while live binding B supplies current approval and execution.

## Active work

1. Keep owned Codex PR #5 draft as the accepted first implementation slice.
2. Add the generation-bound host-refresh regression from `concurrency.md`; a boolean reconnect request can be consumed by an older publication.
3. Add a captured-call authority test: a step sampled under prompt-required A must not become silently auto-approved after a permissive config B arrives before dispatch.
4. Add cached A/live B tests for removed, same-name schema-changed, authority-changed, and verified-equal catalogues.
5. Define one authority fingerprint and one catalogue digest used by cache publication, request advertisement, and call-time compatibility checks.
6. Design the Codex notification-driven relist coordinator using the compiled SDK ordering result: only an accepted-current result may publish.
7. Add typed per-server outcomes for unchanged, replaced, failed, cancelled, superseded, and revision-mismatch refreshes.
8. Add host `preserve_saved`, `replace_from_host`, `clear`, and `reject_on_mismatch` reconstruction semantics after the live-MCP publication boundary is testable.

## Current implementation boundary

The first owned Codex slice changes one host-facing refresh entrypoint. It does not solve:

- generation ownership when refresh publications overlap;
- server-originated tool-list-change relist;
- application publication ordering;
- remote identity or catalogue-digest validation;
- request-captured versus call-time authority;
- cold resume/fork host replacement semantics;
- failed-refresh retention policy.

## Accepted authority direction

For an MCP tool already prepared by the sampling step:

- execute the captured call rather than routing to a replacement client;
- fail on the captured client if it closes;
- permit current policy to add restrictions;
- defer current-policy relaxation until a new sampling step.

For a cached tool advertised without a captured prepared call:

- wait for the live client only as a bounded exception;
- compare advertised A and live B authority fingerprints;
- execute B only when equality is verified;
- otherwise fail closed and require a new sampling step.

## Validation receipts

### Owned Codex PR #5

Passing:

```text
cargo fmt --all -- --check
just test -p codex-core host_mcp_config_refresh_reconnects_ready_clients
just test -p codex-mcp reconciliation_reuses_connection_without_relisting_regular_tools
```

Broader limits:

- full `codex-core` encountered unrelated sandbox-dependent failures;
- the app-server MCP filter stopped at the pre-existing missing `started_at_ms` field;
- neither result is evidence against the reconnect candidate.

### Official Rust SDK fixture

Retained output:

```text
sdk_cache=catalogue_c naive_application=catalogue_b ticketed_application=catalogue_c requests=3
```

Result: one compiled test passed, zero failed.

The reproduction proves that the SDK's private cache generation is not an application publication contract. A Codex or SDK coordinator needs a public ticket, accepted-current result, or stream containing only accepted snapshots.

## Stop rule

Do not promote Campaign #84 as complete until compiled owned-fork tests prove:

- generation-bound explicit host refresh;
- notification-driven relist with late-result rejection;
- remote identity and catalogue equality decisions;
- captured-call authority under config changes;
- cached A/live B mismatch behavior;
- failed refresh and partial-server outcomes;
- host reconstruction policy across resume and fork.

Keep public Codex and the official Rust SDK read-only unless a separate human decision authorizes upstream contact.