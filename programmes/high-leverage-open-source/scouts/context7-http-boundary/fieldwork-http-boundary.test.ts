import { createDecipheriv } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname } from "node:path";

import type express from "express";
import { afterAll, describe, expect, test } from "vitest";

import { getClientIp } from "../src/lib/client-ip.js";
import { generateHeaders } from "../src/lib/encryption.js";

const TARGET_HEAD = "594a73133e14631af8c915a1b4f2c8039c964fe1";
const TEST_ENCRYPTION_KEY = "1111111111111111111111111111111111111111111111111111111111111111";

const outcomes: Record<string, string> = {};

function makeRequest(
  headers: Record<string, string | string[]>,
  remoteAddress: string
): express.Request {
  return {
    headers,
    socket: { remoteAddress },
  } as express.Request;
}

function decryptClientIp(value: string): string {
  const [ivHex, encryptedHex] = value.split(":");
  if (!ivHex || !encryptedHex) throw new Error("Expected encrypted client-IP metadata");

  const decipher = createDecipheriv(
    "aes-256-cbc",
    Buffer.from(TEST_ENCRYPTION_KEY, "hex"),
    Buffer.from(ivHex, "hex")
  );
  let decrypted = decipher.update(encryptedHex, "hex", "utf8");
  decrypted += decipher.final("utf8");
  return decrypted;
}

afterAll(() => {
  const receiptPath = process.env.FIELDWORK_CONTEXT7_IDENTITY_RECEIPT;
  if (!receiptPath) return;

  mkdirSync(dirname(receiptPath), { recursive: true });
  writeFileSync(
    receiptPath,
    `${JSON.stringify(
      {
        schemaVersion: 1,
        targetHead: TARGET_HEAD,
        encryptionVariable: "CLIENT_IP_ENCRYPTION_KEY",
        encryptionKeySource: "explicit-test-environment",
        outcomes,
        claimClasses: {
          requestParser: "target-executed",
          parserToOutboundMetadata: "target-executed",
          httpRouteContextWiring: "source-read",
          hostedApiReceipt: "not-executed",
        },
      },
      null,
      2
    )}\n`
  );
});

describe("Fieldwork Context7 HTTP identity boundary", () => {
  test("a direct caller can replace socket identity with a public-looking forwarded IP", () => {
    const req = makeRequest({ "x-forwarded-for": "198.51.100.77" }, "203.0.113.9");

    expect(getClientIp(req)).toBe("198.51.100.77");
    outcomes.publicForwardedIpOverridesSocket = "passed";
  });

  test("a direct caller controls identity even when every forwarded entry is private", () => {
    const req = makeRequest({ "x-forwarded-for": "127.0.0.1, 10.0.0.8" }, "203.0.113.9");

    expect(getClientIp(req)).toBe("127.0.0.1");
    outcomes.privateForwardedListOverridesSocket = "passed";
  });

  test("socket identity is used only when the forwarded header is absent", () => {
    const req = makeRequest({}, "::ffff:203.0.113.9");

    expect(getClientIp(req)).toBe("203.0.113.9");
    outcomes.socketFallbackWithoutForwardedHeader = "passed";
  });

  test("caller-selected identity becomes outbound encrypted metadata", () => {
    expect(process.env.CLIENT_IP_ENCRYPTION_KEY).toBe(TEST_ENCRYPTION_KEY);
    const req = makeRequest({ "x-forwarded-for": "198.51.100.77" }, "203.0.113.9");
    const selectedClientIp = getClientIp(req);
    const headers = generateHeaders({ clientIp: selectedClientIp, transport: "http" });
    const encryptedClientIp = headers["mcp-client-ip"];

    expect(encryptedClientIp).toBeDefined();
    expect(decryptClientIp(encryptedClientIp)).toBe("198.51.100.77");
    outcomes.forwardedIpReachesOutboundMetadata = "passed";
  });

  test.fails(
    "repair control: socket identity wins without an explicit trusted-proxy policy",
    () => {
      outcomes.trustedProxyRepairControl = "expected-failure";
      const req = makeRequest({ "x-forwarded-for": "198.51.100.77" }, "203.0.113.9");

      expect(getClientIp(req)).toBe("203.0.113.9");
    }
  );
});
