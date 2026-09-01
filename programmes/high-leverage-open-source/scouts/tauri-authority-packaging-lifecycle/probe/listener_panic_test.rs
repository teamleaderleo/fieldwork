  #[test]
  fn listener_panic_does_not_stall_future_events() {
    use std::{
      panic::{catch_unwind, AssertUnwindSafe},
      sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
      },
    };

    let listeners = Listeners::default();
    let panic_event = crate::EventName::new("panic-event".to_owned()).unwrap();

    listeners.listen(panic_event.clone(), EventTarget::Any, |_| {
      panic!("intentional listener panic")
    });

    let panicked = catch_unwind(AssertUnwindSafe(|| {
      listeners
        .emit(EmitArgs::new(panic_event.as_str_event(), &()).unwrap())
        .unwrap();
    }));
    assert!(panicked.is_err(), "listener panic should propagate to the caller");

    let after_event = crate::EventName::new("after-panic".to_owned()).unwrap();
    let fired = Arc::new(AtomicBool::new(false));
    let fired_in_handler = fired.clone();

    listeners.listen(after_event.clone(), EventTarget::Any, move |_| {
      fired_in_handler.store(true, Ordering::SeqCst);
    });
    listeners
      .emit(EmitArgs::new(after_event.as_str_event(), &()).unwrap())
      .unwrap();

    assert!(
      fired.load(Ordering::SeqCst),
      "event manager stopped dispatching after callback panic"
    );
  }
