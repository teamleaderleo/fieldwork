## In simple words

Vercel AI kept moving while this scout was executing. Two new harness commits landed after the original pin. The OpenCode authorization concern reduces to a negative result because its relay authorizer already consumes grants exactly once and handles duplicate requests as a counted queue. The Pi inline-extension failure question also reduces to a negative result after reading the exact dependency release: each reload creates a fresh extension runtime, and inline factory failures are captured into that fresh result instead of preserving the disposed session's old runtime.

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

## Pi inline extension runtime — negative result

Introducing Vercel commit: `c20a3153ad58ecc42a1c97442a6dafba60821e73`  
Vercel source read at: `ecd916953720da85a278ff7abb80db46d5545c7b`  
Exact Pi dependency release inspected: `earendil-works/pi@v0.80.10`, release commit `8dc7883`  
Prepared owned probe: `teamleaderleo/ai#65`  
Prepared execution carrier: `teamleaderleo/ai#66`

The new Pi adapter support intentionally:

- copies caller-supplied extension factories;
- preserves one active extension runtime across routine resource-only reloads;
- disposes an old Pi session before creating a fresh extension runtime during a genuine tool-set rebuild;
- reloads the shared resource loader after disposal so the replacement Pi session receives a fresh runtime.

The source initially suggested one failure window:

```text
dispose old Pi session
  -> await resourceLoader.reload()
  -> create replacement AgentSession
```

If `reload()` could reject after disposal while leaving its previous cached extension runtime visible, a later Vercel retry could skip the explicit fresh-runtime reload branch and reuse stale extension state.

The exact Pi `v0.80.10` implementation reverses that premise.

### Exact dependency behavior

`DefaultResourceLoader.reload()` clears the extension cache after the first load, then calls the extension loading path. `loadExtensionsCached()` reaches `loadExtensionsInternal()` without an existing runtime argument, so every reload constructs a new `ExtensionRuntime` via `createExtensionRuntime()`.

Inline factories are then loaded against that new runtime. `DefaultResourceLoader.loadExtensionFactories()` catches each factory exception and appends a diagnostic entry to the result's `errors` array instead of rethrowing the factory failure.

After the extension pass, `reload()` assigns the newly produced `extensionsResult` to `this.extensionsResult`.

Therefore the disputed sequence is:

```text
dispose old Vercel Pi session
  -> Pi reload creates new extension runtime
  -> inline factory failure becomes new-result diagnostic
  -> Pi reload continues
  -> Vercel replacement session receives the new runtime/result
```

The old disposed session runtime is not the loader's retained result after this factory-failure class.

### Disposition

`NEGATIVE RESULT / STOP`

The stale-extension-runtime retry hypothesis is disproven for inline factory failures under the exact Pi dependency release. The prepared owned test and execution carrier are no longer needed as promotion evidence and should be retired.

Reopen only if a different Pi reload failure occurs *before* a new extension result is published and Vercel retries with a loader state whose runtime ownership remains ambiguous. Package resolution/settings failures before extension loading are a distinct boundary and were not established here.

## Boundary

These are quiet source/owned-fork investigations. No third-party upstream mutation occurred.
