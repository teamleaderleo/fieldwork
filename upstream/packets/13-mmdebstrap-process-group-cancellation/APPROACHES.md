# Unit 13 approaches ledger

## In simple words

The selected repair gives each backend invocation one caller-owned process group and sends cancellation to that group. Wrapper-only termination loses because nested work survives. Stronger escalation remains deferred because only synthetic evidence supports it.

The original Linux Fieldwork carrier remains the technical history. A byte-identical current-main restack on PR #406 is the selected delivery-reconciliation approach.

## Selected product approach

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

## Selected carrier approach

### Byte-identical current-main restack

Latest review accepted the bounded mechanism and rejected the stale delivery identity after Linux Fieldwork `main` changed governing workflow and tests.

Selected repair:

- start `repair/313-current-main-reconciliation` from exact `main@6cc74d846c50b9bbb88247e8a128b67e8c174c1e`;
- copy the exact nine blob SHAs from `fix/coverage-backend-process-group@dfc6d0503fb844f4c428ce16a567a9fdcd35280a`;
- create source head `e82b9b059850fce1efcf8daadef89049495a8b27`;
- execute current Linux Fieldwork CI through [PR #406](https://github.com/teamleaderleo/linux-fieldwork/pull/406);
- renew complete-diff review after the gate.

Why it wins:

- preserves every accepted source and evidence byte;
- establishes one pinned current base;
- lets current discovery, patch validation, and signal/result controls test the carrier;
- avoids rewriting or force-moving the historical PR #313 branch;
- separates ancestry repair from product-policy changes.

## Executed losing approaches

### Imported wrapper-only termination

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

### Reuse stale merge-ref receipt as current evidence

Rejected. CI 931/943 remains valid for its exact source and generated merge. It cannot support current-main compatibility after governing workflow and test inputs moved.

### Force-update historical PR #313 onto current main

Rejected for this repair. PR #313 is the canonical development and review history. A separate one-commit restack provides a clearer ancestry fence and preserves old receipts.

### Use PR #358 as the reconciliation carrier

Rejected after live inspection. PR #358 is a closed, unrelated broad mmdebstrap fixture contract repair. The review cross-reference is stale or misdirected for unit 13. PR #406 owns this unit's current-base execution.

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

## Packet fixture repair

### Original absolute-path harness

Preserved as `fixtures/local-process-model/harness_original.py` because it is the exact first-run source.

It loses as the default replay because it:

- requires `/tmp/unit13-probe`;
- waits only for `child-ready` before reading `wrapper-ready`;
- has limited failure cleanup.

### Relocatable reviewed harness

Selected as `fixtures/local-process-model/harness.py` because it:

- resolves sibling files through `__file__`;
- waits for both readiness markers;
- detects early driver exit;
- cleans every retained PID in `finally`;
- compiles and produces the same exact output.

This changes packet reproducibility only. It does not change the product mechanism or evidence conclusion.

## Carrier repairs and supersession

- CI 885: historical status-only fixture used an incompatible strict patch policy.
- CI 906: candidate patch declared incorrect hunk counts.
- CI 921: corrected counts retained stale source context.
- [PR #332](https://github.com/teamleaderleo/linux-fieldwork/pull/332) repaired context but closed as byte-identical duplicate after the parent moved.
- CI 927: QEMU losing controls deadlocked by waiting for the driver before releasing the deliberately surviving operation.
- CI 931: fixture ordering repaired; complete historical Fieldwork gate passed.
- [PR #336](https://github.com/teamleaderleo/linux-fieldwork/pull/336) closed after divergent same-file ancestry prevented a merge state.
- [PR #339](https://github.com/teamleaderleo/linux-fieldwork/pull/339) is the refined QEMU evidence successor at `8253ab2ef6fed22b34fc5f5d6d20cda75c25e2c7`.
- [PR #406](https://github.com/teamleaderleo/linux-fieldwork/pull/406) is the current-main delivery-reconciliation carrier at `e82b9b059850fce1efcf8daadef89049495a8b27`.

## Adjacent questions excluded

- repeated SIGINT during cleanup;
- TERM-resistant or TERM-deferring descendants;
- bounded group-drain diagnostics and escalation;
- descendants that create another group or session;
- full interactive QEMU/debvm and `/dev/tty` behavior;
- package operations, mounts, network, and non-Linux semantics.

These questions remain outside unit 13's selected source patch unless real target evidence makes one a prerequisite.
