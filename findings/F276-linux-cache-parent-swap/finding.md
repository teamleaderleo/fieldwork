# F276-linux-cache-parent-swap: cache path validation can lose authority before I/O

Finding state: `repair`

Workstream: `H`  
Canonical Fieldwork issue: `#276`  
Canonical finding path: `findings/F276-linux-cache-parent-swap/finding.md`  
Canonical implementation: `none`  
Exact implementation head: `none`  
Canonical Linux baseline carrier: `teamleaderleo/linux-fieldwork` draft PR #255  
Exact Linux baseline head: `d204faf3f38293a1171a0735bdd0224e6dd95899`  
Historical Linux evidence carrier: closed PR #228 at `dabe79cefb6062e20dc6201556b5f541a8470bbc`  
Exact source base: `teamleaderleo/linux-fieldwork@8827ad0764a532b737d8b501cf0980b7f330294a`  
Strongest evidence class: `target-executed` for the reproduced pathname behavior  
Cleanup-gate evidence class: `target-test-prepared`  
Current review disposition: `HOLD`  
Upstream contact authorized: `no`

## In simple words

The Linux caching proxy checks that a package path belongs below its cache directory. It keeps the checked result as an ordinary pathname and later walks that pathname again to read or publish bytes.

Deterministic tests proved that another same-user process can replace a checked parent directory or old-cache object during that gap and redirect later work outside the validated cache root. The current baseline also adds a missing lifecycle gate: the complete evidence suite must run under dedicated temporary roots, leave them empty, and leave the checkout unchanged under ordinary and optimized Python.

## Why we care

A redirected cache read can return outside-file bytes through the loopback proxy. A redirected publication can write origin bytes outside the cache root with the proxy process's permissions.

The scenario requires another process with the same user identity and mutation authority over a cache descendant. Production frequency, installed-service exposure, and cross-user impact remain unknown.

A clean evidence lifecycle also matters. A suite that exits zero while leaving generated directories, hidden cache temporaries, or bytecode can conceal cleanup failures and make later reruns depend on prior state.

## Current finding

The composed candidate separates validation from use:

1. `request_context()` resolves a candidate and verifies a strict descendant of the resolved cache root;
2. the handler retains a `pathlib.Path`;
3. cache-hit checks and reads later use pathname-based existence, metadata, and open operations;
4. publication later creates a sibling temporary pathname and publishes with pathname-based `os.replace()`.

Those later operations resolve parent components again.

The exact predecessor execution established this split:

- old-cache parent replacement served outside bytes and copied them into the new cache;
- old-cache final-component replacement served outside bytes and copied them into the new cache;
- new-cache parent replacement published origin bytes below the outside directory;
- new-cache final-name symlink insertion replaced the symlink entry while preserving its outside target;
- mutated state was restored and an immediate same-root rerun succeeded;
- the complete matrix passed under real optimized Python.

Linux Fieldwork CI run `30587406344` executed the predecessor exact head with 232 successful tests. Historical PR #228 is closed without merge. Current-main PR #255 preserves the behavior test and is the only active baseline carrier.

## Cleanup review and repair

Review `4824617051` found that the carried test still lacked the predecessor review's distinguishing cleanup requirement. The optimized child inherited temporary-directory selection and the suite performed no suite-level runtime inventory.

Current Linux head `d204faf3...` adds:

- `tests/test_caching_proxy_parent_swap_cleanup.py`;
- `investigations/caching-proxy-parent-swap-race/artifacts/cleanup-gate.md`.

The new gate:

- runs the complete suite under a dedicated ordinary temporary root;
- retains the suite's existing optimized-child run;
- runs a separate direct optimized execution with recursion disabled;
- sets `TMPDIR`, `TEMP`, and `TMP` to the dedicated root;
- disables bytecode writes;
- requires an empty runtime inventory after each run;
- requires unchanged top-level `complete-*` and relevant `__pycache__` checkout inventory.

The earlier current-main head `e70674ab...` passed CI run `30593222539` / 735 before this gate was added. That green run does not clear the new cleanup condition.

## Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The candidate validates a resolved strict descendant before later filesystem work. | `source-read` | composed implementation and imported cache handler at the named Linux source revisions | Validation alone does not bind later path traversal. |
| Cache-hit reads and cache publication later re-traverse retained pathnames. | `source-read` | source map and generated candidate operation map | Source ordering does not establish practical exposure frequency. |
| Parent replacement redirects old-cache reads and new-cache publication; old final-component replacement redirects reads; new final publication replaces the symlink entry. | `target-executed` | Linux run `30587406344` at predecessor head `dabe79ce...` | Same-UID deterministic fixture on hosted Linux. |
| State restoration, immediate rerun, and real optimized-Python behavior passed on the predecessor exact head. | `target-executed` | Linux run `30587406344` | Does not establish crash cleanup or every platform. |
| Dedicated ordinary/optimized temporary-root inventory is present on the current baseline branch. | `target-test-prepared` | Linux PR #255 at `d204faf3...` | Requires exact-head hosted execution and review. |

## System and ownership map

- **Entrypoint:** loopback HTTP `ProxyRequestHandler.do_GET()` in the generated caching-proxy candidate.
- **Request owner:** `request_context()` parses authority and path and returns old/new cache paths.
- **Read owner:** the cache-hit branch checks, opens, streams, and may copy an old-cache object.
- **Publication owner:** `cache_destination()` creates a hidden exclusive temporary and publishes with `os.replace()`.
- **State owner:** filesystem names below `oldcachedir` and `newcachedir`; the handler retains no directory descriptor.
- **Recovery owner:** temporary-file cleanup, connection close, thread and server shutdown, and immediate rerun assertions.
- **Current baseline owner:** Linux issue #227 and draft PR #255.

## Historical and implementation precedent

### Linux `openat()` directory-descriptor rationale

- Source: https://man7.org/linux/man-pages/man2/openat.2.html
- Principle: a checked pathname can race when a directory component changes; an opened directory descriptor supplies a stable reference for later relative operations.
- Boundary: this candidate has two roots, recursive directory creation, readonly behavior, permissions, atomic publication, and streaming contracts.

### Python directory-descriptor APIs

- Source: https://docs.python.org/3/library/os.html
- Principle: Python exposes `dir_fd` support for many filesystem operations on supporting platforms.
- Boundary: primitive availability does not choose the component-walk policy, portability fallback, or root trust boundary.

## Approaches considered

### Retained: reproduce, clean the evidence carrier, then repair

The exact behavior is established. The baseline carrier now needs its new cleanup gate executed before implementation work begins.

### Declined: another lexical prefix or `resolve()` check

A second check only moves the race window when later operations traverse the pathname again.

### Declined: process-local locking

A Python lock coordinates threads in one process and leaves same-UID filesystem mutation outside its authority.

### Candidate direction: descriptor-relative descendants

Open each configured cache root once for the request operation and perform descendant walks, creation, reads, temporary creation, and replacement relative to opened directory identity. Preserve the current external-root trust boundary explicitly.

### Deferred: Linux `openat2()`-only design

A Linux-specific resolution policy remains an option if ordinary descriptor-relative component walking cannot preserve the contract cleanly.

## Compatibility requirements for one canonical repair

A repair must preserve:

- ordinary old-cache reads and new-cache publication;
- primary new-cache-hit behavior;
- recursive descendant creation;
- `0666 & umask` mode behavior;
- atomic final-name replacement;
- hidden unique temporary names;
- readonly behavior;
- origin status, framing, complete-stream validation, and retry;
- post-commit error behavior;
- sockets, threads, server lifecycle, cleanup, and immediate rerun;
- explicit diagnostics for rejected components or unsupported platforms.

Configured roots and their external ancestors may remain trusted if every descendant operation is anchored to an opened root and never re-enters through the checked pathname.

## Deferred questions

| Question | Reason | Reopening trigger |
| --- | --- | --- |
| Configured root or external ancestor replacement | Broader trust boundary than descendant swaps | Concrete writable-root deployment or selected stronger authority model |
| Cross-UID mutation | Filesystem permissions differ | Shared writable cache evidence |
| Remote exposure | Current candidate binds loopback | Evinced non-loopback deployment path |
| Crash durability | Independent from pathname authority | Selected durability campaign |
| Miss coalescing and checksums | Independent cache semantics | Existing cache-composition follow-up |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| `linux-fieldwork@dabe79ce...` | Linux Fieldwork CI `30587406344`, 232 tests including the race matrix and optimized child | success | `target-executed` |
| `linux-fieldwork@e70674ab...` | Linux Fieldwork CI `30593222539` / 735 before cleanup-gate addition | success | `full-gate` for that prior head, excluding the new cleanup condition |
| `linux-fieldwork@d204faf3...` | cleanup regression plus Linux Fieldwork CI | pending | `target-test-prepared` |
| `fieldwork@28a5d703...` | Fieldwork integrity `30587905595` / 1173 | success | `full-gate` for the predecessor Fieldwork head |

## Current disposition

- Finding state: `repair`
- Review disposition: `HOLD`
- Canonical baseline: Linux PR #255 at `d204faf3...`
- Exact next transition: execute the new exact head and complete a four-file review.
- Clearing condition: ordinary and optimized dedicated-root inventories are empty, checkout-generated inventory is unchanged, Linux CI passes, and the current issue, PR, and finding agree.
- Following transition: land the baseline record, then create one canonical descriptor-relative implementation carrier under Linux issue #227.
- Upstream contact: unauthorized.

## Changes to the canonical conclusion

| Date | Carrier | Change |
| --- | --- | --- |
| 2026-07-31 | Linux PR #228 | Prepared deterministic parent and final-component probes, restoration, reruns, and optimized execution. |
| 2026-07-31 | Linux run `30587406344` | Promoted the pathname behavior from prepared/model evidence to exact target execution. |
| 2026-07-31 | Linux PR #255 | Restacked the exact baseline onto current main and retired PR #228. |
| 2026-07-31 | Review `4824617051` and head `d204faf3...` | Reopened the lifecycle gate and added dedicated-root ordinary/optimized inventory checks. |

## References

- `teamleaderleo/fieldwork` issue #276 and PR #278
- `teamleaderleo/linux-fieldwork` issues #188 and #227
- `teamleaderleo/linux-fieldwork` merged PR #198, closed PR #228, and draft PR #255
- `evidence/20260731-h-source-map.md`
- `evidence/20260731-h-local-generated-source-model.md`
- `evidence/20260731-current-main-cleanup-repair.md`
- Linux `openat(2)` rationale: https://man7.org/linux/man-pages/man2/openat.2.html
- Python `os` directory-descriptor APIs: https://docs.python.org/3/library/os.html
