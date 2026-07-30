# F23-codex-terminal-producer-retention: Retain bounded terminal output before best-effort broadcast

Finding state: `delivery-gate-ready`

Workstream: `J/N/O — Codex process output and current-source evidence`  
Canonical Fieldwork issue: `#23`  
Canonical finding path: `findings/F23-codex-terminal-producer-retention/finding.md`  
Canonical implementation: `pending owned Codex source PR after artifact materialization`  
Exact implementation head: `8c7ea38419d790032db459816980e6b4dd38f574` retained in artifact; owned branch is not yet materialized  
Exact base or source revision: `openai/codex@97576b1794872e342450ebd577123e052ab57626`  
Strongest evidence class: `target-executed`  
Reviewed input generation: `Fieldwork #268 run 30587866332; artifact 8777460316; artifact digest and checksum review`  
Current review disposition: `HOLD source review until exact tree materialization`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

A running process produces bytes. Codex keeps a bounded transcript and also broadcasts live output to listeners. The live broadcast is intentionally best-effort: a listener can arrive late or fall behind.

Terminal completion should therefore use the bytes retained by the producer, not ask a lossy listener to reconstruct the final transcript. The current candidate retains output before broadcast and reconciles completion with that producer-owned bounded transcript.

The behavior has passed exact current-source controls. The remaining defect is bookkeeping: the verified source tree exists in a retained artifact, while the intended owned Codex source branch still points at the untouched base.

## Why we care

A command can finish successfully while its completion item omits bytes the producer received. The model or user can then see an incomplete result even though Codex observed the output.

This is distinct from unbounded logging. The retained transcript follows Codex's existing bounded head/tail policy and preserves explicit omission behavior.

## What happens if we leave it alone

A late or lagging broadcast subscriber can define the completion transcript. Output that existed before subscription or while the subscriber lagged can be absent from the final item.

Observed controls cover ordinary close, delayed subscription, partial stream replacement, and invalid UTF-8 progress. Hard termination, process-tree containment, and restart reattachment remain separate.

## Current finding

Unified-exec output should be retained at the non-lossy producer boundary before best-effort broadcast. Completion should reconcile partial streamed output with that authoritative bounded producer transcript.

The retained source preserves upstream improvements:

- bounded output collection;
- `VecDeque` pending decode bytes;
- progress across invalid UTF-8;
- close/drain ordering before completion;
- explicit omission semantics.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Producer-owned retention prevents late-subscriber loss for normal close | `target-executed` | exact local-output and completion controls in run `30587866332` | Linux normal-close path |
| Invalid UTF-8 bytes remain retained when live broadcast lags | `target-executed` | exact invalid-UTF-8 producer control | Bounded transcript policy still applies |
| Partial stream output can be replaced by authoritative completion output | `target-executed` | exact reconciliation control | Does not settle remote process identity |
| Current deque behavior remains intact | `target-executed` | five exact split/progress controls | Source base is `97576b...` |
| Retained source artifact is internally exact | `source-read` | artifact metadata, five checksum records, four-file archive, resolved names | Owned Git branch still lacks the commit |

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
- Process termination, sandbox denial, and restart recovery have adjacent owners.

## Historical precedent

### Bounded unified-exec output collection

- Source: openai/codex PR #31802.
- Principle supported: retain bounded head/tail output, continue draining, and mark omissions.
- Important difference: a bounded buffer can still be populated from a lossy subscriber instead of the producer.

### Lifecycle event ordering

- Source: openai/codex PR #34713.
- Principle supported: wait for output-task closure, drain trailing chunks, and publish terminal events in order.
- Important difference: ordering does not by itself give completion a producer-owned transcript.

### `VecDeque` streaming decode

- Source: openai/codex PR #36194.
- Principle supported: avoid front-shifting bytes and make progress around invalid UTF-8.
- Important difference: the historical Fieldwork source touched the same files and had to be reconstructed while preserving this current behavior.

### Windows containment

- Sources: openai/codex PRs #29981 and #29982.
- Principle supported: process-tree containment and output-reader ordering are explicit platform contracts.
- Important difference: containment and transcript retention are adjacent but independently testable.

## Approaches considered

### Retained approach: producer-owned bounded transcript

This uses the first non-lossy owner, preserves live streaming, and retains current memory limits.

### Declined: completion from broadcast subscription

Broadcast is allowed to drop delivery. A late or lagging subscriber cannot define an authoritative final transcript.

### Declined: unbounded output retention

The invariant concerns ownership, not unlimited storage. Existing bounded head/tail and omission semantics remain.

### Declined: cherry-pick historical source mechanically

Current upstream changed the same decoder files. A mechanical conflict choice would discard `VecDeque` and invalid-byte progress improvements.

### Deferred: hard-termination and restart recovery

Those require process settlement and durable reattachment contracts beyond normal-close transcript ownership.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Output arrives before listener subscribes | exact completion control | final item includes retained output |
| Live broadcast deliberately lags | real driver-backed `SpawnedProcess` control | producer transcript remains complete within bound |
| Invalid UTF-8 during lag | exact producer control | bytes retained and decoder progresses |
| Partial live transcript | reconciliation control | authoritative completion replaces partial stream |
| ASCII and multibyte max-byte split | exact deque controls | no codepoint split |
| Invalid byte between valid prefixes | exact deque controls | valid prefix consumed and remaining bytes advance |
| Full library compatibility | bounded carrier gate | `codex-core --lib` passed |
| Integration compile compatibility | bounded carrier gate | all integration targets compiled |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Hard-kill trailing bytes | Producer may terminate before close/drain | process settlement finding |
| Windows process tree | Platform containment owner | dedicated Windows process finding |
| Remote executor reattachment | Requires durable remote identity | restart/recovery finding |
| Durable tool-result persistence | Separate Session/ThreadStore owner | F83 and receipt findings |
| Entire unbounded stream | Conflicts with declared retention policy | reopen only if product policy changes |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `teamleaderleo/fieldwork#268@58c0d027e2acf80fb9e16d89d0daba65de0dc563` | run `30587866332` | Linux hosted carrier | nine exact controls, full library gate, integration compilation passed | `target-executed` |
| artifact `8777460316` | checksum and archive inspection | retained workflow artifact | five payload checksums verified; exact four files and nine names retained | `source-read` artifact review |

Artifact metadata:

- source head `8c7ea38419d790032db459816980e6b4dd38f574`;
- source tree `563f90f55c0ebd9454171d24697d796cba1388d4`;
- source parent `97576b1794872e342450ebd577123e052ab57626`;
- artifact digest `sha256:9c6c4f6741ee2514e995849ca2bed9caf0f80b80fdbb3a9ea31565df3ebda2dd`.

## Complete-diff and compatibility review

- Declared source fence: exactly four unified-exec process/watcher files.
- Historical source was reconstructed against `97576b...` while preserving current deque behavior.
- The retained patch and source archive are available and checksum-verified.
- The intended owned branch `fieldwork/23-terminal-97576-source` currently compares identical to untouched base with zero commits.
- An attempted source PR correctly failed because no source commit exists on the branch.
- Public Codex has advanced substantially; after artifact materialization, current overlap must be refreshed before proposal packaging.
- Execution carriers #53 and Fieldwork #268 remain non-canonical and should retire only after source and receipts transfer.

## Current disposition and desk routing

- Finding state: `delivery-gate-ready`
- Review disposition: `HOLD source review until exact tree materialization`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: create the retained tree as one commit parented by `97576b...`, move the intended branch to exact head `8c7ea384...` or a proven equivalent commit, verify tree and file identities, then open the four-file source PR.
- Clearing condition: owned source branch and retained artifact agree on parent, tree, files, and patch.
- Required subgates: Git materialization, source PR, current drift classification, complete-diff review, carrier retirement.
- Autonomous work remaining: source materialization and review.
- Non-delegable human decision: none.

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | historical #49/#53 | Retained producer-ownership invariant and reconstructed current deque-compatible source |
| 2026-07-31 | Fieldwork #268 run `30587866332` | Bounded terminal behavior and package gates passed |
| 2026-07-31 | artifact review | Target evidence accepted; branch materialization identified as the sole source-review blocker |

## References

- Fieldwork issues #23 and #239.
- Fieldwork PR #268.
- Owned Codex PRs #49 and #53.
- `findings/F239-codex-upstream-convergence/finding.md`.
- Artifact `8777460316` and run `30587866332`.
- Public upstream interaction: none.
