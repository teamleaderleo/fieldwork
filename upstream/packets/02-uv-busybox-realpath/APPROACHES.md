# Approaches — Unit 02: BusyBox-safe relocatable launchers

## Selected approach

Remove only unsupported `realpath --` delimiters from every generated relocatable owner, retain `dirname --`, preserve `realpath`-based symlink canonicalization, and make `copy_entrypoint` recognize corrected and historical `python` and `python3` forms.

State: `TECHNICALLY GREEN — CLEAN SOURCE PUBLICATION PENDING`.

## Decision criteria

1. BusyBox success must have clean stderr.
2. GNU behavior and external-symlink interpreter selection must remain unchanged.
3. Generated wheel, POSIX activation, fish activation, project-run recognition, and native assertions must stay synchronized.
4. Existing uv-generated launchers must remain copyable after upgrade.
5. The source contribution must remain one reviewable four-file commit with no Fieldwork machinery.

## Why this approach won

- It changes the exact utility that fails and no more.
- GNU and Alpine 3.22 BusyBox execution passed.
- Historical macOS execution supports the same delimiter-free form.
- PR #8079's symlink-first behavior remains intact because `realpath` remains.
- The exact native fish/venv expectation passes.
- Four-form migration coverage prevents silent skipping of old launchers.

## Rejected or deferred approaches

### Remove `--` from both utilities

The superseded clean branch did this. Rejected because BusyBox `dirname --` passes the matrix, so removing it creates unnecessary generated-text churn and a larger migration surface.

### Detect BusyBox or shell flavor during generation

Rejected because relocatable files can execute on a different host from the generator. One common emitted form is more reliable than recording generation-host utility behavior.

### Redirect `realpath` stderr

Rejected because it hides genuine path-resolution errors along with the false BusyBox diagnostic.

### Replace `realpath` with `readlink -f` or `cd`

Rejected because it changes the utility/semantic contract and risks reopening the external-symlink defect fixed by PR #8079.

### Normalize an option-like `$0`

Deferred. Direct generated-shebang execution exposed the script pathname, not caller-requested bare values such as `-tool`. The supported `./-tool` case passed. Add normalization only for a reproducible supported entry path.

### Recognize arbitrary interpreter basenames

Deferred. The exact migration contract has observed `python` and `python3` producers. Pattern matching versioned or alternate interpreter names without an observed producer would broaden a security- and correctness-sensitive exact-prefix parser by speculation.

### Recognize only corrected forms

Rejected. Existing virtual environments can retain delimiter-bearing launchers after uv upgrades. Current plus historical recognition is a bounded migration cost with a direct unit test.

### Cross-crate launcher-text centralization

Deferred. It may be maintainable later, but it is not needed to fix the compatibility defect and would expand dependencies and review scope.

## Executed discriminators

| Question | Result | Decision |
| --- | --- | --- |
| Does current BusyBox emit noise? | yes, every baseline case | remove `realpath --` |
| Does BusyBox accept retained `dirname --`? | yes | keep it |
| Does GNU accept delimiter-free `realpath`? | yes | common form selected |
| Does external-symlink behavior survive? | yes | retain `realpath` |
| Do old and new `python`/`python3` launchers copy? | yes, direct unit test | four exact forms |
| Does direct shebang execution expose bare option-like `$0`? | no | no shell normalization |
| Do target-native generated expectations pass? | yes | four-file boundary |
| Does full declared clippy pass? | yes | source shape accepted |

## Exact validated receipt

- Base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Carrier: `c8a5c36d60a5cc35f496f583146967e210f87810`
- Run/job: `30753911776` / `91512671857`
- Artifact: `8835628919`
- Artifact SHA-256: `1d54c978b355e807bb69f962f866574d8c200ae624ed55b0ac9a6cd8c631ff0c`

The remaining action is atomic publication of that exact four-file tree. No public upstream contact occurred.