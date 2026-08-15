# Fantastic Bugs and How to Find Them

## In simple words

This is a reader-facing view over the first Fieldwork compendium seed. It is not a second source of truth: each species links conceptually to structured entries and those entries link back to the concrete cases.

The useful question is rarely “what category does this bug belong to?” It is closer to:

> **What relationship between ownership, visibility, completion, cleanup, and uncertainty has become false?**

## 1. Publication before ownership

**Shape**

```text
object becomes reachable
→ ownership/reuse exclusion arrives later
→ interruption
→ live object can look reusable
```

**Ask**

- What makes the object reachable?
- What prevents another actor from claiming it?
- Which happens first?
- What if execution stops between them?

**Typical repair grammar**

```text
prepare → own → publish → retire
```

See `publication-before-ownership` and `ownership-before-publication`.

## 2. False success after incomplete work

**Shape**

```text
required work fails or is skipped
→ result surface forgets the missing work
→ SUCCESS / CLEAN / EMPTY
```

**Ask**

- What did the operation claim to select?
- Did every selected item reach a terminal result?
- Can “nothing existed” and “everything was skipped” produce the same machine result?
- Does a clean/current marker suppress recovery?

See `false-success-after-incomplete-work` and `success-implies-complete-selected-work`.

## 3. Ambiguous external outcome

**Shape**

```text
mutation dispatched
→ external side may commit
→ acknowledgement/result lost
→ local timeout/interruption
→ outcome unknown
```

**Ask**

- Was dispatch confirmed?
- What proves absence?
- What proves commit?
- Is there a stable operation identity or idempotency key?
- Can we reconcile before retry?

**Dangerous move**

```text
unknown → failed → retry
```

See `ambiguous-external-outcome` and `unknown-outcome-requires-reconciliation-before-retry`.

## 4. Cleanup owner not transferred

**Shape**

```text
creator allocates resource
→ work changes lifecycle owner
→ creator stops cleaning
→ successor never receives cleanup ownership
→ resource leaks
```

**Ask**

- Who created it?
- Who observes the event that makes cleanup legal?
- Where does cleanup ownership move?
- What happens if transfer fails?

See `cleanup-owner-not-transferred` and `resource-has-one-cleanup-owner`.

## 5. Cleanup replaces the selected outcome

**Shape**

```text
primary result R is complete
→ cleanup produces C
→ caller sees C instead of R
```

**Ask**

- When did the primary outcome become authoritative?
- Is cleanup part of the transaction or secondary work?
- Is precedence explicit or merely “last exception wins”?

See `cleanup-replaces-selected-outcome` and `selected-terminal-outcome-survives-cleanup`.

## 6. Proxy signal mistaken for authoritative state

**Shape**

```text
transition requested
→ correlated symptom appears
→ next lifecycle step starts
→ actual transition may still be settling
```

**Ask**

- Which component owns completion?
- What event/state does it emit?
- Can the proxy happen early?
- What is reused immediately afterward?

See `proxy-signal-for-authoritative-state` and `authoritative-state-gates-next-transition`.

## 7. Terminal authority leak

**Shape**

```text
operation becomes terminal
→ old producer remains authoritative
→ late read / callback / reconnect / mutation
```

**Ask**

- Where is terminal state selected?
- Which continuations can already be in flight?
- Do they check terminal/generation state before acting?
- Which producers can be cancelled, returned, or retired?

See `terminal-authority-leak` and `terminal-state-revokes-producer-authority`.

## A reusable hunting move

Many of these species become visible by writing a short execution trace and asking:

> **What if we stop right here?**

See `failure-window-interruption`.

## Important non-equivalences

The compendium should preserve these distinctions:

```text
ack before processing
    ≠
acknowledgement lost after mutation may have committed

cleanup chooses the wrong final result
    ≠
cleanup never settles, so the chosen result is never published

publication before ownership
    ≠
only recoverable predecessor discarded before a fallible handoff

same surface leak
    ≠
same lifecycle owner
```

Those separations are part of the product. A knowledge base that makes every bug look like one familiar pattern is less useful than the original case studies.
