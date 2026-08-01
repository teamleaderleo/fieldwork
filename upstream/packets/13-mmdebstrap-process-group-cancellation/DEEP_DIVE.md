# Unit 13 deep dive

## In simple words

`coverage.py` launches one selected backend wrapper per test. A wrapper can own nested shells, pipelines, a QEMU-style foreground operation, or a privileged sudo worker. When SIGINT reaches only the Python driver, terminating the immediate wrapper leaves nested work able to continue. The selected patch creates a dedicated session/process group before backend execution and sends TERM to that complete in-group operation.

The mechanism has exact canonical-source focused execution. Under the #435 completion contract, the remaining work is delivery packaging: controlled fork, clean target branch, upstream-native regression, ordinary source gate, and final target-diff review.

## Canonical source

- project: mmdebstrap
- canonical repository: `https://gitlab.mister-muffin.de/josch/mmdebstrap`
- canonical branch: `main`
- exact base executed: `77ec9be5417ee44c96343d2347145585da1b1f94`
- last commit touching `coverage.py`: `c82fc7e261c7a2fd85e499484108408fd42331d2`
- canonical/imported `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- canonical `run_null.sh` blob: `e0a8c106f9d3d636baea286d2ab33834748dffc9`
- canonical `run_qemu.sh` blob: `426aeeb854173569b24e64d6eb85019f45bdf0b6`
- Debian packaging VCS: `https://salsa.debian.org/debian/mmdebstrap.git`

The earlier packet treated Salsa as the canonical source host. Current project records and exact execution identify Forgejo `josch/mmdebstrap` as the proposed contribution destination; Salsa remains packaging context.

## Current behavior and invariant

Canonical source launches and interrupts each backend with:

```python
proc = subprocess.Popen(argv)
try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    proc.wait()
    break
```

The governing invariant is:

> A cancellation acknowledged by the coverage driver must reach the complete backend operation boundary created by that driver, while ordinary execution preserves the existing result path.

Exit status and operation cancellation are separate. A status-only repair can return 130 while nested work survives.

## Source ownership map

### Entrypoint

`coverage.py` parses `coverage.txt`, selects a backend command, starts one wrapper, waits for it, and owns final suite status.

### Backend wrappers

- `run_null.sh` can create nested shells, `tee`, a status reader, and generated test work.
- `run_qemu.sh` can create an output follower and foreground `timeout --foreground` operation.
- `run_null.sh SUDO` can create a sudo command and UID-0 worker.

### Side effects

Surviving descendants can continue writing logs, status files, generated artifacts, package state, mounts, or other outputs after the driver reports cancellation.

## Deterministic distinction

Under SIGINT sent only to the driver PID:

| Variant | Driver result | Responsive nested operation | Later work |
| --- | ---: | --- | --- |
| imported baseline | 0 after deliberate release | survives wrapper TERM | yes |
| status-only predecessor | 130 after deliberate release | survives wrapper TERM | yes |
| caller-owned group | 130 | TERM reaches and settles tested group | no |

Selected design:

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

Retained upstream-root patch blob: `f1a2c75adfa009b6f1ac29e5a31bef526400444f`.

## Why the caller owns the repair

The caller chooses the backend and can establish one backend-independent operation identity before wrapper code creates descendants. This avoids backend-specific process-tree enumeration.

`start_new_session=True` makes the child both session leader and process-group leader, allowing `proc.pid` to identify the owned group.

`ProcessLookupError` covers the race where the group exits before signal delivery.

The second `proc.wait()` reaps the wrapper. It does not prove arbitrary group quiescence; topology-specific tests support settlement only for the tested TERM-responsive groups.

## Canonical delivery packet

Linux Fieldwork PR [#401](https://github.com/teamleaderleo/linux-fieldwork/pull/401) is the current durable source package:

- branch/head: `upstream/unit-11-coverage-backend-cancellation@d232e4fdd67cf0592e129a60534e984dcbec6bfe`
- base: `main@6cc74d846c50b9bbb88247e8a128b67e8c174c1e`
- canonical upstream base executed: `77ec9be5417ee44c96343d2347145585da1b1f94`
- upstream-root patch blob: `f1a2c75adfa009b6f1ac29e5a31bef526400444f`
- exact current-source run: `30689911760`
- exact final packet-head run: `30690101504`
- internal initiative disposition: `READY FOR AUTHORIZATION`

The outer #435 packet keeps `REPAIR` because its `READY` definition additionally requires a clean target branch/head, project ordinary gates, and final clean-target review.

## Exact current-source execution

Canonical packet-patch job `91342674259`:

- canonical/imported source identity: exact;
- patch application with zero fuzz: success twice;
- compilation: success;
- six-control matrix: 6/6 twice;
- artifact `8815289674`, SHA-256 `25e62dec929f27e628816568d6264f2bee45474c00b00c3c047f53209608ef1d`.

Canonical refined-topology job `91342674164`:

- exact PR #339 regression carrier materialized;
- canonical wrappers inserted;
- null/QEMU-wrapper/passwordless-sudo matrix: 14/14 twice;
- skips: none;
- actual sudo root-worker controls executed;
- first pass 3.874 seconds, rerun 3.599 seconds;
- artifact `8815290820`, SHA-256 `63634782bfd230129238ee71aa60ad83ae5b43dfcf3291123cfdbd0770bdf63e`.

Final packet head run `30690101504` passed both canonical jobs.

## Carrier lineage

- issue #141 / PRs #143 and #204: status-only predecessor;
- issue #306 / closed PR #313: selected mechanism development and historical repository execution;
- closed PRs #332 and #336: superseded carrier repairs;
- closed PR #339: refined QEMU causal evidence, transferred to PR #401;
- issue #341 / closed PRs #347 and #353: TERM resistance, repeated SIGINT, publication, and escalation comparison;
- closed PR #406: duplicate current-main ancestry restack, superseded by PR #401;
- PR #401: canonical current-source packet and execution.

## Packet model review repair

The original local harness is preserved as `fixtures/local-process-model/harness_original.py`. It depended on `/tmp/unit13-probe` and waited only for the child marker before reading wrapper identity.

The reviewed `harness.py` resolves sibling files through `__file__`, waits for both markers, detects early driver exit, and cleans modeled processes in `finally`. Compilation and replay passed with unchanged output. This changes packet reproducibility only.

## Compatibility and limits

Supported by evidence:

- Linux/POSIX process groups;
- canonical null wrapper;
- canonical QEMU wrapper with the expensive foreground payload substituted;
- actual passwordless sudo path;
- ordinary unsignaled success;
- cleanup and immediate rerun.

Limits:

- descendants can escape with `setsid()` or a new group;
- TERM-resistant descendants can outlive the wrapper;
- repeated SIGINT can replace the first result during cleanup;
- a new session loses controlling-terminal association, so direct `/dev/tty` remains unproved;
- real QEMU/debvm, prepared mirrors, package operations, and non-Linux execution remain unexecuted;
- PGID reuse was outside the tests;
- the full mirror-backed project gate was not run.

Issue #341 demonstrated synthetic TERM-to-KILL sufficiency but supplied no real-backend necessity, grace interval, or acceptable state-loss evidence. Escalation remains outside this unit.

## Duplicate and destination result

The canonical unit-11 packet records no visible equivalent public issue or pull request at the time of preparation. Refresh overlap immediately before submission.

Proposed delivery method: controlled Forgejo fork and pull request. Controlled fork and candidate branch remain absent. Public contact remains unauthorized.

## Current technical answer

The caller-owned process group is the selected bounded repair. Exact canonical-source focused execution supports the responsive-topology claim. Delivery under #435 remains `REPAIR` until the controlled fork branch, upstream-native regression, ordinary gate, and independent clean-target review exist.
