# Upstream pull-request draft — <title>

Draft status: `ready | issue first | not ready`  
Proposed head: `<owned fork and branch>`  
Proposed base: `<upstream branch and exact base>`  
Public interaction authorized: `no | exact authority`

---

## Summary

<One to three bullets describing the user-visible or contract-level change.>

## Problem

<Explain the current behavior, consequence, and governing invariant.>

## Change

<Explain the implementation at the owning boundary. Mention important failure, cleanup, ordering, or compatibility behavior.>

## Tests

- `<exact focused test or command>`
- `<ordinary gate>`
- `<platform or integration control>`

## Compatibility

- public API:
- existing behavior retained:
- platform or runtime notes:
- performance or allocation notes:
- migration or rollback:

## Alternatives considered

- `<alternative and why the submitted direction is narrower or safer>`

## Limits

- `<important untested or intentionally excluded path>`

## Related work

- `<public issue or PR links>`

---

## Submission checklist

- [ ] Branch is a direct child or clean rebase of a recent upstream head.
- [ ] Diff contains only product source, target-native tests, required generated output, and unavoidable dependency changes.
- [ ] Fieldwork wording, temporary workflows, publishers, receipts, and evidence-only files are absent.
- [ ] Every changed file was reviewed at the exact proposed head.
- [ ] Focused regression fails on baseline and passes on candidate where practical.
- [ ] Project-declared ordinary gates ran or missing gates are stated plainly.
- [ ] Current duplicate and overlap search is complete.
- [ ] Commit history and title follow target conventions.
- [ ] Target contribution and AI-disclosure policies were checked at filing time.
- [ ] Exact user authorization to open the pull request is recorded.
