# F84 reconnect 4/4 receipt and captured-authority diagnostic state

Date: 2026-07-31  
Finding: `F84-mcp-call-authority`  
Public upstream interaction: none; `openai/codex` remained read-only.

## Reconnect result

The stronger reconnect carrier completed its focused workflow successfully.

- carrier PR: `teamleaderleo/codex#90`
- executed carrier head: `cf9f8765b67562679f7776169fb506a6a0bb7d94`
- workflow run: `30595049466`
- focused job: `91045520894`
- exact marker: `FIELDWORK_MCP_RECONNECT_QUIESCENCE_EXACT=4/4`
- source base: `openai/codex@4642370542739d5dd080b0c87a9de06a6435d3db`

The four exact controls established:

1. explicit host-requested MCP refresh reconnects a ready client;
2. ordinary runtime refresh continues to reuse a ready client;
3. the public app-server reload path starts exactly one replacement and remains quiescent through the 250 ms observation interval;
4. malformed configuration returns a reload error, performs zero reconnect, preserves the original ready client, and that original client still completes a subsequent tool call.

The clean source-only successor is draft PR `teamleaderleo/codex#101` at exact head `df954cf690e360771b3a2753eaee8a508da21d6c`.

The execution carrier was retired after receipt transfer:

- cleanup head: `69a47d51e73e650cc41322191a9f2d90033e40d1`;
- temporary transformer and workflow deleted;
- direct diff against the carrier base verified empty;
- PR #90 closed without merge.

### Bounded claim

The receipt proves one observed replacement initialization and quiet-period behavior. It does not yet prove that a tool call after a successful reload is served by the newly published replacement runtime.

That missing success-path control is materially different from the malformed-config control: the malformed path deliberately proves continued usability of the preserved original client. Before promotion as a complete successful-reload lifecycle result, issue a post-reload tool call and prove it is served successfully by the replacement runtime.

The intervening public source movement to `f0c30e528a54bdf0fa9a4d52ff74b34383434811` was file-disjoint from the three-file reconnect source fence when reviewed. It does not erase the exact-base receipt, and it does not by itself require a restack. Current-head packaging remains a separate promotion step.

## Captured-authority carrier state

The first structured captured-authority execution did not produce passing behavior evidence.

- carrier PR: `teamleaderleo/codex#92`
- executed candidate head: `af6af7da8c337364a48954521dde5a7f741558f5`
- workflow run: `30595072484`
- focused job: `91045590945`
- source base: `openai/codex@4642370542739d5dd080b0c87a9de06a6435d3db`

Setup, transformation, source-fence verification, and formatting succeeded. The exact cargo compile/test step failed before any `FIELDWORK_MCP_AUTHORITY_CAPTURED_EXACT=4/4` marker. Therefore:

- zero structured-authority behavior controls are counted as passing;
- no clean source branch was published;
- the candidate is not proposal evidence;
- no product repair should be guessed from the incomplete rendered log.

A diagnostic-only carrier update was made at head `175bb38703f9d9e2f12313c342c732915dc5628b`. It leaves the transformer unchanged and captures raw cargo output as a workflow artifact. Diagnostic run `30625457294` is queued at the time of this record.

Static review confirms that the selected captured-first direction matches the exact `PreparedMcpCall` API surface. The remaining immediate question is the concrete compile/test defect, not whether the source exposes the required captured client and authority objects.

## Authority limits still open

Even a future focused `4/4` result will remain insufficient for promotion until an end-to-end mismatch control proves the rejection occurs before all pre-dispatch side effects:

- no approval prompt or remembered-approval registration;
- no permission hook;
- no OpenAI file-input rewrite;
- no memory pollution marking;
- no request metadata construction with live-only authority;
- no MCP server dispatch.

The first candidate also conservatively treats the whole tool `_meta` object as execution authority. Review must narrow that set to fields that actually affect app identity, account authority, approval, rewriting, or dispatch; presentation and telemetry metadata must not create false incompatibility.

## Current disposition

- Reconnect: `target-executed`, clean source draft open, carrier retired, bounded post-success usability control still required.
- Captured authority: `compile/test failure`, diagnostic rerun queued, zero behavior evidence, source promotion held.
- Base movement: no mechanical restack solely for file-disjoint source movement; renew exact-head review when overlap, mergeability, governing protocol, or promotion makes it material.
