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

## Ownership

The rule that decides which actor is currently responsible for a resource or state and which actions that responsibility authorizes: publish, mutate, reuse, clean up, retry, or transfer.

Allocator ownership, cleanup ownership, controller ownership, lease ownership, and Rust value ownership share useful structure but are not interchangeable mechanisms.

Entry: `ownership`.

## Publication

The transition that makes prepared state visible enough for another component to rely on, reference, discover, or treat it as authoritative.

Publication does not automatically imply durability, integrity, or ownership.

Entry: `publication`.

## Generation

An identity for one version of replaceable live state or work. Generations make logical supersession explicit when completion order can differ from replacement order.

Old-generation work may sometimes finish safely without retaining authority to publish state for future work.

Entry: `generation`.

## Commit point

The boundary after which the new state/effect is authoritative enough that ordinary rollback to the prior state would lie, duplicate ownership, or create conflicting topology.

Post-commit repair and compensation may remain possible, but they are not the same as pretending commit never happened.

Entry: `commit-point`.

## Reconciliation

Recovery by comparing durable intent/identity with current authoritative observations and selecting the next safe transition. Reconciliation preserves uncertainty instead of requiring fictional rollback history.

Entry: `reconciliation`.

## Retryability

The property that another attempt can be made without duplicating a completed effect, destroying surviving state, or violating the operation's ownership/identity contract.

An error result alone does not establish retryability.

Entry: `retryability`.

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

A storage view can explain `publication` through pointer visibility and allocator ownership. An auth view can explain `semantic identity` through account authority. A controller view can explain `generation` through accepted-current tickets. A Rust view can explain language ownership without silently equating it with allocator or distributed ownership.

The concept keeps one shared core while domain views supply the local mechanism.

```text
concept
  ├── shared structural meaning
  ├── domain-qualified meaning A
  ├── domain-qualified meaning B
  └── cases showing where the analogy stops
```

That is preferable to either one universal definition that becomes vague or several unrelated glossaries that silently redefine the same word.
