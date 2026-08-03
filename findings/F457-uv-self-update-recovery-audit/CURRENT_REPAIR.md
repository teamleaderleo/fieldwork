# Current repair candidate

## Identity

- source base: `astral-sh/uv#20855@8d9324af47e1b52ec1f57f9232bd408281282cf5`
- controlled fork PR: `teamleaderleo/uv#31`
- branch: `experiment/457-b2-current-head-generation-rollback`
- current exact head: `7098add2d9240eb8c95275f63fe5d544b3f6c4f3`
- focused run: `30859708891`
- ordinary fork CI: `30859708980`
- external execution carrier: `teamleaderleo/fieldwork#607@f30bb9ba19d4851dfa60d3a557782487dfad6429`
- external focused run: `30860080826`
- validated source destination: `candidate/457-b2-windows-generation-rollback`

Run conclusions must be re-queried before use. At this record point both focused executions were queued and ordinary CI was pending.

## Defect being repaired

The current public helper mutates the live installation in this order:

1. copy companion executables;
2. promote the staged receipt;
3. call `self_replace` for canonical `uv.exe`.

Exact current-head execution proved that an injected finalizer error can leave old `uv.exe`, new `uvx.exe`, and a new receipt.

The exact `self-replace` Windows source also establishes that the primitive:

1. renames the running executable away from its canonical path;
2. schedules the renamed executable for deletion;
3. copies the replacement to a temporary file;
4. renames that temporary file into the canonical path.

Therefore an ordinary error in steps 2–4 cannot be repaired by rolling back companions and receipt alone. A separate snapshot of canonical `uv.exe` is required.

## Proposed bounded guarantee

If a companion copy, receipt promotion, or final-executable replacement returns an ordinary error, restore the complete pre-update managed generation before returning the error:

- canonical `uv.exe`;
- every pre-existing companion destination;
- the prior receipt;
- removal of companion paths that did not exist before the attempted update.

If rollback itself fails, retain the snapshot directory and return a combined error that names its path.

## Implementation shape

Before the first live mutation, create a temporary rollback directory inside the installation directory and snapshot:

- canonical `uv.exe` independently of `self-replace`'s private temporary files;
- all companion destinations discovered from the staged installation;
- the live receipt.

Apply the existing public ordering inside one error boundary. On any returned error, restore every snapshot. A byte comparison avoids overwriting the still-running old executable when the canonical path was never displaced; if the canonical path is missing or contains different bytes, the independent old snapshot is restored.

## Hostile controls

The focused matrix checks:

1. the actual running Windows test executable can be copied and byte-compared as a canonical snapshot;
2. a finalizer removes canonical `uv.exe` and then returns an error; expected result is the full old generation;
3. a deterministically later companion copy fails after an earlier companion was overwritten; expected result is the full old generation and no finalizer call;
4. the finalizer succeeds; expected result is the full new generation and promoted receipt.

A Linux-to-Windows cross-target compile gate checks the generated Windows source before the target-native filesystem matrix. Both jobs retain the fully formatted generated `self_update.rs`.

If both jobs pass, a gated third job checks out the exact public candidate, applies the validated transforms, verifies that only `crates/uv/src/commands/self_update.rs` changed, and pushes the source-only candidate branch. It cannot run after a red compile or hostile control.

Workflow concurrency now cancels superseded revisions. The Fieldwork external carrier runs the same exact uv head from a second repository queue because the uv repository queue is saturated.

## First execution classification

Run `30857807847`, job `91832800238`, did not execute a rollback control. It reached Windows compilation and failed because the initial transformer used `std::fs::DirEntry::file_name` with `fs_err::DirEntry`.

The current transformer uses `entries.sort_by_key(|entry| entry.file_name())`. The mid-copy fixture was also tightened so `uvx.exe` is overwritten before a later `uvz.exe` directory causes the injected copy error. The first red run is source-generation feedback, not evidence against the rollback algorithm.

## Model check

`models/ordinary_error_generation_rollback.py` exhaustively checks 32 combinations of pre-existing companions and receipt presence with failure at every ordinary commit step. Every failure restores the exact initial managed mapping, and the success case commits the complete new generation.

The model is a state-machine check, not a substitute for the queued Windows filesystem execution.

## Explicit exclusions

This candidate does not yet claim:

- power-loss or forced-process-termination recovery;
- atomic multi-file visibility to concurrent observers;
- stale transaction discovery on the next invocation;
- custom/GHE axoupdater route repair;
- whole installer descendant cancellation;
- cleanup of every random private temp or relocated executable created internally by `self-replace`.

Those remain separate work. The current candidate is intentionally smaller: close the proven ordinary-error rollback hole first, then decide whether the larger deferred finalizer and journal design is warranted for crash recovery.
