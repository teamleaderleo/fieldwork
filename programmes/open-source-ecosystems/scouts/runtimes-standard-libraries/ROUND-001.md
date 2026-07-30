# Runtimes and Standard Libraries Scout — Round 001

Date: 2026-07-30  
Programme: [Open-Source Ecosystems](../../STATUS.md)  
Scout issue: [#209](https://github.com/teamleaderleo/fieldwork/issues/209)

## In simple words

Compiler diagnostics and standard-library boundary cases produce compact contributions when an issue already carries a source fixture, expected result, and localized owner. This round found excellent Rust diagnostic examples, but deeper assignment checks showed the sampled issues were already claimed. The CPython queue still contains uncovered synchronization and parser candidates.

## Rust reference wave

Repository: `rust-lang/rust`

### Claimed candidates

1. [Nested-turbofish diagnostic](https://redirect.github.com/rust-lang/rust/issues/159745) — assigned after rustbot claim comments.
2. [Missing-match-arm diagnostic](https://redirect.github.com/rust-lang/rust/issues/159686) — assigned.
3. [Dyn-compatibility wording](https://redirect.github.com/rust-lang/rust/issues/159492) — assigned and mentored.
4. [Tidy and `.gitattributes` validation](https://redirect.github.com/rust-lang/rust/issues/157184) — assigned.
5. [Ineffective `#[path]` attributes](https://redirect.github.com/rust-lang/rust/issues/157260) — assigned and mentored.

No matching active pull requests were found in the sampled searches, but assignee and claim state are sufficient to stop independent implementation. Retain these issues as code-reading and test-packet examples. Reopen only if a claim is released or collaboration is explicitly requested.

### Diagnostic reference path

The nested-turbofish case remains a useful model:

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

The `label:E-easy no:assignee` search found the [`expect`-message coordination issue](https://redirect.github.com/rust-lang/rust/issues/159751), but that issue coordinates many independently claimed subdirectories and asks contributors to claim a subdirectory in comments. Treat it as a coordinated batch, not a free whole-issue task.

## CPython first wave

Repository: `python/cpython`

### Deep dive — free-threaded `GenericAlias` iterator race

Issue: [`GenericAlias` iterator race](https://redirect.github.com/python/cpython/issues/154916)

The issue follows a [merged iterator-state PR](https://redirect.github.com/python/cpython/pull/154108), which changed `ga_iternext()` to atomically exchange `gi->obj` with `NULL` in free-threaded builds.

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

Review of the earlier iterator-state PR shows maintainers rejected a large expensive concurrency test for this unusual shared-iterator use. The next packet should therefore carry:

- the TSAN reproducer as retained evidence;
- a small focused unit test for observable reduce/consume outcomes;
- a targeted TSAN or stress command outside the ordinary test suite;
- a concise explanation of why the synchronization change is needed even when ordinary iteration is single-threaded.

Disposition: issue-first or a tightly scoped patch after confirming the preferred reference-acquisition primitive.

### Other CPython candidates

- [`<>` tokenizer issue](https://redirect.github.com/python/cpython/issues/151464) — retain as a parser/token contract candidate.
- [pickle FRAME divergence](https://redirect.github.com/python/cpython/issues/154848) — linked fixes already exist; study the buffering correction.
- [JIT/Hypothesis hang](https://redirect.github.com/python/cpython/issues/154701) — retain as a reduction campaign.
- [Windows stack-protection flake](https://redirect.github.com/python/cpython/issues/154763) — retain for Windows CI access.

## Duplicate stops discovered

Focused pull requests already cover:

- [zip repack/live reader](https://redirect.github.com/python/cpython/issues/154842) → [PR](https://redirect.github.com/python/cpython/pull/154843);
- [incremental iconv state](https://redirect.github.com/python/cpython/issues/154859) → [PR](https://redirect.github.com/python/cpython/pull/154862);
- [ISO-2022-CN-EXT encoding](https://redirect.github.com/python/cpython/issues/154863) → [PR](https://redirect.github.com/python/cpython/pull/154899);
- [negative curses attributes](https://redirect.github.com/python/cpython/issues/154874) → active fixes;
- [struct-sequence repr](https://redirect.github.com/python/cpython/issues/154387) → active fixes;
- [repeated Future traceback loss](https://redirect.github.com/python/cpython/issues/154791) → [PR](https://redirect.github.com/python/cpython/pull/154798).

These are retained as examples of strong packets: a short reproducer, direct code explanation, failing test, and explicit control cases.

## Return

- **Claimed references:** the five Rust issues above.
- **Issue-first/deep probe:** CPython's `GenericAlias` iterator race.
- **Retain:** the tokenizer and JIT reduction candidates.
- **Stop duplicate implementation:** the CPython issues with active fixes.
- **Next expansion:** search unassigned Rust work with claim-state checks, then add Go and Node.js candidates.