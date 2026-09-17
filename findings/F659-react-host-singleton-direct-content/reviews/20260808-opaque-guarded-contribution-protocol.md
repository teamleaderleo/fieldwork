# Body DSIH — guarded contribution protocol synthesis

## Goal

Unify the strongest server/client findings into one body-specific protocol without reviving the rejected raw-boundary-stream experiment.

A complete server representation needs to solve simultaneously:

1. body-scope order;
2. adjacent text isolation;
3. Suspense/Activity control-comment collision;
4. boundary failure cleanup;
5. preamble property/adoption authority;
6. matching hydration provenance;
7. empty opaque content;
8. conversion into the client contribution model.

## Proposed protocol family

Treat body DSIH as a first-class **guarded opaque contribution** rather than ordinary singleton `innerHTML` property bytes.

For a body contribution with token `T`, conceptually separate two channels:

### Singleton opening / property ownership

The document preamble still carries the persistent body opening and attributes, plus an adopted contribution token/descriptor:

```text
<body ...>
<!--react-body-owner:T:descriptor-->
```

For a boundary-local body, the boundary's inline preamble marker carries only the candidate token:

```text
<!--body:T-->
```

Cleanup of singleton attributes is authorized only if `T` matches the contribution token that actually appears with the adopted document body.

A losing boundary whose body preamble was never hoisted therefore cannot clear another body's attributes merely because it emitted an early candidate marker.

The descriptor can carry the already-researched emitted prop/style/ViewTransition ownership metadata.

### Opaque child contribution

The raw DSIH bytes are emitted at the body's **ordinary body-scope Fiber position**, bracketed by React-generated opaque guards:

```text
<!--react-opaque-start:T-->
<raw DSIH bytes>
<!--react-opaque-end:T-->
```

This is true for root and boundary-local body contributions.

The body opening remains preamble; its child contribution no longer lives in `bodyChunks`.

## Why this fixes body-scope ordering

Fizz already renders managed body children through the ordinary segment at the body Fiber position.

Placing the guarded DSIH range into the same segment restores the public client ordering model:

```text
root sibling before
body contribution
root sibling after
```

The guard comments also prevent raw top-level text from merging with adjacent body-scope React text nodes, replacing the missing `lastPushedText` boundary with an explicit DOM boundary.

This avoids the limitation found in the tiny PR 48 element-only experiment.

## Why this avoids PR 34's control-comment collision

PR 34 moved arbitrary DSIH directly into a Suspense boundary stream. `clearHydrationBoundary()` then interpreted raw author comments such as `$`, `/$`, `head`, or `body` as React control markers.

Under a guarded protocol, the cleanup scanner learns one new rule:

1. when it reaches `react-opaque-start:T`, locate the matching `react-opaque-end:T`;
2. treat every DOM node between those guards as opaque payload;
3. remove/skip that range without interpreting any inner comment data as Suspense, Activity, or preamble protocol.

Raw author comments remain ordinary DSIH content even when they exactly equal existing React control words.

The guards themselves are outside the raw payload and are the only comments interpreted by the opaque-range rule.

## Collision-safe token selection

A static guard string is still forgeable by arbitrary DSIH.

Fizz has the raw `__html` value before emitting it, so token allocation can avoid accidental collision without parsing HTML:

1. allocate a request-local numeric opaque contribution ID;
2. construct a guard token from a fixed safe prefix plus the numeric ID;
3. check whether the exact **token data string** occurs anywhere in the raw DSIH source;
4. if it does, advance the ID until a token absent from the raw source is found.

HTML comment data does not decode character references, so choosing a safe ASCII token whose character sequence is absent from the raw source prevents ordinary raw markup from parsing into an identical comment data value through entity syntax.

A deliberate third-party script can inspect/copy React's token after parsing; this protocol is aimed at collision-safe correctness, not defending against code intentionally impersonating React internals.

Use a comment-safe token alphabet that cannot contain `--` or other invalid comment sequences. Do not inject arbitrary `identifierPrefix` text directly into comment data without encoding.

A request-global counter likely belongs in resumable state if tokens can be allocated across prerender/resume; verify this before implementation.

## Matching hydration

For body, `claimHydratableSingleton()` already preserves the body-scope hydration cursor.

When the body Fiber expects DSIH:

1. the cursor locates the opaque start guard at the body's logical slot;
2. the paired end guard identifies the contribution's initial right edge;
3. nodes between guards are the server opaque slot payload under the chosen slot-ownership policy;
4. hydration can create the client contribution bookkeeping;
5. internal guard comments can then be retained until hydration is safely committed or removed while converting to an in-memory Range.

This avoids content-only matching and its identical-node provenance impossibility.

### Empty content

Empty DSIH naturally renders adjacent start/end guards.

The pair still supplies an exact logical slot, solving the zero-node hydration problem.

After hydration commits, the end position can become the same collapsed right-edge live Range used by client-created contributions.

## Boundary failure cleanup

For a boundary-local body fallback whose DSIH range lives inside the boundary stream:

- the outer cleanup walker sees the opaque start guard;
- it skips protocol interpretation inside the opaque range;
- it removes the guarded opaque payload as part of deleting the failed boundary.

The stale preamble-content bug disappears because DSIH no longer escaped into root `bodyChunks`.

Body attributes remain outside the boundary on the persistent singleton, so the inline `body:T` candidate marker uses the adopted body-owner token to decide whether this boundary actually has authority to clear those properties.

## Adoption authority

This design restores the strongest part of the original Suspense-anywhere protocol without giving up early inline markers.

The inline marker means:

```text
boundary candidate token = T
```

The adopted preamble marker means:

```text
actual document body owner token = T
```

Only equality grants property cleanup authority.

A boundary-local body whose `bodyChunks` lost `hoistPreambleState()` adoption can still have its inline candidate marker and child segment, but no matching adopted body-owner token exists; singleton property cleanup is skipped.

This resolves the source-level authority mismatch found in the 2025 inline-marker optimization if that losing case is reachable.

## Client contribution conversion

After successful hydration, remove or retire the server guard comments and convert to the client body contribution representation:

- right-edge live Range for slot;
- ownership semantics according to the policy below;
- renderer bookkeeping keyed to the HostSingleton Fiber/alternate pair.

Fresh client writes use the same representation without serialized comments.

This lets subsequent opaque -> opaque, opaque -> managed, Activity hide/reappear, and stale-owner handling share one client mechanism.

## Remaining hard policy: nodes inserted inside the guarded range before hydration

The guards identify a contiguous server slot, not exact parser-origin identity for every node inside it after arbitrary external mutation.

If third-party code inserts a node between the guards before hydration, React cannot tell from passive DOM state whether that node came from server DSIH or outside code.

Therefore the protocol still requires the separate policy decision already recorded:

### Strong outside-node policy

Preserve third-party nodes even when inserted inside the opaque range.

This requires stronger early runtime/parser provenance than passive guards.

### Opaque-slot policy

Treat the guarded range like ordinary `innerHTML` ownership. Outside nodes inserted inside the range may be removed by later React replacement; nodes outside the guards are preserved.

Passive guarded ranges are sufficient.

Do not hide this policy choice inside the implementation.

## Malformed marker behavior

Before source work, specify fail-safe behavior for:

- missing end guard;
- duplicate/corrupted token;
- moved start/end comments;
- end guard outside the current boundary;
- outside code deleting one guard;
- nested guarded contributions if ever permitted.

The cleanup scanner should locate/validate the matching end guard before granting special opaque parsing behavior. Avoid partially interpreting raw DSIH as React control comments after a damaged start marker.

## Head/html exclusion

This protocol is body-specific.

- `head` has independent Hoistable/resource ownership.
- `html` has persistent document/head/body identity constraints.

Do not generalize the guarded range merely for singleton symmetry.

## Relationship to current experiments

- PR 34: direct unguarded boundary-stream DSIH remains **rejected**; its failure motivates opaque guards.
- PR 48: proves/targets root body placement but remains **partial** because it lacks text/provenance guards.
- PR 32: client placement prototype remains **partial**; server guards would hydrate into the stronger node/Range client model rather than its current insert-before-retire implementation.
- PR 29: property descriptor/adoption research can use the body-owner token side of this protocol.

## Disposition

**LEADING SERVER PROTOCOL DESIGN. RESEARCH BEFORE SOURCE IMPLEMENTATION.**

This is the first design found that addresses body order, text isolation, raw-comment collisions, boundary cleanup, adoption authority, empty content, and hydration slot provenance in one coherent mechanism.

The strong-vs-opaque-slot outside-node policy remains the principal unresolved contract question.

## Evidence class

Synthesis from current Fizz/Fiber source, public Suspense-anywhere history/tests, rejected PR 34/48 experiments, DOM hydration/provenance counterexamples, and client Range research. No public upstream interaction performed.
