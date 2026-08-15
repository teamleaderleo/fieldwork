# Fieldwork glossary — seed view

## In simple words

This glossary is a view over concept entries, not a separate dictionary. Terms can participate in several domains and link to the bug species and invariants that depend on them.

## Authoritative state

The state whose owner is entitled to decide whether a transition happened, an operation is terminal, or a later action is legal.

A correlated symptom may be useful evidence without being authoritative.

Entry: `authoritative-state`.

## Operation owner

The component whose state machine owns one operation's pending/terminal/retry/cleanup rules. The initiator, UI, process parent, and operation owner may be different components.

Entry: `operation-owner`.

## Publication

The transition that makes prepared state visible enough for another component to rely on, reference, discover, or treat it as authoritative.

Publication does not automatically imply durability, integrity, or ownership.

Entry: `publication`.

## Reconciliation

Recovery by comparing durable intent/identity with current authoritative observations and selecting the next safe transition. Reconciliation preserves uncertainty instead of requiring fictional rollback history.

Entry: `reconciliation`.

## Remote-effect certainty

What the local system actually knows about an external mutation after dispatch:

```text
Absent | Persisted | Ambiguous
```

Timeout and cancellation are not automatically proof of `Absent`.

Entry: `remote-effect-certainty`.

## Semantic identity

What makes two representations refer to the same logical object for the decision being made. The relevant identity may include pathname resolution, credential authority, generation, protocol normalization, or another domain-owned binding.

Entry: `semantic-identity`.

## Why the glossary is composable

A future storage view can explain `publication` through pointer visibility and allocator ownership. An auth view can explain `semantic identity` through account authority. A controller view can explain `operation owner` through attempts and generations.

The concept keeps one shared core while domain views supply the local mechanism.

```text
concept
  ├── shared structural meaning
  ├── domain-qualified meaning A
  ├── domain-qualified meaning B
  └── cases showing where the analogy stops
```

That is preferable to either one universal definition that becomes vague or several unrelated glossaries that silently redefine the same word.
