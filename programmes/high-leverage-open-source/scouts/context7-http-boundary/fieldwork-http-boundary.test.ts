import { describe, expect, test } from "vitest";
import type express from "express";

import { getClientIp } from "../src/lib/client-ip.js";

function makeRequest(
  headers: Record<string, string | string[]>,
  remoteAddress: string
): express.Request {
  return {
    headers,
    socket: { remoteAddress },
  } as express.Request;
}

describe("Fieldwork Context7 HTTP identity boundary", () => {
  test("a direct caller can replace socket identity with a public-looking forwarded IP", () => {
    const req = makeRequest(
      { "x-forwarded-for": "198.51.100.77" },
      "203.0.113.9"
    );

    expect(getClientIp(req)).toBe("198.51.100.77");
  });

  test("a direct caller controls identity even when every forwarded entry is private", () => {
    const req = makeRequest(
      { "x-forwarded-for": "127.0.0.1, 10.0.0.8" },
      "203.0.113.9"
    );

    expect(getClientIp(req)).toBe("127.0.0.1");
  });

  test("socket identity is used only when the forwarded header is absent", () => {
    const req = makeRequest({}, "::ffff:203.0.113.9");

    expect(getClientIp(req)).toBe("203.0.113.9");
  });

  test.fails("repair control: socket identity wins without an explicit trusted-proxy policy", () => {
    const req = makeRequest(
      { "x-forwarded-for": "198.51.100.77" },
      "203.0.113.9"
    );

    expect(getClientIp(req)).toBe("203.0.113.9");
  });
});
