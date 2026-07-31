# F254-tarfilter-regex-compatibility: translate GNU transform dialects instead of silently using Python syntax

Finding state: `closed`

Workstream: `H`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-tarfilter-regex-compatibility/finding.md`  
Investigation workspace: `investigations/254-linux-storage-archive-reproducibility/`  
Canonical implementation: `teamleaderleo/linux-fieldwork` PR #151; accepted-neighbor controls in PR #220  
Exact implementation head: product `4555c5c250c1afedb3947fd1a7b5a0323bd9d262`; controls `bb0a79dec47958c6b865d4b382a44baff17ab736`  
Exact base or source revision: PR #151 base `d344c942af4b55b5b0c71c8a66a8870fbf0db7bf`; GNU tar 1.35 under `LC_ALL=C`  
Reviewed input generation: predecessor chain PRs #56, #68, #102, #113; final product and control heads above  
Current review disposition: `ACCEPT`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

`tarfilter` can rename archive members using expressions documented as GNU-tar-style transforms. The old candidate passed those expressions directly to Python's regex engine.

GNU basic regex, GNU extended regex, and Python regex give punctuation different jobs. A pattern could therefore be valid in both programs but rename a different member, or Python could accept a special group that GNU tar rejects.

The merged repair adds a stateful GNU basic/extended translation boundary, rejects forms whose meaning is not proved, and keeps positive controls so a rejection guard does not accidentally ban escaped literals or bracket members.

## Why we care

Archive member names are identities. A silent regex mismatch can alter package layout, link relationships, PAX `path` or `linkpath`, extraction targets, and overwrite behavior while the command still exits successfully.

A visible compile error is safer than a plausible but different archive. The goal is bounded compatibility with explicit rejection outside the proved subset, not an unearned claim of complete GNU/POSIX parity.

## What happens if we leave it alone

Default GNU basic operators and Python operators disagree. GNU tar accepts `x` for extended syntax; escaped groups and backreferences change validity by dialect; anchors and repeated quantifiers are contextual; Python-only `(?...)` syntax may compile and silently create a different language.

Leaving the direct Python path in place would preserve silent wrong-name behavior. Adding only a broad `(?` string rejection would create a second defect by rejecting escaped `(` or bracket-expression content.

## Current finding

A GNU-tar-compatible transform layer must choose the source dialect explicitly and translate with parser state. The merged implementation:

- uses GNU basic syntax by default;
- uses GNU extended syntax when `x` is present;
- handles escapes, bracket expressions, groups, alternation, anchors, intervals, backreferences, and tested repeated-quantifier forms contextually;
- rejects unsupported POSIX bracket constructs, unresolved alphabetic escapes, Python-only active `(?...)` groups, and tested invalid interval forms before archive output;
- composes with occurrence selectors and member, hard-link, symlink, and PAX path handling.

The separate PR #220 controls prove that the Python-group guard still accepts `s/\(?/X/x`, `s/[(?]/X/x`, and `s/\(/X/x` exactly where GNU tar 1.35 accepts them.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Directly applying GNU-style transforms with Python `re` produces semantic and validity mismatches. | target-executed | predecessor differential suite retained through PR #151; GNU tar 1.35 comparisons | Does not measure real-world frequency. |
| The merged translator matches the executed GNU basic/extended matrix and rejects the unproved subset before archive output. | target-executed | PR #151 head `4555c5c...`; Linux Fieldwork CI `30579057679` / 577 success | Does not establish complete POSIX/GNU compatibility. |
| The active `(?...)` guard does not reject escaped literal parentheses or bracket members. | target-executed | PR #220 head `bb0a79de...`; Linux Fieldwork CI `30582215292` / 634 success | Covers three direct accepted-neighbor expressions only. |
| Archive transform scope remains composed across member names, link targets, occurrence selectors, and PAX regeneration. | target-executed | inherited edge matrix in the product and control suites | Locale, encoding, and all metadata formats remain bounded by the retained matrix. |

## System and ownership map

- Entry point: tarfilter transform-expression parsing and application.
- Language boundary owner: the translator converts GNU basic or extended syntax to the supported Python matcher subset.
- State owner: scanner state tracks escapes, bracket expressions, groups, branches, anchors, and intervals.
- Archive owner: transformed member names and link targets feed PAX regeneration and output writing.
- Failure owner: unsupported syntax is rejected before any archive output.
- Test boundary: GNU tar 1.35 under `LC_ALL=C`, exact patch composition, generated archives, member/link/PAX comparisons, and malformed controls.

## Historical precedent

### GNU tar transform contract

- Source: https://www.gnu.org/software/tar/manual/html_section/transform.html
- Revision or date: GNU tar manual retrieved 2026-07-31; executable reference GNU tar 1.35
- Principle supported: transform expressions follow sed-style syntax, with flags controlling scope and regex behavior.
- Important difference: tarfilter keeps Python for archive processing and therefore needs an explicit translation boundary rather than GNU tar's native matcher.

### POSIX basic and extended regular expressions

- Source: https://pubs.opengroup.org/onlinepubs/9699919799/basedefs/V1_chap09.html
- Revision or date: POSIX.1-2017
- Principle supported: BRE and ERE assign different meanings to escaped and unescaped operators.
- Important difference: GNU extensions, Python-only constructs, locale behavior, and diagnostics require additional bounded treatment.

### Predecessor chain

- Source: Linux Fieldwork PRs #56, #68, #102, and #113
- Revision or date: retained before PR #151
- Principle supported: replacement count, transform scope, occurrence selectors, and differential characterization are independent invariants that must compose.
- Important difference: PR #151 owns regex-language translation; it does not replace the earlier archive-scope work.

## Approaches considered

### Retained approach: stateful bounded translator

This preserves the existing Python archive pipeline while making the advertised GNU language boundary explicit and executable. Unsupported syntax fails early rather than silently changing names.

### Declined: pass expressions straight to Python `re`

That is the demonstrated defect. Identical punctuation can mean a literal, operator, group, or invalid form depending on the source dialect.

### Declined: global punctuation replacements

Simple replacements cannot distinguish escapes, bracket expressions, branch boundaries, contextual anchors, groups, or backreferences.

### Declined: broad substring rejection for `(?`

It would reject accepted escaped and bracket-expression neighbors. PR #220 exists specifically to prevent that overreach.

### Deferred: complete GNU/POSIX engine

Locale, collation, POSIX bracket classes, diagnostics, performance limits, and GNU-specific escapes are large independent surfaces. The current repair is intentionally a proved subset with explicit rejection.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| default GNU basic versus explicit extended operators | differential matrix | translated to matching GNU output |
| capture and backreference validity by dialect | edge matrix | accepted or rejected to match executed reference |
| contextual anchors and branch-leading basic `*` | edge matrix | matching output and validity |
| literal `\0`, repeated simple quantifiers, tested repeated intervals | edge matrix | normalized or rejected consistently |
| active Python-only `(?...)` groups | product regression | rejected before output |
| escaped `(` followed by ERE `?` | PR #220 positive control | accepted and matches GNU tar |
| `(` and `?` inside a bracket expression | PR #220 positive control | accepted and matches GNU tar |
| escaped literal `(` | PR #220 positive control | accepted and matches GNU tar |
| member, hard-link, symlink, PAX, and occurrence scope | inherited composition tests | preserved |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| POSIX bracket classes, collating elements, equivalence classes | not covered by the bounded translator | reopen with a differential matrix and source design |
| locale-sensitive ranges and non-`C` locales | GNU/Python locale semantics differ | new locale compatibility finding |
| GNU alphabetic escapes and word boundaries | unresolved translation semantics | reopen when a caller or test requires them |
| malformed diagnostic wording parity | correctness finding owns accept/reject and output, not exact messages | separate diagnostic-compatibility finding |
| catastrophic backtracking or resource limits | performance/security policy distinct from syntax parity | new denial-of-service finding |
| persistent `flags=` and semicolon expression lists | separate transform-state language | owning later expression-state lane |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| linux-fieldwork@`4555c5c250c1afedb3947fd1a7b5a0323bd9d262` | Linux Fieldwork CI `30579057679` / 577 | hosted Linux; GNU tar 1.35 differential fixtures | success | target-executed |
| linux-fieldwork@`ee8b25d3f878a28db2e75076bb499bcc1c884101` | Linux Fieldwork CI `30579704392` / 589 | hosted Linux | success for first clean positive-control content | target-executed |
| linux-fieldwork@`bb0a79dec47958c6b865d4b382a44baff17ab736` | Linux Fieldwork CI `30582215292` / 634 | hosted Linux | success | target-executed |
| retained control | `python3 tests/test_tarfilter_transform_regex_python_group_controls.py` | Linux with GNU tar 1.35, `LC_ALL=C` | inherited matrix plus 3 controls success | target-executed |

## Complete-diff and compatibility review

- Product changed-file fence: seven files in PR #151.
- Positive-control changed-file fence: two files in PR #220.
- Current-base relationship: product merged as `1a1952a78f79b2473f1f9513c1d5820f58987594`; controls merged as `ed49c01a85e9d363626db5d2973a33b67209e13b`.
- Temporary carrier status: PRs #202, #203, and #210 were closed after repaired or unique content reached canonical carriers.
- Compatibility surfaces examined: BRE/ERE operators, escapes, brackets, groups, branches, anchors, intervals, backreferences, occurrence selectors, member/link/PAX scope, and accepted neighbors of the Python-group guard.
- Known routine repair remaining: none within the bounded executed subset.
- Review eligibility: exact product and proof heads completed hosted CI; local merge does not authorize public submission.

## Current disposition and desk routing

- Finding state: `closed`
- Review disposition: `ACCEPT`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: none; retain merged product and positive controls
- Clearing condition: satisfied by PR #151 and PR #220 merges plus runs 577 and 634
- Required subgates: none
- Autonomous work remaining: none within scope
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | predecessor review | found Python-only active groups accepted where GNU tar rejected them |
| 2026-07-30 | PR #151 head `4555c5c...` | repaired the guard and merged the bounded translator |
| 2026-07-30 | PR #220 head `bb0a79de...` | retained accepted-neighbor controls; run 634 succeeded and merged |
| 2026-07-31 | Linux Fieldwork PR #249 | corrected the tracked proof record from pending to exact merged state |

## References

- https://github.com/teamleaderleo/linux-fieldwork/pull/151
- https://github.com/teamleaderleo/linux-fieldwork/pull/220
- https://github.com/teamleaderleo/linux-fieldwork/issues/108
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/investigations/tarfilter-transform-regex-python-group-controls/README.md
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/tests/test_tarfilter_transform_regex_python_group_controls.py
- Linux Fieldwork CI runs `30579057679`, `30579704392`, and `30582215292`
- Linux Fieldwork PR #249 durable-state repair
