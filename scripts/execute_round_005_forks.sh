#!/usr/bin/env bash
set -uo pipefail

record="$GITHUB_WORKSPACE/fieldwork-record"
meson_repo="$GITHUB_WORKSPACE/meson"
shellcheck_repo="$GITHUB_WORKSPACE/shellcheck"
cargo_repo="$GITHUB_WORKSPACE/cargo"
artifact_root="$record/programmes/open-source-ecosystems/scouts/developer-tools-build-systems/artifacts/round-005-execution"
mkdir -p "$artifact_root/meson" "$artifact_root/shellcheck" "$artifact_root/cargo"

meson_outcome=failure
shellcheck_outcome=failure
cargo_outcome=failure

run_meson() {
  set -euo pipefail
  local out="$artifact_root/meson"
  cd "$meson_repo"
  git rev-parse HEAD > "$out/candidate-head.txt"
  git worktree add --detach "$RUNNER_TEMP/meson-base" 0b5b32e284709eb5b23ed30207fe978362d30a3d

  python3 "$RUNNER_TEMP/meson-base/meson.py" introspect --dependencies \
    "$meson_repo/fieldwork/16046/reproducer/meson.build" \
    > "$out/baseline.json"
  python3 meson.py introspect --dependencies \
    fieldwork/16046/reproducer/meson.build \
    > "$out/candidate.json"

  python3 - "$out" <<'PY'
import json
import pathlib
import sys
root = pathlib.Path(sys.argv[1])
baseline = json.loads((root / 'baseline.json').read_text())
candidate = json.loads((root / 'candidate.json').read_text())
assert len(baseline) == 1 and baseline[0]['name'] == 'unknown', baseline
assert candidate == [{
    'name': 'systemd',
    'required': False,
    'version': ['>= 209'],
    'has_fallback': False,
    'conditional': False,
}], candidate
PY
  python3 -m compileall -q mesonbuild
  git diff --check
}

run_shellcheck() {
  set -euo pipefail
  local out="$artifact_root/shellcheck"
  cd "$shellcheck_repo"
  git rev-parse HEAD > "$out/candidate-head.txt"
  cabal update
  cabal v2-build exe:shellcheck
  local bin
  bin=$(realpath "$(cabal list-bin exe:shellcheck)")
  set +e
  (
    cd fieldwork/3263/resourced
    "$bin" -x -f gcc test.bats
  ) > "$out/resourced-control.txt" 2>&1
  local status=$?
  set -e
  printf '%s\n' "$status" > "$out/exit-status.txt"
  test "$status" -ne 0
  ! grep -q 'SC1091' "$out/resourced-control.txt"
  grep -q 'SC2031' "$out/resourced-control.txt"
  git diff --check
}

run_cargo() {
  set -euo pipefail
  local out="$artifact_root/cargo"
  cd "$cargo_repo"
  git rev-parse HEAD > "$out/packet-head.txt"

  cargo test --test testsuite patch::patch_git -- --nocapture \
    > "$out/current-contract.txt" 2>&1

  python3 - <<'PY'
from pathlib import Path
path = Path('tests/testsuite/patch.rs')
text = path.read_text()
marker = '''\n#[cargo_test]\nfn patch_to_git() {'''
test = r'''

#[cargo_test]
fn config_path_patch_can_replace_unreachable_git_dependency_without_fetch() {
    let source = "ssh://127.0.0.1:9/foo-dep.git";
    let p = project()
        .file(
            "Cargo.toml",
            &format!(
                r#"
                    [package]
                    name = "cargo-patch-test"
                    version = "0.0.1"

                    [dependencies.foo-dep]
                    git = "{source}"
                "#,
            ),
        )
        .file(
            ".cargo/config.toml",
            &format!(
                r#"
                    [patch."{source}"]
                    foo-dep = {{ path = "foo-dep" }}
                "#,
            ),
        )
        .file("src/lib.rs", "pub fn local() -> bool { foo_dep::local() }")
        .file("foo-dep/Cargo.toml", &basic_manifest("foo-dep", "0.1.0"))
        .file("foo-dep/src/lib.rs", "pub fn local() -> bool { true }")
        .build();

    p.cargo("check")
        .env("CARGO_NET_RETRY", "0")
        .with_stderr_data(str![[r#"
[LOCKING] 1 package to latest compatible version
[CHECKING] foo-dep v0.1.0 ([ROOT]/foo/foo-dep)
[CHECKING] cargo-patch-test v0.0.1 ([ROOT]/foo)
[FINISHED] `dev` profile [unoptimized + debuginfo] target(s) in [ELAPSED]s

"#]])
        .run();
}
'''
if text.count(marker) != 1:
    raise SystemExit('unexpected patch_to_git marker')
path.write_text(text.replace(marker, test + marker, 1))
PY

  set +e
  cargo test --test testsuite \
    patch::config_path_patch_can_replace_unreachable_git_dependency_without_fetch \
    -- --nocapture > "$out/proposed-contract.txt" 2>&1
  local status=$?
  set -e
  printf '%s\n' "$status" > "$out/proposed-exit-status.txt"
  git checkout -- tests/testsuite/patch.rs
  test "$status" -ne 0
  grep -Eq 'failed to (load source|clone|fetch)|unable to update|Connection refused' \
    "$out/proposed-contract.txt"
  git diff --check
}

if run_meson > "$artifact_root/meson/runner.log" 2>&1; then
  meson_outcome=success
fi
if run_shellcheck > "$artifact_root/shellcheck/runner.log" 2>&1; then
  shellcheck_outcome=success
fi
if run_cargo > "$artifact_root/cargo/runner.log" 2>&1; then
  cargo_outcome=success
fi

export MESON_OUTCOME="$meson_outcome"
export SHELLCHECK_OUTCOME="$shellcheck_outcome"
export CARGO_OUTCOME="$cargo_outcome"
export ROUND005_RUN_URL="${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/actions/runs/${GITHUB_RUN_ID}"
export ROUND005_START_HEAD="$GITHUB_SHA"
python3 - "$record/programmes/open-source-ecosystems/scouts/developer-tools-build-systems/ROUND-005-EXECUTION.md" <<'PY'
import os
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
path.write_text(f'''# Developer tools and build systems — Round 005 execution

Run: {os.environ['ROUND005_RUN_URL']}  
Runner: ubuntu-latest  
Fieldwork trigger head: `{os.environ['ROUND005_START_HEAD']}`  
Upstream contact: none; unauthorized

## In simple words

This execution checked the current Meson fork fix against its exact base, reran ShellCheck's separate sourced-function control from the correct directory, and tested Cargo's current patch behavior against the proposed broad no-fetch contract. Raw outputs are retained under `artifacts/round-005-execution/`.

## Results

| Target | Outcome | Interpretation |
| --- | --- | --- |
| Meson | {os.environ['MESON_OUTCOME']} | Exact base must emit `unknown`; candidate must emit `systemd`; Python compilation and diff checks are included. |
| ShellCheck follow-up | {os.environ['SHELLCHECK_OUTCOME']} | The include must resolve without SC1091 and the separate sourced-function SC2031 must remain reproducible. |
| Cargo | {os.environ['CARGO_OUTCOME']} | Existing `patch_git` must pass; the proposed broad no-fetch contract must fail on the original-source product path; source is restored afterward. |

Evidence is `target-executed` only for rows marked `success`. This is focused Linux evidence, not each repository's complete cross-platform gate.
''')
PY

# Retire the execution carrier from Fieldwork main before publishing results.
cd "$GITHUB_WORKSPACE/fieldwork-main"
git config user.name fieldwork-bot
git config user.email fieldwork-bot@users.noreply.github.com
git rm .github/workflows/fieldwork-round-005-execution-pr.yml
git commit -m "Retire round 005 execution carrier"
git push origin HEAD:main

# Publish retained evidence to the canonical Round 005 branch and remove this script.
cd "$record"
rm -f scripts/execute_round_005_forks.sh
rm -f programmes/open-source-ecosystems/scouts/developer-tools-build-systems/ROUND-005-EXECUTION-TRIGGER.md
git config user.name fieldwork-bot
git config user.email fieldwork-bot@users.noreply.github.com
git add programmes/open-source-ecosystems/scouts/developer-tools-build-systems scripts/execute_round_005_forks.sh
git commit -m "Record round 005 fork execution"
git push origin HEAD:research/developer-tools-round-005

if [[ "$meson_outcome" != success || "$shellcheck_outcome" != success || "$cargo_outcome" != success ]]; then
  exit 1
fi
