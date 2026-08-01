# Upstream pull request draft

## Status

**Draft only. Do not submit without a public-upstream invitation.**

Target: `openai/codex`

Proposed title:

> fix: retain terminal completion bytes before best-effort broadcast

## Draft body

### Summary

Retain bounded stdout/stderr bytes in the unified-exec producer before best-effort broadcast delivery, then use those bytes to produce an authoritative completion transcript.

This covers output emitted before a completion subscriber attaches and output missed by a lagging or closed broadcast receiver.

### What changes

- retain raw producer-read stdout/stderr bytes in bounded deques;
- retain each chunk before attempting broadcast;
- return retained bytes on normal EOF;
- reconcile streamed and retained views through suffix/prefix overlap;
- handle invalid UTF-8 without losing forward progress;
- preserve prompt hard-termination behavior;
- add focused regressions for pre-subscription output, lag, reconciliation, retention bounds, invalid UTF-8, and receiver closure.

### Files

- `codex-rs/core/src/unified_exec/async_watcher.rs`
- `codex-rs/core/src/unified_exec/async_watcher_tests.rs`
- `codex-rs/core/src/unified_exec/process.rs`
- `codex-rs/core/src/unified_exec/process_tests.rs`

### Source revisions for private preparation

- current public base: `670f69416bf91c5dfd8b58669e78050b584ff053`
- private clean source head: `a020d7bd3e7f6886c3fbc21d75b3110586df08f5`
- source tree: `9a067c244d464e863a7b50978826ac9930df680b`
- diff size: 281 additions, 52 deletions across four files

Refresh all revisions immediately before submission.

### Tests

Required current-head receipt:

```bash
just fmt
cargo fmt --all -- --check
# nine exact terminal-retention controls
cargo test -p codex-core --lib
# relevant integration-target compilation
```

Historical private evidence includes:

- nine exact controls passing on the latest retained source head;
- an earlier authoritative run passing the nine controls, full `codex-core` library gate, and integration-target compilation.

Replace this historical summary with the fresh current-head commands, counts, links, and exit codes before submission.

### Design notes

Broadcast remains best-effort for live output. Completion gains a producer-owned transcript with an explicit bound. Reconciliation preserves a streamed prefix that may have fallen outside the retained window while avoiding duplicate overlap.

### Risks

- bounded retention intentionally drops oldest bytes beyond the cap;
- overlap logic must avoid duplication and truncation;
- raw-byte retention and lossy text conversion need boundary review;
- normal EOF and hard termination have different waiting contracts.

## Reviewer checklist

- [ ] Four-file source fence confirmed.
- [ ] Current public base confirmed.
- [ ] Retention cap and eviction semantics accepted.
- [ ] Suffix/prefix overlap logic reviewed with binary and UTF-8 edge cases.
- [ ] Normal EOF has authoritative output.
- [ ] Hard termination remains prompt.
- [ ] Nine exact controls pass on the submitted commit.
- [ ] Full `codex-core` library gate passes or every shared failure has a baseline receipt.
- [ ] Integration target compiles.
- [ ] Public issue linkage follows maintainer preference.

## Submission gate

- public-upstream invitation received;
- current source branch freshly restacked;
- current-head execution complete;
- independent review complete;
- private links removed from public text;
- issue/PR scope remains this four-file unit only.
