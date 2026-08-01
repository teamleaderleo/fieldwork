# Unit 16 — Bind confirmation modification to the correlated call

## In simple words

Gemini CLI can have more than one active tool call awaiting approval. The confirmation response already carries a correlation ID for one call, yet the baseline inline and editor modification paths select `state.firstActiveCall`. That lets one call's edited arguments be derived from another active call while the write still targets the correlated call ID.

The owned candidate resolves the exact call ID, requires `AwaitingApproval`, passes that waiting call to the modifier, then re-reads the same object after asynchronous modification before rebuilding and publishing arguments. It fails closed when the call disappears, changes status, or is replaced by another approval generation.

The source candidate and 14 focused/adjacent tests are green. Promotion still needs a current-main rebase, a genuinely parallel two-call out-of-order scheduler control, the project-declared `npm run preflight`, and independent exact-head review.

## Current disposition

`REPAIR`

Last verified: `2026-08-01`  
Worker: `chatgpt:gpt-5.6-thinking`  
Priority-zero parent: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)  
Upstream contact authorized: `no`

## Contribution

- Target project: `google-gemini/gemini-cli`
- Proposed upstream destination: `google-gemini/gemini-cli:main`
- Proposed title: `fix(scheduler): bind confirmation modification to the correlated call`
- Contribution synopsis: Bind inline and editor modification authority to the call ID owned by the confirmation loop, validate the waiting generation before and after asynchronous modification, and reject stale authority instead of falling back to active-call insertion order.
- Work class: `upstream-fork research`

## Exact identities

- Public upstream base tested: [`3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`](https://redirect.github.com/google-gemini/gemini-cli/commit/3499c84f7b8e70c86600e7cd2c67a7c65a667f5e)
- Public upstream head inspected: [`f47d6c6f7a1308d81f9f57acf7d279f0928c5249`](https://redirect.github.com/google-gemini/gemini-cli/commit/f47d6c6f7a1308d81f9f57acf7d279f0928c5249)
- Owned target fork: `teamleaderleo/gemini-cli`
- Canonical source branch: [`fix/scheduler-confirmation-call-affinity`](https://github.com/teamleaderleo/gemini-cli/tree/fix/scheduler-confirmation-call-affinity)
- Canonical source head: [`b359ece8a2bd059aef870a084ab9494eff16fa8f`](https://github.com/teamleaderleo/gemini-cli/commit/b359ece8a2bd059aef870a084ab9494eff16fa8f)
- Canonical source base: [`3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`](https://github.com/teamleaderleo/gemini-cli/commit/3499c84f7b8e70c86600e7cd2c67a7c65a667f5e)
- Original clean publisher branch: [`fieldwork/confirmation-call-affinity-source`](https://github.com/teamleaderleo/gemini-cli/tree/fieldwork/confirmation-call-affinity-source)
- Fieldwork packet branch: [`p0/435-unit-16-gemini-confirmation-call-affinity`](https://github.com/teamleaderleo/fieldwork/tree/p0/435-unit-16-gemini-confirmation-call-affinity)
- Packet content head before this README synchronization: [`54502215def10a61487152f039c18d30950dd30a`](https://github.com/teamleaderleo/fieldwork/commit/54502215def10a61487152f039c18d30950dd30a)
- Final exact packet tip: recorded in the handoff comment on #435; a tracked file cannot embed the SHA of the commit containing itself.
- Execution carrier: [`teamleaderleo/gemini-cli#6`](https://github.com/teamleaderleo/gemini-cli/pull/6) at `07307db4bfbbc66acaa8f58faeb279a1f765b301`
- Evidence branch: closed [`teamleaderleo/gemini-cli#2`](https://github.com/teamleaderleo/gemini-cli/pull/2) at `a7f5cc934446849e19a08cc8f4527473ada74401`
- Superseded clean publications: `c707e267ae2053195646f00f495c159484fc6c15` and earlier publisher outputs recorded on #6.

## Current code and tests

### Product code

- [`confirmation.ts`](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.ts) — exact-ID waiting-call lookup plus post-await identity/status revalidation for inline and editor paths.

### Target-native tests

- [`confirmation.affinity.repair.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.affinity.repair.test.ts) — six focused authority controls.
- [`confirmation.test.ts`](https://github.com/teamleaderleo/gemini-cli/blob/b359ece8a2bd059aef870a084ab9494eff16fa8f/packages/core/src/scheduler/confirmation.test.ts) — eight adjacent confirmation controls with a stateful validating-to-waiting fixture.

### Required generated or dependency files

- Not applicable. The canonical source diff contains exactly three TypeScript files.

## Changed-file fence

| Path | Role | Keep upstream? |
| --- | --- | --- |
| `packages/core/src/scheduler/confirmation.ts` | production | yes |
| `packages/core/src/scheduler/confirmation.affinity.repair.test.ts` | regression | yes, subject to maintainer preference on filename/location |
| `packages/core/src/scheduler/confirmation.test.ts` | adjacent fixture correction | yes |

## Evidence summary

| Claim | Evidence class | Exact receipt | Limit |
| --- | --- | --- | --- |
| Baseline inline modification can receive `call-a` while the response owns `call-b` | `target-executed` | [PR #2 run `30505534210`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30505534210) | focused inline harness on the pinned base |
| Candidate binds inline and editor modification to `call-b` | `target-executed` | [run `30595253180`](https://github.com/teamleaderleo/gemini-cli/actions/runs/30595253180), job `91046140436` | stateful focused harness; no real scheduler instance |
| Candidate rejects removal, status loss, and generation replacement during modification | `target-executed` | same run, six focused tests | generation replacement is modeled by object replacement/correlation change |
| Adjacent confirmation behavior remains green | `target-executed` | same run, eight adjacent tests | selected files only |
| Core build and typecheck pass | `target-executed` | same run | core workspace, not full repository preflight |
| Candidate files are untouched by the five public commits after the tested base | `source-read` | [`3499c84...f47d6c6`](https://redirect.github.com/google-gemini/gemini-cli/compare/3499c84f7b8e70c86600e7cd2c67a7c65a667f5e...f47d6c6f7a1308d81f9f57acf7d279f0928c5249) | adjacent scheduler files changed and require rerun after rebase |

## Packet navigation

- [Deep dive](./DEEP_DIVE.md)
- [Approaches](./APPROACHES.md)
- [Tests and receipts](./TESTS.md)
- [Upstream issue draft](./UPSTREAM_ISSUE.md)
- [Upstream pull-request draft](./UPSTREAM_PR.md)
- [Review and human inspection guide](./REVIEW.md)

## Duplicate and prior-art result

- Search date: `2026-08-01`
- Current upstream issues/PRs searched for `firstActiveCall` confirmation modification, scheduler approval wrong-call modification, and confirmation editor correlation.
- Current upstream commits searched for confirmation call affinity.
- Equivalent implementation found: `no`
- Relationship to prior work: independent candidate developed from the owned scout/evidence chain: Fieldwork #22, Fieldwork PR #45, target hub #5, portfolio PR #269, evidence PR #2, and production carrier PR #6.

## Remaining work

Complete in this order:

1. Rebase the exact three-file candidate onto current public main (currently `f47d6c6f7a1308d81f9f57acf7d279f0928c5249`) without widening the diff.
2. Add one scheduler-level test with two simultaneously active waiting calls and out-of-order confirmation responses, proving each modifier and `updateArgs` stays with its own call.
3. Run the focused and adjacent suites, core typecheck/build, and `npm run preflight` on one immutable rebased head.
4. Obtain independent complete-diff review, repeat the duplicate search, and choose issue-first submission after explicit authority.

## Blockers and limits

- The clean source head is five public commits behind current main.
- The committed focused harness contains another waiting call but does not drive two real simultaneous confirmation loops through the scheduler.
- Full `npm run preflight` has not run at the canonical source head.
- The target contribution policy requires an existing issue and maintainer alignment before a code PR.
- Public upstream contact remains unauthorized.
- This runtime could not clone over the network, so no new local execution occurred during packet assembly; retained GitHub Actions receipts remain the execution record.

## Latest handoff

State: `REPAIR`  
Exact source head: `b359ece8a2bd059aef870a084ab9494eff16fa8f`  
Exact packet head: final branch tip recorded on #435  
Tests: `14/14` focused plus adjacent green; core posttest build, typecheck, Prettier, pre-commit ESLint, three-file fence, and clean tracked tree green in run `30595253180`  
Temporary machinery remaining: draft carrier PR #6 and its workflow on the carrier branch; canonical source branch contains no workflow  
Next worker action: rebase the three-file commit onto current upstream main and add the real parallel out-of-order scheduler control before running preflight  
Public upstream interaction: none
