# Candidate issue and pull-request packets

Issue: #122

State: internal drafting only

Upstream contact authorized: false

These packets separate observations that can support a narrow patch from questions that require an architectural decision. They are not defect claims until the corresponding engine-level barrier runs at the pinned source revision.

## DataFusion candidate A — abort on ordinary Parquet writer error

### Why this may be a narrow pull request

The sequential Parquet task owns `AsyncArrowWriter<BufWriter>`. The pinned Arrow Parquet API provides:

- non-consuming `finish(&mut self)`;
- consuming `into_inner(self)`;
- `BufWriter::abort(&mut self)`.

DataFusion currently calls consuming `close()` on the normal path. A narrow experiment can replace that with `finish()` and, when a write or finish operation returns an error, recover the underlying `BufWriter` and call `abort().await` before returning the initiating error.

### Required behavior

- preserve the first writer or Parquet error as primary;
- attach or log abort failure as secondary cleanup information;
- never complete the object after the initiating error;
- verify zero retained multipart state when abort succeeds;
- leave the successful close path unchanged.

### Required tests

1. multipart part failure after output begins;
2. Parquet finalization failure;
3. abort succeeds;
4. abort fails while the initiating error remains primary;
5. successful publication still completes exactly once.

### Limitation

This does not solve cancellation by dropping the result stream. Once the entire writer future is dropped, async cleanup cannot run inside that future.

## DataFusion candidate B — cancellation-safe publication supervisor

### Why this is probably an issue before a pull request

Dropping `DataSinkExec`'s result stream drops `sink.write_all`. The Parquet sink's task set is then dropped, and its Tokio-backed writer tasks are aborted. The underlying multipart writer is dropped before an awaited abort can run.

A cancellation-safe design needs structured ownership rather than a local error branch. Plausible designs include:

1. a publication supervisor task that outlives the result stream long enough to abort writers;
2. a cancellation token signalled by result-stream drop, with the supervisor performing abort and recording cleanup completion;
3. a generic file-sink publication handle with `commit`, `abort`, and `unknown` terminal states.

### Decision questions

- May cleanup continue after the query result stream is dropped?
- Where are cleanup errors reported when the caller no longer awaits the result?
- What bounded shutdown guarantee applies when the runtime itself is terminating?
- Should the design cover CSV and JSON sinks as well as Parquet?
- Which metrics expose retained upload state and cleanup latency?

### Required engine barrier

Cancel after the first multipart part is accepted and record writer-task termination, abort, complete, upload drop, final visibility, retained parts, cleanup latency, and same-destination retry.

## DuckDB candidate A — query-affine failed teardown signal

### Narrow source direction

Replace the process-wide failed-query teardown boolean with the active query identifier:

- capture the originating active query number when the S3 handle initializes;
- publish the failed query number before active query state is destroyed;
- suppress implicit completion only when the handle's captured identifier matches the failed query identifier;
- use an invalid sentinel for handles created outside an active query.

### Required controls

- stale handle survives into a later failed query;
- handle destroyed after the teardown window ends;
- direct handle with no active query;
- ordinary writer error;
- successful implicit close;
- cleanup failure does not replace the initiating query error.

## DuckDB candidate B — explicit multipart abort

The pinned HTTPFS source has initialize and finalize operations but no multipart abort primitive. This should remain separate from query-affine containment.

A bounded repair needs:

- S3 AbortMultipartUpload request support;
- explicit upload lifecycle states;
- idempotent abort behavior;
- retained-part verification in the mock server;
- abort on ordinary writer failure and failed-query teardown;
- secondary reporting for abort failure;
- no abort after a known successful completion.

## DuckDB candidate C — clarify cooperative timeout semantics

The pinned engine records `max_execution_time` as a deadline but samples it cooperatively in `InterruptCheck`. A synchronously blocked remote request is not a strict wall-clock watchdog.

A documentation candidate should distinguish:

- cooperative engine timeout;
- explicit connection interruption;
- application-level hard timeout or watchdog;
- cleanup completion after cancellation.

This packet should be considered only after the focused remote-I/O control is stable.

## Polars candidate — classify local publication before remote cleanup

The first Polars experiment should use a local temporary destination and cancel after Parquet row-group output begins.

Record:

- whether a final path appears;
- whether a temporary path remains;
- footer validity and readable row count;
- cancellation-to-return and cancellation-to-close latency;
- retry to the same path;
- explicit cancel versus dropping `InProcessQuery`.

Only after this boundary is known should a remote object-store cleanup claim be drafted.

## Promotion rules

A candidate becomes an upstream-ready packet only when it has:

1. an exact source revision;
2. a deterministic timing barrier;
3. an executed positive or negative control;
4. a classified visible or retained side effect;
5. a likely owning subsystem;
6. a minimal repair surface;
7. regression tests that distinguish publication, abort, drop, and unknown commit state.

No upstream interaction occurred.
