# Unit 13 approaches ledger

## Selected product approach

### Caller-owned session/process group

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

Why it wins:

- the caller selects the backend and can establish the operation boundary before backend code runs;
- one boundary covers null, QEMU-wrapper, sudo, and future descendants that remain in-group;
- parent-only SIGINT reaches nested responsive work;
- ordinary unsignaled and source/interface behavior remain successful;
- no backend-specific process discovery or escalation policy is added.

Clean source:

- base `77ec9be5417ee44c96343d2347145585da1b1f94`;
- head `431614b3af58ba4f70791aa1d42cf5b71c965dd2`;
- candidate blob `9e31f21cf37228257b5e0705d9ecb13b7a66e40f`;
- diff `coverage.py` only, 8 additions and 3 deletions;
- clean review `teamleaderleo/mmdebstrap#4`.

## Selected delivery approach

### Clean controlled source branch plus durable packet evidence

- canonical packet: `teamleaderleo/linux-fieldwork#401`;
- outer packet: `teamleaderleo/fieldwork#439`;
- clean source review: `teamleaderleo/mmdebstrap#4`;
- focused runner PR #2: closed after evidence transfer;
- ordinary runner PR #3: closed after evidence transfer.

Why it wins:

- the public-shaped source branch contains only the product hunk;
- execution workflows and research fixtures stay outside the clean diff;
- exact run, job, artifact, blob, and cleanup identities remain durable in the packets;
- historical carriers can be closed after evidence transfer;
- independent review can inspect one complete source file rather than research packaging.

## Selected test/submission shape

### Source-only clean contribution with retained external regression

The target suite treats every non-dot `tests/` entry as a `coverage.txt`-indexed shell-template package scenario. Testing the outer coverage orchestrator from inside that same harness would require recursively constructing a miniature coverage suite substantially larger than the product fix.

Selected shape:

- `coverage.py` only on the clean branch;
- exact deterministic baseline/status/group reproducer retained in the packet;
- focused target execution 6/6 twice and refined execution 14/14 twice;
- native ordinary source slice `help`, `man`, `version` 3/3 twice;
- recursive target-native test reopened only if eligible review or upstream policy requires it.

Decision record: `receipts/2026-08-01-source-only-submission-shape.md`.

## Selected ordinary-gate approach

### Bounded project-native source and command-interface slice

The full prepared-mirror 283-entry matrix is broad environment coverage and requires package/mirror state unrelated to the signal ownership discriminator.

Selected ordinary gate:

```sh
./coverage.sh help man version
```

This executes the project's real source checks, `coverage.py` inventory, `run_null.sh`, and native shell-template scenarios without package installation side effects.

Run `30706633832` passed 3/3 twice.

The exact base has a pre-existing Black defect on canonical `tarfilter` blob `ad776167a8473d5d15dbe22e850f4f6db35cf278`. The successful gate isolates only that exact blob while keeping real Black 26.5.1 enforcement for every other checked Python file.

The full matrix remains an evidence limit and reopen item, not a current blocker for the narrow source-only lifecycle unit.

## Executed losing approaches

### Immediate-wrapper termination

```python
proc = subprocess.Popen(argv)
proc.terminate()
proc.wait()
break
```

Result: nested work can survive and later work can run; final status can be 0.

### Status-only correction

Result: final status becomes 130 while nested work still survives. Status correctness and operation cancellation are separate.

Historical records: issue #141, PRs #143 and #204.

### Reuse historical CI as current-source evidence

Rejected. Historical runs remain valid for their exact heads. Canonical and controlled target execution were added.

### Byte-identical Linux Fieldwork ancestry restack

PR #406 confirmed the nine-file historical carrier could be restacked onto Linux Fieldwork `main`, but PR #401 and the clean target branch provide stronger canonical source evidence. PR #406 is closed superseded.

### Keep historical carriers open

Rejected after evidence transfer. PR #313 and PR #339 are closed; their unique evidence is retained in PR #401.

### Treat Salsa as the contribution destination

Rejected. Canonical contribution destination is Forgejo `josch/mmdebstrap`; Salsa is Debian packaging context.

### Backend-specific descendant discovery

Rejected because it couples the caller to evolving shell, pipeline, QEMU, sudo, and future backend topology.

### Same-session background process group

Rejected after PTY comparison: background groups can stop on terminal input. A new session preserves inherited descriptors while removing controlling-terminal association.

### Claim arbitrary group quiescence

Rejected. The second wait reaps only the wrapper. Claims remain limited to executed TERM-responsive topologies.

### Add a recursive native test by default

Rejected as disproportionate. It would construct a second coverage suite inside a coverage scenario and mainly test the recursive scaffolding. Reopen on explicit review or policy requirement.

### Treat the full prepared-mirror matrix as mandatory for this source unit

Rejected as the default closeout gate because package and mirror execution do not sharpen the parent-only signal ownership discriminator. Reopen if independent review or maintainer policy requires it.

### TERM-to-KILL escalation

Synthetic research in issue #341 and PRs #347/#353 showed bounded escalation can drain a resistant test group. It remains unselected because no real backend demonstrated need, no grace interval was justified, and KILL can discard cleanup state.

Reopen when a real backend ignores or materially defers TERM, outlives its wrapper, or demonstrates an operational repeated-SIGINT requirement.

## Packet fixture choice

- `harness_original.py`: retained as exact original packet-time source;
- `harness.py`: selected default replay because it is relocatable, waits for both readiness markers, diagnoses early exit, and cleans modeled processes in `finally`.

Both preserve the same three-way result.

## Current remaining gate

Eligible independent complete-diff acceptance on `teamleaderleo/mmdebstrap#4`.

Do not assign an unrelated reviewer merely to clear the gate. No public upstream contact is authorized.
