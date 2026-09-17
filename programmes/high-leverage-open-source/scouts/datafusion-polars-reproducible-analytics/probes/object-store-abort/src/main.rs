use std::fmt;
use std::ops::Range;
use std::sync::{Arc, Mutex};

use async_trait::async_trait;
use bytes::Bytes;
use futures_util::future::{FutureExt, ready};
use futures_util::stream::BoxStream;
use object_store::buffered::BufWriter;
use object_store::memory::InMemory;
use object_store::path::Path;
use object_store::{
    CopyOptions, GetOptions, GetResult, ListResult, MultipartUpload, ObjectMeta, ObjectStore,
    PutMultipartOptions, PutOptions, PutPayload, PutResult, RenameOptions, Result as StoreResult,
    UploadPart,
};
use serde::Serialize;
use tokio::io::AsyncWriteExt;

#[derive(Debug, Default, Clone, Serialize, PartialEq, Eq)]
struct Counters {
    multipart_started: usize,
    parts_submitted: usize,
    complete_calls: usize,
    abort_calls: usize,
}

#[derive(Debug)]
struct TrackingUpload {
    counters: Arc<Mutex<Counters>>,
}

#[async_trait]
impl MultipartUpload for TrackingUpload {
    fn put_part(&mut self, _data: PutPayload) -> UploadPart {
        self.counters.lock().unwrap().parts_submitted += 1;
        ready(Ok(())).boxed()
    }

    async fn complete(&mut self) -> StoreResult<PutResult> {
        self.counters.lock().unwrap().complete_calls += 1;
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
}

impl TrackingStore {
    fn new(counters: Arc<Mutex<Counters>>) -> Self {
        Self {
            inner: InMemory::new(),
            counters,
        }
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
        self.inner.put_opts(location, payload, opts).await
    }

    async fn put_multipart_opts(
        &self,
        _location: &Path,
        _opts: PutMultipartOptions,
    ) -> StoreResult<Box<dyn MultipartUpload>> {
        self.counters.lock().unwrap().multipart_started += 1;
        Ok(Box::new(TrackingUpload {
            counters: Arc::clone(&self.counters),
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

#[derive(Debug, Clone, Copy)]
enum FinishMode {
    ExplicitAbort,
    DropOnly,
    SuccessfulShutdown,
}

impl FinishMode {
    fn label(self) -> &'static str {
        match self {
            Self::ExplicitAbort => "explicit_abort",
            Self::DropOnly => "drop_only",
            Self::SuccessfulShutdown => "successful_shutdown",
        }
    }
}

#[derive(Debug, Serialize)]
struct ScenarioReceipt {
    mode: &'static str,
    counters: Counters,
}

async fn run_scenario(mode: FinishMode) -> ScenarioReceipt {
    let counters = Arc::new(Mutex::new(Counters::default()));
    let store: Arc<dyn ObjectStore> = Arc::new(TrackingStore::new(Arc::clone(&counters)));
    let path = Path::from(format!("{}.parquet", mode.label()));

    // Capacity eight and payload twenty-four force the exact object_store 0.13.2
    // BufWriter across its multipart threshold with multiple submitted parts.
    let mut writer = BufWriter::with_capacity(store, path, 8);
    writer.write_all(&[0x5a; 24]).await.unwrap();

    match mode {
        FinishMode::ExplicitAbort => writer.abort().await.unwrap(),
        FinishMode::DropOnly => drop(writer),
        FinishMode::SuccessfulShutdown => writer.shutdown().await.unwrap(),
    }

    tokio::task::yield_now().await;
    let snapshot = counters.lock().unwrap().clone();
    ScenarioReceipt {
        mode: mode.label(),
        counters: snapshot,
    }
}

async fn collect_receipts() -> Vec<ScenarioReceipt> {
    vec![
        run_scenario(FinishMode::ExplicitAbort).await,
        run_scenario(FinishMode::DropOnly).await,
        run_scenario(FinishMode::SuccessfulShutdown).await,
    ]
}

fn assert_contract(receipts: &[ScenarioReceipt]) {
    let explicit = &receipts[0].counters;
    assert_eq!(explicit.multipart_started, 1);
    assert!(explicit.parts_submitted > 0);
    assert_eq!(explicit.abort_calls, 1);
    assert_eq!(explicit.complete_calls, 0);

    let dropped = &receipts[1].counters;
    assert_eq!(dropped.multipart_started, 1);
    assert!(dropped.parts_submitted > 0);
    assert_eq!(dropped.abort_calls, 0);
    assert_eq!(dropped.complete_calls, 0);

    let completed = &receipts[2].counters;
    assert_eq!(completed.multipart_started, 1);
    assert!(completed.parts_submitted > 0);
    assert_eq!(completed.abort_calls, 0);
    assert_eq!(completed.complete_calls, 1);
}

#[tokio::main]
async fn main() {
    let receipts = collect_receipts().await;
    assert_contract(&receipts);
    println!("{}", serde_json::to_string_pretty(&receipts).unwrap());
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn explicit_abort_drop_and_success_have_distinct_receipts() {
        let receipts = collect_receipts().await;
        assert_contract(&receipts);
    }
}
