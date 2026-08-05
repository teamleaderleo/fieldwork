# Approaches

## A — Keep the earliest proven source

Source: `teamleaderleo/codex#51@30a0a9b50da5fd2f7d58ee81315e0311e84e221e` on public base `b545c94041017d000e2c8b2f6272705d21b85dfb`.

Evidence: run `30550323542`, four exact controls, full thread-store suite, and accepted bounded review.

Disposition: retained as prior art; retired as a delivery source because the public base advanced.

## B — Execute the earliest source on a later exact pin

Carrier: `teamleaderleo/codex#52@324ddccba14b2b0934e2c56cc0cda7ca04a56e6d`.

Observed attempts:

- run `30560746088`, job `90932794178`: transformation stopped before formatting or tests because an expected anchor was absent; zero source tests ran and no source branch published;
- later run `30582576317` supplied an exact-pin receipt for public `97576b1794872e342450ebd577123e052ab57626`.

Disposition: retired machinery. The failed run remains evidence that transforms require exact anchors and phase-specific receipts.

## C — Selected predecessor at `a01a2d...`

Source: `teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`, parent `a01a2d91461a57809e944de7758477b92617ab01`.

Carrier: `teamleaderleo/codex#80@401c2e5e6a37730aae3e8da95591cc6f56655cfc`.

Evidence: run `30583967538`, exact fences, formatting, four exact controls, full thread-store package, clean publication, and review `4823945751`.

Disposition: canonical predecessor for Fieldwork #435; superseded by later current-base materialization.

## D — Direct-current predecessor at `464237...`

Source: `teamleaderleo/codex#97@926e0bc5a32b136f31b9eaae75e2de4abc20fa95`, direct parent `4642370542739d5dd080b0c87a9de06a6435d3db`.

Carrier: `teamleaderleo/codex#98@8161e9ee3423d78768263e8838bd6e4800178902`.

Evidence: run `30598744048`, exact parent and source fences, formatting, four exact controls, and complete thread-store package.

Disposition: strongest validated predecessor and input to current reconciliation.

## E — Direct transplant onto current public source

Diagnostic PR: `teamleaderleo/codex#131`.

Base: public `670f69416bf91c5dfd8b58669e78050b584ff053`.
Head: predecessor `926e0bc5a32b136f31b9eaae75e2de4abc20fa95`.

GitHub reports a conflict in `session/mod.rs`. A blind merge or old patch replay could drop current image-preparation analytics and other session changes.

Disposition: rejected as a delivery path; preserved as the conflict receipt.

## F — Semantic three-file reconstruction on current public source

Carrier: `teamleaderleo/codex#132@4bd35b35dee5649c6ba5af4c3535af2081c58bfc`.
Run/job: `30674601315` / `91299123673`.
Target: `teamleaderleo/codex:fix/session-durable-append-acknowledgement`.

Method:

- exact base `670f6941...`;
- validated test-support blobs from `926e0bc5...`;
- exact-anchor semantic edits in current `session/mod.rs`;
- exact three-file product fence;
- format check;
- list-and-resolve one exact full test name for each selector;
- execute four controls with `--exact` and require `4/4`;
- execute the full thread-store package;
- publish one direct-child source commit.

Observed result:

- generated/tested head `06971a3a2b95d70a809472bfbd6fe7884063a563`;
- exact controls `4/4`;
- thread-store `163/163`;
- formatting passed;
- current branch head rewritten to `16cb14688dac752a5a13c180e94355b199f240a7` from the same parent;
- all three product blob SHAs identical between tested and current heads;
- owned source review `teamleaderleo/codex#136`, review `4841949952`, no code findings.

Disposition: selected approach completed successfully. Carrier #132 is execution-only and may be retired after receipt transfer.

## G — Treat channel delivery as durability

Potential implementation: infer persistence from raw-response emission, task completion, or channel delivery.

Disposition: rejected. The implementation deliberately emits raw response items after the persistence attempt even when acknowledgement is false. Delivery and durability are separate facts.

## H — Expand this unit into typed certainty, retry, or compaction

Potential implementation: replace `bool` with typed persistence certainty and consume it immediately in receipt, retry, replay, or compaction logic.

Disposition: rejected for unit 23. That changes policy and identity ownership, exceeds the bounded prerequisite, and requires separate tests and review.