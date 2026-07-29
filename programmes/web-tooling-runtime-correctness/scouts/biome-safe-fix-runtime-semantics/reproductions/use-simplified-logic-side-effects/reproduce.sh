#!/usr/bin/env bash
set -euo pipefail

case_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
work_file="$case_dir/actual.mjs"
before_file="$case_dir/before.txt"
after_file="$case_dir/after.txt"
trap 'rm -f "$work_file" "$before_file" "$after_file"' EXIT

cp "$case_dir/input.mjs" "$work_file"
node "$work_file" | tee "$before_file"

npx --yes @biomejs/biome@2.5.6 --version
npx --yes @biomejs/biome@2.5.6 lint "$work_file" --write --only=complexity/useSimplifiedLogicExpression

printf '\n--- rewritten source ---\n'
cat "$work_file"
printf '\n--- after ---\n'
node "$work_file" | tee "$after_file"

test "$(cat "$before_file")" != "$(cat "$after_file")"
