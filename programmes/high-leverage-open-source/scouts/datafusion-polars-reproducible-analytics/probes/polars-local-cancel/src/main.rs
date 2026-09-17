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
#[serde(rename_all = "snake_case")]
enum QueryOutcome {
    CompletedBeforeCancelRequest,
    CompletedAfterCancelRequest,
    InterruptedAfterCancelRequest,
}

#[derive(Debug, Serialize)]
struct RunReceipt {
    mode: &'static str,
    rows: usize,
    barrier_bytes: u64,
    barrier_elapsed_ms: u128,
    cancellation_requested: bool,
    outcome: QueryOutcome,
    query_error: Option<String>,
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
    DataFrame::new(rows, vec![Series::new("payload".into(), values).into()])
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

fn wait_for_visible_output(path: &Path) -> (u64, u128) {
    let started = Instant::now();
    let deadline = started + Duration::from_secs(60);
    loop {
        if let Ok(metadata) = std::fs::metadata(path) {
            if metadata.len() > 0 {
                return (metadata.len(), started.elapsed().as_millis());
            }
        }
        assert!(
            Instant::now() < deadline,
            "Polars did not expose local Parquet bytes before the barrier deadline"
        );
        sleep(Duration::from_micros(100));
    }
}

fn run_cancel_attempt(df: DataFrame, path: &Path, rows: usize) -> PolarsResult<RunReceipt> {
    let started = Instant::now();
    let query = sink_plan(df, path)?.collect_concurrently()?;
    let (barrier_bytes, barrier_elapsed_ms) = wait_for_visible_output(path);

    let (cancellation_requested, outcome, query_error) = match query.fetch() {
        Some(Ok(_)) => (false, QueryOutcome::CompletedBeforeCancelRequest, None),
        Some(Err(error)) => return Err(error),
        None => {
            query.cancel();
            match query.fetch_blocking() {
                Ok(_) => (true, QueryOutcome::CompletedAfterCancelRequest, None),
                Err(error) => (
                    true,
                    QueryOutcome::InterruptedAfterCancelRequest,
                    Some(error.to_string()),
                ),
            }
        }
    };

    Ok(RunReceipt {
        mode: "cancel_after_first_visible_bytes",
        rows,
        barrier_bytes,
        barrier_elapsed_ms,
        cancellation_requested,
        outcome,
        query_error,
        elapsed_ms: started.elapsed().as_millis(),
        file: inspect_file(path),
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
        rows: expected_rows,
        barrier_bytes: 0,
        barrier_elapsed_ms: 0,
        cancellation_requested: false,
        outcome: QueryOutcome::CompletedBeforeCancelRequest,
        query_error: None,
        elapsed_ms: started.elapsed().as_millis(),
        file,
    })
}

fn collect_receipt() -> PolarsResult<Receipt> {
    let temp = tempfile::tempdir().unwrap();
    let path = temp.path().join("publication.parquet");
    let rows = 1_000_000;
    let df = build_frame(rows)?;

    let cancelled = run_cancel_attempt(df.clone(), &path, rows)?;
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
