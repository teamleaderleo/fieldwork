use std::sync::Arc;
use std::sync::atomic::{AtomicBool, Ordering};
use std::time::Duration;

use anyhow::Context;
use rmcp::model::{
    CallToolRequestParams, CallToolResponse, CallToolResult, ClientRequest, ContentBlock, Request,
    ServerCapabilities, ServerInfo,
};
use rmcp::service::{PeerRequestOptions, RequestContext};
use rmcp::{ClientHandler, RoleServer, ServerHandler, ServiceError, ServiceExt};

#[derive(Clone, Default)]
struct ProbeState {
    handler_started: Arc<AtomicBool>,
    cancellation_observed: Arc<AtomicBool>,
    side_effect_completed: Arc<AtomicBool>,
}

#[derive(Clone)]
struct SlowSideEffectServer {
    state: ProbeState,
}

impl ServerHandler for SlowSideEffectServer {
    fn get_info(&self) -> ServerInfo {
        ServerInfo::new(ServerCapabilities::builder().enable_tools().build())
    }

    async fn call_tool(
        &self,
        _request: CallToolRequestParams,
        context: RequestContext<RoleServer>,
    ) -> Result<CallToolResponse, rmcp::ErrorData> {
        self.state.handler_started.store(true, Ordering::SeqCst);

        tokio::select! {
            _ = context.ct.cancelled() => {
                self.state.cancellation_observed.store(true, Ordering::SeqCst);
                Ok(CallToolResult::success(vec![ContentBlock::text("cancelled")]).into())
            }
            _ = tokio::time::sleep(Duration::from_millis(250)) => {
                self.state.side_effect_completed.store(true, Ordering::SeqCst);
                Ok(CallToolResult::success(vec![ContentBlock::text("completed")]).into())
            }
        }
    }
}

#[derive(Clone, Default)]
struct ProbeClient;

impl ClientHandler for ProbeClient {}

async fn start_pair() -> anyhow::Result<(
    rmcp::service::RunningService<rmcp::RoleClient, ProbeClient>,
    ProbeState,
)> {
    let state = ProbeState::default();
    let server = SlowSideEffectServer {
        state: state.clone(),
    };
    let (server_transport, client_transport) = tokio::io::duplex(4096);

    tokio::spawn(async move {
        let service = server.serve(server_transport).await?;
        service.waiting().await?;
        anyhow::Ok(())
    });

    let client = ProbeClient.serve(client_transport).await?;
    Ok((client, state))
}

async fn send_probe_request(
    client: &rmcp::service::RunningService<rmcp::RoleClient, ProbeClient>,
    options: PeerRequestOptions,
) -> Result<rmcp::service::RequestHandle<rmcp::RoleClient>, ServiceError> {
    client
        .send_request_with_option(
            ClientRequest::CallToolRequest(Request::new(CallToolRequestParams::new(
                "slow_side_effect".to_owned(),
            ))),
            options,
        )
        .await
}

async fn wait_until_started(state: &ProbeState) -> anyhow::Result<()> {
    tokio::time::timeout(Duration::from_secs(2), async {
        while !state.handler_started.load(Ordering::SeqCst) {
            tokio::time::sleep(Duration::from_millis(5)).await;
        }
    })
    .await
    .context("server handler did not start")?;
    Ok(())
}

async fn external_timeout_case() -> anyhow::Result<(bool, bool)> {
    let (client, state) = start_pair().await?;
    let handle = send_probe_request(&client, PeerRequestOptions::no_options()).await?;
    wait_until_started(&state).await?;

    let outer_timeout = tokio::time::timeout(Duration::from_millis(50), handle.await_response()).await;
    anyhow::ensure!(outer_timeout.is_err(), "external timeout unexpectedly received a result");

    tokio::time::sleep(Duration::from_millis(300)).await;
    let cancelled = state.cancellation_observed.load(Ordering::SeqCst);
    let side_effect = state.side_effect_completed.load(Ordering::SeqCst);

    anyhow::ensure!(!cancelled, "external timeout unexpectedly sent MCP cancellation");
    anyhow::ensure!(side_effect, "server side effect did not continue after external timeout");

    Ok((cancelled, side_effect))
}

async fn native_timeout_case() -> anyhow::Result<(bool, bool)> {
    let (client, state) = start_pair().await?;
    let handle = send_probe_request(
        &client,
        PeerRequestOptions::with_timeout(Duration::from_millis(50)),
    )
    .await?;
    wait_until_started(&state).await?;

    let result = handle.await_response().await;
    anyhow::ensure!(
        matches!(result, Err(ServiceError::Timeout { .. })),
        "native rmcp timeout did not return ServiceError::Timeout: {result:?}"
    );

    tokio::time::sleep(Duration::from_millis(100)).await;
    let cancelled = state.cancellation_observed.load(Ordering::SeqCst);
    let side_effect = state.side_effect_completed.load(Ordering::SeqCst);

    anyhow::ensure!(cancelled, "native rmcp timeout did not send MCP cancellation");
    anyhow::ensure!(!side_effect, "server side effect completed despite native cancellation");

    Ok((cancelled, side_effect))
}

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let (external_cancelled, external_side_effect) = external_timeout_case().await?;
    let (native_cancelled, native_side_effect) = native_timeout_case().await?;

    println!(
        "{{\n  \"dependency\": \"rmcp 3.0.0\",\n  \"external_timeout\": {{\n    \"cancellation_observed\": {external_cancelled},\n    \"side_effect_completed\": {external_side_effect}\n  }},\n  \"native_request_timeout\": {{\n    \"cancellation_observed\": {native_cancelled},\n    \"side_effect_completed\": {native_side_effect}\n  }}\n}}"
    );

    Ok(())
}
