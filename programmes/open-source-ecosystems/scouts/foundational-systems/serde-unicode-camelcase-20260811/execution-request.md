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

Carrier generation 5 additionally requires:

- exact baseline source expressions are present before execution;
- `git apply --check` accepts the reviewer-facing `candidate.patch` while the production file is still clean;
- deterministic `apply-candidate.py` transforms the exact pinned production source;
- the production-only resulting diff, before regression tests are appended, matches `candidate.patch` byte-for-byte after removing Git's `index` metadata line;
- focused owner regressions are appended only after that production-diff identity gate.

Run `31425497304` re-proved both baseline RED paths, then stopped before candidate execution because the hand-written patch artifact had incorrect hunk counts. The next carrier generation also separates production-diff verification from test materialization so the reviewer patch comparison cannot be polluted by appended test code.

Generation 1 failed only because bare `None` collided with `RenameRule::None`. Generation 2 was superseded before terminal execution because it left non-ASCII word starts after underscores ASCII-only inside camelCase. Generation 3 keeps the change camelCase-specific while honoring the maintainer's non-ASCII case-conversion direction.

Transfer terminal receipts into the durable report, then retire this marker and temporary workflow.
