# Systems and command-line tools — Round 003

Snapshot: 2026-08-01  
Programme: [`open-source-ecosystems`](../../README.md) / issue [`#207`](https://github.com/teamleaderleo/fieldwork/issues/207)  
Scout lane: [`#210`](https://github.com/teamleaderleo/fieldwork/issues/210)  
Fieldwork base: `main` at `041d29ab9c5e5859cb69518a432354be71b67af8`  
Public upstream contact: **none; unauthorized**

## In simple words

This round moved away from the concentrated mmdebstrap work and inspected current curl, fish, strace, jq, libfuse, zstd, bubblewrap, rsync, libarchive, and util-linux issue and source state.

The strongest unclaimed local experiments are:

1. **curl #21610** — prove and bound destination and symlink-target truncation caused by opening the final cache path before the temporary-file transaction begins.
2. **fish #12892** — make array-slice contents expand as an ordinary argument list before parsing integers and ranges.
3. **strace #313** — characterize the two valid `RTM_GETNEIGH` payload layouts and the discriminator that selects `ifinfomsg` versus `ndmsg`.

Several initially attractive issues are explicit stops: strace #319 is already fixed on current master despite remaining open; libfuse #836 is already corrected in current source; jq #3128 has prior and current contributor ownership; jq #3538 has two open implementations; and libarchive #3314 is already owned by Linux Fieldwork issue #409.

## Scope and exact source revisions

| Target | Inspected revision | Main owning areas | Native test areas |
| --- | --- | --- | --- |
| curl | [`527573490eb2564b3d7c9dd51d8bff963b5d6303`](https://github.com/curl/curl/commit/527573490eb2564b3d7c9dd51d8bff963b5d6303) | `lib/curl_fopen.c`; HSTS, Alt-Svc, and cookie persistence callers | `tests/libtest/`, protocol persistence tests, direct unit coverage where available |
| fish | [`9654f5e4bd00066e8d0db7fdb66e7b12458f8f4e`](https://github.com/fish-shell/fish-shell/commit/9654f5e4bd00066e8d0db7fdb66e7b12458f8f4e) | `src/expand.rs`, slice parsing and ordinary variable expansion | `tests/checks/expansion.fish`, `tests/checks/zero_based_array.fish` |
| strace | [`c605d6b45b0e59b0a29120c4de39d27f7c841014`](https://github.com/strace/strace/commit/c605d6b45b0e59b0a29120c4de39d27f7c841014) | `src/rtnl_neigh.c`, route decoder dispatch | netlink route decoder fixtures and generated expected-output tests |
| jq | [`603db3f57741d217ba651e61086b550a72148b83`](https://github.com/jqlang/jq/commit/603db3f57741d217ba651e61086b550a72148b83) | compiler path/destructuring and `delpaths` internals | `tests/jq.test`, parser and bytecode tests |
| libfuse | [`9d63190c9c56a24e1095144e8ffaf66124fa0550`](https://github.com/libfuse/libfuse/commit/9d63190c9c56a24e1095144e8ffaf66124fa0550) | low-level examples and callback contracts | example integration and syscall tests |
| zstd | [`5c7b7bad26808e6b40ac3b3d0075466e27738a9d`](https://github.com/facebook/zstd/commit/5c7b7bad26808e6b40ac3b3d0075466e27738a9d) | CLI tracing and recursive file traversal | CLI shell tests and unit tests |

A dated scan does not reserve an issue. Assignment, linked commits, pull requests, contributor-intent comments, and project-specific claim mechanisms must be refreshed immediately before implementation begins.

## Ranked candidate queue

| Rank | Target | Candidate | Consequence | Ownership / overlap at snapshot | Next distinguishing probe | Disposition |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | curl | [`#21610`](https://github.com/curl/curl/issues/21610) — final path opened and truncated before temp-file transaction | an HSTS, Alt-Svc, or cookie cache can lose its previous contents when a later write/rename step fails; a symlink target can be truncated before the symlink path is replaced | open, unassigned; four comments; maintainer favors reverting `0c667188e0`; no matching PR or later fix commit found; defect remains in current `lib/curl_fopen.c` | direct `Curl_fopen`/persistence matrix over existing regular file, symlink-to-regular, new path, special file, successful replace, and failure after transaction setup | **promote experiment** |
| 2 | fish | [`#12892`](https://github.com/fish-shell/fish-shell/issues/12892) — cartesian variable expansion inside array indices | `$foo[$bar1$bar2]` selects the wrong elements because raw slice parsing consumes component indices instead of the ordinary concatenated argument strings | open, unassigned; maintainer agreement on expected semantics; no matching PR found | focused expansion tests comparing direct slice expression with an intermediate variable, then ranges, literals, quoting, empty lists, and invalid values | **promote experiment** |
| 3 | strace | [`#313`](https://github.com/strace/strace/issues/313) — `RTM_GETNEIGH` payload layout selection | valid netlink requests can be decoded using the wrong structure, producing misleading field names and values | open, unassigned; one comment explains that `ndmsg` is correct only for some requests; no implementation overlap found | synthetic request matrix that varies family, flags, payload length, and bridge-neighbor operation without requiring a real bridge | **issue-first experiment** |
| 4 | curl | [`#22327`](https://github.com/curl/curl/issues/22327) — HTTPS multi-socket integration stops requesting response reads | an event-loop integration can hang after a successful TLS handshake and transmitted HTTP/2 request | new report with detailed logs, but likely sensitive to Boost.Asio integration ownership and callback lifecycle | reduce to curl's `multi_socket` examples with a local TLS server; compare HTTP/1.1, HTTP/2, socket callback transitions, and timer actions | **reduce before promotion** |
| 5 | fish | [`#12819`](https://github.com/fish-shell/fish-shell/issues/12819) — expanded `]` terminates a variable slice | data produced by expansion changes parser structure, yielding surprising selections instead of a clear invalid-index or unmatched-bracket error | open, unassigned; semantics need careful compatibility review | matrix separating lexical delimiters from post-parse expansion values in quoted and unquoted slices | **issue-first parser probe** |
| 6 | zstd | [`#4368`](https://github.com/facebook/zstd/issues/4368) — zero trace duration used as divisor | trace output can report an infinite or otherwise non-useful speed for a zero-duration operation | open report; low operational consequence; source and output behavior still need current-head confirmation | force or model zero duration, capture emitted trace format, and determine whether the result is a defined floating-point infinity or a real trap on supported builds | **small diagnostic probe** |
| 7 | rsync | [`#282`](https://github.com/RsyncProject/rsync/issues/282) — I/O timeout does not stop a remotely blocked read | backup chains can remain blocked when the remote process is stuck in kernel I/O | old report, environment-heavy, remote/kernel failure required | local two-process protocol fixture with a deliberately non-progressing peer; distinguish transport silence from a child blocked before protocol participation | **retain / expensive reduction** |
| 8 | bubblewrap | [`#134`](https://github.com/containers/bubblewrap/issues/134) — `/proc/xen` interaction in Qubes | sandbox startup can fail in a Qubes-specific proc topology | old Qubes/Jessie report and high environment cost | refresh on current Qubes and current bubblewrap before any source work | **capability queue** |

## Explicit stops and retained references

| Target | Candidate | Existing ownership or landed state | Retained value |
| --- | --- | --- | --- |
| strace | [`#319`](https://github.com/strace/strace/issues/319) — unknown syscalls absent from `-c` summary | current master already contains commit [`be4ac3ff`](https://github.com/strace/strace/commit/be4ac3ff65b8f3c291eddaf3836cdf99807b6e44) and test commit [`9beb5f46`](https://github.com/strace/strace/commit/9beb5f461dc26ee43a23dc60bff10b91db595b54); issue remains open | strong stale-issue overlap check: inspect current source and commit history before claiming apparently unassigned work |
| libfuse | [`#836`](https://github.com/libfuse/libfuse/issues/836) — `hello_ll` xattr assertion on root directory | current `example/hello_ll.c` accepts inode 1 or 2; the reported `ino == 2` crash condition is gone | example callback contract: directory xattr callbacks are ordinary and should return a protocol error or value rather than assert |
| jq | [`#3128`](https://github.com/jqlang/jq/issues/3128) — destructuring inside `path()` | PR #3384 was closed after deeper complexity emerged; another contributor has explicitly offered to take the issue and open a PR | useful compiler regression and warning that the initial `SUBEXP_BEGIN`/`SUBEXP_END` sketch is incomplete |
| jq | [`#3538`](https://github.com/jqlang/jq/issues/3538) — mixed-sign non-leaf indices in `delpaths` | open PRs #3543 and #3548 plus active design discussion; one comparative test shows normalization must preserve grouping order | excellent third-key regression showing why normalize-without-resort is incomplete |
| libarchive | [`#3314`](https://github.com/libarchive/libarchive/issues/3314) — cpio inode behavior | already owned by Linux Fieldwork issue [`#409`](https://github.com/teamleaderleo/linux-fieldwork/issues/409) with a controlled probe lane | cross-platform inode-model and test-capability pattern; do not duplicate |

## Probe 1 — curl atomic persistence without pre-truncation

### Question

Can curl preserve the previous destination contents and any symlink target until the temporary output has been successfully written and renamed, while retaining the intended behavior for new paths and non-regular destinations?

### Why this is distinguishing

Current `Curl_fopen()` calls `curlx_fopen(filename, "w")` before `fstat`, random temp-name generation, temp-file creation, writing, flush, or rename. For a regular file, this destroys the old contents before the atomic transaction starts. For a symlink to a regular file, it follows and truncates the target, then later replaces the symlink path.

Commit `0c667188e0c6cda615a036b8a2b4125f2c404dde` changed exactly this decision. Before it, curl used `stat(filename)` first:

- an existing regular file entered the temp-file path without opening the destination;
- a missing or non-regular path used direct `fopen()`;
- a symlink to a regular file was classified through its target, so the later rename replaced the symlink path while leaving the target contents intact.

The issue description proposes `lstat()` plus rejection of non-regular paths, while the maintainer discussion favors reverting the old `stat()` contract. Those are observably different policies. The first experiment must test the policy boundary rather than treating them as equivalent fixes.

### Local fixture matrix

Use a disposable directory and invoke the smallest available direct harness around `Curl_fopen()`; add a CLI persistence control only after the helper-level behavior is proven.

1. **Existing regular file, successful commit**
   - seed content and non-default mode;
   - open through `Curl_fopen`, write replacement, close, rename;
   - assert replacement bytes, inherited mode policy, and no leftover temp file.
2. **Existing regular file, transaction failure**
   - force temp creation, write, flush, or rename failure through an existing test fault hook if available;
   - otherwise run a dedicated unprivileged fixture with an unwritable directory and record the capability precondition;
   - assert original bytes and mode remain unchanged.
3. **Symlink to regular file**
   - seed target sentinel bytes and point destination symlink at it;
   - assert the target is never modified;
   - separately record whether the final destination becomes a regular file, matching the pre-`0c667188e0` behavior, or whether symlinks are rejected under a newly chosen policy.
4. **New path**
   - assert successful creation and document whether it uses direct or temporary output.
5. **Non-regular destination**
   - use a safe sink such as `/dev/null` or a controlled special-file fixture;
   - preserve direct-open compatibility unless maintainers explicitly choose rejection.
6. **Caller coverage**
   - run HSTS, Alt-Svc, and cookie persistence paths against the same preservation controls.

Do not rely solely on `chmod 0555`: a root CI worker can still write. A passing failure-path test must prove its fault was actually reached.

### Candidate implementation boundary

The smallest compatibility candidate is a semantic revert of the open-first block:

1. inspect with `stat()` before opening;
2. use direct `fopen()` for missing or non-regular destinations;
3. use the existing exclusive temp-file transaction for an existing regular destination;
4. preserve the current ownership/mode-inheritance guard;
5. leave broad symlink rejection or `O_NOFOLLOW` policy for a separately justified change unless the tests and maintainers select it.

If a security-hardening policy is selected instead, document the behavior change for symlinks and special files explicitly. Do not smuggle it into a regression repair.

### Promotion rule

Promote a candidate branch only after:

- current head reproduces target truncation;
- a deterministic failure-path control proves old destination preservation;
- symlink target preservation is tested independently of final-path policy;
- new and non-regular destination behavior is recorded;
- HSTS, Alt-Svc, and cookie callers remain compatible;
- no active upstream PR or contributor claim appears on refresh.

## Probe 2 — fish ordinary expansion inside array slices

### Question

Should the characters between `[` and `]` undergo the same ordinary argument expansion as command arguments, producing complete strings before those strings are parsed as indices and ranges?

Maintainer discussion says yes. For:

```fish
set foo a b c d e f g h i j k l m n o p q r s t u v w x y z
set bar1 1 2
set bar2 3 4
echo $foo[$bar1$bar2]
```

ordinary cartesian expansion produces `13 23 14 24`, so the selected values should be `m w n x`.

### Current mechanism

`src/expand.rs` detects a following slice and immediately calls `parse_slice()` on the slice text before the normal variable cartesian-product loop runs. This lets the slice parser consume the component values as separate indices rather than the combined argument strings.

The correction needs an explicit two-stage contract:

1. expand the slice expression into a list of complete strings using ordinary argument-expansion semantics;
2. parse each resulting string as one index or range against the final variable length.

### Focused matrix

- reported `$bar1$bar2` case versus `set cardinal $bar1$bar2; $foo[$cardinal]`;
- one variable plus literal suffix and prefix;
- ranges created by expansion;
- quoted and unquoted slice expressions;
- empty variable components;
- multiple resulting arguments;
- zero, negative, out-of-range, and malformed values;
- no-slice and literal-slice controls;
- expansion-limit behavior for large cartesian products;
- completion-time expansion, especially any reusable path shared with `complete -a`.

### Promotion rule

Promote after current-head reproduction, exact parity with the intermediate-variable control, and a focused test showing existing literal, range, negative-index, invalid-index, and completion behavior remains stable.

## Probe 3 — strace `RTM_GETNEIGH` payload discriminator

### Question

Which observable request property determines whether an `RTM_GETNEIGH` payload is an `ifinfomsg` bridge-family request or an `ndmsg` neighbor request?

Current source dispatches solely on `family == AF_BRIDGE`: bridge uses `decode_ifinfomsg`, every other family uses `decode_ndmsg`. The issue report and its only comment indicate that both layouts are valid in different situations and cite Linux commit `bd961c9bc66497f0c63f4ba1d02900bb85078366`.

### Synthetic matrix

Construct raw route-netlink requests in the existing decoder test style and vary:

- `nlmsg_type = RTM_GETNEIGH`;
- `AF_BRIDGE`, `AF_INET`, and `AF_INET6` family;
- dump/request flags;
- payload sizes matching `ifinfomsg`, `ndmsg`, and truncated prefixes;
- bridge FDB-specific attributes versus neighbor attributes;
- kernel-era behavior implied by the cited commit.

A valid discriminator should be derived from the kernel UAPI and request construction, not guessed from payload bytes after the fact. If the UAPI remains intentionally ambiguous, the useful output may be a documented best-effort decoder or a request-shape heuristic proposed upstream for judgment.

### Promotion rule

Do not patch until the synthetic fixtures establish at least one current misdecode and one control for each valid layout. A real bridge/Qubes/network namespace is not required for the first probe.

## Work order

1. Refresh curl #21610 ownership and current head.
2. Build the direct preservation matrix and establish a deterministic post-open failure.
3. If curl reproduces cleanly, promote a dedicated internal experiment branch and packet.
4. In parallel only after the curl fixture is bounded, add fish #12892 current-head characterization.
5. Keep strace #313 issue-first until the kernel request-layout contract is sourced and executable.
6. Re-run overlap checks immediately before any implementation branch or external proposal.

## Authority and contact boundary

This round authorizes public-source reading and internal Fieldwork branches, tests, notes, issues, and draft pull requests. It does not authorize comments, reactions, issue claims, pull requests, emails, patches, or any other contact with curl, fish, strace, jq, libfuse, zstd, rsync, bubblewrap, libarchive, or their maintainers.
