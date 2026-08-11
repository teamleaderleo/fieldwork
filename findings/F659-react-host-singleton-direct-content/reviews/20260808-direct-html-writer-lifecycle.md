## In simple words

The HostSingleton direct-content problem is larger than missing `ContentReset` bookkeeping. Client direct HTML is a whole-child-list write during singleton acquisition and during direct-HTML-to-direct-HTML updates too. A cleanup-only repair can therefore pass the existing transition tests while still deleting style/resource state that lives in the same persistent singleton outside the current Fiber's child ownership.

## Exact source path

Current React source pin: `ec61f187fe39b0aa8ec6b508f2553b2047dc30cc`.

### Acquisition

`acquireSingletonInstance(type, props, instance, fiber)` calls:

```text
setInitialProperties(instance, type, props)
precacheFiberNode(...)
updateFiberProps(...)
```

For non-null `dangerouslySetInnerHTML.__html`, the generic DOM property path assigns `instance.innerHTML`.

So an external style-related child already present in a persistent body/head can be removed on acquisition before any later release/reset logic is relevant.

### Direct HTML update

`commitHostUpdate` reaches `updateProperties`. When the old and new non-null `__html` values differ, the DOM property path assigns `instance.innerHTML = nextHtml`.

Therefore an external child inserted after the first direct-HTML write can be removed by a later direct-HTML-to-direct-HTML update even though no `ContentReset` transition occurs.

### Transition away / release

The current proposed repair handles these phases through generic text clearing. That has the same whole-child-list ownership problem demonstrated by the second-review external-style and head-hoistable regressions.

## Consequence

A repair that only changes:

- the render-time predicate;
- `ContentReset` ordering; and
- release cleanup

cannot establish persistent-singleton interoperability for opaque direct content across the complete lifecycle.

A complete policy must cover at least:

```text
cold/reacquire direct HTML write
→ direct HTML update
→ transition away
→ release
→ hydration handoff
```

and decide how React distinguishes its opaque contribution from style/resources or imperative nodes that share the persistent singleton.

## Obvious alternative rejected

Using the existing sparse container/head clearer as a generic answer is incomplete. It preserves scripts/styles/stylesheet links based on tag/category, but dangerous HTML itself may have supplied those exact tags. The paired body controls in the second-review verifier require an externally inserted `<style>` to survive while a `<style>` produced by React-owned dangerous HTML is removed.

That distinction requires provenance or a deliberate contract change; tag-based preservation cannot express it.

## Disposition

**HOLD cleanup-only source promotion.** Keep the predicate and commit-order findings as useful local mechanics, but treat opaque HostSingleton child ownership as a writer/lifecycle contract question until one design covers acquisition, update, transition, release, hydration, and external child coexistence.

Public upstream contact authorized/performed: false / false.