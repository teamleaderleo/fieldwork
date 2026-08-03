#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR=${1:?usage: probe.sh <cargo-binstall-source-dir>}
EXPECTED_HEAD=f3284c9c2dd42d52f4437bf415a5712669699999
ACTUAL_HEAD=$(git -C "$SOURCE_DIR" rev-parse HEAD)

if [[ "$ACTUAL_HEAD" != "$EXPECTED_HEAD" ]]; then
  echo "unexpected cargo-binstall head: $ACTUAL_HEAD" >&2
  exit 2
fi

INSTALLER="$SOURCE_DIR/install-from-binstall-release.sh"
if [[ ! -f "$INSTALLER" ]]; then
  echo "installer missing: $INSTALLER" >&2
  exit 2
fi

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/fakebin" "$WORK/cargo-home/bin"

cat > "$WORK/fakebin/curl" <<'EOF'
#!/bin/sh
set -eu
: "${PROBE_ARCHIVE:?PROBE_ARCHIVE is required}"
cat "$PROBE_ARCHIVE"
EOF
chmod 0755 "$WORK/fakebin/curl"

make_archive() {
  local mode=$1
  local archive=$2
  local payload="$WORK/payload-$mode"
  mkdir -p "$payload"
  cat > "$payload/cargo-binstall" <<'EOF'
#!/bin/sh
set -eu
{
  printf 'args=%s\n' "$*"
  printf 'mode=%s\n' "$(stat -c '%a' "$0")"
} > "${PROBE_RECEIPT:?PROBE_RECEIPT is required}"
EOF
  chmod "$mode" "$payload/cargo-binstall"
  tar -C "$payload" -czf "$archive" cargo-binstall
}

run_installer() {
  local installer=$1
  local archive=$2
  local receipt=$3
  local log=$4
  rm -f "$receipt" "$log" "$WORK/github-path"
  set +e
  PATH="$WORK/fakebin:$PATH" \
    PROBE_ARCHIVE="$archive" \
    PROBE_RECEIPT="$receipt" \
    BINSTALL_VERSION=v0.0.0 \
    CARGO_HOME="$WORK/cargo-home" \
    CI=1 \
    GITHUB_PATH="$WORK/github-path" \
    sh "$installer" >"$log" 2>&1
  local status=$?
  set -e
  printf '%s' "$status"
}

assert_receipt_mode() {
  local receipt=$1
  local expected=$2
  grep -Fx 'args=--self-install' "$receipt"
  grep -Fx "mode=$expected" "$receipt"
}

ARCHIVE_0755="$WORK/cargo-binstall-0755.tgz"
ARCHIVE_0644="$WORK/cargo-binstall-0644.tgz"
make_archive 0755 "$ARCHIVE_0755"
make_archive 0644 "$ARCHIVE_0644"

echo '== archive identities =='
tar -tvzf "$ARCHIVE_0755"
tar -tvzf "$ARCHIVE_0644"

echo '== current installer: executable archive =='
STATUS=$(run_installer "$INSTALLER" "$ARCHIVE_0755" "$WORK/current-0755.receipt" "$WORK/current-0755.log")
[[ "$STATUS" == 0 ]]
assert_receipt_mode "$WORK/current-0755.receipt" 755

echo '== current installer: non-executable archive =='
STATUS=$(run_installer "$INSTALLER" "$ARCHIVE_0644" "$WORK/current-0644.receipt" "$WORK/current-0644.log")
if [[ "$STATUS" == 0 ]]; then
  echo 'current installer unexpectedly executed a 0644 launcher' >&2
  cat "$WORK/current-0644.log" >&2
  exit 1
fi
if [[ -e "$WORK/current-0644.receipt" ]]; then
  echo '0644 launcher unexpectedly produced a receipt' >&2
  cat "$WORK/current-0644.receipt" >&2
  exit 1
fi
grep -E 'Permission denied|permission denied' "$WORK/current-0644.log"
printf 'observed_status=%s\n' "$STATUS"

PATCHED="$WORK/install-from-binstall-release.patched.sh"
python3 - "$INSTALLER" "$PATCHED" <<'PY'
from pathlib import Path
import sys

source = Path(sys.argv[1]).read_text()
needle = './cargo-binstall --self-install || ./cargo-binstall -y --force cargo-binstall'
replacement = 'chmod u+x ./cargo-binstall\n\n' + needle
if source.count(needle) != 1:
    raise SystemExit(f'expected one launcher execution site, found {source.count(needle)}')
Path(sys.argv[2]).write_text(source.replace(needle, replacement))
PY

echo '== patched installer: non-executable archive =='
STATUS=$(run_installer "$PATCHED" "$ARCHIVE_0644" "$WORK/patched-0644.receipt" "$WORK/patched-0644.log")
[[ "$STATUS" == 0 ]]
assert_receipt_mode "$WORK/patched-0644.receipt" 744

echo '== patched installer: executable archive =='
STATUS=$(run_installer "$PATCHED" "$ARCHIVE_0755" "$WORK/patched-0755.receipt" "$WORK/patched-0755.log")
[[ "$STATUS" == 0 ]]
assert_receipt_mode "$WORK/patched-0755.receipt" 755

echo 'RESULT current-0755=pass current-0644=permission-failure patched-0644=pass-mode-744 patched-0755=pass-mode-755'
