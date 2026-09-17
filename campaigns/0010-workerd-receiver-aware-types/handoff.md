# Campaign 0010 Handoff

## In simple words

The research trail is now organized and the remaining work is narrow. Stensibly is protected. The workerd candidate is worth executing and reviewing, but it is not accepted or authorized for upstream publication.

```text
FIELDWORK HANDOFF
State: ready-for-synthesis
Programme: web-tooling-runtime-correctness (#15)
Target: workers-sdk ecosystem / primary code target cloudflare/workerd (#3)
Testbed: stensibly
Batch: none
Campaign: 0010 / #230
Assignment: coordinator materialization of completed receiver-research lanes
Claim scope supported: integration and interface
Integration context: lanes/L01-runtime-integration/report.md
Durable artifacts: campaigns/0010-workerd-receiver-aware-types/
In simple words: workerd enforces a receiver rule its generated declarations omit; the local application is fixed, and the fork candidate needs exact-head execution and review before any upstream pull request.
Finding: receiver-aware TypeScript declarations can represent direct workerd call semantics, while generator correctness requires provenance through overrides, generics, inheritance, and context-global extraction.
Branch candidates: 1) teamleaderleo/workerd#1 canonical candidate; 2) no second implementation candidate; 3) local wrapper/runtime regression already merged.
Evidence labels used: Documented, Observed, Inferred, Unknown
Uncertainty: exact-head focused execution, complete generated-output compatibility, and final independent review.
Dependencies discovered: current workerd contribution and AI-disclosure policy; optional maintainer direction on the submitted issue.
Decision needed: whether clearing conditions justify preparing an upstream workerd pull request.
Upstream contact authorized: no new contact; only the existing submitted issue is authorized.
```

## Retained paths

- `STATUS.md`
- `question.md`
- `lanes/L01-runtime-integration/report.md`
- `lanes/L02-typescript-tooling/report.md`
- `lanes/L03-workerd-generator/report.md`
- `synthesis.md`
- `decision.md`
- `review.md`
- `upstream-packet.md`

## Coordinator request

Review the evidence classification and disposition. Do not interpret this handoff as approval to comment upstream, open a Cloudflare pull request, merge the owned-fork candidate, or close the archival Stensibly PR.
