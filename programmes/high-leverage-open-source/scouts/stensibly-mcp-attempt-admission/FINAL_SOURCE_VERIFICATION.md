# Stensibly MCP attempt observation final-source verification

Target: merged `teamleaderleo/stensibly#691`  
Exact final source head: `8f48b586f87b5619066cceb8e43a99e22cbb5e3a`  
Merge commit: `03627c362cedd86445a917a0e5fcdde5a6d5b0c4`  
Target work class: Tier 1 deterministic observation compiler  
External contact authorized: no

## In simple words

An earlier Fieldwork review found four admission/privacy gaps in the pre-merge Stensibly candidate:

1. arrays could retain out-of-range numeric-looking own fields;
2. namespaced credential-shaped attempt/request IDs could pass admission;
3. unknown field names or symbol descriptions could appear in diagnostics;
4. the admitted failure-stage list duplicated the exhaustive stage-window table.

Stensibly PR #691 later integrated those repairs under separate authority, added terminal response-serialization evidence, passed its canonical CI, and merged.

This Fieldwork carrier no longer transforms target source. It verifies the exact final source directly with additional hostile controls.

## Final-source contract

The merged source:

- admits only `length` and exact canonical indices `0..length-1` for observation arrays;
- rejects extra string and symbol fields before slot reads;
- uses fixed label-level diagnostics for unsupported fields;
- rejects direct and delimiter-namespaced credential-shaped attempt/request identities during creation and re-admission;
- derives the runtime failure-stage vocabulary from `failureStageWindows`;
- retains the final PR #691 lifecycle and response-serialization semantics.

## Additional hostile controls

The Fieldwork test adds seven focused cases:

1. out-of-range data field `4294967295` is rejected while array length remains one;
2. out-of-range accessor `4294967295` is rejected with zero getter invocation;
3. symbol array field is rejected with fixed prose, no symbol-description leak, and zero getter invocation;
4. namespaced GitHub, Stensibly, OpenAI-shaped, Slack-shaped, and environment/secret locator IDs are rejected during creation;
5. the same IDs are rejected during receipt re-admission;
6. credential-shaped unknown record fields produce fixed prose with zero getter invocation;
7. failure-stage admission is derived from the exhaustive window table rather than a second literal list.

These controls run beside the complete target attempt-observation and single-failure suites.

## Exact execution gate

The temporary workflow:

- pins the Fieldwork branch head;
- checks out exact final Stensibly head `8f48b586...`;
- copies one hostile test without changing tracked target source;
- installs Bun `1.3.10` and committed dependencies;
- runs target and Fieldwork tests;
- runs TypeScript typecheck and runtime parity;
- requires the tracked final-source worktree to remain clean;
- uploads logs and an exact-head JSON receipt.

A green result verifies the merged generation. It does not create a new source candidate or claim authority over the already-merged target decision.

## Historical carrier result

The earlier transformer generation at Fieldwork head `c642af5e7b934055e8ba6389acddbc8f73be1c58` passed 23 tests, typecheck, runtime parity, and diff hygiene against pre-merge target head `7a5146da...`. Artifact `8795873954` retained that repaired diff and logs.

That receipt remains useful repair-lineage evidence only. Final-source currentness requires execution against `8f48b586...`.

## Boundary

No provider transport, HTTP request, authority grant, credential, private data, deployment, merge, release, payment, or public upstream interaction is performed by this verification carrier. The target merge already occurred under separate repository authority.
