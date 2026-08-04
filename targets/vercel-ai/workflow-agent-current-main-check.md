# WorkflowAgent current-main check — 2026-08-05

Public revision inspected: `vercel/ai@94e6a99cd9f599b8d400e856d64edb2098d6e349`

A new upstream fix, `#18273`, now streams successfully executed sibling tool results when another tool pauses. That is a useful adjacent lifecycle repair, but it does not resolve the following Fieldwork campaigns.

## #488 — cancellation into local tool execution

Current normal execution routes through `executeTool()`, whose call to `tool.execute()` includes `toolCallId`, messages, context, and sandbox but no `abortSignal`.

The approved-tool continuation also invokes `execute()` without an `abortSignal`.

The agent still builds an effective merged caller/timeout signal for model generation, so the semantic gap remains: model work observes workflow cancellation while locally owned tools do not.

## #489 — approval identity uniqueness

`writeApprovalRequests()` still emits:

```ts
approvalId: `approval-${tc.toolCallId}`
```

The current implementation therefore still assumes provider tool-call IDs are unique across all approval occurrences. No step, generation, or independent generated identity is included.

## #537 — initiating messages after approval

The approved-tool continuation derives `messages = prompt.messages` for telemetry callbacks, but invokes the tool with:

```ts
execute(approval.input, {
  toolCallId: approval.toolCallId,
  messages: [],
  context: resolvedContext,
  experimental_sandbox: sandbox,
})
```

The execution contract drift remains: telemetry sees the prompt messages while the tool itself receives an empty array.

## Consolidated implementation direction

These are distinct observable failures, but the safest implementation likely uses one shared local-tool execution helper for normal and approved paths. That helper should own:

- the initiating message snapshot;
- the effective abort signal;
- resolved per-tool context;
- sandbox;
- telemetry callbacks;
- consistent error classification.

Approval identity generation remains a separate creation-time concern because the identity must survive persistence and resume.

## Evidence boundary

This check establishes current source currency only. Target-native regression tests remain required before promoting a production candidate.
