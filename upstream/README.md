# Upstream contribution packets

## In simple words

Issue #435 is the priority-zero backlog. Each numbered unit gets one durable packet in this directory so a new worker can continue from GitHub alone, without finding an old chat.

The packet records the technical result, exact source and tests, approaches tried and rejected, current blockers, proposed upstream issue text, proposed upstream pull-request text, and the clean branch or patch series that would eventually be submitted.

Public upstream contact remains unauthorized unless the user explicitly authorizes the exact interaction.

## Canonical surfaces

- backlog and routing: [`teamleaderleo/fieldwork#435`](https://github.com/teamleaderleo/fieldwork/issues/435)
- stable unit numbers and assigned paths: [`INDEX.md`](./INDEX.md)
- per-unit packets: [`packets/`](./packets/)
- reusable packet files: [`templates/`](./templates/)
- general repository rules: [`../START_HERE.md`](../START_HERE.md), [`../AGENTS.md`](../AGENTS.md), and [`../REVIEWING.md`](../REVIEWING.md)

The Fieldwork packet is the durable research and proposal record. The clean product source normally lives in the owned fork of the target repository.

## Starting a fresh chat

A user should be able to give only the unit number:

> Take upstream unit `<NN>` from `teamleaderleo/fieldwork#435`. Read the repository instructions, `upstream/README.md`, `upstream/INDEX.md`, and every linked issue, pull request, branch, test, and prior-art record for that unit. Work only on that unit. Create or update its assigned packet directory and the clean target-source branch when possible. Preserve all observations, approaches, tests, exact revisions, links, blockers, and drafts in GitHub. Do not contact public upstream. Finish with one current disposition and a continuation-ready handoff.

The worker must begin by resolving `<NN>` through `INDEX.md`. The worker should not require the user to locate a prior conversation.

## One unit, two branches

Most units use two distinct branches:

1. **Fieldwork packet branch** — owns Markdown, retained receipts, comparison notes, draft text, and links.
2. **Target-source branch** — owns only the proposed product code, target-native tests, required generated output, and unavoidable dependency or lock changes.

Never use an execution-only workflow branch as the proposed upstream source branch. Temporary workflows and publishers must be removed after receipts are transferred.

When no owned target fork exists, the packet must record:

- upstream repository and default branch;
- exact inspected upstream SHA;
- preferred owned-fork name;
- intended source branch name;
- whether the repository must be forked before direct materialization;
- a retained patch when one already exists;
- the smallest next action requiring user authority.

Do not invent a branch or claim direct-source materialization when repository access is absent.

## Assigned packet directory

Each unit owns exactly one directory:

```text
upstream/packets/<NN>-<short-slug>/
```

Create these files from `upstream/templates/`:

```text
README.md          canonical index and current handoff
DEEP_DIVE.md       source map, failure model, consequence, and selected design
APPROACHES.md      approaches tried, rejected, retained, and reopening triggers
TESTS.md           exact commands, environments, cases, receipts, and gaps
UPSTREAM_ISSUE.md  polished issue draft when an issue-first route is useful
UPSTREAM_PR.md     polished pull-request draft for the proposed source change
REVIEW.md          exact-head self-review and final human inspection guide
```

Optional retained artifacts belong beside those files:

```text
patches/           patch or patch-series files
receipts/          compact immutable execution receipts
fixtures/          small deterministic fixtures that cannot live naturally upstream
screenshots/       only when visual evidence is essential
```

Large logs, build trees, dependency caches, binaries, and copied target repositories do not belong in Fieldwork.

## Packet source of truth

`README.md` is the entry point and current handoff for the unit. It must link every other packet file and every live source, test, issue, pull request, workflow, receipt, or patch.

At minimum it records:

- unit number and title;
- current disposition: `READY`, `ISSUE FIRST`, `REPAIR`, `HOLD`, `SUPERSEDED`, or `RETIRE`;
- target repository and proposed destination;
- exact inspected upstream base;
- canonical owned source branch and exact head, or repository-admission requirement;
- proposed upstream title;
- concise contribution synopsis;
- changed-file inventory;
- exact tests and ordinary gates that ran;
- evidence limits and compatibility risk;
- duplicate and prior-art result;
- remaining work in strict order;
- upstream-contact authorization;
- latest handoff with no dependency on chat history.

Every material observation belongs in the packet or an owning GitHub issue or pull request. Chat-only findings are unfinished work.

## Deep-dive contract

`DEEP_DIVE.md` should let a careful reviewer understand the change without reading the entire investigation history. It must cover:

1. current behavior and governing invariant;
2. source entrypoints, state owners, side effects, cleanup, and failure paths;
3. deterministic reproduction or characterization;
4. consequence and claim boundary;
5. selected implementation and why it owns the failure;
6. compatibility, platform, performance, API, migration, and rollback considerations;
7. exact code and test links pinned to commit SHAs;
8. remaining uncertainty and the controls that could reverse the conclusion.

Keep extensive chronology in linked issues and reviews. Keep the deep dive focused on the current technical answer.

## Approaches ledger

`APPROACHES.md` preserves work that would otherwise be rediscovered:

- selected approach;
- viable alternatives;
- executed losing approaches;
- rejected easy answers;
- reasons each option won or lost;
- evidence that would reopen a rejected option;
- adjacent questions intentionally excluded from this unit.

A negative result is useful when it is specific enough to stop another worker from repeating the same attempt.

## Tests and receipts

`TESTS.md` separates:

- source-read claims;
- model or fixture execution;
- target-native focused execution;
- repository-declared ordinary gates;
- integration or platform execution;
- checks prepared but never run;
- failures caused by setup, runners, fixtures, or packaging rather than product behavior.

Every executed result names the exact source head, command or workflow, environment, test count or assertions, result, and material coverage limit.

A green job does not become a broader claim than the assertions that actually ran.

## Draft issue and pull request

`UPSTREAM_ISSUE.md` and `UPSTREAM_PR.md` are polished standalone drafts, not notes addressed to Fieldwork.

They should:

- use the target project's terminology;
- omit Fieldwork workflow, evidence, and internal state vocabulary;
- explain observed behavior, expected behavior, reproduction, proposed change, tests, compatibility, and limits;
- link only to material appropriate for public upstream use;
- avoid overstating severity, prevalence, adoption, platform coverage, or maintainer intent;
- disclose AI assistance only as required by the target project's current policy;
- remain unposted until exact public-contact authority is granted.

When an issue is unnecessary, `UPSTREAM_ISSUE.md` should say `not applicable — direct pull request preferred` and explain why. When a PR is premature, `UPSTREAM_PR.md` should say `not ready — issue/design discussion first` and name the missing decision.

## Branch, fork, and patch rules

Default route:

- keep the clean candidate on an owned fork branch;
- rebase it onto a recent exact public upstream head;
- link code and tests with commit-pinned GitHub URLs;
- keep the Fieldwork packet as the broader technical record;
- prepare an upstream PR from the owned fork only after authorization.

Use retained patch files when:

- the target contribution process is patch- or mailing-list-based;
- an owned fork is unavailable but a precise diff already exists;
- the patch is useful evidence for later direct materialization.

For patch-based work, record:

- exact base SHA;
- series order and subject lines;
- `git apply --check` or target-equivalent result;
- generated cover-letter draft when applicable;
- version history and reroll notes;
- which tests ran against the applied series.

Do not force a GitHub pull-request workflow onto a mailing-list project. Do not force email-patch packaging onto a normal GitHub project.

## Working sequence

For one unit:

1. read the complete packet and all linked live records;
2. inspect current public upstream source, contribution guidance, duplicates, and overlapping work;
3. reconcile the owned candidate with current upstream;
4. create or repair the clean source branch;
5. run the smallest discriminating test, then the target's ordinary gates;
6. update all packet files with exact results and pinned links;
7. review the complete candidate diff and packet claims;
8. remove temporary machinery and stale descriptions;
9. leave one explicit disposition and one exact next action;
10. update #435 with a compact handoff or blocker.

Do not open a broad new lane merely because cleanup exposes an adjacent question. Record a bounded follow-up in the packet unless it prevents the current contribution from being finished.

## Completion standard

A unit is `READY` only when the packet identifies:

- exact clean source head and upstream base;
- complete changed-file list;
- current duplicate/prior-art result;
- target-native focused tests and ordinary gates;
- compatibility risks and evidence limits;
- polished issue and PR drafts as applicable;
- complete-diff review result;
- removal of temporary workflows and evidence-only source changes;
- the exact public action still awaiting authorization.

The user's later deep dive may still find a defect. `READY` means the unit is coherent, current, independently inspectable, and no longer dependent on hidden chat context.