# Runtimes and Standard Libraries Scout — Round 001

Date: 2026-07-30  
Programme: [Open-Source Ecosystems](../../STATUS.md)  
Scout issue: [#209](https://github.com/teamleaderleo/fieldwork/issues/209)

## In simple words

Compiler diagnostics and standard-library boundary cases produce compact contributions when the issue already carries a source fixture, expected result, and localized owner. This round found excellent Rust diagnostic examples, but deeper assignment checks showed the sampled issues were already claimed. The CPython queue still contains uncovered synchronization and parser candidates.

## Rust reference wave

Repository: `rust-lang/rust`

### Claimed candidates

1. [#159745](https://github.com/rust-lang/rust/issues/159745) — nested generic parameters missing a turbofish produce only `expected expression, found ','`. The issue is assigned after rustbot claim comments.
2. [#159686](https://github.com/rust-lang/rust/issues/159686) — a missing match arm receives tuple and alternative-pattern suggestions. The issue is assigned.
3. [#159492](https://github.com/rust-lang/rust/issues/159492) — pedagogic dyn-compatibility wording. The issue is assigned and mentored.
4. [#157184](https://github.com/rust-lang/rust/issues/157184) — validate `ignore-tidy-cr` entries against `.gitattributes`. The issue is assigned.
5. [#157260](https://github.com/rust-lang/rust/issues/157260) — reject ineffective `#[path]` attributes. The issue is assigned and mentored.

No matching active pull requests were found in the sampled searches, but assignee and claim state are sufficient to stop independent implementation. Retain these issues as code-reading and test-packet examples. Reopen only if a claim is released or collaboration is explicitly requested.

### Diagnostic reference path

#159745 remains a useful model:

1. add the issue input to the closest parser/suggestion UI test;
2. confirm current stderr exactly;
3. trace the parse recovery that interprets `<` as comparison syntax;
4. guard the suggestion so ordinary comparison expressions remain unaffected;
5. run the focused UI test and bless output;
6. add neighboring negative cases.

This describes where to look while respecting the active claim.

### Search correction

For Rust, an open issue with no pull request can still be owned. Check:

- assignee field;
- triagebot assignment block;
- `@rustbot claim` comments;
- issue text requesting subdirectory-level coordination;
- Zulip/mentor guidance when an `E-mentor` label exists.

The search `label:E-easy no:assignee` found #159751, but that issue coordinates many independently claimed subdirectories and explicitly asks contributors to claim a subdirectory in comments. Treat it as a coordinated batch, not a free whole-issue task.

## CPython first wave

Repository: `python/cpython`

### Deep dive — free-threaded `GenericAlias` iterator race

Issue: [#154916](https://github.com/python/cpython/issues/154916)

The issue follows merged [PR #154108](https://github.com/python/cpython/pull/154108), which changed `ga_iternext()` to atomically exchange `gi->obj` with `NULL` in free-threaded builds.

Current `Objects/genericaliasobject.c` still has:

```c
if (gi->obj)
    return Py_BuildValue("N(O)", iter, gi->obj);
```

inside `ga_iter_reduce()`. That plain read races with the atomic exchange in `ga_iternext()` when one iterator is shared across threads. The issue includes a ThreadSanitizer trace and a Python reproducer.

### Likely correction boundary

A correct free-threaded path needs a stable strong reference or an equivalent protected snapshot of `gi->obj` while preserving the consumed-iterator result. A simple atomic load alone can still expose lifetime questions if another thread exchanges and decrements the object immediately after the load.

Potential designs to evaluate:

- critical section around snapshot and increment;
- an atomic helper that returns a safely owned reference under the project's object-lifetime rules;
- aligning iterator state access across `iternext`, `reduce`, traverse, and clear.

### Test constraint

Review of PR #154108 shows maintainers rejected a large expensive concurrency test for this unusual shared-iterator use. The next packet should therefore carry:

- the TSAN reproducer as retained evidence;
- a small focused unit test for observable reduce/consume outcomes;
- a targeted TSAN or stress command outside the ordinary test suite;
- a concise explanation of why the synchronization change is needed even when ordinary iteration is single-threaded.

Disposition: issue-first or a tightly scoped patch after confirming the preferred reference-acquisition primitive.

### Other CPython candidates

- [#151464](https://github.com/python/cpython/issues/151464) — tokenizer emits `<>` even when the grammar rejects it. Retain as a parser/token contract candidate.
- [#154848](https://github.com/python/cpython/issues/154848) — `_pickle.c` and `pickletools` diverge around FRAME boundaries. The issue body links PRs #154893 and #154909, so stop independent implementation and study the buffering fix.
- [#154701](https://github.com/python/cpython/issues/154701) — JIT hang in Hypothesis has a reliable suite-level reproduction but lacks a reduced case. Retain as a reduction campaign.
- [#154763](https://github.com/python/cpython/issues/154763) — Azure stack-protection test flake. Retain for Windows CI access.

## Duplicate stops discovered

The following current bugs already had focused pull requests:

- #154842 zipfile repack/live reader → PR #154843;
- #154859 iconv incremental decoder state → PR #154862;
- #154863 ISO-2022-CN-EXT empty encoding → PR #154899;
- #154874 negative curses attributes → PRs #154875 and #154887;
- #154387 struct-sequence repr → PRs #154434 and #154687;
- #154791 repeated Future traceback loss → PR #154798.

These are retained as examples of strong packets: a short reproducer, direct code explanation, failing test, and explicit control cases.

## Return

- **Claimed references:** Rust #159745, #159686, #159492, #157184, and #157260.
- **Issue-first/deep probe:** CPython #154916.
- **Retain:** CPython #151464 and #154701.
- **Stop duplicate implementation:** the six CPython issues with active PRs listed above.
- **Next expansion:** search unassigned Rust work with claim-state checks, then add Go and Node.js candidates.