# uv tool design experiment index

## In simple words

This directory began with one false-success bug and now contains two related layers:

1. **the bounded public-issue experiment** — how `tool upgrade --all` should propagate inventory failure and how a useful recovery hint could be rendered;
2. **the VDFL playground** — if we owned the product direction ourselves, how we would design tool-state observation, recovery, generations, launchers, rollback, ownership, machine output, and the everyday CLI.

The second layer is deliberately our own product fiction. It does not widen the upstream ask and creates no upstream action.

## Start here by question

### What exactly happened in the original diagnostic experiment?

Read:

1. `README.md`
2. `RESULTS.md`
3. `RANKING.md`

Current bounded finalists:

- **B2** — shared exact-path invalid-directory-name diagnostic plus `tool upgrade --all` inventory context;
- **E** — scoped `tool upgrade --all` wrapper using the central hint machinery.

Both have executed evidence.

### What should a good hint be allowed to tell the user?

Read:

- `HINT_BOUNDARIES.md`
- `CONTENT_PROTOTYPES.md`

Central rule:

```text
a hint is part of the recovery path
```

The action should be executable from the state that produced the diagnostic, specific to the exact failure family, and conservative when ownership or deployment policy is unknown.

### What would we build if this were our product?

Read:

- `VDFL_VISION.md`
- `CLI_EXPERIENCE.md`

Major bets:

```text
claimed managed root
+ typed complete/incomplete inventory
+ independent desired ToolSpec
+ immutable generations
+ stable logical launchers
+ one active-generation pointer per tool
+ finding/remediation data model
+ doctor / repair --dry-run
+ rollback/history
+ explicit machine schema
+ complete aggregate-command semantics
```

### Can the generation/repair model actually behave that way?

Read/run:

- `model.py`
- `MODEL_RESULTS.md`

The dependency-free model currently exercises:

- crash before active-pointer switch;
- retry and activation;
- rollback;
- claimed-root quarantine;
- unclaimed-root preservation;
- retired entrypoint fail-closed behavior;
- owned stale-launcher cleanup;
- foreign public-executable preservation.

### How could immutable generations work across Unix and Windows?

Read:

- `TRANSACTIONAL_LAYOUT.md`
- `SHIM_INSPIRATION.md`

Current preferred product model:

```text
stable public launcher
    ↓
logical root/tool/entrypoint identity
    ↓
one active-generation pointer
    ↓
complete immutable generation
```

Current uv source gives two relevant platform facts:

- Unix tool entrypoints are published as symlinks to environment entrypoints;
- Windows tool entrypoints are copied, and uv's native trampoline format embeds readable launcher metadata such as the Python path.

The VDFL design makes Unix symlinks and Windows native launchers platform implementations of one logical-launcher contract.

## Inspiration map

The durable design notes record exact source revisions/URLs. The useful ideas are:

| Project | Idea to steal | Warning to remember |
| --- | --- | --- |
| uv itself | central typed `Hint` collection; Windows trampoline metadata | current tool state spans environment, lock, receipt and public entrypoints |
| Homebrew | findings with remediation; doctor-style read-only diagnostics | recovery advice should respect actual ownership/permissions |
| pipx | health/repair; recorded metadata; JSON results; ownership-aware exposure cleanup | backup/live-directory confusion and partial-exposure cases show why state classes matter |
| Git | friendly human status plus versioned porcelain format | scripts should never parse changing prose |
| Nix | generations, history and rollback | one pointer switch is powerful only after generation completeness is established |
| rustc/rustfix | suggestion applicability/confidence | filesystem repair needs a second safety/destructiveness axis |
| Cargo | reusable lexical `did you mean` machinery | fuzzy user-input help must stay separate from filesystem ownership |
| Volta | stable command shims and platform-specific implementations | central-manager dependency can enter the launch hot path |
| mise | shims, `which` introspection, automatic reshim | stale shims, obscured `which`, and system fallback are product tradeoffs |

## Current VDFL principles

### Observation precedes policy

```text
desired state + observed state -> findings -> plan -> mutation -> re-observation
```

A command does not replace inspection failure with a convenient default.

### Desired state survives disposable state

```text
ToolSpec != mutable environment
```

A broken environment or receipt should be rebuildable when independent desired metadata remains trustworthy.

### Activation has one authority point

```text
complete generation exists != generation is active
```

Only the active-generation pointer grants executable authority.

### Public commands have ownership identity

Stable launchers record/resolve logical root, tool and entrypoint identity. They do not silently fall through to an unrelated system binary when managed state breaks.

### Cleanup follows activation

Post-activation cleanup may be retryable. A retired stale launcher must fail closed rather than execute old generation code.

### Repair is a typed plan

```text
finding
+ evidence
+ confidence
+ safety
+ previewable action
```

Unknown or destructive cases can remain diagnostic-only.

### Aggregate success implies complete selected scope

Machine output carries `complete`. Exit status agrees with it.

## Evidence classes

### Target/owned-fork execution

The diagnostic thunderdome and scoped E candidate have real owned-fork execution receipts recorded in `RESULTS.md` / `RANKING.md`.

### Model execution

The VDFL filesystem state machine is `model-executed` evidence only. It establishes coherence of the reduced state transitions, not correctness on real uv, Windows, virtual environments, package resolution, or crash-ordering semantics.

### Design/source reading

`VDFL_VISION.md`, `TRANSACTIONAL_LAYOUT.md`, `SHIM_INSPIRATION.md`, and `CLI_EXPERIENCE.md` mix source-read facts with deliberately illustrative product design. They label the imagined parts through context and do not claim existing projects use our proposed architecture.

## Useful next branches

If we keep playing with this, the highest-value next experiments are:

1. **cross-tool entrypoint collision model** — two ToolIds claim the same stable launcher name;
2. **active-pointer corruption model** — choose rollback/rebuild when older complete generations survive;
3. **real Windows launcher prototype** — add logical root/tool/entrypoint identity to a small owned trampoline and measure startup/read behavior;
4. **real Unix stable-launcher prototype** — compare direct symlink, shared native dispatcher and tiny script/binary launcher overhead;
5. **legacy-root migration design** — bring current uv-style package directories into claimed/catalog/generation state without breaking existing public entrypoints;
6. **shared-root policy** — explicit user versus shared-group ownership/lock semantics;
7. **machine-schema prototype** — versioned `tool status` / `doctor` / `repair --dry-run` JSON with finding codes;
8. **full repair convergence test** — apply a plan, re-run doctor, require zero applicable findings or a precisely narrowed remainder;
9. **generation GC model** — prove active and rollback-retained generations cannot be collected;
10. **entrypoint-set publication under interruption** — add/remove names around activation and classify every crash point.

The experiment can stop whenever the ideas stop teaching us something. It already has value independent of any upstream outcome.
