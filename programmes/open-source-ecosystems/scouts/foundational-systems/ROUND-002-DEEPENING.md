# Cloud Hypervisor expansion — Round 002 deepening

Date: 2026-08-10  
Programme: [Open-Source Ecosystems](../../STATUS.md)  
Scout issue: [#211](https://github.com/teamleaderleo/fieldwork/issues/211)  
Target: `cloud-hypervisor/cloud-hypervisor`  
Target revision: `a1fcb9f790616ac615f66de73be540b0b20844b1`  
Upstream-contact authorization: `false`

This file continues `ROUND-002-cloud-hypervisor.md`. It preserves the first-pass report as a dated reconnaissance snapshot and records the stronger evidence found afterward.

## In simple words

Two small Cloud Hypervisor questions now stand out.

First, the 16 KiB sparse-test failure is almost exactly explained by the test fixture asking a 16 KiB-granularity memfd to preserve 4 KiB data/hole boundaries. A synthetic 16 KiB granularity model turns the test's requested extents into the exact `(0, 32768)` extent reported upstream. Production sparse-copy code still does not appear to require 4 KiB pages. The missing evidence is a real 16 KiB-kernel run of a page-size-aware fixture repair.

Second, the `MIGRATABLE_VERSION` override used by live-upgrade tests appears to have been lost during later test/workload consolidation. This is source-proven on current `main`: the old override was intentionally added, the live-migration folding commit explicitly preserved it, but current `dev_cli.sh` no longer forwards or mentions it and `test_assets.yaml` hard-pins the previous Cloud Hypervisor binary to v39.0. This explains why `dev_cli` can no longer select a different migration source version.

The aarch64 cache-error issue is also real source debt, but it is lower priority: the code still panics when existing sysfs cache files cannot be read or parsed, yet proving a realistic failure path requires either an aarch64 host race/fault or a small testability refactor. The old vDPA unplug crash, by contrast, looks stale enough that it should be retested before anybody writes a patch.

## Updated ranking

### 1. Sparse fixture granularity on 16 KiB kernels

Issue: [16 KiB sparse-test failure](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8582)

#### Exact model result

The upstream test requests:

```text
[(8192, 4096), (20480, 8192)]
```

The retained Fieldwork probe now has a `model16k` mode. It models a backing where any 16 KiB granule touched by a write remains allocated when later hole punches cover only part of that granule.

For the current fixture:

```text
write 8192..12288   -> touches granule 0 (0..16384)
write 20480..28672  -> touches granule 1 (16384..32768)
                       ↓
modelled sparse map -> [(0, 32768)]
```

That is exactly the actual extent list in the canonical issue report.

Run:

```sh
python3 programmes/open-source-ecosystems/scouts/foundational-systems/artifacts/cloud-hypervisor-sparse-page-granularity.py model16k
```

Expected retained model result:

```text
requested=[(8192, 4096), (20480, 8192)]
modelled=[(0, 32768)]
issue_reported=[(0, 32768)]
matches_issue=True
```

**Evidence class:** `model-executed` for the 16 KiB quantization hypothesis; `upstream-reported` for the real 16 KiB test failure. This is not a substitute for target execution on a 16 KiB kernel.

#### Why more than two tests may be weakened

Several other sparse tests use memfd sources with fixed 4096-byte coordinates but assert only byte contents afterward. On a coarse-granularity host, `SEEK_DATA` can return a larger allocated extent than the intended data range. Copying the extra bytes can go unnoticed when those extra bytes are zero and the destination assertion also expects zero.

`single_extent_at_zero_offset` is stronger because the destination is prefilled with `0xFE`. An over-wide sparse copy therefore overwrites sentinel bytes and becomes visible. `written_pages_show_as_data_extents` is also strong because it directly checks the extent map.

This means a repair should audit the **fixture quantum across the sparse test module**, not just loosen the two failing assertions.

#### Candidate boundary

The leading repair remains test-only:

```text
host page size
      ↓
fixture quantum
      ↓
page-aligned synthetic data + hole ranges
      ↓
existing production SEEK_DATA/SEEK_HOLE code unchanged
```

Do not change `next_data_extent()` or `write_region_sparse()` unless real 16 KiB execution disproves this model. Do not simply accept coalesced extents in assertions, because the tests are meant to exercise sparse copying rather than silently degrade into a dense/over-wide copy.

**Next gate:** real 16 KiB target execution before and after a fixture-only candidate, plus the normal 4 KiB regression control.

### 2. `MIGRATABLE_VERSION` lost from `dev_cli`

Issue: [cannot select upgrade source version through dev_cli](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8616)

State at retrieval:

- open;
- no assignee;
- one reporter comment asking how to choose a specific version after recent test changes;
- no matching canonical pull request found.

#### The feature existed deliberately

Commit [1ca6c159 — option to override default migratable version](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/commit/1ca6c159ef4cca6ffa94f24daa75e7971e8dbd16) added two linked pieces:

1. `dev_cli.sh` forwarded `MIGRATABLE_VERSION` into the live-migration test container;
2. the live-migration runner validated the value and used it when constructing the previous-release download URL.

The commit message explicitly says this was needed for MSHV because usable migration compatibility begins after breaking changes.

#### Test consolidation preserved the contract

Commit [c118606d — fold live migration tests into x86-64 script](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/commit/c118606d645f210d3eded192c6eb73d88c8696d6) removed the dedicated live-migration runner but deliberately added:

```sh
--env MIGRATABLE_VERSION="$MIGRATABLE_VERSION"
```

to the normal integration container and moved the version-selection logic into the combined x86-64 runner. In other words, folding the tests was intended to preserve the override.

The companion aarch64 standardization commit [5909ce85](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/commit/5909ce85edfc35ae61bd090d778bed9b718bf20f) likewise made both architectures use the same `MIGRATABLE_VERSION` mechanism.

#### Current `main` no longer carries it

At `a1fcb9f...`:

- `scripts/dev_cli.sh` contains no `MIGRATABLE_VERSION` reference;
- its common integration environment forwards build/custom-kernel/auth variables but not the migratable version;
- `scripts/run_integration_tests_x86_64.sh` no longer contains the version-selection block and instead requires `~/workloads/cloud-hypervisor-static` to already exist;
- `scripts/run_integration_tests_aarch64.sh` likewise requires `cloud-hypervisor-static-aarch64` as an existing workload;
- `scripts/test_assets.yaml` defines both previous-release binaries with URLs hard-coded to `v39.0`;
- `scripts/fetch_workloads.py` treats those YAML URLs as ordinary static assets and has no migratable-version override.

This is a coherent explanation for the issue: the source version became an asset-manifest property instead of a runtime test parameter.

Commit [4442d3b0 — download assets before entering container](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/commit/4442d3b09bbf521298132bf640d0e0871a59f65c) is relevant history because it moved workload acquisition to the host-side `fetch_workloads.py` path. The exact later edit that removed the preserved environment entry is less important than the current contract break: the knob has no consumer now.

#### Why the repair is not quite "add one env line"

Simply forwarding `MIGRATABLE_VERSION` again would not fix current behavior because the versioned release binary is fetched **before** the container starts and its URL is fixed in `test_assets.yaml`.

A repair must decide where dynamic version selection belongs under the newer no-network-in-container architecture. Plausible boundaries include:

1. teach `fetch_workloads.py` to substitute a requested migration version for the previous-release asset while retaining v39.0 as the default;
2. give the previous-release binary a dedicated dynamic fetch path outside the static manifest;
3. make `dev_cli.sh` select/fetch that one asset before normal manifest verification.

There is an integrity tradeoff: the static manifest has a known SHA-1 for v39.0, while an arbitrary release version cannot reuse that checksum. A candidate should make that loss of fixed-manifest verification explicit rather than quietly disabling verification for unrelated assets.

**Evidence class:** `source-read` with historical contract evidence. No MSHV hardware is required to prove that current `dev_cli` cannot carry the requested version through its current source path; hardware is required to prove the chosen alternate release actually migrates successfully.

**Next gate:** build a no-network argument/asset-selection regression around `fetch_workloads.py` or `dev_cli.sh`, then exercise one non-v39 version on an MSHV runner before promotion.

### 3. aarch64 cache topology should return errors instead of panic

Issue: [propagate cache-discovery runtime errors](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8097)

Current `arch/src/aarch64/cache.rs` still contains multiple runtime panic points:

```rust
fs::read_to_string(...).expect(...)
src[..].parse().unwrap()
src.trim().parse::<u32>().unwrap()
```

`read_cache_topology()` returns `None` when the top-level cache directory is absent, but once the directory exists, read or format failures inside its files can panic the VMM instead of returning a typed error. `CpuManager` consumes `read_cache_topology()` while building aarch64 cache/PPTT information.

This is therefore more than style-only cleanup: a host-side discovery failure can escape the normal VMM error chain. Still, sysfs cache files are kernel-generated and normally stable, so the practical trigger is less immediate than #8582 or #8616.

No active canonical PR was found for #8097 in this pass.

**Likely evidence path:** separate file reading/parsing from the hard-coded sysfs root enough to run malformed/missing-value unit fixtures; then propagate a typed `arch`/CPU error rather than panicking. Do not make a broad error-handling sweep under the umbrella of this issue.

**Disposition:** retain as a bounded aarch64 follow-up; lower priority than the first two candidates.

## Retest / stop findings

### vDPA hot-unplug crash: current-main retest before patching

Issue: [vDPA hot-unplug process crash](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/7785)

The report is consequential: v51.1 panicked during `vm.remove-device`, poisoned a mutex, and killed the VMM. No canonical PR references the issue directly.

However, current source no longer matches the reported failure boundary. At `a1fcb9f...`:

- `DeviceManager::remove_device()` validates removal before changing configuration;
- `VmConfig::remove_device()` explicitly has a `// Remove if vDPA device` branch and removes matching vDPA entries;
- device ejection uses typed `DeviceManagerError` paths around missing device/tree state rather than the reported exact line-number `unwrap()`.

That does **not** prove current vDPA unplug is correct: actual vDPA hardware and DMA teardown matter. It does mean an implementation based on the v51.1 panic trace would be stale.

**Disposition:** retest current `main` on real vDPA hardware first. If it no longer crashes, retain a negative/stale result; if it still fails, capture the new stack and ownership boundary before designing a fix.

### SMBIOS secret-path feature: do not duplicate prior contributor work

Issue: [load SMBIOS OEM strings from paths to avoid command-line secret exposure](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/6951)

This remains a meaningful security/operational feature and Bradford previously said the direction sounded good. The reporter later implemented [PR 7198](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/pull/7198). That PR was closed, not because the feature was rejected, but because a newly added test was failing and the author had stopped responding; Bradford later explicitly said there was still interest in moving it forward.

This is existing contributor work with substantial design/review history. It should be revived/rebased by that contributor or handled only after a deliberate ownership decision, not treated as a fresh empty issue.

**Disposition:** park; do not race the historical implementation.

### QCOW multiqueue corruption: retest after merged repair

Issue: [QCOW multiqueue corruption with backing files](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/8621)

The issue remains open, but [PR 8624](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/pull/8624) is already merged and addresses a stale punch-hole / cluster-reuse race capable of erasing newly allocated QCOW metadata. That is high-consequence work, but the next useful action is to rerun the reporter's heavy workload against current `main`, not invent a second fix from the still-open issue state.

**Disposition:** current-main retest candidate, not an implementation candidate yet.

### IOAPIC EOI race: stop

Issue: [potential missing INTx interrupt during EOI](https://redirect.github.com/cloud-hypervisor/cloud-hypervisor/issues/5260)

Recent maintainer discussion leans toward the relevant legacy INTx/VFIO support no longer being a supported direction. Bradford says they think support was dropped and Sebastien Boeuf says they are okay discarding it, pending one final maintainer check.

**Disposition:** do not resurrect this old race as new Fieldwork work.

## Current branch order

The best next engineering probes are now:

1. **#8582 — 16 KiB sparse fixture:** implement a test-only host-page-size fixture candidate in the owned fork; prove on 4 KiB and obtain a real 16 KiB run.
2. **#8616 — migratable-version override:** create a no-network regression around version-to-asset selection and design the smallest host-side dynamic-fetch boundary that preserves the newer workload architecture.
3. **#8097 — aarch64 cache errors:** map the narrow parser/read error type and testability boundary before implementation.
4. **#8666 — ACPI propagation:** clean and restack the already-existing separate research lane rather than adding more machinery.

Retest rather than patch #7785 and #8621. Park #6951 behind existing contributor history. Stop #8707, #8492, #8690, #8693, and #5260 because they are assigned, actively fixed, historically occupied, or no longer a desired direction.

Automated upstream contact remained prohibited and no third-party repository state was changed during this deepening pass.
