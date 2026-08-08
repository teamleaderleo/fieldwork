
  #[test]
  fn scope_listener_panic_does_not_stall_future_events() {
    use std::{
      panic::{catch_unwind, AssertUnwindSafe},
      sync::{
        atomic::{AtomicBool, Ordering},
        Arc,
      },
    };

    let scope = new_scope();
    let panicking_id = scope.listen(|_event| {
      panic!("intentional scope listener panic");
    });

    let first = catch_unwind(AssertUnwindSafe(|| {
      scope.allow_file("/scope-panic-first").unwrap();
    }));
    assert!(first.is_err(), "scope listener panic must still reach the caller");

    scope.unlisten(panicking_id);

    let delivered = Arc::new(AtomicBool::new(false));
    let delivered_clone = delivered.clone();
    scope.listen(move |_event| {
      delivered_clone.store(true, Ordering::SeqCst);
    });

    scope.allow_file("/scope-panic-second").unwrap();

    assert!(
      delivered.load(Ordering::SeqCst),
      "filesystem scope stopped dispatching after callback panic"
    );
  }
