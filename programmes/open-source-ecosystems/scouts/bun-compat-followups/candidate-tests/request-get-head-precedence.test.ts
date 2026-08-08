// Prepared regression candidate for oven-sh/bun; Fieldwork-owned, unexecuted on Bun.
// Evidence class: target-test-prepared.
// Intended neighborhood: test/js/web/request/request.test.ts.

import { describe, expect, test } from "bun:test";

const bodyError = "Request with GET/HEAD method cannot have body.";
const usedError = "Cannot construct a Request with a Request object that has already been used.";

function postRequest() {
  return new Request("https://example.com/", { method: "POST", body: "payload" });
}

function expectBodyError(fn: () => unknown) {
  expect(fn).toThrow(bodyError);
}

function expectUrlError(fn: () => unknown) {
  expect(fn).toThrow(/Invalid URL|parse URL|URL/i);
}

describe("Request GET/HEAD body precedence", () => {
  test.each(["GET", "HEAD"])("rejects %s with init body", method => {
    expectBodyError(() => new Request("https://example.com/", { method, body: "x" }));
  });

  test.each(["GET", "HEAD"])("rejects %s when inheriting an input body", method => {
    expectBodyError(() => new Request(postRequest(), { method }));
  });

  test("null and undefined init.body do not suppress an inherited body", () => {
    expectBodyError(() => new Request(postRequest(), { method: "GET", body: null }));
    expectBodyError(() => new Request(postRequest(), { method: "GET", body: undefined }));
  });

  test("a replacement init body still makes GET invalid", () => {
    expectBodyError(() => new Request(postRequest(), { method: "GET", body: "fresh" }));
  });

  test("GET/HEAD body error wins over disturbed input-body error", async () => {
    const input = postRequest();
    await input.text();
    expectBodyError(() => new Request(input, { method: "GET" }));
    expect(() => new Request(input, { method: "POST" })).toThrow(usedError);
  });

  test("GET/HEAD body error wins over locked input-body error", () => {
    const input = postRequest();
    const reader = input.body!.getReader();
    try {
      expectBodyError(() => new Request(input, { method: "GET" }));
      expect(() => new Request(input, { method: "POST" })).toThrow(usedError);
    } finally {
      reader.releaseLock();
    }
  });

  test("GET/HEAD body error wins over ReadableStream keepalive extraction error", () => {
    expectBodyError(
      () =>
        new Request("https://example.com/", {
          method: "GET",
          body: new ReadableStream(),
          duplex: "half",
          keepalive: true,
        }),
    );

    // Control: once the method accepts a body, the downstream validation
    // remains observable.
    expect(
      () =>
        new Request("https://example.com/", {
          method: "POST",
          body: new ReadableStream(),
          duplex: "half",
          keepalive: true,
        }),
    ).toThrow("keepalive");
  });

  test("URL parsing still wins before body-phase errors", () => {
    expectUrlError(() => new Request("::::", { method: "GET", body: "x" }));

    // Stronger discriminator: a shallow patch that merely moves the GET/HEAD
    // guard ahead of the current body extraction would pass the case above but
    // could still get the constructor phase ordering wrong. The malformed URL
    // must also beat the ReadableStream+keepalive path.
    expectUrlError(
      () =>
        new Request("::::", {
          method: "GET",
          body: new ReadableStream(),
          duplex: "half",
          keepalive: true,
        }),
    );
  });
});
