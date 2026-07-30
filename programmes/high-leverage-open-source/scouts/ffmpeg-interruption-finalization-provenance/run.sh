#!/usr/bin/env bash
set -u -o pipefail

case_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
results_dir="${RESULTS_DIR:-$case_dir/results/latest}"
ffmpeg_bin="${FFMPEG_BIN:-ffmpeg}"
ffprobe_bin="${FFPROBE_BIN:-ffprobe}"
source_dir="${FFMPEG_SOURCE_DIR:-}"

rm -rf "$results_dir"
mkdir -p "$results_dir"

"$ffmpeg_bin" -version >"$results_dir/ffmpeg-version.txt" 2>&1
"$ffprobe_bin" -version >"$results_dir/ffprobe-version.txt" 2>&1
if [[ -n "$source_dir" && -f "$source_dir/ffbuild/config.log" ]]; then
  cp "$source_dir/ffbuild/config.log" "$results_dir/config.log"
fi

failures=0

expect_eq() {
  local name="$1" actual="$2" expected="$3"
  if [[ "$actual" != "$expected" ]]; then
    printf 'ASSERTION FAILED: %s expected=%s actual=%s\n' "$name" "$expected" "$actual" >&2
    failures=$((failures + 1))
  else
    printf 'assertion passed: %s=%s\n' "$name" "$actual"
  fi
}

expect_file() {
  local name="$1" path="$2"
  if [[ ! -s "$path" ]]; then
    printf 'ASSERTION FAILED: %s missing-or-empty path=%s\n' "$name" "$path" >&2
    failures=$((failures + 1))
  else
    printf 'assertion passed: %s size=%s\n' "$name" "$(stat -c '%s' "$path")"
  fi
}

expect_absent() {
  local name="$1" path="$2"
  if [[ -e "$path" ]]; then
    printf 'ASSERTION FAILED: %s unexpectedly exists path=%s size=%s\n' \
      "$name" "$path" "$(stat -c '%s' "$path")" >&2
    failures=$((failures + 1))
  else
    printf 'assertion passed: %s absent\n' "$name"
  fi
}

wait_for_output_growth() {
  local path="$1"
  for _ in $(seq 1 150); do
    if [[ -f "$path" ]] && [[ "$(stat -c '%s' "$path")" -ge 8192 ]]; then
      return 0
    fi
    sleep 0.1
  done
  printf 'output did not reach the packet-written threshold: %s\n' "$path" >&2
  return 1
}

probe_file() {
  local input="$1" prefix="$2"
  "$ffprobe_bin" \
    -v error \
    -show_entries 'format=format_name,duration,size,start_time:stream=index,codec_name,codec_type,duration,nb_frames' \
    -of json \
    "$input" \
    >"$results_dir/${prefix}-probe.json" \
    2>"$results_dir/${prefix}-probe.stderr"
}

run_long_encode() {
  local output="$1" log="$2"
  "$ffmpeg_bin" \
    -nostdin \
    -hide_banner \
    -loglevel info \
    -re \
    -f lavfi \
    -i 'testsrc2=size=320x240:rate=30' \
    -t 20 \
    -an \
    -c:v mpeg4 \
    -q:v 5 \
    -y \
    "$output" \
    >"$log" 2>&1 &
  encode_pid=$!
}

completed="$results_dir/completed.mp4"
"$ffmpeg_bin" \
  -nostdin \
  -hide_banner \
  -loglevel info \
  -f lavfi \
  -i 'testsrc2=size=320x240:rate=30' \
  -t 2 \
  -an \
  -c:v mpeg4 \
  -q:v 5 \
  -y \
  "$completed" \
  >"$results_dir/completed.log" 2>&1
completed_status=$?
probe_file "$completed" completed
completed_probe_status=$?

sigint_output="$results_dir/direct-sigint.mp4"
run_long_encode "$sigint_output" "$results_dir/direct-sigint.log"
if ! wait_for_output_growth "$sigint_output"; then
  failures=$((failures + 1))
fi
sleep 1
kill -INT "$encode_pid"
wait "$encode_pid"
sigint_status=$?
probe_file "$sigint_output" direct-sigint
sigint_probe_status=$?

sigkill_output="$results_dir/direct-sigkill.mp4"
run_long_encode "$sigkill_output" "$results_dir/direct-sigkill.log"
if ! wait_for_output_growth "$sigkill_output"; then
  failures=$((failures + 1))
fi
sleep 1
kill -KILL "$encode_pid"
wait "$encode_pid" 2>/dev/null
sigkill_status=$?
probe_file "$sigkill_output" direct-sigkill
sigkill_probe_status=$?

staged_tmp="$results_dir/staged.tmp.mp4"
staged_final="$results_dir/staged-final.mp4"
run_long_encode "$staged_tmp" "$results_dir/staged-sigint.log"
if ! wait_for_output_growth "$staged_tmp"; then
  failures=$((failures + 1))
fi
sleep 1
kill -INT "$encode_pid"
wait "$encode_pid"
staged_status=$?
probe_file "$staged_tmp" staged-sigint
staged_probe_status=$?
if [[ "$staged_status" -eq 0 ]]; then
  mv "$staged_tmp" "$staged_final"
fi

expect_eq completed_status "$completed_status" 0
expect_eq completed_probe_status "$completed_probe_status" 0
expect_file completed_output "$completed"

expect_eq sigint_status "$sigint_status" 255
expect_eq sigint_probe_status "$sigint_probe_status" 0
expect_file sigint_output "$sigint_output"
if ! grep -Fq 'Exiting normally, received signal 2.' "$results_dir/direct-sigint.log"; then
  printf 'ASSERTION FAILED: graceful signal log lacks normal signal exit marker\n' >&2
  failures=$((failures + 1))
fi

expect_eq sigkill_status "$sigkill_status" 137
expect_file sigkill_output "$sigkill_output"
if [[ "$sigkill_probe_status" -eq 0 ]]; then
  printf 'ASSERTION FAILED: hard-killed ordinary MP4 unexpectedly parsed successfully\n' >&2
  failures=$((failures + 1))
else
  printf 'assertion passed: hard-killed ordinary MP4 probe failed status=%s\n' "$sigkill_probe_status"
fi

expect_eq staged_status "$staged_status" 255
expect_eq staged_probe_status "$staged_probe_status" 0
expect_file staged_temporary_output "$staged_tmp"
expect_absent staged_final_output "$staged_final"

export RESULTS_DIR="$results_dir"
export COMPLETED_STATUS="$completed_status"
export COMPLETED_PROBE_STATUS="$completed_probe_status"
export SIGINT_STATUS="$sigint_status"
export SIGINT_PROBE_STATUS="$sigint_probe_status"
export SIGKILL_STATUS="$sigkill_status"
export SIGKILL_PROBE_STATUS="$sigkill_probe_status"
export STAGED_STATUS="$staged_status"
export STAGED_PROBE_STATUS="$staged_probe_status"
export ASSERTION_FAILURES="$failures"
python3 - <<'PY'
import json
import os
from pathlib import Path

root = Path(os.environ["RESULTS_DIR"])

def file_record(name: str) -> dict:
    path = root / name
    return {
        "exists": path.exists(),
        "size": path.stat().st_size if path.exists() else None,
    }

summary = {
    "experiment": "EXP-20260731-ffmpeg-mp4-interrupt-publication",
    "completed": {
        "process_status": int(os.environ["COMPLETED_STATUS"]),
        "probe_status": int(os.environ["COMPLETED_PROBE_STATUS"]),
        "file": file_record("completed.mp4"),
    },
    "direct_sigint": {
        "process_status": int(os.environ["SIGINT_STATUS"]),
        "probe_status": int(os.environ["SIGINT_PROBE_STATUS"]),
        "file": file_record("direct-sigint.mp4"),
    },
    "direct_sigkill": {
        "process_status": int(os.environ["SIGKILL_STATUS"]),
        "probe_status": int(os.environ["SIGKILL_PROBE_STATUS"]),
        "file": file_record("direct-sigkill.mp4"),
    },
    "staged_sigint": {
        "process_status": int(os.environ["STAGED_STATUS"]),
        "probe_status": int(os.environ["STAGED_PROBE_STATUS"]),
        "temporary_file": file_record("staged.tmp.mp4"),
        "final_file": file_record("staged-final.mp4"),
    },
    "assertion_failures": int(os.environ["ASSERTION_FAILURES"]),
}
(root / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
PY

if [[ "$failures" -ne 0 ]]; then
  printf '%s assertion(s) failed\n' "$failures" >&2
  exit 1
fi
