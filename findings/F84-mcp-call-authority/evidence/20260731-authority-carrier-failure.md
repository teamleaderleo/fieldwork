# Authority carrier #79 failure receipt

Date: 2026-07-31  
Carrier: `teamleaderleo/codex#79`  
Carrier head: `d96bcf0b8d9b254474c1d27739bd40ee5c6a04fa`  
Source base selected by workflow: `a01a2d91461a57809e944de7758477b92617ab01`  
Workflow: `fieldwork-84-mcp-authority-a01a`  
Run: `30584093534`  
Job: `91011250342`  
Conclusion: `failure`  
Evidence class: `carrier-only`; zero source-behavior evidence

## First failure

The workflow completed checkout, identity setup, and Rust toolchain setup. It failed in `Apply latest-head authority candidate` before formatting, source-fence verification, tests, or source publication.

Exact error:

```text
turn context: expected 1 anchor, found 2
Process completed with exit code 1
```

The transformer attempted to replace a broad `let turn_context = &step_context.turn;` anchor in `codex-rs/core/src/mcp_tool_call.rs`. The current file contains two matching anchors, so the script correctly stopped instead of modifying an ambiguous location.

## Classification

- harness/source-application failure;
- no candidate source was executed;
- no authority test ran;
- no source-only branch was published;
- V8 canary passed independently;
- broad blocking CI remains unrelated to this first failure.

Disposition: `REPAIR`, with the present approach also superseded in design by the captured-first plus authority-checked cached fallback recorded in the canonical finding.

## Smallest next action

Build the successor directly against current public Codex source instead of repairing this textual transformer. The successor should:

1. use `step_context.mcp.prepare_call` for ordinary captured calls;
2. reserve current-runtime preparation for cached-only advertisements;
3. compare a deliberate callable-authority fingerprint in `codex-mcp`;
4. run end-to-end controls proving exact captured-client dispatch and zero approval/hook/rewrite/MCP dispatch on mismatch.

Public upstream interaction: none.
