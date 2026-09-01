## In simple words

This Serde round found one narrow deserialization contract defect worth promoting and three broader buffering/tagging branches worth keeping behind it.

The strongest branch is an internally tagged enum with `deny_unknown_fields` and a bare unit variant. Serde removes the tag, buffers every remaining map entry, then hands the buffer to `InternallyTaggedUnitVisitor`. That visitor deliberately drains every remaining key/value pair as `IgnoredAny` and returns success. The same container attribute does reject those fields when the variant is written as an empty struct variant (`A {}`). Two public Serde issues already describe this behavior, but a focused open-PR search found no active implementation for those issue numbers.

A narrow next gate is target-native execution at the pinned revision, followed by a regression test that compares `A` with `A {}` under the same internally tagged `deny_unknown_fields` container. If the pin reproduces the public control, the likely implementation owner is the unit-variant path in `serde_derive/src/de/enum_internally.rs` together with `InternallyTaggedUnitVisitor` in `serde/src/private/de.rs`.

Two other live buffering limitations remain visible in current source: buffered `Content` cannot represent 128-bit integers, and buffered deserializers do not preserve a format's `is_human_readable()` mode. Both already have older public reports and are adjacent to broader upstream buffering work, including the draft format-specific buffer proof of concept in PR #2912. Those are lower-priority Fieldwork branches unless the upstream architecture settles or a smaller compatible patch becomes clear.

Disposition: **PROMOTE the bare-unit `deny_unknown_fields` branch to target-native execution; PARK the broader buffering fidelity branches; PARK the duplicate internal-tag serialization case as an API/design question.**

## Target and evidence

- target: `serde-rs/serde`
- exact source revision read: `747814f7d5fbab872df3b02f070c165b91bde062`
- branch: `master`
- retrieval date: `2026-08-11` UTC+8
- upstream permissions observed through the connector: read-only for this agent
- upstream contact authorization: `false`
- evidence classes used: `source-read`, `model-executed`
- target-native execution: pending
- execution feasibility note: this runtime could not resolve GitHub from the container and had no usable local Rust checkout/toolchain cache, so the pinned target tree could not be executed here

The model probe is `probe.py`. It mirrors the current tag-removal and bare-unit/empty-struct control flow. It does not replace target-native Serde tests.

## Promote first — internally tagged bare unit ignores unknown fields

### User-visible contract

Consider these equivalent-looking variant shapes:

```rust
#[derive(serde::Deserialize)]
#[serde(tag = "type", deny_unknown_fields)]
enum Bare {
    A,
}

#[derive(serde::Deserialize)]
#[serde(tag = "type", deny_unknown_fields)]
enum EmptyStruct {
    A {},
}
```

For input containing the selected tag plus an extra field, the public issue control reports that `EmptyStruct::A {}` rejects the extra field while `Bare::A` accepts it:

```json
{"type":"A","token":"testToken"}
```

Public reports:

- https://github.com/serde-rs/serde/issues/2123
- https://github.com/serde-rs/serde/issues/2294

Issue #2294 contains a compact bare-unit reproduction and a direct bare-unit versus empty-struct control. As of this scout, focused open-PR searches for `2123` and `2294` plus `deny_unknown_fields` / internally tagged unit variants returned no matching open implementation.

### Current source path

Pinned derive path:

- https://github.com/serde-rs/serde/blob/747814f7d5fbab872df3b02f070c165b91bde062/serde_derive/src/de/enum_internally.rs

Pinned private deserialization path:

- https://github.com/serde-rs/serde/blob/747814f7d5fbab872df3b02f070c165b91bde062/serde/src/private/de.rs

The current internally tagged derive does this in two phases:

1. `TaggedContentVisitor` extracts the configured tag and buffers all other map entries into `Content::Map`.
2. The selected variant deserializes from a `ContentDeserializer` over that buffered content.

For a bare unit variant, `deserialize_internally_tagged_variant` chooses the `Style::Unit` arm and calls:

```text
Deserializer::deserialize_any(
    __deserializer,
    InternallyTaggedUnitVisitor::new(type_name, variant_name),
)
```

That arm receives `cattrs` as an argument to the function but does not branch on `cattrs.deny_unknown_fields()`.

`InternallyTaggedUnitVisitor::visit_map` then consumes every entry as `IgnoredAny`:

```text
while access.next_entry::<IgnoredAny, IgnoredAny>()?.is_some() {}
Ok(())
```

This is the mechanism that erases the extra field after the tag has already selected a unit variant.

### Why the empty-struct control differs

A struct variant is routed through `struct_::deserialize(..., cattrs, StructForm::InternallyTagged(...))`. The generated struct visitor has the ordinary unknown-field policy available through the container attributes. With `deny_unknown_fields`, unknown field identifiers become errors instead of an ignored arm.

So the semantic difference is introduced by variant shape inside Serde's generated/private path, rather than by the input format or application code.

### Existing target tests

Pinned test file:

- https://github.com/serde-rs/serde/blob/747814f7d5fbab872df3b02f070c165b91bde062/test_suite/tests/test_enum_internally_tagged.rs

The current test suite has broad internally tagged coverage for unit, newtype, map, struct, enum, ordering, and sequence forms. A focused search of this file found no `deny_unknown_fields` coverage. That leaves the public bare-unit/empty-struct discriminator uncovered in the main internally tagged test file.

### Model probe

Run from the Fieldwork repository:

```text
python programmes/open-source-ecosystems/scouts/foundational-systems/serde-20260811/probe.py
```

The model performs the same relevant state transitions:

1. remove `("type", "A")` as the tag;
2. retain `("token", "testToken")` in buffered content;
3. current bare-unit model drains the entry and returns `ok`;
4. the empty-struct + deny control returns `unknown field 'token'`.

It also checks tag-only success and duplicate-tag rejection as negative controls.

### Narrow implementation candidates

Ranked by preserving current behavior outside the requested attribute:

1. **Pass the deny policy into the internally tagged unit path.** Preserve the current drain-and-accept behavior when `deny_unknown_fields` is absent; reject any buffered entry when the container enables it.
2. **Route bare unit + deny through an empty-struct-equivalent visitor.** This would align bare `A` with `A {}` more directly, but may produce slightly different diagnostics or sequence behavior and therefore deserves focused compatibility tests.
3. **Teach `InternallyTaggedUnitVisitor` to carry a policy bit.** This is mechanically narrow but the error should retain the same unknown-field quality as generated struct visitors, rather than degrading to a generic map-length error.

The first target-native patch experiment should test map/struct token streams, unknown string and byte keys where supported, tag-only success, duplicate-tag behavior, and behavior without `deny_unknown_fields`.

### Recommendation

**PROMOTE — high mechanism confidence, medium promotion confidence until target-native execution.**

The behavior is already public as an upstream issue, so Fieldwork's contribution here is the source owner, current-pin confirmation by reading, control path, missing-test map, and a bounded next experiment. Any future human upstream work should refresh issue/PR ownership first.

## Park — 128-bit integers disappear at the buffering boundary

### Current source

Pinned private buffer type:

- https://github.com/serde-rs/serde/blob/747814f7d5fbab872df3b02f070c165b91bde062/serde_core/src/private/content.rs

`Content<'de>` currently has integer variants through `U64` and `I64`; it has no `U128` or `I128` variants. The comment says this buffer is used for untagged and internally tagged enums.

The current tag/content key visitor also carries an explicit source comment that it cannot capture `i128` and `u128`.

Public report:

- https://github.com/serde-rs/serde/issues/2576

That issue gives a format-level control: an `i128` field deserializes directly with CBOR implementations that support it, while the same value fails when an internally tagged enum forces the value through Serde's buffered `Content` path.

### Overlap and architecture

Issue #2576 points to open PR #2348 as containing 128-bit support:

- https://github.com/serde-rs/serde/pull/2348

Current `Content` also says it is obsoleted by format-specific buffer types in PR #2912:

- https://github.com/serde-rs/serde/pull/2912

PR #2912 is an open draft proof of concept from a maintainer for allowing formats to provide their own buffer type, initially motivated by format-specific semantics lost by `Content`.

### Recommendation

**PARK — current defect mechanism is source-visible, but implementation ownership and direction overlap broader live buffering work.**

Revisit if #2348/#2912 move, close, or leave a clearly independent 128-bit compatibility patch.

## Park — buffered deserializers lose `is_human_readable()`

Public report:

- https://github.com/serde-rs/serde/issues/2172

The report demonstrates an untagged `IpAddr` round trip through MessagePack: serialization uses the non-human-readable representation, then deserialization through an untagged enum buffers the input and asks `ContentRefDeserializer` to try variants. Because that buffered deserializer does not preserve the originating format's human-readable mode, the type sees the trait default instead.

Focused current-source search found no `is_human_readable` override on `ContentDeserializer` or `ContentRefDeserializer` at the pinned revision.

This is another example of the same architectural loss described by the current `Content` comment and PR #2912: a generic buffer reproduces values but cannot automatically reproduce every format-specific deserializer behavior.

### Recommendation

**PARK — real fidelity gap, broader compatibility owner.**

A future experiment should first decide whether the intended upstream direction is to propagate one boolean through Serde's generic buffer adapters or to rely on format-specific buffers. The latter can preserve more than this one bit.

## Park — internally tagged newtype payload can serialize a duplicate tag key

Public report:

- https://github.com/serde-rs/serde/issues/3029

Current `TaggedSerializer` emits the outer internal tag before delegating map/struct fields from a newtype payload. A payload struct can itself contain the same field name, producing two serialized keys.

Serde's derive-time conflict checker already rejects the analogous direct **struct variant** field/tag conflict. It cannot inspect an arbitrary newtype payload type in the same way, so this becomes an API/model problem: the inner payload may have a duplicate tag, may carry a contradictory tag value, or may intentionally expose that field when serialized independently.

The issue discussion suggests removing/skipping the inner tag field and connects the use case to the broader tagged-enum fallback discussion.

### Recommendation

**PARK — source behavior is deterministic, but a compatible library policy is wider than a local correctness patch.**

## Negative results retained

1. **Adjacently tagged duplicate tag/content fields are already guarded.** The map visitor tracks whether tag and content were seen and reports duplicate fields; the derive checks that configured tag and content names differ.
2. **Buffered sequence/map adapters check exhaustion.** Their helper deserializers call `end()` after visitors return, so a generic "visitor returned early and silently accepted trailing buffered values" hypothesis did not survive source review.
3. **Direct struct fields have explicit duplicate detection.** Generated map deserialization stores per-field state and calls `duplicate_field` on repeats.
4. **Flattened struct fields claim recognized buffered entries.** The current `FlatStructAccess` takes matching entries from the shared buffer; generic flattened maps deliberately borrow entries instead, which explains known multi-flatten-map ambiguity but did not yield a fresh narrow defect in this round.
5. **Internal direct struct-variant tag conflicts are checked at derive time.** The remaining duplicate-tag serialization case is limited to opaque newtype payloads, where the derive cannot inspect another type's serialized keys.
6. **No Serde-specific Fieldwork scout was found before the claim.** The parent OE-05 lane was the coordination owner for this round.

## Ranked next actions

1. Run the public #2294 bare-unit versus empty-struct control against exact Serde revision `747814f7d5fbab872df3b02f070c165b91bde062`.
2. Add a target-native regression in `test_suite/tests/test_enum_internally_tagged.rs` that proves tag-only success, extra-field rejection under `deny_unknown_fields`, and unchanged extra-field acceptance when the attribute is absent.
3. Prototype the smallest policy-aware unit visitor or generated unit branch, then compare diagnostics with the empty-struct control.
4. Refresh upstream issue/PR ownership immediately before any human-facing implementation or submission.
5. Keep #2576/#2172 behind #2912/#2348 architecture movement unless a separate compatibility test exposes a smaller independent owner.

## Authority

This scout performed read-only inspection of `serde-rs/serde`. No upstream issue, pull request, review, comment, reaction, branch, email, or other public interaction was created or changed.
