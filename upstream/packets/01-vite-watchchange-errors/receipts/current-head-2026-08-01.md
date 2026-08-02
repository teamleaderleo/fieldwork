# Current-head receipt — 2026-08-03

## Review fence

- Work class: owned-fork source candidate
- Public Vite base and current main: `e6b6b167afa0a80548829d1f24a0712f9194389a`
- Canonical source: `ba8ac979ee91c77fdd91304ccde38942e9752133`
- Canonical branch: `fix/fieldwork-25-watchchange-error-isolation`
- Canonical source PR: `teamleaderleo/vite#4`
- Diff inventory: exactly three files, 425 additions, 18 deletions
- Packet PR: `teamleaderleo/fieldwork#438`

Any source or material public-base movement expires this receipt.

## Source repairs

The canonical source was restored from a temporary five-file carrier head to the clean three-file product fence.

Ordinary type checking then exposed and caused repair of:

1. an optional hook passed to `getHookHandler` without narrowing;
2. an optional plugin flag leaking from a helper declared to return `boolean`.

Final head `ba8ac979...` contains only the narrow typing corrections plus the selected watcher lifecycle repair.

## Exact source mechanism

- watcher events call an internal notification path;
- applicable plugin hooks run in existing parallel groups with existing sequential barriers;
- each hook's synchronous throw or asynchronous rejection is reported individually;
- every applicable hook settles before Vite-owned invalidation/HMR proceeds;
- asynchronous hooks remain registered for close-time waiting;
- environment-level infrastructure rejection is separately settled and reported;
- the documented direct `pluginContainer.watchChange()` path remains fail-fast.

## Final workflows

### Zizmor

- Run `30753769710`
- Result: **success**

### CI

- Run `30753769684`
- Result: **success**

Passed jobs:

- changed-file discovery;
- lint, build, formatting, typecheck, documentation tests, and workflow checks;
- Ubuntu Node 20 Build&Test;
- Ubuntu Node 22 Build&Test;
- Ubuntu Node 24 Build&Test;
- Ubuntu Node 26 Build&Test;
- macOS Node 24 Build&Test;
- Windows Node 24.15.0 Build&Test;
- `Build & Test Passed or Skipped` aggregate.

The `Build & Test Failed` aggregate skipped.

Every Build&Test job completed build, unit, ordinary serve, bundled-development serve, and build tests.

Preview run `30753769692` skipped as expected for the internal PR.

## Complete-diff pre-review

Result: `ACCEPT`.

Confirmed:

- per-plugin errors cannot end sibling notification work;
- sequential barriers preserve ordering;
- all environments settle before later watcher work;
- direct public hook behavior remains unchanged;
- generated declarations do not expose the internal method;
- tests cover change/add/unlink, refreshed cache content, dual rejection, blocked-sibling ordering, sequential barriers, and synchronous throws;
- source contains no workflow, trigger, dependency, lockfile, generated output, or Fieldwork-only file;
- no blocking lifecycle, compatibility, or test defect was found.

## Prior art and overlap

Merged Vite PR `#22188` added listener-level logging but did not continue the inner watcher transaction or settle sibling hooks.

Current public main remains the exact base. Fresh issue/PR searches found no open overlapping repair at this receipt.

## Disposition

`ACCEPT`

The exact source is technically ready for human review. Repeat current-main, duplicate, and contribution-policy checks before any authorized public action.

Public upstream interactions for Unit 01: zero.
