# Web Tooling and Runtime Correctness

## In simple words

Find where build, browser, parser, formatter, and runtime tooling loses source or state, invalidates incorrectly, leaks resources, disagrees across modes, or performs badly on realistic projects.

- Programme hub: #15
- State: `ready`
- Coordinator: unclaimed
- Upstream contact: unauthorized

## Ready scouts

- #25 — Vite plugin, HMR, and invalidation behavior
- #26 — Playwright retry, teardown, and artifact lifecycle
- #27 — Biome transform and fix safety across owned projects

## Current decision

Run scouts independently against pinned revisions and controlled projects. Promote only reduced correctness, isolation, compatibility, resource, performance, or integration findings.
