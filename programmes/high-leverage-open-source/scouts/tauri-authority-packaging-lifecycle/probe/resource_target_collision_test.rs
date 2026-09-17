
#[cfg(test)]
mod fieldwork_resource_target_collision {
  use super::*;
  use std::{collections::HashMap, fs, time::{SystemTime, UNIX_EPOCH}};

  #[test]
  fn duplicate_resource_targets_are_rejected() {
    let unique = SystemTime::now()
      .duration_since(UNIX_EPOCH)
      .unwrap()
      .as_nanos();
    let root = std::env::temp_dir().join(format!(
      "tauri-resource-target-collision-{}-{unique}",
      std::process::id()
    ));
    let output = root.join("out");
    fs::create_dir_all(&output).unwrap();

    let first = root.join("first.txt");
    let second = root.join("second.txt");
    fs::write(&first, b"first").unwrap();
    fs::write(&second, b"second").unwrap();

    let mut resources = HashMap::new();
    resources.insert(first.to_string_lossy().into_owned(), "same.txt".to_string());
    resources.insert(second.to_string_lossy().into_owned(), "same.txt".to_string());

    let result = copy_resources(ResourcePaths::from_map(&resources, true), &output);
    let _ = fs::remove_dir_all(&root);

    assert!(
      result.is_err(),
      "duplicate resource targets were silently overwritten"
    );
  }
}
