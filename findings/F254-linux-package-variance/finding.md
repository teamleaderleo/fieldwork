# F254-linux-package-variance: stop when observed package variance follows a declared input

Finding state: `stopped`

Workstream: `H`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-linux-package-variance/finding.md`  
Investigation workspace: `investigations/254-linux-storage-archive-reproducibility/`  
Canonical implementation: none; retained corpus in `teamleaderleo/linux-fieldwork` PR #112  
Exact implementation head: `7c67db4942ff9f5863a20af42c443f456783ddf5`  
Exact base or source revision: `bcf67b818f98b6c7f6a5dac50d39f8a125485e4a`; generated native package `lf12-variance-probe` version `1.0`  
Reviewed input generation: Debian 13 retained environment and ten-build matrix  
Current review disposition: `REJECT`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

A tiny Debian package was built repeatedly while practical environmental inputs changed. The package stayed byte-for-byte identical across elapsed time, build path, locale, timezone, hostname environment, a real build-user change, file creation order, and serial versus four-job compilation.

Changing `SOURCE_DATE_EPOCH` by one day changed archive timestamps, while extracted payload bytes and package control data stayed equal. That is a declared-input change, not an unexplained defect.

The correct result is to keep the corpus and stop proposing a fix for this fixture.

## Why we care

Reproducibility work can waste time if every differing build artifact is treated as a product defect. Package bytes, extracted payload, control data, archive metadata, `.buildinfo`, and `.changes` describe different layers.

A useful probe must say which layer changed, which input changed, and whether the difference violates the intended contract. Here the package-content path normalized the tested ambient inputs; build-event metadata still recorded environment and time as expected.

## What happens if we leave it alone

There is no demonstrated package defect to leave unfixed. The risk is the opposite: promoting a speculative source or packaging change from a matrix whose only package difference follows an intentionally changed epoch.

Without the retained stop record, future workers may rerun the same ambient factors, conflate `.buildinfo` variance with `.deb` variance, or claim one controlled fixture proves universal Debian reproducibility.

## Current finding

The tested native Debian package is reproducible across the ambient factors in the retained matrix. The only `.deb` byte difference followed a changed `SOURCE_DATE_EPOCH` and was confined to archive timestamps; installed bytes and control data remained equal.

No source or packaging defect was demonstrated. The corpus remains useful as a regression fixture and as a model for separating artifact layers.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Same-environment repeated builds produced byte-identical `.deb` files. | target-executed | PR #112 report and dedicated workflow run `30543908611` / 6 | One generated native package on Debian 13. |
| Path, locale, timezone, `HOSTNAME`, real user, file order, and two-target parallelism did not change package bytes in this fixture. | target-executed | `variance-matrix.tsv`, complete-byte comparisons, extracted/control comparisons | Most variants also used distinct paths; the path-only control bounds but does not eliminate all confounding. |
| Changing the declared epoch changed archive timestamps while extracted payload and control data stayed equal. | target-executed | alternate-epoch row and `diff-summary.txt` | Does not prove every package should ignore other declared inputs. |
| `.buildinfo` and `.changes` variance is build-event metadata and must not be silently described as package-content variance. | target-executed | retained comparisons and report interpretation | Their separate reproducibility or policy requirements are outside this finding. |

## System and ownership map

- Fixture owner: `run-variance-probe.sh` generates one native source package with two independent C object targets.
- Build owner: `dpkg-buildpackage -us -uc -b` under the retained Debian 13 environment.
- Package owner: `dpkg-deb` creates the `.deb` and normalizes ownership under `Rules-Requires-Root: no` plus `--root-owner-group`.
- Evidence layers: complete `.deb` bytes, extracted payload, control tree, `ar` and data-tar metadata, `.buildinfo`, and `.changes`.
- Cleanup owner: the runner accepts only guarded roots below `/tmp` or `/var/tmp`.
- Test boundary: one architecture, compiler family, dpkg version, native package format, and the named matrix.

## Historical precedent

### Debian reproducible-build definition

- Source: https://reproducible-builds.org/docs/definition/
- Revision or date: retrieved 2026-07-31
- Principle supported: identical source, environment, and build instructions should produce bit-for-bit identical artifacts; inputs must be defined rather than assumed.
- Important difference: this finding intentionally varies selected inputs and classifies which output layer changes.

### SOURCE_DATE_EPOCH

- Source: https://reproducible-builds.org/docs/source-date-epoch/
- Revision or date: retrieved 2026-07-31
- Principle supported: build systems use a declared timestamp input to normalize embedded and archive times.
- Important difference: the matrix changes that declared input on purpose, so timestamp variance is expected rather than unexplained.

### Debian `.buildinfo`

- Source: https://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-buildinfo
- Revision or date: Debian Policy retrieved 2026-07-31
- Principle supported: `.buildinfo` records build environment and metadata used to reproduce or audit the build.
- Important difference: it is not the installed package payload and can vary when the build event varies.

## Approaches considered

### Retained approach: keep the exact corpus and stop the defect claim

The fixture, environment, commands, equality layers, and negative result are durable. This prevents duplicate work and provides a small probe for future packaging changes.

### Declined: promote a source or packaging fix

No unexplained package-content difference exists in the executed matrix. A fix would be speculative and could remove intended timestamp authority.

### Declined: compare only extracted payload

Equal installed bytes can hide archive-metadata differences. The corpus correctly compares whole package bytes, extraction, control data, and archive listings separately.

### Declined: treat `.buildinfo` or `.changes` differences as `.deb` failure

Those files describe the build event and checksums. The report preserves their differences without misclassifying the package artifact.

### Deferred: broaden to arbitrary packages and toolchains

A larger corpus may be useful, but it is a new investigation. One controlled native package cannot support ecosystem-wide frequency or universal normalization claims.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| same path and environment after elapsed time | two baseline builds | identical `.deb`; build-event metadata changed |
| different build path | path-only and other rows | identical `.deb` |
| locale and timezone | matrix rows | identical `.deb` |
| `HOSTNAME` environment | matrix row | identical `.deb` |
| build as `nobody:nogroup` | real user row | identical `.deb` |
| input file creation order | matrix row | identical `.deb` |
| `make -j4` with two independent objects | asserted parallel row | identical `.deb`; real parallel invocation observed |
| alternate `SOURCE_DATE_EPOCH` | declared-input row | different archive timestamps; equal extracted/control data |
| destructive output root | `tests/test_lf12_probe_safety.py` | roots outside `/tmp` or `/var/tmp` rejected |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| non-native source packages and generated tarballs | different source and archive pipelines | reopen with a bounded package family |
| other architectures, distributions, compilers, and dpkg versions | environment matrix not executed | new exact environment receipt |
| changed UTS hostname | only `HOSTNAME` environment was varied | reopen with namespace capability and controlled test |
| larger input-order or parallel schedules | current fixture has two staged files and two object targets | broaden only when a concrete package needs it |
| `diffoscope` or `reprotest` | current complete-byte and layer comparisons were sufficient for the stop | add when a new unexplained difference appears |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| linux-fieldwork@`7c67db4942ff9f5863a20af42c443f456783ddf5` | Linux Fieldwork CI `30543908605` / 293 | hosted Linux | success | target-executed |
| linux-fieldwork@`7c67db4942ff9f5863a20af42c443f456783ddf5` | LF-12 reproducible package variance `30543908611` / 6 | Debian 13 container, amd64 | success | target-executed |
| retained runner | `bash artifacts/run-variance-probe.sh /tmp/lf12-variance-run` | Debian 13 boundary recorded in `environment.txt` | ten-build matrix completed | target-executed |

## Complete-diff and compatibility review

- Complete changed-file fence: eight unique LF-12 files in PR #112.
- Current-base relationship at merge: base `bcf67b8...`; merge commit `c730b8ef2e90e07ad18b5835b225a8b41e22420a`.
- Temporary carrier status: stale-base PR #19 was superseded; PR #112 is the retained current-main promotion.
- Compatibility surfaces examined: package bytes, payload, control data, archive timestamps, build-event metadata, user, path, locale, timezone, hostname environment, file order, parallelism, cleanup safety.
- Known source defect remaining: none demonstrated.
- Review eligibility: the negative result and stop are exact-head and target-executed; they do not establish ecosystem-wide reproducibility.

## Current disposition and desk routing

- Finding state: `stopped`
- Review disposition: `REJECT`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: retain corpus; do not implement a fix for this fixture
- Clearing condition: new unexplained package-content variance under a pinned environment
- Required subgates: none
- Autonomous work remaining: none within current scope
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | stale-base PR #19 | original ten-build matrix and stop decision retained |
| 2026-07-30 | PR #112 head `7c67db49...` | current-main promotion passed repository CI and dedicated LF-12 execution |
| 2026-07-31 | F254 materialization | classified the result explicitly as `stopped`, not a latent implementation candidate |

## References

- https://github.com/teamleaderleo/linux-fieldwork/pull/112
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/programmes/debian-packages/lanes/LF-12-reproducible-package-variance/scouts/LF-SCOUT-DEB-02/report.md
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/programmes/debian-packages/lanes/LF-12-reproducible-package-variance/scouts/LF-SCOUT-DEB-02/artifacts/variance-matrix.tsv
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/programmes/debian-packages/lanes/LF-12-reproducible-package-variance/scouts/LF-SCOUT-DEB-02/artifacts/diff-summary.txt
- Linux Fieldwork workflows `30543908605` and `30543908611`
