# Upstream pull-request draft

## Title

`fix(async): share shutdown completion across callers`

## Body

## Summary

- keep one async shutdown operation alive across caller cancellation
- let concurrent and later callers join the same terminal result
- report an abandoned shutdown failure once through the event loop

## Maintainer notes retained outside the public body

The target repository currently prefers a short pull-request description. The public draft above intentionally omits internal Fieldwork history, execution carriers, disposition language, and a long test plan.

The final implementation does **not** use `asyncio.shield`. Exact Python 3.14 execution showed that a cancelled shielded waiter can add an automatic inner-task exception report. The clean source joins the retained task through `asyncio.wait`, then awaits the completed task for its exact terminal outcome.

Before any authorized filing:

- re-check current upstream `main` and rebase if it moved from `3b7c24c3e67dc84f7b0eddd0c5fd2ca685705021`;
- rebuild or squash the seven clean commits into the target's preferred commit shape;
- re-run the final focused gate on the rebased exact head;
- verify no equivalent public issue or pull request appeared;
- decide whether `Playwright stop task failed` is the preferred diagnostic message;
- keep Fieldwork links, private-fork execution links, internal reviews, and authority language out of the public PR;
- add an issue link only if maintainers request issue-first discussion.

## Proposed changed files

- `playwright/async_api/_context_manager.py`
- `tests/async/test_async_stop_cancellation.py`
- `tests/async/test_async_stop_exit_contract.py`

## Proposed commit subject

`fix(async): share shutdown completion across callers`

## Internal validation summary

Do not paste this section into the short public body unless maintainers request details.

- deterministic upstream negative reproduction on Python 3.10 and 3.14;
- paired baseline showing only abandoned-failure observability missing;
- full repository pre-commit passed;
- wheel build passed on Python 3.10, 3.12, and 3.14;
- all 33 focused cases passed on each version;
- tracked diff hygiene passed;
- exact source is limited to three files.

## Public claim boundary

The change fixes async shutdown ownership after caller cancellation. It preserves one cleanup operation, a stable terminal result for every caller, and one fallback event-loop report for an abandoned failure.

It does not claim:

- measured production frequency;
- measured browser-process leakage;
- a fix for failed async startup task ownership;
- bounded driver-process termination;
- a general solution for every Playwright cancellation path.

No public upstream filing is authorized by this draft.
