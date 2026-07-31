# Current-main baseline and cleanup repair

Date: 2026-07-31  
Fieldwork issue: #276  
Fieldwork PR: #278  
Linux issue: `teamleaderleo/linux-fieldwork` #227  
Canonical Linux baseline: draft PR #255  
Exact Linux head: `d204faf3f38293a1171a0735bdd0224e6dd95899`  
Upstream contact authorized: `no`

## Transition

Historical Linux PR #228 executed the deterministic parent/final replacement matrix successfully at exact head `dabe79cefb6062e20dc6201556b5f541a8470bbc`. Linux Fieldwork CI run `30587406344` passed 232 tests. PR #228 then closed without merge after its byte-equivalent behavior test moved to current-main PR #255.

The first current-main PR #255 head `e70674ab22ba67b77982b5fbe19735dcb04cb449` passed Linux Fieldwork CI `30593222539` / 735. Review `4824617051` found that the carried suite still lacked the cleanup condition required by the predecessor review: the optimized child inherited temporary-directory selection, and no suite-level inventory proved that ordinary or optimized execution left no residue.

## Repair

Linux head `d204faf3...` adds:

- `tests/test_caching_proxy_parent_swap_cleanup.py`;
- `investigations/caching-proxy-parent-swap-race/artifacts/cleanup-gate.md`.

The test runs the complete suite under dedicated ordinary and optimized temporary roots. It sets `TMPDIR`, `TEMP`, and `TMP`, disables bytecode writes, requires each runtime root to be empty after completion, and verifies that top-level `complete-*` plus relevant `__pycache__` checkout inventory remains unchanged.

## Evidence classes

- Reproduced pathname behavior at `dabe79ce...`: `target-executed`.
- Prior current-main full gate at `e70674ab...`: `full-gate` for that head, excluding the later cleanup condition.
- Cleanup gate at `d204faf3...`: `target-test-prepared` until exact-head Linux CI runs.
- Fieldwork finding reconciliation at this head: evidence/documentation update pending Fieldwork integrity.

## Clearing condition

1. Linux Fieldwork CI executes exact head `d204faf3...` successfully.
2. A reviewer inspects the complete four-file PR #255 diff.
3. The review confirms that both ordinary and optimized runs use the dedicated root and that empty inventories are asserted after the child exits.
4. Linux issue #227, PR #255, Fieldwork issue #276, PR #278, and the canonical finding agree on carrier, head, evidence class, and authority.

## Following transition

Land the baseline evidence record, then create one canonical descriptor-relative implementation carrier. Preserve cache permissions, atomic replacement, readonly behavior, framing, complete-stream validation, retry, post-commit behavior, cleanup, and rerun. Keep configured-root and ancestor replacement as an explicit separate trust-boundary question.
