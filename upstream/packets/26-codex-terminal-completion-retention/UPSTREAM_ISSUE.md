# Upstream issue

## Status

`OPEN — MAINTAINER TRIAGE PENDING`

Issue: [openai/codex#37207](https://redirect.github.com/openai/codex/issues/37207)

Title:

> Unified exec can omit command output when its completion listener starts late or falls behind

Filed by the owner on 2026-08-06 after reviewing the final issue form.

## Filed scope

The issue reports that unified exec can receive stdout or stderr and still omit those bytes from the completed tool result when the completion listener subscribes late or falls behind.

The filed report includes:

- the local `Lagged(_) => continue` path;
- the matching completion-watcher behavior;
- reproduction steps for late subscription and receiver lag;
- the expected completed-result behavior;
- a link to the owned four-file implementation proof.

## Implementation proof

Owned source: `teamleaderleo/codex#144`

The implementation stores each output chunk before live broadcast and builds the completed result from that retained output when the command closes.

## Public interaction boundary

The issue filing is complete. No public pull request, follow-up comment, reaction, review, or other upstream interaction is authorized without another owner decision.