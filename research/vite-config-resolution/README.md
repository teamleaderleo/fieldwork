# Vite config resolution: a guide to the copies, the tests, and the trade-offs

## In simple words

This study guide explains how Vite can derive configuration without writing generated settings into the objects supplied by its caller. It belongs to the web-tooling runtime-correctness research and follows the Vite changes in PR 23208. The demonstrated optimizer-cache failure led to a broader examination of shared input, compatibility accessors, and hook timing. The guide explains the submitted repair, its tests, and its limits rather than proposing another investigation.

This guide describes submitted commit `9641e4f018ed1a2917d617832ff69560c86d0ef9` against base `8492422b8f110625a90c702f42f30784e8cf19dc`. It is a study document, separate from the PR description. Short snippets sometimes omit surrounding code so the operation is easier to see.

[Complete diff](https://github.com/vitejs/vite/commit/9641e4f018ed1a2917d617832ff69560c86d0ef9) · [PR discussion](https://redirect.github.com/vitejs/vite/pull/23208)

## Start with the one-minute version

You give Vite some instructions. Vite fills in missing settings and translates older settings into newer ones. Previously, some of that work happened directly on the objects you supplied.

If you reused those objects, they could contain changes from Vite's previous run.

The patch makes copies of the affected containers before Vite writes to them. It puts each copy into the working config, so the rest of resolution reads the copy.

```text
Before

caller ───────────────┐
                     ▼
               shared object ◄──────── working config
                     │
                     ▼
                 Vite writes
                     │
                     ▼
           caller sees those writes


After the relevant copy

caller ──────────────► original object

working config ─────► copied object
                            │
                            ▼
                        Vite writes
                            │
                            ▼
                 resolution reads the copy
```

The demonstrated cache bug involves an array growing on each resolution. Other changes protect caller input and compatibility behavior; they aren't all separate cache bugs.

**The question to ask at every hunk:** Which object could be shared, what is Vite about to write, and where will later code read the result?

## A small vocabulary

| Term | What it means here |
| --- | --- |
| Inline config | The object passed directly to Vite's API. |
| Working config | The values Vite is currently merging, translating, and filling in. |
| Resolved config | The result Vite uses to operate the server or build. |
| Default | A value Vite supplies when an option hasn't been supplied. |
| Compatibility | Keeping an older option working with a newer option. |
| Alias | Two names referring to the same thing. |
| Hook | A plugin function Vite calls at a particular stage. |
| Mutation | Changing a property or array on an existing object. |
| Shallow copy | A new outer container holding the same property values or array entries. |

This assignment does not copy an object:

```ts
const working = original
```

Both variables refer to it. This makes a new outer object:

```ts
const working = { ...original }
```

But `working.build` and `original.build` can remain the same nested object. Copying an array with `.slice()` similarly preserves the identity of the objects inside it.

### The punctuation you'll keep seeing

| Syntax | Read it as |
| --- | --- |
| `x ??= {}` | If `x` is null or undefined, give it an empty object. Otherwise keep it. |
| `x = { ...x }` | Create a shallow copy and replace `x` with it. Null/undefined contribute no properties. |
| `x?.y` | Read `y` if `x` isn't null/undefined; otherwise return undefined. |
| `x ?? fallback` | Use the fallback only for null/undefined. |
| `x || fallback` | Use the fallback for any falsy value, including false. |
| `condition ? a : b` | Choose `a` when the condition is truthy, otherwise `b`. |
| `x == null` | Check for either null or undefined. |
| `x === undefined` | Check only for undefined. |
| `x!`, `as SomeType`, `as const` | TypeScript information; these don't clone or validate values at runtime. |

Empty arrays and empty objects are truthy. `false`, `0`, `''`, `null`, and `undefined` are falsy. The distinctions matter when translating a compact expression into plain English.

## How the pieces fit together

The diff lists some helper functions before `resolveConfig()`, but that isn't execution order. Start studying at resolver entry, then follow the helpers it calls.

```text
supplied inlineConfig
        │
        ▼
copy root and early compatibility containers
        │
        ▼
install early compatibility accessors
        │
        ▼
load/merge config file, select plugins, run config hooks
        │
        ▼
copy affected environment containers and normalize settings
        │
        ▼
run environment hooks and resolve environment options
        │
        ▼
resolve server, preview, CSS, and remaining config
        │
        ▼
finish compatibility conversion and plugin-name collection
        │
        ▼
resolved config ─────► original inlineConfig retained for restart
```

This is a simplified reading map, not a complete call graph. The important timing distinction is that some copies must happen before config hooks and others happen after them.

## 1. Copying the root and early compatibility options

[Source: config.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/config.ts#L1481)

**ELI5:** Make your own instruction sheet before writing on it. If the sheet refers to another shared sheet, copy that one before writing on it too.

```ts
let config: InlineConfig = { ...inlineConfig }
config.build = { ...config.build }
setupRollupOptionCompat(config.build, 'build')
```

The root copy makes replacing `config.build` safe. The build copy makes installing properties inside `config.build` safe. One copy doesn't do both jobs.

`setupRollupOptionCompat()` installs a getter/setter for `rollupOptions` that forwards to `rolldownOptions`. It changes the object even if it doesn't appear to change the option's value.

The same operation covers `worker`, `optimizeDeps`, and, when supplied, `ssr.optimizeDeps`. SSR needs a parent copy before its child can be replaced.

**TL;DR:** Early compatibility setup stays early, but its accessors land on copies.

**Trade-off:** Hooks now see different objects for these copied containers. A caller holding the original won't observe the compatibility accessors being installed. That is intentional, but it is a real identity change.

**Tests:** Frozen early inputs; a hook that checks the accessor is already installed and assigns through it; separate checks that later-written objects haven't been copied before the hook.

## 2. Copying the environments map and its entries

[Source: config.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/config.ts#L1569)

**ELI5:** Make your own list of environments before replacing entries in the list. Make your own environment entry before changing that entry's properties.

```ts
config.environments = { ...config.environments }
```

This occurs after config hooks. Later code assigns resolved entries into the map, so copying only the root config wouldn't be sufficient.

The client assignment looks dense:

```ts
const configEnvironmentsClient = (config.environments!.client = {
  ...config.environments!.client!,
})
```

It is equivalent to these steps:

```ts
const clientCopy = { ...config.environments!.client! }
config.environments!.client = clientCopy
const configEnvironmentsClient = clientCopy
```

Both the local variable and the working config now refer to the copy. Copying only into a local variable could leave the rest of resolution reading the original from the map.

The SSR branch copies an entry if it exists. The added branch isn't a request to create SSR in previously unsupported circumstances.

**TL;DR:** Replacing map entries and changing entry properties require protecting two different levels.

**Trade-off:** More containers are allocated. Keeping the assignments close together makes it possible to see that later reads use the new objects.

## 3. Environment warmup and asset settings

[Source: config.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/config.ts#L1647)

**ELI5:** Vite moves older instructions into their newer locations without writing those translations back onto your original pages.

```ts
configEnvironmentsClient.dev = {
  ...configEnvironmentsClient.dev,
  warmup: warmupOptions.clientFiles,
}
```

An environment copy can still share its nested `dev` object. Replacing `dev` protects the next level before adding warmup files. SSR warmup and `build.emitAssets` use the same pattern.

Putting `warmup` after the spread means it wins over an existing property, matching the previous direct assignment. Likewise, the `ssrEmitAssets !== undefined` condition continues accepting an explicit `false`.

**TL;DR:** Keep the existing translation and precedence; write the translated settings into copied nested objects.

**Tests:** Original objects lack the new properties while resolved environments contain the expected warmup lists and asset setting.

## 4. Writing client resolve settings back to the top level

[Source: config.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/config.ts#L1745)

**ELI5:** The final combined lookup instructions belong in the result, not in the caller's original instructions.

```ts
config.resolve = { ...config.resolve }
config.resolve.conditions = config.environments.client.resolve?.conditions
config.resolve.mainFields = config.environments.client.resolve?.mainFields
```

`resolve` here names options for finding modules. It is not a call to `resolveConfig()`.

**TL;DR:** Protect the top-level resolve object before putting merged client values into it.

**Tests:** Original conditions remain `['source']`; the resolved conditions include both `source` and `client`, with the expected main fields.

## 5. Removing a redundant optimizer alias before merging

[Source: config.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/config.ts#L1266)

**ELI5:** Two labels can point to the same options. Remove the redundant label from your working copy, not from the caller's object.

```ts
let optimizeDepsForMerge = optimizeDeps
if (
  optimizeDeps?.rolldownOptions &&
  optimizeDeps.rolldownOptions === optimizeDeps.rollupOptions
) {
  optimizeDepsForMerge = { ...optimizeDeps }
  delete optimizeDepsForMerge.rollupOptions
}
```

The equality compares references, not contents. The branch only runs when both names point to the same object and the Rolldown value is truthy.

`&&` stops when its left side is falsy, which makes the direct accesses on the right safe. Outside the branch, the local variable keeps its original value. The merge receives whichever value was selected.

**TL;DR:** Preserve the existing alias-handling condition while moving its `delete` onto a copy.

**Tests:** Explicit aliases and frozen options supplied by hooks. The result must retain working aliases without duplicating a plugin.

## 6. Optimizer `resolve` and `output`: why the `??= {}` lines disappear

[Source: config.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/config.ts#L1287)

**ELI5:** “Find a box, or make an empty one” becomes “make your own box, copying any contents.” You don't need to check whether the box exists again afterward.

Earlier initialization becomes:

```ts
rolldownOptions.resolve = { ...rolldownOptions.resolve }
rolldownOptions.output = { ...rolldownOptions.output }
```

The old later `resolve ??= {}` and `output ??= {}` lines are therefore redundant. Initialization hasn't disappeared; it now also separates supplied objects.

The defaults remain:

```ts
rolldownOptions.resolve.symlinks ??= !preserveSymlinks
rolldownOptions.output.topLevelVar ??= true
```

These fill missing values and preserve explicit `false`. The copied objects also receive applicable esbuild-to-Rolldown conversions.

**TL;DR:** Initialize and copy once, then run the existing conversions and defaults.

**A nuance about the outer copy:** The preceding `merged.rolldownOptions = { ...merged.rolldownOptions }` is distinct from the nested copies. For ordinary object-valued input, `mergeWithDefaults` already builds a fresh outer Rolldown object because defaults include `rolldownOptions: {}`. That outer spread appears redundant on that path. It remains in the submitted patch; removing it would warrant checking compatibility fallback inputs. The nested objects do not get the same protection from those defaults.

**Tests:** Frozen nested options, explicit-value precedence, and independently resolved environment settings.

## 7. Optimizer `transform`, `moduleTypes`, and esbuild options

[Source: config.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/config.ts#L1328)

**ELI5:** Translate the older instructions only where the newer instructions haven't already made a choice.

For definitions, the existing condition requires an esbuild value and no Rolldown value. Inside that condition:

```ts
rolldownOptions.transform = {
  ...rolldownOptions.transform,
  define: merged.esbuildOptions.define,
}
```

The copy protects `transform`; the condition preserves precedence. The definitions object itself can remain shared because this step assigns it rather than editing inside it.

For loader conversion:

```ts
const moduleTypes = (rolldownOptions.moduleTypes = {
  ...rolldownOptions.moduleTypes,
})
```

This puts the copy into the working options and gives the loop a convenient reference to it. The loop keeps existing entries and skips the same unsupported loader kinds as before. For example, an existing `.txt: 'json'` wins over an esbuild `.txt: 'text'` instruction.

Finally, esbuild options are copied before adding their `preserveSymlinks` default.

**TL;DR:** Keep conversion rules; give their writes separate containers.

**Trade-off:** These are explicit copies around known write paths. A loader map may get copied even if no entries ultimately qualify. This isn't an automatic system that detects the first actual write.

## 8. Copying the optimizer plugin list before appending

[Source: config.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/config.ts#L1443)

**ELI5:** Make your own guest list before adding Vite's guests. Don't add them to the original list again every time you reopen it.

The runtime operation is approximately:

```ts
const plugins = (options.plugins || []).slice()
plugins.push(...convertedPlugins)
options.plugins = plugins
```

The real code includes a TypeScript assertion. It doesn't convert the value at runtime. `.slice()` creates a new list containing the same plugin objects.

The fallback uses `||` because the previous code accepted falsy plugin values, including `false`. An earlier candidate used `plugins?.slice() ?? []`, which tries to call `.slice()` on `false`. We observed and fixed that regression.

**TL;DR:** Append generated plugins to a fresh list, keeping the caller's list reusable.

**Why this can rebuild the cache:** Optimizer plugin names enter the config hash. Appending another converted plugin changes that list on the next resolution. Merely writing the same default twice needn't change the resulting hash.

**Tests:** A real unchanged restart reuses the cache; a plugin-name change causes a rebuild. The `false` regression resolves frozen options twice and checks the converted name.

## 9. Server and preview allowed hosts

[Server source](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/server/index.ts#L1272) · [Preview source](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/preview.ts#L69)

**ELI5:** Vite can extend its allowed-host list without changing the list you handed it.

```ts
allowedHosts: Array.isArray(_server.allowedHosts)
  ? _server.allowedHosts.slice()
  : _server.allowedHosts
```

The option can be an array or `true`. Copy arrays and retain the boolean alternative. Preview copies its explicitly supplied array; otherwise it retains the existing fallback to the resolved server option.

**TL;DR:** Copy lists, preserve non-list settings and inheritance.

**Tests:** Frozen original lists remain unchanged; resolved lists include the configured and derived hosts. These are input-isolation checks, not additional demonstrated optimizer-cache bugs.

## 10. Filesystem `allow`: unpacking the ternary

[Source: server/index.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/server/index.ts#L1279)

**ELI5:** If the caller supplied a list, use your own copy. If no list was supplied, start with the workspace root.

```ts
allow: raw?.fs?.allow ? raw.fs.allow.slice() : [workspaceRoot]
```

Expanded:

```ts
const supplied = raw?.fs?.allow
let allow
if (supplied) {
  allow = supplied.slice()
} else {
  allow = [workspaceRoot]
}
```

An empty array is truthy, so `[]` remains an empty list at this selection step. Vite can subsequently add required or discovered paths. The fallback behavior matches the previous expression for supported array-or-absent inputs.

The copy is needed before package-manager discovery appends paths. A later `.map()` that produces normalized paths doesn't undo an earlier `.push()` into the caller's array.

**TL;DR:** Protect the list before its first mutation, not just before its final result is returned.

**Tests:** A temporary pnpm store record forces discovery to run. The original list stays `['src']`; the resolved list contains absolute source and store paths. Cleanup runs in `finally`.

## 11. HMR compatibility accessors

[Source: utils.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/utils.ts#L1417)

**ELI5:** Vite attaches a forwarding connection between old HMR settings and newer WebSocket settings. Attach it to Vite's copy, not the caller's object.

```ts
if (serverConfig.hmr === true) {
  serverConfig.hmr = {}
} else if (serverConfig.hmr) {
  serverConfig.hmr = { ...serverConfig.hmr }
}
```

The existing disabled-HMR/WebSocket early return stays in place. `true` becomes an object as before. An existing object gets copied before accessors are installed.

The accessor for `hmr.port` reads/writes the associated `serverConfig.ws.port`. Reinstalling an accessor on a shared HMR object can connect it to a later merge result, affecting what an earlier result observes.

**TL;DR:** Keep forwarding functional and attached to the correct result.

**Tests:** Both directions of port forwarding work. A second merged result can change without redirecting the first result's accessor. The caller's port remains a plain unchanged value.

## 12. Nested environment build options in `mergeConfig`

[Source: utils.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/utils.ts#L1356)

**ELI5:** Copying the folder doesn't copy the sheet inside it. Copy the build sheet before installing its compatibility properties.

```ts
if (isObject(merged.build)) {
  merged.build = { ...merged.build }
  setupRollupOptionCompat(merged.build, 'build')
}
```

The helper already copied the environment entry. The new line copies its nested build object. This affects public `mergeConfig()` calls as well as use during resolution.

**TL;DR:** The merge result gets its own build object and accessors; the caller's build object keeps its original properties.

**Trade-off:** Callers can observe the changed build-object identity. It is part of the intended input-isolation change.

**Tests:** Three starting configurations exercise different merge branches: no map, an empty map, and an existing client build.

## 13. Lightning CSS defaults

[Source: plugins/css.ts](https://github.com/vitejs/vite/blob/9641e4f018ed1a2917d617832ff69560c86d0ef9/packages/vite/src/node/plugins/css.ts#L230)

**ELI5:** If no browser targets were chosen, put Vite's choice into a copy. If targets were chosen, this step has no reason to change anything.

```ts
if (
  resolved.transformer === 'lightningcss' &&
  resolved.lightningcss?.targets == null
) {
  resolved.lightningcss = {
    ...resolved.lightningcss,
    targets: convertTargets(/* Vite's baseline */),
  }
}
```

The missing-target condition moved from an inner `??=` to the outer `if`. `== null` deliberately includes both null and undefined, preserving the old fallback behavior. Explicit targets keep the original object shared through this step.

**TL;DR:** Add default targets to a copy only when targets are missing.

**Tests:** Missing targets get defaults, null gets defaults, and explicit targets retain their object identity. No CSS compilation is needed to test this configuration behavior.

## Reading the tests without getting lost

Each test has three jobs: build an input that would expose a mistake, run the real code, and inspect the outcome.

```ts
const original = Object.freeze({})  // Catch writes to the source.
const result = await runRealCode(original)
expect(original).toEqual({})        // Source contents unchanged.
expect(result.someSetting).toBe(true) // Required work happened.
```

`toBe` checks identity for objects. `toEqual` compares contents. `toMatchObject` checks selected properties and permits others. `test.each()` runs separate cases using shared test code. `vi.fn()` records calls; it doesn't mean the entire resolver is mocked. Type annotations don't freeze anything; `Object.freeze()` does.

There are 22 added cases in the submitted patch:

| Group | Cases | Purpose |
| --- | ---: | --- |
| Early frozen options | 1 | Keep original properties unchanged while resolved aliases exist. |
| Early hook timing | 1 | Copy and compatibility setup happen before the hook. |
| Late hook timing | 1 | Preserve shared references and don't read the observable getter prematurely. |
| Environment normalization | 1 | Warmup/assets reach results without changing originals. |
| Resolve write-back | 1 | Preserve input and merged output values. |
| Combined server/preview/fs/CSS/HMR | 1 | Check the full resolution path with frozen inputs. |
| Explicit/null CSS targets | 2 | Preserve explicit identity and null fallback. |
| Top-level/custom optimizer conversion | 2 | Protect nested writes in both placements. |
| Explicit Rolldown precedence | 1 | New copying mustn't override explicit options. |
| Explicit aliases | 1 | Keep aliases connected without duplicating plugins. |
| Disabled Rolldown plugins | 1 | Preserve the valid false fallback during conversion. |
| Hook-supplied optimizer options | 2 | Handle objects introduced after entry-time copies. |
| Shared environment options | 1 | Resolve differing settings independently. |
| Environment-build merges | 3 | Cover three distinct merge starting points. |
| Successive HMR merges | 1 | Each result's accessors follow its own WebSocket options. |
| Package-manager filesystem discovery | 1 | Actually exercise the array-appending path. |
| Real restart and invalidation | 1 | Cache reuse when unchanged; rebuild after a plugin-name change. |

The restart test checks that environments were actually replaced, not merely that the hashes match. It also checks that optimization runs after a meaningful change, so an implementation that always reused the cache would fail.

Some tests preserve behavior that already worked on the base. Passing on old code doesn't make a test useless: it may prevent a repair from breaking compatibility. Frozen inputs are a detection technique, not evidence that most users supply frozen configs. The exact old-base failure count for the final 22 cases isn't established by our local reports; don't treat an estimate as a measured result.

## What could go wrong with the approach?

### References and property behavior change

Two equivalent objects aren't the same object. Code holding an original reference no longer sees the covered Vite writes. Object spread reads enumerable getters and creates ordinary data properties; it doesn't preserve arbitrary prototypes or descriptors.

The patch intentionally regenerates the compatibility accessors it needs on working objects. It isn't a general guarantee for every exotic configuration object.

### Shallow copying has a boundary

Nested services and plugin objects often remain shared. A hook can mutate shared input, and a future Vite write to a previously read-only nested value might require another copy. The patch doesn't recursively protect everything.

### Allocation and maintenance cost

Copying an object costs work proportional to the properties copied; copying a list costs work proportional to its length. These copies occur during configuration resolution, not once per transformed source file.

Temporary copies become eligible for garbage collection when unreachable. Copies retained by resolved config live with it. An old config retained by application/plugin code also retains the objects reachable through it. We haven't measured retained heap or worst-case large configs.

The maintenance burden is that a future write needs the same reference check. The tests make many existing expectations visible, but they don't automatically audit new code.

## Alternatives and why we didn't choose them

| Alternative | Benefit | Cost or limitation | Assessment |
| --- | --- | --- | --- |
| Copy only the root | Very little code. | Nested objects remain shared. | Insufficient for the covered writes. |
| `mergeConfig({}, inlineConfig)` | Reuses existing merge logic. | Can preserve nested references and itself install compatibility accessors on shared nested build objects. Also changes environment identity earlier. | Doesn't replace the needed protections. |
| Deep-clone the whole config | Centralizes copying. | Requires decisions about plugins, functions, services, prototypes, cycles, and intended identity; can change hook observations. | A much larger behavioral change. |
| Clone selected paths once at entry | One visible list of copies. | Later hooks can supply new objects; copying late-written values early can affect identity/getter timing. | Simpler location, harder timing semantics. |
| Fix only plugin accumulation | Smallest fix for the demonstrated cache symptom. | Leaves other direct resolver mutations in place. | Valid narrower scope, but the maintainer discussion supported examining the broader problem. |
| Deduplicate plugins or ignore duplicate names in the hash | Could suppress this symptom. | Doesn't repair mutated input, may alter intentional plugin behavior, and can hide relevant differences. | Poor substitute for avoiding the accidental append. |
| Build every resolved object explicitly from scratch | Makes result construction clear. | Large rewrite of merging and compatibility behavior; must preserve all options and extension points. | Possible future design, unnecessary for this repair. |
| Automatic copy-on-write proxies | Could intercept writes centrally. | Adds proxy identity, accessor, array, and interoperability questions. | Too much machinery for these known sites. |

**My assessment:** the submitted approach is a reasonable incremental repair. Its strength is preserving the surrounding resolution sequence. Its weakness is that reference safety remains something maintainers must consider at individual write sites.

## Evidence and its limits

The submitted commit passed 1,002 local unit tests with 3 skipped, full repository build/lint/formatting, and Vite typecheck. [Upstream CI for that exact commit](https://github.com/vitejs/vite/actions/runs/34053022775) passed Linux Node 20/22/24/26, macOS Node 24, and Windows Node 24.15.0 jobs.

The local timing comparison used an earlier commit with identical production code. Baseline and candidate batch averages overlapped around 0.34 ms per resolution. Added test bodies totaled about 92 ms in a focused run. Neither figure measures full startup, all downstream configurations, or memory retention. See [the timing method and results](PERFORMANCE.md).

## A short self-check

Try answering before expanding each answer.

<details>
<summary>Why doesn't copying config also protect config.build?</summary>

The root copy holds the same nested build reference until build is copied separately.

</details>

<details>
<summary>Why is the new local moduleTypes variable assigned into rolldownOptions too?</summary>

The loop and the rest of resolution must use the same copied object. A detached local copy wouldn't replace the value that later code reads.

</details>

<details>
<summary>Why preserve false instead of treating it as a missing setting everywhere?</summary>

False is an explicit choice for options such as minify. Their defaulting uses nullish or undefined checks. The plugin-list fallback is a different case whose existing behavior accepts false as no list. The option's meaning determines the condition.

</details>

<details>
<summary>Why isn't every mutated input automatically a cache miss?</summary>

Only a subset of resolved settings is hashed, and a repeated write can produce the same final value. An accumulating plugin list changes the hashed names; defaulting a missing value to true can resolve to true both times.

</details>

<details>
<summary>Why doesn't the patch copy everything before running hooks?</summary>

Hooks can observe references and getters, and can supply new objects. Keeping copies near the relevant writes preserves more of the existing timing and covers later-supplied values.

</details>

## Retention and handoff

Retained by request as a study document under the [Vite target map](../../targets/vite/map.md), associated with the web-tooling runtime-correctness programme. This is documentation of already-examined source and previously executed checks, not a new scout or a new upstream submission.

The source explanations are scoped to the exact revisions at the top of this guide. The linked CI run is execution evidence for that submitted commit. [The timing note](PERFORMANCE.md) owns the local measurement method, limitations, and artifacts. No new Vite validation or benchmark execution was performed while adding this document to Fieldwork.

Self-review checked the transferred text, portable links, reference-policy compliance, benchmark report structure and summary arithmetic, and retained harness syntax. Remaining uncertainties are the generality of performance observations, untested config objects, and the exact final old-base failure count. No implementation change or new investigation is proposed. No third-party upstream writes were performed during this documentation task.
