# Unit 13 deep dive

## In simple words

`coverage.py` launches one selected backend wrapper per test. A wrapper can own nested shells, pipelines, a QEMU-style foreground operation, or a privileged sudo worker. Parent-only SIGINT currently reaches the Python driver alone. Terminating only the wrapper leaves nested work able to continue. The selected patch creates one process group before backend execution and sends TERM to that complete in-group operation.

## Target and exact source

- upstream project: mmdebstrap
- canonical upstream repository: `https://salsa.debian.org/debian/mmdebstrap.git`
- inspected release/tag: `debian/1.5.7-3`
- resolved source commit: `6fde999741f4fe1e7bf38079acf29432ef87a35e`
- imported Fieldwork commit: `782774b01002abf37878d834a54d0bbf8b226397`
- imported `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- inspected current upstream `main`: `77ec9be5417ee44c96343d2347145585da1b1f94`
- retrieval date: 2026-08-01

The relevant `coverage.py` lifecycle on current upstream main remains byte-equivalent to the imported blob in the inspected mirror: `Popen(argv)`, `proc.terminate()`, `proc.wait()`, then `break`.

Pinned imported source: [coverage.py at `782774b…`](https://github.com/teamleaderleo/linux-fieldwork/blob/782774b01002abf37878d834a54d0bbf8b226397/upstream/mmdebstrap/coverage.py#L412-L423).

## Current behavior and invariant

The driver chooses a backend command and waits for its immediate wrapper. Under parent-PID-only SIGINT, Python raises `KeyboardInterrupt` in the driver. The imported handler sends TERM only to the wrapper PID.

The governing invariant is:

> A cancellation acknowledged by the coverage driver must reach the complete backend operation boundary that the driver created, while ordinary execution preserves the existing result path.

Exit status and operation cancellation are separate. Returning 130 while descendants continue still violates the operation invariant.

## Source ownership map

### Entrypoint

`coverage.py` parses `coverage.txt`, selects a backend command, starts one wrapper, and owns the wait/result loop.

### Backend wrappers

- `run_null.sh` can create nested shells, `tee`, a status reader, and the generated test process.
- `run_qemu.sh` can create an output follower plus a foreground `timeout --foreground` QEMU/debvm operation.
- `run_null.sh SUDO` can create a sudo command and UID-0 worker.

### State and side effects

The driver owns the immediate `Popen` object and final suite status. The wrappers own nested process topology and target work. Later work can mutate logs, exit-status files, generated artifacts, mounts, or package state after the driver has acknowledged cancellation.

## Deterministic distinction

Under SIGINT sent only to the driver PID:

| Variant | Driver result | Nested operation | Later work |
| --- | ---: | --- | --- |
| imported baseline | 0 after losing-control release | survives wrapper TERM | yes |
| status-only predecessor | 130 after release | survives wrapper TERM | yes |
| caller-owned group | 130 | TERM reaches tested responsive group | no |

The selected design changes the owner boundary before execution:

```python
proc = subprocess.Popen(argv, start_new_session=True)
try:
    proc.wait()
except KeyboardInterrupt:
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    proc.wait()
    print("interrupted by SIGINT", file=sys.stderr)
    raise SystemExit(130)
```

Pinned patch: [candidate at `dfc6d050…`](https://github.com/teamleaderleo/linux-fieldwork/blob/dfc6d0503fb844f4c428ce16a567a9fdcd35280a/investigations/mmdebstrap-coverage-process-group/0001-own-backend-process-group.patch).

## Why the caller owns the repair

The caller selects the backend and can establish a backend-independent operation identity before any wrapper creates descendants. This provides one signal boundary across current and future in-group descendants without process-tree enumeration.

`start_new_session=True` makes the immediate child the session leader and process-group leader, so its PID is the group ID used by `killpg`.

`ProcessLookupError` handles a wrapper/group that exits between interruption and signal delivery.

The second `proc.wait()` preserves wrapper reaping. It does not prove arbitrary descendant quiescence; the no-survivor result comes from executed controls for responsive topologies.

## Exact tests and links

- null topology: [test module at `dfc6d050…`](https://github.com/teamleaderleo/linux-fieldwork/blob/dfc6d0503fb844f4c428ce16a567a9fdcd35280a/tests/test_mmdebstrap_coverage_process_group.py)
- QEMU topology, refined evidence: [test module at `8253ab2e…`](https://github.com/teamleaderleo/linux-fieldwork/blob/8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7/tests/test_mmdebstrap_coverage_qemu_process_group.py)
- sudo topology: [test module at `dfc6d050…`](https://github.com/teamleaderleo/linux-fieldwork/blob/dfc6d0503fb844f4c428ce16a567a9fdcd35280a/tests/test_mmdebstrap_coverage_sudo_process_group.py)
- canonical investigation: [README at `dfc6d050…`](https://github.com/teamleaderleo/linux-fieldwork/blob/dfc6d0503fb844f4c428ce16a567a9fdcd35280a/investigations/mmdebstrap-coverage-process-group/README.md)

## Compatibility

### Supported by evidence

- Linux/POSIX process groups and `/proc`-observed lifecycle controls;
- exact imported null wrapper;
- exact imported QEMU wrapper with the expensive foreground payload substituted;
- actual passwordless sudo path on the CI runner;
- inherited terminal file-descriptor input/output in a reduced PTY comparison;
- ordinary unsignaled success for each retained topology.

### Risks and limits

- A descendant can escape with `setsid()` or a new process group.
- A TERM-resistant descendant can outlive the wrapper after `proc.wait()` returns.
- A repeated SIGINT can replace the first result during cleanup.
- A new session has no controlling-terminal association, so direct `/dev/tty` behavior remains unproved.
- Real QEMU/debvm, mounts, network, package operations, and other operating systems remain unexecuted.
- PGID reuse was not exercised; the signal follows immediately after a caught interruption while the wrapper is expected to exist, and `ProcessLookupError` handles an absent group.

## Stronger cleanup comparison

Issue #341 and PR #347 compared TERM resistance, repeated SIGINT, bounded diagnostics, and TERM-to-KILL. TERM-to-KILL drained the synthetic in-group topology, while no real backend evidence justified selecting escalation. Unit 13 therefore retains the narrow responsive-topology contract.

## Duplicate and prior-art result

A bounded 2026-08-01 search of the current upstream Gitea/Salsa issue and merge-request surfaces for `SIGINT`, `KeyboardInterrupt`, `killpg`, `process group`, and the `coverage.py` handler found no matching public repair. Current upstream source still contains the imported lifecycle. This is a search result, not a guarantee that private, unindexed, mailing-list, or future work is absent.

Internal prior art consists of the status-only repair (#141, #143, #204), the canonical process-group carrier (#306, #313), the QEMU evidence successor (#339), and the deferred escalation comparison (#341, #347, #353).

## Current technical answer

The bounded mechanism is accepted for group-wide TERM delivery and settlement in the tested responsive topologies. Delivery remains incomplete because the source exists only as a retained patch inside Linux Fieldwork, with no clean target fork branch or current-upstream target-native gate.