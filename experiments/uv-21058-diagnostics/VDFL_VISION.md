# If we were designing our own uv

## In simple words

If this were our tool manager, I would make the installed state **inspectable, rebuildable, versioned, and explicit about uncertainty**.

The original `tool upgrade --all` bug is one small symptom of a larger design opportunity. Today a directory scan has to become either a valid list, per-tool errors, or a top-level error before commands can reason about it. Our version would preserve the observations themselves: which root was selected, whether uv owns that root, every child found, what could be parsed, what metadata survived, which environment and entrypoints are actually present, and whether the inventory is complete.

Then diagnostics, audit, upgrade, uninstall, repair, JSON output, crash recovery, and rollback can all consume the same truth instead of inventing their own interpretation of damaged state.

This is product design for our imaginary fork. It is not an upstream proposal and it does not select a direction for https://redirect.github.com/astral-sh/uv/issues/21058.

## Inspirations worth stealing

Retrieved 2026-08-12.

### Homebrew: diagnostics are findings with remediation

Current Homebrew diagnostics have a `Finding` / `Remediation` concept rather than treating every check as an ad-hoc printed warning. The checks can carry remediation text and commands separately from the finding itself.

Source:

- https://github.com/Homebrew/brew/blob/0d7b47e8d897dce76ee46a5d25636cf1c60fc39b/Library/Homebrew/diagnostic/finding.rb
- https://github.com/Homebrew/brew/blob/0d7b47e8d897dce76ee46a5d25636cf1c60fc39b/Library/Homebrew/diagnostic.rb

What I would steal: **diagnostic output should originate from typed findings, and recovery should be data attached to a finding rather than prose embedded deep in one command.**

Homebrew also has a useful cultural distinction: `brew doctor` can report conditions that deserve attention without pretending every warning means the package manager itself is unusable. That suggests a separate read-only health surface instead of making ordinary commands carry every diagnostic check.

### pipx: health, repair, recorded metadata, reset, and JSON

Current pipx has explicit `health` and `repair` commands. `health` checks managed environments without changing them; `repair` rebuilds failed environments from recorded metadata and leaves healthy environments alone. It also has `reset --dry-run`, JSON-capable command results, and persistent metadata used to reconstruct installs.

Sources:

- https://github.com/pypa/pipx/blob/04301bcce2fbf57b5498e12e91ee4c8509c56c7e/src/pipx/commands/health.py
- https://github.com/pypa/pipx/blob/04301bcce2fbf57b5498e12e91ee4c8509c56c7e/src/pipx/result.py
- https://github.com/pypa/pipx/blob/04301bcce2fbf57b5498e12e91ee4c8509c56c7e/docs/how-to/troubleshoot.rst
- https://github.com/pypa/pipx/blob/04301bcce2fbf57b5498e12e91ee4c8509c56c7e/docs/reference/json-output.rst

Its own current comparison documentation explicitly lists health/repair as functionality pipx has and `uv tool` lacks.

What I would steal: **checking and repairing are first-class operations, and the desired install metadata should survive independently enough that a broken environment can be rebuilt.**

### Git: human output and machine output are different contracts

`git status` has friendly human output and a separate `--porcelain` format that is intentionally stable for scripts.

Source:

- https://github.com/git/git/blob/11c6700f10234578d10523faf35656ca491425c9/Documentation/git-status.adoc

What I would steal: **never force automation to parse our prose.** Human diagnostics can improve over time while a versioned status schema stays stable.

### Nix: install a new generation, then switch the pointer

Nix profiles are versioned and can be rolled back. The documented model keeps package versions separately and changes the active profile generation through a pointer, allowing atomic publication on Unix and explicit history/rollback.

Sources:

- https://github.com/NixOS/nix/blob/24b65e35d9d4c9d64c1bd5844a35f2a779356d63/doc/manual/source/package-management/profiles.md
- https://github.com/NixOS/nix/blob/24b65e35d9d4c9d64c1bd5844a35f2a779356d63/src/nix/profile-rollback.md

What I would steal: **an upgrade should build a complete replacement generation before it becomes current, and the previous complete generation should remain recoverable for a while.**

### rustc/rustfix: suggestions carry applicability

Rust diagnostics distinguish suggestions by confidence. `MachineApplicable` means tooling may apply the suggestion automatically; less certain suggestions require user judgment.

Reference:

- https://doc.rust-lang.org/stable/nightly-rustc/rustc_errors/enum.Applicability.html

What I would steal, with an extra axis: **a recovery action should declare both confidence and safety.** A suggestion can be logically certain yet destructive, or reversible yet based on uncertain intent.

### Cargo: fuzzy suggestions belong to lexical mistakes

Cargo has reusable edit-distance helpers for nearby names and uses them for `did you mean`-style errors.

Source:

- https://github.com/rust-lang/cargo/blob/eb98b54bc9f3c74519f43d066cb3fd02ebc88df0/src/util/edit_distance.rs

What I would steal is also a boundary: fuzzy matching is great for command names, package names, features, and other lexical choices. **Filesystem recovery should remain evidence-based.** We should never edit-distance an unexpected directory into a tool identity and then mutate it.

## Product thesis

The core rule would be:

```text
desired state + observed state -> findings -> plan -> mutation -> new observed state
```

No command gets to skip the `observed state` part by replacing an inspection failure with a convenient default.

A second rule:

```text
mutable environment != authoritative desired state
```

An environment can be deleted, half-written, upgraded under us, or corrupted. We should retain enough independent metadata to know what the user asked uv to manage and to rebuild it when possible.

A third:

```text
publish complete generations; repair incomplete observations
```

Do the expensive and failure-prone work before changing the current generation.

## 1. Claim the tool root explicitly

The custom-root problem in the hint experiment points at a deeper answer: a managed directory should identify itself as managed state.

Our tool root would contain an internal reserved namespace whose name cannot collide with a package name:

```text
$UV_TOOL_DIR/
├── .uv/
│   ├── root.toml
│   ├── catalog/
│   ├── exposures/
│   ├── transactions/
│   ├── quarantine/
│   └── locks/
├── ruff/
├── black/
└── ...
```

`root.toml` could contain only boring identity/version data:

```toml
schema = 1
kind = "uv-tool-root"
created_by = "uv 1.0.0"
id = "01J..."
```

The marker does several useful things:

- distinguishes an initialized uv root from an arbitrary directory named by `UV_TOOL_DIR`;
- gives state migrations an explicit schema boundary;
- gives repair code evidence that the surrounding directory was intentionally claimed by uv;
- reserves `.uv/` for internal state so caches, transaction journals, and quarantine never masquerade as packages.

### Unclaimed custom root

If `UV_TOOL_DIR` points at a non-empty directory with no marker, a mutating command should stop before interpreting all children as tool installations:

```text
error: The configured tool directory is not initialized for uv
  Caused by: `UV_TOOL_DIR` points to `/srv/shared/python`

hint: Check `UV_TOOL_DIR`, or initialize this directory as a uv tool root if it is intended for uv tools
```

A read-only inspection can still report what it sees, but destructive repair stays disabled until ownership is established.

That is much safer than discovering `tool backup` under `$HOME` and suggesting deletion because someone accidentally exported `UV_TOOL_DIR=$HOME`.

## 2. Inventory should be a typed snapshot

Instead of forcing inspection into `Vec<(PackageName, Result<Tool, Error>)>`, I would make the inventory result preserve what was actually observed.

Illustrative Rust-ish model:

```rust
struct ToolInventory {
    root: ToolRoot,
    complete: bool,
    entries: Vec<InventoryEntry>,
    findings: Vec<Finding>,
}

struct ToolRoot {
    path: PathBuf,
    source: RootSource,       // Default | UV_TOOL_DIR | Other
    ownership: RootOwnership, // Claimed | Unclaimed | InvalidMarker
    schema: Option<u32>,
}

enum InventoryEntry {
    Managed(ToolState),
    Unexpected(UnexpectedEntry),
    Unreadable(UnreadableEntry),
}

struct ToolState {
    name: PackageName,
    desired: Observation<ToolSpec>,
    current_generation: Observation<Generation>,
    receipt: Observation<ToolReceipt>,
    environment: Observation<EnvironmentState>,
    lock: Observation<LockState>,
    exposures: Vec<ExposureState>,
}

enum Observation<T> {
    Present(T),
    Missing,
    Invalid { error: String },
    Unreadable { path: PathBuf, error: io::Error },
    UnsupportedVersion { found: u32, supported: u32 },
}
```

The exact types can differ. The important product property is that **absence, corruption, unreadability, unsupported versions, and unexpected filesystem objects remain different facts.**

Then an aggregate command can say whether its selected scope was completely inspected.

## 3. Desired state should survive a broken environment

Each installed tool should have a small authoritative `ToolSpec` outside the mutable generation:

```toml
name = "ruff"
requirement = "ruff>=0.12"
python = ">=3.12"
backend = "uv"

[options]
prerelease = "if-necessary-or-explicit"
```

It would record the user intent and the options uv needs to recreate the environment. Resolved artifacts and locks can live beside the generation, but the desired spec should survive deleting that generation.

This gives repair a meaningful boundary:

```text
receipt corrupt + ToolSpec present       -> rebuild is possible
receipt missing + ToolSpec present       -> rebuild is possible
entire catalog entry missing             -> uv cannot invent original intent
foreign directory with no catalog entry  -> unexpected state, never silently adopt
```

A receipt inside the environment can still be useful as generation metadata. It stops being the only surviving authority for what the installation was supposed to be.

## 4. Tool upgrades should create generations

I would make an installed tool look conceptually like:

```text
ruff/
├── current -> generations/000014
└── generations/
    ├── 000013/
    └── 000014/
```

Upgrade path:

```text
resolve desired update
      ↓
build generation 000015 off to the side
      ↓
validate environment + receipt + lock + expected entrypoints
      ↓
publish generation metadata
      ↓
atomically switch current 000014 -> 000015
      ↓
reconcile exposures that changed
      ↓
retain 000014 for bounded rollback
```

A crash during build leaves `current` on the previous complete generation. A later cleanup can remove the abandoned staging directory.

This directly attacks the mixed-generation family where environment, launcher, lock, and receipt can otherwise describe different versions after a late failure.

### History and rollback

The CLI becomes pleasantly unsurprising:

```text
uv tool history ruff
uv tool rollback ruff
uv tool rollback ruff --to 13
```

I would keep a small number of previous generations by default and let `uv tool gc` remove older unused generations.

## 5. Public executable ownership should be first-class

A tool manager should never need to guess whether a public executable belongs to it while uninstalling or repairing.

The internal exposure catalog would record something like:

```rust
struct Exposure {
    public_path: PathBuf,
    owner: ToolId,
    entrypoint: String,
    created_identity: FileIdentity,
}
```

Removal rule:

```text
remove only if the current file still matches the exposure uv published
```

If another tool or the user replaced the path afterward, preserve it and emit a finding.

This would improve several families at once:

- uninstall after receipt loss;
- stale entrypoints after tool removal;
- collisions during install;
- an application dropping an entrypoint during upgrade;
- another package manager replacing a uv-owned command;
- Windows copied/trampoline executables where a dangling-symlink check is unavailable.

### Stable launchers

I would seriously consider making uv-generated launchers target a stable per-tool `current` path instead of a version-specific environment path. Then ordinary upgrades do not need to rewrite every unchanged launcher.

A generic trampoline plus a versioned exposure map is even cleaner, though it adds runtime complexity. The design criterion would be: **switching the current tool generation should require as few public filesystem mutations as possible.**

## 6. Findings and remediations are data

Every health problem should have a stable code and structured evidence:

```rust
struct Finding {
    code: FindingCode,
    severity: Severity,
    subject: Subject,
    summary: String,
    evidence: Vec<Evidence>,
    remediations: Vec<Remediation>,
}

struct Remediation {
    action: RepairAction,
    confidence: Confidence,
    safety: Safety,
    preview: String,
}

enum Confidence {
    Certain,
    Conditional,
    Unknown,
}

enum Safety {
    ReadOnly,
    Reversible,
    Destructive,
}
```

Automation rule:

```text
Certain + ReadOnly        -> safe to run automatically
Certain + Reversible      -> may be auto-applied under an explicit repair policy
Conditional + Reversible  -> present to user, preserve rollback
anything Destructive      -> require explicit user authorization
Unknown                   -> diagnose only
```

This is the rustc applicability idea adapted to filesystem ownership.

Examples:

```text
F1001 invalid-tool-directory-name
confidence: certain
safety: reversible
repair: move unexpected child into uv quarantine
```

```text
F1204 tool-root-permission-denied
confidence: unknown
safety: unknown
action: none
```

```text
F2102 missing-environment-with-valid-spec
confidence: certain
safety: reversible
repair: rebuild a new generation from ToolSpec
```

## 7. A real health and repair surface

I would add these commands:

```text
uv tool status
uv tool doctor
uv tool repair
uv tool history <name>
uv tool rollback <name>
uv tool gc
```

### `uv tool status`

Cheap, read-only inventory summary. It should avoid network access and expensive package verification.

```text
$ uv tool status
Tool directory: /home/leo/.local/share/uv/tools
Root: initialized (schema 1)
Inventory: degraded

✓ black 25.1.0
✓ ruff 0.12.4
! unexpected directory: /home/leo/.local/share/uv/tools/tool backup
  F1001 invalid-tool-directory-name

2 healthy, 1 finding
```

### `uv tool doctor`

Deeper read-only validation:

- catalog/spec readability;
- current-generation pointer validity;
- receipt/schema consistency;
- interpreter launchability;
- lock readability;
- entrypoint ownership;
- expected versus observed exposures;
- leftover transaction/staging state;
- optional full generation integrity checks.

It should emit findings, never silently repair them.

### `uv tool repair`

Consumes the same findings and produces a plan.

Default:

```text
$ uv tool repair --dry-run
F1001 /home/leo/.local/share/uv/tools/tool backup
  would move unexpected directory to:
  /home/leo/.local/share/uv/tools/.uv/quarantine/2026-08-12/tool backup
  safety: reversible

No tool environments would be changed.
```

Apply:

```text
$ uv tool repair
Moved unexpected directory to quarantine
Re-inspecting tool state...
Inventory complete
```

For ambiguous findings:

```text
F1204 cannot read /opt/uv/tools/ruff/uv-receipt.toml: Permission denied
  no automatic repair available
```

The recovery command itself should use the same inventory model, so we never reproduce the current failure mode where a hint points at a command that cannot survive the damaged state.

## 8. Quarantine beats deletion for unknown objects

When the root is positively owned by uv and an unexpected child blocks inventory, our preferred repair should usually be **quarantine**:

```text
<root>/tool backup
    ↓
<root>/.uv/quarantine/<timestamp>/tool backup
```

Benefits:

- same-filesystem rename can be cheap and atomic on common filesystems;
- questionable state is preserved for inspection;
- retry immediately tests whether it was the blocker;
- user can restore it;
- uv avoids asserting that the object was junk.

Quarantine is disabled automatically when the root itself is unclaimed or its ownership marker is invalid.

## 9. Transaction state should be visible

For operations that span generation publication and exposure changes, keep a tiny transaction record under `.uv/transactions/`.

Illustrative record:

```json
{
  "id": "tx-01J...",
  "tool": "ruff",
  "from_generation": 14,
  "to_generation": 15,
  "phase": "generation-published",
  "pending": ["remove-exposure:ruff-lsp"]
}
```

On the next command, uv can classify the unfinished work instead of reverse-engineering intent from whatever files remain.

The transaction journal should remain small. Immutable staging + one atomic current-generation switch should carry most of the safety; the journal exists for the few cross-resource side effects that remain.

## 10. Human status and machine status use the same finding codes

Human:

```text
! ruff: environment is missing
  F2102
  hint: Run `uv tool repair ruff` to rebuild it from recorded install metadata
```

Machine:

```json
{
  "schema": 1,
  "complete": true,
  "root": {
    "path": "/home/leo/.local/share/uv/tools",
    "source": "default",
    "ownership": "claimed"
  },
  "tools": [
    {
      "name": "ruff",
      "state": "degraded",
      "findings": [
        {
          "code": "F2102",
          "kind": "missing_environment",
          "remediations": [
            {
              "action": "rebuild_generation",
              "confidence": "certain",
              "safety": "reversible"
            }
          ]
        }
      ]
    }
  ]
}
```

Human wording can evolve. `schema: 1`, finding codes, enums, and field meanings are the porcelain contract.

## 11. Aggregate commands have a completeness contract

Every all-tools operation receives an inventory with `complete` plus findings.

The default rule:

```text
unknown coverage cannot become affirmative success
```

For our CLI I would use a simple exit model:

```text
0 = operation completed over the full selected scope and policy passed
1 = operation completed over the full scope and found a domain-negative result
    (for example vulnerabilities or doctor findings)
2 = requested scope could not be completed
```

Examples:

```text
uv tool upgrade --all
0 = all selected tools inspected and settled
2 = inventory incomplete or an upgrade failed
```

```text
uv tool audit --all
0 = complete audit, no vulnerabilities
1 = complete audit, vulnerabilities found
2 = audit coverage incomplete or execution failed
```

Machine output always carries `complete` so callers do not infer coverage from an empty array.

I would resist an `--allow-partial` mode that turns incomplete coverage into exit 0. A `--best-effort` mode may still produce partial results, but the status should continue to communicate incompleteness.

## 12. Manifest/export gives users an escape hatch

The desired tool catalog should be exportable:

```text
uv tool export > tools.toml
uv tool sync tools.toml
```

Example:

```toml
[tool.ruff]
requirement = "ruff>=0.12"
python = ">=3.12"

[tool.black]
requirement = "black==25.1.0"
python = "3.13"
```

This gives users a recovery route even after catastrophic local-state loss and makes a machine's tool setup reproducible.

The on-disk internal catalog can contain more implementation metadata; the export format should stay small and user-owned.

## 13. State migrations fail intelligibly

Every persistent metadata format carries a schema version.

Older uv reading newer state should say:

```text
error: This tool state was written by a newer uv
  Caused by: tool metadata schema 4 is newer than supported schema 3

hint: Upgrade uv before modifying this tool installation
```

A migration should create/retain enough prior metadata to roll back the migration itself when feasible.

We should never turn an unsupported state version into `malformed receipt`, because those imply different recovery authority.

## 14. Fuzzy help and recovery help stay separate

For input mistakes, be generous:

```text
$ uv tool upgrdae ruff
error: unrecognized subcommand `upgrdae`

  tip: a similar subcommand exists: `upgrade`
```

For observed state, require evidence:

```text
/home/leo/.local/share/uv/tools/ruf
```

must never silently become `ruff` because edit distance says so.

A typo in user input can be corrected heuristically. A filesystem object is already state; adopting or mutating it changes ownership.

## 15. Entry-point collisions should explain authority

Instead of:

```text
error: Executable already exists: black
hint: use --force
```

our version would try to classify the existing path:

```text
error: Cannot expose `black`: `/home/leo/.local/bin/black` already exists

existing owner: outside uv
requested owner: uv tool `black`

hint: Use `--force` only if uv should replace this existing executable
```

If the file is known to belong to another uv tool:

```text
existing owner: uv tool `black-beta`
```

Now `--force` has an intelligible consequence.

## 16. Example: the original invalid-directory case in our version

Correct root, unexpected child:

```text
$ uv tool upgrade --all
error: Failed to inspect installed tools
  Caused by: Invalid tool directory name: `/home/leo/.local/share/uv/tools/tool backup`
  Caused by: Not a valid package or extra name: "tool backup" ...

hint: Run `uv tool repair --dry-run` to preview a reversible recovery
```

Dry run:

```text
$ uv tool repair --dry-run
F1001 invalid tool directory name
  path: /home/leo/.local/share/uv/tools/tool backup
  action: quarantine unexpected directory
  safety: reversible
  confidence: certain
```

Wrong root:

```text
$ UV_TOOL_DIR=$HOME uv tool upgrade --all
error: The configured tool directory is not initialized for uv
  Caused by: `UV_TOOL_DIR` points to `/home/leo`

hint: Check `UV_TOOL_DIR` before initializing or modifying this directory
```

That distinction is the product experience I want.

## 17. Example: corrupt receipt with independent desired state

```text
$ uv tool status ruff
ruff — degraded

✓ desired spec: ruff>=0.12
✓ current generation: 14
! receipt: malformed TOML
✓ environment: executable
✓ exposures: 1/1 owned

F2201 malformed generation receipt
repair: rebuild a new generation from recorded desired state
```

Then:

```text
$ uv tool repair ruff
Built generation 15 from recorded spec
Validated receipt, environment, and exposures
Switched current generation 14 -> 15
Retained generation 14 for rollback
```

The corrupt receipt remains evidence inside old generation 14 until GC.

## 18. Example: interrupted upgrade

```text
$ uv tool status ruff
ruff — healthy
current generation: 14

info: abandoned staged generation 15 found
repair: remove abandoned staging state
```

No mixed live state, no mystery about which version is authoritative.

If publication occurred and cleanup was interrupted:

```text
ruff — degraded
current generation: 15
transaction tx-01J...: cleanup pending

! stale owned exposure `/home/leo/.local/bin/ruff-lsp`
repair: finish transaction
```

The transaction record explains intent directly.

## 19. What I would leave out

A VDFL still says no to plenty of cleverness.

I would avoid:

- silently adopting unknown directories as tools;
- automatically deleting foreign files;
- arbitrary rename recovery;
- auto-repair that changes requested package versions;
- treating a machine-readable empty result as complete when inspection failed;
- one giant `repair everything` algorithm whose actions cannot be previewed separately;
- network access in the cheap `status` command;
- putting every possible validation on the hot path of ordinary `uvx` execution;
- fuzzy state reconciliation based on filenames alone;
- hiding an unfinished transaction by printing the last known healthy metadata as though it were current observation.

## 20. Smallest coherent version of this vision

We would not need to build all of this at once.

A plausible sequence for our own product:

### Phase 1 — truthful observation

- root marker + reserved `.uv/` namespace;
- typed `ToolInventory` with `complete`;
- `uv tool status --output json`;
- stable finding codes;
- aggregate commands consume completeness explicitly.

### Phase 2 — recovery

- `uv tool doctor`;
- structured remediations with confidence/safety;
- `uv tool repair --dry-run`;
- quarantine for confidently unexpected children in an owned root;
- ownership-aware exposure catalog.

### Phase 3 — rebuildability

- independent desired `ToolSpec` catalog;
- repair broken/missing environments from recorded intent;
- export/sync user manifest.

### Phase 4 — transactional generations

- staged immutable generations;
- atomic current pointer;
- bounded history/rollback;
- transaction records for remaining multi-resource publication work;
- garbage collection.

Each phase improves the product by itself.

## Current favorite UX

If I had to choose the personality of our tool manager in one sentence:

> It should tell you exactly what it knows, exactly what it could not establish, and the safest action it can actually perform from the state you are in.

And if it knows enough to fix something safely, the hint should stop being a paragraph and become a previewable repair plan.
