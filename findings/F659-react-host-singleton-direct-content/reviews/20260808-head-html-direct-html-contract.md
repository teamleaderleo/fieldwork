# HostSingleton DSIH contract — body versus head/html

## Question

Should a direct-content repair preserve equivalent `dangerouslySetInnerHTML` semantics for all three DOM HostSingleton types (`html`, `head`, `body`), or is `body` the only singleton with a currently defensible repair contract?

## Conclusion

**Treat `body` DSIH as the explicit tested repair target. Treat `head` and `html` DSIH as unresolved contract contradictions, not parity requirements.**

This does not mean React can remove or reject head/html DSIH immediately. It means Fieldwork should stop using generic singleton parity as a design requirement for the body repair.

## Original HostSingleton contract

The original public HostSingleton implementation describes the feature as a response to interoperability problems with third-party scripts, browser extensions, and style/resource placement.

Its explicit react-dom constraints include:

- `document.documentElement`, `document.head`, and `document.body` are persistent instances;
- none of those three instances are unmounted;
- none changes referential identity;
- head and body must not reposition/reorder/otherwise alter placement of style-related nodes outside React.

The original singleton test suite exercises persistent identity, resource/style retention, managed children, hydration, and text children. It does not establish a dedicated DSIH contract for head/html/body.

## Later DSIH coverage

The 2026 singleton release-cleanup change introduced the dedicated DSIH lifecycle tests now present in the public singleton suite.

Every one of those DSIH regressions uses **`body`**:

- release of a body with DSIH;
- wrapper / `__html` becoming undefined;
- body direct HTML -> direct HTML;
- body managed children -> direct HTML;
- body direct HTML -> managed children.

No corresponding dedicated `head` or `html` DSIH regression was added there.

This does not prove head/html DSIH is unsupported, but it does establish a materially stronger tested compatibility commitment for body.

## Why generic head DSIH contradicts the singleton goal

The ordinary DOM prop path implements a non-null `dangerouslySetInnerHTML.__html` by assigning `element.innerHTML`.

For the persistent `head`, that is whole-child-list replacement.

But `document.head` is also the physical home of React Hoistables/resources and third-party style/script/link nodes that are deliberately retained by singleton/resource cleanup paths.

A generic `head.innerHTML = ...` operation can remove those nodes regardless of who owns them, including stable React resource Fibers that receive no new Placement after the wipe.

That conflicts with the original HostSingleton constraint that head must preserve style-related outside placement.

## Why generic html DSIH contradicts an even harder invariant

For the persistent `document.documentElement`, assigning `innerHTML` replaces its child list.

The browser's document model represents `head` and `body` as children of the document element. A documentElement-level whole-child-list replacement can therefore remove and recreate `document.head` / `document.body`.

That directly conflicts with the explicit HostSingleton invariant that all three singleton DOM instances retain referential identity.

This is stronger than the ordinary outside-child ownership question: a successful generic html DSIH write can destroy the very persistent singleton instances the feature promises to keep stable.

## Server asymmetry does not repair the client contract

Fizz's singleton serializer generically accepts DSIH for `html`, `head`, and `body`, because all three use `pushStartSingletonElement`.

That means server output can represent these values. It does not make the current client whole-node writer compatible with HostSingleton identity/resource invariants.

A complete head/html policy therefore has to choose one of the following families:

1. **document-aware singleton writer** that preserves persistent identities / protected resource ownership while applying raw markup;
2. **explicit restriction / warning / rejection** for DSIH on singleton types whose whole-node semantics cannot honor HostSingleton invariants;
3. another carefully specified compatibility mode with equivalent guarantees.

Fieldwork currently has no small source candidate for any of these.

## Compatibility evidence

Read-only searches found no dedicated public React regression asserting `<head dangerouslySetInnerHTML>` or `<html dangerouslySetInnerHTML>` lifecycle behavior comparable to the body tests.

Historical/public issue search also did not surface a clear active compatibility owner for whole-head or whole-html DSIH. Many DSIH uses around document markup involve nested `script`, `style`, `noscript`, or body content rather than assigning raw HTML to the singleton element itself.

Absence of tests/search hits is not proof that applications do not depend on it, so changing public behavior still requires an explicit compatibility decision.

## Fieldwork disposition

### Body

**REPAIR / CONTRACT ACTIVE.**

Body DSIH has explicit current regression coverage and is the correct target for the placement/provenance research.

### Head

**CONTRACT HOLD.**

Do not promote generic head reset/cleanup. Any repair must account for Hoistables/resources and third-party head state.

### Html

**CONTRACT HOLD / HARD IDENTITY CONFLICT.**

Do not write a release/update-only patch that pretends generic documentElement DSIH is safe. The initial/client writer itself can violate persistent head/body identity.

## Consequence for existing experiments

- PR 27 and PR 32 should remain body-specific.
- PR 24's null/undefined-wrapper release fix can still include html as a false-cleanup case, because null/undefined `__html` performs no write at all; preventing a bogus release clear protects identity without endorsing non-null html DSIH.
- Head direct-content tests remain adversarial contract evidence, not acceptance requirements for the body candidate.

## Evidence class

- original invariants: public PR/source history read;
- body DSIH commitment: public test/history read;
- head/html contradiction: source/DOM consequence analysis;
- compatibility restriction decision: unresolved product-policy question;
- public upstream contact performed: none.
