# Cargo 16574 exact-version fast-path execution

Run: https://github.com/teamleaderleo/fieldwork/actions/runs/30842332925  
Runner: ubuntu-latest  
Cargo packet head: a365453b3e5925c12a775738fb836f96947efe1c  
Upstream contact: none; unauthorized

## In simple words

This probe tested one matching path patch against an unreachable git dependency with the exact requirement `=0.1.0`. The observed exact-version fast-path state was **absent**.

- `present`: Cargo completed from the local patch without reaching the git source.
- `absent`: Cargo reached the original git source and failed there.

Raw output and the current source map are retained under `artifacts/round-005-execution/cargo-exact/`.

Evidence class: target-executed focused Linux contract; no production source change.
