## In simple words

The current direct-HTML repair has the right body transition ordering, but its cleanup still assumes that because React once wrote opaque content it owns every child present later. That fails for style-related nodes inserted outside React. The same whole-container clearing is also too broad for `head`, and the small Activity guards do not isolate descendant mutations from a visible owner of the same persistent singleton.

The current recommendation is to hold the direct-content cleanup candidate while preserving its useful predicate/order findings, keep `html` in contract research, and keep Activity ownership in research until hidden descendant mutation and reappearance restoration have a coherent answer.

## Review boundary

- Worker: GPT-5.6 Sol, independent second review
- React source revision: `teamleaderleo/react@ec61f187fe39b0aa8ec6b508f2553b2047dc30cc`
- Existing clean candidate reviewed: `repair/host-singleton-content-reset@ed2c1ade64d40761fade7998afe83be62d2d1239`
- Existing verifier reviewed: `verify/host-singleton-content-reset-head@a321472ef9799f6b5d161bc73042b1dd8a707640`
- Second-review verifier: `teamleaderleo/react` draft PR 22, branch `review/host-singleton-second-review`
- Claim scope: mechanism
- Public upstream contact authorized/performed: false / false

## Established source findings

### Body direct content

`updateHostSingleton` always reconciles `pendingProps.children`, and the child reconciler creates HostText Fibers for non-empty string, number, and bigint children. DOM `setProp` has a body-specific guard that avoids the ordinary direct `textContent` write for those values. This makes body text/number/bigint Fiber-owned and supports excluding them from opaque-direct-content cleanup.

For body, the useful render-time predicate is:

```js
props.children == null && shouldSetTextContent(type, props)
```

With current DOM semantics this identifies a non-null `dangerouslySetInnerHTML.__html` value while excluding Fiber-managed text children and unset `__html` wrappers.

The pre-child ordering is also correct in isolation: stale opaque HTML must be dealt with before replacement child Placement effects run.

### The predicate does not prove current DOM child ownership

The predicate proves that the Fiber supplied an opaque direct-content value. It does not identify which child DOM nodes currently belong to that write.

A HostSingleton exists specifically because its DOM node persists and can coexist with state inserted outside React. The original HostSingleton contract calls out preserving style-related nodes outside React, and current DOM container clearing has special logic that retains scripts, styles, and stylesheet links under persistent `html` / `head` / `body` containers.

Counterexample for body update:

1. React writes `<body dangerouslySetInnerHTML={{__html: '<div id="managed-old">old</div>'}} />`;
2. an external system appends a `<style>` node to the persistent body;
3. React transitions the body to managed children;
4. the refined candidate runs the generic singleton reset, assigning `body.textContent = ''`;
5. both the stale React HTML and the external style node are removed.

The same over-clear exists on release after an external style node is appended.

A sparse clearer is not automatically a complete repair: preserving all scripts/styles/stylesheet links would also preserve those same tag types when they came from React-owned dangerous HTML. A complete implementation needs an explicit ownership rule for opaque singleton content and later external insertions.

Decision: the proposed predicate is useful for identifying the previous render mode, but it is insufficient as the release/update cleanup authority by itself.

### Head is a shared physical container

`head` is the only DOM singleton placement scope and is also the physical destination for HostHoistables and resources whose Fibers can live elsewhere in the React tree.

React already has a specialized `clearHead` path that preserves marked hoistables, scripts, styles, and stylesheet links. The refined direct-content candidate instead reaches the generic singleton text reset, which assigns `head.textContent = ''` and removes every child.

Counterexample:

1. render `<head dangerouslySetInnerHTML={{__html: ''}} />`;
2. in a later commit, keep those head props and mount a stable hoisted `<meta>` elsewhere in the tree;
3. transition the head singleton to managed children while keeping the same hoistable Fiber;
4. the proposed pre-child head reset removes the hoistable DOM node;
5. the unchanged HostHoistable Fiber has no Placement effect that would restore it.

The same over-clear exists on releasing a dangerous-HTML head owner while separately owned head content remains live.

Decision: generic head reset/release is too broad.

### Head and html text children are not purely Fiber-owned

For `head` and `html`, generic DOM prop handling also calls `setTextContent` for string, number, and bigint children. Only `body` has the explicit guard that disables this direct text write.

Therefore the statement “HostSingleton text children are Fiber-managed” is complete for body and incomplete for head/html. `html` textual content can also destroy the persistent `head` and `body` nodes, so html string/number/bigint children belong with non-null html dangerous HTML in the persistent-document contract investigation.

### Activity guards are partial

The proposed `offscreenSubtreeWasHidden` guards repair two real ownership errors:

- a previously hidden singleton should not run a host update that mutates the currently visible owner and replaces the DOM node's Fiber/props association;
- deleting a singleton that was already released by the disappear phase should not release the shared node a second time.

They do not isolate descendant mutations. Already-hidden Offscreen trees still traverse mutation effects, and child Fibers with `Placement` still execute `commitHostPlacement`. Because body/html are not singleton placement scopes, a new managed child under a hidden body can be inserted into the live `document.body` currently owned by another visible singleton.

Counterexample:

1. Activity A owns an empty body;
2. A becomes hidden and releases the singleton;
3. visible owner B acquires the body with direct HTML;
4. while A remains hidden, A updates from no child to a new managed `<div>`;
5. the singleton host update can be suppressed by the guard, but the new child Placement still targets the shared body and mutates B's visible DOM.

The existing deeper reappearance case remains valid too: B can physically detach A's retained managed child using direct HTML, and A's reappearance has no ordinary Placement effect to restore that already-mounted Fiber's DOM node.

Decision: keep the two guards as useful research, not as a complete source candidate.

## Exact regressions retained in the second-review verifier

The second-review verifier adds three disposable pressure areas:

1. `preserves an external style when body leaves direct HTML` and the corresponding release case
   - apply the refined direct-content candidate;
   - insert a style node outside React after the direct-HTML write;
   - require stale React HTML to disappear while the external style node survives.

2. `preserves a stable hoistable when head leaves direct HTML`
   - applies the refined direct-content candidate;
   - keeps one HostHoistable Fiber stable across the head transition;
   - requires the exact hoistable DOM node to remain in `document.head`.

3. `does not place new managed children from an already hidden singleton owner`
   - applies the small Activity update/release guards plus the existing Activity ownership matrix;
   - keeps one visible direct-HTML body owner active;
   - adds a new child under the already-hidden owner;
   - requires the hidden child to stay out of the live body.

The verifier branch contains no product-source edits of its own.

## Recommended disposition

### Direct-content repair

**HOLD / REDESIGN CLEANUP AUTHORITY.** Retain these established pieces:

- body text/number/bigint should remain outside the opaque-direct-content predicate;
- unset/null `__html` wrappers do not establish direct-content ownership;
- opaque direct content must be retired before replacement child Placement.

The missing piece is child-level ownership on a persistent shared DOM singleton. Whole-node `textContent = ''` cleanup can erase later external state.

Required controls before a clean source candidate returns:

- direct HTML -> empty/element/string/number/bigint;
- hydrated direct HTML -> managed children;
- ordinary text -> children with an imperative sibling preserved;
- direct HTML -> children with an external style-related sibling preserved;
- release after direct HTML with an external style-related sibling preserved;
- unset/null `__html` release preserving external children;
- keyed replacement;
- explicit empty-HTML ownership contract.

### Head

HOLD. Any complete repair needs to distinguish the old head singleton's opaque contribution from separately owned hoistables/resources and third-party state. Generic `textContent = ''` is unacceptable.

### Html

HOLD / contract decision. Actual non-null dangerous HTML and textual children can conflict with persistent `documentElement` / `head` / `body` identity.

### Activity

HOLD / deeper ownership design. A complete answer must cover at least:

- hidden singleton host updates;
- repeated release;
- hidden descendant Placement/deletion;
- visible-owner replacement of hidden managed nodes;
- restoration/reconciliation on reappearance;
- current Fiber/props/event ownership of the persistent DOM node.

## Evidence classification

- source paths and control-flow conclusions: source-read;
- new pressure tests: target-test-prepared until the second-review workflow executes;
- existing verifier results are retained as prior evidence only and are not upgraded by this review.

## Decision

**HOLD / SPLIT.** The current direct-content candidate has correct local predicate/order ideas but lacks sufficient DOM child ownership for persistent singletons. Reject generic head cleanup, keep html and Activity as separate research lines, and require the body external-style discriminator before reviving a clean source candidate. No upstream interaction.