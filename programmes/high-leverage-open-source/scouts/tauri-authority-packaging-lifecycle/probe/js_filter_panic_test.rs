
  #[test]
  fn js_filter_panic_does_not_poison_listener_registry() {
    use std::panic::{catch_unwind, AssertUnwindSafe};

    let app = crate::test::mock_app();
    let webview_window = crate::WebviewWindowBuilder::new(&app, "filter-panic", Default::default())
      .build()
      .unwrap();
    let webview = webview_window.as_ref();

    let listeners = Listeners::default();
    let event = crate::EventName::new("filter-panic".to_owned()).unwrap();
    let id = listeners.next_event_id();
    listeners.listen_js(
      event.as_str_event(),
      webview.label(),
      EventTarget::webview(webview.label()),
      id,
    );
    let args = EmitArgs::new(event.as_str_event(), &()).unwrap();

    let first = catch_unwind(AssertUnwindSafe(|| {
      let _ = listeners.emit_js_filter(
        std::iter::once(webview),
        &args,
        Some(|_: &EventTarget| -> bool {
          panic!("intentional JS listener filter panic");
        }),
      );
    }));
    assert!(first.is_err(), "filter panic must still reach the caller");

    let registry_read = catch_unwind(AssertUnwindSafe(|| {
      listeners.has_js_listener(event.as_str_event(), |_| true)
    }));
    assert!(
      matches!(registry_read, Ok(true)),
      "JS listener registry was poisoned by filter panic"
    );
  }
