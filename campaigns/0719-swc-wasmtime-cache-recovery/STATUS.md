# SWC Wasmtime Cache Recovery

## In simple words

Campaign #719 has two distinct Wasmtime filesystem-cache recovery discriminators and a stronger sibling implementation precedent, but it still lacks target-native execution.

Owned-fork PR `teamleaderleo/swc#1` covers an abandoned deterministic temporary file that can block final cache publication. PR `teamleaderleo/swc#3` covers a rejected final cache artifact that Wasmtime leaves behind. The current Wasmer backend handles the second lifecycle explicitly by deleting a cache file when module deserialization rejects it.

A temporary Fieldwork execution carrier was prepared to obtain RED -> GREEN receipts for both cases. The carrier workflow was added on owned Fieldwork PR #761, but the control-plane transition needed to schedule the modified workflow was blocked by the connected tool safety layer. The carrier is closed and no cache test execution is claimed from it.

- Campaign issue: #719
- Programme: #15
- Parent scout: #718
- Target hub: #717
- State: `claimed`
- Worker: GPT-5.6 Sol
- Public source pin/current upstream main: `swc-project/swc@5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Stale-temp candidate: `teamleaderleo/swc#1` at `bce1d2e03f654d6aaaac77d76e2a818b3b743706`
- Rejected-cache discriminator: `teamleaderleo/swc#3` at `825e42ed44676001d6c6a52bc1d0807a91852137`
- Prepared execution carrier: `teamleaderleo/fieldwork#761`, closed/unexecuted
- Evidence: `source-read`, `model-executed`, `target-test-prepared`
- Upstream contact: prohibited for automated workers

## Recovery case 1 — abandoned deterministic temporary file

Current Wasmtime publication serializes the compiled module, derives a deterministic sibling by appending `.tmp` to the cache extension, opens it with `create_new(true)`, and treats `AlreadyExists` as `Ok(())`.

A prior interrupted writer can therefore leave this state:

```text
final cache = absent
fixed .tmp  = present
```

A later store sees the stale temp path, reports success, and returns without creating the final cache file. The dependency-free model reproduced that transition.

PR #1 prepares unique same-directory temporary paths, complete write before rename, cleanup on failure, and the existing concurrent-writer destination behavior.

Evidence: `source-read`, `model-executed`, `target-test-prepared`.

## Recovery case 2 — rejected final cache artifact

Current Wasmtime load logic is effectively:

```rust
let module = std::fs::read(path).ok()?;
let engine = ENGINE.get_or_try_init(init_engine).ok()?;
let cache = wasmtime::Module::deserialize(engine, module).ok()?;
Some(runtime::ModuleCache(Box::new(WasmtimeCache(cache))))
```

A failed deserialization becomes a cache miss, but the rejected file remains at the final path.

The current Wasmer sibling has an explicit recovery rule:

```rust
let module = wasmer::Module::deserialize_from_file(store.engine(), path);
if module.is_err() {
    let _ = std::fs::remove_file(path);
}
```

That sibling behavior is strong source precedent for treating a rejected serialized artifact as untrusted persistent cache state rather than a permanent cache miss.

PR #3 writes invalid cache bytes, invokes the real Wasmtime `load_cache`, and requires both a cache miss and removal of the rejected file. It remains test-only so the repair is independently reviewable.

Evidence: `source-read`, `target-test-prepared`.

## Candidate direction for rejected-cache recovery

The bounded source-grounded candidate is:

1. read the final cache file;
2. attempt Wasmtime deserialization;
3. on success, return the module cache;
4. on deserialization rejection, best-effort remove that exact final artifact and return `None`.

This mirrors the Wasmer sibling lifecycle without mixing it with stale-temp publication changes.

The candidate still needs target execution and Windows review before promotion.

## Execution carrier #761

A temporary owned Fieldwork carrier was prepared with SWC nightly `2026-04-10` and two intended RED -> GREEN transitions:

- stale-temp regression on pinned base, then exact PR #1 candidate plus focused/full package tests, formatting and clippy;
- rejected-cache PR #3 RED, then a runner-only deletion candidate plus focused/full package tests, formatting and clippy.

The carrier branch reached head `41e997c0817f3a26c2e618ff5b90f312ef5598f8`. Its PR was closed during workflow-trigger handling, and the connected tool subsequently blocked the reopen/control-plane mutation. No alternate bypass was attempted.

Therefore:

- carrier prepared: yes;
- target tests executed: no;
- RED receipt: none;
- GREEN receipt: none;
- evidence upgrade: none.

## Review finding on PR #1

An earlier attempted full-file edit accidentally duplicated part of `WasmtimeRuntime::init`. The branch was force-restored immediately to exact head `bce1d2e03f654d6aaaac77d76e2a818b3b743706`; PR #1 contains none of that bad intermediate edit.

This remains recorded because exact-head review is part of the evidence boundary.

## Current disposition

**HOLD / EXECUTE when a clean carrier is available.**

Promotion requires:

1. stale-temp base assertion RED and exact PR #1 candidate GREEN;
2. rejected-cache PR #3 assertion RED and bounded deletion candidate GREEN;
3. focused Wasmtime tests plus full `swc_plugin_backend_wasmtime` tests;
4. `cargo fmt` and package clippy;
5. explicit Windows destination/replacement review;
6. exact-head diff review and retained execution receipt.

No third-party upstream mutation occurred.
