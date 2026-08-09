// Prepared target test for Fieldwork #744.
// Intended insertion point: crates/tauri/src/event/listener.rs #[cfg(test)] module.

#[test]
fn js_filter_predicate_runs_without_js_listener_registry_lock() {
  use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc,
  };

  let app = crate::test::mock_app();
  let webview_window = crate::WebviewWindowBuilder::new(&app, "filter-lock", Default::default())
    .build()
    .unwrap();
  let webview = webview_window.as_ref();

  let listeners = Listeners::default();
  let listeners_from_filter = listeners.clone();
  let event = crate::EventName::new("filter-lock".to_owned()).unwrap();
  let id = listeners.next_event_id();
  listeners.listen_js(
    event.as_str_event(),
    webview.label(),
    EventTarget::webview(webview.label()),
    id,
  );
  let args = EmitArgs::new(event.as_str_event(), &()).unwrap();

  let lock_was_available = Arc::new(AtomicBool::new(false));
  let lock_was_available_from_filter = lock_was_available.clone();

  listeners
    .emit_js_filter(
      std::iter::once(webview),
      &args,
      Some(move |_: &EventTarget| {
        lock_was_available_from_filter.store(
          listeners_from_filter.inner.js_event_listeners.try_lock().is_ok(),
          Ordering::SeqCst,
        );
        true
      }),
    )
    .unwrap();

  assert!(
    lock_was_available.load(Ordering::SeqCst),
    "JS filter predicate ran while the JS listener registry mutex was held"
  );
}
