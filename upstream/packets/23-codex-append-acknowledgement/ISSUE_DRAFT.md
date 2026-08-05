# Upstream issue draft — proposal sequence item 2

> Do not post without explicit public-contact authorization. Refresh against current public source, repeat duplicate search, and update every revision immediately before use.

## Title

Expose the authoritative history-append acknowledgement at the Codex session boundary

## Problem

`Session::record_conversation_items()` updates live conversation history, attempts to append rollout items, and then emits raw response items. The result of the authoritative live-thread append is logged inside the persistence helper and discarded.

A caller therefore cannot distinguish:

- an append that acknowledged;
- a failure before the item was written;
- an error returned after the item may already have committed.

Raw-response delivery cannot answer that question. A generic storage error also cannot authorize retry because the write may already exist.

## Proposed bounded prerequisite

Return an acknowledgement from `record_conversation_items()` while preserving current caller behavior:

- no live thread: success because no durable append is required for the ephemeral session;
- acknowledged live append: success;
- pre-write failure: failure;
- commit-then-error: failure even though reloaded history may contain the item.

The result means only whether the required append operation acknowledged. It does not prove absence, authorize replay, or settle remote effects.

## Why a boolean first

All reviewed production call sites currently ignore the value. A boolean is therefore enough to expose the missing signal without introducing unused certainty or identity contracts. A typed result becomes appropriate when a concrete consumer needs to distinguish confirmed absence from unknown commit outcome.

## Implementation evidence

A reviewed three-file prototype exists in the owned fork at `teamleaderleo/codex#140`. It covers ephemeral authority, acknowledged persistence, pre-write failure, and commit-then-error separately and passed the complete thread-store package at its exact source pin.

That commit is implementation evidence, not a current-main patch. Public source has advanced and changed `session/mod.rs`; the prototype must be refreshed and rerun before any proposed pull request.

## Question for maintainers

Is `Session::record_conversation_items()` the right boundary to expose this acknowledgement, and is acknowledgement-only semantics the preferred first step before any caller policy or typed reconciliation state?

## Non-goals

- automatic retry or replay;
- typed `Absent/Persisted/Unknown` certainty in this change;
- duplicate reconciliation or receipt identity;
- compaction, resume, fork, or rollback policy;
- remote-effect settlement;
- changing raw-response delivery.

## Sequence note

This is intentionally the second bounded Codex proposal. Producer-owned terminal-output retention should be discussed first because it demonstrates direct user-visible information loss from allowing best-effort delivery to own the final transcript.

No public upstream interaction has occurred.