# Upstream packet directories

## In simple words

Each numbered contribution owns one directory listed in `../INDEX.md`. That directory is the complete continuation record for the unit.

A worker may create or update only the assigned unit directory unless the assignment explicitly includes coordinator synthesis. This keeps new chats from overwriting one another or requiring shared conversation memory.

## Creating a packet

Copy the Markdown files from `../templates/` into the exact assigned path:

```text
upstream/packets/<NN>-<short-slug>/
```

Keep filenames stable so links from issues, target pull requests, and reviews remain durable.

## Required files

- `README.md` — canonical current state and navigation
- `DEEP_DIVE.md` — technical explanation and current design
- `APPROACHES.md` — selected, losing, rejected, and deferred options
- `TESTS.md` — exact execution and evidence limits
- `UPSTREAM_ISSUE.md` — polished issue draft or explicit not-applicable result
- `UPSTREAM_PR.md` — polished pull-request draft or explicit issue-first result
- `REVIEW.md` — exact-head self-review and user deep-dive guide

## Optional directories

- `patches/` for patch or email series
- `receipts/` for compact execution receipts
- `fixtures/` for small deterministic retained inputs
- `screenshots/` only when a visual result is essential

## Link rule

Use commit-pinned links for code and tests whenever an exact head exists. Branch links may be included for convenience but never replace the pinned link in a disposition-relevant claim.

## Update rule

Update the packet during the work, not only at the end. Record:

- newly inspected source;
- a discovered duplicate or overlap;
- a disproved premise;
- a test or setup failure classification;
- a source-head move;
- a selected or rejected approach;
- a newly exposed compatibility risk;
- the exact next action.

A polished final packet should contain the current answer and concise history needed to avoid repeating failed approaches. Raw chronological chatter belongs in linked issue or pull-request comments.

## Handoff rule

Before ending a work session:

1. commit every material observation;
2. update `README.md` with the current disposition and exact heads;
3. synchronize issue and pull-request drafts with the actual candidate;
4. identify tests that ran and tests that remain;
5. link the exact code and test files;
6. state whether temporary workflows or publishers remain;
7. post a compact update to Fieldwork #435;
8. confirm that no public upstream interaction occurred unless exact authority was granted.

Another worker should be able to resume by reading the packet and linked GitHub records only.