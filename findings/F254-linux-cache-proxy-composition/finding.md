# F254-linux-cache-proxy-composition: compose the complete request-to-cache lifecycle

Finding state: `closed`

Workstream: `H`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-linux-cache-proxy-composition/finding.md`  
Investigation workspace: `investigations/254-linux-storage-archive-reproducibility/`  
Canonical implementation: `teamleaderleo/linux-fieldwork` PR #198  
Exact implementation head: `5e69cd25e62d0e86364459d97c9df8568ff84187`  
Exact base or source revision: base `a0ec62f64fd6a9ff2cc20b28142ec876c52a5145`; imported proxy blob `e57a8516a0c76167894b05fc56be0e3165535488`  
Reviewed input generation: predecessor composition `00caba3d753536dd9a3a68fc6f110c75e338ec08`; final record head above  
Current review disposition: `ACCEPT`  
Desk routing: `not-entered`  
Upstream contact authorized: `no`

## In simple words

The caching proxy is a small development helper that fetches a package file for a client and keeps a local copy. Its request parser, origin connection, HTTP response handling, cache writer, and final-file publication all meet in one handler.

Several focused repairs were correct alone but overlapped in that same handler. The safe answer was not to trust a pile of separately green patches. Linux Fieldwork built one exact composed proxy and tested the complete trip from untrusted request text to final cache publication. That composition is merged locally.

## Why we care

A cache repeats wrong answers. A cached error page or truncated package can be served repeatedly. Request text can affect local path authority, proxy credentials can cross the wrong trust boundary, and a post-commit failure can produce a misleading HTTP stream.

The helper is used in development and CI rather than as a default public service, which bounds exposure. Inside that boundary, the consequences remain concrete: wrong package bytes, stale corrupted cache entries, credential leakage, path escape, and tests that report a success response before the cache is valid.

## What happens if we leave it alone

Individually green patches can still lose one another through source-anchor replacement or patch order. Ordinary Python can appear safe while `python -O` removes assertion checks. A final cache path can become visible before the body is complete, and a late error can append a second status after `200` already began.

The merged composition closes those demonstrated paths. Leaving only the focused branches would have preserved a composition gap.

## Current finding

The complete request-to-cache lifecycle must be validated and executed as one source state. The merged candidate:

1. accepts only the supported method and bodyless framing;
2. requires the absolute request target and `Host` to name the same origin;
3. confines cache paths below the selected root;
4. strips proxy credentials and hop-by-hop request fields;
5. checks origin status in ordinary runtime code;
6. validates transfer coding and declared length before downstream commitment;
7. writes into an exclusive hidden temporary file;
8. publishes the final name only after complete receipt;
9. sends one `502` before commitment;
10. logs and closes after commitment without emitting a second response.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| The nine-file source composition enforces the listed request, origin, framing, publication, and post-commit invariants together. | integration-executed | Linux Fieldwork PR #198 head `5e69cd25e62d0e86364459d97c9df8568ff84187`; CI run `30580697438` / 612 success; `tests/test_caching_proxy_complete_stack.py` | Does not prove crash durability, remote deployment policy, or all URI syntax. |
| Optimized Python cannot erase the selected status and request checks. | integration-executed | ordinary and optimized paths in the retained complete-stack matrix; Python `assert` specification | Does not establish behavior for unrelated interpreter optimizations or alternative runtimes. |
| The imported mmdebstrap source is preserved; the repository generates the candidate for evidence. | source-read | PR #198 complete nine-file diff and `investigations/caching-proxy-complete-stack/compose.py` | No upstream source branch or release is changed. |
| Cache publication stays hidden until full receipt and cleans incomplete temporaries before retry. | integration-executed | fixed-length premature-EOF, writer-failure, cleanup, mode, and retry cases in the complete-stack test | Same-UID path replacement after validation remains outside scope. |

## System and ownership map

- Entry point: generated candidate based on `upstream/mmdebstrap/caching_proxy.py`.
- Request owner: `ProxyRequestHandler.do_GET` validates method, body framing, target authority, and path.
- Origin owner: one `HTTPConnection` sends sanitized request headers and yields status/framing/body.
- Downstream owner: the handler decides when `200` may be committed and when only connection close remains possible.
- Cache owner: `cache_destination` creates an exclusive temporary with baseline-compatible mode and atomically replaces the final name after success.
- Cleanup: exceptions remove the temporary; pre-commit errors return one `502`; post-commit errors close the connection.
- Test boundary: local origin and client sockets, ordinary and optimized Python subprocesses, complete cache-tree inspection, and retry.

## Historical precedent

### HTTP absolute-form and authority

- Source: https://www.rfc-editor.org/rfc/rfc9112.html#name-absolute-form
- Revision or date: RFC 9112, 2022
- Principle supported: a forwarding proxy derives routing authority from the absolute request target and validates host information.
- Important difference: the finding also maps the accepted URL path into a local cache namespace.

### HTTP message framing and incomplete bodies

- Source: https://www.rfc-editor.org/rfc/rfc9112.html#name-message-body-length
- Revision or date: RFC 9112, 2022
- Principle supported: invalid or incomplete upstream framing cannot be treated as a complete successful response.
- Important difference: the local invariant includes both downstream signaling and final cache publication.

### Hop-by-hop fields

- Source: https://www.rfc-editor.org/rfc/rfc9110.html#name-message-forwarding
- Revision or date: RFC 9110, 2022
- Principle supported: connection-specific fields belong to one hop and must not be forwarded blindly.
- Important difference: the focused matrix also checks proxy credentials and dynamic `Connection` tokens.

### Python optimized assertions

- Source: https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement
- Revision or date: Python language reference retrieved 2026-07-31
- Principle supported: `python -O` emits no assertion code.
- Important difference: the repair replaces security- and protocol-bearing assertions with ordinary runtime checks rather than banning optimized mode.

### Path traversal containment

- Source: https://cwe.mitre.org/data/definitions/22.html
- Revision or date: CWE-22 retrieved 2026-07-31
- Principle supported: canonicalize and verify containment before granting filesystem authority.
- Important difference: same-UID mutation between check and open is explicitly not claimed solved.

## Approaches considered

### Retained approach: explicit composition and one integration matrix

Generate one candidate from exact retained inputs, keep source identity visible, and execute the complete request-to-cache lifecycle under ordinary and optimized Python. This is the smallest approach that can detect patch-order loss across the overlapping handler.

### Declined: trust separately green focused patches

The patches replace adjacent source anchors and can remove one another's checks. Separate success does not establish composed behavior.

### Declined: keep assertions for friendly inputs

Optimized Python removes them. The affected checks govern authority and protocol validity, so they must execute in ordinary runtime control flow.

### Deferred: solve miss coalescing and crash durability in the same change

Those are distinct concurrency and persistence invariants. Combining them would widen source, test, and review scope without strengthening the demonstrated repair.

## Edge cases covered

| Edge case or control | Evidence | Result |
| --- | --- | --- |
| method, body framing, target/Host disagreement, encoded or escaping path | complete-stack matrix | rejected before origin or cache side effects |
| proxy credentials and connection-nominated request headers | complete-stack matrix | stripped before origin request |
| origin non-200 under ordinary and optimized Python | complete-stack matrix | one `502`, no cache entry |
| fixed, chunked, and EOF-delimited successful bodies | complete-stack matrix | downstream bytes and final cache entry complete |
| invalid length, unsupported transfer coding, premature EOF | complete-stack matrix | no published incomplete cache entry |
| cache-writer or downstream failure | complete-stack matrix | original failure retained; temporary cleaned; no second status |
| concurrent misses and retry | complete-stack matrix | duplicate download remains possible; no partial final-name visibility |
| final mode and cleanup | complete-stack matrix | baseline-compatible mode; temporary removed |

## Edge cases deferred or outside scope

| Edge case | Why deferred | Owning next record or reopening trigger |
| --- | --- | --- |
| same-UID pathname replacement after validation | requires descriptor-relative or directory-handle design | reopen if source candidate targets race-resistant open semantics |
| miss coalescing | separate concurrency policy | new bounded cache-generation finding |
| file and directory `fsync` | separate crash-durability contract | new persistence finding |
| checksums or authentication | content trust policy is distinct from transport completeness | reopen with explicit integrity authority |
| remote deployment and broader URI syntax | helper is currently bounded to local development/CI use | reopen when deployment or caller contract expands |

## Exact execution and receipts

| Repository/head | Command or workflow | Platform/environment | Result | Evidence class |
| --- | --- | --- | --- | --- |
| linux-fieldwork@`00caba3d753536dd9a3a68fc6f110c75e338ec08` | Linux Fieldwork CI `30578916643` / 572 | hosted Linux | success | integration-executed |
| linux-fieldwork@`5e69cd25e62d0e86364459d97c9df8568ff84187` | Linux Fieldwork CI `30580697438` / 612 | hosted Linux | success | integration-executed |
| retained candidate | `python3 -m unittest -v tests/test_caching_proxy_complete_stack.py` | local Linux | 7 tests, success | integration-executed |

## Complete-diff and compatibility review

- Complete changed-file fence: nine files in PR #198.
- Current-base relationship at merge: PR base `a0ec62f64fd6a9ff2cc20b28142ec876c52a5145`; merged as `8d9f7fa92f0cb2f553ca3578b78d7e04f4e4167f`.
- Temporary carrier status: focused inputs are retained as evidence; superseded composition carriers were closed.
- Compatibility surfaces examined: request authority, path identity, request/response hop fields, fixed/chunked/EOF framing, status, optimized Python, file mode, temporary cleanup, retry, concurrent misses, and post-commit behavior.
- Known routine repair remaining: none within the bounded finding.
- Review eligibility: the final source head and complete diff were reviewed; the local merge is not public upstream acceptance.

## Current disposition and desk routing

- Finding state: `closed`
- Review disposition: `ACCEPT`
- Review Queue entry: none
- Delivery lane: `not-entered`
- Exact next transition: none; retain the merged local evidence
- Clearing condition: satisfied by PR #198 merge and exact-head CI run 612
- Required subgates: none
- Autonomous work remaining: none within scope
- Non-delegable human decision: none

## Changes to the canonical conclusion

| Date | Pull request or commit | Change in conclusion |
| --- | --- | --- |
| 2026-07-30 | predecessor head `00caba3d...` | complete composition first passed Linux Fieldwork CI run 572 |
| 2026-07-30 | PR #198 head `5e69cd25...` | tracked front-page state was repaired and the exact final head passed run 612 |
| 2026-07-30 | merge `8d9f7fa9...` | local evidence composition closed |
| 2026-07-31 | Linux Fieldwork PR #249 | durable README changed from pre-merge wording to exact merged state |

## References

- https://github.com/teamleaderleo/linux-fieldwork/pull/198
- https://github.com/teamleaderleo/linux-fieldwork/issues/188
- https://github.com/teamleaderleo/linux-fieldwork/issues/194
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/investigations/caching-proxy-complete-stack/README.md
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/investigations/caching-proxy-complete-stack/compose.py
- https://github.com/teamleaderleo/linux-fieldwork/blob/main/tests/test_caching_proxy_complete_stack.py
- Linux Fieldwork CI runs `30578916643` and `30580697438`
- Linux Fieldwork PR #249 durable-state repair
