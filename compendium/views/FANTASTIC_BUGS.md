# Fantastic Bugs and How to Find Them

## In simple words

This is a reader-facing view over the first Fieldwork compendium seed. It is not a second source of truth: each species links conceptually to structured entries and those entries link back to the concrete cases.

The useful question is rarely “what category does this bug belong to?” It is closer to:

> **What relationship between ownership, visibility, completion, cleanup, identity, generation, and uncertainty has become false?**

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

See `ambiguous-external-outcome`, `remote-effect-certainty`, `retryability`, and `reconciliation`.

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

See `cleanup-owner-not-transferred`, `resource-has-one-cleanup-owner`, and `ownership`.

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

See `proxy-signal-for-authoritative-state`, `authoritative-state-gates-next-transition`, and `authoritative-state`.

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

## 8. Stale generation publishes after replacement

**Shape**

```text
generation A starts
→ generation B supersedes A
→ B becomes current
→ A finishes last
→ A republishes stale authority
```

**Ask**

- What identity distinguishes generations?
- Which event makes one accepted current?
- Can older callbacks still reach the shared publisher?
- Do old in-flight operations need captured authority without global publication authority?

**Typical repairs**

```text
quiesce predecessor → start successor
```

or:

```text
monotonic generation ticket
→ publish only if still current
```

See `stale-generation-publication`, `only-current-generation-may-publish`, `generation`, and `fence-publication-by-generation`.

## 9. Shared terminal operation becomes its own dependency

**Shape**

```text
owner terminal promise P waits for child
→ child crosses async boundary
→ child calls same owner terminal operation
→ child receives P
→ child waits for P
→ P waits for child
```

**Ask**

- Which callbacks are awaited by the shared terminal operation?
- Can they asynchronously reenter the same owner?
- How do we distinguish callback ancestry from legitimate concurrent joiners?
- If a timeout breaks the cycle, who owns unfinished cleanup afterward?

See `shared-terminal-operation-self-dependency` and `operation-owner`.

## 10. Fanout iterates live membership

**Shape**

```text
opening set = [A, B, C]
→ invoke A
→ A removes B
→ live iteration skips B
```

**Ask**

- Is the contract opening membership or continuously live membership?
- Can callbacks mutate the child set synchronously?
- Are removals meant to affect this operation or only future ones?

**Typical repair**

```text
snapshot opening membership
→ invoke snapshot
→ mutations affect future operations
```

See `fanout-iterates-live-membership` and `snapshot-opening-membership`.

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

validated identity becomes stale after a valid check
    ≠
normalization destroys identity before the check

stale generation publishes globally
    ≠
old in-flight operation legitimately finishes under captured old authority

shared terminal promise
    ≠
self-dependency merely because multiple callers share it
```

Those separations are part of the product. A knowledge base that makes every bug look like one familiar pattern is less useful than the original case studies.
