# Campaign 0719: SWC Wasmtime Cache Recovery

State: `claimed`

Campaign issue: #719

Programme: #15

Parent scout: #718

Primary target: #717

Pinned target revision: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`

Upstream contact authorized: `false`

## In simple words

SWC can cache compiled WebAssembly plugins on disk. The initial scout found one publication failure in the Wasmtime backend: an abandoned deterministic `.tmp` file can make a later store report success while the final cache file remains absent.

A second source comparison found another recovery gap. The Wasmer backend deletes a cache file when deserialization rejects it; Wasmtime returns a miss and leaves the rejected file in place. That stale final file can interfere with publication and guarantees that the same invalid bytes remain available to the next fresh process.

The campaign now owns these as two separate recovery cases with one narrow lifecycle question: after an on-disk Wasmtime cache artifact becomes unusable, can the next successful compilation reliably publish a usable final cache entry?

## Exact question

Can Wasmtime filesystem caching recover from both abandoned temporary files and rejected final cache artifacts without treating missing or unusable final state as successful publication?

## Current source boundaries

- `crates/swc_plugin_backend_wasmtime/src/lib.rs` — load, deserialize, serialize, and publish runtime cache entries.
- `crates/swc_plugin_runner/src/cache.rs` — cache miss, compilation, filesystem publication, and in-process retention.
- `crates/swc_plugin_backend_wasmer/src/lib.rs` — sibling invalid-cache deletion rule.
- `crates/swc_plugin_backend_wasmer/src/filesystem_cache.rs` — sibling unique temporary-file publication rule.

## Prepared discriminators

### Abandoned temporary file

Owned draft `teamleaderleo/swc#1`, head `bce1d2e03f654d6aaaac77d76e2a818b3b743706`.

The test pre-creates the legacy deterministic `.tmp` path, stores a minimal valid Wasm module through the real Wasmtime runtime, and requires the final cache path to exist after a successful store.

### Rejected final cache

Owned draft `teamleaderleo/swc#3`, head `825e42ed44676001d6c6a52bc1d0807a91852137`.

The test writes invalid serialized bytes to the final Wasmtime cache path, calls `load_cache`, requires the load to fail, and requires the rejected artifact to be removed. This mirrors the explicit Wasmer recovery rule and leaves the path available for a freshly compiled cache artifact.

Both are `target-test-prepared`; target-native execution remains pending.

## Change thesis

Current behaviour: Wasmtime can leave an unusable cache artifact in the path used by future processes, either as an abandoned deterministic temporary file or a rejected final cache file.

Consequence: later processes can miss serialized-module reuse, recompile, or fail publication depending on the filesystem state and platform rename semantics.

Proposed improvement: use unique completed temporary artifacts for publication and discard final cache artifacts that the runtime itself rejects.

Evidence: source comparison, dependency-free stale-temp model, and two owned-fork target regression drafts.

Boundary: frequency, real build cost, cross-platform candidate behavior, and exact repair correctness require target execution.

## Stop condition

Stop when both recovery cases have base RED evidence, candidate GREEN evidence on the affected crate, exact-head diff review, and a clear answer on concurrent publication and Windows destination behavior.
