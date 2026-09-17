# SWC mapped `arguments` candidate receipt — local GREEN — 2026-08-09

## In simple words

The one-line `unused`-pass candidate derived by Fieldwork turns the campaign's non-inline semantic matrix GREEN on pinned SWC and passes the focused package checks run by the carrier.

The candidate changes the existing parameter/`arguments` safeguard from the currently visited optimizer scope to the assigned identifier's syntax context:

```rust
!self.data.used_arguments(self.ctx.scope)
```

becomes:

```rust
!self.data.used_arguments(i.id.ctxt)
```

On the tested path, that makes the safeguard follow an enclosing function parameter across a nested arrow or ordinary nested function. It preserves exactly the writes that remain observable through a sloppy mapped `arguments` object while still allowing the tested strict, unobserved, and unrelated-local writes to be removed.

This is **local-path GREEN evidence, not acceptance of the general repair**. Active upstream PR `swc-project/swc#12037` contains the same one-line change, and maintainer review states that the inline pass can change identifier contexts to avoid collisions. A post-inline identifier context may therefore have no corresponding scope data, making `i.id.ctxt` an unstable proxy for the parameter's declaring function.

Fieldwork will not create a competing SWC implementation. The useful next question is to reproduce or rule out that inline/remapped-context counterexample.

No third-party upstream mutation occurred.

## Execution identity

- Campaign: #766
- Execution carrier: `teamleaderleo/fieldwork#768`
- Carrier branch: `fieldwork/execution/swc-mapped-arguments-candidate`
- Carrier exact head: `a5becad36b191a83b9a349092e89706c678bb34d`
- Workflow: `Fieldwork integrity`
- Workflow run: `31292179758`
- Job: `93191110056` (`swc-mapped-arguments-candidate`)
- Runner: GitHub-hosted Ubuntu 24.04
- Pinned SWC source: `5bf27fd72e4667bac6cc86888b8facb8b91f8077`
- Rust toolchain: `nightly-2026-04-10` (`rustc 1.96.0-nightly f5eca4fcf`)
- Candidate source file: `crates/swc_ecma_minifier/src/compress/optimize/unused.rs`

## Candidate diff executed

The carrier applied exactly this production diff inside the runner:

```diff
@@ -787,7 +787,7 @@ impl Optimizer<'_> {
                  ) && var.usage_count == 0
                      && var.flags.contains(VarUsageInfoFlags::DECLARED)
                      && (!var.flags.contains(VarUsageInfoFlags::DECLARED_AS_FN_PARAM)
-                        || !self.data.used_arguments(self.ctx.scope)
+                        || !self.data.used_arguments(i.id.ctxt)
                          || self.ctx.expr_ctx.in_strict)
```

The pre-test `git diff --check` passed.

Evidence class for the candidate source: `target-executed` on an execution carrier, not a canonical SWC candidate head.

## Semantic matrix

Configuration:

```json
{
  "defaults": false,
  "unused": true
}
```

The fixture exercised seven cases and expected one combined runtime line:

```text
2 2 2 1 7 5 1
```

### 1. Direct sloppy parameter write

```js
function direct(b) {
    b = 2;
    return arguments[0];
}
```

Expected/observed: `2`.

The assignment remained in optimized output.

### 2. Nested arrow write to outer sloppy parameter

```js
function nestedArrow(b) {
    run(() => {
        b = 2;
    });
    return arguments[0];
}
```

Expected/observed: `2`.

The assignment remained in optimized output.

### 3. Nested ordinary-function write to outer sloppy parameter

```js
function nestedFunction(b) {
    run(function () {
        b = 2;
    });
    return arguments[0];
}
```

Expected/observed: `2`.

The assignment remained in optimized output.

### 4. Strict nested write control

```js
function strictNested(b) {
    "use strict";
    run(() => {
        b = 2;
    });
    return arguments[0];
}
```

Expected/observed: `1`.

The optimized output correctly reduced the arrow to `run(()=>{});` because strict parameters are not mapped to the arguments object.

### 5. No `arguments` observation

```js
function noArgumentsRead(b) {
    run(() => {
        b = 2;
    });
    return 7;
}
```

Expected/observed: `7`.

The optimized output correctly reduced the arrow to `run(()=>{});`.

### 6. Unrelated local write while `arguments` is observed

```js
function unrelatedLocal(b) {
    let x = 1;
    run(() => {
        x = 2;
    });
    return arguments[0];
}
```

Expected/observed: `5` for input `5`.

The optimizer removed the unused local declaration/write and kept the arguments result. This is an important over-retention control: merely using `arguments` did not cause unrelated nested writes to be retained.

### 7. Default-parameter control

```js
function defaultParam(b = 1) {
    run(() => {
        b = 2;
    });
    return arguments[0];
}
```

Expected/observed: `1`.

The candidate retained `b = 2`, which is conservative for this non-simple parameter-list case. Runtime remained correct. This control does not establish optimality; it records that the candidate did not change semantics in the tested case.

## Target test receipts

First run with snapshot generation:

```text
UPDATE=1 cargo test -p swc_ecma_minifier --test compress -- mapped_arguments_candidate --nocapture
```

Result:

```text
test result: ok. 1 passed; 0 failed; 0 ignored; 2927 filtered out
```

Second run without UPDATE:

```text
cargo test -p swc_ecma_minifier --test compress -- mapped_arguments_candidate --nocapture
```

Result:

```text
test result: ok. 1 passed; 0 failed; 0 ignored; 2927 filtered out
```

The fixture harness executed optimized JavaScript and matched the expected runtime oracle.

Evidence class: `target-executed` GREEN for this semantic matrix.

## Package checks

The carrier then ran:

```text
cargo fmt --all -- --check
cargo clippy -p swc_ecma_minifier --all-targets -- -D warnings
git diff --check
```

All completed successfully. The overall job conclusion was `success`.

Evidence class: focused package gate for the ephemeral candidate; this is not a repository-wide full gate.

## Generated output review

The optimized output demonstrates the intended selective behavior:

```js
function direct(b) {
    b = 2;
    return arguments[0];
}
function nestedArrow(b) {
    run(()=>{
        b = 2;
    });
    return arguments[0];
}
function nestedFunction(b) {
    run(function() {
        b = 2;
    });
    return arguments[0];
}
function strictNested(b) {
    "use strict";
    run(()=>{});
    return arguments[0];
}
function noArgumentsRead(b) {
    run(()=>{});
    return 7;
}
function unrelatedLocal(b) {
    run(()=>{});
    return arguments[0];
}
function defaultParam(b = 1) {
    run(()=>{
        b = 2;
    });
    return arguments[0];
}
```

The log also shows the optimizer still dropping an unrelated assignment to `x`, confirming the candidate did not globally disable unused assignment removal inside functions that observe `arguments`.

## Active upstream ownership

Upstream PR `swc-project/swc#12037`, head `0a1971a63345e41de567d4fd97c9927283a13201`, independently proposes the same one-line change and a nested-scope regression fixture.

At the time of Fieldwork review, the PR remained open. A maintainer (`Austaras`) commented:

```text
This would not be enough. In inline pass swc would change ident ctxt(to avoid name collision) which would result in non exist scope data.
```

The PR head still contained the one-line context substitution when inspected.

This is disposition-relevant upstream review evidence. A locally green result does not clear the inline-context concern.

## Why the inline concern is substantive

SWC stores per-scope facts such as `USED_ARGUMENTS` keyed by `SyntaxContext`.

The local candidate assumes the assigned identifier's current `ctxt` can be used to retrieve the declaring function's scope record. That is true for the tested non-inline nested-scope examples.

The inliner uses remapping/renaming machinery when moving code and avoiding binding collisions. If a parameter identifier receives a fresh/remapped context after its original scope analysis, then:

```text
current identifier ctxt != original declaring-function scope key
```

and `used_arguments(i.id.ctxt)` may return false because no scope data exists under the remapped key. The same semantic bug could then reappear after code motion.

The durable requirement is therefore stronger than the one-line patch:

> The optimizer needs access to the parameter's mapped-arguments ownership fact after transformations that can rewrite identifier identity/context.

How that ownership should be represented is unresolved.

## Disposition

**LOCAL GREEN ACCEPTED; GENERAL REPAIR HOLD / OBSERVE ACTIVE UPSTREAM.**

The one-line candidate is validated for the ordinary nested-scope path and passes the focused package checks. It must not be promoted as the general fix because active upstream review identifies an inline/remapping case that can invalidate the candidate's lookup key.

Highest-value next research transition:

1. construct a target-native inline/remap discriminator for the maintainer's concern;
2. determine whether the one-line patch causes a semantic miscompile, merely fails to fix the original bug after inlining, or becomes conservatively safe;
3. identify what durable parameter-to-declaring-function ownership information survives remapping;
4. keep upstream PR #12037 as the implementation owner and avoid automated upstream interaction.
