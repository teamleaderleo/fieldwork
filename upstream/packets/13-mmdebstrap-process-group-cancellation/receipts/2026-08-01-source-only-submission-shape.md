# Source-only submission-shape decision — 2026-08-01

## Decision

Keep the clean target contribution source-only: `coverage.py` is the sole changed file.

Do not add a guessed Python file under `tests/`. Do not add a recursive mini-coverage fixture unless an eligible independent reviewer or upstream maintainer requires it.

## Reason

The target suite treats every non-dot entry under `tests/` as a shell-template package scenario indexed by `coverage.txt`. `coverage.py` rejects unmatched test files and dispatches matched files through `run_null.sh`, sudo, or QEMU.

The changed behavior belongs to the outer `coverage.py` orchestrator itself. A native regression from inside that same harness would need to:

1. create a second miniature coverage tree;
2. copy source and wrappers;
3. create nested `coverage.txt`, `tests/`, cache metadata, hooks, and tool stubs;
4. launch nested `coverage.py`;
5. arrange a descendant-survival topology;
6. send parent-only SIGINT;
7. distinguish baseline/status/group outcomes;
8. guarantee cleanup of nested groups.

That recursive harness would be substantially larger and more fragile than the 13-line product hunk. It would primarily test the constructed mini-harness rather than a normal package scenario.

## Evidence retained instead

The source-only shape is backed by exact deterministic external regression evidence:

- target run `30706007117`;
- zero-fuzz patch and target byte equivalence;
- six-control baseline/status/group matrix twice;
- fourteen-control refined null/QEMU-wrapper/passwordless-sudo matrix twice;
- no skips; actual sudo controls;
- cleanup and immediate rerun;
- project-native ordinary source slice `30706633832`, 3/3 twice.

The clean review surface is `teamleaderleo/mmdebstrap#4`, containing one file with 8 additions and 3 deletions.

## Compatibility and review effect

The source-only decision does not broaden the technical claim. It remains limited to TERM-responsive descendants that stay in the caller-owned group.

An eligible reviewer should still decide whether upstream review expectations justify the disproportionate recursive test. A request for such a test reopens this decision.

## Reopen triggers

Reopen when any of these occurs:

- an eligible reviewer requires a target-native regression;
- upstream contribution policy explicitly requires a test in the same change;
- a smaller stable target-native hook or self-test surface is identified;
- current source changes make recursive coverage testing straightforward;
- the external reproducer is found not to preserve an important target boundary.

## Authority

This decision changes only internal packet and candidate organization. It does not authorize canonical-upstream contact or submission.
