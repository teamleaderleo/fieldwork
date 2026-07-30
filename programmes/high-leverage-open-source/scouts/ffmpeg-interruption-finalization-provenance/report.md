# FFmpeg interruption, finalization, and media provenance

## In simple words

FFmpeg writes media packets while a command is running and usually writes container metadata when the command finishes. This first probe asks what an application sees when ordinary MP4 output is interrupted: a graceful signal may still produce a parseable partial file at the requested final pathname, while a hard kill may leave an unusable file. The immediate goal is to measure those states and test whether writing to a temporary pathname gives the application a clean publication decision.

## Identity

- Fieldwork issue: #125
- Programme: #114, high-leverage open source
- Worker: `chatgpt:gpt-5.6-thinking`
- Fieldwork branch: `scout/125-ffmpeg-interruption-finalization`
- Fieldwork base: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`
- Owned path: `programmes/high-leverage-open-source/scouts/ffmpeg-interruption-finalization-provenance/`
- Stable target: FFmpeg 8.1.2, tag commit `38b88335f99e76ed89ff3c93f877fdefce736c13`
- Development retrieval fence: `86940d45aff7d59810794df3ab2b39b7b83b478c`
- Retrieval date: 2026-07-31
- Upstream contact authorized: `no`
- Upstream interaction performed: `none`

## Bounded first question

When an ordinary MP4 encode is interrupted after packets have reached the output:

1. does a single graceful `SIGINT` leave a file at the requested final pathname;
2. does FFmpeg write a trailer and return a distinct interrupted status;
3. can `ffprobe` parse the resulting partial file;
4. how does that compare with `SIGKILL`, which bypasses cleanup;
5. does application-level temporary-path staging keep the final pathname absent unless the process completes successfully?

Claim scope begins at `mechanism/interface`. Any production or ecosystem consequence remains provisional.

## Source map

### Signal intake and scheduler stop

At development head `86940d45aff7d59810794df3ab2b39b7b83b478c`, `fftools/ffmpeg.c` records the received signal and increments `received_nb_signals`. The transcode loop observes that count, breaks, stops the scheduler, and continues into output trailer writing.

Relevant paths:

- `fftools/ffmpeg.c`: `sigterm_handler()`, `decode_interrupt_cb()`, `transcode()`, `main()`;
- `fftools/ffmpeg_sched.c`: scheduler stop and worker settlement;
- `fftools/ffmpeg_mux.c`: output trailer, close, and final stats;
- `libavformat/mux.c`: generic trailer dispatch;
- `libavformat/movenc.c`: MP4/MOV trailer and index metadata.

### Trailer and exit result

`transcode()` calls `of_write_trailer()` for every output after `sch_stop()`. `of_write_trailer()` calls `av_write_trailer()`, closes the output IO context, and checks whether anything was written. `main()` then returns `255` when any signal was received, even when the graceful cleanup path completed.

This creates an important application boundary: process status reports interruption, while the requested output pathname may contain a parseable partial artifact.

## Competing hypotheses

### H1 — graceful partial file

A single `SIGINT` stops work, writes the MP4 trailer, closes the file, leaves a parseable shorter media file at the final pathname, logs normal signal exit, and returns `255`.

### H2 — unusable interrupted file

The output exists but lacks enough final metadata for `ffprobe` to parse it, so graceful interruption resembles hard process death from the consumer's perspective.

### H3 — timing-dependent mixed state

Whether the output is parseable depends on whether a header and packets were written before interruption. The experiment waits for file growth before signalling so it tests the trailer boundary rather than the empty-output boundary.

### H4 — staging supplies publication authority

Writing to `name.tmp.mp4` and renaming only after exit status `0` leaves the final pathname absent after graceful interruption, while retaining the partial temporary artifact for explicit inspection or cleanup.

## Experiment

Experiment ID: `EXP-20260731-ffmpeg-mp4-interrupt-publication`.

The owned execution carrier builds FFmpeg 8.1.2 from the exact tag commit with a minimal native configuration, generates synthetic video, and runs four cases:

1. completed MP4 encode;
2. direct-to-final-path `SIGINT`;
3. direct-to-final-path `SIGKILL`;
4. temporary-path `SIGINT` with rename only on status `0`.

The runner retains command logs, process statuses, file sizes, `ffprobe` JSON or errors, and an assertion summary.

## Evidence boundary

Before the workflow runs, the source ordering is `source-read` and the shell case is `target-test-prepared`. No result is described as executed yet.

The synthetic fixture preserves:

- ordinary file protocol output;
- MP4 trailer dependence;
- real process signals;
- final-path visibility;
- consumer classification through the matching `ffprobe` build.

It omits:

- large or multi-stream production inputs;
- network protocols;
- hardware encoders;
- Windows control events;
- disk-full and injected write errors;
- application-specific acceptance rules;
- current-development execution.

## Initial change thesis

- **Current behaviour:** source inspection indicates graceful signal handling proceeds through trailer writing and returns interrupted status `255`.
- **Consequence:** an application that treats pathname existence as publication may expose a partial artifact even though the producer reports interruption.
- **Proposed improvement:** likely application-level staging and explicit acceptance, unless execution reveals an FFmpeg contract or diagnostic defect.
- **Evidence required:** exact stable-target execution, completed and hard-kill controls, consumer parse results, and raw logs.
- **Boundary:** recoverable partial output can be intentional and useful; the experiment does not presume a core FFmpeg bug.

## Next actions

1. Execute the exact stable target in the Fieldwork carrier.
2. Classify each output as absent, parseable partial, or unparseable.
3. Inspect current-development source for any divergence from the stable tag.
4. Decide whether to retain an application publication pattern, open a narrower diagnostic question, or stop with expected behavior.
