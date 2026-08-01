# Experiment: curl destination pre-truncation

Experiment ID: `EXP-20260801-curl-fopen-pretruncate`

State: `complete`

Target label: none registered at snapshot

Target hub: none registered at snapshot

Testbed label or neutral identifier: installed curl 8.10.1

Claim scope: `mechanism`

Integration context: none

Related work: Fieldwork issue #470; systems and CLI scout Round 003

Owner: ChatGPT systems-cli scout

Date: 2026-08-01

## In simple words

curl saves HSTS state through a helper that is supposed to write a temporary file and replace the final cache only after the new data is ready. Current code first opens the final path in write mode. That can destroy the old file before the temporary-file transaction begins.

This experiment used only temporary files and a refused loopback connection. On curl 8.10.1, a 16-byte symlink target became empty before the symlink path was replaced, and a 10,801-byte HSTS cache became a 1,024-byte partial cache under a file-size limit. Both results repeated exactly.

The result supports a bounded mechanism claim: the installed curl does not preserve the prior destination across these two persistence boundaries. It does not yet prove a candidate against current upstream master.

## Question

Does curl preserve an existing HSTS destination and a symlink target until its replacement cache has been written successfully?

## Why this experiment

The current multi-repository scout ranked curl issue #21610 first because the behavior can destroy persistent user state and has a small local reproducer. The upstream discussion favors reverting the open-first change, but the first useful Fieldwork step is an independent, repeatable baseline with clear capability and evidence boundaries.

## Change thesis

- **current behaviour:** non-Windows `Curl_fopen()` opens the final path with write/truncate mode before `fstat`, random temp-name generation, temp creation, writing, and rename;
- **consequence:** an existing cache or a symlink target can lose data before the replacement transaction succeeds;
- **candidate improvement:** restore a pre-open classification step and keep existing regular destinations untouched until rename succeeds;
- **evidence boundary:** this experiment executes installed curl 8.10.1 and inspects current upstream source separately. It does not execute a current-master build or a candidate patch.

## Scope boundary

The supported claim is mechanism-only:

- HSTS persistence through the installed curl command;
- Linux filesystem behavior for a symlink-to-regular destination;
- Linux `RLIMIT_FSIZE` behavior in a child process;
- two repeat runs in one environment.

The result does not establish cross-platform behavior, the exact current-master runtime result, the best upstream policy for symlinks and special files, or caller behavior for Alt-Svc and cookies.

## Sources and environment

### Sources

- curl issue 21610, retrieved 2026-08-01, documents the reported truncation mechanisms and owning callers. Evidence label: `Documented`.
- curl `lib/curl_fopen.c` at `527573490eb2564b3d7c9dd51d8bff963b5d6303`, retrieved 2026-08-01, shows the current open-before-`fstat` sequence. Evidence label: `Observed` source state.
- curl commit `0c667188e0c6cda615a036b8a2b4125f2c404dde`, retrieved 2026-08-01, shows the exact change from `stat()`-before-open to open-before-`fstat`. Evidence label: `Observed` change history.

### Environment

- system: Linux `6.12.13`, x86_64, glibc 2.41;
- runtime: Python 3.13.5;
- command: curl 8.10.1 with HSTS support;
- user: root inside a disposable container;
- dependencies: Python standard library and installed curl;
- relevant configuration: child `RLIMIT_FSIZE=1024`, `SIGXFSZ` ignored;
- network policy: no external network; refused connection to `127.0.0.1:1` only.

Running as root is why the experiment does not use an unwritable-directory control. The file-size limit and symlink fixtures remain effective under root.

## Inputs

### Symlink fixture

```text
target.txt: "DO NOT TRUNCATE\n" (16 bytes)
hsts.txt -> target.txt
```

### Limited-write fixture

A syntactically HSTS-like cache containing two header lines and 300 host entries, totaling 10,801 bytes, with the curl child limited to 1,024-byte files.

No production data, credentials, external hosts, or retained mutable fixtures were used.

## Command

```text
python3 run.py --output results/latest.json
```

An alternate curl binary can be selected with:

```text
python3 run.py --curl /path/to/curl --output results/latest.json
```

## Distinguishing outcomes

| Observation | Interpretation |
| --- | --- |
| symlink target remains 16 bytes | installed curl did not reproduce target pre-truncation |
| symlink target becomes shorter before destination becomes a regular HSTS file | installed curl reproduced final-path open/truncate before replacement |
| 10,801-byte cache remains intact under the 1,024-byte limit | previous destination was preserved across later persistence failure |
| cache becomes shorter and no separate write error is reported | previous complete destination was not protected by an atomic all-or-nothing boundary |

## Procedure

1. Resolve the selected curl binary and retain its first version line.
2. Create a `TemporaryDirectory`.
3. Create the symlink fixture and invoke curl with `--hsts` against the refused loopback endpoint.
4. Record command status, stderr, target size, destination type, and destination size.
5. Create the 10,801-byte HSTS fixture.
6. Spawn curl with `RLIMIT_FSIZE=1024` and `SIGXFSZ` ignored.
7. Record command status, stderr, and before/after cache sizes.
8. Serialize the result to JSON.
9. Exit success only when both truncation mechanisms reproduce.
10. Repeat the command and compare the distinguishing values.
11. Allow `TemporaryDirectory` cleanup to remove every mutable artifact.

## Actual result

Both runs produced the same values:

- symlink target: 16 bytes before, 0 bytes after;
- destination path after the run: regular file, 111 bytes;
- limited HSTS cache: 10,801 bytes before, 1,024 bytes after;
- curl status: 7, caused by the refused connection;
- stderr: transfer failure only; no separate write-error text.

The runner returned success because both expected baseline mechanisms reproduced.

## Raw evidence

- machine-readable result: `results/latest.json`;
- interpretation and repeat receipt: `results/notes.md`;
- runner: `run.py`;
- fixtures: generated at runtime below `TemporaryDirectory`;
- repeated-run information: two runs, both `target_after_bytes=0`, `destination_after_type=regular`, `cache_after_bytes=1024`, and `write_error_reported=false`.

## Interpretation

The symlink result directly supports the open-first mechanism: the final path was followed and its target truncated before the symlink path became a regular HSTS file.

The file-limit result supports the broader persistence consequence: curl did not retain the previous complete cache when the replacement output could not exceed 1,024 bytes. It does not by itself distinguish initial destination truncation from partial temp output followed by rename. A direct helper harness with deterministic lifecycle fault injection is needed for that separation.

Current upstream source inspection shows the same open-first sequence at revision `527573...`, so a current-master build is likely to reproduce. That statement remains `Inferred` until the exact revision is built and executed.

## Owned-repository trial

A separate owned-application trial is not required for the mechanism baseline. curl's own HSTS command path exercises the persistence helper directly enough for this bounded question.

Caller-wide claims for HSTS, Alt-Svc, and cookie persistence should use curl's native tests or a current-source direct harness rather than a separate application.

## Wider integration context

No operational or ecosystem claim is made. The issue report identifies HSTS, Alt-Svc, and cookie callers, but this experiment executed HSTS only.

## Uncertainty and threats to validity

- installed curl 8.10.1 is older than inspected current master;
- only Linux x86_64 was executed;
- root execution excludes permission-denial behavior;
- the loopback transfer fails before any useful response, although curl still performs HSTS persistence during cleanup;
- status 7 masks whether a persistence error would otherwise affect the command result;
- the file-limit case does not identify which lifecycle stage produced the final 1,024-byte file;
- the runner does not test successful mode inheritance, new paths, non-regular destinations, Alt-Svc, or cookies;
- the correct policy may be a semantic revert using `stat()` or a broader hardening change using `lstat()`/`O_NOFOLLOW`; those policies differ for symlinks and special files.

## Reproduction status

- [x] Plain-language block updated
- [ ] Target label and hub recorded — no curl target hub was found
- [x] Exact command recorded
- [x] Source revisions or versions recorded
- [x] Evidence labels used for wider claims
- [x] Deterministic in the declared environment
- [x] Repeated run available
- [ ] Independent reproduction available
- [ ] Cross-platform result available
- [ ] Negative result

## Disposition

Retain as a completed mechanism experiment and promote the next step through Fieldwork issue #470:

1. build current curl head;
2. reproduce both controls on that exact revision;
3. add a direct `Curl_fopen()` harness with deterministic fault injection;
4. compare semantic revert and hardening policies without conflating them;
5. keep all external contact unauthorized until explicitly changed.

## Boundaries

- Upstream contact remains unauthorized.
- No secrets, production payloads, or proprietary inputs were retained.
- This mechanism result is not presented as cross-platform or general operational proof.
