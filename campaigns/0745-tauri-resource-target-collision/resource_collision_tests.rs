// Prepared target tests for Fieldwork #745.
// Intended insertion point: crates/tauri-build/src/lib.rs #[cfg(test)] surface.

#[cfg(test)]
mod fieldwork_resource_target_collision {
  use super::*;
  use std::{
    collections::HashMap,
    fs,
    time::{SystemTime, UNIX_EPOCH},
  };

  fn temp_root(name: &str) -> std::path::PathBuf {
    let unique = SystemTime::now()
      .duration_since(UNIX_EPOCH)
      .unwrap()
      .as_nanos();
    let root = std::env::temp_dir().join(format!(
      "tauri-{name}-{}-{unique}",
      std::process::id()
    ));
    fs::create_dir_all(&root).unwrap();
    root
  }

  #[test]
  fn flattened_glob_rejects_distinct_sources_with_same_basename() {
    let root = temp_root("flattened-glob-collision");
    let output = root.join("out");
    fs::create_dir_all(root.join("docs/a")).unwrap();
    fs::create_dir_all(root.join("docs/b")).unwrap();
    fs::create_dir_all(&output).unwrap();

    fs::write(root.join("docs/a/readme.md"), b"first").unwrap();
    fs::write(root.join("docs/b/readme.md"), b"second").unwrap();

    let mut resources = HashMap::new();
    resources.insert(
      root.join("docs/**/*.md").to_string_lossy().into_owned(),
      "website-docs/".to_string(),
    );

    let result = copy_resources(ResourcePaths::from_map(&resources, true), &output);
    let _ = fs::remove_dir_all(&root);

    assert!(
      result.is_err(),
      "flattened glob silently let two distinct sources claim website-docs/readme.md"
    );
  }

  #[test]
  fn flattened_glob_allows_distinct_basenames_in_same_target_directory() {
    let root = temp_root("flattened-glob-distinct");
    let output = root.join("out");
    fs::create_dir_all(root.join("docs/a")).unwrap();
    fs::create_dir_all(root.join("docs/b")).unwrap();
    fs::create_dir_all(&output).unwrap();

    fs::write(root.join("docs/a/alpha.md"), b"alpha").unwrap();
    fs::write(root.join("docs/b/beta.md"), b"beta").unwrap();

    let mut resources = HashMap::new();
    resources.insert(
      root.join("docs/**/*.md").to_string_lossy().into_owned(),
      "website-docs/".to_string(),
    );

    let result = copy_resources(ResourcePaths::from_map(&resources, true), &output);

    assert!(result.is_ok(), "distinct flattened targets should remain valid");
    assert_eq!(fs::read(output.join("website-docs/alpha.md")).unwrap(), b"alpha");
    assert_eq!(fs::read(output.join("website-docs/beta.md")).unwrap(), b"beta");

    let _ = fs::remove_dir_all(&root);
  }

  #[test]
  fn distinct_map_entries_cannot_claim_the_same_final_file() {
    let root = temp_root("map-target-collision");
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
      "distinct resource entries silently competed for the same final target"
    );
  }
}
