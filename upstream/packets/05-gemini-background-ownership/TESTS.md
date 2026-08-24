# Tests and receipts — Unit 05 background shell cleanup ownership

## In simple words

The candidate’s six final file blobs have extensive target-native execution on public base `d55e366…`: a baseline leak characterization, 121-test initial ownership transfer, 123-test manual-background extension, and 39-test atomic claim repair. Each source generation also passed target formatting, package build, and core typecheck on its execution carrier.

The current branch `f754eafd…` applies those unchanged file blobs to public head `f47d6c6…`, whose one-commit delta touched no unit file. Its owned draft PR triggered only a skipped E2E launcher and emitted no ordinary status. This packet therefore keeps current-head compatibility at `source-read` plus `target-test-prepared`, while the predecessor receipts remain `target-executed` for the identical file content.

The largest important gaps are current-head target execution, target-declared `npm run preflight`, independent complete-diff review, and real PTY/cancellation/Windows controls.

## Identity

- Exact current upstream base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- Exact current candidate head: `f754eafde164420b43df5a58861d874cfb73acde`
- Exact executed predecessor base: `d55e366f6ab393e024c613d940fead3696d56eac`
- Final executed source stack head: `417ce25afdfd28cc4f6d0f1dcd5ad2686ec5e255`
- Current-base refresh carrier: `teamleaderleo/gemini-cli#18`, merged internally as `f754eafd…`
- Canonical current draft: `teamleaderleo/gemini-cli#19`
- Test dates: `2026-07-31` for retained execution; current-base/status inspection `2026-08-01`
- Environment and platform: GitHub-hosted Linux runners; characterization records include Node 22; target contribution guidance currently specifies Node `~20.19.0` for development and current preflight should use the supported version

## Claim-to-evidence matrix

| Claim | Evidence class | Test or source | Result | Coverage limit |
| --- | --- | --- | --- | --- |
| a short requested-background command can finish before claim and retain the temp directory on the base | `target-executed` | [`Gemini #9@c0f5202d`](https://github.com/teamleaderleo/gemini-cli/pull/9), run [`30596117032`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30596117032) | predicted retained-directory assertion passed | mocked execution; Linux-oriented filesystem path |
| initial transfer preserves creator fallback, both exit/claim orderings, actual child exit, cleanup-result precedence, and child `error` then real `close` once | `target-executed` | [`Fieldwork #334@0c398748`](https://github.com/teamleaderleo/fieldwork/pull/334), target run [`30623523324`](https://github.com/teamleaderleo/fieldwork/actions/runs/30623523324), publisher [`30624706086`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30624706086) | 121 passed, one existing skip; build/typecheck/format/fence passed | pinned Linux child path; five-file generation before manual extension |
| manual foreground-to-background claim transfers cleanup before the original foreground promise continuation | `target-executed` | [`Gemini #13@1c8a1982`](https://github.com/teamleaderleo/gemini-cli/pull/13), publisher run [`30629626006`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30629626006), job `91152716494` | 123 passed, one existing skip; build/typecheck/format/fence passed | child path; same-account self-review |
| nested claims, throwing callbacks, callback settlement, listener failure, rejected publication, and immediate retry are controlled | `target-executed` | characterization [`#14@1522d0ae`](https://github.com/teamleaderleo/gemini-cli/pull/14), run [`30649820502`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30649820502); final publisher [`30651009451`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30651009451) | characterization 37/37; final 39/39; build/typecheck/format/fence passed | callback side effects beyond current local state remain a design limit |
| current public base has no overlapping edits in the six unit files | `source-read` | compare `d55e366…f47d6c6…`; current compare [`f47d6c6…f754eafd`](https://github.com/teamleaderleo/gemini-cli/compare/fieldwork/upstream-f47-background-ownership-base...fieldwork/unit-05-background-ownership-current-source) | exactly six unit files in candidate diff | public main can advance after inspection date |
| current candidate passes target ordinary gates | `target-test-prepared` | [`Gemini #19`](https://github.com/teamleaderleo/gemini-cli/pull/19), workflow `30674218875` | E2E launcher skipped; no commit statuses | current-head execution absent |

## Baseline characterization

### Command or workflow

Execution carrier for [`Gemini #9`](https://github.com/teamleaderleo/gemini-cli/pull/9), run [`30596117032`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30596117032):

```text
Prettier check
focused target-native Vitest characterization
core workspace typecheck
clean-tree validation
```

### Assertions

- create a command with `is_background: true` and zero delay;
- settle the mocked execution before the delayed claim;
- await the normal result;
- require the extracted `gemini-shell-*` directory to remain;
- remove the retained directory in teardown.

### Result

- status: `pass`, where the passing assertion confirms the baseline defect
- test count: one focused characterization plus declared formatting/typecheck gate
- workflow: `30596117032`
- artifact or receipt: retained in Gemini #9 and Fieldwork finding #319/#320
- observed behavior: request intent suppressed creator cleanup despite absent accepted background ownership

## Candidate-focused tests

### Initial explicit transfer and child actual-exit cleanup

- Exact source head: `c9a0ec7f452ee9a3252661b78c230a1c7b5f9fcc`
- Source PR: [`Gemini #11`](https://github.com/teamleaderleo/gemini-cli/pull/11)
- Publisher: [`Gemini #10`](https://github.com/teamleaderleo/gemini-cli/pull/10)
- Command or workflow: run [`30624706086`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30624706086), job `91137148865`
- Tests and assertions:
  - `executionLifecycleService.test.ts`: 26 passed;
  - process-exit cleanup controls: 4 passed;
  - shell ownership-transfer controls: 3 passed;
  - adjacent `shell.test.ts`: 89 passed, one existing skip;
  - exit-before-claim keeps creator ownership;
  - claim-before-exit keeps resources until exit;
  - foreground and declined transfer creator-clean;
  - failed preflight produces no history/log side effects;
  - child actual exit invokes cleanup;
  - cleanup rejection preserves process result;
  - child `error` followed by awaited real `close` finalizes once.
- Result: `121 passed, 1 skipped`; package posttest build, explicit core typecheck, Prettier, exact parent, five-file fence, and clean worktree passed
- Receipt: artifact `8791620099`, digest `sha256:ab74a490fb2e6de882e66f13fdafe783b7149025f6938c3bdb1c25fa9df73f36`; patch digest `532894720bef54d36d120a7951cf4c8b2dafef244303d2eb3c3c811a2eff4830`; file-list digest `d4e90edb1e45c1bf94148df9af728c3d8e4fc38aa55b2fff3d1ee9431d8d9a6c`; metadata digest `8922bce12d003bcb6a0f112ce1e250a59d08783143c448de978dc05137a1f63f`
- Coverage limit: Linux child-process slice; no current-head, PTY, cancellation, or Windows result

### Manual foreground-to-background ownership transfer

- Exact source head: `1c8a198295ecbd01971bb79f0ed6afed16e66dbf`
- Source PR: [`Gemini #13`](https://github.com/teamleaderleo/gemini-cli/pull/13)
- Publisher: [`Gemini #12`](https://github.com/teamleaderleo/gemini-cli/pull/12)
- Command or workflow: run [`30629626006`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30629626006), job `91152716494`
- Tests and assertions:
  - real `ShellExecutionService.background(pid)` invokes `onBackgroundClaim` before the original result continuation;
  - a foreground shell later claimed as background keeps temporary resources through settlement;
  - actual child close removes resources once;
  - model-requested transfer, declined transfer, exit-before-claim, foreground completion, and child `error` then `close` remain covered.
- Result: `123 passed, 1 skipped`; package build, explicit core typecheck, target Prettier, exact five-file fence, clean source publication passed
- Receipt: artifact `8792869417`, digest `sha256:d6d8816d07929593012470fa4a256d85a9529beadc35af429eb5e7045701c02f`
- Coverage limit: same-account content review; public current base had not yet been refreshed

### Claim characterization

- Exact test-only head: `1522d0ae74acdb3ee71243829b8b1031565e3d54`
- PR: [`Gemini #14`](https://github.com/teamleaderleo/gemini-cli/pull/14)
- Executor: [`Gemini #15@6c753373`](https://github.com/teamleaderleo/gemini-cli/pull/15)
- Workflow: [`30649820502`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30649820502), job `91220038173`
- Assertions:
  - guarded re-entry on the predecessor can accept nested and outer calls and emit two starts;
  - throwing callback can leave lifecycle foreground while retaining history/log publication;
  - execution can still settle foreground after test cleanup.
- Result: `37/37` focused and adjacent tests passed, confirming predecessor behavior
- Coverage limit: characterization only; no repair in this head

### Final atomic claim repair

- Exact source head: `417ce25afdfd28cc4f6d0f1dcd5ad2686ec5e255`
- Source PR: [`Gemini #17`](https://github.com/teamleaderleo/gemini-cli/pull/17)
- Publisher: [`Gemini #16`](https://github.com/teamleaderleo/gemini-cli/pull/16)
- Workflow: [`30651009451`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30651009451), job `91224012827`
- Tests and assertions:
  - 4/4 new atomicity controls: re-entry rejected, throwing claim cleanly retryable, callback settlement rejected, failing start listener isolated;
  - 26/26 adjacent lifecycle tests;
  - 5/5 process-exit cleanup controls;
  - 4/4 manual/temp ownership controls;
  - exact prior history restored on rejection;
  - no rejected log stream/file;
  - accepted logging starts after lifecycle acceptance and before promise continuation;
  - immediate same-PID retry succeeds.
- Result: `39/39`; package posttest build, core typecheck, Prettier, three-file source fence, one-parent source, and clean tree passed
- Receipt: artifact `8801397571`, digest `sha256:0a998a250d07f9608ddfd7c66cafdb3c0e9ce480e81ca9f48cd748dd1bdc5abc`; patch digest `sha256:ed9f2f865ba0ad5a359c6e2d9eadf91d543ff085bfc427aa38814611c6579f22`; file-list digest `sha256:da0c6455eb19ac1b19ce6d71f5b8ad3bd0a6a270d7e2cdfa9df36ac507320f80`; metadata digest `sha256:a3962f2ff671e261aafde5a5c701689e73309122db57bddd18fa3142816f0ac3`
- Coverage limit: no independent acceptance; no general transaction guarantee for arbitrary future callback side effects

### Current-base materialization

- Exact base: `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`
- Exact source head: `f754eafde164420b43df5a58861d874cfb73acde`
- Refresh carrier: [`Gemini #18`](https://github.com/teamleaderleo/gemini-cli/pull/18), internally merged
- Canonical draft: [`Gemini #19`](https://github.com/teamleaderleo/gemini-cli/pull/19)
- Source result: compare contains exactly the six final product/test files; public delta from `d55e366…` to `f47d6c6…` contains no unit path
- Workflow result: run `30674218875`, `Trigger E2E`, completed `skipped`; combined commit statuses empty
- Failure classification: `runner/trigger behavior`, not product evidence
- Coverage limit: no current-head target command executed

## Ordinary repository gates

| Gate | Exact command or workflow | Result | Notes |
| --- | --- | --- | --- |
| format | publisher Prettier on exact changed-file fences | passed on all three executed source generations | current `f754eafd…`: not run |
| lint | target-declared lint within full preflight | not run as a retained exact candidate gate | current target policy requires preflight before submission |
| typecheck or compile | explicit core workspace typecheck | passed on `c9a0ec7f…`, `1c8a1982…`, `417ce25a…` | current head: not run |
| focused package tests | runs `30624706086`, `30629626006`, `30651009451` | passed | exact counts above |
| complete target-declared suite | `npm run preflight` | not run | required before public PR preparation |
| build or generated output | package posttest build | passed on executed generations | generated output not applicable; current head not run |
| platform matrix | Linux GitHub runner | partial pass | PTY/Windows/cancellation matrix not run |
| E2E launcher | run `30674218875` | skipped | no current-head product assertion |

## Reversing controls

- baseline short requested-background command retains the directory; candidate exit-before-claim creator-cleans it
- foreground cleanup passes on baseline and candidate
- accepted claim keeps resources until actual exit
- throwing claim leaves no publication and allows immediate retry
- nested claim returns `false` and emits one start event
- child synthetic `error` plus awaited real `close` invokes cleanup once
- cleanup rejection leaves successful exit result unchanged
- callback-driven settlement rejects background ownership and emits no start

## Soak, leak, and cleanup controls

- iterations: focused deterministic single-transition controls; no long-duration soak
- resources observed: temporary directory, PID file, background history map, log PID set, log stream map, log file, start listeners, lifecycle resolver/execution identity
- timers/tasks/processes/files/listeners before and after: exact cleanup asserted in focused tests; carrier clean-tree checks passed
- cancellation or interruption behavior: unexecuted for this unit
- immediate rerun result: one same-PID immediate retry after a throwing claim passed on final atomicity head

## Setup and harness failures

| Attempt | Failure | Classification | Product claim affected? | Repair or stop |
| --- | --- | --- | --- | --- |
| early Fieldwork carrier #321, target gates `30597354345` / integrity `30597354348` | initial carrier remained pending while review found duplicate child `error`/`close` finalization | product-design review, before promotion | yes, generic exit callback exact-once claim | added owner-level `exited` guard and deterministic regression in #334 |
| #334 head `80dcefaa…` | regression waited 100 ms and could pass before real `close` | fixture/test design | exact-once production change remained plausible; test proof insufficient | commit `c1faf83a…` recipe added a real close barrier; final head `0c398748…` passed |
| first atomicity source `c3e07b42…` | rejected-log cleanup could race an immediate same-PID retry | product-design review | yes, retry atomicity | move log creation after accepted claim; add immediate retry test; final `417ce25a…` |
| current draft #19 | only E2E trigger run skipped | runner/trigger | no current-head product result available | execute explicit current-head target gate on a suitable owned carrier or local target checkout |

## Checks prepared but not executed

- the three final focused test files at [`f754eafd`](https://github.com/teamleaderleo/gemini-cli/tree/f754eafde164420b43df5a58861d874cfb73acde/packages/core/src) — unchanged from executed blobs, awaiting current-head run
- target `npm run preflight` — required current ordinary gate
- real PTY duplicate/failure path — source callback exists, execution receipt absent
- cancellation/escalation cleanup ordering — separate lifecycle interaction
- Windows temporary-directory and process tracking path — source review and runner needed

## Platform and integration gaps

- Windows process and temporary filesystem behavior
- real `node-pty` terminal exit, error, abort, and duplicate callback ordering
- cancellation and kill escalation while ownership transfer is pending or accepted
- abrupt CLI termination and stale-directory cleanup across restarts
- long-duration repeated background execution and inode/disk measurement
- A2A server mode and remote-agent paths

## Cleanup receipt

- Temporary workflows removed from canonical source head: `yes`
- Publisher or execution-only files removed: `yes`
- Generated residue checked: `yes` on executed source publishers; current source compare contains no generated files
- Immediate rerun performed: `yes` for rejected claim retry; no full current-head rerun
- Remaining temporary branches or PRs: historical branches for #9/#10/#12/#14/#15/#16/#18; source PRs #11/#13/#17 remain open as retained generations; canonical source diff #19 contains none of their workflow files

## Current test judgment

`EXECUTE`

Reason: the identical final file blobs carry strong focused target execution and the current public-base delta does not overlap the unit. The exact current source head still lacks a passing retained ordinary gate, complete target preflight, and the requested adapter/platform controls. A skipped E2E launcher provides no product evidence.

Clearing condition: run formatter, all three focused files plus adjacent shell/lifecycle suites, core build/typecheck, and target `npm run preflight` on exact head `f754eafde164420b43df5a58861d874cfb73acde`, then obtain independent complete-diff review or record any current-base repair.
