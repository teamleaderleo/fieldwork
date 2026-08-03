# Developer tools and build systems — Round 005 execution

Run: https://github.com/teamleaderleo/fieldwork/actions/runs/30839352175  
Job: `91772318148`  
Runner: ubuntu-latest  
Fieldwork trigger merge head: `61c3ad484f88a6e98f1a08f1e034b7e47831411e`  
Upstream contact: none; unauthorized

## In simple words

This run established three focused results against owned forks:

1. Meson's exact base emits a dependency named `unknown`, while the candidate emits the project option value `systemd`.
2. ShellCheck's separately reduced sourced-function fixture still emits SC2031 when the include is resolved correctly, proving that it is not the literal-export bug.
3. Cargo's current `patch_git` contract passes, while a broad no-fetch expectation still reaches the original git source and fails there.

The run did not claim a complete repository gate or cross-platform coverage.

## Meson

Exact comparison base: `0b5b32e284709eb5b23ed30207fe978362d30a3d`  
Candidate checkout head: `22740b56695248262ba1900a37af2333a00aec8c`

Base output:

```json
[{"name":"unknown","required":false,"version":[">= 209"],"has_fallback":false,"conditional":false}]
```

Candidate output:

```json
[{"name":"systemd","required":false,"version":[">= 209"],"has_fallback":false,"conditional":false}]
```

The candidate also passed `python3 -m compileall -q mesonbuild` and `git diff --check`.

Disposition from this run: **target-executed focused success**. A later Meson fork run separately executed the invalid-option hardening at production source commit `3c02349af58d72eeb104b177151e7511033381a6`.

## ShellCheck sourced-function follow-up

Executed ShellCheck checkout head: `30358eeb89ae199c0371543e97318647cbd1c984`  
Invocation directory: the fixture directory  
Exit status: `1`

Output:

```text
test.bats:16:8: note: COMPREPLY was modified in a subshell. That change might be lost. [SC2031]
```

SC1091 was absent, so the source file resolved. This confirms a separate live function/include-flow false positive. The exact fixture was rehomed, with matching blobs, to ShellCheck fork PR #3.

Disposition: **target-executed focused finding; production fix not selected**.

## Cargo broad patch-source contract

Executed packet checkout head: `ab8fb9333bbb608b996a0cdc12d71e674b9fb523`

Current control:

```text
test patch::patch_git ... ok
test result: ok. 1 passed; 0 failed
```

Broad proposed no-fetch contract:

- exit status `101`;
- Cargo printed `Updating git repository ssh://127.0.0.1:9/foo-dep.git`;
- failure path: `failed to load source` → `unable to update` → loopback connection refused;
- the injected test source was restored afterward;
- `git diff --check` passed.

This proves that ordinary current `[patch]` behavior still consults the original source candidate set. It does not answer the narrower historical exact-version/single-patch fast-path question, which has its own fork probe.

Disposition: **target-executed broad negative control; production change held for design**.

## Artifact index

- `artifacts/round-005-execution/meson/baseline.json`
- `artifacts/round-005-execution/meson/candidate.json`
- `artifacts/round-005-execution/meson/candidate-head.txt`
- `artifacts/round-005-execution/shellcheck/resourced-control.txt`
- `artifacts/round-005-execution/shellcheck/exit-status.txt`
- `artifacts/round-005-execution/shellcheck/candidate-head.txt`
- `artifacts/round-005-execution/cargo/current-contract.txt`
- `artifacts/round-005-execution/cargo/proposed-contract.txt`
- `artifacts/round-005-execution/cargo/proposed-exit-status.txt`
- `artifacts/round-005-execution/cargo/packet-head.txt`

## Carrier retirement

Execution-only Fieldwork PR #592 was closed without merge. The temporary workflow is absent from `main`; the execution script and trigger are absent from `research/developer-tools-round-005`. Evidence is retained only in the canonical report branch.
