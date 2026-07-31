# Codex terminal successor addendum — 2026-07-31

This note records terminal-retention execution after the lane moved from the Codex fork into Fieldwork PR `#268`.

## Exact identities

- Fieldwork PR: `#268`;
- source base: `97576b1794872e342450ebd577123e052ab57626`;
- historical source: `7db66fe3f235df77c36a9db521677e23379bcac5`;
- initial Codex reconstruction carrier: `d5028fc9771407aa7a9bafbceb7eba051b91de36`;
- current Codex reconstruction carrier: `c4e0de2e54d804d1054afb90c30b7150a774151c`;
- current Fieldwork carrier head: `e9ff284f22deac696c456ad6f459b91552204b56`;
- current run: `30585576009`.

Codex PR `#70` remains the fork-side fallback.

## Run 1 — formatter prerequisite

Run `30584446394` passed exact checkout, source fetch, setup, and reconstruction. Whole-repository formatting stopped because `uv` was absent.

Classification: harness/tool provisioning. The carrier added pinned `astral-sh/setup-uv`.

## Run 2 — test-access design defect

Run `30584681645` passed:

1. exact source fetch;
2. all prerequisites, including `uv`;
3. four-file reconstruction;
4. target-native formatting;
5. exact four-file fence.

`codex-core` test compilation then failed because two sibling-module tests called private `spawn_local_output_task`.

This exposed a test-design choice:

- widen the helper to `pub(super)`; or
- keep the helper private and drive the production constructor.

## Selected repair

Keep `spawn_local_output_task` private.

The current Codex carrier rewrites the two local-output controls to use a real driver-backed `SpawnedProcess` through production `UnifiedExecProcess::from_spawned`.

This is stronger because it:

- exercises the production entrypoint;
- preserves the smallest implementation API;
- avoids test-only visibility;
- still lags best-effort broadcast deliberately;
- checks complete producer-owned retention for text and invalid UTF-8.

A brief module-scoped visibility repair at Fieldwork commit `6c0a7e68ce0605c1eac14d987724646600fb4a86` was superseded by this production-path design before delivery.

## Current run boundary

Run `30585576009` has cleared:

- exact carrier checkout;
- script extraction;
- source-ref fetch;
- target CI, Rust, nextest, and `uv` setup;
- source reconstruction;
- target formatting;
- exact four-file fence.

The nine exact controls are the current active phase. Focused `codex-core`, artifact export, source review, latest-pin renewal, and clean publication remain downstream.

Public upstream interaction performed: `false`.
