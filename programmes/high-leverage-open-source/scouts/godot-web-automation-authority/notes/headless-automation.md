# Godot headless and unit-test automation source map

## In simple words

Godot has two useful automation levels for this scout. The native `--test` entrypoint starts before normal project execution and is available from platform mains, including web builds, but its current test context still initializes most core/server/scene/module surfaces plus editor types in tools builds. For project-level behavior, `--headless` switches display/audio to dummy drivers and is intended for CI and scripts.

This is enough to keep small correctness probes in the native test suite while reserving project/browser fixtures for import, persistence, focus, and presentation lifecycle.

State: source-read. Fork tests prepared; no target execution claimed in this environment.

## Exact source

Development revision: `godotengine/godot@4173760fdf6c2c722e82e08cb58e55f34c9efd80`.
Retrieved: 2026-08-09.

Key paths:

- `main/main.h`
- `main/main.cpp`
- platform main entrypoints

## Unit-test entrypoint

Platform mains invoke the `TEST_MAIN_OVERRIDE` macro, which calls `Main::test_entrypoint()` before ordinary engine setup. When `--test` is present and the binary was compiled with `tests=yes`, the sequence is:

```text
test_setup()
test_main(argc, argv)
test_cleanup()
```

The command-line help exposes `--test [--help]` when tests are compiled in.

## Current test context is broad

`Main::test_setup()` documents a TODO for multiple test contexts. Today it initializes, among other things:

- Engine, core types, core drivers, ProjectSettings and translation services;
- module core initialization and core singletons;
- server types and server-level modules/extensions;
- a dummy rasterizer plus RenderingServer;
- ThemeDB;
- scene and driver types, scene singletons and scene-level modules/extensions;
- editor types and editor-level modules/extensions in tools builds;
- platform APIs and a no-project default theme.

This makes native tests excellent for small engine invariants that touch nodes/resources/animation, but they are not a tiny isolated unit-test runtime.

## Headless project execution

The general command line exposes `--headless` as dummy display plus dummy audio and describes it as useful for servers and scripts. Display startup also points CI users to `--headless` when native display creation is unavailable.

## Scout implications

### Use native tests for

- AnimationMixer/AnimationPlayer transform semantics;
- ResourceUID map/cache invariants;
- serialization helpers that do not require a real editor filesystem scan;
- pure scene/resource lifecycle behavior that can run against generated objects.

### Use headless projects for

- scene save/load/restart receipts;
- import/reimport behavior where editor-generated metadata is already available;
- deterministic action/replay adapters that need a SceneTree;
- command-line exit codes, logs, and generated receipt files.

### Use browser execution for

- canvas focus/blur semantics;
- RAF gaps and page lifecycle;
- IDBFS persistence;
- WebGL context loss;
- browser-specific memory/resource cleanup.

## Current prepared target tests

Owned fork draft PR `teamleaderleo/godot#1` carries the AnimationPlayer combined-TRS probe.

Owned fork draft PR `teamleaderleo/godot#2` carries a ResourceUID reverse-cache replacement probe. The production cache-history path needs a stronger save/reload fixture before promotion.

## Evidence boundary

Supported: initialization and command-routing behavior at the pinned source revision.

Unknown: compile/test status of the prepared fork tests, exact CI cost, and browser-specific `--test` execution behavior.

Automated upstream contact: prohibited.
