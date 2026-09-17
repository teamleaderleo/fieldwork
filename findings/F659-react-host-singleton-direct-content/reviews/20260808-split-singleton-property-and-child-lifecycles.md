# HostSingleton lifecycle split — properties versus body child contribution

## Core result

The leading body ownership model implies that current `releaseSingletonInstance()` conflates two different lifecycle domains:

1. **exclusive singleton state** on the persistent body node;
2. **this Fiber's child contribution** inside the shared body scope.

A complete repair should separate them.

## Exclusive singleton state

The persistent `document.body` itself has one current HostSingleton owner for:

- attributes;
- style properties applied to body;
- event props / current props mapping;
- refs;
- DOM -> HostSingleton Fiber association;
- other property-backed state.

Acquisition/release naturally belong to this exclusive lifecycle.

### Acquire

The currently visible/active owner applies its body properties and becomes the singleton DOM association.

### Release

When that owner disappears or is replaced, remove only state represented by that owner's singleton props and relinquish the body association.

No body child-list deletion should be implied merely by releasing exclusive singleton state.

## Child contribution lifecycle

Managed/opaque body content belongs to the body Fiber's **body-scope contribution slot**, not to the persistent body element globally.

Its lifecycle is mutation/content lifecycle:

- mount/place contribution;
- update/reorder/replace contribution;
- hide/unhide contribution under Activity/Offscreen;
- delete contribution when the owning Fiber is permanently deleted.

This is conceptually parallel to HostComponent children even though body is a persistent HostSingleton and opaque DSIH has no ordinary child Fibers.

## Why this matters for Activity

Current disappear layout effects call HostSingleton release when an Activity hides.

For managed body children, those descendant DOM nodes remain connected and are hidden by normal Offscreen traversal. Release affects the singleton properties only.

For current DSIH, however, `releaseSingletonInstance()` clears `instance.textContent`, deleting the hidden owner's child content entirely.

That asymmetry is the root of later detached/reappearance problems.

Under the split model:

1. hide Activity A;
2. A releases body attributes/events/current singleton association;
3. A's managed or opaque contribution remains connected and becomes hidden;
4. visible owner B acquires body properties and uses its own contribution slot;
5. on A reappearance, A reacquires body properties and unhides its existing contribution.

No whole-body child wipe or reconstruction is necessary.

## Permanent deletion

When a body HostSingleton Fiber is genuinely deleted:

### Managed contribution

Existing deletion traversal already removes its HostComponent/Text descendants.

After deletion, remove the Fiber's body slot Range/bookkeeping.

### Opaque contribution

A dedicated contribution deletion effect removes the opaque nodes owned by that Fiber, then drops its slot/provenance state.

This is where DSIH child cleanup belongs.

## Keyed replacement

The current reconciler eagerly releases a deleting HostSingleton because a keyed replacement can target the same persistent DOM instance later in the commit.

Under the split model:

- old singleton **properties** may still need eager release before the replacement acquires them;
- old child contribution deletion follows its own ordered mutation path;
- the replacement Fiber gets its own body slot / contribution position and later acquires exclusive body properties.

Do not use property release as a surrogate for child contribution deletion.

## Ordinary opaque update

DSIH -> DSIH does not release the singleton at all.

The contribution mutation path:

1. retains body slot;
2. retires old opaque owned nodes;
3. inserts replacement opaque fragment;
4. updates contribution provenance.

Body attributes/events remain with the same owner throughout.

## Opaque -> managed / managed -> opaque

These are also contribution transitions, not singleton release/acquire transitions.

The persistent body owner does not change. Only the content implementation inside that Fiber's slot changes.

This is another reason generic `ContentReset` / `releaseSingletonInstance` cleanup is the wrong abstraction for the full repair.

## Relationship to PR 24

PR 24 fixes a narrow current-architecture false cleanup:

`dangerouslySetInnerHTML={{__html: null/undefined}}` performed no direct child write, yet release treated wrapper presence as authority to clear all singleton children.

The refined PR 24 condition checks the actual direct-HTML write predicate (`__html != null`) and is still a valid small repair today.

In the eventual contribution architecture, even non-null DSIH child cleanup should migrate out of singleton property release and into contribution deletion.

So PR 24 is a current-source correctness fix, not the final lifecycle abstraction.

## Relationship to stale-owner guard

The stale-owner guard in PR 41 belongs exclusively to singleton **property** update/release authority.

A hidden Fiber that no longer owns body attributes/events should not mutate them.

Its child contribution may still legitimately update while hidden, provided placement is routed to that Fiber's own body slot and normal visibility rules apply.

This makes the split between property authority and contribution authority explicit and testable.

## Host config API direction

Long-term renderer APIs may become clearer if they reflect the split rather than adding more conditions to `releaseSingletonInstance`:

Conceptually:

```text
acquireSingletonProperties(...)
releaseSingletonProperties(...)

place/update/deleteSingletonContribution(...)
hide/unhideSingletonContribution(...)
```

Exact API naming/design is future work. The important point is lifecycle ownership, not the final function names.

## Head/html exclusion

This lifecycle decomposition is currently justified for **body child scope**.

Head has separate resource/Hoistable semantics; html has persistent document child identity constraints. Do not generalize contribution deletion APIs to them without separate contracts.

## Disposition

**LEADING LIFECYCLE MODEL.**

For body, acquisition/release should govern exclusive persistent-element state. Child content should have an independent contribution lifecycle that survives hide/reappear and is deleted only by contribution deletion/replacement.

This is one of the strongest simplifications produced by the review so far.
