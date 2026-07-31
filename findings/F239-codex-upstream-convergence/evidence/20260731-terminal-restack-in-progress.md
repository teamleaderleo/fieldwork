# Terminal producer retention: latest-head restack in progress

Date: 2026-07-31

This note records the active restack after public Codex advanced beyond the prior current-source pin.

- latest public head inspected: `3d1d26915a303c3b4765828f973f5464f8c28c5c`;
- compare from prior terminal base `4642370542739d5dd080b0c87a9de06a6435d3db`: eleven commits ahead;
- overlap with the four terminal source files: none;
- retained verified blobs:
  - `async_watcher.rs` — `a0427969dec77d57f6bc3037108cd4be26125cd0`;
  - `async_watcher_tests.rs` — `57002ea930169d2815aed51e42bbb37f27faedc8`;
  - `process.rs` — `ca47e90159328921a3f469fd0dad72c91ef5f86a`;
  - `process_tests.rs` — `b76c9151eb9b5a42e6e6cdfe4ef4b1c0c1686f58`.

A clean base branch `fieldwork/23-terminal-source-base-3d1d269` now points at the latest inspected public head. The next transition is to materialize exactly those four blobs on that base, open a source-only draft PR, and execute the exact nine controls plus a raised-stack focused package gate.

Historical receipts remain valid for their exact trees. This note does not classify the latest-head source until the new branch and execution receipt exist.

No merge or public upstream interaction is included.