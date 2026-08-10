# Serde Unicode camelCase scout — 2026-08-11

## In simple words

Current Serde `camelCase` rename logic still slices the first **byte** of a Rust identifier. That panics when the first Unicode scalar occupies more than one UTF-8 byte. Open Serde issue [#2953](https://redirect.github.com/serde-rs/serde/issues/2953) reports the field case with CJK identifiers; the same current source expression independently exists in the enum-variant path.

The first exact carrier already reproduced both baseline failures on the pinned source. Candidate generation 1 then exposed a candidate-only Rust name-resolution bug and was rejected. Further review found that merely replacing the final byte slice would still leave Unicode word starts after underscores ASCII-only inside field camelCase. Candidate generation 3 therefore keeps the change **camelCase-specific** while implementing Unicode case conversion across the camelCase operation itself:

- safely Unicode-lowercase the first scalar;
- remove field underscores;
- Unicode-uppercase each later word start;
- preserve standalone PascalCase behavior in this candidate.

That matches the upstream maintainer direction to support non-ASCII case changes while avoiding a broad rewrite of every Serde rename mode.

## Scout identity

- Programme: `open-source-ecosystems`
- Parent lane: Fieldwork #211 / OE-05 foundational libraries
- Target: `serde-rs/serde`
- Exact public source: `747814f7d5fbab872df3b02f070c165b91bde062`
- Source subject: `Release serde_derive_internals 0.30.0`
- Primary owner: `serde_derive/src/internals/case.rs`
- Public issue owner: [serde-rs/serde#2953](https://redirect.github.com/serde-rs/serde/issues/2953)
- Matching public repair found in focused PR search: none
- Owned Fieldwork path: `programmes/open-source-ecosystems/scouts/foundational-systems/serde-unicode-camelcase-20260811/`
- Research PR: Fieldwork #796
- Exact execution carrier: Fieldwork #798
- Upstream contact authorized: `false`
- Third-party target remains read-only

## Evidence state

Current evidence:

- `source-read`: exact current Serde rename implementation and tests inspected.
- `documented`: maintainer direction on #2953 says non-ASCII case changes should be supported using Unicode-aware string/character case conversion.
- `target-executed`: generation-1 carrier run `31423850341` reproduced the baseline field and enum-variant derive panics independently on exact source.
- `target-test-prepared`: candidate generation 3 and its expanded Unicode/compatibility matrix are retained here.
- generation-3 terminal GREEN: pending the current exact carrier run.

No local Rust toolchain is available in the chat execution container, so local compilation is outside the evidence set. Target execution uses the owned Fieldwork Actions carrier.

## Exact source map

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

Both final expressions assume byte index `1` is a character boundary.

The field path's `PascalCase.apply_to_field()` itself is UTF-8-safe in traversal because it iterates `field.chars()`. However, it uses `to_ascii_uppercase()` at word starts. Therefore replacing only the final byte slice would fix the panic while still leaving Unicode word-start casing incomplete for inputs such as `foo_éclair`.

## Public issue and maintainer direction

Serde issue [#2953](https://redirect.github.com/serde-rs/serde/issues/2953) demonstrates a compile-time derive panic for:

```rust
#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
struct Payload {
    项目名称: String,
}
```

The reported failure is a UTF-8 boundary panic at byte index 1.

A maintainer response says Serde wants to support non-ASCII case changes and suggests allocating and using Unicode `to_uppercase` or the character equivalent. This selects Unicode case conversion over a byte-length-only panic avoidance patch.

## Additional source finding — enum variants share the defect

`RenameRule::apply_to_variant` has the same first-byte camelCase expression. A Unicode-leading enum variant therefore reaches the same panic independently:

```rust
#[derive(Deserialize)]
#[serde(rename_all = "camelCase")]
enum Event {
    项目名称,
}
```

The original public issue only demonstrates fields. Fieldwork's exact baseline carrier reproduced both field and variant failures separately.

## Exact baseline RED receipt

Run: `31423850341`
Job: `93570777431`
Target: `serde-rs/serde@747814f7d5fbab872df3b02f070c165b91bde062`
Rust stable observed in carrier: `1.97.1`

Field derive baseline:

```text
byte index 1 is not a char boundary; it is inside '项' (bytes 0..3 of string)
```

Variant derive baseline:

```text
byte index 1 is not a char boundary; it is inside '项' (bytes 0..3 of string)
```

Evidence class: `target-executed` RED for both public derive paths.

## Candidate evolution

### Generation 1 — rejected candidate compile bug

Generation 1 added:

```rust
fn lowercase_first(value: &str) -> String {
    let mut chars = value.chars();
    match chars.next() {
        Some(first) => first.to_lowercase().chain(chars).collect(),
        None => String::new(),
    }
}
```

Exact run `31423850341` applied that candidate after both baseline RED controls, then Rust compilation failed because this file imports `use self::RenameRule::*;`. Bare `None` resolved to `RenameRule::None` instead of `Option::None` in the `match` arm.

Disposition: **candidate-only failure**, invariant retained.

### Generation 2 — compile collision repaired, then superseded by semantic review

Generation 2 replaced the `match` with `if let Some(first) = chars.next()` and kept field camelCase as:

```rust
lowercase_first(&PascalCase.apply_to_field(field))
```

That fixes the name collision and the first-byte panic. Review then found a precision gap: `PascalCase.apply_to_field()` still ASCII-uppercases word starts. Under the maintainer's Unicode direction:

```text
foo_éclair
```

should exercise Unicode uppercase on the post-underscore word start. Generation 2 would leave that interior `é` lowercase.

Disposition: **superseded before terminal execution**.

### Generation 3 — current candidate

Generation 3 retains a first-scalar helper for enum variants and adds a camelCase-specific field transform:

```rust
fn lowercase_first(value: &str) -> String {
    let mut chars = value.chars();
    if let Some(first) = chars.next() {
        first.to_lowercase().chain(chars).collect()
    } else {
        String::new()
    }
}

fn camel_case_field(field: &str) -> String {
    let mut camel = String::new();
    let mut capitalize = false;

    for ch in field.chars() {
        if ch == '_' {
            capitalize = true;
        } else if capitalize {
            camel.extend(ch.to_uppercase());
            capitalize = false;
        } else {
            camel.push(ch);
        }
    }

    lowercase_first(&camel)
}
```

Call sites become:

```rust
CamelCase => lowercase_first(variant)
CamelCase => camel_case_field(field)
```

Production fence remains one file: `serde_derive/src/internals/case.rs`.

## Candidate invariant

For Serde `camelCase` only:

1. all string traversal occurs on Unicode scalar boundaries;
2. the first scalar is lowercased using Unicode case mapping;
3. underscores are removed from fields as today;
4. each field word start after an underscore is uppercased using Unicode case mapping;
5. case mappings that expand to multiple scalars are retained;
6. ordinary ASCII camelCase outputs remain unchanged;
7. standalone PascalCase and every other rename rule retain their current behavior in this candidate.

## Prepared regression matrix

`add-regression.py` first verifies both vulnerable baseline expressions are still present, then adds three direct owner tests.

### Unicode field controls

```text
项目名称    -> 项目名称
Éclair      -> éclair
İ_value     -> i\u{307}Value
foo_éclair  -> fooÉclair
foo_σigma   -> fooΣigma
foo_ßeta    -> fooSSeta
```

Why these are useful:

- CJK proves UTF-8 safety when there is no case mapping.
- `Éclair` proves first-scalar lowercase.
- Turkish `İ` proves lowercase can expand to multiple scalars.
- `foo_éclair` and `foo_σigma` prove Unicode uppercase after underscore word boundaries.
- German `ß` proves an interior uppercase mapping can expand to multiple scalars.

### Unicode variant controls

```text
项目名称 -> 项目名称
Éclair   -> éclair
Σigma    -> σigma
```

### PascalCase compatibility fence

Generation 3 explicitly proves standalone PascalCase stays unchanged in this candidate:

```text
foo_éclair -> Fooéclair
foo_σigma  -> Fooσigma
```

This fence prevents the camelCase repair from silently widening into a broader serialized-name change.

### Existing ASCII controls

The repository's existing exact tests remain required:

- `internals::case::rename_fields`
- `internals::case::rename_variants`

## User-facing derive probes

The carrier creates a temporary crate outside the Serde checkout with a path dependency on exact local `serde` plus `derive`.

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

Generation-3 GREEN requires both bins to compile after the exact baseline REDs are preserved.

## Current exact acceptance gate

1. exact pinned target identity;
2. field baseline fails with the byte-boundary panic;
3. variant baseline independently fails with the same panic;
4. generation-3 patch applies cleanly;
5. both user-facing derive bins compile;
6. `unicode_camel_case_field` passes;
7. `unicode_camel_case_variant` passes;
8. `unicode_camel_case_does_not_widen_pascal_case` passes;
9. existing `rename_fields` passes;
10. existing `rename_variants` passes;
11. `cargo fmt --all -- --check` passes;
12. `git diff --check` passes.

## Challenged alternatives

### A — first-character byte-length fix only

Find the first scalar's UTF-8 byte length and retain ASCII case conversion.

This would stop the panic but leave `Éclair` unchanged, conflicting with the maintainer's selected Unicode direction.

Disposition: **reject**.

### B — generation-2 first-scalar Unicode fix only

This repairs the CJK panic and Unicode-lowercases the first scalar, but field word starts after underscores remain ASCII-only through the existing PascalCase helper.

Disposition: **superseded**.

### C — Unicode-convert every rename rule now

Changing all `to_ascii_lowercase` / `to_ascii_uppercase` paths would alter non-ASCII serialized names under lowercase, UPPERCASE, snake_case, SCREAMING_SNAKE_CASE, PascalCase, and related modes.

Disposition: **split**. A broader Unicode rename policy deserves its own compatibility matrix and review.

### D — special-case CJK/multibyte strings as unchanged

This would repair the reported sample without honoring Unicode case conversions for accented or Greek identifiers.

Disposition: **reject**.

## Consequence

A valid Rust identifier plus documented `rename_all = "camelCase"` can currently make Serde's derive macro panic during compilation. The same owner affects fields and enum variants.

The current candidate keeps the production change in one file and limits new Unicode wire-name semantics to the camelCase mode named by the public issue.

## Overlap

- Existing public issue: [serde-rs/serde#2953](https://redirect.github.com/serde-rs/serde/issues/2953).
- Focused public PR searches for #2953 / CJK / non-ASCII camelCase found no matching repair at scout time.
- Fieldwork had no dedicated Serde camelCase investigation before this scout.

Any future public contribution should attach to the existing upstream issue and remains a separate human decision.

## Current disposition

**HIGH / EXACT RED PROVEN / GENERATION-3 GREEN PENDING.**

The baseline defect and enum sibling are target-executed. Candidate generations 1 and 2 have explicit losing reasons. Generation 3 is the current bounded implementation under exact execution.

## Stop condition

Stop with one of:

1. generation-3 exact GREEN on user-facing derives, Unicode owner tests, ASCII controls, PascalCase compatibility fence, format, and diff hygiene;
2. current upstream source or a public PR absorbs the repair;
3. execution exposes a Unicode case mapping incompatibility that cannot remain camelCase-specific.

No automated upstream interaction or mutation occurred.
