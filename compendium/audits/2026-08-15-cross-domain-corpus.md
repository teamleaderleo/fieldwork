# Cross-domain corpus audit — 2026-08-15

## In simple words

This audit asks which recurring structures are already supported by genuinely different Fieldwork/Linux Fieldwork cases and which ones still need a second domain before they should be treated as mature generic species.

The goal is not to maximize the number of patterns. The useful result is a smaller set of abstractions whose **owner relationship survives translation**, plus explicit cases where similar vocabulary hides different failure grammar.

## Current cross-domain matrix

| Generic candidate | Representative cases | Current judgment | What transfers | What stays local |
|---|---|---|---|---|
| false success after incomplete work | Fieldwork #626; Linux Fieldwork #611; Linux cancellation note | mature | required work missing but status forgets incompleteness | audit selection policy, QCOW DIRTY semantics, CLI signal status |
| ambiguous external outcome | Fieldwork #83, #134, #384 | mature | effect may have happened while local evidence cannot classify terminal outcome | transport, mutation API, cancellation protocol, receipt shape |
| cleanup replaces selected outcome | Linux Fieldwork #297; Fieldwork #76, #882 | mature | authoritative primary result is replaced by later secondary cleanup/cancellation outcome | signal precedence, provider abort policy, response-body cancellation |
| validated identity goes stale before use | Fieldwork #406, #471; Linux Fieldwork #164 | supported | validated/selected identity is reused after authority/binding changes | descriptor/path mechanics, credential/account authority, durable cleanup marker |
| normalization erases semantic distinction | Fieldwork #225; Linux Fieldwork #28 | supported | normalizer removes distinctions needed by identity/policy | cache-key aliases versus archive member matching |
| terminal authority leak | Fieldwork #714, #127 | supported | operation is terminal while owned producer still publishes/schedules work | iterator reads, reconnect timers, stream bodies |
| cleanup owner not transferred | Fieldwork #319; related shutdown cases #149/#171 | supported | creator stops cleanup without successor owning the same resource lifetime | temp directory, shared async close task, irreversible client close semantics |
| proxy signal for authoritative state | Linux Fieldwork #423; comparison questions in Fieldwork #528 | candidate/supported boundary | correlated symptom is weaker than owner-issued completion | VM event monitor versus agent-runtime state owner |
| publication before ownership | Linux Fieldwork #609 | supported Linux-derived generic candidate | reachability becomes authoritative before reuse-prevention ownership | current concrete proof is storage/refcount-specific; needs unrelated second domain |

## Mature family: false success after incomplete work

The strongest transfer is not “exit code bugs.” It is:

```text
operation claims set S
→ some required member/prerequisite never reaches valid terminal result
→ result is computed only from surviving subset S'
→ success surface does not encode S - S'
```

Linux Fieldwork #611 uses a clean marker rather than an aggregate exit code, but the same truthfulness invariant holds: a marker certifies work that did not complete.

A useful specialization remains `cancellation-falls-through-to-success`: the incomplete work is caused by interruption and local cleanup is complete, which makes the accidental zero especially deceptive.

## Mature family: ambiguous external outcome

The stable core is epistemic rather than transport-specific:

```text
a consequential effect may already exist
+
local observer lacks evidence to classify it
```

The key negative rule is:

```text
unknown != absent
```

This family should retrieve idempotency, stable operation identity, reconciliation, and remote-effect certainty. It should *not* automatically retrieve premature queue acknowledgement as though moving ACK later solves both problems.

## Mature family: cleanup result precedence

Linux process/signal handling and async JavaScript/provider cleanup preserve one transferable question:

> When did the primary outcome become authoritative, and which later failures are merely cleanup consequences?

The important counterexample is a cleanup operation that is itself the final required commit step. In that contract, cleanup failure legitimately changes success.

## Supported family: validated identity goes stale before use

This family survived a useful three-way comparison:

```text
pathname containment
account/credential authority
persisted cleanup markers
```

The common structure is not “TOCTOU” in the narrow filesystem sense. It is:

```text
proof P binds token T to object/authority X under context C
→ C or binding changes
→ action dereferences T again
→ P no longer proves the identity being acted on
```

The invariant transfers cleanly. The repair mechanism usually does not.

This is exactly the kind of entry that benefits from facets rather than one domain parent.

## Supported family: normalization erases semantic distinction

Two very different implementation mistakes preserve the same error:

```text
normalization happens before the decision that needs original distinctions
```

One case loses dot components before containment/cache-key validation; another uses character-set stripping where exact archive-prefix removal was intended.

This family should keep a strong contract-relative limit: canonicalization is correct when the protocol explicitly defines the collapsed forms as equivalent.

## Supported family: terminal authority leak

The common structure is:

```text
terminal state selected
→ producer/continuation owned by old operation still has mutation/scheduling authority
```

A mature version should add at least one case outside stream/reconnect runtimes—possibly a stale worker generation or background controller—before widening terminology further.

## Candidate family: publication before ownership

The Linux QCOW case is unusually strong and already yields a reusable invariant:

```text
Owned(x) before Published(x)
```

But a generic Fieldwork species should remain below `mature` until an unrelated domain demonstrates the same **reachability versus reuse/claim authority** structure. Superficial analogies to queue acknowledgement or cleanup transfer are not enough.

Potential places to test rather than assume:

- lease/reservation publication in controllers;
- durable job ownership before external acknowledgement;
- cache/index pointer publication before replacement validity;
- generation publication before old-owner retirement.

## Similarity traps to preserve in retrieval

### Premature ACK versus ambiguous ACK loss

```text
premature ACK:
replay authority destroyed before required handling

ambiguous ACK loss:
effect may already exist, but confirmation is missing
```

Different repair families.

### Result precedence versus cleanup liveness

```text
precedence bug:
wrong terminal value wins

liveness bug:
correct terminal value never becomes observable
```

A shared terminal-owner concept may connect them without merging species.

### Stale validation versus over-normalization

```text
stale validation:
identity changes after a valid check

over-normalization:
identity was changed before the check
```

Both can produce “checked one thing, used another,” but the discriminator is time/context versus representation.

### Publication before ownership versus recoverable-owner loss

```text
publication-before-ownership:
live object can look free

recoverable-owner loss:
only retryable predecessor disappears before successor succeeds
```

Both reward “what if we stop here?” but protect different invariants.

## Candidate concepts that now justify first-class glossary work

The audit repeatedly depends on these terms:

```text
authoritative state
operation owner
cleanup owner
publication
reachability
ownership
reusability
terminal state
remote-effect certainty
commit point
reconciliation
idempotency
generation
semantic identity
normalization
authority context
```

A next tranche should materialize concept entries where multiple bug species currently rely on a term with domain-qualified meanings.

## Recommended next corpus attacks

Bias toward cases likely to **break** the current taxonomy:

1. a stale-generation publication case where old work is valid but no longer authoritative;
2. a shared lifecycle-promise/reentry deadlock where there is one terminal owner but it waits on itself;
3. a cache-integrity case where publication is atomic but content authority is wrong;
4. a path case where repeated revalidation is still insufficient because the threat model requires descriptor-relative identity;
5. a negative result where a magic constant is protocol-owned and therefore correct;
6. an operation where cleanup is part of the commit and must override apparent earlier success;
7. a deliberately best-effort aggregate whose zero exit is correct despite skipped objects.

Those counterexamples will be more valuable than another ten confirming examples.
