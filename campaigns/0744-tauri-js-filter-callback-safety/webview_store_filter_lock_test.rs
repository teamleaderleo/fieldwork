// Prepared target test for Fieldwork #744.
// Intended insertion point: crates/tauri/src/manager/mod.rs #[cfg(test)] surface.

#[test]
fn app_emit_filter_predicate_runs_without_webview_store_lock() {
  use crate::sealed::ManagerBase;
  use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc,
  };

  let app = crate::test::mock_app();
  let webview_window = crate::WebviewWindowBuilder::new(&app, "filter-webview-lock", Default::default())
    .build()
    .unwrap();
  let webview = webview_window.as_ref();
  let manager = app.handle().manager();

  let event = crate::EventName::new("filter-webview-lock".to_owned()).unwrap();
  let id = manager.listeners.next_event_id();
  manager.listeners.listen_js(
    event.as_str_event(),
    webview.label(),
    crate::EventTarget::webview(webview.label()),
    id,
  );

  let lock_was_available = Arc::new(AtomicBool::new(false));
  let lock_was_available_from_filter = lock_was_available.clone();

  manager
    .emit_filter(
      event,
      EmitPayload::Serialize(&()),
      |_: &crate::EventTarget| {
        lock_was_available_from_filter.store(
          manager.webview.webviews.try_lock().is_ok(),
          Ordering::SeqCst,
        );
        true
      },
    )
    .unwrap();

  assert!(
    lock_was_available.load(Ordering::SeqCst),
    "public filter predicate ran while the global webview-store mutex was held"
  );
}
