# Playwright blob report durability — source review

Date: 2026-07-30

Parent scout: #26

Owned target probe: `teamleaderleo/playwright#2`

Owned execution carrier: `teamleaderleo/playwright#32`

Pinned Playwright source revision: `beaf223604b5c199b25287cd3c66bb8a9801a30c`

Upstream contact authorized: `false`

No upstream contact occurred.

## In simple words

Playwright's blob reporter builds one ZIP file at the end of a run.

Before that final step, the report events exist only in memory. While the final step is running, Playwright writes directly to the filename that merge tooling later treats as a complete report.

This creates two different questions:

1. **Atomic publication:** prevent an interrupted write from leaving a corrupt file that looks complete.
2. **Crash recovery:** preserve enough events before `onEnd` to reconstruct work after the process exits.

The first is a small file-publication correction. The second is a larger reporter contract. They should not be presented as one patch.

## Source-confirmed current boundary

`BlobReporter` retains:

- telemetry events in an in-memory message list;
- attachment source-to-ZIP mappings in memory;
- the final report name and metadata in memory.

`onEnd()`:

1. appends the final result event;
2. prepares the output directory and final `.zip` path;
3. creates a ZIP writer;
4. adds attachment files and one generated `report.jsonl` buffer;
5. pipes directly into `fs.createWriteStream(finalZipPath)`;
6. resolves only after the output stream closes.

No journal or replayable partial event file is written before `onEnd`.

## Merge consequence

`createMergedReport()` lists every file in the supplied directory whose name ends with `.zip`.

For every selected file it immediately:

- opens the ZIP;
- reads its entries;
- parses report metadata and events.

There is no completeness marker or skip rule for a final-looking but interrupted ZIP.

Supported consequence:

> If the reporter process exits after the final `.zip` path appears but before the archive closes, later merge tooling can select that corrupt archive and abort report merging.

This is stronger than a cosmetic leftover-file concern. One incomplete shard can block aggregation of otherwise complete shard reports in the same directory.

## Current-state execution matrix

Playwright PR #2 now tests three factual phases:

1. process exits from another reporter after `onTestEnd`, before blob `onEnd`;
2. process exits when the blob reporter's final ZIP write stream opens;
3. `onEnd` completes normally.

Assertions distinguish:

- no output report;
- one final-path `.zip` that cannot be extracted;
- one extractable `.zip` containing non-empty `report.jsonl`.

Execution carrier PR #32, workflow run `30497149316`, is queued. No target result is claimed yet.

## Repair slice A — atomic final publication

Purpose:

- ensure a `.zip` filename means the archive closed successfully;
- prevent merge tooling from selecting an interrupted archive;
- keep current event buffering and successful report contents unchanged.

Candidate sequence:

1. prepare the final output path as today;
2. create a unique temporary filename in the same directory that does **not** end in `.zip`;
3. stream and close the archive at that temporary path;
4. rename the closed temporary file to the final `.zip` path;
5. remove the temporary file on caught write or close failure.

Same-directory rename is required so publication uses the filesystem's rename boundary rather than a copy across devices.

Compatibility questions:

- existing `PWTEST_BLOB_DO_NOT_REMOVE` behavior and an already-existing destination;
- Windows destination replacement semantics;
- cleanup after process termination, where the non-`.zip` temporary file may remain;
- error preservation when close, rename, or cleanup fails.

Promise level:

- prevents corrupt final-looking report paths;
- does not preserve events when the process exits before publication;
- does not make `onEnd` crash-resilient.

## Repair slice B — recoverable event journal

Purpose:

- retain replayable event state before `onEnd`;
- distinguish incomplete, finalized, and recovered report generations;
- support deliberate recovery after process interruption.

This requires decisions beyond atomic file publication:

- append format and versioning;
- event flush or checkpoint cadence;
- attachment durability and path ownership;
- terminal completion marker;
- duplicate-event and duplicate-attachment handling;
- reporter ordering and partial `onEnd` semantics;
- recovery command or automatic discovery;
- cleanup and compaction of completed journals;
- compatibility with blob merge and older Playwright versions.

A journal cannot be inferred from the existing ZIP format alone. It is a new durability contract and should have its own issue after the phase matrix confirms the current boundary.

## Rejected combined framing

Do not say that a temporary ZIP rename makes reports crash-recoverable. It only makes final publication atomic.

Do not require an incremental journal merely to stop corrupt final filenames from entering merge discovery. That would make the first repair unnecessarily broad.

Do not name an interrupted final-path ZIP as a partial report unless its contents and replay rules are defined. Today it is an invalid archive.

## Self-review disposition

Evidence checked:

- blob reporter event and attachment ownership;
- final ZIP write sequence;
- output-directory preparation;
- merge report file discovery;
- ZIP extraction and metadata parsing path.

Strongest source-supported conclusion:

Playwright exposes the final `.zip` name before archive completion, and merge tooling trusts every `.zip` in the directory. Atomic publication is a narrow candidate independent from crash-recovery journaling.

Missing proof:

- the three-phase target matrix has not executed;
- interrupted writer timing may need a stronger deterministic hook;
- destination replacement behavior needs platform controls;
- no journal design has been implemented or tested.

Next action:

1. execute the current-state matrix;
2. if confirmed, open or retain atomic publication as the first candidate;
3. keep recoverable journaling as a separate design question requiring a phase-interruption and replay contract.

Self-review is not independent acceptance.
