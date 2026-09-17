# Unreal / C++ systems scout — target selection and first branch

## In simple words

This scout asked for the smallest public Unreal/C++ investigation that can prove mature-codebase navigation, real engine/plugin conventions, C++ reasoning, and target-native evidence around consequential behavior.

**Current answer:** start with **Cesium for Unreal**, pinned at `71006dd87e040b55d6e3063e47e945f41728c81b` with `cesium-native` submodule `b4137763914820b01a42b52ee886a55b036cd6ac`.

The first bounded question sits where Unreal movie capture switches Cesium into offline tile selection while normal occlusion evidence still arrives on Unreal render frames. The source map shows a plausible clock mismatch: offline selection can iterate repeatedly without producing a new render-frame occlusion result, while cesium-native deliberately delays refinement when occlusion is unavailable. That is a **source-read hypothesis**, not an executed bug claim.

The next useful transition is a target-native reproduction using Cesium's existing Unreal Automation test style. If the baseline does not show a movie/offline selection difference, record a negative result and stop this branch. If Cesium setup cannot reach existing tests cleanly, fall back to the smaller Project Borealis Unreal Git plugin concurrency candidate instead of spending the scout on setup friction.

## Assignment contract

- Worker: **Ibn al-Haytham 🔭**
- Parent: Fieldwork #917
- Programme: `open-source-ecosystems` / Fieldwork #207
- Target at start: `portfolio-inbox`; first selected target: Cesium for Unreal
- Target hub: none yet; recurring work has not earned a Cesium target hub
- Owned path: `programmes/open-source-ecosystems/scouts/unreal-cpp-systems/report.md`
- Claim scope supported here: **interface**, evidence class **source-read**
- Upstream-contact authorization: `false`
- Stop condition: either one target clearly owns a runnable, falsifiable next question, or the accessible targets prove too costly / weakly testable for this lane
- Automated upstream contact: prohibited

## Target comparison

| Target | Access / license | Current activity | Test / build path | Unreal-specific depth | Setup cost | Scout result |
|---|---|---|---|---|---|---|
| **CesiumGS/cesium-unreal** | public, Apache-2.0 | active; selected revision is v2.29.0 release | Unreal 5.6+, CMake/cesium-native, `TestsProject`, Unreal Automation tests in `Source/CesiumRuntime/Private/Tests` | **high** — streaming, tile selection, renderer occlusion, async loading, LOD, Sequencer | medium/high | **selected**; richest consequence + testability combination |
| **getsentry/sentry-unreal** | public, MIT | very active | sample project, init scripts, platform SDK dependencies, Unreal Automation tests | medium/high — crash lifecycle, platform SDK integration, editor/runtime boundaries | medium | strong harness; current open bug candidates inspected were platform-specific or already carried candidate fixes |
| **unrealcv/unrealcv** | public, MIT | active; UE5.6 support documented | plugin build in a C++ UE project + runtime client commands | high at camera/network/simulation boundary | medium | attractive, but no bounded first correctness question beat Cesium during this pass |
| **TriAxis-Games/RealtimeMeshComponent** | public Core edition, MIT; contribution license also permits proprietary Pro use | active | source plugin build + examples; UE5.5–5.8 | **high** rendering / runtime-generated geometry | low/medium | strong rendering target; some advanced surfaces live in Pro, and no sharper current question beat Cesium |
| **ProjectBorealis/UEGitPlugin** | public, MIT | active | source plugin compile; editor/Git workflows | medium — editor source control, async/background workers, locking | low/medium | **fallback**; current concurrent lock-cache mutation report has crisp crash consequence |
| **carla-simulator/carla** | public, MIT | very active | full simulator build/test stack | very high — Unreal simulation, sensors, networking, world runtime | **very high** | heavyweight control; poor first target for a bounded evidence sprint |

Relevant upstream issue context is kept quiet per Fieldwork policy:

- Cesium Sequencer / occlusion context: https://redirect.github.com/CesiumGS/cesium-unreal/issues/956
- Project Borealis lock-cache race fallback: https://redirect.github.com/ProjectBorealis/UEGitPlugin/issues/238
- Cesium GeoJSON out-of-bounds crash alternate: https://redirect.github.com/CesiumGS/cesium-unreal/issues/1870

These issue reports are context only. The branch selection comes from source and test mapping, not from treating an issue list as a work queue.

## Pinned Cesium source map

Repository root: https://github.com/CesiumGS/cesium-unreal  
Pinned commit: https://github.com/CesiumGS/cesium-unreal/commit/71006dd87e040b55d6e3063e47e945f41728c81b  
Pinned cesium-native submodule: `b4137763914820b01a42b52ee886a55b036cd6ac`

### Unreal-side control flow

`ACesium3DTileset::Tick` is the main game-thread selection entrypoint in `Source/CesiumRuntime/Private/Cesium3DTileset.cpp`.

The relevant path is:

```text
Unreal render frame
  → CesiumViewExtension::PostRenderViewFamily_RenderThread
  → aggregate Unreal primitive occlusion history
  → queue occlusion results

next game/render-family boundary
  → CesiumViewExtension::BeginRenderViewFamily
  → publish queued occlusion results

ACesium3DTileset::Tick
  → update pooled bounding-volume proxies from CesiumViewExtension
  → copy actor properties into TilesetOptions
  → build view frustums
  → realtime: updateViewGroup(...)
  → movie:    updateViewGroupOffline(...)
  → show selected tiles / update load status
```

Key owners:

- `Source/CesiumRuntime/Private/CesiumViewExtension.cpp` owns the Unreal render-thread → later-consumer occlusion-history transfer.
- `Source/CesiumRuntime/Private/CesiumBoundingVolumeComponent.cpp` maps Unreal primitive visibility history into `TileOcclusionState`; if a result is unavailable it preserves the prior state.
- `Source/CesiumRuntime/Private/Cesium3DTileset.cpp` owns movie-mode switching and copies `EnableOcclusionCulling` / `DelayRefinementForOcclusion` into cesium-native options.
- `ACesium3DTileset::PlayMovieSequencer()` enables `_captureMovieMode`, disables ancestor/sibling preloads, raises `LoadingDescendantLimit`, and disables LOD transitions. It does **not** independently disable occlusion culling or delayed refinement.
- Movie mode chooses `Tileset::updateViewGroupOffline(...)`.

### Native-side offline loop

At pinned cesium-native `b4137763914820b01a42b52ee886a55b036cd6ac`, `Cesium3DTilesSelection/src/Tileset.cpp` implements `updateViewGroupOffline` as:

```text
dispatch main-thread tasks
updateViewGroup(...)
while previous load progress < 100%:
  asset accessor tick
  dispatch main-thread tasks
  load tiles
  dispatch main-thread tasks
  updateViewGroup(...)
```

The loop advances Cesium async/loading work. It does not itself cause Unreal to render another frame or produce a new `FPrimitiveOcclusionHistory` snapshot.

### Delayed-refinement rule

At the same native revision, `Cesium3DTilesSelection/src/TilesetSelection.cpp` explicitly treats an unavailable occlusion result as a reason to postpone refinement when `delayRefinementForOcclusion` is enabled and the tile was not previously refined:

```text
occlusion unavailable
+ delayRefinementForOcclusion
+ tile not previously refined
→ count tile as waiting for occlusion
→ render current tile
→ treat SSE as satisfied for this visit
```

The comment says the normal expectation is that valid occlusion information will arrive in the next several frames.

That expectation is exactly what movie/offline selection needs to challenge, because several native selection iterations may occur inside one Unreal frame.

## First bounded question

> When Sequencer/movie capture enters `updateViewGroupOffline` with occlusion culling and delayed refinement enabled, can a tile remain at lower detail because native offline selection repeatedly sees `OcclusionUnavailable` without an intervening Unreal render-frame occlusion update?

### Invariant under test

Offline/movie selection should converge on the detail required for the captured frame without depending on future render-frame evidence that cannot arrive during the same offline convergence loop.

That invariant does **not** imply that occlusion culling must always be disabled in movie mode. The repair owner remains deliberately unresolved.

## Competing explanations

### H1 — clock mismatch causes under-refinement

Movie/offline selection can hit `OcclusionUnavailable`; delayed refinement treats that as a reason to render the current tile and avoid descendant loads. The offline loop may then reach its load-progress stopping condition without a new Unreal occlusion snapshot, leaving lower detail selected for the captured frame.

### H2 — current state already prevents the failure

A prior rendered frame may have supplied enough definite occlusion history, or previous selection state may already be refined, so the delayed-refinement branch may rarely or never block real Sequencer capture on current code. If a clean target-native reproduction cannot produce a differential, retain this as a negative result.

### H3 — diagnosis is right but repair belongs in cesium-native

Even if Unreal movie mode exposes the failure, the true contract may be that `updateViewGroupOffline` should ignore or override delayed-occlusion waiting for every renderer, rather than teaching the Unreal adapter to alter options. A reproduction should identify the failing invariant first; implementation ownership comes afterward.

## Target-native discriminator

Use the existing Cesium Unreal Automation test conventions around `Source/CesiumRuntime/Private/Tests/Cesium3DTileset.spec.cpp` and a deterministic local tileset fixture where hierarchical refinement is observable.

The first execution should compare the same view under these conditions:

| Case | Movie/offline mode | Occlusion | Delay refinement | Expected discriminator |
|---|---:|---:|---:|---|
| A | yes | on | on | disputed baseline |
| B | yes | on | off | should remove waiting-for-occlusion as a refinement blocker |
| C | yes | off | irrelevant | negative control for the occlusion mechanism |
| D | no | on | on | realtime control where render frames can advance occlusion history |

Useful evidence includes selected tile identities/detail, `tilesWaitingForOcclusionResults`, load progress, and a stable rendered/scene assertion if the existing harness exposes one cleanly.

The test must answer two separate questions:

1. **Does current pinned code produce a movie/offline selection differential?**
2. **If yes, does removing delayed waiting eliminate it without proving that the option toggle is the final repair boundary?**

No candidate implementation should begin until question 1 fails on the baseline.

## Execution boundary

This scout did not execute Unreal Engine or Cesium's target-native tests. The available automation context can read public GitHub state but does not provide a licensed/configured Unreal Engine build environment.

Evidence class therefore remains **source-read**. A target-native test plan exists; a target-native execution receipt does not.

Setup itself has a stop condition: before writing product code, reach a known existing Cesium Automation test on the pinned target. If the environment cannot reach that point cleanly within the bounded scout effort, classify setup separately and switch to the UEGitPlugin race fallback instead of turning installation into the research result.

## Ranked branch candidates

### 1. Cesium movie/offline selection × delayed occlusion refinement — **retain finding; execute next**

**Consequence:** captured frames may use lower detail than offline convergence intends.  
**Likely owner boundary:** Unreal movie-mode option handoff vs cesium-native offline selection semantics.  
**Evidence required:** target-native FAIL/PASS differential at pinned revisions.  
**Recommendation:** coordinator should promote to a child campaign only after target execution demonstrates the baseline difference, or if it deliberately wants a reproduction campaign whose first gate is that execution.

### 2. Project Borealis UEGitPlugin lock-cache race — **fallback scout candidate**

The current report describes parallel fetch workers and other readers/writers touching the same cached locked-file collection, with observed memory-corruption/crash consequence. It is a smaller setup surface and a good concurrency/lifecycle exercise, though it proves more editor-tooling fluency and less runtime/rendering depth than Cesium.

**Next evidence:** source map every writer/reader and identify a deterministic concurrency test boundary before selecting a repair.

### 3. Cesium GeoJSON `GetObjectAsMultiLineString` out-of-bounds crash — **small alternate**

A current good-first bug report provides a concrete editor crash around a malformed/particular MultiLineString conversion path. This is attractive for C++ correctness and Unreal API use, but it exercises less of the engine/runtime model that motivated #917.

**Next evidence:** source-map parser ownership and build the smallest target-native regression that separates invalid input handling from valid MultiLineString behavior.

## Negative results / parked targets

- **Sentry Unreal:** excellent contribution/test machinery; the open bugs inspected in this pass were either platform-packaging-specific or already accompanied by candidate fixes, so none beat the Cesium runtime question.
- **Realtime Mesh Component:** strong rendering depth and lower setup cost, but the public Core/Pro split narrows some advanced surfaces and this pass did not find a better bounded question.
- **UnrealCV:** active and genuinely Unreal-specific, but no first correctness/performance question beat Cesium after the initial map.
- **CARLA:** exceptional Unreal/runtime depth; setup size and simulator breadth make it a poor first bounded target.
- **Direct Unreal Engine source:** licensing/access and public-artifact boundaries make it less convenient for a first public Fieldwork evidence lane than a permissively licensed plugin.

## Recommendation

**Finish #917 as a scout handoff with Cesium selected and the reproduction gate explicit.** Do not create a Cesium target hub merely for this one branch. Do not treat the existence of upstream issue context as reproduction evidence.

Requested next transition:

```text
source-read scout
→ target-native execution on pinned Cesium
→ negative result OR demonstrated interface failure
→ coordinator decides finding/campaign/target-hub promotion
```

Automated third-party upstream contact remained prohibited and none was performed.
