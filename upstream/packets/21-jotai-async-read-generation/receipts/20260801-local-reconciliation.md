# Unit 21 local reconciliation receipt

Date: `2026-08-01`  
Worker environment: Linux container, Node `v22.16.0`, Git command-line client  
Network during execution: unavailable  
Public upstream contact: none

## Exact inputs

- Public Jotai source revision: `56a9cc51de8a5dd762b95a145820f12589cc47c9`
- Source path copied for the patch check: `src/vanilla/utils/atomWithStorage.ts`
- Unit 20 prerequisite patch source: Fieldwork PR #252 head `d9dd61c4a0d1f9073c300519990e6ba9ec2855d9`
- Unit 21 patch source: Fieldwork PR #317 workflow-free head `34670f709753668827043bbc76c4159a8b36ade2`
- Executed repair evidence head: `e99c7d2e9e3b16c04b1738397ad6109758ad481e`

Local input SHA-256 values:

```text
90d96bdbde5cb4e9def1c312a4c391e60a04f4d9aad99b1828bb10d3491acea3  unit20.patch
bf30817d85f38c533ad557b0d885086aa838767690d2ab8b3ca2abc6029d8b66  unit21.patch
19c7f2266cc7a2a891918339726c27c42c27ece9aeab3adc597434e9d41f09c1  executed-model.mjs
```

The patch check used the exact `createJSONStorage` source segment from the pinned Jotai file. It was a source-segment reconciliation, not a complete repository checkout or target-native test run.

## Patch-order check

Commands:

```text
git apply --check unit21.patch
git apply --check unit20.patch
git apply unit20.patch
git apply --check unit21.patch
git apply unit21.patch
git diff --check
```

Output:

```text
direct_unit21_status=1
direct_unit21_error=error: patch failed: src/vanilla/utils/atomWithStorage.ts:117 error: src/vanilla/utils/atomWithStorage.ts: patch does not apply
stacked_apply=pass
```

Judgment: unit 21 is a stacked source contribution. Its unit-only patch applies after unit 20 establishes `cachedValues`; it does not apply directly to public Jotai main. A clean target-source branch must be based on unit 20's future clean source head, or the upstream delivery must be an explicitly stacked pull request.

## Expanded behavior model

Command:

```text
node executed-model.mjs
```

Output:

```text
ok 1 - newer same-key completion remains authoritative
ok 2 - pre-removal completion cannot republish identity
ok 3 - older valid result cannot restore after newer missing result
ok 4 - older valid result cannot restore after newer malformed result
ok 5 - stale malformed result cannot delete newer valid identity
ok 6 - unrelated key identity remains stable
ok 7 - cached A survives newer rejected read while older B stays stale
ok 8 - rejected newer read prevents older B from establishing empty cache
ok 9 - later successful read establishes identity after rejection
ok 10 - rejection remains caller-visible and unrelated key stays stable
ok 11 - same-string stale caller can reuse newer cached identity
{"passed":11,"node":"v22.16.0"}
```

The retained packet model is a formatting-normalized semantic mirror of the executed model. The target-native draft carries the same eleven cases.

## Evidence classification

- Patch prerequisite and ordering: `source-read` plus local source-segment execution.
- Eleven-case model: `model-executed`.
- Existing six-case repair matrix at `e99c7d2...`: `target-executed` through retained GitHub Actions runs.
- Expanded rejection controls: `target-test-prepared`; target-native execution remains required.
- Repository-wide format, build, and test gates: not run in this session.

## Limits

- No owned `teamleaderleo/jotai` repository was available.
- No complete Jotai checkout or dependency installation ran in this session.
- The retained target-native rejection cases require execution on the eventual clean source branch.
- Read versus `setItem` and subscription-event ordering remain outside unit 21.
