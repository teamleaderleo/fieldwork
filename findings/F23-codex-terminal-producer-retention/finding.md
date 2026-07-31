# F23-codex-terminal-producer-retention: Retain bounded terminal output before best-effort broadcast

Finding state: `comparative-evaluation-active`

Workstream: `J/N/O — Codex process output and current-source evidence`  
Canonical Fieldwork issue: `#23`  
Canonical finding path: `findings/F23-codex-terminal-producer-retention/finding.md`  
Canonical implementation: `teamleaderleo/codex#93`, pending latest-public-head successor  
Exact implementation head: `7f15307fd2c157d8a139310d2e8243f3f2b391a4` on base `4642370542739d5dd080b0c87a9de06a6435d3db`  
Latest public source reviewed: `openai/codex@3d1d26915a303c3b4765828f973f5464f8c28c5c`  
Strongest evidence class: `target-executed` for the nine candidate controls; mixed for the broad package gate  
Reviewed input generation: `run 30587866332; artifact 8777460316; source #91/#93; current-source carrier #94 run 30597355839; complete public overlap review`  
Current review disposition: `RESTACK AND EXECUTE on latest public head`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

A process produces stdout and stderr. Codex retains a bounded transcript and broadcasts live output to listeners. The broadcast is deliberately best-effort: a listener can subscribe late or fall behind.

Terminal completion should use the bytes retained by the producer rather than asking a lossy listener to reconstruct the final transcript.

The four-file source candidate is materialized and its nine focused controls passed. The prior broad package gate encountered stack exhaustion in an unrelated test. Public Codex has moved again, although the complete public delta remains file-disjoint from the terminal source fence. The remaining work is a direct latest-head restack and a broad package run under the raised-stack condition already used for this class of repository test.

## Why we care

A command can finish while its completion item omits bytes Codex received. The model or user then receives an incomplete result even though the process producer observed the output.

This finding preserves Codex's existing bounded head/tail policy. It changes the owner of the retained completion transcript, not the retention limit.

## Governing invariant

Producer-received output must enter the bounded authoritative transcript before best-effort live broadcast. Terminal completion reconciles partial streamed output against that producer-owned transcript.

Success at adjacent boundaries proves less:

- process exit does not prove the subscriber received every byte;
- broadcast delivery does not prove the final transcript;
- bounded retention does not prove hard-kill drain or process-tree settlement;
- a focused behavior pass does not prove the complete current package gate.

## Current source and evidence

### Historical behavior receipt

Fieldwork run `30587866332` established:

- exact controls `9/9`;
- repository formatting;
- exact four-file source fence;
- focused `codex-core` library gate;
- integration target compilation;
- source export and artifact upload.

Artifact `8777460316` retained:

- digest `sha256:9c6c4f6741ee2514e995849ca2bed9caf0f80b80fdbb3a9ea31565df3ebda2dd`;
- source archive SHA-256 `dca7808534f03a576a3b1d11f312393a8861c7c5f268cea2b3d6ac442f1122f5`;
- source tree `563f90f55c0ebd9454171d24697d796cba1388d4`;
- source parent `97576b1794872e342450ebd577123e052ab57626`.

### Materialized source

Owned source PR #93 is a real four-file source candidate:

- base `4642370542739d5dd080b0c87a9de06a6435d3db`;
- head `7f15307fd2c157d8a139310d2e8243f3f2b391a4`;
- exactly four files;
- 294 additions and 57 deletions.

It reuses the independently verified blobs from predecessor source #91:

| File | Blob |
| --- | --- |
| `codex-rs/core/src/unified_exec/async_watcher.rs` | `a0427969dec77d57f6bc3037108cd4be26125cd0` |
| `codex-rs/core/src/unified_exec/async_watcher_tests.rs` | `57002ea930169d2815aed51e42bbb37f27faedc8` |
| `codex-rs/core/src/unified_exec/process.rs` | `ca47e90159328921a3f469fd0dad72c91ef5f86a` |
| `codex-rs/core/src/unified_exec/process_tests.rs` | `b76c9151eb9b5a42e6e6cdfe4ef4b1c0c1686f58` |

### Prior current-source carrier

Execution carrier #94 checked out exact source head `7f15307...` and ran the nine declared controls through the repository `just test` entrypoint.

Run `30597355839` reached the broad `codex-core` package gate after the candidate-specific controls passed. The broad package gate then hit stack exhaustion in a test outside the four-file candidate fence.

This is a mixed receipt:

- candidate behavior: supported at the old pin;
- broad default-stack package gate: failed outside the candidate fence;
- raised-stack broad gate: still required;
- latest-public-head behavior: still required.

## Current public compatibility

The complete public compare from `464237054...` to `3d1d26915...` is eleven commits ahead and zero behind.

The delta changes release packaging, MCP, tool planning/registration, skills, external-agent connector detection, and associated tests. It does not touch any of the four terminal candidate files.

That file-disjoint result supports direct restacking. It does not substitute for target execution because dependencies, shared test code, and crate-level behavior can still change outside the source fence.

## System and ownership map

```text
process stdout/stderr producer
├── bounded producer-owned transcript
├── best-effort live broadcast
└── close/drain completion
    → reconcile partial stream
    → terminal completion item
```

- The output task owns bytes as they arrive.
- The bounded buffer owns retained completion content and omission metadata.
- Broadcast owns responsive live delivery and may lose subscriber delivery.
- The completion path owns final reconciliation.
- Process termination, containment, and restart recovery have separate owners.

## Claim table

| Claim | Evidence class | Exact support | Current limit |
| --- | --- | --- | --- |
| Producer-owned retention prevents late-subscriber loss on normal close | `target-executed` | exact controls in run `30587866332` and prior-pin carrier | Linux normal-close path |
| Invalid UTF-8 bytes remain retained while a subscriber lags | `target-executed` | focused producer/decoder controls | bounded policy still applies |
| Authoritative completion can replace a partial streamed transcript | `target-executed` | reconciliation control | does not establish process settlement |
| Current deque/progress behavior was preserved in the source candidate | artifact and source review | exact four blobs and nine controls | latest-head execution remains |
| Public drift is file-disjoint from the source fence | `source-read` | complete `464237... → 3d1d269...` compare | shared dependencies can still affect behavior |
| Broad default-stack failure is outside the source fence | mixed execution receipt | #94 reached broad package gate after focused controls | exact raised-stack receipt remains |

## Approaches considered

### Retained: producer-owned bounded transcript

This uses the first non-lossy owner, preserves live streaming, and keeps the existing memory bound and omission semantics.

### Declined: completion from broadcast subscription

Broadcast can drop delivery by design. A late or lagging subscriber cannot own an authoritative final transcript.

### Declined: unbounded retention

The issue is ownership rather than unlimited storage. The existing bounded policy remains.

### Declined: treat the old current pin as current

Public source moved through eleven commits. File-disjointness permits restacking but does not preserve a present-tense delivery claim without execution.

### Deferred: hard termination and restart recovery

Those need process settlement, containment, and durable reattachment contracts beyond normal-close transcript ownership.

## Edge cases covered

| Edge case | Result |
| --- | --- |
| output before listener subscription | final completion includes retained output |
| deliberately lagging live subscriber | producer transcript remains complete within the bound |
| invalid UTF-8 during lag | bytes remain retained and decoder progresses |
| partial live transcript | authoritative completion replaces partial stream |
| ASCII and multibyte max-byte split | no codepoint split |
| invalid byte between valid prefixes | valid prefix consumed and remaining bytes advance |
| exact source fence | four files only |

## Edge cases deferred

| Edge case | Owner or trigger |
| --- | --- |
| hard-kill trailing bytes | process settlement finding |
| Windows process-tree containment | Windows process finding |
| remote executor reattachment | restart/recovery finding |
| durable tool-result persistence | F83 and replay findings |
| entire unbounded output stream | product-policy change |

## Exact next controls

1. Materialize the identical four verified blobs on public head `3d1d26915...`.
2. Verify the latest source branch changes exactly the four declared files.
3. Run repository formatting and require a clean tree.
4. Resolve and run the same nine exact controls.
5. Run the focused `codex-core` package with the raised stack condition.
6. Preserve an ordinary-stack diagnostic only as separate environment evidence.
7. Review the complete four-file diff on the exact latest source head.
8. Transfer receipts into #23, #239, this finding, and the source PR.
9. Retire execution carriers after source and receipts are durable.

## Current disposition and desk routing

- Finding state: `comparative-evaluation-active`
- Review disposition: `RESTACK AND EXECUTE on latest public head`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: latest-head source materialization followed by the nine exact controls and raised-stack package gate.
- Clearing condition: exact latest source head, clean four-file diff, focused controls, raised-stack package result, complete-diff review, and carrier retirement agree.
- Required subgates: public overlap, source identity, target-native formatting/testing, broad package gate, review, and cleanup.
- Autonomous work remaining: source restack, execution, review, synthesis, and carrier retirement.
- Non-delegable human decision: merge, release, deployment, credentials, or public upstream contact.

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-31 | historical source and carrier | retained producer-ownership invariant and current deque-compatible source |
| 2026-07-31 | run `30587866332` | nine controls and bounded package/compile gates passed |
| 2026-07-31 | artifact review | verified exact source tree and blobs |
| 2026-07-31 | source #93 | materialized the four-file candidate on public pin `464237054...` |
| 2026-07-31 | carrier #94 | focused controls passed; unrelated default-stack broad test failed |
| 2026-07-31 | public compare through `3d1d26915...` | source fence remains file-disjoint; latest-head execution required |

## References

- Fieldwork issues #23 and #239.
- Owned Codex PRs #91, #93, and #94.
- `findings/F239-codex-upstream-convergence/finding.md`.
- `findings/F239-codex-upstream-convergence/evidence/20260731-terminal-materialization-verification.md`.
- `findings/F239-codex-upstream-convergence/evidence/20260731-terminal-current-source-restack.md`.
- Public Codex source through `3d1d26915a303c3b4765828f973f5464f8c28c5c`, read-only.
- Public upstream interaction: none.
