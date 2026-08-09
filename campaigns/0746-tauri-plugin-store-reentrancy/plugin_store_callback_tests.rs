// Prepared target tests for Fieldwork #746.
// Intended insertion point: crates/tauri/src/app.rs test surface where AppHandle internals are visible.

#[cfg(test)]
mod fieldwork_plugin_store_callback_ownership {
  use super::*;
  use crate::plugin::Builder as PluginBuilder;
  use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc,
  };

  #[test]
  fn dynamic_plugin_setup_runs_without_the_global_store_lock() {
    let app = crate::test::mock_app();
    let lock_was_available = Arc::new(AtomicBool::new(false));
    let lock_was_available_clone = lock_was_available.clone();

    let plugin = PluginBuilder::new("fieldwork-dynamic-setup")
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

  #[test]
  fn remove_plugin_drops_the_plugin_after_releasing_the_store_lock() {
    let app = crate::test::mock_app();
    let lock_was_available = Arc::new(AtomicBool::new(false));
    let lock_was_available_clone = lock_was_available.clone();

    let plugin = PluginBuilder::new("fieldwork-remove-drop")
      .on_drop(move |app| {
        lock_was_available_clone.store(
          app.manager.plugins.try_lock().is_ok(),
          Ordering::SeqCst,
        );
      })
      .build();

    app.handle().plugin(plugin).unwrap();
    assert!(app.handle().remove_plugin("fieldwork-remove-drop"));

    assert!(
      lock_was_available.load(Ordering::SeqCst),
      "remove_plugin dropped the plugin while the global plugin store mutex was held"
    );
  }

  #[test]
  fn same_name_replacement_drops_the_old_plugin_after_releasing_the_store_lock() {
    let app = crate::test::mock_app();
    let old_drop_lock_was_available = Arc::new(AtomicBool::new(false));
    let old_drop_lock_was_available_clone = old_drop_lock_was_available.clone();

    let old = PluginBuilder::new("fieldwork-replace-drop")
      .on_drop(move |app| {
        old_drop_lock_was_available_clone.store(
          app.manager.plugins.try_lock().is_ok(),
          Ordering::SeqCst,
        );
      })
      .build();
    let replacement = PluginBuilder::new("fieldwork-replace-drop").build();

    app.handle().plugin(old).unwrap();
    app.handle().plugin(replacement).unwrap();

    assert!(
      old_drop_lock_was_available.load(Ordering::SeqCst),
      "same-name replacement dropped the old plugin while the global plugin store mutex was held"
    );
  }
}
