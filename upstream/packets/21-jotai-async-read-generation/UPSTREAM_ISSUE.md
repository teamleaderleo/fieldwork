# Upstream discussion draft — asynchronous JSON reads can replace newer cached identity

Draft status: `not applicable — direct pull request preferred after clean materialization; optional discussion text retained`  
Public interaction authorized: `no`

---

## Summary

`createJSONStorage()` reuses parsed values when serialized JSON is unchanged. With an asynchronous string storage backend and a per-key parsed-value cache, an older read can settle after a newer read and replace the cached identity selected by the newer operation. A read that began before removal can also settle after removal and repopulate the cache.

This affects shared cache identity rather than the value returned to the initiating caller. Each caller can still receive its own backend result, while later reads observe identity chosen by stale completion order.

## Reproduction

1. Create one asynchronous string storage adapter whose reads can be resolved manually.
2. Start two reads for the same key.
3. Resolve the newer read first with value B.
4. Resolve the older read second with value A.
5. Read B again and compare object identity with the first B result.

Minimal outline:

```ts
const older = storage.getItem('key', fallbackA)
const newer = storage.getItem('key', fallbackB)

resolveNewer(JSON.stringify({ value: 'B' }))
const firstB = await newer

resolveOlder(JSON.stringify({ value: 'A' }))
await older

const secondB = await storage.getItem('key', fallbackC)
expect(secondB).toBe(firstB)
```

The same pattern can cross completed removal: start a read, await removal, resolve the old read, restore identical JSON, and compare restored identity with the stale result.

## Observed behavior

On the characterized source stack, the final identity comparison fails: the older completion replaces shared cache authority. A pre-removal read can also repopulate identity after removal settlement.

The focused characterization ran on Ubuntu with Node 22, 24, and 26.

## Expected behavior

For one key, only the latest initiated read or completed removal invalidation should be allowed to change shared parsed identity. Older callers should still settle normally, subject to the existing same-string identity reuse behavior.

## Current source observation

Each asynchronous read creates a parse closure. When its backend promise settles, that closure can update or delete the adapter-local cache. The cache has no ordering token that distinguishes a current read from a stale one.

## Candidate direction

Keep a monotonically increasing generation for each key:

- advance it when a read starts;
- let valid and malformed completions update cache state only when their captured generation remains current;
- advance it when removal invalidation settles.

This keeps the public API and stored JSON format unchanged.

## Compatibility and risks

- one additional adapter-local map entry per observed key;
- write and subscription-event ordering remain separate questions;
- a rejected newer read advances authority, leaves prior cache identity unchanged, and keeps the rejection caller-visible;
- equal serialized bytes may continue to reuse current cached object identity.

## Evidence limits

- focused Node execution only;
- no claim about application frequency or production impact;
- complete repository build and test gates remain pending on a direct source branch.

## Versions and environment

- project commit: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- platform: Ubuntu 24.04
- runtimes: Node 22, 24, and 26
- storage: deterministic deferred asynchronous string storage fixture

## Additional context

The parsed identity cache was introduced to preserve same-key identity during mount and subscription setup. The proposed generation fence preserves that behavior while ordering shared cache publication for asynchronous reads.

---

## Filing checklist

- [ ] Repeat the current upstream discussion, issue, and pull-request search immediately before filing.
- [ ] Reproduce on the final direct source base.
- [ ] Keep impact and prevalence wording within the focused evidence.
- [ ] Remove internal research links and receipts.
- [ ] Follow the current bug-discussion policy if maintainers prefer discussion before a pull request.
- [ ] Check the current AI-disclosure policy.
- [ ] Record exact user authorization before any public interaction.
