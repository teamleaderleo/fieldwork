#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="${CMUX_UPSTREAM_URL:-https://github.com/manaflow-ai/cmux.git}"
MAIN_SHA="${CMUX_MAIN_SHA:-e49e7cdf300ad6eff38aef21145cd1183636e76c}"
PR_HEAD_SHA="${CMUX_PR_HEAD_SHA:-1516fc0c2e64bc21772b88738377f360c53cea03}"

workdir="$(mktemp -d)"
trap 'rm -rf "$workdir"' EXIT
repo="$workdir/cmux"
mkdir -p "$repo"
git -C "$repo" init -q
git -C "$repo" remote add upstream "$UPSTREAM_URL"

printf 'target=%s\n' "$UPSTREAM_URL"
printf 'main_sha=%s\n' "$MAIN_SHA"
printf 'pr_head_sha=%s\n' "$PR_HEAD_SHA"

# Read-only fetch. Blob filtering keeps the audit bounded while merge-tree can
# still request the specific objects it needs from the promisor remote.
git -C "$repo" fetch --quiet --no-tags --filter=blob:none upstream "$MAIN_SHA" "$PR_HEAD_SHA"

main_tree="$(git -C "$repo" rev-parse "$MAIN_SHA^{tree}")"
pr_tree="$(git -C "$repo" rev-parse "$PR_HEAD_SHA^{tree}")"
printf 'main_tree=%s\n' "$main_tree"
printf 'pr_tree=%s\n' "$pr_tree"

merge_output="$workdir/merge-tree.txt"
set +e
git -C "$repo" merge-tree --write-tree "$MAIN_SHA" "$PR_HEAD_SHA" >"$merge_output" 2>&1
merge_status=$?
set -e

printf 'merge_tree_exit=%s\n' "$merge_status"
if (( merge_status == 0 )); then
  merged_tree="$(head -n 1 "$merge_output" | tr -d '[:space:]')"
  printf 'mergeable=true\n'
  printf 'merged_tree=%s\n' "$merged_tree"
  exit 0
fi

printf 'mergeable=false\n'
printf '%s\n' '--- merge-tree conflict output ---'
cat "$merge_output"
printf '%s\n' '--- conflict files ---'
sed -n 's/^CONFLICT ([^)]*): Merge conflict in //p' "$merge_output" | sort -u

# A conflict is the expected discriminator outcome, not a harness failure.
exit 0
