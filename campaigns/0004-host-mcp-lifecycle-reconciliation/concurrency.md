# MCP Refresh, Relist, and Authority Ordering

## In simple words

Campaign #84 now has two confirmed generation problems.

First, the owned Codex reconnect candidate uses a boolean. A host reload can request reconnect for desired state B, yet an older publication A can consume that request first.

Second, the official Rust SDK uses a private generation to protect its own response cache. A stale relist result rejected by that cache still returns successfully to application code. Without an application publication ticket, an older callback can replace a newer catalogue.

Both cases need one rule: a freshness request belongs to an identified generation, and only a result accepted for the newest relevant generation may publish.

## Current Codex owners

### Session refresh invalidation

`McpRefresh` contains:

- `pending: AtomicBool`;
- a semaphore serializing publication;
- `invalidate()` to set pending;
- `claim()` to swap pending to false;
- a guard restoring pending when claimed work ends before publication.

This preserves work across cancellation and coalesces invalidations. It does not preserve the identity or ordering of desired-state revisions.

### Runtime reconnect intent

`McpRuntime` contains:

- `reconnect_pending: AtomicBool`;
- `reconnect_on_next_refresh()` to set it;
- `replace()` to claim it;
- a guard restoring it when publication does not finish.

This binds reconnect intent to whichever `replace()` call arrives first, rather than to the desired-state generation that requested the reconnect.

## Codex adversarial host-refresh sequence

1. Publication A claims the current refresh invalidation and computes desired state A.
2. Host reload installs desired state B, marks refresh pending, and requests reconnect for B.
3. Publication A reaches `McpRuntime::replace()` and consumes the boolean reconnect request.
4. Publication A creates a fresh client for A.
5. Publication B later computes desired state B.
6. B sees reconnect already cleared.
7. When configured connection identity is unchanged, B may reuse A's freshly created client and its startup catalogue.

The final runtime can therefore carry desired configuration B with remote identity and catalogue captured during publication A.

## Compiled Rust SDK ordering sequence

The retained official-SDK fixture ran two overlapping callback relists:

```text
R1 captures older cache generation and waits
→ N2 invalidates again
→ R2 returns catalogue C and publishes first
→ R1 returns catalogue B late
```

Observed:

```text
sdk_cache=catalogue_c
naive_application=catalogue_b
ticketed_application=catalogue_c
requests=3
```

The SDK cache remained correct because its private generation rejected R1's stale write. The R1 caller still received `Ok(B)`, so a naive publisher rolled application state back. A callback notification-generation ticket retained C.

This confirms that response-cache freshness and application publication freshness are different decisions.

## Request-authority interaction

A third generation boundary occurs after model sampling.

- Sampling step A captures model tools and router metadata.
- Thread MCP state can refresh to B while the model response is in flight.
- Current core dispatch refreshes and resolves the tool call through B.

A current configuration may need to tighten an in-flight call. It must not silently relax the authority under which the call was sampled.

The safest rule is dual authorization:

```text
an in-flight call may proceed only when captured authority A and current authority B both allow it
```

This means:

- prompt when either authority requires prompting;
- deny when either authority disallows the action;
- use the tighter sandbox or permission restriction;
- begin a relaxation only with a newly sampled step.

Catalogue generation and approval generation should be recorded separately even when they usually move together.

## Unified refresh ticket

A refresh ticket should contain:

- monotonically increasing desired-state generation;
- source reason: host reload, user reconnect, auth change, server notification, config change, or recovery;
- per-server reconnect or relist requirement;
- configured connection identity;
- observed remote server identity;
- advertised catalogue digest;
- live catalogue digest;
- approval/config authority digest;
- supersession state;
- requested completion policy: synchronous, background publication, or advisory only.

## Publication rules

1. An older publication cannot consume a newer generation's reconnect requirement.
2. A relist result can publish only when its ticket remains current.
3. A failed newer result cannot make an older successful result current again without an explicit retention decision.
4. Per-server results publish independently only when the campaign's partial-failure policy allows it.
5. Request bindings already captured by a sampling step remain immutable.
6. Current policy may add restrictions to an in-flight call but cannot relax captured authority.
7. Cached-startup late binding requires verified equality between the advertised and live authority fingerprints.

## Required Codex regressions

### Generation-bound host reconnect

Hold publication A after desired state A is computed and before runtime replacement. While held:

- install config B;
- request reconnect for B;
- release A;
- allow B to publish;
- assert B receives a client initialized for B's generation;
- assert A cannot consume B's reconnect ticket;
- assert no late A result overwrites B.

### Concurrent host reload and notification

- start host refresh B;
- receive tool-list notification C during publication;
- delay B's server result;
- complete C first;
- verify the chosen ordering policy and typed supersession result;
- verify neither result publishes with the other generation's identity or catalogue.

### Captured approval versus current relaxation

- sample under A requiring approval;
- apply permissive B before dispatch;
- emit the A tool call;
- verify it still prompts or fails closed;
- reverse the policies and verify current B can tighten the call.

### Cached A/live B compatibility

Test:

- removed tool;
- same name with changed input schema;
- same name with changed annotations or approval metadata;
- equal accepted fingerprint.

Require fail-closed mismatch or a recorded verified late rebind.

## Candidate implementation approaches

### Generation-bound reconnect request

Replace the boolean reconnect switch with a requested generation. Publication claims reconnect only when publishing that generation or a later generation under an explicit coalescing rule.

### Serialized explicit host refresh

Acquire the publication gate, install B, and publish a fresh runtime before returning. This gives direct completion semantics but can block on server startup and needs timeout plus partial-failure rules.

### Per-server refresh tickets

Use one ticket per server so a slow or failed server does not prevent unrelated accepted publications. The thread-level generation still joins the resulting server revisions into one request-binding receipt.

### SDK accepted-result coordinator

An opt-in SDK helper can expose:

- public relist ticket;
- accepted-current result;
- coalesced watch stream of accepted catalogues.

Codex still owns remote identity validation, catalogue revision, request binding, and approval authority.

## Current recommendation

Keep the one-line reconnect candidate as the compiled first slice. The next Codex source change should introduce generation ownership before expanding refresh behavior.

Use the same generation vocabulary for host reload, notification relist, reconnect, and catalogue publication. Keep approval authority separate and apply current changes as added restrictions only for already-sampled work.