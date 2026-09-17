## In simple words

Rspack's SWC minimizer persistent cache currently trusts the 8-byte key stored beside a cached minimized value as the identity of that value. The serialized value carries the minimized source and extracted-comment data, but carries no copy of the logical cache key that produced it.

At `web-infra-dev/rspack@c336816e002ee7bf9c275a1aa949e1f708364899`, this leaves a semantic gap after storage integrity succeeds: two minimize records can exchange their physical keys, the pack integrity hash can be recomputed, and recovery will place each decoded value under the exchanged key. The minimizer then sees a cache hit for the expected key and installs the other asset's minimized source.

The public reproducer for `web-infra-dev/rspack#14862` reports exactly that outcome on `@rspack/core@2.1.4`: `a.js` receives B's minimized output and `b.js` receives A's after the two 8-byte keys are swapped and the pack hash is recomputed. Current main still contains the same key/value ownership path.

I prepared a user-owned draft repair testbed at `teamleaderleo/rspack#1`, pinned to current upstream commit `c336816e002ee7bf9c275a1aa949e1f708364899`. The candidate stores the logical `MinimizeCacheKey` inside each serialized minimize entry and drops recovered entries whose embedded key disagrees with the physical storage key. A native `cacheCases/common/minimize-cache` discriminator corrupts the two keys only after compiler close has flushed the persistent cache, then expects both mismatched entries to miss and recompute on the next cold start.

Current answer: the bug mechanism is source-confirmed on current Rspack main, the external report supplies an executed reproduction on 2.1.4, and a current-main target-native repair discriminator is prepared in the user-owned fork. Upstream remains untouched and upstream contact authorization remains `false`.

## Claim

- Fieldwork parent: `#457`
- Candidate: **H — Rspack persistent-cache logical-key recovery**
- Target: `web-infra-dev/rspack`
- Exact target revision: `c336816e002ee7bf9c275a1aa949e1f708364899`
- Public anchor: `https://github.com/web-infra-dev/rspack/issues/14862`
- External reproducer revision: `hardfist/rspack-persistent-cache-minimize-recovery-repro@8fff2d631859953a12acd385e7eba16f002c3522`
- User-owned repair testbed: `https://github.com/teamleaderleo/rspack/pull/1`
- Repair head after native discriminator/format cleanup: `1af42061073e0d5c82bea1b5b169a539c7c4e483`
- Upstream-contact authorization: `false`

Exact question:

> After persistent-cache bytes pass storage integrity and deserialization, where does Rspack bind a recovered minimize value back to the exact logical cache key that produced it?

Answer at the pinned revision: **nowhere inside the serialized minimize value or its recovery path.** Recovery treats the physical storage key as the logical key.

## Source ownership map

### 1. The minimizer computes the logical key from live asset inputs

`crates/rspack_plugin_swc_js_minimizer/src/lib.rs` computes `MinimizeCacheKey` from:

- original source bytes,
- minimizer option hash,
- filename,
- `is_module` mode.

It then calls `cache.get(key)`. A hit immediately replaces the current asset source with the cached source and marks the asset minimized.

This is the semantic boundary: a cached value returned under key `K` must have been produced for the live inputs that hash to `K`.

### 2. Save writes identity outside the serialized value

`crates/rspack_core/src/cache/persistent/occasion/minimize/mod.rs` defines serialized `Entry` with only:

- minimized `source`,
- optional extracted-comments source and filename.

`MinimizeCacheKey(u64)` becomes the 8-byte storage key through `to_ne_bytes()`. `MinimizeOccasion::save()` encodes `Entry` and calls `storage.set(SCOPE, key.to_bytes(), bytes)`.

So identity lives beside the value in storage; the value has no self-describing key.

### 3. Filesystem integrity authenticates the pack bytes as a set of key/value bytes

`crates/rspack_storage/src/filesystem/db/bucket/pack/mod.rs` serializes each record as:

1. key length and value length,
2. raw key bytes,
3. raw value bytes.

The pack content hash covers every key and value. Bucket load compares that hash against metadata before returning the records.

That check detects accidental byte changes when metadata stays unchanged. The public #14862 reproducer deliberately recomputes the integrity hash after exchanging two keys, so storage accepts the mutated pack as internally consistent.

### 4. Recovery trusts the physical key

`MinimizeOccasion::recovery()` calls `storage.load("occasion_minimize")`, parses each loaded storage key with `MinimizeCacheKey::from_bytes`, decodes `Entry`, and inserts the decoded output into the in-memory map under the parsed storage key.

There is no second identity source to compare against because `Entry` carries no logical key.

### 5. The generic occasion layer adds no later key binding

`CacheContext::load_occasion()` delegates to `occasion.recovery()` and returns a successful recovered artifact. The `Occasion` trait itself defines recovery/save/reset behavior and adds no independent entry-identity validation.

That completes the path from live input key to persisted bytes and back to asset replacement.

## Invariant and violation

Invariant:

> A recovered `CachedMinimizeEntry` returned under `MinimizeCacheKey K` must have been generated from the asset inputs whose minimizer key is `K`.

Current persisted representation contains two independent pieces:

- physical key `K`,
- serialized minimized output `V`.

Recovery assumes `K -> V` is the original association after pack integrity succeeds. An integrity-valid mutation can produce `K1 -> V2` and `K2 -> V1`. Both entries decode successfully, both keys have valid length, and both become cache hits for the wrong assets.

## External executed reproduction

`hardfist/rspack-persistent-cache-minimize-recovery-repro@8fff2d631859953a12acd385e7eba16f002c3522` uses the public compiler API and published `@rspack/core@2.1.4`.

The reproducer:

1. builds two production entrypoints with filesystem persistent cache,
2. finds `occasion_minimize/0.pack`,
3. verifies there are exactly two 8-byte minimize keys,
4. verifies the existing pack hash,
5. exchanges the two key byte sequences while leaving values in place,
6. recomputes the same pack hash and updates `_meta`,
7. starts a fresh Node process,
8. inspects `dist/a.js` and `dist/b.js`.

Reported result:

- recovery exits successfully,
- `a.js` contains B and lacks A,
- `b.js` contains A and lacks B.

This external execution is useful behavior evidence. The current-main claim above comes from reading the pinned current source and preparing the same discriminator against that exact revision.

## Competing explanations challenged

### Pack integrity may already bind the pair tightly enough

It binds the current pack bytes to the recorded content hash. The hash is unkeyed and recomputable. Once the reproducer updates `_meta`, `Bucket::load_all()` sees a valid pack and returns the exchanged `(key, value)` pairs. This explains why storage corruption detection and semantic identity are separate checks.

### Cache version or build-dependency validation may reject the cache first

The mutation leaves cache version and build dependencies unchanged. The relevant meta validation occurs before occasion recovery and has no knowledge of the original per-entry minimize key/value association. Current minimize recovery therefore receives the mutated records when the wider cache generation remains valid.

### The defect may live only in the pack layer

Pack storage correctly returns the key/value records it was given after its integrity check passes. The minimize occasion gives semantic meaning to those bytes and currently stores that meaning only in the key. The narrow repair belongs naturally at the minimize serialization/recovery boundary.

### A `u64` cache-key collision may be the real bug

The public reproducer exchanges two distinct existing keys. No hash collision is required. Embedding the same `u64` key inside the value preserves the current collision model while detecting exchanged labels.

### Rejecting a bad entry may leave the artifact unusable

The minimizer already has a normal cache-miss path: it minimizes the current live source, records a new `(MinimizeCacheKey, CachedMinimizeEntry)`, and saves dirty entries after asset processing. A rejected recovered entry therefore flows into ordinary recomputation.

A neighboring current Rspack cache change, PR `#15047`, also uses conservative recovery: source-map cache data that cannot be reconstructed from the current asset is treated as invalid so computation can proceed from live input. That is compatible with the reject-and-recompute direction used here.

## Repair candidates

### A. Embed the logical key inside `Entry` and compare during recovery — recommended

Candidate in `teamleaderleo/rspack#1`:

```rust
#[cacheable]
struct Entry {
  pub cache_key: u64,
  // source/comments...
}
```

Save writes `cache_key: key.0`. Recovery decodes the entry, compares `entry.cache_key` with the physical `MinimizeCacheKey`, logs and skips a mismatch, then lets the minimizer's normal miss path recompute.

Advantages:

- tiny ownership-local change,
- direct check of the violated invariant,
- no duplicate key derivation logic,
- keeps unaffected entries reusable,
- preserves the current `u64` key model.

### B. Persist full provenance and recompute the key during recovery

Persist original source/options/filename/module mode beside each output and rebuild the hash at recovery time.

This duplicates key inputs, grows the cache, and pulls minimizer-specific derivation concerns into recovery. The embedded key provides the required pair binding with much less data.

### C. Reset the whole minimize scope on any mismatch

This is conservative and simple but discards unaffected minimize entries. Per-entry rejection already has a natural recomputation path.

### D. Replace the pack content hash with an authenticity mechanism

That would target a broader hostile-mutation problem across storage. Candidate H is narrower: semantic key/value association for minimize entries after an integrity-valid read. The ownership-local binding solves that exact defect.

## Serialization compatibility

Adding `cache_key` changes the serialized `Entry` layout. Existing minimize entries created by older code may fail decoding under the new layout. Current recovery already treats per-entry decode failure as recoverable: it logs the decode error, skips that entry, and returns the remaining artifact. The skipped key then becomes a normal minimizer cache miss and can be rewritten in the new format.

Execution should still confirm this upgrade path before any merge-ready recommendation. A global cache-version bump appears heavier than the current per-entry recovery behavior requires.

## Native discriminator prepared on current main

Rspack already has `tests/rspack-test/cacheCases/common/minimize-cache`, exercised by `tests/rspack-test/Cache.test.js`. The case has exactly two minimized JavaScript assets and performs repeated cold restarts through `NEXT_START()`.

The fork testbed extends that existing case instead of adding a new runner.

Important sequencing detail: Rspack `Compiler.close()` runs shutdown hooks, cache shutdown, and the native compiler close before invoking its callback. The discriminator wraps `compiler.close` and mutates the pack only after the original close callback fires. That means persistent writes have completed before corruption.

Prepared sequence:

1. Build 0: empty cache -> `0` hits, `2` misses.
2. Close compiler and exchange the two physical keys; recompute `_meta` pack hash.
3. Build 1 on the repair candidate: both embedded/physical key pairs disagree -> `0` hits, `2` misses; both assets recompute.
4. Close and restart again.
5. Build 2: repaired entries are persisted under matching keys -> `2` hits, `0` misses.
6. Existing later changed-file and HMR assertions continue.

On unchanged current-main code, step 3 has no mismatch check and therefore takes the exchanged records as hits. The public reproducer shows the corresponding semantic cross-wire on 2.1.4.

## Testbed state

User-owned fork only:

- base branch: `fieldwork/457-h-base-c336816e`
- repair branch: `fieldwork/457-h-minimize-key-binding`
- draft PR: `teamleaderleo/rspack#1`
- repair commit: `727de9e05b1809dc8ffb1ebc8c6c8e07aab48c71`
- native discriminator commit: `087cedea22fa63387f31292af4c875439812006d`
- format cleanup head: `1af42061073e0d5c82bea1b5b169a539c7c4e483`

The first CI pass on the discriminator reported JavaScript lint success and a formatter-only failure in the modified test config. The formatter-only issue was corrected in `1af42061073e0d5c82bea1b5b169a539c7c4e483`. Broader current-head CI is execution evidence to collect before promoting this from prepared repair to repair-ready.

No branch, comment, issue mutation, reaction, workflow action, or pull request was created in `web-infra-dev/rspack`.

## Overlap check

At investigation time on 2026-08-11:

- `web-infra-dev/rspack#14862` was open, unassigned, and had zero comments.
- An open-PR search tied to `14862` found no repair PR.
- A broader minimize/cache/key PR search found no equivalent repair for this logical-key association defect.
- `web-infra-dev/rspack#14864` and `#14865` concern missing snapshot recovery and stale outputs; they are neighboring persistent-cache correctness cases with different ownership paths.
- Open PR `#15047` is a neighboring source-map persistent-cache change and a useful reject/recompute precedent, but it does not repair minimize key/value association.

## Evidence ledger

| Evidence | Class | Result |
| --- | --- | --- |
| Current minimize key derivation and cache-hit consumption at `c336816e...` | `source-read` | logical key is computed from live source/options/filename/module mode; hit installs cached source |
| Current `MinimizeOccasion` save/recovery | `source-read` | serialized value carries no logical key; recovery trusts physical key |
| Current filesystem pack hashing/load | `source-read` | integrity covers current key/value bytes and accepts records when recomputed hash matches metadata |
| Generic `CacheContext` / `Occasion` path | `source-read` | adds no later per-entry key binding |
| `#14862` + reproducer at `8fff2d6...` | external executed report | exchanged keys + recomputed hash cross-wire A/B on `@rspack/core@2.1.4` |
| `teamleaderleo/rspack#1` repair candidate | `target-test-prepared` | embeds logical key and rejects mismatch on exact current base |
| Existing Rspack `minimize-cache` case extended with post-close corruption | `target-test-prepared` | expects reject/recompute then clean cold-cache hits |
| First fork CI pass | CI hygiene evidence | JS lint passed; formatter-only test-file failure corrected on next head |

## Confidence and claim scope

Confidence in the current-main mechanism: **high**.

The source path is short and complete from key derivation through persistence, pack verification, recovery, cache lookup, and asset replacement. The external reproduction directly exercises the same representation. The remaining gap is current-main execution of the prepared discriminator and upgrade-compatibility confirmation.

Claim scope is deliberately narrow: **integrity-valid minimize cache records can lose semantic key/value association because the serialized value lacks its logical key**.

This finding does not attempt to redesign storage integrity across every persistent-cache occasion.

## Recommended next move

1. Let the current fork PR execute its native cache case and CI on the exact pinned base.
2. If the discriminator passes, classify the repair as `target-executed` and inspect the complete fork diff once more.
3. Add or adjust upgrade-compatibility coverage if old `Entry` bytes produce any behavior beyond per-entry miss/recompute.
4. Keep `web-infra-dev/rspack` read-only until explicit upstream-contact authorization exists.
