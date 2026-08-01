# Approaches

## A — Keep the earliest proven source

Source: `teamleaderleo/codex#51@30a0a9b50da5fd2f7d58ee81315e0311e84e221e` on public base `b545c94041017d000e2c8b2f6272705d21b85dfb`.

Evidence:

- run `30550323542`;
- four exact controls passed;
- `codex-thread-store` 158/158;
- complete three-file review accepted the bounded prerequisite.

Disposition: retained as prior art, retired as delivery source because the public base advanced.

## B — Execute the earliest source on a later exact pin

Carrier: `teamleaderleo/codex#52@324ddccba14b2b0934e2c56cc0cda7ca04a56e6d`.

Observed attempts:

- run `30560746088`, job `90932794178`: source transformation stopped before formatting or tests because an expected anchor was absent; exact source-test count 0; no source branch published;
- later reviewed exact-head carrier run `30582576317` supplied an execution receipt for public `97576b1794872e342450ebd577123e052ab57626`.

Disposition: retired machinery. Its failure receipt remains useful evidence that textual transforms need exact anchors and phase-specific reporting.

## C — Selected source at `a01a2d...`

Source: `teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`, parent `a01a2d91461a57809e944de7758477b92617ab01`.

Carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`.

Evidence:

- run `30583967538` completed source verification, exact fence checks, formatting, four exact append controls, complete thread-store tests, and clean source publication;
- independent review `4823945751` accepted the three-file bounded prerequisite;
- Fieldwork PR #292 and issue #239 preserve the finding and handoff.

Disposition: canonical selected predecessor in unit #435; superseded for current delivery by later direct-current materialization.

## D — Direct-current source at `464237...`

Source: `teamleaderleo/codex#97@926e0bc5a32b136f31b9eaae75e2de4abc20fa95`, direct parent `4642370542739d5dd080b0c87a9de06a6435d3db`.

Carrier: `teamleaderleo/codex#98@8161e9ee3423d78768263e8838bd6e4800178902`.

Evidence:

- run `30598744048` passed exact parent and source fences;
- formatting passed;
- four unique exact append controls passed;
- complete `codex-thread-store` package passed;
- Fieldwork PR #326 transferred the receipt.

Disposition: strongest validated predecessor and input to current reconciliation.

## E — Direct transplant onto current public source

Diagnostic PR: `teamleaderleo/codex#131`.

Base: clean branch at public `670f69416bf91c5dfd8b58669e78050b584ff053`.
Head: validated source `926e0bc5a32b136f31b9eaae75e2de4abc20fa95`.

GitHub reports the merge as conflicting. Inspection identifies current `session/mod.rs` drift, including image-preparation analytics, in the same file. A blind merge or old patch replay would risk dropping current behavior.

Disposition: rejected as a delivery path; preserved as the current conflict receipt.

## F — Semantic three-file reconstruction on current public source

Carrier: `teamleaderleo/codex#132@4bd35b35dee5649c6ba5af4c3535af2081c58bfc`.
Run: `30674601315`.
Target: `teamleaderleo/codex:fix/session-durable-append-acknowledgement`.

Method:

- exact base `670f6941...`;
- validated test-support blobs from `926e0bc5...`;
- exact-anchor semantic edits in current `session/mod.rs`;
- exact three-file product fence;
- formatting and exact tests before publication;
- one direct-child clean source commit.

Disposition: selected current approach; execution pending at packet creation.

## G — Expand this unit into typed certainty, retry, or compaction

Potential implementation: replace `bool` with typed persistence certainty and immediately consume it in receipt, retry, replay, or compaction logic.

Disposition: rejected for unit 23. That expansion changes policy and identity ownership, exceeds the three-file prerequisite, and requires separate tests and review.
