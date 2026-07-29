#![cfg(test)]

use std::sync::Arc;
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::time::Duration;

use rmcp::model::{
    CacheScope, ListToolsResult, PaginatedRequestParams, ServerCapabilities, ServerInfo,
    ServerNotification, Tool, ToolListChangedNotification,
};
use rmcp::service::{MaybeSendFuture, NotificationContext, Peer, RequestContext};
use rmcp::{ClientHandler, RoleClient, RoleServer, ServerHandler};
use tokio::sync::{Mutex, Notify, RwLock};

const TIMEOUT: Duration = Duration::from_secs(10);

fn catalogue(label: &str) -> ListToolsResult {
    ListToolsResult::with_all_items(vec![Tool::new(
        label.to_string(),
        format!("{label} description"),
        Arc::new(Default::default()),
    )])
    .with_ttl_ms(60_000)
    .with_cache_scope(CacheScope::Private)
}

fn catalogue_label(result: &ListToolsResult) -> String {
    result
        .tools
        .first()
        .expect("fixture catalogue should contain one tool")
        .name
        .to_string()
}

#[derive(Clone)]
struct ControlledServer {
    request_count: Arc<AtomicUsize>,
    peer: Arc<Mutex<Option<Peer<RoleServer>>>>,
    first_relist_started: Arc<AtomicBool>,
    release_first_relist: Arc<Notify>,
}

impl ControlledServer {
    fn new() -> Self {
        Self {
            request_count: Arc::new(AtomicUsize::new(0)),
            peer: Arc::new(Mutex::new(None)),
            first_relist_started: Arc::new(AtomicBool::new(false)),
            release_first_relist: Arc::new(Notify::new()),
        }
    }

    async fn notify_tool_list_changed(&self) {
        let peer = wait_for_server_peer(&self.peer).await;
        peer.send_notification(ServerNotification::ToolListChangedNotification(
            ToolListChangedNotification {
                method: Default::default(),
                extensions: Default::default(),
            },
        ))
        .await
        .expect("send tool-list-change notification");
    }
}

impl ServerHandler for ControlledServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo::new(ServerCapabilities::builder().enable_tools().build())
    }

    async fn list_tools(
        &self,
        _request: Option<PaginatedRequestParams>,
        _context: RequestContext<RoleServer>,
    ) -> Result<ListToolsResult, rmcp::ErrorData> {
        let request_number = self.request_count.fetch_add(1, Ordering::SeqCst) + 1;
        match request_number {
            1 => Ok(catalogue("catalogue_a")),
            2 => {
                self.first_relist_started.store(true, Ordering::SeqCst);
                self.release_first_relist.notified().await;
                Ok(catalogue("catalogue_b"))
            }
            3 => Ok(catalogue("catalogue_c")),
            other => Ok(catalogue(&format!("unexpected_request_{other}"))),
        }
    }

    fn on_initialized(
        &self,
        context: NotificationContext<RoleServer>,
    ) -> impl std::future::Future<Output = ()> + MaybeSendFuture + '_ {
        let peer = Arc::clone(&self.peer);
        async move {
            *peer.lock().await = Some(context.peer.clone());
        }
    }
}

#[derive(Clone)]
struct PublishingClient {
    notification_generation: Arc<AtomicU64>,
    completed_callbacks: Arc<AtomicUsize>,
    second_publication_finished: Arc<AtomicBool>,
    naive_catalogue: Arc<RwLock<Option<String>>>,
    ticketed_catalogue: Arc<RwLock<Option<String>>>,
}

impl PublishingClient {
    fn new() -> Self {
        Self {
            notification_generation: Arc::new(AtomicU64::new(0)),
            completed_callbacks: Arc::new(AtomicUsize::new(0)),
            second_publication_finished: Arc::new(AtomicBool::new(false)),
            naive_catalogue: Arc::new(RwLock::new(None)),
            ticketed_catalogue: Arc::new(RwLock::new(None)),
        }
    }

    async fn set_initial(&self, label: String) {
        *self.naive_catalogue.write().await = Some(label.clone());
        *self.ticketed_catalogue.write().await = Some(label);
    }
}

impl ClientHandler for PublishingClient {
    fn on_tool_list_changed(
        &self,
        context: NotificationContext<RoleClient>,
    ) -> impl std::future::Future<Output = ()> + MaybeSendFuture + '_ {
        let generation = self
            .notification_generation
            .fetch_add(1, Ordering::SeqCst)
            + 1;
        let current_generation = Arc::clone(&self.notification_generation);
        let completed_callbacks = Arc::clone(&self.completed_callbacks);
        let second_publication_finished = Arc::clone(&self.second_publication_finished);
        let naive_catalogue = Arc::clone(&self.naive_catalogue);
        let ticketed_catalogue = Arc::clone(&self.ticketed_catalogue);

        async move {
            let result = context
                .peer
                .list_tools(None)
                .await
                .expect("callback relist should succeed");
            let label = catalogue_label(&result);

            *naive_catalogue.write().await = Some(label.clone());
            if generation == current_generation.load(Ordering::SeqCst) {
                *ticketed_catalogue.write().await = Some(label);
            }

            if generation == 2 {
                second_publication_finished.store(true, Ordering::SeqCst);
            }
            completed_callbacks.fetch_add(1, Ordering::SeqCst);
        }
    }
}

async fn wait_for_server_peer(peer: &Mutex<Option<Peer<RoleServer>>>) -> Peer<RoleServer> {
    tokio::time::timeout(TIMEOUT, async {
        loop {
            if let Some(peer) = peer.lock().await.clone() {
                return peer;
            }
            tokio::time::sleep(Duration::from_millis(5)).await;
        }
    })
    .await
    .expect("server peer should become available")
}

async fn wait_for_bool(value: &AtomicBool, message: &'static str) {
    tokio::time::timeout(TIMEOUT, async {
        while !value.load(Ordering::SeqCst) {
            tokio::time::sleep(Duration::from_millis(5)).await;
        }
    })
    .await
    .expect(message);
}

async fn wait_for_count(value: &AtomicUsize, expected: usize, message: &'static str) {
    tokio::time::timeout(TIMEOUT, async {
        while value.load(Ordering::SeqCst) < expected {
            tokio::time::sleep(Duration::from_millis(5)).await;
        }
    })
    .await
    .expect(message);
}

#[tokio::test(flavor = "multi_thread", worker_threads = 4)]
async fn stale_relist_result_can_roll_back_application_but_not_sdk_cache() {
    let server = ControlledServer::new();
    let client = PublishingClient::new();

    let (server_transport, client_transport) = tokio::io::duplex(64 * 1024);
    let server_for_task = server.clone();
    let server_task = tokio::spawn(async move { server_for_task.serve(server_transport).await });
    let client_service = client
        .clone()
        .serve(client_transport)
        .await
        .expect("initialize client service");

    let initial = client_service
        .peer()
        .list_tools(None)
        .await
        .expect("initial list tools");
    assert_eq!(catalogue_label(&initial), "catalogue_a");
    client.set_initial("catalogue_a".to_string()).await;
    assert_eq!(server.request_count.load(Ordering::SeqCst), 1);

    server.notify_tool_list_changed().await;
    wait_for_bool(
        &server.first_relist_started,
        "first relist should reach the controlled server",
    )
    .await;

    server.notify_tool_list_changed().await;
    wait_for_bool(
        &client.second_publication_finished,
        "second relist should publish before first relist is released",
    )
    .await;

    assert_eq!(
        client.naive_catalogue.read().await.as_deref(),
        Some("catalogue_c")
    );
    assert_eq!(
        client.ticketed_catalogue.read().await.as_deref(),
        Some("catalogue_c")
    );

    server.release_first_relist.notify_one();
    wait_for_count(
        &client.completed_callbacks,
        2,
        "both relist callbacks should complete",
    )
    .await;

    assert_eq!(
        client.naive_catalogue.read().await.as_deref(),
        Some("catalogue_b"),
        "a naive callback publisher rolls back to the late stale result"
    );
    assert_eq!(
        client.ticketed_catalogue.read().await.as_deref(),
        Some("catalogue_c"),
        "a public generation ticket would reject the late stale result"
    );

    let cached = client_service
        .peer()
        .list_tools(None)
        .await
        .expect("read accepted SDK cache result");
    assert_eq!(
        catalogue_label(&cached),
        "catalogue_c",
        "the SDK cache should retain the newer accepted relist"
    );
    assert_eq!(
        server.request_count.load(Ordering::SeqCst),
        3,
        "the final list call should be served from the SDK cache"
    );

    println!(
        "sdk_cache=catalogue_c naive_application=catalogue_b ticketed_application=catalogue_c requests=3"
    );

    client_service.cancel().await.expect("cancel client service");
    server_task.abort();
}
