use std::fmt;
use std::ops::Range;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

use async_trait::async_trait;
use bytes::Bytes;
use datafusion::arrow::array::{ArrayRef, StringArray};
use datafusion::arrow::datatypes::{DataType, Field, Schema};
use datafusion::arrow::record_batch::RecordBatch;
use datafusion::dataframe::DataFrameWriteOptions;
use datafusion::prelude::{SessionConfig, SessionContext};
use futures_util::future::{FutureExt, ready};
use futures_util::stream::BoxStream;
use object_store::memory::InMemory;
use object_store::path::Path;
use object_store::{
    CopyOptions, GetOptions, GetResult, ListResult, MultipartUpload, ObjectMeta, ObjectStore,
    PutMultipartOptions, PutOptions, PutPayload, PutResult, RenameOptions, Result as StoreResult,
    UploadPart,
};
use serde::Serialize;
use tokio::sync::Notify;
use tokio::time::{sleep, timeout};
use url::Url;

#[derive(Debug, Default, Clone, Serialize, PartialEq, Eq)]
struct Counters {
    put_opts_calls: usize,
    multipart_started: usize,
    parts_submitted: usize,
    complete_calls: usize,
    abort_calls: usize,
    upload_dropped: usize,
    final_visible: bool,
}

#[derive(Debug)]
struct TrackingUpload {
    counters: Arc<Mutex<Counters>>,
    first_part: Arc<Notify>,
    release_parts: Arc<Notify>,
    block_parts: bool,
}

impl Drop for TrackingUpload {
    fn drop(&mut self) {
        self.counters.lock().unwrap().upload_dropped += 1;
    }
}

#[async_trait]
impl MultipartUpload for TrackingUpload {
    fn put_part(&mut self, _data: PutPayload) -> UploadPart {
        self.counters.lock().unwrap().parts_submitted += 1;
        self.first_part.notify_one();
        if self.block_parts {
            let release_parts = Arc::clone(&self.release_parts);
            async move {
                release_parts.notified().await;
                Ok(())
            }
            .boxed()
        } else {
            ready(Ok(())).boxed()
        }
    }

    async fn complete(&mut self) -> StoreResult<PutResult> {
        let mut counters = self.counters.lock().unwrap();
        counters.complete_calls += 1;
        counters.final_visible = true;
        Ok(PutResult {
            e_tag: None,
            version: None,
        })
    }

    async fn abort(&mut self) -> StoreResult<()> {
        self.counters.lock().unwrap().abort_calls += 1;
        Ok(())
    }
}

#[derive(Debug)]
struct TrackingStore {
    inner: InMemory,
    counters: Arc<Mutex<Counters>>,
    first_part: Arc<Notify>,
    release_parts: Arc<Notify>,
    block_parts: bool,
}

impl TrackingStore {
    fn new(block_parts: bool) -> Self {
        Self {
            inner: InMemory::new(),
            counters: Arc::new(Mutex::new(Counters::default())),
            first_part: Arc::new(Notify::new()),
            release_parts: Arc::new(Notify::new()),
            block_parts,
        }
    }

    fn snapshot(&self) -> Counters {
        self.counters.lock().unwrap().clone()
    }
}

impl fmt::Display for TrackingStore {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "TrackingStore")
    }
}

#[async_trait]
impl ObjectStore for TrackingStore {
    async fn put_opts(
        &self,
        location: &Path,
        payload: PutPayload,
        opts: PutOptions,
    ) -> StoreResult<PutResult> {
        self.counters.lock().unwrap().put_opts_calls += 1;
        let result = self.inner.put_opts(location, payload, opts).await?;
        self.counters.lock().unwrap().final_visible = true;
        Ok(result)
    }

    async fn put_multipart_opts(
        &self,
        _location: &Path,
        _opts: PutMultipartOptions,
    ) -> StoreResult<Box<dyn MultipartUpload>> {
        self.counters.lock().unwrap().multipart_started += 1;
        Ok(Box::new(TrackingUpload {
            counters: Arc::clone(&self.counters),
            first_part: Arc::clone(&self.first_part),
            release_parts: Arc::clone(&self.release_parts),
            block_parts: self.block_parts,
        }))
    }

    async fn get_opts(&self, location: &Path, options: GetOptions) -> StoreResult<GetResult> {
        self.inner.get_opts(location, options).await
    }

    async fn get_ranges(&self, location: &Path, ranges: &[Range<u64>]) -> StoreResult<Vec<Bytes>> {
        self.inner.get_ranges(location, ranges).await
    }

    fn delete_stream(
        &self,
        locations: BoxStream<'static, StoreResult<Path>>,
    ) -> BoxStream<'static, StoreResult<Path>> {
        self.inner.delete_stream(locations)
    }

    fn list(&self, prefix: Option<&Path>) -> BoxStream<'static, StoreResult<ObjectMeta>> {
        self.inner.list(prefix)
    }

    fn list_with_offset(
        &self,
        prefix: Option<&Path>,
        offset: &Path,
    ) -> BoxStream<'static, StoreResult<ObjectMeta>> {
        self.inner.list_with_offset(prefix, offset)
    }

    async fn list_with_delimiter(&self, prefix: Option<&Path>) -> StoreResult<ListResult> {
        self.inner.list_with_delimiter(prefix).await
    }

    async fn copy_opts(&self, from: &Path, to: &Path, options: CopyOptions) -> StoreResult<()> {
        self.inner.copy_opts(from, to, options).await
    }

    async fn rename_opts(&self, from: &Path, to: &Path, options: RenameOptions) -> StoreResult<()> {
        self.inner.rename_opts(from, to, options).await
    }
}

#[derive(Debug, Serialize)]
struct ScenarioReceipt {
    mode: &'static str,
    outer_task_cancelled: bool,
    elapsed_ms: u128,
    counters: Counters,
}

fn make_context(store: Arc<TrackingStore>) -> SessionContext {
    let mut config = SessionConfig::new().with_target_partitions(1);
    config.options_mut().execution.objectstore_writer_buffer_size = 8;
    let ctx = SessionContext::new_with_config(config);
    let url = Url::parse("fieldwork://bucket").unwrap();
    let store: Arc<dyn ObjectStore> = store;
    ctx.register_object_store(&url, store);
    ctx
}

fn make_batch() -> RecordBatch {
    let values = (0..4096)
        .map(|i| format!("{i:08}-{}", "x".repeat(120)))
        .collect::<Vec<_>>();
    let payload = Arc::new(StringArray::from(values)) as ArrayRef;
    let schema = Arc::new(Schema::new(vec![Field::new(
        "payload",
        DataType::Utf8,
        false,
    )]));
    RecordBatch::try_new(schema, vec![payload]).unwrap()
}

async fn run_cancelled() -> ScenarioReceipt {
    let store = Arc::new(TrackingStore::new(true));
    let ctx = make_context(Arc::clone(&store));
    let df = ctx.read_batch(make_batch()).unwrap();
    let started = Instant::now();
    let write = tokio::spawn(async move {
        df.write_parquet(
            "fieldwork://bucket/cancelled.parquet",
            DataFrameWriteOptions::new().with_single_file_output(true),
            None,
        )
        .await
    });

    timeout(Duration::from_secs(30), store.first_part.notified())
        .await
        .expect("DataFusion did not submit the first multipart part");
    write.abort();
    let join = write.await;
    let outer_task_cancelled = join
        .as_ref()
        .err()
        .is_some_and(tokio::task::JoinError::is_cancelled);
    store.release_parts.notify_waiters();

    timeout(Duration::from_secs(5), async {
        loop {
            if store.snapshot().upload_dropped > 0 {
                break;
            }
            sleep(Duration::from_millis(10)).await;
        }
    })
    .await
    .expect("multipart upload ownership did not settle after cancellation");

    let counters = store.snapshot();
    assert!(outer_task_cancelled);
    assert!(counters.multipart_started > 0);
    assert!(counters.parts_submitted > 0);
    assert_eq!(counters.complete_calls, 0);
    assert!(!counters.final_visible);

    ScenarioReceipt {
        mode: "cancel_after_first_part",
        outer_task_cancelled,
        elapsed_ms: started.elapsed().as_millis(),
        counters,
    }
}

async fn run_successful() -> ScenarioReceipt {
    let store = Arc::new(TrackingStore::new(false));
    let ctx = make_context(Arc::clone(&store));
    let df = ctx.read_batch(make_batch()).unwrap();
    let started = Instant::now();
    df.write_parquet(
        "fieldwork://bucket/success.parquet",
        DataFrameWriteOptions::new().with_single_file_output(true),
        None,
    )
    .await
    .unwrap();

    let counters = store.snapshot();
    assert!(counters.final_visible);
    assert!(counters.complete_calls > 0 || counters.put_opts_calls > 0);

    ScenarioReceipt {
        mode: "successful_publication",
        outer_task_cancelled: false,
        elapsed_ms: started.elapsed().as_millis(),
        counters,
    }
}

async fn collect_receipts() -> Vec<ScenarioReceipt> {
    vec![run_cancelled().await, run_successful().await]
}

#[tokio::main]
async fn main() {
    let receipts = collect_receipts().await;
    println!("{}", serde_json::to_string_pretty(&receipts).unwrap());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn cancellation_and_success_have_distinct_publication_receipts() {
        let receipts = collect_receipts().await;
        assert_eq!(receipts.len(), 2);
    }
}
