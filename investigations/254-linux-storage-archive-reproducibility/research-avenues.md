# Workstream H research avenues and continuity ledger

Upstream contact authorized: no

## In simple words

A bounded fix can be finished without declaring the surrounding subject dead. A negative result can stop one proposed change without erasing the questions it exposed.

This file preserves the adjacent research avenues from Workstream H. It exists so that a tool failure, safety boundary, policy restriction, unavailable environment, stale public state, or abandoned worker chat cannot silently erase useful directions.

## State words used here

- `closed` means the specific bounded finding was repaired, executed, and merged locally, or otherwise completed with no remaining transition for that exact claim.
- `stopped` means the current implementation or defect premise should not continue now. The evidence, reason, and reopening trigger remain active knowledge.
- Neither word means “the whole topic is uninteresting” or “never investigate nearby questions.”

## Continuity rule

When an avenue cannot continue, preserve before stopping:

1. the concrete question;
2. why it may matter;
3. the exact source or environment boundary already inspected;
4. what evidence exists;
5. the blocker or safety boundary;
6. the smallest safe next probe;
7. the condition that would make the avenue worth reopening;
8. whether public interaction is authorized.

Do not collapse an unavailable tool, skipped job, missing privilege, policy boundary, or external-contact prohibition into a technical negative result. Record it as a blocker or evidence limit.

## Cache-proxy avenues

### Descriptor-relative path authority

- Question: can cache reads and publication be expressed relative to trusted directory descriptors so same-UID pathname replacement after validation cannot redirect access?
- Why it matters: the merged composition validates resolved paths before use, but does not fence later mutation by another process with the same filesystem authority.
- Existing evidence: merged cache composition PR #198 and exact-head run 612.
- Smallest next probe: construct a controlled rename/symlink swap between validation and open, then compare path-based and descriptor-relative candidates.
- Reopening trigger: a reproducible same-UID escape or a current source design that can adopt `openat`-style ownership without broad portability loss.

### Miss coalescing and writer generations

- Question: should concurrent misses share one origin fetch, and which client owns cancellation or failure?
- Why it matters: duplicate downloads are currently allowed; a future coalescer could introduce stale-writer, cancellation, or observer-settlement defects.
- Existing evidence: current matrix proves no partial final-name visibility under duplicate misses.
- Smallest next probe: two clients, one slow origin, one client disconnect, one writer failure, then assert final cache state and each client outcome.
- Reopening trigger: performance pressure, origin-rate limits, or a concrete coalescing candidate.

### Crash-durable publication

- Question: what durability contract should exist across file data, rename, and parent-directory metadata?
- Why it matters: atomic namespace publication does not prove survival after sudden power loss.
- Existing evidence: hidden temporary plus atomic replace under ordinary process failure.
- Smallest next probe: a fault-injection model around file flush, rename, and directory sync; do not claim storage durability from ordinary CI.
- Reopening trigger: a deployment or package workflow that relies on cache survival across host crash.

### Content trust and remote deployment

- Question: should the helper verify checksums or authenticated metadata, and what URI/deployment surface is supported beyond local CI?
- Why it matters: transport completeness is not content authenticity, and loopback development use is narrower than a remote service.
- Smallest next probe: map current callers and package-verification ownership before adding trust or network authority.
- Reopening trigger: a real remote caller, checksum contract, or deployment proposal.

## Destructive harness avenues

### Race-resistant recursive deletion

- Question: can deletion remain inside one trusted directory handle after validation even when another same-UID process mutates path components?
- Why it matters: decision-time resolution defeats existing symlinks but does not eliminate mutation after the check.
- Existing evidence: direct, final-symlink, and ancestor-symlink preservation in merged PR #199 and run 620.
- Smallest next probe: adversarial rename/symlink swapping against a disposable tree, with sentinels outside every allowed root.
- Reopening trigger: a demonstrated post-validation escape or a descriptor-relative deletion candidate.

### Explicit cleanup capabilities

- Question: should harnesses receive an already-created owned directory or capability object instead of a caller-chosen pathname?
- Why it matters: capability-style ownership may make the destructive boundary easier to review than expanding path allowlists.
- Smallest next probe: compare current CLI ergonomics with a parent-created output directory whose identity is retained by descriptor or inode.
- Reopening trigger: proposals for custom temporary roots or reuse across more harnesses.

### Cross-platform path semantics

- Question: which parts of the strict-descendant and symlink model remain correct on non-Linux platforms?
- Why it matters: drive roots, junctions, mount points, and path normalization differ.
- Smallest next probe: only after a supported non-Linux execution requirement exists; use native filesystem controls rather than textual path simulation.

## Tarfilter and archive avenues

### Locale and POSIX bracket semantics

- Question: how should POSIX character classes, collating elements, equivalence classes, and locale-sensitive ranges map into the chosen matcher?
- Why it matters: the current translator is intentionally bounded to the executed `LC_ALL=C` subset.
- Existing evidence: merged product PR #151 and positive controls PR #220.
- Smallest next probe: a differential corpus across GNU tar and tarfilter under two named locales, with expressions that can make a proposed translation lose.
- Reopening trigger: caller demand, a real mismatch, or a proposal to claim broader GNU/POSIX compatibility.

### GNU-specific escapes and diagnostics

- Question: which alphabetic escapes and malformed-expression diagnostics are compatibility requirements rather than implementation details?
- Smallest next probe: inventory GNU tar acceptance, output, exit status, and error category for a bounded set; keep diagnostic wording separate from rename semantics.
- Reopening trigger: a user-facing compatibility failure or upstream preparation.

### Regex resource limits

- Question: can accepted translated expressions cause catastrophic backtracking or unbounded resource use in Python's matcher?
- Why it matters: syntax parity does not establish safe runtime complexity.
- Smallest next probe: adversarial names and patterns with time/memory limits, compared against GNU tar behavior and an explicit policy boundary.
- Reopening trigger: a measured pathological case or service-style untrusted expression input.

### Transform-state language

- Question: how should persistent `flags=`, semicolon-separated expression lists, occurrence state, and replacement case-conversion compose?
- Why it matters: these features share state across expressions and can invalidate individually correct transforms.
- Smallest next probe: one ordered expression-list matrix covering member names, link targets, PAX regeneration, and failure before output.
- Reopening trigger: continuation of the later expression-state lanes or preparation of one complete compatibility packet.

### Broader archive metadata

- Question: do all transform paths preserve sparse metadata, ownership, timestamps, xattrs, ordering, and unusual link encodings when regex behavior changes?
- Smallest next probe: reuse retained archive fixtures and compare whole archives plus extraction, not only member-name lists.
- Reopening trigger: a new transform implementation mechanism or archive-format expansion.

## Reproducibility avenues

### Broader package corpus

- Question: which real source packages expose unexplained variance under the same factor-isolation method?
- Why it matters: the retained native fixture is a negative result, not proof that all Debian packages are reproducible.
- Existing evidence: PR #112, repository run 293, dedicated LF-12 run 6.
- Smallest next probe: choose one package with generators, compression, or archive inputs and vary one factor at a time while retaining package, payload, control, and build-event layers.
- Reopening trigger: a package-specific symptom or unexplained byte difference.

### Toolchain and architecture boundaries

- Question: do compiler family, architecture, source format, or dpkg version expose variance hidden by the current amd64 Debian 13 fixture?
- Smallest next probe: one controlled second environment with the same source and declared epoch, then classify the first differing layer.
- Reopening trigger: available native/VM capacity and a bounded comparison question.

### Host identity and scheduling

- Question: does changing the actual UTS hostname, larger file-order sets, or richer parallel schedules affect outputs where environment-only `HOSTNAME` and two-object `-j4` did not?
- Smallest next probe: namespace-backed hostname change and a fixture with enough independent work to vary scheduling meaningfully.
- Reopening trigger: capability becomes available or a real package depends on these surfaces.

### Diagnostic tooling

- Question: when should `diffoscope` or `reprotest` be added?
- Answer: after a new unexplained difference appears. They are diagnostic amplifiers, not a reason to reopen a stopped fixture by themselves.

## Ecosystem and overlap avenues

### Public-state expiry

- Question: is the equivalent PPMd fix still active, semantically equivalent, and relevant to current releases?
- Existing evidence: read-only 2026-07-31 observation at exact public head `78b75ec7c9bca13870cecb5cd4f60272bed86fc9` and internal overlap PR #219.
- Smallest next probe: fresh read-only head/state/source comparison before any branch creation.
- Reopening trigger: closed-unmerged, abandoned, materially changed, or missing from a required release.

### Downstream patch retirement

- Question: after an equivalent fix lands, which downstream packages or workarounds can be removed, and from which release?
- Why it matters: successful upstream repair can leave stale downstream patches that later conflict or mask regressions.
- Smallest next probe: map distro-carried patches and released versions only when the public fix state changes.
- Reopening trigger: merge plus release adoption, or a downstream package carrying the same workaround.

### Distinct semantic follow-up

- Question: does a nearby PPMd or refill case differ enough to justify independent work?
- Smallest next probe: state the new invariant and fixture difference explicitly; do not reopen merely because the code area is interesting.
- Reopening trigger: a case the active fix does not cover.

## Cross-cutting composed-integration avenues

### Evidence-state automation

- Question: can CI detect tracked records that still say “queued,” “rerun required,” or “ready to merge” after the exact head has completed or merged?
- Why it matters: stale prose caused real routing repair in Linux PR #249.
- Smallest next probe: a read-only checker that compares recorded heads/runs/dispositions with controlled repository metadata, without silently changing state.
- Reopening trigger: repeated stale-closeout defects or integration with Fieldwork's coordination evaluator.

### Skipped-job classification

- Question: can workflow summaries make the difference between product execution, documentation integrity, path-filter skip, capability skip, and harness failure explicit?
- Why it matters: a skipped product job must not be promoted as product evidence, while a green repository gate may still validate a documentation-only repair.
- Smallest next probe: machine-readable per-job evidence class and reason, tested against LF-23 and other mixed workflows.

### Composition-first review heuristics

- Question: which independently green repairs share enough source ownership that they require one composed candidate and matrix?
- Smallest next probe: derive overlap from changed functions, state owners, and test fixtures, then compare against known cache and tarfilter stacks.
- Reopening trigger: another multi-PR stack touching one lifecycle or publication boundary.

## Safety and interruption note

If future work is interrupted by a safety system, unavailable capability, restricted command, policy boundary, or uncertain authority:

- do not invent a technical conclusion;
- do not delete the avenue;
- retain the exact attempted action, what was and was not observed, the safe evidence already available, and the smallest allowed continuation;
- route only the genuinely non-delegable authority question to a person.

This ledger grants no merge, deployment, release, credential, private-data, or public-interaction authority.
