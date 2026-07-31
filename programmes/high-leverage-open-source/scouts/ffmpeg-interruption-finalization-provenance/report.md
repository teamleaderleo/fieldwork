# FFmpeg interruption, finalization, and media provenance

State: `target-executed`

## In simple words

FFmpeg can report that an encode was interrupted while still leaving a valid, shorter MP4 at the requested output pathname. A hard kill leaves an existing file that the matching `ffprobe` cannot parse.

An application that owns publication should therefore separate “FFmpeg produced bytes” from “the application accepted this output.” In the executed absent-destination fixture, writing to a temporary pathname and renaming only after status `0` kept the final pathname absent after interruption while preserving the partial file for inspection or cleanup.

## Identity

- Fieldwork issue: #125
- Programme: #114, high-leverage open source
- Worker: `chatgpt:gpt-5.6-thinking`
- Fieldwork branch: `scout/125-ffmpeg-interruption-finalization`
- Executed Fieldwork head: `2abc0ce4e61a05792f42e081a76eccdcb26b4348`
- Fieldwork base: `896a617c4b4dd8dd9fb9493d05f801c7baf9ade3`
- Owned path: `programmes/high-leverage-open-source/scouts/ffmpeg-interruption-finalization-provenance/`
- Stable target: FFmpeg 8.1.2, tag commit `38b88335f99e76ed89ff3c93f877fdefce736c13`
- Development retrieval fence: `86940d45aff7d59810794df3ab2b39b7b83b478c`
- Retrieval date: 2026-07-31
- Native execution run: `30584720219`
- Executed-head Fieldwork integrity: `30584720190`
- Artifact: `8777658832`
- Artifact digest: `sha256:cbb23ce99d6c1f37470dc37d4f242d83cec303f08dc2939403bccd2536ef656a`
- Upstream contact authorized: `no`
- Upstream interaction performed: `none`

## Bounded question

When an ordinary MP4 encode is interrupted after packets have reached the output:

1. does a single graceful `SIGINT` leave a file at the requested final pathname;
2. does FFmpeg write a trailer and return a distinct interrupted status;
3. can `ffprobe` parse the resulting partial file;
4. how does that compare with `SIGKILL`, which bypasses cleanup;
5. starting from an absent destination, does application-level temporary-path staging keep the final pathname absent unless the process completes successfully?

## Source map

At development head `86940d45aff7d59810794df3ab2b39b7b83b478c`, `fftools/ffmpeg.c` records the received signal and increments `received_nb_signals`. The transcode loop observes that count, breaks, stops the scheduler, and continues into output trailer writing.

Relevant paths:

- `fftools/ffmpeg.c`: signal intake, transcode loop, and final process status;
- `fftools/ffmpeg_sched.c`: scheduler stop and worker settlement;
- `fftools/ffmpeg_mux.c`: output trailer, close, and final statistics;
- `libavformat/mux.c`: generic trailer dispatch;
- `libavformat/movenc.c`: MP4/MOV trailer and index metadata.

`transcode()` calls `of_write_trailer()` after `sch_stop()`. `of_write_trailer()` calls `av_write_trailer()`, closes the output IO context, and checks whether anything was written. `main()` returns `255` when a signal was received even when graceful cleanup completed.

This creates the observed application boundary: process status reports interruption while the requested pathname contains a parseable partial artifact.

## Executed experiment

Experiment ID: `EXP-20260731-ffmpeg-mp4-interrupt-publication`.

The exact stable target was built with a minimal native configuration. Synthetic video was encoded in four cases after the runner waited for packet-sized output growth.

### Completed control

```text
process status: 0
ffprobe status: 0
duration: 2.0 seconds
file exists: yes
file size: 223346 bytes
```

Disposition: ordinary successful publication control passed.

### Direct graceful interruption

```text
process status: 255
ffprobe status: 0
duration: 3.533333 seconds
file exists: yes
file size: 419217 bytes
```

Disposition: `SIGINT` followed the graceful finalization path. The producer reported interruption while the matching consumer parsed the partial MP4 successfully.

The interrupted file is larger than the completed control because the cases use different intended timing boundaries; size is evidence of packet progress, not a quality comparison.

### Direct hard kill

```text
process status: 137
ffprobe status: 1
duration: unavailable
file exists: yes
file size: 262188 bytes
```

Disposition: `SIGKILL` bypassed cleanup. Pathname existence did not imply a parseable MP4.

### Staged graceful interruption

The final pathname was absent before this case began.

```text
process status: 255
temporary ffprobe status: 0
temporary duration: 3.533333 seconds
temporary file exists: yes
temporary file size: 419217 bytes
final file exists: no
```

Disposition: temporary-path staging preserved the recoverable partial artifact while keeping the initially absent final pathname unpublished because rename authority required status `0`.

## Accepted findings

1. **Process outcome and media usability are separate facts.** Status `255` can accompany a valid, parseable partial MP4.
2. **Pathname existence is not an acceptance receipt.** It occurs in both graceful and hard-kill cases, with different consumer outcomes.
3. **Graceful interruption is observably different from hard death.** The graceful path writes enough final container metadata for parsing in this fixture.
4. **Application staging can withhold first publication.** For the executed absent-destination case, rename-on-success made final-path visibility depend on the application's acceptance rule rather than FFmpeg's first write.
5. **Recoverable partial output is not itself a core defect.** It can be useful for inspection or recovery; applications decide whether to publish, retain, or delete it.

Evidence class: `target-executed` for exact FFmpeg 8.1.2 under the named synthetic fixture.

## Application receipt pattern

For consequential media generation, retain a receipt with at least:

- exact input and tool identity;
- process status and terminating signal;
- temporary and final pathname identities;
- consumer parse status;
- observed duration or stream metadata;
- application acceptance decision;
- rename, cleanup, or quarantine outcome.

For a destination that is absent before the attempt, the executed publication sequence is:

1. choose a unique temporary pathname in the destination filesystem;
2. run FFmpeg against that temporary pathname;
3. retain process and probe receipts;
4. accept only under the application's explicit policy;
5. rename atomically to the final pathname on acceptance;
6. otherwise retain, quarantine, or delete the temporary artifact explicitly.

Replacing an existing accepted artifact is a stronger contract. It requires a separate control that proves the old final generation remains byte-for-byte unchanged and parseable after interrupted replacement work. That control was not executed here.

## Evidence boundary

The fixture preserves:

- ordinary file-protocol output;
- ordinary non-fragmented MP4 trailer dependence;
- executed `SIGINT` and `SIGKILL` outcomes with matching process status and logs;
- final-path visibility when the staged destination begins absent;
- consumer classification through the matching `ffprobe` build.

The retained runner waits for output growth before signaling, but it does not yet check `kill -0` immediately before every signal or install a cleanup trap for a live encoder after a harness failure. The exact receipt's signal log and statuses support the executed outcome; future reruns should add those liveness and cleanup controls before claiming a stronger reusable harness guarantee.

It does not establish:

- preservation or atomic replacement of an existing accepted final artifact;
- behavior for every format, muxer, protocol, encoder, or signal;
- Windows control-event behavior;
- disk-full or write-error settlement;
- application-specific quality or completeness thresholds;
- current-development runtime parity;
- production performance or large-input behavior.

## Current disposition

**ACCEPT the bounded producer mechanism and retain temporary-path staging as an executed first-publication pattern for an initially absent destination. STOP the core-defect search on this evidence.**

A new lane is justified only for a distinct contract: preserving an existing accepted artifact during replacement, format-specific finalization, write-error settlement, Windows interruption, network output, or an application that intentionally publishes graceful partial media.

The one-off execution workflow is retired after receipt transfer. The retained carrier consists of the report, experiment definition, and runner; the runner's unexecuted liveness/cleanup hardening remains explicit above.
