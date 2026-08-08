# React HostSingleton — current public main revalidation

## Scope

Read-only recheck against public `react/react` at `2042572329425f9ebf35ae6287ea5bab72b2c497` after the broader review had been developed against owned-fork baseline `ec61f187fe39b0aa8ec6b508f2553b2047dc30cc`.

No public upstream interaction was performed.

## Result

The load-bearing source facts used by the current Fieldwork conclusions remain present on current public main.

### Release cleanup

`packages/react-dom-bindings/src/client/ReactFiberConfigDOM.js`

`releaseSingletonInstance(instance, type, props)` still:

1. clears singleton properties represented by the releasing Fiber;
2. checks only whether `props.dangerouslySetInnerHTML != null`;
3. assigns `instance.textContent = ''` for that wrapper-present case.

Therefore a wrapper such as `{__html: null}` or `{__html: undefined}` still receives whole-child-list cleanup authority even though the direct-HTML setter performs no child write for a null/undefined `__html` value.

The source TODO about ordinary HostSingleton updates failing to clear stale DSIH also remains.

### Preamble ownership

The same file still defines `clearSingletonPreambleContribution(instance)` as whole-attribute removal because the marker carries only singleton identity and no contributed-property ownership. The TODO to include contributed properties remains.

### Fizz body preamble DSIH

`packages/react-dom-bindings/src/server/ReactFizzConfigDOM.js` still:

- pushes `<!--body-->` to the boundary target when a body comes from a non-root `preambleState`;
- serializes the body start tag into `preamble.bodyChunks`;
- calls `pushStartSingletonElement(preamble.bodyChunks, props, 'body', ...)`;
- has `pushStartSingletonElement` write `dangerouslySetInnerHTML` through `pushInnerHTML(target, ...)` into that same singleton preamble buffer.

So the distinction found in the fork baseline remains current: managed body children returned by `pushStartSingletonElement` stay in normal boundary rendering, while body DSIH bytes are emitted into the root-adopted singleton preamble buffer.

## Consequences

- The narrow unset-wrapper release finding remains live on public main.
- The preamble marker attribute/style ownership gap remains live on public main.
- The boundary-contributed body DSIH stream/provenance finding remains live on public main.
- No public-main change discovered by this recheck invalidates PR 24, PR 29, PR 32, or PR 34 as research/verification lanes.

## Evidence class

Source-read revalidation only. This does not promote any queued experiment or verifier to executed/pass status.
