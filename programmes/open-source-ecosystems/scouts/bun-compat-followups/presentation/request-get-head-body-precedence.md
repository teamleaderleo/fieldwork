# Presentation candidate: Request GET/HEAD body precedence

## Proposed upstream title

`webcore: reject GET/HEAD bodies in the Request constructor with Fetch-compatible precedence`

## Status

**Ready to present as a compatibility candidate; implementation should remain coordinated with active RoboBun work.**

- Revalidated against Bun `main` at `9d519e8ca9f63a19f94790c47019bd7b6752c27a` on 2026-08-09.
- `src/runtime/webcore/Request.rs` is byte-identical to the original scout pin (`52bf09cb1cdbed0fbda4cf576e5d329cf92366ef`) for this path.
- Active overlap: https://redirect.github.com/oven-sh/bun/pull/37033 changes adjacent Request-input body copying and deliberately pins the current wrong GET/HEAD-vs-used-body precedence for a later compatibility change.
- No separate open Bun issue was found owning the constructor-level GET/HEAD body rule.
- Automated upstream contact remains prohibited; this is Fieldwork-owned preparation only.

## Problem

Bun enforces the GET/HEAD request-body restriction when fetching, but `new Request(...)` itself currently has no constructor-level rejection.

That produces two compatibility problems:

1. invalid `Request` objects can be constructed and survive until a later operation;
2. when several things are invalid at once, Bun reports a later body-processing error where Node/undici reports the GET/HEAD-body error first.

Reference behavior in Node `v22.16.0` / undici `6.21.2`:

```text
new Request(url, { method: "GET", body: "x" })
→ TypeError: Request with GET/HEAD method cannot have body.

new Request(usedPostRequest, { method: "GET" })
→ TypeError: Request with GET/HEAD method cannot have body.

new Request(lockedPostRequest, { method: "GET" })
→ TypeError: Request with GET/HEAD method cannot have body.

new Request(url, {
  method: "GET",
  body: new ReadableStream(),
  duplex: "half",
  keepalive: true,
})
→ TypeError: Request with GET/HEAD method cannot have body.
```

The same downstream failures remain visible when the method allows a body:

```text
POST + used input body
→ Cannot construct a Request with a Request object that has already been used.

POST + ReadableStream + keepalive
→ keepalive
```

Malformed URL parsing also remains earlier than body extraction:

```text
new Request("::::", {
  method: "GET",
  body: new ReadableStream(),
  duplex: "half",
  keepalive: true,
})
→ Failed to parse URL from ::::
```

## Why the obvious patch is insufficient

The current Bun constructor reads and **extracts** `init.body` inside the `values_to_try` loop before final URL parsing and before the constructor has completed final method selection. In particular, a ReadableStream body can hit the `keepalive` rejection and `BodyValue::from_js` before `href_from_string` validates the URL.

A single guard near the end of `construct_into` would therefore be too late: body extraction or an unusable-input check can already have thrown.

A guard at the top would also be wrong because the final method may come from `init`, and URL parsing must still beat body-extraction errors once WebIDL conversion has completed.

So this is a small ordering repair, not merely one new `if`.

## Suggested implementation seam

Keep the change local to `Request::construct_into` and the Request tests.

1. During the existing init-member pass, capture whether `init.body` is present/non-null and retain the raw JS value without extracting it yet. If it must survive later JS calls/GC, use the existing strong-handle pattern rather than a bare unrooted `JSValue`.
2. Preserve input-Request body presence separately. After #37033, `BodyValue::Empty` must count as a real non-null input body.
3. Complete final method selection and URL validation.
4. Before body extraction, stream keepalive validation, tee/proxy creation, or input-body usability checks, reject when:
   - effective method is GET or HEAD; and
   - `init.body` is non-null **or** the Request input has a non-null body.
5. Then continue the existing body path:
   - non-null `init.body` replaces the input body;
   - otherwise a disturbed/locked input body gets the existing used-Request TypeError;
   - stream+keepalive still gets the existing keepalive error for body-accepting methods.

The desired error text, matching Node/undici, is:

`Request with GET/HEAD method cannot have body.`

## Interaction with #37033

#37033 is adjacent and useful, not a reason to discard this candidate. It adds the input-Request unusable-body check and explicitly documents the remaining precedence mismatch:

- Node: GET/HEAD-body error wins over the used-body error.
- #37033 as currently written: used-body error wins because Bun lacks the constructor-level GET/HEAD check.

The cleanest implementation is therefore to layer this change on top of #37033 (or rebase immediately after it lands) and move that newly-added usability check behind the GET/HEAD-body guard.

## Regression matrix

The retained Fieldwork test already covers:

- GET and HEAD + direct init body;
- GET and HEAD + inherited Request body;
- inherited body with `init.body: null` / `undefined`;
- disturbed input body: GET error wins; POST still gets used-body error;
- locked input body: GET error wins; POST still gets used-body error;
- GET + ReadableStream + keepalive: GET error wins;
- malformed URL still beats the GET/HEAD body error.

Before implementation, add one extra discriminator to the target test:

- malformed URL + GET + ReadableStream + keepalive must throw the URL parse error, proving the patch did not merely move the body guard ahead of URL validation.

## Scope recommendation

**Good upstream-sized change after #37033 stabilizes.** Expected source footprint is `Request.rs` plus `test/js/web/request/request.test.ts` (and possibly a tiny adjustment to #37033's body-clone regression if the rebase requires it).

Avoid broad RequestInit/WebIDL cleanup in this PR. Bun has other constructor-order differences, but this candidate has a narrow observable contract with strong multi-invalid test cases. Fix the body phase boundary and leave unrelated dictionary-order work separate.

## Evidence labels

- Bun implementation: `source-read`, current main revalidated.
- Node/undici controls: `model-executed` locally on Node `v22.16.0`, undici `6.21.2`.
- Bun regression: `target-test-prepared`; exact-current Bun executable still unavailable to this Fieldwork worker.
