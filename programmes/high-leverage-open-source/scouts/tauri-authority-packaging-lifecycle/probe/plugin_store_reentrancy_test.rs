
#[cfg(test)]
mod fieldwork_plugin_store_reentrancy {
  use super::*;
  use crate::plugin::Builder as PluginBuilder;
  use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc,
  };

  #[test]
  fn dynamic_plugin_setup_is_not_run_while_plugin_store_is_locked() {
    let app = crate::test::mock_app();
    let lock_was_available = Arc::new(AtomicBool::new(false));
    let lock_was_available_clone = lock_was_available.clone();

    let plugin = PluginBuilder::new("fieldwork-dynamic-outer")
      .setup(move |app, _api| {
        lock_was_available_clone.store(
          app.manager.plugins.try_lock().is_ok(),
          Ordering::SeqCst,
        );
        Ok(())
      })
      .build();

    app.handle().plugin(plugin).unwrap();

    assert!(
      lock_was_available.load(Ordering::SeqCst),
      "dynamic plugin setup ran while the global plugin store mutex was held"
    );
  }
}
