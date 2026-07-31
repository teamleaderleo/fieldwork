import { describe, expect, test } from "vitest";
import type express from "express";
import {
  createClientIpPolicy,
  getClientIp,
  isPrivateOrLocalIp,
} from "../src/lib/client-ip.js";

describe("isPrivateOrLocalIp", () => {
  test.each([
    "10.0.0.1",
    "192.168.1.1",
    "172.16.0.1",
    "127.0.0.1",
    "169.254.1.1",
    "100.64.0.1",
    "100.127.255.255",
    "::1",
    "0::1",
    "0:0:0:0:0:0:0:1",
    "fe80::1",
    "FE80::1",
    "febf::1",
    "fc00::1",
    "fd12::1",
    "fdff::1",
    "::ffff:127.0.0.1",
  ])("treats %s as private or local", (ip) => {
    expect(isPrivateOrLocalIp(ip)).toBe(true);
  });

  test.each([
    "8.8.8.8",
    "203.0.113.10",
    "100.63.255.255",
    "100.128.0.1",
    "2001:db8::1",
    "1::1",
    "::11",
    "::ffff:8.8.8.8",
    "fe8::1",
    "fc::1",
    "fd0::1",
    "fec0::1",
  ])("treats %s as public", (ip) => {
    expect(isPrivateOrLocalIp(ip)).toBe(false);
  });
});

describe("getClientIp trusted-proxy policy", () => {
  function makeRequest(
    headers: Record<string, string | string[]>,
    remoteAddress?: string
  ): express.Request {
    return {
      headers,
      socket: remoteAddress ? { remoteAddress } : undefined,
    } as express.Request;
  }

  test("ignores caller-controlled forwarding by default", () => {
    const req = makeRequest(
      { "x-forwarded-for": "198.51.100.77" },
      "203.0.113.10"
    );

    expect(getClientIp(req)).toBe("203.0.113.10");
  });

  test("requires a socket address even when forwarding is present", () => {
    const req = makeRequest({ "x-forwarded-for": "198.51.100.77" });
    const policy = createClientIpPolicy("10.0.0.0/8");

    expect(getClientIp(req, policy)).toBeUndefined();
  });

  test("accepts one forwarded client from an explicitly trusted socket", () => {
    const req = makeRequest(
      { "x-forwarded-for": "198.51.100.77" },
      "10.0.0.9"
    );
    const policy = createClientIpPolicy("10.0.0.0/8");

    expect(getClientIp(req, policy)).toBe("198.51.100.77");
  });

  test("walks a trusted proxy chain from right to left", () => {
    const req = makeRequest(
      { "x-forwarded-for": "198.51.100.77, 192.168.20.3" },
      "10.0.0.9"
    );
    const policy = createClientIpPolicy(
      "10.0.0.0/8, 192.168.0.0/16"
    );

    expect(getClientIp(req, policy)).toBe("198.51.100.77");
  });

  test("does not accept a spoofed prefix before the nearest untrusted hop", () => {
    const req = makeRequest(
      {
        "x-forwarded-for":
          "203.0.113.250, 198.51.100.77, 192.168.20.3",
      },
      "10.0.0.9"
    );
    const policy = createClientIpPolicy(
      "10.0.0.0/8, 192.168.0.0/16"
    );

    expect(getClientIp(req, policy)).toBe("198.51.100.77");
  });

  test("falls back to the socket when every forwarded hop is trusted", () => {
    const req = makeRequest(
      { "x-forwarded-for": "192.168.20.3, 10.1.2.3" },
      "10.0.0.9"
    );
    const policy = createClientIpPolicy(
      "10.0.0.0/8, 192.168.0.0/16"
    );

    expect(getClientIp(req, policy)).toBe("10.0.0.9");
  });

  test.each([
    "198.51.100.77, not-an-ip",
    "",
    "198.51.100.77:443",
    "[2001:db8::1]",
  ])("fails malformed forwarding %j closed to the socket", (forwarded) => {
    const req = makeRequest({ "x-forwarded-for": forwarded }, "10.0.0.9");
    const policy = createClientIpPolicy("10.0.0.0/8");

    expect(getClientIp(req, policy)).toBe("10.0.0.9");
  });

  test("fails duplicate forwarded header values closed to the socket", () => {
    const req = makeRequest(
      { "x-forwarded-for": ["198.51.100.77", "203.0.113.10"] },
      "10.0.0.9"
    );
    const policy = createClientIpPolicy("10.0.0.0/8");

    expect(getClientIp(req, policy)).toBe("10.0.0.9");
  });

  test("matches an IPv4-mapped trusted socket against an IPv4 CIDR", () => {
    const req = makeRequest(
      { "x-forwarded-for": "198.51.100.77" },
      "::ffff:10.0.0.9"
    );
    const policy = createClientIpPolicy("10.0.0.0/8");

    expect(getClientIp(req, policy)).toBe("198.51.100.77");
  });

  test("supports an explicit IPv6 trusted proxy subnet", () => {
    const req = makeRequest(
      { "x-forwarded-for": "2001:db8:2::77" },
      "2001:db8:1::9"
    );
    const policy = createClientIpPolicy("2001:db8:1::/64");

    expect(getClientIp(req, policy)).toBe("2001:db8:2::77");
  });

  test.each([
    "10.0.0.0/33",
    "2001:db8::/129",
    "10.0.0.0/not-a-prefix",
    "not-an-ip/24",
    "10.0.0.0/8/extra",
    "10.0.0.0/8,",
  ])("rejects invalid trusted-proxy configuration %j", (configuration) => {
    expect(() => createClientIpPolicy(configuration)).toThrow(
      "Invalid CONTEXT7_TRUSTED_PROXY_CIDRS configuration"
    );
  });
});
