use std::path::Path;
use std::sync::Arc;
use std::thread::sleep;
use std::time::{Duration, Instant};

use polars::prelude::*;
use serde::Serialize;

#[derive(Debug, Serialize)]
struct FileReceipt {
    exists: bool,
    bytes: u64,
    parquet_valid: bool,
    readable_rows: Option<usize>,
    read_error: Option<String>,
}

#[derive(Debug, Serialize)]
struct RunReceipt {
    mode: &'static str,
    cancellation_result: Option<String>,
    elapsed_ms: u128,
    file: FileReceipt,
}

#[derive(Debug, Serialize)]
struct Receipt {
    cancelled: RunReceipt,
    retry_success: RunReceipt,
}

fn build_frame(rows: usize) -> PolarsResult<DataFrame> {
    let values = (0..rows)
        .map(|i| format!("{i:08}-{}-{i:08}", "x".repeat(224)))
        .collect::<Vec<_>>();
    DataFrame::new(vec![Series::new("payload".into(), values).into()])
}

fn sink_plan(df: DataFrame, path: &Path) -> PolarsResult<LazyFrame> {
    let target = SinkDestination::File {
        target: SinkTarget::Path(PlRefPath::new(path.to_str().unwrap())),
    };
    let options = ParquetWriteOptions {
        compression: ParquetCompression::Uncompressed,
        row_group_size: Some(16_384),
        ..Default::default()
    };
    df.lazy().with_streaming(true).sink(
        target,
        FileWriteFormat::Parquet(Arc::new(options)),
        UnifiedSinkArgs::default(),
    )
}

fn inspect_file(path: &Path) -> FileReceipt {
    let metadata = std::fs::metadata(path).ok();
    let exists = metadata.is_some();
    let bytes = metadata.as_ref().map_or(0, std::fs::Metadata::len);
    if !exists || bytes == 0 {
        return FileReceipt {
            exists,
            bytes,
            parquet_valid: false,
            readable_rows: None,
            read_error: None,
        };
    }

    match std::fs::File::open(path)
        .map_err(|e| e.to_string())
        .and_then(|file| ParquetReader::new(file).finish().map_err(|e| e.to_string()))
    {
        Ok(df) => FileReceipt {
            exists,
            bytes,
            parquet_valid: true,
            readable_rows: Some(df.height()),
            read_error: None,
        },
        Err(error) => FileReceipt {
            exists,
            bytes,
            parquet_valid: false,
            readable_rows: None,
            read_error: Some(error),
        },
    }
}

fn wait_for_output(path: &Path, min_bytes: u64) {
    let deadline = Instant::now() + Duration::from_secs(30);
    loop {
        if std::fs::metadata(path).is_ok_and(|m| m.len() >= min_bytes) {
            return;
        }
        assert!(
            Instant::now() < deadline,
            "Polars did not expose local Parquet bytes before the barrier deadline"
        );
        sleep(Duration::from_millis(5));
    }
}

fn run_cancelled(df: DataFrame, path: &Path) -> PolarsResult<RunReceipt> {
    let started = Instant::now();
    let query = sink_plan(df, path)?.collect_concurrently()?;
    wait_for_output(path, 64 * 1024);
    query.cancel();
    let cancellation_result = query.fetch_blocking().err().map(|error| error.to_string());
    let file = inspect_file(path);

    assert!(
        file.exists,
        "the local final path should already exist after output begins"
    );
    assert!(
        cancellation_result.is_some(),
        "explicit cancellation should return an interrupted query result"
    );

    Ok(RunReceipt {
        mode: "cancel_after_visible_bytes",
        cancellation_result,
        elapsed_ms: started.elapsed().as_millis(),
        file,
    })
}

fn run_retry(df: DataFrame, path: &Path, expected_rows: usize) -> PolarsResult<RunReceipt> {
    let started = Instant::now();
    sink_plan(df, path)?.collect()?;
    let file = inspect_file(path);
    assert!(
        file.parquet_valid,
        "successful retry must publish a valid Parquet file"
    );
    assert_eq!(file.readable_rows, Some(expected_rows));

    Ok(RunReceipt {
        mode: "same_path_retry_success",
        cancellation_result: None,
        elapsed_ms: started.elapsed().as_millis(),
        file,
    })
}

fn collect_receipt() -> PolarsResult<Receipt> {
    let temp = tempfile::tempdir().unwrap();
    let path = temp.path().join("publication.parquet");
    let rows = 300_000;
    let df = build_frame(rows)?;

    let cancelled = run_cancelled(df.clone(), &path)?;
    let retry_success = run_retry(df, &path, rows)?;

    Ok(Receipt {
        cancelled,
        retry_success,
    })
}

fn main() -> PolarsResult<()> {
    let receipt = collect_receipt()?;
    println!("{}", serde_json::to_string_pretty(&receipt).unwrap());
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn cancellation_then_retry_has_classified_local_publication() {
        let receipt = collect_receipt().unwrap();
        assert!(receipt.cancelled.file.exists);
        assert!(receipt.cancelled.cancellation_result.is_some());
        assert!(receipt.retry_success.file.parquet_valid);
    }
}
