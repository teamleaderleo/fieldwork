# Workstream E live-state audit — 2026-07-31

Assignment: reconcile the agents/CLI portfolio after updated Fieldwork instructions, identify what still needs care, distinguish active source from evidence and execution carriers, and repair the project explanation without touching concurrent target branches.

Upstream contact authorized: `false`.

## Inputs read

### Fieldwork instructions

- `START_HERE.md`
- `AGENTS.md`
- `CHARTER.md`
- `CODE_FIRST.md`
- `PLAIN_LANGUAGE.md`
- `METHOD.md`
- `REFERENCE_POLICY.md`
- `PROGRAMMES.md`
- `TARGET_HUBS.md`
- `EXPERIMENTS.md`
- `TESTBEDS.md`
- `INTEGRATION_CONTEXT.md`
- `COORDINATION.md`
- `REVIEWING.md`
- `BATCHES.md`
- canonical finding pilot PR `#264@578fb94a641905a02ee8feaa292ff928756d5ad6`

### Coordination records

- initiative `#254`, including current body and E updates;
- Codex command issue `#239`;
- Gemini lane `#22`;
- T3/OpenCode campaign `#71` and completed review `#234`;
- inventory PR `#250@b2333e2749732770f7d42ec1ee2b836a785620a0`;
- `TARGET_PORTFOLIOS.md` and `RESEARCH_INVENTORY.md` from PR `#250`.

### Owned target surfaces

- recent Codex PRs through `teamleaderleo/codex#82`;
- Gemini PRs `teamleaderleo/gemini-cli#1` through `#8`;
- T3 legacy and V2 heads recorded in campaign `#71` and review `#234`.

## Project-state defects found

### 1. Gemini inventory mixes evidence and implementation

`TARGET_PORTFOLIOS.md` from PR `#250` labels Gemini PRs `#1`–`#4` as “Current candidate heads.” The live state is more precise:

- `#1`: open target-executed evidence; production repair separate;
- `#2`: closed target-executed evidence; implementation successor `#6`;
- `#3`: closed target-executed evidence; implementation/publication successors `#7/#8`;
- `#4`: open target-executed design-contract evidence;
- `#6`: active source repair with a known post-await authority defect;
- `#7`: active staged source repair; exact formatted behavior/type receipt green;
- `#8`: active source-publication carrier; first run failed in shallow Git object setup.

Recommended inventory correction: rename the old group to “retained evidence heads,” add a separate “active repair and publication heads” group, and state each exact next gate.

### 2. T3/OpenCode inventory predates the V2 transfer decision

`RESEARCH_INVENTORY.md` still says OpenCode/T3 is active comparative research and names `#234` as part of the live issue family. The live decision is:

- review `#234` completed;
- A interruption ownership transfers to V2, with composed-head execution still required;
- B pending requests transfer after direct cancellation and late-response controls;
- C uses explicit cancel-on-restart;
- D release ownership transfers to V2;
- legacy test-only PR `teamleaderleo/t3code#1` is closed;
- core V2 and OpenCode V2 evidence remain branch-specific and divergent.

Recommended inventory correction: classify the legacy path as stopped/retained evidence and the V2 composed gate as active research.

### 3. Earlier E blocked handoff expired

The prior E handoff described GitHub runner allocation as the blocker. Current runs have results:

- Gemini typed receipt `30581298716`: success;
- Gemini source publication `30581445734`: failed before source application because the carrier could not read base tree `d55e366...` after shallow fetch;
- Codex terminal run `30583869200`: source reconstruction passed; repository formatting stopped because `uv` was absent;
- Codex current upstream advanced to `a01a2d91461a57809e944de7758477b92617ab01` and new source/carrier successors were opened.

The live blockers are carrier repair and current-pin renewal, not runner allocation.

## Exact current target snapshots

### Gemini CLI

| PR | Head | Class | Current state |
| --- | --- | --- | --- |
| `#1` | `30da6f7566d394150f9d62522e374c42c931c072` | evidence | target-executed missing abort handoff; needs separate real process-tree repair |
| `#2` | `a7f5cc934446849e19a08cc8f4527473ada74401` | evidence | closed; affinity repair routes to `#6` |
| `#3` | `974f6e288bf3e86af0c06cb445b9626bd5d2280f` | evidence | closed; waiting repair routes to `#7/#8` |
| `#4` | `e33c6715cd289f912574025580cd74e4da9fe5bc` | evidence/design | target-executed asynchronous-kill contract; design choice remains |
| `#5` | `3952c0fedf35e9f35ebc200c4ab9120727a5a11c` | execution carrier | closed; receipts transferred |
| `#6` | `0ffa264696cb7dd422ee0596518fd2f1194b529d` | source repair | REPAIR: post-await exact-ID/status fence and controls required |
| `#7` | `9d257f565fa42c88bed519038a789dff81668b35` | staged source plus workflows | run `30581298716` green; clean source publication still required |
| `#8` | `90c65f3380dc1bb6ada7aa4e9e6767b01af399c0` | execution carrier | run `30581445734` failed before source application on missing base tree |

### Codex

Current observed upstream pin: `a01a2d91461a57809e944de7758477b92617ab01`.

| Family | Current source or carrier | State |
| --- | --- | --- |
| Receipt wire and replay | source `#73@e205ffe911dcbd661b47c4107e7f26ae772f8182`; carriers `#74/#78/#80` | active; exact current-source validation and replay gates remain |
| MCP publication | source `#75@c3373c717f3138ff5f0a979d12836f60800d2bcf`; carrier `#77` | active exact tests |
| MCP reconnect | source `#76@7e9d80c4965a76b802f02d7bace17ea1c4a8931c`; carrier `#82@8203182f0c4ba6811b86b0e33b3788cf8a235644` | first carrier run cancelled; request-path and strict all-or-zero controls remain |
| MCP authority | carrier `#79@bd985ba91b54da866659f303526ffb79d7b2e757` | active |
| Deferred exposure | current source `#81@8f73d8e0bb9a61e7dec7b1367d13649a88615dea`; older mixed carrier `#64` | current source inherits prior exact receipt; current exact gates and carrier consolidation remain |
| Stack pressure | diagnostic `#71@fd2c0b6e53fd66cf8eccb7e4d8256a9417aca1e0` | active diagnostic, no product source proposed |
| Terminal retention | isolated carrier `#70@220aaf936ff7445908d02ddd4df409bf4a7a9b84` targeting `97576b...` | reconstruction green; formatting harness failed because `uv` absent; latest-pin renewal still required |

Closed exact-pin predecessors remain immutable evidence when their front page names the current successor. They should stay outside the ordinary active review list.

### T3/OpenCode

| Surface | Exact head or record | State |
| --- | --- | --- |
| Core V2 evaluation | `0d61f31820f8254338571ac3049e7dc0ac621f7c`, run `30556506779` | target-executed green for A/D ownership boundaries |
| OpenCode V2 evaluation | `4f94ecabee645bafeffcc6d620905bd0b7ad6d13`, run `30557111582` | target-executed green for branch-specific adapter/cleanup behavior |
| Review decision | Fieldwork `#234` | completed |
| Legacy test carrier | `teamleaderleo/t3code#1@cae5d869f3ca441b4117197e34796a7d8b9466af` | closed evidence |
| Remaining work | composed V2 head | direct terminal-request cancellation, late-response rejection, cleanup ordering, and branch composition |

## Exact workflow classifications

### Gemini typed receipt

- Repository/head: `teamleaderleo/gemini-cli@9d257f565fa42c88bed519038a789dff81668b35`
- Run: `30581298716`
- Conclusion: success
- Established: formatted staged patch, four files / 16 tests, build, core typecheck
- Limit: no clean current-source publication head

### Gemini source publication

- Repository/head: `teamleaderleo/gemini-cli@90c65f3380dc1bb6ada7aa4e9e6767b01af399c0`
- Run/job: `30581445734` / `91002417191`
- Conclusion: harness failure
- First failed step: extract reviewed staged repair
- Exact error: `fatal: unable to read tree (d55e366f6ab393e024c613d940fead3696d56eac)`
- Smallest repair: fetch the exact base commit/tree explicitly before computing the staged diff or checking out the base

### Codex terminal carrier

- Repository/head: `teamleaderleo/codex@220aaf936ff7445908d02ddd4df409bf4a7a9b84`
- Run/job: `30583869200` / `91010510538`
- Conclusion: harness failure after source reconstruction
- Passed steps: exact carrier checkout, script extraction, exact-ref fetch, target CI setup, Rust setup, nextest setup, source reconstruction
- First failed step: format and verify source fence
- Exact error: `uv run ...`; `No such file or directory: 'uv'`
- Smallest repair: use the narrow Rust formatter for the four-file fence or install the repository-declared Python formatter prerequisite before whole-repository `just fmt`
- Additional currentness gate: renew the source against `a01a2d...` before promotion

## Retirement vocabulary recommended for E

Use these phrases consistently:

- **closed evidence** — the branch keeps a reproduction or historical receipt; implementation lives elsewhere;
- **closed execution carrier** — the temporary rig is closed and its receipt/successor is named;
- **superseded exact pin** — useful historical comparison; a newer source head owns current review;
- **active source repair** — candidate code still needs a named gate;
- **active execution carrier** — workflow machinery still needs a result or cleanup;
- **fully retired** — a later exact canonical source head is independently reviewable and contains no temporary workflow.

This avoids using “retired” for a carrier whose proposed source still contains or depends on temporary workflow machinery.

## Repairs made by this audit

- created canonical portfolio finding `findings/F254-workstream-e-current-state/finding.md`;
- replaced the expired runner-blocked narrative with current workflow outcomes;
- separated “care now,” “keep as evidence,” and “safe to ignore during ordinary review”;
- recorded exact current heads and successor relationships;
- preserved inventory corrections as a bounded follow-up instead of editing concurrent PR `#250`.

## Next actions

1. Repair Gemini PR `#8` exact-base fetch and publish a clean source-only waiting-ownership head.
2. Perform complete-diff review on that published head, transfer run `30581298716`, then close temporary publication machinery.
3. Correct Gemini PR `#6` after-await authority handling and execute during-await cancellation/replacement controls.
4. Repair Codex terminal formatting setup, renew onto current upstream, execute exact-name/count controls, and publish a source-only head.
5. Keep Codex issue `#239` as the technical command surface while this finding remains the plain-language navigation surface.
6. Materialize separate canonical findings for Gemini process termination, Gemini approval ownership, Codex receipt persistence, Codex MCP authority/publication, Codex terminal retention, and T3/OpenCode V2 composition when those states next change.
7. Update PR `#250` inventory wording after the canonical finding workflow is accepted or through a rebased inventory repair PR.

Public upstream interaction performed: `false`.
