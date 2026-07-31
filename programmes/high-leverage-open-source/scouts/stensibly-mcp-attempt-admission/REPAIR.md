# Stensibly MCP attempt admission and privacy repair

Target: `teamleaderleo/stensibly#691`  
Exact target head: `7a5146da52139dec062575baa512eb2c97531060`  
Target work class: Tier 1 deterministic observation compiler  
External contact authorized: no

## Defects

Complete review of the exact three-file target candidate retained four admission/privacy defects.

### 1. Out-of-range numeric-looking array fields

`exactDenseArray()` admits any own string key matching a nonnegative-integer spelling, even when the numeric index is outside `[0, length)`. A hidden data property or accessor at `4294967295` can therefore survive array admission without participating in iteration, ordering, or the canonical fingerprint.

### 2. Namespaced credential-shaped identities

The identity detector is anchored only at the start of the field. Values such as `attempt:github_pat_...`, `request.ghp_...`, `grant-xoxb-...`, and `trace:sk-proj-...` pass the public identity grammar and can be persisted during creation or re-admission.

### 3. Attacker-controlled diagnostics

Unknown record keys and symbol descriptions are interpolated into thrown diagnostics. The validator correctly uses descriptors and avoids invoking accessors, but the error text can still publish an untrusted credential-shaped property name.

### 4. Duplicated failure-stage authority

The admitted `failureStages` array duplicates the keys of the exhaustive `failureStageWindows` table. A future stage can be added to one and omitted from the other, creating admission/ordering drift.

## Selected repair

The exact-source transformer:

- requires every old source block to occur exactly once before replacement;
- admits only `length` plus exact canonical indices `0..length-1` for arrays;
- rejects every extra string or symbol field with fixed label-only prose;
- uses fixed label-only prose for unknown record fields;
- adopts the landed delimiter-aware credential detector used by delegated GitHub authority receipts;
- derives the admitted failure-stage vocabulary directly from `failureStageWindows` and freezes the exported list;
- updates the existing unknown-field expectation to the fixed diagnostic.

The first carrier generation used a hand-authored unified patch. It failed before target setup because two minimal-context hunks did not apply to the exact source. That result was carrier-only. The current transformer replaces exact complete source blocks and aborts unless each preimage is unique, avoiding line-number and hunk-count ambiguity while retaining a reviewable resulting target diff.

## Hostile-input controls

The focused target-native test requires:

1. hidden data property `4294967295` rejected while array length remains one;
2. accessor `4294967295` rejected with zero getter invocation;
3. namespaced GitHub, Stensibly, OpenAI-shaped, Slack-shaped, and environment/secret locator identities rejected during creation;
4. the same identities rejected during re-admission;
5. a credential-shaped unknown property rejected with fixed prose and zero getter invocation;
6. the admitted failure-stage list exactly equals the exhaustive window keys and no separate literal list remains.

## Exact execution boundary

The carrier checks out the exact target head, compiles and executes `apply_repair.py` in a disposable worktree, copies only the focused test, installs Bun `1.3.10`, and runs:

- existing attempt-observation tests;
- existing single-failure regression;
- the new hostile-input matrix;
- target TypeScript typecheck;
- target runtime-parity check;
- repaired diff hygiene.

This is a repair carrier, not the canonical Stensibly source branch. A green result should be composed by the owner into the target three-file candidate, rerun through its complete CI, and receive a fresh complete-diff review.

## Boundary

This repair changes no provider transport, HTTP request, authority grant, durable production state, credential, deployment, merge, release, payment, private data, or public upstream interaction. It does not claim that identity-pattern matching is a general secret scanner; it closes the named credential-shaped persistence families at this bounded receipt boundary.
