## In simple words

This curl round found one narrow HTTP resume state defect worth promoting.

When curl resumes a download, it expects a successful partial response to confirm the byte offset in `Content-Range`. Current source does that for numeric ranges, but treats a `Content-Range` whose first meaningful character is `*` differently on any response below 300: it resets the internal resume offset to zero with the comment `get everything`.

That `*` form means the requested range was unsatisfied according to curl's own source comment. On a malformed `206 Partial Content` response such as `Content-Range: bytes */11`, clearing the resume offset disables curl's later resume-safety check. The curl command-line tool has already opened an existing partial output file in append mode. A local installed-curl control therefore turns a 5-byte partial file `hello` into `helloWORLD!` and exits successfully. The same fixture with no `Content-Range`, or a numeric range beginning at the wrong offset, returns curl error 33 and leaves the file at `hello`.

The historical source path is useful: the `*` handling and `resume_from = 0` reset were introduced in 2014 to parse unsatisfied ranges on `416 Requested Range Not Satisfiable`. Later fixes fenced 416 out of this reset. The surviving `<300` branch now applies the old reset to successful responses, where it bypasses the exact safety property resume mode is trying to enforce.

Disposition: **PROMOTE the 2xx unsatisfied-`Content-Range` resume branch to exact-pin execution and a focused regression/fix experiment.**

## Target and evidence

- target: `curl/curl`
- exact source revision read: `2c22d3069aef507d6a6876a6d20616fe5e50c6a3`
- branch: `master`
- retrieval date: `2026-08-11` UTC+8
- upstream permissions observed through the connector: read-only for this agent
- upstream contact authorization: `false`
- evidence classes used: `source-read`, `model-executed`
- supplemental execution: installed curl `8.10.1` against a loopback stdlib server
- exact target-native execution: pending
- excluded owned work: Fieldwork issue #470 / PR #474, which cover cache-persistence pre-truncation and are unrelated to this parser state

The retained probe is `probe.py`. It contains both a model of the pinned source transition and an optional installed-curl loopback discriminator. The installed binary is supporting evidence only; it does not upgrade this return to `target-executed`.

## Promote first — 2xx unsatisfied Content-Range clears resume safety

### Expected resume invariant

A resumed HTTP GET is safe to append only when the response confirms that its body begins at the requested local-file offset.

At a requested resume offset of 5, these controls distinguish the state:

- `206` + `Content-Range: bytes 5-10/11`: confirms offset 5; appending is coherent.
- `206` + no `Content-Range`: does not confirm the offset; current curl returns range error 33.
- `206` + `Content-Range: bytes 6-11/12`: confirms a different offset; current curl returns range error 33.
- `206` + `Content-Range: bytes */11`: says the requested range was unsatisfied, yet current header handling clears the requested offset and bypasses the same range-error check.

The fourth case is the candidate.

### Current source owner

Pinned source:

- https://github.com/curl/curl/blob/2c22d3069aef507d6a6876a6d20616fe5e50c6a3/lib/http.c

Current header handling documents four accepted historical shapes, including:

```text
Content-Range: [asterisk]/[total]
```

and explicitly says the asterisk form means the requested range was unsatisfied.

The parser then advances to the first digit or `*`. If it finds a digit and the parsed number equals `data->state.resume_from`, it marks `k->content_range = TRUE`. If it reaches anything other than a digit and the response status is below 300, current source does:

```text
data->state.resume_from = 0; /* get everything */
```

This creates the state transition at issue:

```text
resume requested at 5
+ 206 Content-Range: bytes */11
=> resume_from becomes 0
=> content_range remains false
=> later resume validation no longer runs
```

The later guard only rejects unsupported resume when `data->state.resume_from` remains nonzero and `k->content_range` is false. Its error is `CURLE_RANGE_ERROR` with the message that the HTTP server does not seem to support byte ranges.

### CLI output state makes the transition destructive

Pinned command-line source:

- https://github.com/curl/curl/blob/2c22d3069aef507d6a6876a6d20616fe5e50c6a3/src/tool_operate.c

For `--continue-at -`, the tool stats the existing output file and sets the requested resume offset to that file size. When resume is active, it opens the output file with mode `ab`.

That append decision occurs before the HTTP response headers can change libcurl's internal `resume_from` state. Resetting `resume_from` to zero therefore does not turn the already-open append stream into a replace/truncate stream. It only disables the later range-validation guard.

This is why the malformed successful response can append a body that has not proven its starting offset.

### Model probe

Run:

```text
python programmes/open-source-ecosystems/scouts/foundational-systems/curl-20260811/probe.py
```

The exact-source model checks:

```text
206 + bytes 5-10/11  -> resume=5, content_range=true
206 + bytes */11     -> resume=0, content_range=false
206 + bytes 6-11/12  -> resume=5, content_range=false
416 + bytes */5      -> resume=5, content_range=false
```

The `416` control records current behavior after the historical fixes: the unsatisfied range no longer resets resume state for that status.

### Installed curl control

The same probe optionally invokes the locally installed curl binary against a one-request loopback TCP server. The observed binary in this research environment was:

```text
curl 8.10.1 ... libcurl/8.10.1 ...
```

The output file begins as exactly five bytes:

```text
hello
```

The server body is six bytes:

```text
WORLD!
```

Observed controls:

| response | exit | output |
| --- | ---: | --- |
| `206`, `bytes 5-10/11` | 0 | `helloWORLD!` |
| `206`, `bytes */11` | 0 | `helloWORLD!` |
| `206`, no `Content-Range` | 33 | `hello` |
| `206`, `bytes 6-11/12` | 33 | `hello` |
| `416`, `bytes */5`, empty body | 0 | `hello` |

The key discriminator is the second row. Removing the header or supplying a conflicting numeric offset activates curl's range error and preserves the partial file. The unsatisfied `*` form alone converts that protected path into successful append.

This installed execution predates the exact pin and is therefore retained as supplemental behavior confirmation rather than target-native evidence.

## Historical source map

Commit:

- https://github.com/curl/curl/commit/0187c9e11d079335f6863e583704e4350fe6b3e8

The 2014 commit was titled `http: fix the Content-Range: parser`. It added explicit recognition of `*/[total]`, documented it as the form for an unsatisfied requested range, and added the unconditional `resume_from = 0; /* get everything */` fallback.

The associated test change was for a `416 Requested Range Not Satisfiable` response with `Content-Range: bytes */87`.

Later curl history fixed the 416 interaction. Current source now performs the reset only for `httpcode < 300`, leaving the 2xx residue investigated here.

Related historical report/fix family:

- https://github.com/curl/curl/issues/10521
- https://github.com/curl/curl/pull/10644
- https://github.com/curl/curl/pull/12176

Issue #10521 concerned the opposite status family: a valid 416 unsatisfied-range response reset resume state and broke special completed-download handling. The eventually merged fix family restored 416 behavior. It does not supply a current owner for malformed 2xx + `*` behavior.

### Why history raises confidence

The source comment, original commit, and historical test all associate `*` with an **unsatisfied** range. The current 2xx behavior uses that signal to discard the client's resume offset, which is semantically opposite to requiring proof before appending.

That does not require curl to make a malformed server response valid. It requires curl to fail safely instead of weakening its local-file consistency check after receiving contradictory framing metadata.

## Current test map

Relevant pinned tests inspected:

- `tests/data/test1475`
- `tests/data/test1156`
- `tests/libtest/lib1156.c`
- `tests/data/test1117`
- `tests/data/test3035`

Pinned URLs:

- https://github.com/curl/curl/blob/2c22d3069aef507d6a6876a6d20616fe5e50c6a3/tests/data/test1475
- https://github.com/curl/curl/blob/2c22d3069aef507d6a6876a6d20616fe5e50c6a3/tests/data/test1156
- https://github.com/curl/curl/blob/2c22d3069aef507d6a6876a6d20616fe5e50c6a3/tests/libtest/lib1156.c
- https://github.com/curl/curl/blob/2c22d3069aef507d6a6876a6d20616fe5e50c6a3/tests/data/test1117
- https://github.com/curl/curl/blob/2c22d3069aef507d6a6876a6d20616fe5e50c6a3/tests/data/test3035

Coverage found:

- test1475: `416` + `Content-Range: */100` under `-C - -f`; verifies existing output is preserved.
- lib1156/test1156: matrix across resume, fail-on-error, 200/416, and presence of `Content-Range`. Its successful 200 range uses numeric `Content-Range: bytes 3/7`.
- test1117: a normal numeric `206 Partial Content` range after a prior 416.
- test3035: retry/auto-resume with normal numeric 206 ranges and output consistency.

A focused search at the pin did not find a regression fixture combining a successful `206` resume with an unsatisfied `Content-Range: bytes */...` and an existing append-mode output file.

That missing discriminator is the first target-native test to add.

## Narrow fix experiment

The first experiment should preserve existing numeric and 416 behavior while refusing to weaken resume validation for a 2xx asterisk range.

A minimal behavioral target is:

1. matching numeric 206 offset: success, append body;
2. missing Content-Range under resumed 206: `CURLE_RANGE_ERROR`, preserve file;
3. wrong numeric 206 offset: `CURLE_RANGE_ERROR`, preserve file;
4. asterisk 206 Content-Range: same safe failure/preservation as an unconfirmed resume;
5. completed-file 416 `*/size`: retain current successful completed-download behavior;
6. non-resume transfer with a malformed 2xx `*` header: record compatibility before changing any unrelated path.

The smallest candidate may be to stop clearing `resume_from` for the asterisk case when an HTTP GET resume is active, allowing the existing post-header resume validation to decide the error. The exact source owner should remain bounded to `Curl_http_header` unless target-native tests reveal an interaction that requires a more explicit parser result.

### Policy choice to keep narrow

Two different projects could be attempted:

- **resume safety fix:** an unsatisfied `*` response cannot certify the requested append offset, so keep resume validation active;
- **strict Content-Range parser:** reject malformed grammar, arbitrary prefixes, mismatched status semantics, and other legacy formats.

This scout recommends the first. Curl intentionally accepts several historical nonstandard Content-Range forms. Tightening the entire parser would combine compatibility policy with the local-file corruption boundary and make review harder.

## Negative result — Transfer-Encoding `identity` prefix

Pinned source:

- https://github.com/curl/curl/blob/2c22d3069aef507d6a6876a6d20616fe5e50c6a3/lib/content_encoding.c

In one skip-decoding branch, current source checks identity with a prefix comparison over eight bytes. That means names beginning with `identity` can satisfy the local `is_identity` boolean.

A focused installed-curl control did not turn this into a distinct user-visible defect:

- in modes that skip non-chunk transfer decoding, unknown transfer codings are already accepted/skipped as a family;
- when transfer decoding is requested, exact `identity` succeeds while unknown names such as `identityX` reach the ordinary bad-content-encoding path.

Disposition: **STOP this branch.** The prefix expression is suspicious in isolation but did not survive the reachable-behavior discriminator.

## Other negative results retained

1. Current duplicate/multiple `Content-Length` handling explicitly accepts repeated equal values and rejects different or malformed values.
2. Current transfer-encoding handling rejects transfer codings listed after `chunked` and limits decoder stack depth.
3. Existing Fieldwork curl issue #470 / PR #474 own the unrelated persistence pre-truncation boundary, so no persistence/cache work was duplicated here.
4. Focused Fieldwork search found no current owner for this Content-Range resume branch.
5. Focused upstream open-PR search found no implementation for resumed `206` plus unsatisfied `Content-Range` at retrieval time.

## Ranked recommendation

1. **PROMOTE — 2xx unsatisfied Content-Range clears resume state and can permit append.** High mechanism confidence; medium promotion confidence until exact pin execution.
2. **TARGET-NATIVE NEXT — add a 206 `bytes */total` resume fixture with an existing output file.** Require error and byte preservation as the discriminator.
3. **KEEP FIX NARROW — preserve numeric legacy forms and current 416 completed-file semantics.** Avoid converting this into a general Content-Range grammar cleanup.
4. **STOP — Transfer-Encoding identity-prefix suspicion.** No distinct reachable consequence survived controls.
5. **REFRESH OWNERSHIP before any human upstream implementation/submission.** Existing public history is old, but current open ownership can change.

## Authority

This scout performed read-only inspection of `curl/curl`. No upstream issue, pull request, review, comment, reaction, branch, email, or other public interaction was created or changed.
