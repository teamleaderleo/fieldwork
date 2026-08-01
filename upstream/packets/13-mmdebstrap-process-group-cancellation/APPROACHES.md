# Unit 13 approaches ledger

## In simple words

The selected repair gives each backend invocation one caller-owned process group and sends cancellation to that group. Wrapper-only termination loses because nested work survives. Stronger escalation remains deferred because only synthetic evidence supports it.

## Selected approach

### Caller-owned session/process group

```python
proc = subprocess.Popen(argv, start_new_session=True)
...
os.killpg(proc.pid, signal.SIGTERM)
proc.wait()
raise SystemExit(130)
```

Why it wins:

- `coverage.py` selects the backend and can establish the operation boundary before backend code runs;
- one backend-agnostic boundary covers the exact null, QEMU-wrapper, and sudo topologies;
- parent-only SIGINT reaches nested in-group work;
- ordinary unsignaled behavior stays unchanged in the executed controls;
- the implementation adds no backend-specific process discovery or escalation policy.

Retained source: [candidate patch at `dfc6d050…`](https://github.com/teamleaderleo/linux-fieldwork/blob/dfc6d0503fb844f4c428ce16a567a9fdcd35280a/investigations/mmdebstrap-coverage-process-group/0001-own-backend-process-group.patch).

## Executed losing approaches

### Imported wrapper-only termination

Behavior:

```python
proc = subprocess.Popen(argv)
...
proc.terminate()
proc.wait()
break
```

Result: the immediate wrapper receives TERM; nested work can remain live and perform later work. The driver may also reach the normal success epilogue and return 0.

### Status-only repair

Behavior: keep wrapper-only termination, print an interruption diagnostic, and return 130.

Result: exit status becomes accurate while nested backend work can still survive. This proves status correctness and cancellation delivery are separate requirements.

Historical records:

- [issue #141](https://github.com/teamleaderleo/linux-fieldwork/issues/141)
- [historical PR #143](https://github.com/teamleaderleo/linux-fieldwork/pull/143) at `96ddac76ab9dead7875937a6edfa37137bc52eb9`
- [merged Fieldwork restack PR #204](https://github.com/teamleaderleo/linux-fieldwork/pull/204) at `b5efc8faf35c1da725a3b995a344fadc078ad5d2`

### Backend-specific descendant discovery

Rejected because the caller would need to understand evolving shell, pipeline, QEMU, sudo, and future backend topologies. Establishing one group before launch is smaller and more stable.

### Same-session background process group

Rejected after the retained PTY comparison: background process groups can stop on terminal input. A new session preserves inherited file-descriptor I/O in the reduced control while removing a controlling-terminal association.

### Immediate claim of complete group quiescence

Rejected. `proc.wait()` waits for the immediate wrapper only. The claim is limited to complete settlement in the executed TERM-responsive topologies.

### TERM-to-KILL escalation

Compared in [issue #341](https://github.com/teamleaderleo/linux-fieldwork/issues/341) and [PR #347](https://github.com/teamleaderleo/linux-fieldwork/pull/347) at `615bd4f5256d9851f682e48e037169ceeb7bb98c`.

Synthetic controls found that bounded TERM-to-KILL drained the tested resistant group and retained final status. Selection remains deferred because no real mmdebstrap backend demonstrated a need, no grace interval was justified, and KILL can discard backend cleanup.

Reopening trigger: a real backend ignores or materially defers TERM, outlives its wrapper, or establishes an operational repeated-SIGINT requirement.

## Carrier repairs and supersession

- CI 885: historical status-only fixture used an incompatible strict patch policy.
- CI 906: candidate patch declared incorrect hunk counts.
- CI 921: corrected counts retained stale source context.
- [PR #332](https://github.com/teamleaderleo/linux-fieldwork/pull/332) repaired context but closed as byte-identical duplicate after the parent moved.
- CI 927: QEMU losing controls deadlocked by waiting for the driver before releasing the deliberately surviving operation.
- CI 931: fixture ordering repaired; complete Fieldwork gate passed.
- [PR #336](https://github.com/teamleaderleo/linux-fieldwork/pull/336) closed after divergent same-file ancestry prevented a merge state.
- [PR #339](https://github.com/teamleaderleo/linux-fieldwork/pull/339) is the clean evidence successor at `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`.

## Adjacent questions excluded

- repeated SIGINT during cleanup;
- TERM-resistant or TERM-deferring descendants;
- bounded group-drain diagnostics and escalation;
- descendants that create another group or session;
- full interactive QEMU/debvm and `/dev/tty` behavior;
- package operations, mounts, network, and non-Linux semantics.

These questions remain outside unit 13's selected source patch unless real target evidence makes one a prerequisite.