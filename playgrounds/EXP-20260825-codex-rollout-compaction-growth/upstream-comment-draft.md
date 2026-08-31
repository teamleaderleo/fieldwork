Confirming repeated `compacted.replacement_history` growth on a current Desktop build:

- ChatGPT Desktop `26.818.61809` build `7019`
- bundled `codex-cli 0.149.0-alpha.4.3`
- macOS `26.6.1 (25G76)`, arm64

A reproducible, modification-time-fenced scan of 368 local rollouts produced:

```text
total storage:             34,059,784,421 bytes (31.72 GiB)
compacted records:         6,246
compacted storage:         28,319,667,945 bytes (26.37 GiB)
compacted share:           83.1%
with replacement_history:  6,246 of 6,246
files >= 1 GiB:            8
largest compacted record:  63,397,531 bytes
```

The scan retained only structural classes and byte counts; it excluded transcript content, paths, filenames, thread IDs, and timestamps.

Each of the eight ≥1 GiB rollouts was 91.4–94.8% compacted records by byte size. The largest was a 13.26 GB root/VS Code rollout, with 12.12 GB in 399 compacted records. The next seven were subagent rollouts. This shows that the same storage multiplier affects both inherited child histories and root threads.

A 202 MB rollout in the same store was only 1.4% compacted by byte size, providing a negative control for the classifier.

Current public source at `c3953649156e15b67e572cb9e38bc825a811c24e` still:

1. constructs each checkpoint using `replacement_history: Some(items.clone())`;
2. appends the checkpoint without replacing earlier payloads;
3. loads the complete rollout into a `Vec` on the full-history path.

Cold compression and retained-image budgeting are useful partial mitigations, but they do not bound active rollout growth or repeated non-image replacement histories.

The storage invariant should be:

```text
H bytes of stable replacement history + N compactions
  -> O(H + N × checkpoint metadata), not O(N × H)
```

One implementation direction is to persist immutable checkpoint payloads once and let compacted records reference them. The corresponding regression should repeatedly compact a stable large history and assert sublinear physical growth.

The remaining design boundary is preserving resume, rollback, fork, window-lineage, world-state, and late-suffix behavior while making checkpoint storage proportional to unique retained history.
