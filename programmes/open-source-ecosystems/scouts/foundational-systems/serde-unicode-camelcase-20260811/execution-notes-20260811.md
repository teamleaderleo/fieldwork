# Serde Unicode camelCase execution notes — 2026-08-11

Target: `serde-rs/serde@747814f7d5fbab872df3b02f070c165b91bde062`

Research PR: #796
Execution carrier: #798

## Exact baseline evidence

Run `31423850341`, job `93570777431`, and later run `31425497304`, job `93576095903`, both reproduced the exact public derive failure independently for fields and enum variants:

```text
byte index 1 is not a char boundary; it is inside '项' (bytes 0..3 of string)
```

Evidence class: `target-executed` RED.

## Candidate history

1. Generation 1: rejected after exact candidate compilation exposed `RenameRule::None` shadowing a bare `None` pattern in the helper.
2. Generation 2: superseded by source review because it fixed the first scalar but kept post-underscore field word starts ASCII-only through the existing PascalCase helper.
3. Generation 3: current production candidate. CamelCase uses Unicode first-scalar lowercase and Unicode post-underscore word-start uppercase while standalone PascalCase remains unchanged.

## Carrier packaging history

Run `31425497304` re-proved both exact baseline RED paths and then stopped at candidate materialization with:

```text
error: corrupt patch ... candidate.patch:39
```

No candidate Rust code executed in that run. Classification: carrier packaging only.

The repair now retains two candidate representations:

- `candidate.patch` — reviewer-facing production-only diff with corrected hunk counts;
- `apply-candidate.py` — exact-source deterministic transformer.

Carrier generation 5 requires all of:

1. exact baseline vulnerable expressions present;
2. `git apply --check` accepts `candidate.patch` on the clean production file;
3. `apply-candidate.py` transforms the exact source;
4. production-only generated diff matches `candidate.patch` byte-for-byte after removing Git `index` metadata;
5. only then are the focused owner tests appended;
6. user-facing field and variant derives compile;
7. Unicode owner tests, PascalCase compatibility fence, existing ASCII tests, rustfmt, and `git diff --check` pass.

Current carrier head: `a17858bf9d1a7de3a058643bb648bddf5f426344`.
Current run: `31427896042`, queued at this checkpoint.

## ASCII compatibility model

A model comparison exhaustively checked current versus generation-3 camelCase over all strings of length 0–5 from the ASCII alphabet `abAB09_`.

```text
field spellings:   19,608 checked / 0 mismatches
variant spellings: 19,607 checked / 0 mismatches
```

Evidence class: `model-executed` compatibility screen. Existing exact repository ASCII tests remain required.

## Boundary

The current candidate changes only camelCase Unicode behavior. Broader Unicode semantics for lowercase, uppercase, PascalCase, snake_case, and screaming variants remain a separate compatibility question and are deliberately parked.

Upstream contact authorized: `false`.
