## In simple words

The second review found an existing React design lineage that is directly relevant to opaque HostSingleton child ownership: the original HostSingleton implementation had an **insertion edge** specifically so React-managed children could coexist with non-React nodes in persistent `head` and `body`, and current Fizz already emits singleton **preamble contribution markers** so the client can identify which persistent singleton a server boundary contributed to.

Neither mechanism currently identifies the DOM children produced by `dangerouslySetInnerHTML`. Together, however, they suggest a narrower body-only research direction: represent one opaque body contribution as an owned DOM range rather than treating the entire persistent body child list as owned.

This note is research only. It does not reopen the rejected generic `ContentReset` cleanup and does not propose a product patch yet.

## Boundary

- React source baseline for mechanism review: `ec61f187fe39b0aa8ec6b508f2553b2047dc30cc`.
- Public React main subsequently advanced to `2042572329425f9ebf35ae6287ea5bab72b2c497` through unrelated Fizz browser-bailout plumbing; the client ownership paths discussed here are source-equivalent for this review.
- Public upstream contact authorized/performed: false / false.
- Existing broad direct-content candidate: HOLD.
- `head`, `html`, and Activity ownership remain separate research lanes.

## Historical insertion edge

The original HostSingleton design explicitly called out an insertion edge for persistent `head` and `body`.

Its purpose was to let non-React nodes remain siblings of React-managed Placement effects without React reordering or repositioning those outside nodes. The early implementation scanned the persistent singleton's children, used DOM-node-to-Fiber ownership to find a safe insertion boundary, and used that edge when no ordinary React host sibling existed.

The current singleton test suite still contains a disabled regression named roughly "maintain insertions in head and body between tree-adjacent Nodes" with a comment saying to revisit it if insertion-edge support is reintroduced. That test inserts stylesheet nodes before and after React-managed nodes and expects the outside nodes to retain their relative locations while React children update or disappear.

The long persistent-singleton test also still says that a future server-emitted insertion edge could make fresh client rendering resilient to interstitial placement after server rendering.

### What the old edge did and did not solve

The edge solved **where React-managed child Placement belongs relative to outside nodes**.

It did not provide ownership for opaque children produced by `innerHTML`. Those nodes have no HostComponent/HostText Fibers, so the DOM-to-Fiber ownership scan cannot tell them apart from outside DOM nodes.

Decision: retain insertion-edge semantics as a placement primitive, not as opaque-content provenance by itself.

## Current ownership primitives are insufficient for opaque children

`ReactDOMComponentTree` currently knows whether a DOM node is React-owned when it has a mapped Fiber or a Hoistable marker. Normal hydrated HostComponent/HostText/HostHoistable nodes can therefore acquire explicit ownership.

Children created by `dangerouslySetInnerHTML` have neither child Fibers nor Hoistable markers. A style node inserted by an outside script has neither as well.

Therefore `isOwnedInstance()` cannot distinguish:

- a top-level `<style>` created by React's opaque HTML write;
- a top-level `<style>` inserted later by an extension or third-party script.

Adding a client-only expando to nodes created by a client `innerHTML` write could identify those client-created nodes, but it does not solve hydration because the server-created nodes exist before the client runtime binds the singleton.

## Hydration does not recover opaque child provenance today

Normal matching hydration can bind retained style/link DOM nodes to child Fibers. The existing singleton lifecycle test demonstrates this: after matching hydration, exact retained style/link node identities are associated with the hydrated tree and final unmount removes them as React-owned children.

`dangerouslySetInnerHTML` has no equivalent child hydration path.

Current hydration behavior:

- `hydrateProperties()` performs host setup and text-child validation but does not traverse or bind opaque HTML children;
- development hydration diagnostics can compare `domElement.innerHTML` against normalized `__html` and report a mismatch;
- there is no child Fiber population for the nodes represented by `__html`.

So markerless hydration cannot later answer which exact body child nodes came from the server-rendered opaque contribution once outside nodes coexist with it.

Decision: a complete opaque-child ownership design needs an explicit hydration protocol or an equally durable representation.

## Existing Fizz singleton contribution protocol

Fizz already has a server-to-client singleton ownership concept.

For singleton preamble contributions inside Suspense, Fizz can emit comment markers equivalent to:

- `<!--html-->`
- `<!--head-->`
- `<!--body-->`

The client recognizes these markers when clearing dehydrated boundaries and redirects cleanup to the persistent singleton.

Current client code contains an explicit ownership TODO in `clearSingletonPreambleContribution()`: the marker tells the client **which singleton** was contributed to, but it does not carry enough contributed-property information to distinguish React-owned attributes from imperative/third-party attributes. The current edge case therefore clears every attribute, and the TODO proposes adding contributed properties to the marker.

This matters because opaque child ownership has the same family of problem at child-list level: singleton identity is known, contribution provenance is not.

Decision: investigate extending the existing singleton-contribution protocol before inventing an unrelated ownership channel.

## Body-only opaque range hypothesis

A plausible body-only model is to treat one `dangerouslySetInnerHTML` contribution as an explicit DOM range.

Conceptually:

1. acquire or update body opaque content inside an owned start/end boundary;
2. nodes outside that boundary remain outside the Fiber's child-content authority;
3. direct-HTML -> direct-HTML replaces only nodes inside the owned range;
4. direct-HTML -> managed children removes the old range contents before Placement, then uses a stable boundary as the insertion edge;
5. release removes only the owned range;
6. `__html: ''` still has an explicit empty owned range, so ownership does not depend on there being a produced child node;
7. a `<style>` originating inside React's opaque HTML disappears with the range, while an outside `<style>` appended outside the range survives.

For client-only writes the range could be retained in renderer-owned DOM bookkeeping. For hydration, the server output would need to make the range recoverable.

### Why BODY is the first viable target

Body already has simpler content semantics:

- string/number/bigint children are Fiber-managed rather than direct `textContent` writes;
- body is not the physical home of HostHoistable resources in the same way head is;
- the existing direct-content failure controls are body-centered;
- the original insertion-stability contract explicitly treats body as a persistent container that may contain outside style-related nodes.

This does not make a body range complete yet, but it isolates fewer independent owners than head.

## Hard cases the range design must answer before source work

### Initial client acquisition

If body already contains outside style-related nodes, replacing `body.innerHTML` still destroys them before a range exists.

A complete client acquisition path therefore needs to insert the opaque contribution at a defined insertion edge instead of assigning the whole persistent body's `innerHTML`.

The historical insertion-edge semantics are directly relevant here.

### Managed children -> opaque content

Deletion effects remove the old React-managed children, then the opaque contribution needs a precise insertion location relative to retained outside nodes.

Again, a persistent insertion edge or owned boundary is required; whole-body `innerHTML` is incompatible with the existing preservation contract.

### Hydration

Fizz must make the opaque range recoverable without turning the raw HTML into child Fibers.

Questions:

- Can comment sentinels safely bracket raw body HTML through normal render, streaming, prerender/resume, and Suspense preamble contributions?
- Would the HTML parser move or discard such markers in any supported body cases?
- How should development `dangerouslySetInnerHTML` hydration diagnostics compare only the owned range rather than the singleton's full `innerHTML` once outside nodes coexist?
- How is an empty opaque range represented?

### Owner replacement / keyed singleton replacement

The range must belong to a specific HostSingleton Fiber ownership epoch. A keyed replacement must retire the previous owner's range before the next owner writes into the same persistent body.

### Activity / Offscreen

A range can help an opaque hidden owner retain or retire its own contribution, but it does not solve hidden **managed** descendant Placement/deletion. Activity remains a separate lane.

## Why HEAD stays out of this experiment

`head` is the physical destination for HostHoistables/resources whose Fibers may live elsewhere.

Any head opaque range would need every resource/hoistable insertion path to understand whether it may cross or enter that range. A generic comment range can otherwise accidentally capture separately owned resources or put new resources inside an opaque contribution's ownership boundary.

The existing `clearHead` behavior and stable-Hoistable counterexample already prove that whole-head ownership is invalid.

Decision: do not generalize the body range experiment to head.

## Why HTML stays out

`document.documentElement` has the stronger persistent-document identity contract. Both textual content and dangerous HTML can destroy or replace the `head` / `body` child topology.

A child range inside `html` does not by itself answer whether opaque documentElement content is a supported operation.

Decision: keep html in contract research.

## Rejected alternatives retained

The following directions remain rejected unless new evidence changes their premises:

1. **Generic `textContent = ''` reset/release.** It erases later outside state and stable head Hoistables.
2. **Predicate-as-provenance.** `children == null && shouldSetTextContent(...)` identifies render mode, not current DOM child ownership.
3. **Preserve all style/script/stylesheet tags.** It also preserves those tags when they originated inside React-owned dangerous HTML.
4. **Client-only per-node marking as the whole solution.** It cannot recover server/hydration provenance.
5. **Head/body shared implementation.** Head has independent Hoistable/resource owners and needs separate semantics.
6. **Small Activity update/release guards as completion.** Hidden descendant Placement/deletion and reappearance restoration remain unresolved.
7. **Blanket prohibition of body dangerous HTML as a small repair.** Current tests exercise body direct-HTML updates and managed -> opaque transitions as supported behavior; changing that contract is a larger compatibility decision.

## Next executable contract work

Before implementing the range, add verifier-only body controls for:

- initial client opaque acquisition with an existing outside style node;
- direct-HTML -> direct-HTML update preserving that exact outside node;
- direct-HTML -> managed children preserving it;
- managed children -> direct HTML preserving outside-node ordering;
- React-owned `<style>` inside opaque HTML being removed when the range retires;
- empty opaque HTML retaining a usable ownership boundary;
- server-rendered opaque HTML + an outside style inserted before hydration, followed by transition/release that removes only React opaque content;
- outside stylesheet nodes before and after the React contribution retaining relative order.

If these controls can be stated coherently across client render and hydration, the next source experiment should be a body-only range writer/retirer with an insertion-edge primitive. If the hydration controls cannot be expressed without ambiguous provenance, the protocol needs to be designed first.

## Current decision

**RESEARCH / DEFINE BODY RANGE CONTRACT.**

The original insertion edge and current Fizz preamble markers provide existing React concepts to build on. They materially improve the design direction, but neither currently supplies opaque child ownership. Keep broad cleanup promotion blocked, keep the unset-`__html` release repair independent, and pressure-test a body-only owned-range contract before writing product code.