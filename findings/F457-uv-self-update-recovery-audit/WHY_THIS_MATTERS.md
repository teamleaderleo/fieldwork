# Why this deserves review

## The 30-second case

A self-updater is recovery infrastructure. If it reports an ordinary failure, the command needed to diagnose or retry the update should not disappear, and the installation should not quietly contain files from different releases.

This audit now has clean Windows execution proving both failure classes:

1. the `self-replace` primitive used by the public candidate can return an ordinary missing-source error after removing the canonical executable;
2. the public candidate's companion-copy ordering can leave old `uv.exe` beside new `uvx.exe` when final executable replacement fails.

The public regression does not distinguish the historical defect: its asserted temporary `uv.exe` also passes on the known-broken old code. The public pull request is directionally valuable, but its current evidence and broad guarantee are stronger than the implementation.

## What is execution-proven

### Ordinary final replacement error can remove canonical uv

Exact owned control:

- fork PR: `teamleaderleo/uv#10`;
- exact head: `34031835cbfe8b84edaf8e3ce5d6d846bc50d59e`;
- run/job: `30754221525` / `91513487808`;
- result: helper returned the expected replacement-copy error and its canonical copied executable path was absent;
- artifact: `8836256601`;
- digest: `sha256:2d4ab5cfa6649c86a8e67a4f774ddbcb16f5e634138f396e67223f67d185580b`.

This is not a power-loss thought experiment. It is an ordinary handled error at the exact primitive used by the public candidate.

### Finalizer failure can leave a mixed installation

Exact owned control:

- execution-only PR: `teamleaderleo/uv#17`;
- exact public-candidate base: `77e107dd2665f660c461998bc83174bf26ee7cf6`;
- exact carrier head: `e8b7a3ae5bbdc2d70832985a709e9a5c97a4baf1`;
- run/job: `30754972997` / `91515482594`;
- result: the exact companion-copy loop completed, injected final replacement failed, and live state was old `uv.exe` plus new `uvx.exe`;
- focused test: one passed, zero failed;
- artifact: `8836688193`;
- digest: `sha256:8cce47b0ad3862fbb7f199b21276926ba980c9675af51b092fbf8ecef894e02c`.

This separates two contracts that should not be conflated:

- **command availability** — some `uv.exe` exists at the canonical path;
- **installation coherence** — `uv`, `uvx`, `uvw`, and the receipt describe one recoverable generation.

### The current Job Object policy does not own the installer tree

Exact policy control:

- experiment PR: `teamleaderleo/uv#19`;
- exact head: `6098dab64d959f9cf40fb44bbd8d4849c3aa9239`;
- run/job: `30755788490` / `91517588607`;
- result: with uv's current silent-breakaway policy the delayed descendant survived; under a strict inherited-tree policy it did not;
- artifact: `8837070751`;
- digest: `sha256:ef0f8df1cae24898ad18abafef046d473b2fd3b47d72db96cebd212e18813998`.

This does not prove that strict Job membership is compatible with every real installer. It proves that `kill_on_drop(true)` plus the current Job policy is not evidence of complete descendant cancellation.

### The staged installer direction still has real value

The repaired candidate-side control used the actual running executable, awaited cancellation completion, and observed that cancellation during the isolated installer phase kept canonical `uv.exe` present. That is a meaningful improvement over the historical pre-rename flow.

The correct review position is therefore not "reject the public pull request." It is:

> keep the staging direction, replace the invalid evidence, narrow the guarantee, and repair or explicitly defer the remaining commit boundaries.

## The public head moved, but the core concern remains

Current public PR `astral-sh/uv#20855` is open at `8d9324af47e1b52ec1f57f9232bd408281282cf5`.

Its second commit promotes the staged receipt into the live receipt path after companion copies and before `self_replace`. This fixes the earlier stale-receipt omission, but it adds the receipt to the same partial-commit window:

1. companions are copied into live names;
2. the new receipt is written live;
3. final `uv.exe` replacement runs;
4. an ordinary finalizer error can occur after steps 1–2.

The already executed mixed-generation control was against the first public head. The new commit does not reorder or roll back companion copies or final replacement; it inserts another live mutation before final replacement. An exact-current-head failure control is still appropriate before making a current-head target-executed claim.

Public CI run `30785105065` succeeded at the new head. That establishes repository acceptance under the existing suite, not recovery from the injected finalizer failure above.

## Why green CI did not settle this

The important failures are between successful high-level stages:

- after the generated installer succeeds;
- after one or more companion files are live;
- after the receipt is live;
- after old canonical `uv.exe` is renamed;
- before new canonical `uv.exe` is durable.

Ordinary success tests and an interruption test aimed at an unrelated fixture do not enter those states. The audit adds failure injection at the actual commit boundaries.

## The smallest useful review asks

A reviewer does not need to endorse a transaction framework. The immediate asks are bounded:

1. **Public uv PR:** replace the unrelated-fixture regression with an actual-current-executable old/candidate discriminator and await cancellation completion.
2. **Public wording:** limit the guarantee to cancellation during the isolated installer phase unless final replacement is repaired.
3. **self-replace:** stage replacement bytes before destructive rename and restore canonical on every ordinary post-rename error; define process-death recovery separately.
4. **uv commit helper:** test finalizer failure after companions and receipt have changed; either roll back or record a recoverable transaction.
5. **custom/GHE route:** explicitly exclude it from the claim or move it away from axoupdater's pre-installer rename.
6. **process tree:** do not call direct-child cancellation full installer cancellation; choose a race-free creation-time Job assignment only after compatibility testing.

## What is not ready

This is not an upstream-ready grand patch:

- the deferred-finalizer prototype builds but its first hostile runtime control currently exits before the parent-wait assertion and needs diagnosis;
- the journal-recovery stack still needs a clean current-head matrix;
- the strict updater integration exposed a real `Send` ownership problem for the Job handle and has not reached target execution;
- strict Job compatibility with the real generated installer is unproven;
- an exact-current-public-head mixed binary/receipt failure receipt is not yet retained;
- custom/GHE clean successor runs were cancelled, although the earlier target assertion observed the destructive state;
- multi-file recovery design still needs hashes, atomic journal replacement, directory durability, and idempotent startup recovery.

## Why look now

The existence question is no longer speculative. Two consequential states are cleanly reproduced on Windows, and the public pull request is active and still makes the broad claim those controls contradict.

Review now can do three useful things before the implementation hardens:

- prevent a non-discriminating regression from becoming permanent evidence;
- prevent "canonical command survived one phase" from being mistaken for "failed updates are safe";
- help assign the remaining work to the correct owners instead of forcing one oversized patch.

That is enough reason for a focused review even if the eventual architecture is smaller than the full recovery proposal.

Public upstream contact remains unauthorized and none occurred.
