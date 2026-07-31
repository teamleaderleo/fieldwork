# Workstream H — Linux storage, archive, reproducibility, and integration

Workspace phase: `handoff`  
Materialization status: `provisional PR #283-based adoption`  
Parent initiative: #254  
Protocol base: PR #283 at `23ef5d6e1d955eb7a8984a0491dc99a5e08a1d81`  
Repair input head: PR #308 at `37b8fe6e81f4dba140014fd53e95f1b4546f9ab9`; Fieldwork integrity `30628624377` / 1404 success  
Linux Fieldwork source boundary observed: `main` at `63e7bbff2d2dc6da4078f9f72d02cd4330b1a09a`  
Linux durable-record repair: PR #249 head `fed2b03cb3a584f0e3f2f2db5c58e6a2f0102023`, CI run 720 success, merged as `d7aebcf38459fd3f4791c1ce5da1ec446d6d3296`  
Upstream contact authorized: no

## In simple words

This workspace retains five practical lessons from Linux Fieldwork:

1. a cache proxy must validate authority, framing, filesystem paths, and publication in one composed source state;
2. a destructive test harness must not derive recursive-delete authority from Python's temporary-directory fallback or unresolved symlinks;
3. a GNU-tar-compatible transform layer must translate regex dialects deliberately and test the accepted neighbors of every rejection guard;
4. a reproducibility probe can correctly end with no fix when all observed package variance follows a declared input;
5. an active equivalent public repair is a reason to stop duplicate implementation while retaining the technical lesson and an exact reopening trigger.

The consequential Linux repairs and closeout-record corrections are merged locally. This eight-file Fieldwork packet is durable technical evidence, but it remains a provisional adoption of the still-unaccepted PR #283 protocol. It must not become canonical merely because its own integrity run is green. The next protocol transition is reconciliation onto an independently accepted stable finding/workspace generation, followed by a fresh complete-diff review.

`closed` and `stopped` apply only to the bounded findings below. They do not declare the surrounding subjects dead. [`research-avenues.md`](research-avenues.md) preserves adjacent questions, smallest safe probes, blockers, and reopening triggers so interruption, missing capability, or an authority boundary cannot erase the research map.

## Why this matters

These are boundary failures that can corrupt cached bytes, delete the wrong tree, silently rename archive members, misclassify expected variance as a defect, or duplicate active work. The useful result is knowing which invariant owns each failure and leaving enough exact evidence that the next worker does not repeat the investigation.

## How to read the states

- `closed` means the exact bounded repair or evidence unit completed its local transition. It does not close adjacent research avenues.
- `stopped` means the current defect premise or implementation should not continue now. The evidence and reopening trigger remain retained.
- A skipped job, unavailable environment, policy restriction, safety boundary, or prohibited public interaction is not a technical negative result. It must be recorded as a blocker or evidence limit.

## Provisional finding index

| Finding | State | Linux implementation or record | Current answer |
| --- | --- | --- | --- |
| [`F254-linux-cache-proxy-composition`](../../findings/F254-linux-cache-proxy-composition/finding.md) | `closed` | merged PR #198 | validate and publish the whole request-to-cache lifecycle as one composition |
| [`F254-linux-output-root-safety`](../../findings/F254-linux-output-root-safety/finding.md) | `closed` | merged PR #199 | resolve the requested path, authorize only strict descendants of explicit roots, and prove symlink preservation |
| [`F254-tarfilter-regex-compatibility`](../../findings/F254-tarfilter-regex-compatibility/finding.md) | `closed` | merged PRs #151 and #220 | translate GNU basic/extended syntax explicitly and retain positive controls around rejection boundaries |
| [`F254-linux-package-variance`](../../findings/F254-linux-package-variance/finding.md) | `stopped` | merged PR #112 | ambient variants were byte-identical; the only package difference followed changed `SOURCE_DATE_EPOCH` |
| [`F254-linux-ecosystem-overlap`](../../findings/F254-linux-ecosystem-overlap/finding.md) | `stopped` | merged PRs #214 and #219 | keep the PPMd lesson, but do not implement while an equivalent active fix remains current |

The five files are the current technical-answer surfaces within this branch. Their eventual repository-canonical status depends on adoption into an independently accepted protocol generation.

## System map

- `teamleaderleo/fieldwork` owns cross-repository synthesis, transition state, review/delivery routing, and eventual canonical adoption.
- This PR #283-based branch owns provisional durable materialization only.
- `teamleaderleo/linux-fieldwork` owns imported source identity, patches, executable fixtures, investigation records, focused tests, and Linux CI receipts.
- Linux issues and pull requests own live exact-head routing and local merge history.
- Public project state may be read quietly for source and overlap checks; no public interaction is authorized.

## Established findings

### Cache composition

The request path, origin request, origin response, downstream response, cache writer, and final-name publication overlap in one handler. Individually green patches were insufficient. The final nine-file composition passed Linux Fieldwork CI run 612 at `5e69cd25e62d0e86364459d97c9df8568ff84187` and merged as `8d9f7fa92f0cb2f553ca3578b78d7e04f4e4167f`.

### Destructive harness safety

`tempfile.gettempdir()` is runtime discovery, not cleanup authority. In the observed sandbox it resolved into the checkout, and a repository child was recursively replaced. The final guard and direct/final-symlink/ancestor-symlink controls passed Linux Fieldwork CI run 620 at `6251a11fd30b26d29451e5ee292a6186344429a1` and merged as `12dd20f6965d11024afc6cbbcb2f039d53e4beef`.

### Archive regex compatibility

Python `re` and GNU tar assign different meanings to punctuation. The merged translator selects GNU basic syntax by default, extended syntax under `x`, rejects unproved Python-only groups, and keeps accepted-neighbor controls. Product head `4555c5c250c1afedb3947fd1a7b5a0323bd9d262` passed run 577; control head `bb0a79dec47958c6b865d4b382a44baff17ab736` passed run 634.

### Reproducibility stop

The Debian package corpus stayed byte-identical across elapsed time, path, locale, timezone, hostname environment, real user, file order, and parallel compilation. Changing the declared epoch changed archive timestamps but not extracted payload or control data. No defect was demonstrated.

### Ecosystem overlap stop

The local PPMd refill-accounting candidate overlapped an active equivalent public fix. The internal record keeps the mechanism, exact public head at the 2026-07-31 refresh, and the rule that promotion expires and must be rechecked before any future branch.

## Exact closeout receipts

- Linux Fieldwork PR #249 exact head `fed2b03cb3a584f0e3f2f2db5c58e6a2f0102023`: Linux Fieldwork CI `30592017920` / 720 success; merged as `d7aebcf38459fd3f4791c1ce5da1ec446d6d3296`.
- Protocol PR #283 exact head `23ef5d6e1d955eb7a8984a0491dc99a5e08a1d81`: Fieldwork integrity `30591290799` / 1230 success. Green execution does not make that protocol generation independently accepted.
- PR #308 pre-synchronization head `81a38cd7cdfcac3448b61579a38ecc5fa6ad9a92`: Fieldwork integrity `30595659828` / 1282 success; historical after head movement.
- PR #308 repair input head `37b8fe6e81f4dba140014fd53e95f1b4546f9ab9`: Fieldwork integrity `30628624377` / 1404 success; independent review `4828582244` retained the technical content but required this protocol/adoption cleanup.
- This cleanup advances the branch beyond `37b8fe6e...`; PR metadata owns the new exact head and its replacement integrity receipt.

## Missing evidence and reopening triggers

The compact list below is expanded into concrete questions, smallest safe probes, and continuity rules in [`research-avenues.md`](research-avenues.md).

- Cache: reopen for same-UID pathname replacement races, miss coalescing, crash durability, checksum policy, remote deployment, or broader URI syntax.
- Output-root guard: reopen if same-UID mutation after validation produces an escaping deletion path or if additional cleanup roots are proposed.
- Tarfilter: reopen for locale-sensitive ranges, POSIX bracket constructs, GNU alphabetic escapes, malformed-diagnostic parity, denial-of-service limits, expression-state composition, or broader archive metadata.
- Reproducibility: reopen with a new package, toolchain, architecture, format, or controlled factor that produces unexplained package-content variance.
- Ecosystem overlap: reopen only after a fresh read-only check shows the equivalent fix is closed, abandoned, materially different, or absent from a released version that still carries the defect.
- Cross-cutting: retain stale-state automation, skipped-job classification, and composition-first review heuristics as active research avenues.

## Current outputs

- provisional technical findings: the five root `findings/F254-*` files;
- adjacent research and interruption continuity: [`research-avenues.md`](research-avenues.md);
- Linux executable evidence: the linked Linux Fieldwork investigation and test paths;
- Linux exact-state synchronization: merged PR #249;
- initiative routing: issue #254 comments;
- public proposal or contact: none.

## Current next actions

1. Read and classify Fieldwork integrity for the exact post-cleanup PR #308 head.
2. Review the complete eight-file Markdown diff against repair review `4828582244`; verify that evidence remains claim-scoped and no technical conclusion or avenue changed.
3. Keep the branch in `REPAIR` until an independently accepted stable protocol generation exists and this packet is reconciled onto it.
4. After reconciliation, run exact-head integrity and obtain a fresh eligible independent complete-diff disposition.
5. Preserve every new avenue before stopping: question, consequence, source/environment boundary, evidence, blocker, smallest safe probe, reopening trigger, and authority state.
6. Do not merge, release, deploy, or contact public upstream without separate authority.
