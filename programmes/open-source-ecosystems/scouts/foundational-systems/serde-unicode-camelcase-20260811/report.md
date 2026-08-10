## In simple words

Current Serde `camelCase` rename logic still slices the first **byte** of a Rust identifier. That panics when the first Unicode scalar uses more than one UTF-8 byte. Open Serde issue [#2953](https://redirect.github.com/serde-rs/serde/issues/2953) reports the field case with CJK identifiers; the same current source expression exists independently in the enum-variant path.

A Serde maintainer has already stated the intended direction on #2953: non-ASCII case changes should be supported using Unicode-aware case conversion. The bounded candidate in this scout therefore does one thing: replace the two first-byte camelCase operations with a helper that lowercases the first Unicode scalar and preserves the remainder. Broader conversion of every Serde rename rule from ASCII-only to Unicode case mapping stays outside this candidate.

## Scout identity

- Programme: `open-source-ecosystems`
- Parent lane: Fieldwork #211 / OE-05 foundational libraries
- Target: `serde-rs/serde`
- Exact public source: `747814f7d5fbab872df3b02f070c165b91bde062`
- Source subject: `Release serde_derive_internals 0.30.0`
- Primary owner: `serde_derive/src/internals/case.rs`
- Public overlap owner: Serde issue [#2953](https://redirect.github.com/serde-rs/serde/issues/2953)
- Matching public repair found in focused PR search: none
- Owned Fieldwork path: `programmes/open-source-ecosystems/scouts/foundational-systems/serde-unicode-camelcase-20260811/`
- Upstream contact authorized: `false`
- Upstream target remains read-only

## Evidence state

Current at first materialization:

- `source-read`: exact current Serde source and tests inspected.
- `documented`: maintainer direction on #2953 supports Unicode-aware case changes.
- `target-test-prepared`: deterministic regression materializer and candidate patch are retained here.
- `target-executed`: pending exact-head execution carrier.

No local Rust toolchain is available in the chat execution container, so local compilation is not evidence. Exact target execution is delegated to an owned Fieldwork Actions carrier.

## Source map

Pinned file:

`serde_derive/src/internals/case.rs`

Current enum-variant camelCase branch:

```rust
CamelCase => variant[..1].to_ascii_lowercase() + &variant[1..],
```

Current field camelCase branch:

```rust
CamelCase => {
    let pascal = PascalCase.apply_to_field(field);
    pascal[..1].to_ascii_lowercase() + &pascal[1..]
}
```

Both expressions assume byte index `1` is a character boundary.

Rust identifiers are UTF-8 strings. CJK, Greek, accented Latin, and many other valid identifier starts occupy more than one byte. Slicing `[..1]` or `[1..]` on such strings panics before the rename can complete.

## Existing test map

The same file already contains direct unit tests:

- `internals::case::rename_variants`
- `internals::case::rename_fields`

Those cover ordinary ASCII cases including `Outcome`, `VeryTasty`, `very_tasty`, `A`, and `Z42`. They do not cover a non-ASCII leading scalar.

The workspace contains:

```text
serde
serde_core
serde_derive
serde_derive_internals
test_suite
```

The execution carrier can therefore test both the internal rename owner and a user-facing derive compile probe without changing public upstream state.

## Public issue and maintainer direction

Serde issue [#2953](https://redirect.github.com/serde-rs/serde/issues/2953) demonstrates a compile-time derive panic for:

```rust
#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Payload {
    项目名称: String,
}
```

The reported panic is the expected Rust UTF-8 boundary failure at byte index 1.

A maintainer response says Serde should support non-ASCII case changes and points toward Unicode `to_uppercase` / character-level case conversion. This removes ambiguity about whether non-ASCII identifiers are intentionally unsupported.

## Additional source finding — enum variants share the defect

`RenameRule::apply_to_variant` uses the same `[..1]` / `[1..]` expression for `CamelCase`.

That means a Unicode-leading enum variant such as:

```rust
enum Event {
    项目名称,
}
```

is independently exposed to the same panic when the enum container uses `#[serde(rename_all = "camelCase")]`.

This variant path is absent from the original issue report but has the same owner and the same repair. It belongs in the same bounded regression matrix.

## Candidate invariant

For Serde camelCase rename handling:

1. the first Unicode scalar is read on a character boundary;
2. camelCase lowercases that scalar using Unicode case mapping;
3. the remainder of the identifier is preserved exactly as produced by the existing path;
4. ordinary ASCII rename outputs remain unchanged;
5. case mappings that expand to more than one scalar are preserved rather than truncated;
6. unrelated rename rules retain their current behavior in this candidate.

## Candidate

Retained patch: `candidate.patch`.

Conceptually:

```rust
fn lowercase_first(value: &str) -> String {
    let mut chars = value.chars();
    match chars.next() {
        Some(first) => first.to_lowercase().chain(chars).collect(),
        None => String::new(),
    }
}
```

The helper replaces only the two camelCase byte-slice expressions.

### Why this cut

A broader patch could replace every `to_ascii_lowercase` / `to_ascii_uppercase` in Serde rename rules with Unicode conversion. That would alter existing serialized names under `lowercase`, `UPPERCASE`, `snake_case`, `SCREAMING_SNAKE_CASE`, and PascalCase-related paths for non-ASCII identifiers.

The current candidate avoids that wider compatibility decision. It repairs the panic, follows maintainer direction for camelCase's actual case change, and leaves broader Unicode rename semantics independently reviewable.

## Prepared regression matrix

`add-regression.py` materializes two exact unit tests into the target checkout after confirming both vulnerable baseline expressions are present.

### Field controls

```text
项目名称 -> 项目名称
Éclair   -> éclair
İ_value  -> i\u{307}Value
```

The Turkish capital dotted I is deliberate: Unicode lowercase expands it to `i` plus combining dot. The test proves the implementation does not assume one input scalar maps to one output scalar.

### Variant controls

```text
项目名称 -> 项目名称
Éclair   -> éclair
Σigma    -> σigma
```

### Existing ASCII controls

The existing `rename_fields` and `rename_variants` tests remain required GREEN controls.

## User-facing compile probes

The exact execution carrier creates a temporary crate outside the target workspace and points its dependency at the pinned local `serde` path with the `derive` feature enabled.

Two bins are compiled separately.

Field probe:

```rust
use serde::Deserialize;

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Payload {
    项目名称: String,
}
```

Variant probe:

```rust
use serde::Deserialize;

#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
enum Event {
    项目名称,
}
```

Baseline acceptance for RED:

- exact Serde commit checked out;
- each bin fails separately;
- stderr contains the byte-boundary panic signature.

Candidate acceptance for GREEN:

- apply only `candidate.patch`;
- both bins compile;
- prepared Unicode unit tests pass;
- existing ASCII rename tests pass;
- `cargo fmt --all -- --check` passes;
- `git diff --check` passes.

## Negative controls and challenged alternatives

### Alternative A — use the first scalar's UTF-8 byte length but retain ASCII lowercase

This would avoid the panic:

```text
find first char -> use len_utf8 for slicing -> to_ascii_lowercase
```

It is weaker than the maintainer-stated direction because `Éclair` would remain `Éclair` instead of becoming `éclair`.

Disposition: rejected for this candidate.

### Alternative B — Unicode-convert every rename rule now

This is semantically coherent but widens wire-name changes across unrelated rename modes.

Disposition: split. Revisit only with a dedicated compatibility matrix and maintainer demand.

### Alternative C — special-case CJK / multibyte inputs as unchanged

This fixes the reported sample while leaving accented/Greek first-character case behavior inconsistent.

Disposition: rejected.

## Consequence

The current defect is a procedural-macro panic during compilation. A valid Rust identifier plus a documented Serde rename mode can therefore turn ordinary derive use into an abrupt macro failure.

The likely repair is tiny and local to the rename helper, and the enum-variant sibling increases the value of fixing the owner once instead of patching one observer.

## Overlap

- Existing public issue owner: [serde-rs/serde#2953](https://redirect.github.com/serde-rs/serde/issues/2953).
- Focused public PR search for issue number / CJK / non-ASCII camelCase returned no matching repair at scout time.
- Fieldwork search found no existing dedicated Serde camelCase investigation beyond parent #211's target list.

Any future public submission remains a human decision and should attach to the existing upstream issue rather than opening a duplicate report.

## Current ranking

**High** pending exact target execution.

Reasons:

- current source directly retains the vulnerable expressions;
- upstream issue is open;
- maintainer semantic direction is present;
- field and variant paths share one tiny owner;
- deterministic RED/GREEN controls are cheap;
- patch surface is one production file;
- no matching repair PR found.

## Stop condition

Stop with one of:

1. exact-head field + variant RED, bounded candidate GREEN, and existing rename controls GREEN;
2. target source has moved and already repaired the expressions;
3. a current public PR appears owning the same repair;
4. execution exposes a Unicode mapping compatibility problem that requires a wider policy decision.

No automated upstream interaction is authorized or performed.
