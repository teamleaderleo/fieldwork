# F276-linux-cache-parent-swap: cache path validation can lose authority before I/O

Finding state: `research-active`

Workstream: `H`  
Canonical Fieldwork issue: `#276`  
Canonical finding path: `findings/F276-linux-cache-parent-swap/finding.md`  
Canonical implementation: `none`  
Exact implementation head: `none`  
Canonical evidence carrier: `teamleaderleo/linux-fieldwork` draft PR #228  
Exact evidence head: `dabe79cefb6062e20dc6201556b5f541a8470bbc`  
Exact base or source revision: `teamleaderleo/linux-fieldwork@ed49c01a85e9d363626db5d2973a33b67209e13b`  
Strongest evidence class: `model-executed`  
Reviewed input generation: `teamleaderleo/linux-fieldwork` issue #227 and PR #228  
Current review disposition: `none`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

The Linux caching proxy checks that a package path belongs below its cache directory. It stores the checked result as an ordinary pathname and later walks that pathname again to read or publish bytes. A same-UID process may replace one checked parent directory or final object with a symlink during that gap. The current investigation inserts deterministic barriers, restores each mutated state, reruns the same roots, and repeats the complete matrix under optimized Python.

A local generated-source model already reproduced outside reads and outside publication through replacement parents. Hosted Linux execution remains the authority for the exact repository head and complete matrix.

## Why we care

A redirected cache read can return local file bytes outside the cache root through the loopback proxy. A redirected publication can write origin bytes outside the cache root with the proxy process's permissions. The scenario requires another process with the same user identity and mutation authority over a cache descendant. Production frequency, installed-service exposure, and cross-UID impact remain unknown.

## What happens if we leave it alone

The merged composed proxy states same-UID pathname replacement as an evidence limit. The local model now shows a deterministic consequence for the generated pathname operations: parent replacement redirects old-cache reads and new-cache publication, while final publication replaces the symlink entry itself. A vulnerable cache layout can turn a validated request into a later read or write under a different parent directory.

## Current finding

The exact composed candidate separates path validation from path use:

1. `request_context()` resolves a candidate and verifies that it is a strict descendant of the resolved cache root;
2. the handler retains a `pathlib.Path` value;
3. cache-hit checks and reads later call pathname-based `exists`/`stat`/`open` operations;
4. publication later constructs a sibling temporary pathname, calls pathname-based `os.open()`, and calls pathname-based `os.replace()`.

Those later operations re-resolve parent components. The source therefore contains the classic check/use boundary described by the Linux `openat()` rationale.

The local generated-source model produced this component split:

- old-cache parent replacement returned outside bytes and copied them into the new cache;
- old-cache final-object replacement returned outside bytes and copied them into the new cache;
- new-cache parent replacement published the complete origin object in the outside directory;
- new-cache final-name replacement atomically replaced the symlink entry while leaving its outside target unchanged.

Linux Fieldwork CI run 677 remains queued for the exact repository head, inherited complete matrix, same-root reruns, and optimized child execution.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The composed candidate validates a resolved strict descendant before the handler continues. | `source-read` | `linux-fieldwork/investigations/caching-proxy-complete-stack/compose_impl.py`, `request_context()` at base `ed49c01a...` | This proves the validation step, not later confinement. |
| Cache-hit reads later use the retained pathname for existence, metadata, and open operations. | `source-read` | Imported `upstream/mmdebstrap/caching_proxy.py` cache-hit branch plus the composed setup replacement at `ed49c01a...` | Generated-source execution is recorded separately. |
| Atomic publication later derives a sibling temporary pathname and uses pathname-based `os.open()` and `os.replace()`. | `source-read` | `linux-fieldwork/investigations/caching-proxy-atomic-publication/0001-publish-cache-files-atomically.patch` | Atomic naming does not by itself bind the parent directory identity. |
| Parent replacement redirected an old-cache read and new-cache publication outside the validated roots; final publication replaced the symlink entry without changing its target. | `model-executed` | `evidence/20260731-h-local-generated-source-model.md` | Manual reconstruction from inspected exact source fragments; no full checkout, inherited matrix, or optimized child. |
| The deterministic parent and final-component barriers, cleanup reruns, and optimized child matrix are published on one exact branch. | `target-test-prepared` | Linux PR #228, `tests/test_caching_proxy_parent_swap_race.py` at `dabe79ce...` | No target result is claimed until hosted execution completes. |

## System and ownership map

- **Entrypoint:** loopback HTTP `ProxyRequestHandler.do_GET()` in the generated caching-proxy candidate.
- **Request owner:** `request_context()` parses authority and path, rejects aliases and traversal, and returns old/new cache paths.
- **Read owner:** the cache-hit branch checks the cache path, sends its length, opens it, streams bytes to the client, and may copy old-cache bytes into the new cache.
- **Publication owner:** `cache_destination()` allocates a hidden exclusive temporary file and publishes it with `os.replace()` after streaming completes.
- **State owner:** the filesystem names below `oldcachedir` and `newcachedir`; the handler owns one request but does not retain directory descriptors.
- **Side effects:** loopback response bytes, cache reads, new-cache directory and temporary creation, final-name replacement, logs, and cleanup.
- **Recovery:** exceptions remove the temporary name; post-commit errors close the connection without a second response.
- **Test boundary:** Linux PR #228 subclasses the complete composed matrix, adds parent and final-component replacement probes, restores each mutated state, reruns the same roots, and launches the complete class under `python -O`.

## Historical precedent

### Linux `openat()` directory-descriptor rationale

- Source: https://man7.org/linux/man-pages/man2/openat.2.html
- Revision or date: Linux man-pages rendered 2026; retrieved 2026-07-31
- Principle supported: checking a path and later creating or opening through it races when a directory component can change to a symlink. Opening the target directory and using `*at()` calls makes the descriptor a stable directory reference even after rename.
- Important difference: this finding concerns a Python helper with two cache roots, automatic directory creation, atomic publication, readonly behavior, and compatibility requirements beyond one `openat()` call.

### Python directory-descriptor filesystem APIs

- Source: https://docs.python.org/3/library/os.html
- Revision or date: Python 3 documentation retrieved 2026-07-31; `dir_fd` support entered the relevant APIs in Python 3.3
- Principle supported: `os.open()`, `os.mkdir()`, `os.stat()`, `os.rename()`, `os.replace()`, and related functions can operate relative to directory descriptors on supporting platforms.
- Important difference: availability of primitives does not choose the cache-root trust boundary, component-walk policy, directory-creation behavior, or portability fallback.

### Linux Fieldwork guarded-path review rule

- Source: `teamleaderleo/linux-fieldwork/FIELD_GUIDE.md` at `ed49c01a...`
- Revision or date: 2026-07-31 source boundary
- Principle supported: resolve-before-delete checks still leave a donut when a later destructive or stateful operation re-traverses mutable path components; caches and streaming protocols explicitly list symlink races as productive review territory.
- Important difference: the field guide is a selection and review heuristic. This finding must establish the exact cache consequence with execution.

## Approaches considered

### Retained approach: reproduce before repair

Use deterministic barriers after validation and before the exact read/publication operation. Keep ordinary composed tests as controls. Restore the mutated component and rerun the same roots. This identifies which operation crosses the root and avoids designing against a source-only suspicion.

### Declined: another lexical prefix or `resolve()` check

A second pathname check merely moves the race window. Any check followed by later pathname traversal can lose the checked parent identity again.

### Declined: lock only the Python handler

A process-local lock coordinates threads inside one proxy process. It does not stop another same-UID process from renaming cache directories.

### Deferred: Linux `openat2()`-only implementation

`openat2()` can express strong resolution policies, but Python does not expose it as a standard high-level API. A Linux-specific syscall wrapper may become useful only if ordinary fd-relative component walking cannot preserve the contract cleanly.

### Deferred: configured-root and ancestor replacement

The first candidate may treat resolved cache roots and their external ancestors as trusted configuration while anchoring every descendant traversal to an opened root descriptor. Root replacement and hostile ancestors require a separate, explicitly broader authority decision.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| Ordinary request, origin status, framing, retry, permissions, concurrency, and cleanup | Inherited complete composed matrix | Published on PR #228; exact-head rerun pending. |
| Old-cache parent renamed after both cache paths validate | Deterministic parent-read barrier | Model reproduced outside read/copy; target test adds preservation, cleanup, and rerun. |
| Old-cache final object replaced after validation | Deterministic final-read barrier | Model reproduced outside read/copy; target test adds preservation, cleanup, and rerun. |
| New-cache parent renamed before temporary creation | Deterministic publication barrier | Model reproduced outside publication; target test adds sentinel, cleanup, and rerun. |
| New-cache final-name symlink inserted before publication | Atomic replacement control | Model replaced symlink entry and preserved outside target; target execution pending. |
| Ordinary and optimized interpreter behavior | Child process with `python -O` | Prepared; child marker skips only recursive launching. |
| Hidden temporary cleanup and same-root recovery | Assertions after each mutation | Prepared. |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| Primary new-cache-hit parent replacement | The baseline proves the underlying read authority loss through the old-cache branch first; the first repair must audit both cache-hit branches. | Candidate-wide path audit after target execution. |
| Replacement before recursive new-cache parent creation | Same validated-name invariant, with a directory-creation consequence rather than file publication. | Candidate-wide path audit after target execution. |
| Configured cache root or external ancestor replacement | Broader trust boundary than descendant swap | Separate finding after the descendant result. |
| Cross-UID attacker | Filesystem permission model differs | Reopen with a concrete writable shared-cache deployment. |
| Remote exposure | Candidate binds loopback and no deployment evidence is retained | Reopen with an evidenced remote deployment path. |
| Crash-durable sync | Independent from path identity | Existing cache-composition deferred work. |
| Miss coalescing and checksums | Independent cache semantics | Existing cache-composition deferred work. |
| Arbitrary URI syntax | Request-language decision | Existing cache-composition deferred work. |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| `linux-fieldwork@ed49c01a...` | merged PR #198 complete matrix, run 612 | hosted Linux / Python | success | `integration-executed` |
| reconstructed generated source from `ed49c01a...` | real loopback requests plus parent/final rename-symlink transitions | local Linux / Python 3.13.5 | parent read, final read, and parent publication escaped; final publication target preserved | `model-executed` |
| `linux-fieldwork@dabe79ce...` | direct test plus child `python -O`, via Linux Fieldwork CI run 677 | hosted Linux | queued | `target-test-prepared` |

Classify any failure before the race assertions separately as setup, import, composer, patch, inherited-matrix, optimized-child, or cleanup/rerun failure.

## Complete-diff and compatibility review

- Complete changed-file fence: one Linux investigation README and one focused test.
- Current-base relationship: branch started directly from Linux `main` `ed49c01a...`.
- Temporary carrier status: PR #228 is an evidence carrier and candidate-development surface, not an accepted product patch.
- Imported upstream source: unchanged.
- Compatibility surfaces retained by inheritance: request validation, ordinary and optimized Python controls, cache permissions, atomic final-name visibility, origin status and framing, incomplete-stream cleanup, retry, post-commit behavior, loopback servers, sockets, threads, and temporary files.
- Known routine work: obtain exact-head execution; then update the claim table and design the smallest fd-relative candidate covering every descendant operation.
- Reviewer eligibility: builder self-review only at this state.

## Current disposition and desk routing

- Finding state: `research-active`
- Review disposition: `none`
- Review Queue entry: `none`
- Delivery lane: `not-entered`
- Exact next transition: execute Linux PR #228 at `dabe79ce...`.
- Clearing condition: run 677 completes with authoritative race results, inherited controls, same-root reruns, and optimized execution.
- Required subgates: complete output review, cleanup review, current-base refresh, and exact-head synchronization.
- User decision requested: `none`

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-31 | Linux PR #228 initial head | Converted the merged composition's explicit race limit into a bounded deterministic investigation; no race result claimed. |
| 2026-07-31 | Linux PR #228 `dabe79ce...` | Added final-component controls, explicit state restoration, same-root reruns, and a real optimized-Python child matrix; target result remains pending. |
| 2026-07-31 | Local generated-source model | Reproduced outside reads and outside publication through replacement parents; confirmed final publication replaces the symlink entry while preserving its target. |

## References

- `teamleaderleo/fieldwork` issue #276
- `teamleaderleo/linux-fieldwork` issues #188 and #227
- `teamleaderleo/linux-fieldwork` PRs #198 and #228
- `evidence/20260731-h-source-map.md`
- `evidence/20260731-h-local-generated-source-model.md`
- `teamleaderleo/linux-fieldwork@ed49c01a.../investigations/caching-proxy-complete-stack/compose_impl.py`
- `teamleaderleo/linux-fieldwork@ed49c01a.../investigations/caching-proxy-atomic-publication/0001-publish-cache-files-atomically.patch`
- `teamleaderleo/linux-fieldwork@ed49c01a.../upstream/mmdebstrap/caching_proxy.py`
- Linux `openat(2)` rationale: https://man7.org/linux/man-pages/man2/openat.2.html
- Python `os` directory-descriptor APIs: https://docs.python.org/3/library/os.html
