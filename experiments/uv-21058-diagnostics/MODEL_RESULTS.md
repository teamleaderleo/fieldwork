# Executable VDFL tool-state model results

## In simple words

A dependency-free filesystem model exercised the central claims in `VDFL_VISION.md` and `TRANSACTIONAL_LAYOUT.md`.

The model keeps desired tool metadata outside immutable generations, publishes a generation before changing one active pointer, models stable launcher ownership independently from generation identity, supports rollback by pointer change, turns an invalid tool-root child into a reversible quarantine finding, and refuses to overwrite a foreign public executable.

The first execution passed every assertion.

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

The retained run produced the equivalent of:

```json
{
  "active_generation": 3,
  "black_target": "<temp>/tools/.uv/generations/black/000003/bin/black",
  "findings": [
    "F3101"
  ],
  "foreign_preserved": true,
  "quarantine_exists": true
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

### 5. Invalid tool-root child becomes a reversible finding

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

### 6. Foreign public executable blocks a new exposure

Before preparing generation 4, the model creates a foreign public file at the path wanted by new entrypoint `black-beta`.

The generation itself can be prepared, but exposure reconciliation returns:

```text
F3101 foreign public executable blocks `black-beta`
```

Required result:

```text
foreign bytes unchanged
active generation remains 3
```

Both passed.

This models the ownership rule:

```text
an upgrade may prepare a candidate while public-name conflict resolution remains pending;
foreign state is preserved and the candidate never becomes active
```

## What this establishes

Evidence class: `model-executed`.

The model demonstrates that these ideas are internally coherent in a small filesystem state machine:

1. a complete-but-unactivated generation can coexist with a healthy active generation;
2. one active pointer can control several logical entrypoints together;
3. rollback can be a pointer operation;
4. unexpected children can use reversible repair planning;
5. public executable conflicts can preserve foreign state and block activation;
6. desired metadata can live independently from generations.

## What this does not establish

The model does not execute uv, virtual environments, Windows PE launchers, symlink/junction replacement, real package resolution, concurrent processes, filesystem crash ordering, or actual executable dispatch.

`os.replace()` is used as the model's publication primitive. Real platform semantics still need separate implementation work.

The stable-launcher concept is represented as metadata files. `TRANSACTIONAL_LAYOUT.md` separately maps that concept onto current uv's Unix symlink and Windows trampoline boundaries.

## Next discriminators

Useful extensions to the model:

1. entrypoint removal across generations, including a stale stable launcher before cleanup;
2. two tools contending for one public entrypoint;
3. active-pointer corruption with an older complete generation available;
4. interrupted quarantine / repair application;
5. unclaimed custom root, where quarantine must stay disabled;
6. concurrent generation preparation with serialized activation;
7. transaction replay after active switch but before stale exposure cleanup;
8. migration from one launcher schema to another.

The model should remain small. Once real platform behavior is required, use an owned-fork or platform runner rather than turning this synthetic layer into a fake operating system.
