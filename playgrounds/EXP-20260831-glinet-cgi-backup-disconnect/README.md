# Experiment: disconnected `cgi-io` backup response

Experiment ID: `EXP-20260831-glinet-cgi-backup-disconnect`

State: `complete`

Claim scope: `mechanism`

## In simple words

OpenWrt's `cgi-backup` helper streams a configuration archive from `sysupgrade` to the browser. If the browser disappears, the stream operation can fail before it consumes the archive pipe. The helper then waits for `sysupgrade`, while `sysupgrade` is blocked trying to fill the pipe that the helper stopped reading.

```text
browser disconnects
      ↓
splice(child pipe → CGI response) returns EPIPE
      ↓
cgi-io waits for sysupgrade ─────┐
      ↑                          │
      └── full pipe ← sysupgrade ┘
```

The synthetic model reproduced that cycle twice. A connected negative control transferred the complete two-MiB payload and exited normally. This establishes the pipe-ordering mechanism, not how often it occurs across routers or whether a particular web server should own disconnect cleanup.

## Why this was tested

On 2026-08-31, a GL.iNet Beryl 7 running GL.iNet firmware 4.9.0 had one `cgi-backup` process tree that had survived for about 2.5 days after its client-side pipes lost every external peer. `cgi-backup` slept in `do_wait`; its `tar`/`gzip` descendants slept in `pipe_wait`. Exact PID and start-time checks preceded a PID-scoped cleanup. No router setting or daemon was changed, and connectivity remained available.

That observation suggested a specific mechanism, but it did not by itself prove the source-level cause. This experiment models only the installed code's ordering with synthetic bytes and no network access.

## Source and version boundary

The router's `/www/cgi-bin/cgi-backup` symlink resolved to `/usr/libexec/cgi-io`:

- package: `cgi-io 2022-08-10-901b0f04-21`;
- architecture: `aarch64_cortex-a53`;
- binary SHA-256: `918cd7aa73e603e300085a78a9d65ecbea6c7651684029d3c7927ca507915b90`;
- source revision: [`901b0f0463c9d16a8cf5b9ed37118d8484bc9176`](https://github.com/openwrt/cgi-io/commit/901b0f0463c9d16a8cf5b9ed37118d8484bc9176).

At that revision, `main_backup()` forks `sysupgrade --create-backup -`, splices the child's output to file descriptor 1, exits the splice loop after an error other than `EINTR`, and then calls `waitpid()`. Current upstream master at [`31cb3c89f02d918d7f17bf62a80c852fc38a1ca1`](https://github.com/openwrt/cgi-io/commit/31cb3c89f02d918d7f17bf62a80c852fc38a1ca1) retains that ordering.

Evidence labels: the source ordering is **Documented**; the single-router process graph is **Observed**; the connection between them was **Inferred** until the synthetic model executed.

## Question and competing explanations

Can a disconnected response reader produce the observed `waitpid`/`pipe_wait` cycle?

| Observation | Interpretation |
|---|---|
| Connected reader drains the stream; both processes exit. | Negative control: the payload and process model can terminate normally. |
| Disconnected reader makes `splice()` return `EPIPE`; CGI and producer remain blocked. | Supports the source-ordering hypothesis. |
| Disconnected reader still allows both processes to exit. | Weakens the hypothesis; another router-specific owner is required. |

An alternative explanation remains possible for the original field event: `fcgiwrap`, nginx, or GL.iNet-specific glue may have altered file-descriptor lifetime before the snapshot. The experiment does not reconstruct that full stack.

## Command and environment

```text
python3 run.py
```

- Ubuntu 26.04, Linux `7.0.0-30-generic` x86_64;
- Python `3.14.4`;
- standard library only;
- network disabled;
- synthetic two-MiB payload;
- processes created by the model are PID-scoped and reaped during cleanup.

## Result

Both retained runs met the distinguishing expectations:

- connected control: `splice_errno=0`, full 2,097,152-byte response, `waitpid_completed=true`;
- disconnected case: `splice_errno=32` (`EPIPE`), `waitpid_completed=false`, CGI in `do_wait`, producer in `pipe_write`;
- model pipe capacity: 65,536 bytes, smaller than the synthetic payload;
- no model process survived cleanup.

Raw receipts: [`results/run-1.json`](results/run-1.json) and [`results/run-2.json`](results/run-2.json).

## Change thesis and boundary

Current behavior can stop draining the child pipe after a response-side error and then wait indefinitely for a child that cannot finish writing. A candidate improvement should preserve streaming while ensuring that response failure cannot strand the producer or CGI worker—for example, by terminating/reaping the owned child on an unrecoverable transfer error, or by continuing to drain before waiting. Source and integration review must choose the repair owner and confirm signal, exit-status, partial-response, and web-server behavior.

This is not a patch and not a live-router reproduction. It does not establish ecosystem frequency, prove that the 2.5-day worker materially caused the router OOM, or choose between cleanup strategies. The stale tree used little RSS; it consumed one of four CGI workers and four processes, while the OOM evidence showed broader system memory pressure.

## Disposition

Retain as a completed mechanism experiment and maintainer-ready lead. A human may use it to prepare an upstream report or candidate test. Automated third-party upstream contact remains prohibited, and no upstream mutation was attempted.

No secrets, session IDs, configuration paths, backup content, addresses, or production payloads are retained.
