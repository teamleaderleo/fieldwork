# Codex cached-A/live-B schema-drift reproduction

Date: 2026-07-30  
Public Codex pin: `a5082373f18119dc5d3eb993267c97f37880935d`  
Fieldwork workflow run: `30488803287`  
Workflow job: `90701186402`  
Evidence artifact: `8739076993`  
Artifact digest: `sha256:f759a6b2e0a75bd8b2e2cfb8ef23c42a9d5e4e259473ae121a3b7614089e3148`

## Question

What happens when inference receives cached catalogue A for a same-name MCP tool while the replacement live binding B exposes a different input schema before call dispatch?

## Controlled transition

```text
catalogue A: echo(message: string)
→ A is cached and advertised to inference before replacement startup completes
→ the model emits {"message":"hello"}
→ catalogue B starts with echo(count: integer)
→ current Codex dispatch resolves the call through B
```

## Observed result

The request body advertised A's schema: required field `message`, with no `count` property.

After startup, the same tool call was sent to B. B rejected the A-shaped arguments with:

```text
echo schema v2 requires integer count
```

Codex returned that B-side schema error to the model-visible function-call output. It did not detect or report an A/B catalogue-revision mismatch before invoking B.

The focused test passed because the reproduction asserted the current behavior:

```text
running 1 test
test suite::mcp_tool_cache::regular_mcp_definition_cache_preserves_live_session_state ... ok

test result: ok. 1 passed; 0 failed
```

## Classification

`advertisement_execution_revision_mismatch`

This is fail-closed at the server argument parser in this fixture, but it is not a typed Codex equality decision. A permissive B implementation could accept A-shaped arguments under changed semantics. The safety boundary therefore cannot rely on B rejecting malformed arguments.

## Required correction

For a cached tool with no captured prepared call:

1. retain the advertised A authority fingerprint;
2. wait for live B only as the bounded startup exception;
3. compare A and B before argument rewrite, approval, or execution;
4. execute B only when equality is verified;
5. otherwise return a typed revision-mismatch result and require a new sampling step.

## Harness receipts

The final workflow explicitly installed `just` and `cargo-nextest`, built `test_stdio_server`, applied the patch to an ephemeral read-only public-Codex checkout, passed Rust formatting and diff checks, and ran one focused integration test.

Earlier attempts are retained as harness development receipts:

- missing helper binary: `harness_unavailable`;
- fixture return-type mismatch: test-only compile correction;
- neither attempt reached the behavior boundary.

Public Codex remained read-only. No upstream contact occurred.
