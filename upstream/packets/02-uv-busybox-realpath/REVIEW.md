# Review — Unit 02: uv BusyBox `realpath` compatibility

## Current disposition

`HOLD — independent human review required`

The exact source candidate and focused current-head tests are complete. The remaining reviewer work is judgment: supported `$0` forms, macOS/BSD utility behavior, persisted old launcher recognition, test sufficiency, and Astral's human-ownership policy.

## Review subject

- Work class: upstream bug-fix preparation
- Target repository: `astral-sh/uv`
- Public source base: `79bbface771210df216b738e9bdc7df95e5a9e6b`
- Canonical source branch: `teamleaderleo/uv:upstream/02-busybox-realpath`
- Exact source head: `c43b1262be71d9fc0b60ca613700ef7ae60bf69d`
- Complete compare: [`79bbface...c43b126`](https://github.com/teamleaderleo/uv/compare/79bbface771210df216b738e9bdc7df95e5a9e6b...c43b1262be71d9fc0b60ca613700ef7ae60bf69d)
- Fieldwork packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Complete changed-file fence: wheel.rs, virtualenv.rs, project/run.rs
- Upstream-contact authority: none

## Review reading order

1. [`README.md`](./README.md)
2. [`DEEP_DIVE.md`](./DEEP_DIVE.md)
3. [`APPROACHES.md`](./APPROACHES.md)
4. [`TESTS.md`](./TESTS.md)
5. exact source compare above
6. [`UPSTREAM_ISSUE.md`](./UPSTREAM_ISSUE.md)
7. [`UPSTREAM_PR.md`](./UPSTREAM_PR.md)

## Exact source links

| Area | Exact link | Role |
| --- | --- | --- |
| Wheel generator and native assertion | [`wheel.rs@c43b126`](https://github.com/teamleaderleo/uv/blob/c43b1262be71d9fc0b60ca613700ef7ae60bf69d/crates/uv-install-wheel/src/wheel.rs) | Generates relocatable shebang and asserts exact text |
| Virtualenv activation generators | [`virtualenv.rs@c43b126`](https://github.com/teamleaderleo/uv/blob/c43b1262be71d9fc0b60ca613700ef7ae60bf69d/crates/uv-virtualenv/src/virtualenv.rs) | Generates POSIX and fish relocatable activation paths |
| Project-run recognizer | [`run.rs@c43b126`](https://github.com/teamleaderleo/uv/blob/c43b1262be71d9fc0b60ca613700ef7ae60bf69d/crates/uv/src/commands/project/run.rs) | Recognizes the corrected generated shebang |

## Claims requiring judgment

| Claim or design choice | Evidence | Reviewer question |
| --- | --- | --- |
| Removing both delimiters is the narrow repair | current-head GNU and Alpine BusyBox matrices | Does any supported invocation supply a bare option-like `$0`? |
| All three owners must change together | exact three-file source fence | Should project-run recognize both historical and corrected forms? |
| Symlink behavior is retained | external-symlink matrix and upstream PR #8079 lineage | Is the controlled fixture sufficient? |
| Runtime BusyBox detection adds needless complexity | GNU candidate matrix remains clean | Does upstream prefer explicit platform branching? |
| The source diff should remain three files | one-commit clean compare | Would maintainers prefer a shared helper in the same contribution? |

## Source cleanliness

- [x] Exact source head recorded.
- [x] One commit directly on public base `79bbface`.
- [x] One commit ahead and zero behind.
- [x] Exactly three source files changed.
- [x] No Fieldwork-only files in target source diff.
- [x] No temporary workflows or publishers in target source diff.
- [x] No execution receipts or stale artifacts in target source diff.
- [x] No unrelated generated churn.
- [x] Commit-pinned links resolve to source head `c43b126`.
- [ ] Every changed line independently reviewed by a human.

## Test review

- [x] Exact replacement fence ran: five `realpath --`, seven `dirname --`.
- [x] `git diff --check` passed.
- [x] `cargo fmt --all --check` passed.
- [x] `cargo check -p uv-install-wheel -p uv-virtualenv -p uv` passed.
- [x] `cargo test -p uv-install-wheel test_shebang` passed.
- [x] GNU matrix passed 12/12.
- [x] Alpine 3.22 BusyBox matrix passed 12/12.
- [x] External symlink, spaces, relative, PATH, absolute, and `./-tool` controls passed.
- [x] Setup failures and source failures are separated in `TESTS.md`.
- [ ] macOS/BSD platform gap accepted or closed.
- [ ] Full project suite or clippy requested by reviewer, if needed.

## Final execution receipt

- Execution-only carrier: `9c1465a8beff5e44053756523a053dbc64abc047`
- Workflow/job: [`30676914631`](https://github.com/teamleaderleo/uv/actions/runs/30676914631) / `91305994591`
- Artifact: `8810846105`
- Artifact digest: `sha256:88af531d65679b1a756541d598c8c8fc85d250dd03ee32b58ede2d8a883ad45c`
- Published source tree: `63c644c8bba5a5cb3376401f64bd1ce561aa674e`
- Published source commit: `c43b1262be71d9fc0b60ca613700ef7ae60bf69d`
- Execution PR #6: closed without merge

## Known limits

- bare option-like `$0` remains outside executed evidence;
- native macOS and BSD utility behavior remains unexecuted;
- older generated shebangs can remain after uv updates;
- production prevalence remains unmeasured;
- the full project suite and clippy were outside the focused run.

## Draft and policy review

- [x] Existing public issue #16209 selected instead of duplicate filing.
- [x] Internal PR draft matches the exact source diff and test receipt.
- [x] Public upstream remained untouched.
- [x] Astral contribution and AI policies are recorded.
- [ ] Human independently understands and reviews the code.
- [ ] Human rewrites all public wording in their own words.
- [ ] Explicit authorization exists before any public interaction.

## Reviewer disposition

`HOLD`

Reviewed source head: `c43b1262be71d9fc0b60ca613700ef7ae60bf69d`  
Reason: source preparation and focused tests are complete; independent human judgment and public authorization remain.  
Clearing condition: human review records an affirmative disposition, accepts or closes the named compatibility gaps, authors public wording, and receives explicit authorization.  
Reviewer eligibility: a human who has independently read and understood the exact diff.

## Suggested human response

`Unit 02 source c43b126 is approved for human upstream preparation; the documented platform limits are accepted.`

—or—

`Unit 02 concern: <specific source, test, compatibility, or framing issue>`
