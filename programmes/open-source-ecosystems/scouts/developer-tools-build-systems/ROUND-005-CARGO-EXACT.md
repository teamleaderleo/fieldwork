# Cargo 16574 exact-version fast-path execution

Run: https://github.com/teamleaderleo/fieldwork/actions/runs/30842332925  
Job: `91782183881`  
Runner: ubuntu-latest  
Cargo packet head: `a365453b3e5925c12a775738fb836f96947efe1c`  
Upstream contact: none; unauthorized

## In simple words

This probe tested one matching path patch against an unreachable git dependency with the exact requirement `=0.1.0`. The observed exact-version fast-path state was **absent**.

- `present`: Cargo completed from the local patch without reaching the git source.
- `absent`: Cargo reached the original git source and failed there.

The focused Cargo test exited 101 after attempting to update `ssh://127.0.0.1:9/foo-dep.git`; the retained contract contains the connection-refused source failure. That product classification is valid.

## Evidence boundary

The runner did not have `rg`. The optional source-map command was guarded with `|| true`, so the product test continued, but `source-map.txt` is empty. Do not describe this run as having captured a current source map.

Raw product output, exit status, packet head, and classification are retained under `artifacts/round-005-execution/cargo-exact/`.

Evidence class: target-executed focused Linux contract; auxiliary source-map capture missing; no production source change.
