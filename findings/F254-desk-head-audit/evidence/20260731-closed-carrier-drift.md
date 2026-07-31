# Closed-carrier desk drift and successor repair — 2026-07-31

Canonical implementation: PR #274

Audit implementation head before this observation: `ac66ec07cf59c9fc9cde39a3aadd1fa6ceb4666b`

## Live observation

Desk audit run `30629652297`, job `91152794895`, executed the unchanged read-only evaluator and focused nine-case fixture matrix.

- focused regressions: `9/9`, passed;
- live desk comparison: failed with four `closed_active_entry` findings;
- Fieldwork integrity `30629652302`: passed.

The live findings were:

- Review Queue #213 still marked closed PR #231 at exact head `b7d64f2318c9799ebb229eaaeae275f17e0f60c5` in R3;
- Delivery Desk #160 still marked closed PR #231 at the same head in D0;
- Review Queue #213 still marked closed PR #238 at exact head `bc3a40a18890d0a0faa90630748618a15c8c99d1` in R3;
- Delivery Desk #160 still marked closed PR #238 at the same head in D0.

The audit correctly distinguished exact-head equality from active-state validity: both historical heads still matched their closed pull requests, but closed carriers cannot remain active review or delivery entries.

## Repair applied to the live desks

The evaluator, tests, workflow, and authority boundary were not changed.

Review Queue #213 now records:

- PR #356 at `4157cf22a93b9a087fa7685be602eb099aaadde6`, lane R2;
- PR #357 at `8ce5adf405cf32fb792cd75ff28d4e5aaada36b2`, lane R2.

Delivery Desk #160 now records:

- PR #356 at `4157cf22a93b9a087fa7685be602eb099aaadde6`, lane D1;
- PR #357 at `8ce5adf405cf32fb792cd75ff28d4e5aaada36b2`, lane D1;
- PR #252 remains at `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`, lane D2.

The closed historical carriers #231 and #238 remain evidence inputs for the current-main integrations but are no longer active desk markers.

## Why the successor lanes changed

PRs #356 and #357 are exact current-main integrations with green repository gates and author-account complete-diff reviews. They do not yet have eligible independent acceptance.

Therefore:

- R2 is appropriate for peer complete-diff review;
- D1 is appropriate for one remaining final-review gate;
- R3 and D0 would overstate review and merge authority.

## Expected fresh result

A fresh live audit should pass if all five active references remain open at their exact recorded heads. Any head movement, closure, merge, or issue-marker edit should produce a new observation rather than inheriting this expectation.

## Authority boundary

This record documents a coordinator repair to live routing data after technical reclassification. It does not make the evaluator a writer, grant automatic successor selection, provide independent acceptance, authorize merge, or contact upstream.
