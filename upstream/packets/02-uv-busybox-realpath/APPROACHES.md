# Approaches — Unit 02: BusyBox-safe relocatable launchers

## In simple words

The leading approach removes the unsupported `--` operands from every current launcher owner while keeping the existing quoting and `realpath`-before-`dirname` sequence. It won because the executable matrices preserve the tested behavior on GNU and BusyBox and because it keeps generator and recognizer text synchronized.

## Decision criteria

1. Preserve sibling-interpreter selection after symlink resolution.
2. Remove the BusyBox diagnostic on successful commands.
3. Preserve quoting for spaces and ordinary leading-hyphen invocation.
4. Keep wheel, virtualenv, and project-run text synchronized.
5. Keep the source diff narrow and reviewable.

## Selected approach

### Remove unsupported delimiters in all three owners

- Design: replace `realpath --` with `realpath` and `dirname --` with `dirname` in the wheel generator and snapshot, POSIX/fish activation generators, and project-run recognizer.
- Owning boundary: the existing string-literal owners.
- Evidence: prior 24-case matrix and synchronized source candidate at [`teamleaderleo/uv#3`](https://github.com/teamleaderleo/uv/pull/3); current-head carrier at [`teamleaderleo/uv#5`](https://github.com/teamleaderleo/uv/pull/5).
- Advantages: smallest executable change; no runtime detection; preserves symlink canonicalization; exact textual synchronization.
- Costs and risks: a bare option-like `$0` remains unproved; BSD/macOS execution remains pending human validation.
- Remaining controls: current-head run, human source review, and macOS/BSD gate before public submission.

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
- Negative control: the delimiter-free fragment already preserves all executed GNU cases.

### Assume `$0` can never begin with a hyphen

- Temptation: dismiss the option-safety question.
- Why incomplete: the executed control proves `./-tool`, not every possible process argument.
- Evidence limit: bare option-like `$0` remains unmeasured.

## Prior upstream approaches

| Link | Approach | Status | Relationship to this unit |
| --- | --- | --- | --- |
| [`astral-sh/uv#8058`](https://github.com/astral-sh/uv/issues/8058) | Canonicalize the launcher before taking its directory | closed | Defines the symlink invariant retained here |
| [`astral-sh/uv#8079`](https://github.com/astral-sh/uv/pull/8079) | Replace shell-only directory resolution with nested `realpath`/`dirname` and add symlink tests | merged | Direct implementation lineage; delimiters came from this change |
| [`astral-sh/uv#16209`](https://github.com/astral-sh/uv/issues/16209) | Report BusyBox diagnostic and discuss compatibility trade-off | open | Public issue this unit addresses |
| [`teamleaderleo/uv#2`](https://github.com/teamleaderleo/uv/pull/2) | Executable current-vs-no-delimiter discriminator | open evidence carrier | Establishes behavior matrix |
| [`teamleaderleo/uv#3`](https://github.com/teamleaderleo/uv/pull/3) | Synchronized generated three-owner source candidate | open evidence carrier | Establishes exact patch and affected-crate compile result |

## Deferred adjacent work

- shared launcher helper — broader refactor;
- legacy generated-script migration — separate compatibility question;
- generalized shell utility portability — wider than this defect;
- full system-test expansion — useful follow-up after maintainer direction.

## Decision history

| Date | Exact inputs | Decision | Reason | Reopening trigger |
| --- | --- | --- | --- | --- |
| 2026-07-31 | PR #2 at `f8adfc6`, workflow `30625826268` | Promote delimiter-free fragment | 24/24 matrix, BusyBox quiet, GNU retained | supported bare option-like `$0` |
| 2026-07-31 | PR #3 at `0aad1cc`, workflow `30650924197` | Synchronize all three owners | exact 3-file fence and affected-crate compile passed | current source drift |
| 2026-08-01 | public base `79bbface`, carrier PR #5 | Reconcile and materialize clean branch | old candidate base was 34 commits behind | current-head test failure or upstream overlap |
