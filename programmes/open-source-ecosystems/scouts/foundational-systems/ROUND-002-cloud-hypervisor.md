# Cloud Hypervisor expansion — Round 002

Date: 2026-08-10  
Programme: [Open-Source Ecosystems](../../STATUS.md)  
Scout issue: [#211](https://github.com/teamleaderleo/fieldwork/issues/211)  
Target: `cloud-hypervisor/cloud-hypervisor`  
Target revision: `a1fcb9f790616ac615f66de73be540b0b20844b1`  
Retrieval boundary: 2026-08-10  
Upstream-contact authorization: `false`

## In simple words

Cloud Hypervisor still has useful systems work after the API-shutdown contribution, but several tempting issues are already owned or have active fixes. The strongest unclaimed small candidate in this pass is the 16 KiB-page sparse-test failure: current production sparse-copy code works in byte ranges, while its memfd test fixtures still demand 4 KiB sparse extents. On a host whose memory pages are 16 KiB, the filesystem can report data and holes at a coarser granularity, so the test can fail without showing a defect in the production copy loop.

The next useful move is therefore not to patch production code immediately. First make the sparse fixture page-size aware in the owned fork, then execute the exact unit tests on both a normal 4 KiB host and a real 16 KiB-page kernel. If that makes the failures disappear without touching production code, the portability bug is bounded and reviewable.

The existing ACPI error-propagation lane remains worth repairing separately, but its internal carrier is still too noisy to promote. Several other current issues should be left alone because a maintainer has handed them to somebody, an upstream PR already exists, or the reporter has explicitly offered to implement the change.

## Current target boundary

This round pins canonical Cloud Hypervisor at commit `a1fcb9f790616ac615f66de73be540b0b20844b1`.

Relevant surfaces found in this pass:

| Surface | Role in this round |
| --- | --- |
| `vmm/src/sparse.rs` | Sparse `SEEK_DATA` / `SEEK_HOLE` enumeration, sparse copy, and the 4 KiB-shaped unit fixtures implicated by the 16 KiB-page failure. |
| `vmm/src/api/http/mod.rs` + `vmm/src/lib.rs` | API error/status behavior behind the open 404/405 lifecycle questions; direction is not settled. |
| `vmm/src/acpi.rs` and ACPI child builders | Existing owned-fork investigation for fallible ACPI construction. |
| block-format tests + integration tests | Test-placement cleanup, but a maintainer has already asked another contributor to own it. |
| live-migration timeout test | Already has an active upstream implementation for the missing receive-side assertion. |
| VMDK backend | Reported readonly bug already has an active upstream fix. |

## Ranked candidates

### 1. Retain and promote: sparse tests on 16 KiB-page kernels

Issue: [16 KiB sparse-test failure](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8582)

State at retrieval:

- open;
- no assignee;
- no comments;
- no matching canonical pull request found;
- report includes target-native failures on a 16 KiB-page kernel.

The two reported failures are:

- `sparse::unit_tests::written_pages_show_as_data_extents`;
- `sparse::unit_tests::single_extent_at_zero_offset`.

The clearest failure is the extent mismatch:

```text
actual:   [(0, 32768)]
expected: [(8192, 4096), (20480, 8192)]
```

That expected layout is inherently 4 KiB-shaped: one requested extent starts at 8 KiB and is only 4 KiB long, and another starts at 20 KiB. Those are valid sparse units on the ordinary 4 KiB host used by most current CI, but they are not page-aligned regions on a 16 KiB-page host.

#### Source read

At the pinned revision, the production helpers in `vmm/src/sparse.rs` are not written around a 4096-byte constant. `next_data_extent()` accepts arbitrary `u64` byte offsets and lengths, and `write_region_sparse()` copies whatever extents `SEEK_DATA` / `SEEK_HOLE` returns, using a 1 MiB transfer buffer.

The fixed 4096 values are concentrated in the unit fixtures. `sparse_layout()` writes requested data ranges and explicitly punches every gap, then tests such as `written_pages_show_as_data_extents()` request:

```rust
[(4096 * 2, 4096), (4096 * 5, 4096 * 2)]
```

and assert that `SEEK_DATA` / `SEEK_HOLE` returns those byte ranges exactly.

This weakens the hypothesis that production sparse copying itself assumes 4 KiB pages and strengthens the narrower hypothesis that the test fixture assumes 4 KiB sparse extent granularity.

#### Relevant history

The fixture has already needed one portability repair. Commit `68ae56eb74b1a7e7c5fa6938b3e06712f941ee41` changed the tests to build sparse files with explicit `FALLOC_FL_PUNCH_HOLE` calls after modern shmem/tmpfs large-folio allocation made "unwritten pages stay holes" unreliable.

Historical commit: [PUNCH_HOLE fixture hardening](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/commit/68ae56eb74b1a7e7c5fa6938b3e06712f941ee41)

That repair correctly separated the test from transparent-huge-page / folio allocation policy, but it still asks the filesystem for 4 KiB sub-page data and hole boundaries. The 16 KiB report therefore looks like a second, distinct portability boundary rather than a regression to the old large-folio problem.

#### Competing hypotheses

**H1 — production sparse-copy code has a 4 KiB assumption.**  
Current source read weakens this: the production functions operate on byte ranges returned by the filesystem and do not contain the test's fixed 4096 quantum.

**H2 — memfd sparse fixtures assume a 4 KiB host page.**  
Current source and the reported extent mismatch support this. The expected 4 KiB/8 KiB ranges are not page-aligned on a 16 KiB host.

**H3 — explicit `PUNCH_HOLE` should make arbitrary byte-granularity extents portable.**  
The reported 16 KiB result contradicts this as a general test assumption. Hole punching controls allocation, but the observable sparse extent granularity still belongs to the backing filesystem/kernel.

#### Retained mechanism probe

Probe:

`artifacts/cloud-hypervisor-sparse-page-granularity.py`

It mirrors the fixture shape without importing Cloud Hypervisor: create a memfd, write selected extents, punch every gap, and enumerate the result with `SEEK_DATA` / `SEEK_HOLE`. It has two modes:

```sh
python3 artifacts/cloud-hypervisor-sparse-page-granularity.py fixed4k
python3 artifacts/cloud-hypervisor-sparse-page-granularity.py host
```

Fieldwork execution environment:

```text
Python 3.13.5
Linux 6.18.35 x86_64
host page size: 4096
```

Observed result on this 4 KiB host:

```text
host_page_size=4096
mode=fixed4k quantum=4096
requested=[(8192, 4096), (20480, 8192)]
actual=[(8192, 4096), (20480, 8192)]
match=True
```

The `host` mode is identical on this machine because the host page size is also 4096. This probe therefore validates the existing test premise on a normal 4 KiB host, but **does not reproduce the 16 KiB failure**. A real 16 KiB-page execution remains the decisive gate.

#### Likely repair boundary

The smallest candidate is test-only:

1. derive a fixture quantum from the runtime host page size for memfd-backed sparse-layout tests;
2. express offsets, data extents, destination sentinel ranges, and expected sparse extents in that quantum rather than fixed 4096-byte units;
3. keep production `next_data_extent()` and `write_region_sparse()` unchanged unless target execution disproves the fixture-only diagnosis;
4. avoid mechanically replacing every `4096` in every filesystem-backed test until the desired granularity of each backing filesystem is checked.

The important invariant is not "one sparse extent equals 4 KiB." It is:

```text
requested page-aligned source data extents
        ↓
SEEK_DATA / SEEK_HOLE enumeration
        ↓
sparse copy writes exactly those data extents
        ↓
bytes outside them remain untouched / holes as the test requires
```

#### Promotion gate

Before preparing any human-facing upstream packet:

- run the existing sparse unit tests unchanged on a 4 KiB host;
- demonstrate the current failure on a real 16 KiB-page host;
- apply only the fixture-quantum change;
- rerun on 4 KiB and 16 KiB hosts;
- inspect the complete diff for accidental changes to production sparse-copy semantics;
- if practical, include a 64 KiB-page architecture as an additional negative/compatibility control rather than assuming 16 KiB is the largest relevant boundary.

Current disposition: **promote to a bounded owned-fork / Linux Fieldwork investigation, target execution required.**

### 2. Retain separately: ACPI error propagation

Issue: [fallible ACPI construction](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8666)

This is not a new discovery. The owned fork already has draft internal PR `teamleaderleo/cloud-hypervisor#3`, head `56228e384dea822cae80632037d5b03da09af774`, exploring propagation of ACPI construction failures.

The lane remains technically interesting, but the current carrier has ten commits, four changed files, and substantial diagnostic/workflow material. It should be treated as research evidence, not a clean candidate. The next action there is to re-read current canonical source, isolate the source-only change, and rerun the focused compile/overflow gates with ordinary CI that tests a stable candidate rather than manufacturing one.

Current disposition: **repair/rebase existing lane later; do not mix it with the sparse-page candidate.**

### 3. Park: API lifecycle HTTP status semantics

Issues:

- [no-VM lifecycle endpoints returning 500 rather than documented 404](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8678)
- [OpenAPI documents unreachable 405 lifecycle responses](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8680)

Both reports are concrete, but they expose a semantic choice rather than a mechanical fix. The second report correctly notes that HTTP 405 means the HTTP method itself is unsupported and normally carries `Allow`; a VM lifecycle-state conflict may be better represented by 409 or by a documented project-specific choice. The reporter explicitly offers to send a PR after the preferred direction is settled.

Current disposition: **park pending maintainer direction / reporter ownership.** Do not preempt the design choice.

### 4. Park: hugepage-size-sensitive integration fixtures

Issue: [1 GiB default hugepage-size integration failures](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8620)

The report is specific and likely test-fixture work: several tests use `hugepages=on` without an explicit hugepage size, so a 512 MiB guest becomes invalid on a host whose default hugepage size is 1 GiB. No canonical PR was found in this pass, but the reporter explicitly says they are happy to prepare the patch.

Current disposition: **soft-owned; watch rather than compete.**

## Explicit overlap stops

These looked attractive from issue search but should not become Fieldwork implementation lanes now.

### Disk-backend test migration

Issue: [move disk backend coverage into block unit tests](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8707)

Robert Bradford proposed starting by removing integration tests already duplicated in block tests and then filling block-test gaps. In the issue thread he explicitly asks `@weltling` whether they can handle it.

Disposition: **occupied; stop duplicate work.**

### Receive-migration timeout error assertion

Issue: [verify receive-migration error on timeout cancel](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8492)

Active implementation: [PR 8703](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/pull/8703)

The pull request already adds the missing receive-side exit-status assertion, and Bradford has asked the issue author to review it.

Disposition: **active upstream implementation; stop duplicate work.**

### VMDK readonly propagation

Issue: [VMDK ignores caller readonly for extents](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8690)

Active implementation: [PR 8691](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/pull/8691)

Disposition: **active upstream implementation; stop duplicate work.**

## Environment and evidence map

| Candidate | Evidence now | Decisive next gate | Special environment |
| --- | --- | --- | --- |
| 16 KiB sparse tests | upstream-reported target failure + exact-source read + 4 KiB mechanism probe | current test FAIL and fixture-only candidate PASS on a real 16 KiB-page kernel | 16 KiB page kernel; likely aarch64 |
| ACPI error propagation | existing owned-fork source/compile investigation | clean restack on current canonical source plus focused target compile/test matrix | no special hardware for most compile gates; architecture feature matrix |
| API 404/405 semantics | reproducible report + source-oriented issue analysis | maintainer decision on API status semantics before implementation | none |
| 1 GiB default hugepage fixtures | detailed upstream report | reproduce on 1 GiB-default hugepage host and test explicit-size repair | hugepage configuration / privileged host |
| disk-backend test migration | maintainer-defined direction | owned by another contributor | qemu-img / block test environment |
| migration timeout assertion | active canonical PR | upstream review | migration test environment |
| VMDK readonly | active canonical PR | upstream review | VMDK/qemu-img |

Evidence labels used in this report:

- **Observed (Fieldwork):** the retained 4 KiB memfd mechanism probe reproduces the exact current expected sparse extents on this runner.
- **Documented / source-read:** current `vmm/src/sparse.rs` production helpers are byte-range based while unit fixtures use fixed 4096-byte units.
- **Upstream-reported:** the 16 KiB kernel failures and their exact outputs come from the canonical issue report, not a Fieldwork 16 KiB execution.
- **Inferred:** making the memfd fixture quantum host-page-size aligned is the leading repair direction; it is not yet target-executed on 16 KiB.

## Recommendation

Promote the 16 KiB sparse-fixture question as the next bounded Cloud Hypervisor investigation. It has a small likely ownership boundary, no visible competing implementation, a concrete portability failure, and a clean falsification path: if a page-size-aware fixture still fails on 16 KiB, the production-code hypothesis comes back into play.

Keep the ACPI lane separate and clean it up only after re-reading current source. Park the API and hugepage issues because their reporters have signaled implementation intent or design ownership. Stop the three obvious duplicate lanes with active/assigned work.

Cloud Hypervisor now has enough recurring Fieldwork history that a stable target hub may be justified later, but this round does not need to modify shared target registries to make the next technical decision.

Automated upstream contact remained prohibited and no third-party repository state was changed during this round.
