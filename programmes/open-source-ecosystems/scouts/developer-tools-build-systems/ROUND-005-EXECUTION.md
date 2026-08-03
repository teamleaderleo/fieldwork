# Developer tools and build systems — Round 005 execution

Run: https://github.com/teamleaderleo/fieldwork/actions/runs/30839352175  
Runner: ubuntu-latest  
Fieldwork trigger head: `61c3ad484f88a6e98f1a08f1e034b7e47831411e`  
Upstream contact: none; unauthorized

## In simple words

This execution checked the current Meson fork fix against its exact base, reran ShellCheck's separate sourced-function control from the correct directory, and tested Cargo's current patch behavior against the proposed broad no-fetch contract. Raw outputs are retained under `artifacts/round-005-execution/`.

## Results

| Target | Outcome | Interpretation |
| --- | --- | --- |
| Meson | success | Exact base must emit `unknown`; candidate must emit `systemd`; Python compilation and diff checks are included. |
| ShellCheck follow-up | success | The include must resolve without SC1091 and the separate sourced-function SC2031 must remain reproducible. |
| Cargo | success | Existing `patch_git` must pass; the proposed broad no-fetch contract must fail on the original-source product path; source is restored afterward. |

Evidence is `target-executed` only for rows marked `success`. This is focused Linux evidence, not each repository's complete cross-platform gate.
