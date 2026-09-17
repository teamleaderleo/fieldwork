# wgpu execution receipts and adjacent device-loss lifecycle

State: active execution; mixed compiled, queued, and source-read evidence

Fieldwork issue: #116

Fieldwork draft PR: #126

Owned fork drafts:

- `teamleaderleo/wgpu#1` — browser and public-wrapper characterization
- `teamleaderleo/wgpu#2` — stacked post-detachment core experiment

Upstream contact authorized: false

## Receipt R1 — browser characterization compile and clippy

Exact owned-fork source-test head:

```text
33d307cbe7acea21d23d561c72d270404a47bde4
```

Focused workflow run:

```text
30551656794
```

Job:

```text
90901572782 — Browser characterization compile — success
```

Execution environment:

```text
Ubuntu 24.04
Rust 1.93
wasm32-unknown-unknown
RUSTFLAGS="--cfg wasm_test -D warnings"
```

Command:

```text
cargo clippy --locked \
  --target wasm32-unknown-unknown \
  --package wgpu-test \
  --test wgpu-gpu \
  --features webgl,exhaust
```

Result:

```text
Finished `dev` profile successfully
```

Claim scope:

- the authored browser characterization module compiles for wasm;
- the full `wgpu-gpu` wasm test binary is clippy-clean under the exact command;
- this is not a browser, adapter, Playwright, or GPU execution receipt;
- no asserted runtime state has been observed yet.

## Receipt R2 — public wrapper blocked only by formatting

Same exact source-test head:

```text
33d307cbe7acea21d23d561c72d270404a47bde4
```

Job:

```text
90901572578 — Public wrapper characterization — failure
```

The job reached `cargo fmt --all -- --check`, reported four mechanical rustfmt differences, and skipped the unit tests. The differences were line wrapping and function-signature layout in:

- `tests/tests/wgpu-gpu/create_surface_error.rs`;
- `wgpu/src/api/surface_texture.rs`.

No compile or semantic test failure occurred because execution did not reach those steps.

Current owned-fork head:

```text
6535c7e3ab2b51af90044731cd39c0676521d9bc
```

Current focused run:

```text
30554907501 — queued
```

The revised disposable workflow now:

1. runs rustfmt in the checkout;
2. verifies the normalized tree with rustfmt and `git diff --check`;
3. lists tests;
4. requires both characterization identities with `grep`;
5. runs the `surface_texture::tests` filter.

This prevents both formatting from blocking semantics and a zero-test false-green.

## Receipt R3 — post-detachment core experiment queued

Stacked owned-fork draft:

```text
teamleaderleo/wgpu#2
```

Current experiment head:

```text
1f50fdfd667782f0be96d709e9921990211ad328
```

Focused run:

```text
30553877741 — queued
```

The experiment patches only its disposable CI workspace. It:

- instruments noop HAL acquisition, discard, presentation, and outstanding-image counts;
- injects a test-only failure immediately after `acquired_texture.take()`;
- requires the exact libtest identity;
- checks second acquisition and explicit discard;
- includes a successful-presentation negative control.

Expected controlled state if the source model is correct:

```text
first acquire       -> acquire=1 discard=0 present=0 outstanding=1
post-detach failure -> acquire=1 discard=0 present=0 outstanding=1
second acquire      -> acquire=2 discard=0 present=0 outstanding=2
discard second      -> acquire=2 discard=1 present=0 outstanding=1
success control     -> acquire=1 discard=0 present=1 outstanding=0
```

No result is claimed while the job is queued. Noop remains state-machine evidence, not DX12 or Vulkan platform proof.

## Adjacent known issue — retained frame before detachment

Current upstream issue:

[wgpu issue 9277: Surface drop panics after device loss](https://redirect.github.com/gfx-rs/wgpu/issues/9277)

The issue reports a different failure state from the stacked experiment:

```text
acquire frame
→ device becomes lost
→ public presentation checks device validity
→ presentation returns before queue-level detachment
→ acquired_texture remains populated
→ Surface drop calls HAL unconfigure while frame metadata is alive
→ Vulkan swapchain teardown panics on retained acquire-semaphore Arc
```

This independently validates the lane's theory correction:

```text
RejectedBeforeDetachment != PreparationFailedDetached
```

The issue remains open. No linked repair pull request or commit was found in the searched current history.

## Existing narrow cleanup primitive

Current core already contains `Surface::release_inner()`.

Its behavior:

```text
lock presentation
→ take acquired_texture
→ drop retained texture and backend metadata
→ do not require valid device
→ do not call HAL discard
```

This is directly relevant to the teardown ordering in issue 9277. Current `Surface::drop` instead takes the entire `Presentation`, calls HAL unconfigure, and only drops the retained presentation state afterward.

The narrow repair hypothesis is therefore ordering, not public API redesign:

```text
release retained acquired texture
→ then HAL unconfigure
```

That hypothesis still needs a controlled before/after test, including backend-specific teardown consequences.

## Two failure classes

### `RejectedBeforeDetachment`

```text
public ownership committed
core acquired_texture retained
HAL present not called
normal discard also rejects invalid device
surface teardown can see live frame metadata
```

Known adjacent evidence: upstream issue 9277 on Vulkan.

### `PreparationFailedDetached`

```text
public ownership committed
core acquired_texture removed
preparation fails
HAL present not called
surface record permits another acquisition
platform ownership may remain outstanding
```

Current evidence: source-read; controlled noop experiment queued.

## Next experiment queue

1. finish public wrapper unit execution;
2. finish controlled post-detachment core experiment;
3. build a teardown-order control for issue 9277:
   - retained-frame baseline;
   - device invalidation;
   - public present/discard early error;
   - teardown with retained frame;
   - teardown after `release_inner`-equivalent drain;
4. only after controlled results, select DX12 and Vulkan platform probes;
5. execute browser characterizations in Playwright with exact generated identities.

## Stops

- Do not upgrade wasm compile to browser execution.
- Do not call a rustfmt failure a semantic failure.
- Do not claim discovery priority over issue 9277.
- Do not merge the retained and detached failure classes.
- Do not treat noop as platform proof.
- Do not propose a public breaking API before narrow lifecycle ownership is measured.
- Do not contact upstream without explicit authority.