## In simple words

Vercel AI kept moving while this scout was executing. Two new harness commits landed after the original pin. One OpenCode authorization concern reduces to a negative result because its relay authorizer already consumes grants exactly once and handles duplicate requests as a counted queue. A Pi inline-extension failure boundary remains under target-native characterization.

Current public head sampled here: `ecd916953720da85a278ff7abb80db46d5545c7b`.

## OpenCode raw-input relay authorization — negative result

Commit: `ecd916953720da85a278ff7abb80db46d5545c7b`  
Change: authorize host-tool relay calls using raw tool input rather than provider-metadata-enriched input.

The change initially raises an identity question because relay authorization is keyed by:

```text
toolName + canonical JSON(input)
```

rather than by the runtime `callID`.

Source inspection of `packages/harness-opencode/src/bridge/tool-relay-auth.ts` shows the key is used as a consumable authorization count rather than a reusable boolean grant:

- one stored authorization is removed on one matching request;
- a second identical request needs another authorization;
- requests that arrive before runtime authorization are queued;
- identical pending requests are served FIFO, one authorization at a time;
- different inputs do not cross-authorize;
- canonical object-key ordering avoids accidental mismatch;
- grants and pending requests expire under a bounded TTL;
- `close()` clears stored grants and rejects pending requests.

The target's own `tool-relay-auth.test.ts` explicitly covers exact-once consumption, duplicate pending FIFO behavior, mismatched calls, canonical property ordering, expiry, and close cleanup.

### Disposition

`NEGATIVE RESULT / STOP`

The raw-input repair does not expose an obvious replay or concurrent-identical-call authorization hole under the inspected mechanism. A new campaign would need evidence that the emitter can produce fewer authorization events than relay requests for one logical call family, or that canonicalized raw inputs collapse calls whose side-effect authority must remain distinct.

## Pi inline extension runtime — active characterization

Introducing commit: `c20a3153ad58ecc42a1c97442a6dafba60821e73`  
Current source read at: `ecd916953720da85a278ff7abb80db46d5545c7b`  
Canonical target probe: `teamleaderleo/ai#65`  
Execution carrier: `teamleaderleo/ai#66`

The new Pi adapter support intentionally:

- copies caller-supplied extension factories;
- preserves one active extension runtime across routine resource-only reloads;
- disposes an old Pi session before creating a fresh extension runtime during a genuine tool-set rebuild;
- reloads the shared resource loader after disposal so the replacement Pi session receives a fresh runtime.

The source leaves one failure question worth testing. On a rebuild with an existing Pi session:

```text
dispose old Pi session
  -> await resourceLoader.reload()
  -> create replacement AgentSession
```

If the reload fails after disposal, `piSession` is already cleared. A later retry enters the rebuild path without an existing session and therefore does not take the same explicit fresh-extension reload branch before `createAgentSession()`.

Whether that can reuse invalidated extension state depends on the exact `DefaultResourceLoader` failure semantics supplied by the Pi package currently resolved by Vercel's lockfile.

`teamleaderleo/ai#65` uses the real installed dependency. It performs one successful inline-factory reload, makes the next factory invocation fail, and records:

- exact resolved Pi package version;
- whether `reload()` resolves or rejects;
- whether the post-failure `getExtensions()` runtime is the same object as before;
- extension error counts and extension counts.

### Promotion gate

Promote only if the real pinned loader can leave the previous extension runtime visible after a failed replacement reload and a Vercel retry can feed that runtime into a new Pi session. If Pi replaces or invalidates the cached result safely, retain a negative result.

## Boundary

These are quiet source/owned-fork investigations. No third-party upstream mutation occurred.
