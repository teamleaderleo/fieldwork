# SWC JSX surrogate-entity review

## In simple words

The open SWC JSX surrogate-entity fix has cleared a long sequence of review findings, but its current head still contains a panic path for out-of-range numeric entities.

Upstream issue `swc-project/swc#11802` asks for three things: surrogate-pair support, graceful handling of invalid or unpaired surrogates, and a syntax error instead of a panic for an invalid numeric entity. Active upstream PR `swc-project/swc#11803` owns that work, so Fieldwork should review rather than duplicate it.

Current reviewed PR head: `c2e553207881fb376e6e54efdb94e3551d708813`.

Evidence class: `source-read` plus upstream CI inspection. No third-party mutation was performed.

## Current-head finding

At the current PR head, `crates/swc_ecma_parser/src/lexer/mod.rs::read_jsx_entity` contains a fallible helper:

```rust
fn parse_from_code(lexer: &mut Lexer, s: &str, radix: u32) -> Option<u32> {
    let num = match u32::from_str_radix(s, radix) {
        Ok(num) if num <= 0x10ffff => num,
        _ => {
            lexer.emit_error(lexer.input.cur_pos(), SyntaxError::InvalidJSXValue);
            return None;
        }
    };

    Some(num)
}
```

Its hexadecimal and decimal callers immediately unwrap the result:

```rust
result = parse_from_code(self, &s[2..], 16).unwrap();
...
result = parse_from_code(self, stripped, 10).unwrap();
```

Therefore an entity whose parsed integer is outside Unicode range, such as `&#x110000;`, first emits `InvalidJSXValue` and then unwraps `None`. That preserves a panic path inside the patch whose issue-level acceptance criterion says invalid numeric entities should return a syntax error rather than panic.

This is the same mechanism an earlier inline review called out. That thread is currently resolved with an author reply that the unwrap is by design, but the current code and issue acceptance text remain in tension.

## Review history checked

All current inline review threads on PR #11803 are resolved. Earlier revisions received findings for:

- the high-surrogate upper boundary;
- lone low-surrogate deletion;
- dropping a buffered high surrogate before a scalar;
- decimal surrogate-pair handling;
- preserving the `x` marker when retaining a raw hex entity;
- malformed `&#...;` handling;
- raw/value index mapping in the React JSX text normalizer;
- source spans for invalid entities;
- propagation of entity errors from JSX text scanning;
- the out-of-range numeric unwrap described above.

Most of those threads are outdated against the current head, which indicates the patch has changed substantially during review. The unwrap thread is resolved but not outdated.

## CI boundary

The current PR head has a green upstream CI run. The matrix includes cargo checks, clippy, formatting, package tests, bindings, and repository tests. A green aggregate run does not answer this specific malformed-entity case because the current source still contains the direct `Option::unwrap` after the range rejection.

No target execution of `&#x110000;` was performed by Fieldwork in this review, so the finding remains `source-read` rather than `target-executed`.

## Disposition

**REPAIR / REVIEW HOLD.** Active upstream ownership exists and the patch has substantial review history, so Fieldwork should not create a competing implementation. The remaining review question is narrow: prove that every numeric-entity failure path returns a lexer/parser error without `unwrap`/panic, including both hexadecimal and decimal values above `0x10FFFF`.

A useful discriminator for a human or later owned execution carrier is:

```jsx
<A title="&#x110000;" />
```

and the text form:

```jsx
<A>foo&#x110000;bar</A>
```

Expected result: recoverable parser/lexer error with an actionable span; no process panic and no silent text corruption.

Automated third-party upstream contact remains prohibited.
