# Ripgrep partial-producer failure scout — 2026-08-11

## In simple words

Ripgrep can successfully search bytes produced by a decompressor or preprocessor, find real matches, and then lose some or all visible evidence of those matches when the producer exits with an error at the end.

The behavior depends on output mode. A sequential ordinary search streams match lines before the terminal producer error arrives, so the user sees those matches. Parallel search buffers each file and abandons that buffer when the search returns an error, so the same matches disappear. Count output is emitted only from the search sink's successful `finish`, and the searcher deliberately skips `finish` after an I/O error, so a count can disappear even in a single-file search. Global statistics can consequently report zero matches after ordinary sequential output already printed a match. JSON has the same split: sequential mode can emit `begin` and `match` events followed by a zeroed summary, while parallel mode can discard the per-file events and emit only the zeroed summary.

This is broader than truncated zstd input. A tiny synthetic preprocessor that writes valid searchable stdout and then exits nonzero reproduces the same mode matrix.

**Disposition:** `INVESTIGATE / PROMOTE EXPERIMENT`.

The current source still contains the ownership chain that explains the behavior. Exact-current-head target execution remains pending because the available execution environment has ripgrep 14.1.1 and no Cargo toolchain. The released-binary probe is small and deterministic, and the public decompressor report against ripgrep 15.1.0 describes the same split.

Public upstream contact authorized/performed: `false` / `false`.

## Assignment

- Programme: open-source ecosystems / #207
- Parent scout: #210
- Target: `BurntSushi/ripgrep`
- Claim scope: mechanism / interface
- Owned output: this file
- Target revision inspected: `3fce3b5bb0236da2df6d99672afb8a719642eca7`
- Target branch: `master`
- Public report used as symptom seed: [ripgrep #3382](https://redirect.github.com/BurntSushi/ripgrep/issues/3382)
- Fieldwork branch: `research/ripgrep-partial-producer-failure-20260811`

## Question

When a producer feeding ripgrep emits valid searchable bytes and then exits with an error, what contract governs already-found matches, aggregate counts, buffered parallel output, JSON events, and global statistics?

A useful answer needs to distinguish four possibilities:

1. zstd-specific corruption handling;
2. decompression-specific process handling;
3. a generic producer/read-error boundary shared with preprocessors;
4. an output-mode problem caused after matching has already succeeded.

## Exact source map

Current public head inspected: `3fce3b5bb0236da2df6d99672afb8a719642eca7`.

### Producer process boundary

[`crates/cli/src/process.rs`](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/crates/cli/src/process.rs)

- `CommandReaderBuilder::build` spawns the producer with piped stdout and stderr.
- `CommandReader::read` streams stdout.
- When stdout reaches EOF, `read` sets `eof = true` and calls `close()`.
- `close()` waits for the child. A nonzero exit becomes an I/O error carrying stderr.
- Therefore a producer can yield many successful reads and only later turn the final read into an error.

### Decompression boundary

[`crates/cli/src/decompress.rs`](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/crates/cli/src/decompress.rs)

- recognized compressed files are searched through `DecompressionReader`;
- the decompression reader delegates process output to `CommandReader`;
- the same late nonzero-exit error therefore reaches the generic reader search path.

### High-level search worker

[`crates/core/search.rs`](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/crates/core/search.rs)

- `search_preprocessor()` and `search_decompress()` both call `search_reader()` and then close the producer reader;
- `search_reader()` calls `searcher.search_reader(...)?` before building `SearchResult` from the sink;
- a terminal producer read error therefore prevents `SearchResult { has_match, stats }` from being returned even if the sink already observed matches.

### Parallel output boundary

[`crates/core/main.rs`](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/crates/core/main.rs)

`search_parallel()`:

1. clears a per-worker output buffer;
2. executes `searcher.search(&haystack)`;
3. on `Err`, reports the error and immediately continues;
4. calls `bufwtr.print(...)` only after an `Ok(SearchResult)`.

So match text already rendered into the per-file buffer is abandoned on the error path. Sequential `search()` writes to stdout directly through its printer, so already-emitted ordinary match lines survive before the same error is reported.

### Searcher completion contract

[`crates/searcher/src/sink.rs`](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/crates/searcher/src/sink.rs)

The `Sink` contract says searcher errors terminate immediately **without calling `finish`**.

[`crates/searcher/src/searcher/mod.rs`](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/crates/searcher/src/searcher/mod.rs)

`Searcher::search_reader` uses the generic reader and returns its I/O error through the sink error type. The terminal producer error therefore falls under the no-`finish` rule.

### Count / aggregate printer boundary

[`crates/printer/src/summary.rs`](https://github.com/BurntSushi/ripgrep/blob/3fce3b5bb0236da2df6d99672afb8a719642eca7/crates/printer/src/summary.rs)

- `SummarySink::matched` increments `match_count` while data is searched;
- `SummarySink::finish` emits count output and finalizes aggregate statistics;
- because read errors skip `finish`, the accumulated count is never printed on this path.

## Public symptom and overlap check

The public issue [#3382](https://redirect.github.com/BurntSushi/ripgrep/issues/3382) is open and reports the same user-visible split on ripgrep 15.1.0:

- one damaged `.zst` can print matches and then an error;
- multiple files in normal parallel search can print no matches;
- `--sort=path`, which disables parallelism, restores the matches;
- `-c` can print no count.

The issue currently has one non-technical comment. Searches performed during this scout found no open pull request or commit keyed to `3382`, and no separate issue surfaced for generic preprocessor partial output / nonzero-exit handling.

Evidence label: `issue-state-read / overlap-read`.

## Executed reduced probe — truncated zstd

Execution environment:

- ripgrep `14.1.1`
- zstd CLI `1.5.7`
- no Cargo toolchain available

A generated text file contained three `needle` lines. After zstd compression, truncating only one byte from the compressed file caused `zstdcat` to emit 786,432 bytes, including two `needle` lines, and then exit 1 with `premature end`.

Reduced mode matrix:

| Command form | Exit | Match output | Error output |
| --- | ---: | --- | --- |
| `rg -z needle test.zst` | 2 | two matches | decompressor error |
| `rg -z needle test.zst test.zst` | 2 | **none** | two decompressor errors |
| `rg -z needle test.zst test.zst --sort path` | 2 | four matches | two decompressor errors |
| `rg -zc needle test.zst` | 2 | **no count** | decompressor error |

The compressed fixture was about 13 KB. This is materially smaller than the original report's dictionary fixture and preserves the same discriminating behavior.

Evidence label: `model-executed / released-target-executed`.

## Executed reduced probe — generic preprocessor

To distinguish zstd/decompression from the generic producer boundary, the scout used this producer:

```sh
#!/bin/sh
cat "$1"
echo 'synthetic terminal failure' >&2
exit 7
```

Each input file contained:

```text
alpha
needle
omega
```

Observed on ripgrep 14.1.1:

| Mode | Exit | Visible result |
| --- | ---: | --- |
| one file, ordinary output | 2 | `needle` printed, then producer error |
| two files, parallel | 2 | no matches; producer errors printed |
| two files, `--sort path` | 2 | both matches printed, then producer errors |
| one file, `-c` | 2 | no count; producer error |
| one file, `-l` | 2 | path printed, then producer error |
| two files, parallel `-l` | 2 | no paths; producer errors |
| one file, `--json` | 2 | `begin`, `match`, then final zeroed `summary`; no per-file `end` |
| two files, parallel `--json` | 2 | only final zeroed `summary`; per-file events discarded |
| one file, `--stats` | 2 | match text printed, followed by statistics claiming `0 matches`, `0 matched lines`, `0 files contained matches` |
| two files, parallel `--stats` | 2 | no match text; zero statistics |

This rules out a zstd-specific explanation and strongly supports a shared late-producer-error mechanism.

Evidence label: `model-executed / released-target-executed`.

## Negative control

The same preprocessor changed only to `exit 0` produced normal behavior:

- one-file ordinary search: one match, exit 0;
- two-file parallel search: two matches, exit 0;
- count: `1`, exit 0;
- JSON: `begin,match,end,summary`, exit 0;
- no stderr.

The behavioral switch therefore tracks terminal producer failure, not the preprocessor path or fixture itself.

Evidence label: `model-executed / negative-control`.

## Mechanism finding

The smallest current explanation is a split contract between **partial successful observation** and **terminal stream success**:

1. the producer supplies bytes successfully;
2. the searcher invokes sink callbacks and ordinary printers may render matches;
3. producer EOF/exit handling converts the final read into an I/O error;
4. the searcher returns the error and skips sink `finish`;
5. high-level `SearchResult` is never created;
6. sequential ordinary output has already escaped to stdout;
7. parallel ordinary/JSON output remains in a per-file buffer and is abandoned by `search_parallel()`;
8. summary printers never get their successful `finish`, so counts are not emitted;
9. global stats never receive the absent `SearchResult`, allowing visible sequential matches to coexist with zero aggregate stats.

Confidence: **high** for the mechanism on the inspected source and reproduced released binary; **medium-high** for exact-current-head behavior until a target-native build executes the matrix.

## Competing explanations

### A. zstd truncation policy

Rejected as the primary explanation. The generic nonzero preprocessor reproduces the same split without compression.

### B. decompression wrapper only

Rejected as the primary explanation. `search_preprocessor()` routes through the same generic reader/search result path and reproduces it.

### C. parallel printer only

Partial explanation. It explains dropped ordinary/JSON file output in parallel mode, but cannot explain single-file count loss or sequential stats reporting zero after printing a match.

### D. summary-printer bug only

Partial explanation. The summary printer's dependence on successful `finish` explains count loss, but cannot explain ordinary parallel output disappearing.

### E. generic late producer/read error versus partial search outcome

Best current explanation. It accounts for every observed mode, including global statistics.

## Rejected shortcut

**Flush the parallel worker buffer before continuing on search error.**

This is attractive because it would recover already-rendered ordinary match lines in parallel search. It is incomplete:

- count output still depends on sink `finish` and would remain absent;
- global `SearchResult`/stats would remain absent;
- JSON would need an explicit decision about whether partial `begin`/`match` events without `end` are a valid error representation;
- binary-detection and summary semantics intentionally use successful completion to decide whether prior observations are authoritative.

Treat a parallel-buffer flush as a useful experiment/negative control, not a complete production patch.

## Ranked next experiments

### 1. PROMOTE — explicit partial-outcome characterization at the searcher/worker boundary

Build exact current ripgrep and add a synthetic reader/preprocessor fixture that emits one match and then returns a terminal error.

Matrix at minimum:

- ordinary standard output, one thread and multiple threads;
- `--sort path` as sequential control;
- `-c` and `--count-matches`;
- `-l` / files-with-match;
- `--json`;
- `--stats`;
- producer success control;
- producer failure before any stdout control;
- producer failure after non-matching stdout control.

The first design question is explicit: **should prior matches remain observable when the producer later fails, and if yes, which result types are partial versus final?**

### 2. PROMOTE — test-only parallel flush experiment

On an owned fork/test branch, force the error path in `search_parallel()` to print its worker buffer before reporting/continuing. Run the matrix above.

Purpose: prove exactly which symptoms this fixes and retain the remaining count/stats/JSON failures as evidence against a local-only repair.

### 3. INVESTIGATE — completion-with-error API design

Compare small designs that can preserve partial observations while still returning the terminal producer error. Candidates include:

- a high-level search outcome carrying `SearchResult` plus optional terminal error;
- an error-finalization callback distinct from successful `Sink::finish`;
- a worker-local result that exposes whether any printer output exists before propagating the error.

Any design must preserve existing binary-detection semantics and avoid falsely presenting a partial count as a complete count without an explicit contract.

### 4. PARK — zstd-specific special casing

Low value. The generic preprocessor reproduction demonstrates a shared mechanism, so format-specific handling would leave the broader bug class intact.

## Test placement map

Likely target-native coverage should touch two levels:

1. **searcher/sink contract tests** — synthetic `Read` that returns valid data and then an I/O error, to pin callback/finish behavior;
2. **ripgrep integration tests** — synthetic preprocessor is preferable to requiring damaged zstd tooling for the main behavior matrix; retain one compressed-file probe only if maintainers want regression coverage for the public symptom.

The synthetic preprocessor fixture is deterministic, portable across Unix-like CI, and isolates producer-exit semantics from archive-format behavior. Windows requires a corresponding portable helper or test binary rather than a shell script.

## Current-head execution blocker

Exact target source was read at `3fce3b5bb0236da2df6d99672afb8a719642eca7`, but this execution environment provides ripgrep 14.1.1 and no `cargo` command. Therefore:

- current-head source claims: `source-read`;
- executable behavior claims: `released-target-executed` on 14.1.1 plus public 15.1.0 report;
- exact-current-head target-native behavior: **pending**.

This is a bounded blocker, not a reason to widen implementation scope before the current-head matrix runs.

## Promotion recommendation

**Promote to a test-only owned-fork experiment.**

The strongest candidate is the generic partial-producer failure contract, with public #3382 as one concrete decompression symptom. Start with characterization tests and a deliberate flush-only experiment. Delay production code until the desired semantics for partial count, JSON completion, stats, and binary-detection interaction are explicit.

## FIELDWORK HANDOFF

State: ready-for-synthesis
Programme: open-source-ecosystems / #207
Target: BurntSushi/ripgrep
Testbed: local released binary plus future owned-fork current-head test branch
Batch: none
Campaign: none
Assignment: #210 ripgrep partial-producer failure scout
Claim scope supported: mechanism / interface
Integration context: none
Durable artifacts: `programmes/open-source-ecosystems/scouts/developer-tools-build-systems/RIPGREP-DECOMPRESS-20260811.md`
In simple words: a producer can yield valid searchable data and then fail; ripgrep's mode-dependent completion rules can preserve, discard, or contradict matches already found.
Finding: the shared `CommandReader -> search_reader -> SearchResult/printer` error path explains truncated-zstd, generic-preprocessor, parallel-buffer, count, JSON, and stats discrepancies. A parallel-buffer-only fix is incomplete.
Branch candidates: generic current-head characterization first; parallel flush-only experiment second; completion-with-error API design third.
Evidence labels used: source-read, issue-state-read, overlap-read, model-executed, released-target-executed, negative-control
Uncertainty: exact current-head execution pending; intended semantics for partial aggregate results require an explicit decision.
Dependencies discovered: no Cargo toolchain in the current execution environment; no overlapping PR/commit keyed to public #3382 found in this scout.
Decision needed: whether partial producer output should remain visible/represented after a terminal producer error, especially for count and JSON aggregate modes.
Automated upstream contact: prohibited
Human-performed upstream interaction recorded: none
