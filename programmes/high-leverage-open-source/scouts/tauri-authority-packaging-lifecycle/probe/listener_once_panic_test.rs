
  #[test]
  fn once_listener_panic_still_cleans_up_before_unwind_resumes() {
    use std::{
      panic::{catch_unwind, AssertUnwindSafe},
      sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
      },
    };

    let listeners = Listeners::default();
    let event = crate::EventName::new("once-panic".to_owned()).unwrap();

    listeners.once(event.clone(), EventTarget::Any, |_event| {
      panic!("intentional once listener panic");
    });

    let first = catch_unwind(AssertUnwindSafe(|| {
      listeners
        .emit(EmitArgs::new(event.as_str_event(), &()).unwrap())
        .unwrap();
    }));
    assert!(first.is_err(), "once-listener panic must still reach the caller");

    {
      let handlers = listeners
        .inner
        .handlers
        .lock()
        .expect("once-listener panic poisoned the handler mutex");
      assert!(
        handlers.get(&event).map(|h| h.is_empty()).unwrap_or(true),
        "panicking once listener remained registered after unwind"
      );
    }

    let delivered = Arc::new(AtomicBool::new(false));
    let delivered_clone = delivered.clone();
    listeners.listen(event.clone(), EventTarget::Any, move |_event| {
      delivered_clone.store(true, Ordering::SeqCst);
    });
    listeners
      .emit(EmitArgs::new(event.as_str_event(), &()).unwrap())
      .unwrap();

    assert!(
      delivered.load(Ordering::SeqCst),
      "event manager did not recover after a panicking once listener"
    );
  }
