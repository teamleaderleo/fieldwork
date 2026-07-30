# Current-head relation — Codex rollout append acknowledgement

Retrieval date: 2026-07-31  
Candidate base: `a01a2d91461a57809e944de7758477b92617ab01`  
Current read-only public source: `413492cd6c3a4d4f8dff6f406247ccda5a9d88aa`  
Candidate source: `teamleaderleo/codex#84@d8299b7fdf3aaf7ebc46d2cac840828cf97fc2a2`  
Evidence label: `Observed` source comparison  
Upstream contact authorized: `no`

## Question

Do the two public commits after the candidate base change the append-acknowledgement source fence or its owner boundary?

## Candidate fence

- `codex-rs/core/src/session/mod.rs`;
- `codex-rs/core/src/session/turn_tests.rs`;
- `codex-rs/thread-store/src/in_memory.rs`.

## Complete changed-file result

The public compare changes account-plan, authentication, rate-limit, app-server schema, backend-client, protocol permission, sandbox, TUI status, and related tests.

No changed file intersects the candidate fence.

## Interpretation

The candidate remains mechanically direct and semantically unchanged within its declared source boundary. The comparison supports the existing source conclusion and the `delivery-gate-ready` transition.

A direct child of `413492...` remains the selected delivery form so ancestry, execution, description, and independent review use one current base.

## Expiry

This relation expires when public Codex changes one of the three candidate files or changes the `LiveThread`/`ThreadStore` append contract through another source path.
