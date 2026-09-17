#!/usr/bin/env bash
set -euo pipefail

root=$(git rev-parse --show-toplevel)
bevy="$root/.fieldwork/bevy"
probe="$root/programmes/high-leverage-open-source/scouts/bevy-ecs-schedule-replay/probes/deferred-failure-visibility"
expected=25368b78ce5e9b15dc770cdf2af4595602cc8a7b

test -d "$bevy/.git"
actual=$(git -C "$bevy" rev-parse HEAD)
test "$actual" = "$expected"

git -C "$bevy" diff --quiet
git -C "$bevy" diff --cached --quiet

cd "$probe"
cargo test
cargo run
