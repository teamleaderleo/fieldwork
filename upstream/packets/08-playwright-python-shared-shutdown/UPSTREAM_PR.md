# Upstream pull-request draft

## Title

`fix(async): shield shared shutdown from caller cancellation`

## Body

## Summary

- keep one shared async shutdown task alive across caller cancellation
- let concurrent and later callers join the same success or failure
- report an unobserved shutdown failure once through the event loop

## Maintainer notes retained outside the public body

The target repository's current guidance requests a short pull-request description and omits a test plan from the body. The public draft above follows that convention.

Before any authorized filing:

- rebase the clean three-file source onto the then-current upstream `main`;
- confirm ordinary pytest, mypy, and pre-commit gates on the exact head;
- verify no equivalent upstream issue or pull request appeared;
- decide whether the fallback loop exception message and `task` context key need target-specific wording;
- keep Fieldwork links, execution-carrier links, internal dispositions, and authority language out of the public pull request;
- add an upstream issue link only when maintainers request issue-first discussion.

## Proposed changed files

- `playwright/async_api/_context_manager.py`
- `tests/async/test_async_stop_cancellation.py`
- `tests/async/test_async_stop_exit_contract.py`

## Commit subject

`fix(async): share shutdown completion across callers`

The current clean branch has three extraction commits because GitHub file writes were used to remove stacked carrier history. Before public submission, squash or rebuild as one target-style commit when the target's review convention favors it.

## Public claim boundary

The pull request fixes shutdown ownership after caller cancellation. It preserves one cleanup operation, stable terminal outcome, and one fallback loop report for an abandoned failure. It does not claim measured browser-process leakage, frequency, or broader cancellation fixes outside `PlaywrightContextManager` shutdown.
