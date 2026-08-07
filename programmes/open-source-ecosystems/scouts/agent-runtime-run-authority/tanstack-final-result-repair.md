# TanStack generation final-result persistence repair

## In simple words

TanStack generation middleware can transform a provider result several times before returning it to the caller.

Generation persistence currently records the result by inserting another transform into that same ordered list. If a later middleware transforms the result again, persistence stores the earlier value while the caller receives the later one.

The confirmed image-generation reproduction returns:

```text
https://app.test/final.png
```

but stores:

```text
https://provider.test/original.png
```

A reload can therefore repaint a different successful result from the one originally shown.

## Retrieval and execution boundary

- Confirmed target head: `aade077647556a7ea17d7ddf73bd4e7dc0258301`
- Current observed upstream head after confirmation: `ed44467c5e701f0a4fcc1c9f5639d036de35d26a`
- Intervening upstream commit changes only OpenTelemetry middleware, docs, and tests; generation middleware and persistence are unchanged.
- Characterization run: `31103183149`
- Job: `92621602622`
- Upstream contact authorized: `false`

## Confirmed target result

The focused target-native test registered persistence before a later middleware transform.

The live activity result contained the later transformed URL. The durable generation-run record contained the original provider URL.

Assertion:

```text
Expected: https://app.test/final.png
Received: https://provider.test/original.png
```

Evidence class: `target-executed defect`.

The test explicitly disables artifact extraction. It exercises terminal result metadata ordering without network fetches or blob-store behavior.

## Why `onFinish` is not the smallest repair

`GenerationFinishInfo` currently contains duration and optional usage, but not the final result.

Moving persistence capture into `onFinish` would therefore require widening the public lifecycle payload and changing every generation activity call site: image, video, audio, speech, transcription, and summarize.

That can be a valid future API, but it is larger than the correctness repair requires.

## Selected repair boundary

Add a post-transform observer phase to the shared generation middleware runner.

### Transform contract

Transforms remain ordered result-rewriting functions:

```text
raw provider result
  -> artifact transform
  -> application transform A
  -> application transform B
  -> final live result
```

### Observer contract

Observers run only after the complete transform list and cannot replace the result:

```text
final live result
  -> persistence observer
  -> other terminal observers
  -> return or stream the same final result
```

Generation persistence keeps artifact extraction and durable-URL rewriting as a transform because those operations intentionally modify the live value. It moves only durable terminal capture into the observer phase.

## Compatibility shape

The reviewed implementation uses a `WeakMap<GenerationMiddlewareContext, observers[]>` inside the shared middleware runner.

This avoids adding another required field to `GenerationMiddlewareContext`, so custom context builders remain source-compatible.

The entry is removed in `finally` after transform/observer execution. It is also removed when a transform or observer throws.

The helper is exported only through `@tanstack/ai/adapter-internals`:

```ts
observeGenerationResult(ctx, observer)
```

Persistence already depends on that internal subpath for `providePendingTurn`, so this adds no new package-layer inversion.

## Prepared candidate

Fieldwork materializer:

```text
artifacts/materialize-tanstack-final-result-observer.py
```

Exact candidate head for execution:

```text
ed44467c5e701f0a4fcc1c9f5639d036de35d26a
```

Candidate fence:

1. `.changeset/quiet-maps-rest.md`
2. `packages/ai/src/activities/middleware/run.ts`
3. `packages/ai/src/adapter-internals.ts`
4. `packages/ai/tests/middlewares/generation-result-observer.test.ts`
5. `packages/ai-persistence/src/middleware.ts`
6. `packages/ai-persistence/tests/generation-final-result-authority.test.ts`

## Controls

### Original distinguishing regression

Requires the persisted URL to equal the fully transformed live URL.

### Core observer ordering

An observer registered by an earlier middleware must see the result after a later middleware transform.

### Context isolation

An observer registered for one generation call must not run during a later call with a different middleware context.

### Package gates

The repair workflow also requires:

- exact target identity;
- deterministic materialization;
- formatting and `git diff --check`;
- `@tanstack/ai-persistence` plus dependency builds;
- package type checks;
- package type-aware lint;
- exact six-file generated fence;
- retained candidate artifact.

## Explicit limits

- The repair preserves current behavior where a persistence failure can fail the otherwise successful activity. It does not make persistence best-effort.
- Artifact fetching, blob writes, and durable URL rewriting remain in the transform phase.
- Observer ordering is registration order. Observers see one final value and cannot replace it.
- No owned TanStack fork is connected, so the candidate remains a reproducible Fieldwork artifact rather than a pull request.

## Current disposition

`REPAIR / EXECUTE`

The defect is confirmed. The exact-current-head repair workflow is registered. Do not claim a passing repair until its retained run completes.
