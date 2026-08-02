# uv `EnvironmentOptions` starter-lane screen — 2026-08-02

## In simple words

The remaining unchecked boxes in the public `EnvironmentOptions` migration issue are not a clean first contribution by default. Most have prior implementation attempts. The few with no matching pull request found sit in lower-level crates or early process initialization, where moving parsing requires a deliberate propagation or initialization design rather than adding one field.

## Public anchor

- issue: `astral-sh/uv#14720`
- public source pin inspected: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- retrieval date: 2026-08-02
- public interaction: none

The issue explicitly recommends one variable per pull request and invites additional variable discovery. That remains useful guidance. The checklist alone is not an ownership map.

## Prior-attempt screen

Fresh public pull-request searches found implementation history for:

| Variable | Prior public attempts found |
| --- | --- |
| `UV_COMPILE_BYTECODE_TIMEOUT` | `astral-sh/uv#16388`, `#18504` |
| `UV_RUN_RECURSION_DEPTH` | `astral-sh/uv#18531` |
| `UV_RUN_MAX_RECURSION_DEPTH` | `astral-sh/uv#18593`, `#19240`, `#19245` |
| `UV_GITHUB_FAST_PATH_URL` | `astral-sh/uv#19193` |
| `UV_CUDA_DRIVER_VERSION` / `UV_AMD_GPU_ARCHITECTURE` | `astral-sh/uv#18846` |
| `TRACING_DURATIONS_FILE` | `astral-sh/uv#16109` |

This does not claim every attempt is still open or correct. It does mean a new implementation would require reading and classifying the prior review history first.

## Unoccupied-looking variables and their real boundaries

### `UV_GIT_LFS`

Source owner: `crates/uv-git-types/src/lib.rs`.

Current behavior is parsed once through a process-global `LazyLock<GitLfs>`. `GitLfs::from_env()` is also the fallback for `From<Option<bool>>`, and the value is embedded into `GitUrl` identity, equality, ordering, and hashing.

A migration therefore must decide how the parsed option reaches every `GitUrl` construction and deserialization/lowering path without making the leaf `uv-git-types` crate depend on `uv-settings`. This is settings propagation and identity review, not a one-field starter edit.

Fresh exact-variable PR search found no matching public pull request.

### `UV_STACK_SIZE`

Source owner: `crates/uv-configuration/src/threading.rs`.

`min_stack_size()` reads `UV_STACK_SIZE` with `RUST_MIN_STACK` fallback and is used to size uv's replacement main thread, Tokio-related clients, and the global Rayon pool. The value is needed during early runtime/thread construction, potentially before normal command settings resolution.

A migration must preserve:

- `UV_STACK_SIZE` over `RUST_MIN_STACK` precedence;
- invalid-value fallback;
- the 1 MiB minimum and 4 MiB default;
- one consistent value across main2, Rayon, and other thread builders;
- initialization order before `EnvironmentOptions` is normally consumed.

Fresh exact-variable PR search found no matching public pull request.

### `UV_LOCK_TIMEOUT`

Source owner: `crates/uv-fs/src/locked_file.rs`.

Current behavior is a process-global `LazyLock<Duration>` with a five-minute default. Invalid values warn and fall back rather than aborting uv startup. The value is consumed inside generic async file-lock acquisition in the lower-level `uv-fs` crate.

A migration must decide whether to:

- pass a timeout through every lock acquisition owner;
- initialize a lower-level global once from parsed settings;
- or keep this variable outside `EnvironmentOptions` because the current warning/fallback and low-level availability semantics are intentional.

It must also preserve the current nonfatal invalid-value behavior; the normal integer environment parser may instead turn invalid input into an up-front command error.

Fresh exact-variable PR search found no matching public pull request.

## Decision

`STOP AS FIRST-PATCH LANE / RETAIN AS CODEBASE MAP`

Do not select an unchecked variable merely to obtain a small diff. The remaining apparently available variables are useful medium-depth exercises after one accepted contribution, because each teaches a different uv architecture boundary:

- identity and leaf-crate propagation (`UV_GIT_LFS`);
- early process/thread initialization (`UV_STACK_SIZE`);
- lower-level global policy and error-semantics preservation (`UV_LOCK_TIMEOUT`).

Unit 02 remains the better prospective first contribution. The lockfile diagnostic remains the better small internal review exercise.

## Reopening trigger

Reopen one variable only after:

1. its complete prior PR history is classified;
2. the exact owner and dependency direction are mapped;
3. current invalid-value and precedence semantics are pinned in tests;
4. a propagation shape avoids new dependency cycles and global divergence;
5. no active public implementation owns the same variable.
