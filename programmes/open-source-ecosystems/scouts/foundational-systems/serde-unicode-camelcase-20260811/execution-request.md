# Exact target execution request

Execution carrier only.

Target: `serde-rs/serde@747814f7d5fbab872df3b02f070c165b91bde062`.

Run the preserved baseline RED and candidate-generation-3 GREEN matrix for `camelCase` fields and enum variants.

Required baseline evidence:

- CJK field derive fails with the exact byte-boundary panic;
- CJK enum-variant derive independently fails with the same panic.

Generation 3 requirements:

- Unicode-lowercase the first camelCase scalar safely;
- Unicode-uppercase field word starts following underscores, including expansion-capable characters;
- keep standalone PascalCase behavior unchanged in this candidate;
- user-facing CJK field and variant derives compile;
- focused Unicode owner tests, existing ASCII rename controls, format, and diff hygiene pass.

Carrier generation 4 additionally requires:

- `git apply --check` accepts the reviewer-facing `candidate.patch`;
- deterministic `apply-candidate.py` transforms the exact pinned source;
- the resulting production diff, after removing Git's `index` metadata line, matches `candidate.patch` byte-for-byte.

Run `31425497304` already re-proved both baseline RED paths, then stopped before candidate execution because the hand-written patch artifact had incorrect hunk counts. That was carrier packaging only. The patch counts are repaired and the deterministic transformer is now the execution owner.

Generation 1 failed only because bare `None` collided with `RenameRule::None`. Generation 2 was superseded before terminal execution because it left non-ASCII word starts after underscores ASCII-only inside camelCase. Generation 3 keeps the change camelCase-specific while honoring the maintainer's non-ASCII case-conversion direction.

Transfer terminal receipts into the durable report, then retire this marker and temporary workflow.
