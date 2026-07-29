# Host Capability and MCP Catalogue Lifecycle Reconciliation

## In simple words

Campaign #84 now has three compiled results.

1. Explicit host MCP config reload can create a fresh ready client while ordinary runtime reconciliation keeps its existing reuse contract.
2. Concurrent Rust-SDK relists can leave the SDK cache on newer catalogue C while naive application publication rolls back to older B.
3. Public Codex can advertise cached schema A, accept an A-shaped model call, and later invoke same-name live tool B with a different schema. B's parser rejects the call, and Codex returns that B-side error without first reporting an A/B revision mismatch.

The third result proves the revision split in the real core path. The observed server rejection is useful containment, but it is not a Codex equality decision and cannot be treated as the general safety rule.

Adjacent Scout #130/#131 also compiled a timeout-ownership result: a Codex-style outer timeout sent no MCP cancellation and allowed the server side effect to complete, while the SDK's native request timeout sent cancellation and stopped it. Timeout ownership remains a separate scout, but #84 must account for timed-out calls that can still overlap refresh and publication.

- Campaign issue: #84
- Programme: #14
- Parent campaign: #31
- Target hub: #8
- Priority: P0 after #83
- State: `investigating — schema revision split compiled`
- Worker: GPT-5.6 Thinking
- Fieldwork branch: `campaign/84-host-mcp-lifecycle-reconciliation`
- Owned Codex branch: `fieldwork/31-mcp-config-reload-reconnect`
- Owned draft Codex PR: `teamleaderleo/codex#5`
- Public Codex schema-drift test pin: `openai/codex@a5082373f18119dc5d3eb993267c97f37880935d`
- Official Rust SDK relist test pin: `modelcontextprotocol/rust-sdk@cb50ae7890d8a5daacae1a4ad95f395f06733c07`
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
- traced the Codex request-authority history through the captured-binding, runtime-centralization, and cached-startup changes;
- confirmed that cached catalogue A can supply model planning while live binding B supplies current approval and execution;
- compiled the same-name input-schema transition on public Codex;
- proved that A advertised `echo(message: string)` while B required `echo(count: integer)`;
- proved that current dispatch invoked B with the A-shaped arguments and returned B's schema error to the model;
- retained the exact patch, focused test log, result note, workflow run, job, artifact ID, and artifact digest under `artifacts/codex-cached-schema-drift/`;
- removed the completed temporary schema-drift workflow;
- reviewed Campaign #83's accepted session-scoped receipt owner and adopted its distinction between terminal execution, authoritative persistence, client delivery, and display;
- reviewed Scout #130/#131's compiled timeout result and kept timeout cancellation ownership separate from catalogue publication authority.

## Active work

1. Keep owned Codex PR #5 draft as the accepted first implementation slice.
2. Add the generation-bound host-refresh regression from `concurrency.md`; a boolean reconnect request can be consumed by an older publication.
3. Add a captured-call authority test: a step sampled under prompt-required A must not become silently auto-approved after a permissive config B arrives before dispatch.
4. Convert the compiled same-name schema result into a Codex-side typed pre-execution equality decision. B-side argument rejection is only a negative control.
5. Add cached A/live B tests for changed approval, annotations, visibility, file-input metadata, provenance, behavior, and verified-equal catalogues.
6. Define one authority fingerprint and one catalogue digest used by cache publication, request advertisement, and call-time compatibility checks.
7. Design the Codex notification-driven relist coordinator using the compiled SDK ordering result: only an accepted-current result may publish.
8. Add typed per-server outcomes for unchanged, replaced, failed, cancelled, timed out, superseded, and revision-mismatch refreshes.
9. Specify how an MCP call that timed out locally but remains live on the server is represented during refresh, replacement, shutdown, and result persistence. Coordinate with #83 and #130 rather than duplicating their owners.
10. Add host `preserve_saved`, `replace_from_host`, `clear`, and `reject_on_mismatch` reconstruction semantics after the live-MCP publication boundary is testable.

## Current implementation boundary

The first owned Codex slice changes one host-facing refresh entrypoint. It does not solve:

- generation ownership when refresh publications overlap;
- server-originated tool-list-change relist;
- application publication ordering;
- remote identity or catalogue-digest validation;
- request-captured versus call-time authority;
- call cancellation when an outer timeout ends the local wait;
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
- otherwise fail closed with a typed revision-mismatch result and require a new sampling step.

The compiled schema-drift fixture shows current Codex does not yet perform this comparison. It calls B and relies on B's argument parser to reject the A-shaped call.

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

### Official Rust SDK relist fixture

Retained output:

```text
sdk_cache=catalogue_c naive_application=catalogue_b ticketed_application=catalogue_c requests=3
```

Result: one compiled test passed, zero failed.

The reproduction proves that the SDK's private cache generation is not an application publication contract. A Codex or SDK coordinator needs a public ticket, accepted-current result, or stream containing only accepted snapshots.

### Public Codex cached-schema fixture

Run: `30488803287`  
Job: `90701186402`  
Artifact: `8739076993`  
Digest: `sha256:f759a6b2e0a75bd8b2e2cfb8ef23c42a9d5e4e259473ae121a3b7614089e3148`

Controlled transition:

```text
A advertises echo(message: string)
→ model emits {"message":"hello"}
→ B exposes echo(count: integer)
→ current dispatch calls B
→ B rejects the A-shaped arguments
→ Codex returns B's schema error to the model
```

Result: one focused integration test passed, zero failed.

Classification: `advertisement_execution_revision_mismatch`.

### Adjacent timeout scout

Scout #130/#131 observed with `rmcp 3.0.0`:

```text
external outer timeout: cancellation=false, side effect completed=true
native SDK timeout:     cancellation=true,  side effect completed=false
```

This is not a catalogue-refresh result. It establishes that a locally timed-out Codex call may remain an active server operation while #84 publishes or replaces MCP state.

## Stop rule

Do not promote Campaign #84 as complete until compiled owned-fork tests prove:

- generation-bound explicit host refresh;
- notification-driven relist with late-result rejection;
- remote identity and catalogue equality decisions;
- captured-call authority under config changes;
- cached A/live B mismatch behavior before execution;
- locally timed-out live-call treatment across refresh and publication;
- failed refresh and partial-server outcomes;
- host reconstruction policy across resume and fork.

Keep public Codex and the official Rust SDK read-only unless a separate human decision authorizes upstream contact.
