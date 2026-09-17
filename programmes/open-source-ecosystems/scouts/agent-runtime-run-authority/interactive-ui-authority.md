# Interactive UI authority at the tool boundary

## In simple words

A tool widget changes the front-end from a passive renderer into an actor.

It can request another tool call, send a follow-up prompt, or open a link. The system therefore needs more than a safe iframe: it needs an authority chain from the visible widget back to the correct conversation, MCP server, native tool, and host policy.

TanStack AI's merged MCP Apps implementation is a useful current reference. It separates model data, visible widget data, and interactive call authority, but deliberately leaves authentication and durable session ownership to the host application.

## Retrieval boundary

- TanStack AI observed source: `aade077647556a7ea17d7ddf73bd4e7dc0258301`
- MCP Apps merge: PR `#843`, merge commit `c1a87327b4a3463d37158f32ca90184b5fd092bb`
- Call handler: `packages/ai-mcp/src/apps/call-handler.ts`
- Session-store seam: `packages/ai-mcp/src/apps/session-store.ts`
- Retrieval date: 2026-08-05
- Upstream contact authorized: `false`

## Authority chain

```text
assistant tool result
  -> ui:// resource URI + originating serverId/toolName/toolCallId
  -> UIResourcePart on the visible assistant message
  -> sandboxed widget renderer
  -> client bridge(threadId, message context)
  -> host call endpoint
  -> thread/server descriptor resolution
  -> same-server exposed native-tool check
  -> optional host allowTool policy
  -> fresh MCP connection and callTool
```

## What the design gets right

### Model and widget data remain separate

The `ui://` resource is surfaced as a visible `UIResourcePart` alongside the ordinary tool result. The widget resource does not enter model input. This prevents presentation content from silently becoming model context and keeps the normal tool-result contract authoritative for reasoning.

### Server ownership is explicit

The visible part carries `serverId`, originating native `toolName`, and `toolCallId`. Interactive calls route by the MCP server descriptor associated with that `serverId` rather than letting the widget supply arbitrary transport configuration.

Duplicate or ambiguous server prefixes fail at handler construction.

### Tool authority is conjunctive

The handler reconnects to the selected MCP server and reads the tools that server currently exposes. A call is allowed only when:

1. the requested native tool is exposed by that server; and
2. the optional host `allowTool` policy also approves it.

The host policy extends the exposure check; it cannot replace or bypass it.

### Untrusted arguments fail closed

Widget args must be an object. Arrays, primitives, and null are rejected rather than coerced to an empty argument set.

### Per-call transport lifecycle is bounded

The handler reconnects for each call and closes the client in `finally`. Call and close errors can be reported through a host observability hook without exposing transport configuration to the widget.

## Deliberate integration boundaries

### Conversation ownership is host-owned

`McpAppCallRequest.threadId` is a wire field supplied through the client bridge. The call handler uses it to query the optional `McpSessionStore`, but it does not authenticate the user or prove that the caller owns that thread.

That is a reasonable library boundary. It means the route that invokes the handler must bind the authenticated principal and the requested thread before calling it. A persistent store must not treat a client-supplied thread ID as authorization by itself.

This is an integration requirement, not evidence of an exploitable defect in the library.

### Session durability is optional

The shipped in-memory store is single-instance, uses a sliding TTL, and opportunistically sweeps old thread entries. Persistent or distributed routing is an application backend concern.

A multi-instance deployment that needs stateful MCP transports must supply a shared store and define its own tenant/thread ownership rules.

### Conversation writeback is separate

The widget can send a follow-up prompt through the client chat bridge, but the MCP call handler itself does not establish a durable transcript relation between the widget action, the originating tool call, and the subsequent assistant run.

The visible `toolCallId` and optional `messageId` are correlation material; the handler currently reserves `messageId` and does not consume it.

## Front-facing review questions

1. Is the widget visibly attached to the exact assistant message and tool call that created it?
2. Can an old widget remain interactive after its originating run/message has been superseded or deleted?
3. Does the bridge send the originating message/tool identity, and does the host validate it?
4. Can a widget target a different thread by editing its request body?
5. Are link actions blocked unless the host explicitly handles them?
6. Is the iframe sandbox/proxy a host constant rather than widget-controlled navigation?

## Rear-facing review questions

1. Is `serverId` derived from the originating tool discovery rather than arbitrary transport input?
2. Is the tool checked against the selected server's current exposed native tools?
3. Does host authorization bind principal, tenant, thread, server, and tool?
4. Is stateful transport routing shared across replicas when required?
5. Are per-call clients always closed, including failure paths?
6. Are widget actions persisted or auditable with their originating message/run identity?

## Connection to run authority

Interactive widget authority has the same propagation problem as resumable runs.

A rear-facing server/tool allowlist can be correct while the front-facing widget belongs to a stale message. A front-facing widget can be rendered in the right bubble while its call endpoint accepts an unbound thread identity. Correctness requires both:

- origin identity: message, tool call, server, thread, and possibly run;
- current authority: whether that origin remains allowed to perform a new action now.

A future conformance probe could render two generations of the same widget, supersede the first run, and verify that only the currently authoritative message can issue a state-changing call.

## Current disposition

Retain as a front/rear integration map and potential conformance-test avenue. Do not promote a security or correctness defect without a concrete host integration, threat model, and executable reproduction.
