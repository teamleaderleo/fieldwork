# Campaign: T3 and OpenCode completion reconciliation

State: `claimed`

## In simple words

T3 can remember that an OpenCode-backed turn is still running after the in-memory OpenCode adapter has been rebuilt. The rebuilt adapter knows which OpenCode session to resume, but it does not know the old T3 turn ID. When OpenCode later reports that the session is idle, the adapter currently emits completion only when that in-memory turn ID exists.

A focused regression test is now committed on the owned T3 fork. It resumes an existing OpenCode session, delivers an immediate provider `idle` status, and requires the adapter to emit canonical `session.state.changed` with `ready`. The current source has no such fallback, so the test is expected to time out. No target-native run is claimed because this environment cannot clone or install the repository and the fork has no branch-push CI run for the commit.

The production repair is deliberately not committed yet. A thread-scoped `ready` fallback is small, but a delayed idle event from an old provider instance could clear a newer turn unless provider-session or generation affinity is proved. The next evidence gate is therefore to run the prepared test and add an adapter-replacement ordering case before choosing between thread-scoped reconciliation and durable turn identity.

## Assignment

- Fieldwork issue: #71
- Programme: `agent-cli-execution` (#14)
- Worker: `chatgpt:gpt-5.6-thinking`
- Claim scope: `mechanism` and `interface`
- Retrieval date: `2026-07-30`
- Upstream contact authorized: `false`
- Owned Fieldwork path: `campaigns/t3-opencode-completion-reconciliation/`
- Owned target branch: `teamleaderleo/t3code:fieldwork/opencode-completion-reconciliation`

Pinned sources:

- T3 Code base: `teamleaderleo/t3code@85a89868703530e03c5e79797c7b952c684bd222`
- OpenCode reference: `teamleaderleo/opencode@7565e03536d19e850f9996c407f9bf5e932b5f7a`
- Prepared target test commit: `teamleaderleo/t3code@97a745ff8cc67076c7909ec9de418e3660acf723`
- Fieldwork base: `teamleaderleo/fieldwork@ed91a4d1de9d62b3eab50d0b0188917b061746db`

Dependencies:

- scout PR #63;
- programme #14;
- completed Gemini lifecycle scout #22;
- cross-agent process comparison #24.

Stop condition:

Stop if the target-native trace disproves the restart identity gap, if correct reconciliation requires changing OpenCode itself, or if no bounded repair can avoid closing the wrong turn.

## Repository protocol followed

The T3 fork's `AGENTS.md`, `CONTRIBUTING.md`, vendored Effect guidance, and Effect function checklist were read before writing the test.

Applied constraints:

- focused backend test only;
- no repository-wide checks;
- no browser or live T3 state;
- no target pull request without a separate explicit request;
- no upstream issue or pull request;
- no production repair before the regression boundary is established.

## Source-confirmed behavior

### OpenCode adapter resume

The OpenCode resume cursor stores a schema version and OpenCode session ID. `startSession` validates and re-adopts that upstream session. The new `OpenCodeSessionContext` initializes `activeTurnId` as undefined.

The cursor therefore restores conversation identity but not the T3 turn identity recorded by the orchestration layer.

### OpenCode idle mapping

The adapter captures `context.activeTurnId` before processing each subscribed event.

For `session.status`:

- `busy` updates the adapter-local session to running;
- `retry` emits a warning;
- `idle` clears local active state and emits canonical `turn.completed` only when the captured turn ID is present.

If the adapter was rebuilt and no new turn was sent through that instance, an idle event produces no canonical lifecycle transition.

### T3 lifecycle projection

`ProviderRuntimeIngestion` clears a persisted active turn when it receives:

- `turn.completed` for the applicable turn;
- an inactive `session.state.changed` state such as `ready`;
- `session.exited`.

`turn.aborted` is not part of that session-state transition block.

### Interruption

`ProviderService.interruptTurn` allows session recovery. The OpenCode adapter then calls upstream `session.abort` and emits `turn.aborted`, but does not directly clear adapter active state or emit `ready`/`turn.completed`.

A later OpenCode idle event can settle the turn while the adapter still knows its ID. After adapter reconstruction, the same idle path may have no turn ID and emit nothing.

## Prepared target regression

Target path:

`apps/server/src/provider/Layers/OpenCodeAdapter.restart.test.ts`

Target commit:

`97a745ff8cc67076c7909ec9de418e3660acf723`

Intended command:

```sh
vp test run apps/server/src/provider/Layers/OpenCodeAdapter.restart.test.ts
```

Scenario:

1. create an adapter against a fake external OpenCode server;
2. resume `ses_persisted` from the durable cursor;
3. have the fake SDK event stream immediately publish `session.status: idle`;
4. collect the first canonical `session.state.changed` event for the thread;
5. require its state to be `ready`.

Expected current result:

- the collector reaches its one-second failure bound;
- no `session.state.changed` event is emitted;
- the source reason is that the resumed context has no `activeTurnId`, so the idle branch is skipped.

Evidence status:

- test file committed: **observed**;
- source behavior: **source-confirmed**;
- target test execution: **not run**;
- current expected failure: **inferred from source**, not reported as an executed failure;
- branch-push workflow runs for the test commit: none returned.

## Repair candidates

### Candidate A: thread-scoped idle reconciliation

When OpenCode reports idle:

- if `activeTurnId` exists, retain the precise `turn.completed` event;
- otherwise emit `session.state.changed` with `state: ready`.

Benefits:

- small adapter-local change;
- no OpenCode cursor format change;
- directly expresses provider session truth;
- clears stale T3 running state after adapter reconstruction.

Risk that must be tested:

A delayed idle event from a replaced adapter/session may be thread-scoped but no longer applicable. If provider-instance identity is reused during hot reload and the canonical event lacks provider-session affinity, the fallback could clear a newer turn.

Required guard evidence:

- old OpenCode session idle after replacement must not clear a newer session's active turn;
- provider session ID, adapter generation, or another continuation identity must distinguish the events when required.

### Candidate B: durable active-turn identity

Version the OpenCode resume cursor or related persisted runtime payload to carry the active T3 turn ID while work is running. Restore it into the rebuilt adapter context so idle can emit turn-specific completion.

Benefits:

- preserves the existing turn-specific completion contract;
- T3's lifecycle guard rejects completion for a different newer turn;
- avoids a generic ready transition when exact identity is available.

Costs and open questions:

- cursor versioning and migration;
- active-turn ID must be refreshed on send and cleared on completion/error/abort;
- the provider must deliver current idle status after subscription or recovery needs an explicit status query;
- a stale cursor can cause duplicate old-turn completion, which must remain idempotent;
- pending approval/question identity remains a separate in-memory recovery problem.

### Current decision

Do not choose yet.

Candidate A is the smallest repair but needs replacement-ordering proof. Candidate B preserves stronger identity but changes persistence and still depends on an idle observation after resume.

## Next target tests

1. **Resumed idle fallback** — the prepared test.
2. **Normal active turn** — busy/idle with an active turn emits exactly one applicable `turn.completed` and no redundant thread-scoped ready event.
3. **Repeated steering** — initial prompt plus two steering prompts reuse or explicitly replace one turn and converge on ready.
4. **Adapter replacement** — old session idle after replacement cannot clear the new session's active turn.
5. **Interrupt without later idle** — interruption reaches an explicit settled state rather than relying on incidental provider status.
6. **Interrupt with later idle** — no duplicate or conflicting completion.
7. **Pending request after resume** — permission/question response is reconstructed with exact affinity or rejected as explicitly expired.

## Negative results and limits

- No target-native test was executed.
- No production file was changed.
- No target pull request was opened.
- No claim is made that the public steering reports share one root cause.
- A generic idle-to-ready patch is not yet considered safe across provider hot reload.
- Restoring an OpenCode session ID does not restore pending approval/question maps.
- No browser, mobile, desktop, remote, or live-data trial was performed.
- No upstream contact occurred.

## Current recommendation

Run the prepared target test first. Then add the adapter-replacement ordering test before applying Candidate A. If replacement affinity cannot be proved cheaply, prefer a turn-specific persistence design or add provider-session/generation identity to the canonical lifecycle boundary.

Keep the campaign claimed until at least one target-native result and one repair-safety case are durable.
