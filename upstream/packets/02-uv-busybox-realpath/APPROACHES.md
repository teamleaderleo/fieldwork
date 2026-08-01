# Approaches — Unit 02: BusyBox-safe relocatable launchers

## In simple words

The selected approach removes the unsupported `--` operands from every current launcher owner while keeping the existing quoting and `realpath`-before-`dirname` sequence. It won because current-head GNU and BusyBox execution preserve the intended behavior, the affected crates compile, the native shebang assertion passes, and generator and recognizer text remain synchronized.

## Decision criteria

1. Preserve sibling-interpreter selection after symlink resolution.
2. Remove the BusyBox diagnostic on successful commands.
3. Preserve quoting for spaces and ordinary leading-hyphen invocation.
4. Keep wheel, virtualenv, and project-run text synchronized.
5. Keep the source diff narrow, formatted, and reviewable.
6. Publish one source-only commit directly on the reviewed public base.

## Selected approach

### Remove unsupported delimiters in all three owners

- Design: replace `realpath --` with `realpath` and `dirname --` with `dirname` in the wheel generator and assertion, POSIX/fish activation generators, and project-run recognizer.
- Exact source: [`c43b126`](https://github.com/teamleaderleo/uv/commit/c43b1262be71d9fc0b60ca613700ef7ae60bf69d).
- Exact compare: [`79bbface...c43b126`](https://github.com/teamleaderleo/uv/compare/79bbface771210df216b738e9bdc7df95e5a9e6b...c43b1262be71d9fc0b60ca613700ef7ae60bf69d).
- Owning boundary: the existing string-literal owners.
- Evidence: prior 24-case discriminator at PR #2, synchronized source candidate at PR #3, and successful current-head execution at PR #6 / workflow `30676914631`.
- Advantages: smallest executable change; no runtime detection; preserves symlink canonicalization; exact textual synchronization; one clean source commit.
- Costs and risks: a bare option-like `$0` remains unproved; BSD/macOS execution remains a human review decision; old generated text can persist.
- Remaining controls: independent human source review, platform-gap acceptance or execution, public-policy compliance, and explicit authorization.

## Viable alternatives

### Normalize a bare leading-hyphen `$0`

- Design: use a shell `case` to prefix `./` before calling `realpath`.
- Why it remains plausible: it would make operand intent explicit for a bare option-like process argument.
- What it would improve: a hostile invocation class outside the current matrix.
- What it would widen or complicate: generated shell text, snapshots, shell compatibility, and recognizer matching.
- Exact discriminator: reproduce a supported shell invocation where `$0` begins with `-` without a path prefix.
- Reopening trigger: a real supported invocation or upstream contract requiring that case.

### Accept both old and new shebang text in project-run

- Design: recognize the delimiter and delimiter-free forms.
- Why it remains plausible: existing environments can retain older generated scripts.
- What it would improve: explicit backward recognition.
- What it would widen or complicate: another permanent string contract and tests.
- Exact discriminator: demonstrate project-run encountering persisted old launchers through a supported update path.
- Reopening trigger: maintainer confirmation that both forms form a compatibility promise.

### Centralize the fragment

- Design: introduce a shared helper or constant for generator and recognizer text.
- Why it remains plausible: prevents future textual drift.
- What it would improve: maintainability.
- What it would widen or complicate: crate boundaries or abstraction scope.
- Exact discriminator: identify a natural existing shared crate without new dependency edges.
- Reopening trigger: maintainer preference during human review.

## Executed losing approaches

### Keep the current fragment

- Exact branch: [`fieldwork/307-relocatable-launcher-portability@f8adfc6`](https://github.com/teamleaderleo/uv/tree/f8adfc6a573e3b8c44713e132ba9b7a2a3dbd502).
- What ran: current vs delimiter-free fragments on GNU and Alpine BusyBox across six invocation forms.
- Result: current BusyBox executions succeeded while emitting `realpath: --`.
- Why it lost: violates clean-stderr invariant.
- Useful evidence retained: the diagnostic is compatibility noise while the resolved interpreter remains correct.

### Wheel-only correction

- Exact source observation: the pattern exists in wheel, virtualenv, and project-run owners.
- What ran: source ownership search and generated three-file candidate.
- Result: one-file scope would leave sibling owners inconsistent.
- Why it lost: fails synchronized-contract criterion.
- Useful evidence retained: exact owner and replacement counts.

### Unformatted delimiter-only virtualenv replacement

- Exact carrier: `76cdc876678e6bb517f543f1021aaeb87e6d0f4a`.
- What ran: exact candidate generation followed by rustfmt.
- Result: `cargo fmt --all --check` required the relocatable activation match arm to use a braced form.
- Why it lost: failed the target formatter.
- Useful evidence retained: final virtualenv hunk is +4/-4 while the semantic replacement remains two `realpath` and four `dirname` delimiters.

### Broad carrier against stale fork main

- Exact carrier: PR #5.
- Result: carrier-wide comparison included unrelated upstream history and ordinary CI load.
- Why it lost: poor evidence isolation.
- Useful evidence retained: exact current source artifact and setup-failure receipt.
- Repair: isolated execution base `d2ebfd9` with a two-file carrier and one focused workflow.

## Rejected easy answers

### Redirect `realpath` stderr

- Temptation: suppress the visible symptom.
- Why incomplete: hides genuine path-resolution errors with the compatibility diagnostic.
- Negative control: the candidate removes the diagnostic while leaving stderr available for real failures.

### Replace `realpath` with `readlink -f`

- Temptation: common GNU/Linux canonicalization idiom.
- Why incomplete: changes the portability and symlink contract; prior upstream work deliberately selected `realpath`.
- Source fact: upstream issue #8058 and PR #8079 chose `realpath` to repair symlinked launchers.

### Detect BusyBox at runtime

- Temptation: retain `--` elsewhere.
- Why incomplete: adds shell detection, runtime branching, and failure modes to every generated launcher.
- Negative control: the delimiter-free fragment preserves all executed GNU cases.

### Assume `$0` can never begin with a hyphen

- Temptation: dismiss the option-safety question.
- Why incomplete: the executed control proves `./-tool`, not every possible process argument.
- Evidence limit: bare option-like `$0` remains unmeasured.

## Prior upstream and owned approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [`astral-sh/uv#8058`](https://github.com/astral-sh/uv/issues/8058) | Canonicalize the launcher before taking its directory | closed | Defines the symlink invariant retained here |
| [`astral-sh/uv#8079`](https://github.com/astral-sh/uv/pull/8079) | Nested `realpath`/`dirname` plus symlink tests | merged | Direct implementation lineage; delimiters came from this change |
| [`astral-sh/uv#16209`](https://github.com/astral-sh/uv/issues/16209) | BusyBox diagnostic report and trade-off discussion | open | Public issue this unit addresses |
| [`teamleaderleo/uv#2`](https://github.com/teamleaderleo/uv/pull/2) | Executable current-vs-no-delimiter discriminator | evidence carrier | Establishes behavior matrix |
| [`teamleaderleo/uv#3`](https://github.com/teamleaderleo/uv/pull/3) | Synchronized generated three-owner source candidate | evidence carrier | Establishes original exact patch and compile result |
| [`teamleaderleo/uv#5`](https://github.com/teamleaderleo/uv/pull/5) | Current-head artifact carrier against stale fork main | closed without merge | Retained exact files and setup failures |
| [`teamleaderleo/uv#6`](https://github.com/teamleaderleo/uv/pull/6) | Isolated current-head tests and clean publication | closed without merge | Final successful execution carrier |

## Deferred adjacent work

- shared launcher helper — broader refactor;
- legacy generated-script migration — separate compatibility question;
- generalized shell utility portability — wider than this defect;
- complete project suite expansion — reviewer or maintainer direction;
- native macOS/BSD validation — platform follow-up.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-31 | PR #2 at `f8adfc6`, workflow `30625826268` | Promote delimiter-free fragment | 24/24 matrix, BusyBox quiet, GNU retained | supported bare option-like `$0` |
| 2026-07-31 | PR #3 at `0aad1cc`, workflow `30650924197` | Synchronize all three owners | exact 3-file fence and affected-crate compile passed | current source drift |
| 2026-08-01 | public base `79bbface`, PR #5 artifact `8810498589` | Retain exact current-head files | old candidate base was 34 commits behind | source overlap or failed current test |
| 2026-08-01 | workflow `30676820652` | Adopt rustfmt braced virtualenv arm | target formatter rejected the unbraced candidate | formatter behavior changes |
| 2026-08-01 | PR #6 at `9c1465a`, workflow `30676914631` | Publish source head `c43b126` | format, compile, native test, GNU/BusyBox matrices, and exact publication fence passed | human review or platform evidence reverses conclusion |
