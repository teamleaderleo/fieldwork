# Executable VDFL tool-state model results

## In simple words

A dependency-free filesystem model exercised the central claims in `VDFL_VISION.md` and `TRANSACTIONAL_LAYOUT.md`.

The model keeps desired tool metadata outside immutable generations, publishes a generation before changing one active pointer, models stable launcher ownership independently from generation identity, supports rollback by pointer change, turns an invalid child in a claimed tool root into a reversible quarantine finding, keeps an unclaimed custom root read-only, lets retired entrypoints fail closed before cleanup, and refuses to overwrite a foreign public executable.

The extended execution passed every assertion.

## Artifact

Runner: `model.py`

Environment used for the retained local execution:

```text
Python 3
standard library only
synthetic temporary directory
no network
no external commands
```

Exact command:

```sh
python model.py
```

## Output

The retained extended run produced the equivalent of:

```json
{
  "active_generation": 4,
  "black_target": "<temp>/tools/.uv/generations/black/000004/bin/black",
  "findings": [
    "F3101"
  ],
  "foreign_preserved": true,
  "quarantine_exists": true,
  "retired_launcher_removed": true,
  "unclaimed_root_preserved": true
}
```

Temporary path identity varies per run.

## Scenarios exercised

### 1. Initial complete generation

The model installs logical tool `black` generation 1 with two entrypoints:

```text
black
blackd
```

Both stable launcher records resolve through the active-generation pointer to generation 1.

### 2. Complete candidate dies before activation

Generation 2 is fully prepared and published, then the model injects failure immediately before the active-pointer switch.

Required result:

```text
active generation remains 1
black still resolves generation 1
```

This passed.

The experiment therefore distinguishes:

```text
complete generation exists on disk
```

from:

```text
that generation is executable authority
```

Only the active pointer grants authority.

### 3. Retry commits through one pointer

Generation 3 is built successfully with the same entrypoint set and activated.

Required result:

```text
black  -> generation 3
blackd -> generation 3
```

Both changed together because stable launcher identity is separate from generation identity.

### 4. Rollback needs no rebuild

The model switches active generation 3 -> 1 and verifies `black` resolves the older version, then switches back 1 -> 3.

No generation files are rebuilt or copied.

This passed.

### 5. Invalid child in a claimed root becomes a reversible finding

The model creates:

```text
<root>/tool backup
```

`doctor()` returns:

```text
F1001 invalid tool directory name
confidence: certain
safety: reversible
repair: quarantine
```

`repair(dry_run=True)` reports the move while leaving the directory in place.

`repair(dry_run=False)` moves it into:

```text
<root>/.uv/quarantine/tool backup
```

This passed.

### 6. Entrypoint retirement is separate from activation

Generation 4 removes `blackd` and keeps only `black`.

The active pointer switches to generation 4 successfully.

Before launcher cleanup:

```text
black  -> generation 4
blackd launcher still exists
```

Resolving `blackd` through that stale owned launcher fails with a retired-entrypoint error. It does **not** execute generation 3.

The cleanup plan then identifies the stale launcher and removes it only because its launcher metadata still says it belongs to the same root/tool/entrypoint.

Required result:

```text
activation succeeds independently from stale-launcher deletion
retired entrypoint never falls through to old code
owned stale launcher can be removed later
```

This passed.

This is an important transaction result: post-commit cleanup can be retryable without becoming executable authority.

### 7. Foreign public executable blocks a new exposure

Before preparing generation 5, the model creates a foreign public file at the path wanted by new entrypoint `black-beta`.

The generation itself can be prepared, but exposure reconciliation returns:

```text
F3101 foreign public executable blocks `black-beta`
```

Required result:

```text
foreign bytes unchanged
active generation remains 4
```

Both passed.

This models the ownership rule:

```text
an upgrade may prepare a candidate while public-name conflict resolution remains pending;
foreign state is preserved and the candidate never becomes active
```

### 8. Unclaimed custom root disables destructive repair

A separate synthetic directory is created with:

```text
<wrong-root>/tool backup
```

and no `.uv/root.json` ownership marker.

`doctor()` returns only:

```text
F0001 configured tool directory is not initialized for this manager
```

`repair(dry_run=True)` returns no quarantine plan.

Required result:

```text
unexpected child remains untouched
```

This passed.

The model therefore enforces the safety distinction that motivated the root marker:

```text
claimed uv root + unexpected child -> reversible managed repair may be offered
unclaimed arbitrary directory      -> diagnose root selection; do not mutate contents
```

## What this establishes

Evidence class: `model-executed`.

The model demonstrates that these ideas are internally coherent in a small filesystem state machine:

1. a complete-but-unactivated generation can coexist with a healthy active generation;
2. one active pointer can control several logical entrypoints together;
3. rollback can be a pointer operation;
4. unexpected children in a claimed root can use reversible repair planning;
5. an unclaimed custom root can disable destructive recovery even when it contains the same invalid child name;
6. a retired entrypoint can fail closed after activation and be cleaned up later;
7. public executable conflicts can preserve foreign state and block activation;
8. desired metadata can live independently from generations.

## What this does not establish

The model does not execute uv, virtual environments, Windows PE launchers, symlink/junction replacement, real package resolution, concurrent processes, filesystem crash ordering, or actual executable dispatch.

`os.replace()` is used as the model's publication primitive. Real platform semantics still need separate implementation work.

The stable-launcher concept is represented as metadata files. `TRANSACTIONAL_LAYOUT.md` separately maps that concept onto current uv's Unix symlink and Windows trampoline boundaries.

## Next discriminators

Useful extensions to the model:

1. two tools contending for one public entrypoint;
2. active-pointer corruption with an older complete generation available;
3. interrupted quarantine / repair application;
4. concurrent generation preparation with serialized activation;
5. transaction replay after active switch but before stale exposure cleanup;
6. migration from one launcher schema to another;
7. a root path reused by a different root ID;
8. garbage collection that cannot remove the active or rollback-retained generations.

The model should remain small. Once real platform behavior is required, use an owned-fork or platform runner rather than turning this synthetic layer into a fake operating system.
