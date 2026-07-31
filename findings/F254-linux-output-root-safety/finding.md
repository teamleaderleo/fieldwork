# F254-linux-output-root-safety: do not derive recursive-delete authority from temporary-directory discovery

Finding state: `closed`

Workstream: `H`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-linux-output-root-safety/finding.md`  
Investigation workspace: `investigations/254-linux-storage-archive-reproducibility/`  
Canonical implementation: `teamleaderleo/linux-fieldwork` PR #199  
Exact implementation head: `6251a11fd30b26d29451e5ee292a6186344429a1`  
Exact base or source revision: `a0ec62f64fd6a9ff2cc20b28142ec876c52a5145`  
Reviewed input generation: direct guard predecessor `b1e8aa4e9376e41962e456467c2f3fdcb38cae17`; symlink proof `556c15c67b2978a1eae635a27f4b69986b4dc0e2`  
Current review disposition: `ACCEPT`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

The LF-23 cancellation harness deletes and recreates its output directory. It used Python's current temporary-directory answer as permission for that recursive deletion.

In one real sandbox, `/tmp` disappeared between commands and Python chose the checkout as its temporary directory. A repository child then passed the guard and its sentinel was deleted before the cancellation test began.

The merged repair separates discovery from authority: only strict descendants of the harness artifact directory, `/tmp`, or `/var/tmp` are disposable. The complete requested path is resolved first, so neither a final symlink nor an ancestor symlink can redirect deletion elsewhere.

## Why we care

A test harness must not destroy source or evidence while attempting to test product behavior. This is a filesystem authority boundary: the caller chooses a path, and the harness performs recursive replacement with its own process permissions.

Misclassifying the harness failure as a product cancellation result would also contaminate every later conclusion.

## What happens if we leave it alone

Runtime temporary-directory selection can vary with environment variables and filesystem availability. If the selected directory happens to be the checkout, a repository child can be treated as disposable. A string-prefix or unresolved-child check can also approve a path whose final or ancestor symlink points outside the allowed root.

The observed consequence was real sentinel deletion. The merged guard and regressions close the demonstrated direct and symlink forms.

## Current finding

Destructive path authorization must come from an explicit allowlist and the resolved requested path, not from `tempfile.gettempdir()` or string shape. The harness now:

- resolves the complete output path;
- rejects the allowed roots themselves;
- requires a strict descendant of the artifact directory, `/tmp`, or `/var/tmp`;
- preserves rejected paths and sentinels;
- enforces the same rule under ordinary and optimized Python.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Dynamic temporary-directory discovery can resolve into the checkout and grant unintended recursive-delete authority. | target-executed | retained reproduction and direct regression in `investigations/lf-23-cancellation-harness-safety/README.md` | Frequency outside the observed sandbox is unknown. |
| The merged guard rejects direct roots and repository children selected through `TMPDIR` fallback. | target-executed | PR #199 head `6251a11f...`; `tests/test_lf23_cancellation_harness_safety.py`; CI run `30580869813` / 620 | Custom roots outside the explicit allowlist remain unsupported. |
| Resolving the complete path before authorization rejects both final-component and ancestor-symlink escapes. | target-executed | `tests/test_lf23_cancellation_harness_symlink_safety.py`; predecessor run 596; final run 620 | Same-UID mutation after validation is outside the focused proof. |
| The safety composition did not execute the separate product cancellation probe. | source-read | exact workflow list for `6251a11f...`: Linux Fieldwork CI success; LF-23 cancellation probe skipped | The finding does not claim renewed cancellation-product execution on this head. |

## System and ownership map

- Entry point: `cancellation_harness.py` receives a caller-selected output path.
- Authority owner: the harness guard decides whether recursive replacement is permitted.
- Side effect: the selected directory may be removed and recreated before the cancellation matrix runs.
- State at risk: source checkout, sentinels, retained artifacts, or any same-permission tree reached through a path.
- Cleanup owner: Python filesystem operations after guard approval.
- Test boundary: subprocesses with controlled `TMPDIR`, real directories and symlinks, sentinel bytes, ordinary and optimized Python.

## Historical precedent

### Linux Fieldwork guarded-but-unresolved donut

- Source: https://github.com/teamleaderleo/linux-fieldwork/blob/main/FIELD_GUIDE.md
- Revision or date: lessons through 2026-07-30
- Principle supported: resolve first, reject roots, require a strict child, then perform destructive removal.
- Important difference: this finding executes both final and ancestor symlink forms against the specific LF-23 harness.

### Python temporary directory selection

- Source: https://docs.python.org/3/library/tempfile.html#tempfile.gettempdir
- Revision or date: Python documentation retrieved 2026-07-31
- Principle supported: the returned temporary directory depends on environment and runtime discovery.
- Important difference: the API reports a location; it does not authorize recursive deletion of every descendant selected by a caller.

### Python path resolution

- Source: https://docs.python.org/3/library/pathlib.html#pathlib.Path.resolve
- Revision or date: Python documentation retrieved 2026-07-31
- Principle supported: resolution exposes symlink and `..` effects before a containment decision.
- Important difference: resolution narrows decision-time authority but does not by itself eliminate later same-UID mutation races.

## Approaches considered

### Retained approach: explicit roots plus resolved strict-descendant check

The allowlist is small, reviewable, and tied to harness-owned disposable state. Resolving the full request before comparison defeats both final and ancestor symlink redirects in the executed model.

### Declined: trust `tempfile.gettempdir()`

Temporary-directory discovery is environment-dependent and can return a repository path. It is not an authority declaration.

### Declined: string prefix checks

A prefix can match siblings, `..`, or unresolved symlink paths. The repository field guide already records this as a destructive-operation failure pattern.

### Deferred: descriptor-relative deletion with race fencing

Same-UID mutation after validation requires a different design around directory handles, open-at semantics, or ownership assumptions. The current repair is bounded to decision-time resolution.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| output equals an allowed root | direct safety test | rejected |
| output is a repository child after `TMPDIR` points to checkout | direct safety test | rejected; sentinel preserved |
| output is a strict artifact-directory descendant | existing harness control | allowed |
| final output component is a symlink to outside target | symlink safety test | rejected; link and sentinel preserved |
| ancestor below `/tmp` or `/var/tmp` is a symlink to outside target | symlink safety test | rejected; no outside output created |
| ordinary and optimized Python | focused reconstructed slice | 4/4 normal and 4/4 optimized succeeded |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| same-UID mutation after resolution | decision-time proof cannot fence later mutation | reopen on a demonstrated race or descriptor-relative candidate |
| additional caller-configurable roots | each root widens destructive authority | require separate allowlist review and controls |
| platform-specific path semantics outside Linux | repository and harness are Linux-focused | reopen with a supported platform requirement |
| product cancellation behavior | safety composition changed only harness authority and tests | owning LF-23 cancellation investigation |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| linux-fieldwork@`b1e8aa4e9376e41962e456467c2f3fdcb38cae17` | Linux Fieldwork CI `30578704079` / 564 | hosted Linux | success | target-executed |
| linux-fieldwork@`556c15c67b2978a1eae635a27f4b69986b4dc0e2` | Linux Fieldwork CI `30579993408` / 596 | hosted Linux | success | target-executed |
| linux-fieldwork@`6251a11fd30b26d29451e5ee292a6186344429a1` | Linux Fieldwork CI `30580869813` / 620 | hosted Linux | success | target-executed |
| reconstructed guard slice | normal and `python -O` focused tests | local Linux, outside `/tmp`, `PYTHONPATH=tests` | 4 tests success in each mode | target-executed |
| linux-fieldwork@`6251a11f...` | LF-23 cancellation probe run 77 | hosted Linux | skipped | setup/routing evidence only |

## Complete-diff and compatibility review

- Complete changed-file fence: five files in PR #199.
- Current-base relationship at merge: base `a0ec62f...`; merge commit `12dd20f...`.
- Temporary carrier status: PRs #208 and #217 were closed after unique proof content reached canonical PR #199.
- Compatibility surfaces examined: direct roots, repository fallback, artifact-root authority, final and ancestor symlinks, sentinel preservation, ordinary/optimized Python.
- Known routine repair remaining: none within decision-time authority scope.
- Review eligibility: consequential destructive-path work received cross-review and exact-head hosted CI; no public acceptance is implied.

## Current disposition and desk routing

- Finding state: `closed`
- Review disposition: `ACCEPT`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: none; retain merged guard and proofs
- Clearing condition: satisfied by PR #199 merge and CI run 620
- Required subgates: none
- Autonomous work remaining: none within scope
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | predecessor `b1e8aa4e...` | removed dynamic temp-root authority and proved direct preservation |
| 2026-07-30 | review carrier #208 | added final and ancestor symlink controls |
| 2026-07-30 | PR #199 head `6251a11f...` | composed all unique safety work; CI run 620 succeeded |
| 2026-07-30 | merge `12dd20f...` | local harness-safety correction closed |
| 2026-07-31 | Linux Fieldwork PR #249 | stale rerun/merge wording repaired |

## References

- https://github.com/teamleaderleo/linux-fieldwork/pull/199
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/investigations/lf-23-cancellation-harness-safety/README.md
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/investigations/lf-23-cancellation-harness-symlink-safety/README.md
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/tests/test_lf23_cancellation_harness_safety.py
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/tests/test_lf23_cancellation_harness_symlink_safety.py
- Linux Fieldwork CI runs `30578704079`, `30579993408`, and `30580869813`
- Linux Fieldwork PR #249 durable-state repair
