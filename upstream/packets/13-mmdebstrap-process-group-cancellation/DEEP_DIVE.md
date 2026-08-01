# Unit 13 deep dive

## Question

When SIGINT is delivered only to the `coverage.py` driver, does cancellation stop the complete selected backend operation and report a conventional interrupted status?

Canonical source terminated only the immediate wrapper and then broke into the ordinary epilogue. Nested work could survive. A status-only correction returned 130 while preserving the survivor defect.

## Exact source

- canonical project: mmdebstrap
- canonical repository: `https://gitlab.mister-muffin.de/josch/mmdebstrap`
- branch/base: `main@77ec9be5417ee44c96343d2347145585da1b1f94`
- base `coverage.py` blob: `9a522484aef05deae514a98e4b6adf5feb6c886d`
- clean controlled source: `teamleaderleo/mmdebstrap:linux-fieldwork/unit-11-coverage-backend-cancellation@431614b3af58ba4f70791aa1d42cf5b71c965dd2`
- candidate `coverage.py` blob: `9e31f21cf37228257b5e0705d9ecb13b7a66e40f`
- complete clean diff: `coverage.py` only; 8 additions, 3 deletions
- clean review surface: `teamleaderleo/mmdebstrap#4`

## Source mechanism

Canonical source:

```python
proc = subprocess.Popen(argv)
try:
    proc.wait()
except KeyboardInterrupt:
    proc.terminate()
    proc.wait()
    break
```

Selected source:

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

The driver owns the repair because it selects the backend and can establish one operation identity before wrapper code creates shells, pipelines, QEMU-like foreground operations, or privileged workers.

`start_new_session=True` makes the wrapper session and process-group leader. `proc.pid` therefore identifies the group used by `killpg`.

`ProcessLookupError` accepts the group disappearing between interruption and delivery. The second wait reaps the wrapper. It does not prove arbitrary resistant-descendant drain.

## Deterministic distinction

| Variant | Parent-only SIGINT result | Nested responsive work | Later work |
| --- | ---: | --- | --- |
| imported baseline | 0 after deliberate release | survives wrapper TERM | yes |
| status-only predecessor | 130 after release | survives wrapper TERM | yes |
| selected group candidate | 130 | group receives TERM and settles | no |

## Focused target execution

Run `30706007117` on the controlled exact target source:

- zero-fuzz patch application;
- patch-materialized source byte-equal to clean target source;
- candidate compilation;
- six-control matrix 6/6 twice;
- refined null/QEMU-wrapper/passwordless-sudo matrix 14/14 twice;
- no skips;
- actual sudo controls;
- cleanup and immediate rerun.

Artifacts:

- `8820336271`, SHA-256 `97eba28273b50dfcf51c32a2fe4cf49aa50da5634a3aaba6b052ad3728ae1ce8`;
- `8820337503`, SHA-256 `8d72b079fa9e30ee92bdf28cf217e9df3e4ae7a5ffeb7374b76950313bf24614`.

## Project-native ordinary source slice

Run `30706633832`, job `91386769087`:

- native `./coverage.sh help man version` entrypoint;
- real source checks, `coverage.py` inventory, `run_null.sh`, and shell-template scenarios;
- first pass 3/3;
- immediate rerun 3/3;
- candidate compilation and cleanup;
- artifact `8820528312`, SHA-256 `13986015aebc37cd3624f5114baa2a599f3c3dccb01e838b367287b2585b8f55`.

The exact base has an unrelated existing Black failure on canonical `tarfilter` blob `ad776167a8473d5d15dbe22e850f4f6db35cf278`. The successful gate isolates only that exact blob and keeps real Black 26.5.1 enforcement for the changed `coverage.py` and all other checked Python files.

## Submission-shape decision

The clean contribution is source-only.

The target suite treats every non-dot `tests/` entry as a `coverage.txt`-indexed shell-template package scenario. A native regression for the outer coverage orchestrator would require recursively constructing and launching a miniature coverage suite, substantially exceeding the size and stability of the product change.

The deterministic external reproducer was executed against the exact target source and remains retained with full receipts. A recursive target-native test is a reopen item if independent review or upstream policy requires it.

## Compatibility analysis

Supported by evidence:

- Linux/POSIX process groups;
- exact canonical null wrapper;
- exact canonical QEMU wrapper with expensive payload substituted;
- actual passwordless sudo path;
- inherited standard descriptors;
- ordinary source/interface scenarios;
- cleanup and immediate rerun.

Risks and exclusions:

- descendants can escape with `setsid()` or a new group;
- TERM-resistant descendants can outlive the wrapper;
- repeated SIGINT can interrupt cleanup;
- direct controlling-terminal access remains unproved;
- PGID reuse was not formally proved impossible;
- real QEMU/debvm package operations and non-Linux execution remain unexecuted.

Issue #341 and closed PRs #347/#353 retain stronger cleanup-policy research. Synthetic TERM-to-KILL sufficiency did not provide real-backend necessity or a justified grace interval. Escalation remains unselected.

## Why the full package matrix is an evidence limit

The source change belongs to the outer orchestration boundary, not package extraction, mirror construction, or package-manager semantics. Exact wrapper topology tests distinguish the changed behavior directly, while the native ordinary source slice exercises the actual source-check and dispatch path.

The full prepared-mirror 283-entry matrix could expand environment coverage but does not add a sharper discriminator for parent-only signal ownership. It remains visible and may be required by independent review or maintainer policy, but is not treated as a current blocker for the narrow source-only unit.

## Carrier and packet routing

- canonical packet: `teamleaderleo/linux-fieldwork#401`;
- outer packet: `teamleaderleo/fieldwork#439`;
- clean target review: `teamleaderleo/mmdebstrap#4`;
- focused runner PR #2: closed after evidence transfer;
- ordinary runner PR #3: closed after evidence transfer;
- historical PRs #313 and #339: closed after evidence transfer;
- duplicate PR #406: closed superseded.

## Current technical answer

The caller-owned process group is the selected bounded repair. The clean one-file source diff is ready for eligible independent review.

Unit 13 remains `REPAIR` under #435 only because eligible independent complete-diff acceptance is absent. Public canonical-upstream contact remains unauthorized.
