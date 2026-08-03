#!/usr/bin/env bash
set -euo pipefail

SOURCE_INPUT=${1:?usage: probe.sh <jj-source-dir>}
SOURCE_DIR=$(cd "$SOURCE_INPUT" && pwd)
EXPECTED_HEAD=3a650c3a68aadfa693b193ffb3176fd09b824c86
EXPECTED_BLOB=47dd3e95d1caedf638b7b74422e0dd8d13214fd1
ACTUAL_HEAD=$(git -C "$SOURCE_DIR" rev-parse HEAD)
TARGET="$SOURCE_DIR/lib/src/stacked_table.rs"

if [[ "$ACTUAL_HEAD" != "$EXPECTED_HEAD" ]]; then
  echo "unexpected Jujutsu head: $ACTUAL_HEAD" >&2
  exit 2
fi
if [[ $(git -C "$SOURCE_DIR" hash-object lib/src/stacked_table.rs) != "$EXPECTED_BLOB" ]]; then
  echo "unexpected stacked_table.rs blob" >&2
  exit 2
fi

inject_test() {
  local mode=$1
  python3 - "$TARGET" "$mode" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
mode = sys.argv[2]
source = path.read_text()
marker = '    #[test_case(false; "memory")]'
if source.count(marker) != 1:
    raise SystemExit(f'expected one insertion marker, found {source.count(marker)}')

if mode == 'current':
    test = r'''
    #[test]
    fn stacked_table_appledouble_head_is_treated_as_segment() -> TestResult {
        let temp_dir = new_temp_dir();
        let dir = temp_dir.path().to_path_buf();
        let store = TableStore::init(dir.clone(), 3);
        let head = store.get_head()?;
        let sidecar_name = format!("._{}", head.name());
        std::fs::write(dir.join("heads").join(&sidecar_name), b"appledouble")?;

        let reloaded = TableStore::load(dir, 3);
        let err = match reloaded.get_head() {
            Ok(_) => panic!("AppleDouble sidecar was unexpectedly ignored"),
            Err(err) => err,
        };
        assert!(err.to_string().contains(&sidecar_name), "{err:#}");
        Ok(())
    }

'''
elif mode == 'candidate':
    test = r'''
    #[test]
    fn stacked_table_ignores_non_segment_heads_but_preserves_corruption() -> TestResult {
        let temp_dir = new_temp_dir();
        let dir = temp_dir.path().to_path_buf();
        let store = TableStore::init(dir.clone(), 3);
        let head = store.get_head()?;
        let sidecar_name = format!("._{}", head.name());
        std::fs::write(dir.join("heads").join(&sidecar_name), b"appledouble")?;
        std::fs::write(dir.join("heads").join("g".repeat(SEGMENT_FILE_NAME_LENGTH)), b"noise")?;

        let reloaded = TableStore::load(dir.clone(), 3);
        let reloaded_head = reloaded.get_head()?;
        assert_eq!(reloaded_head.name(), head.name());

        let corrupt_name = "a".repeat(SEGMENT_FILE_NAME_LENGTH);
        std::fs::write(dir.join("heads").join(&corrupt_name), b"truncated")?;
        let reloaded = TableStore::load(dir, 3);
        let err = match reloaded.get_head() {
            Ok(_) => panic!("valid-looking corrupt head was unexpectedly ignored"),
            Err(err) => err,
        };
        assert!(err.to_string().contains(&corrupt_name), "{err:#}");
        Ok(())
    }

'''
else:
    raise SystemExit(f'unknown mode: {mode}')

path.write_text(source.replace(marker, test + marker))
PY
}

apply_candidate() {
  python3 - "$TARGET" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
source = path.read_text()
needle = '''            let head_file_name = head_entry.map_err(TableStoreError::LoadHeads)?.file_name();
            let table = self.load_table(head_file_name.to_str().unwrap().to_string())?;
            tables.push(table);'''
replacement = '''            let head_file_name = head_entry.map_err(TableStoreError::LoadHeads)?.file_name();
            let Some(table_name) = head_file_name.to_str().filter(|name| {
                name.len() == SEGMENT_FILE_NAME_LENGTH
                    && name
                        .bytes()
                        .all(|byte| matches!(byte, b'0'..=b'9' | b'a'..=b'f'))
            }) else {
                tracing::trace!(?head_file_name, "skipping invalid table head name");
                continue;
            };
            let table = self.load_table(table_name.to_owned())?;
            tables.push(table);'''
if source.count(needle) != 1:
    raise SystemExit(f'expected one head loader site, found {source.count(needle)}')
path.write_text(source.replace(needle, replacement))
PY
}

cd "$SOURCE_DIR"

echo '== current source characterization =='
inject_test current
cargo test -p jj-lib --lib stacked_table_appledouble_head_is_treated_as_segment -- --nocapture

git reset --hard "$EXPECTED_HEAD"

echo '== bounded candidate comparison =='
apply_candidate
inject_test candidate
git diff --check
cargo test -p jj-lib --lib stacked_table_ignores_non_segment_heads_but_preserves_corruption -- --nocapture

printf 'current_blob=%s\n' "$EXPECTED_BLOB"
printf 'RESULT current-sidecar=load-error candidate-sidecar=ignored candidate-nonhex=ignored candidate-valid-name-corruption=error\n'
