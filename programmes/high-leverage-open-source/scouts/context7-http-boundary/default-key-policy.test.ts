import { createDecipheriv } from "crypto";
import { afterEach, describe, expect, test, vi } from "vitest";

const CLIENT_IP = "198.51.100.77";
const PUBLIC_DEFAULT_KEY =
  "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f";
const EXPLICIT_TEST_KEY =
  "f00102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1eff";
const MISSING_KEY_MESSAGE =
  "CLIENT_IP_ENCRYPTION_KEY is required; omitting mcp-client-ip metadata.";

type Candidate = "compatibility-retained" | "explicit-key-only";

function candidate(): Candidate {
  const value = process.env.FIELDWORK_CANDIDATE;
  if (value !== "compatibility-retained" && value !== "explicit-key-only") {
    throw new Error(
      "FIELDWORK_CANDIDATE must name one exact default-key policy candidate",
    );
  }
  return value;
}

async function loadGenerateHeaders(key: string | undefined) {
  vi.resetModules();
  if (key === undefined) {
    delete process.env.CLIENT_IP_ENCRYPTION_KEY;
  } else {
    process.env.CLIENT_IP_ENCRYPTION_KEY = key;
  }
  return (await import("../src/lib/encryption.js")).generateHeaders;
}

function decryptClientIp(value: string, key: string): string {
  const [ivHex, ciphertextHex, extra] = value.split(":");
  expect(extra).toBeUndefined();
  expect(ivHex).toMatch(/^[0-9a-f]{32}$/);
  expect(ciphertextHex).toMatch(/^[0-9a-f]+$/);
  const decipher = createDecipheriv(
    "aes-256-cbc",
    Buffer.from(key, "hex"),
    Buffer.from(ivHex, "hex"),
  );
  let plaintext = decipher.update(ciphertextHex, "hex", "utf8");
  plaintext += decipher.final("utf8");
  return plaintext;
}

function generate(generateHeaders: Awaited<ReturnType<typeof loadGenerateHeaders>>) {
  return generateHeaders({
    clientIp: CLIENT_IP,
    sessionId: "session-default-policy",
    apiKey: "test-api-key",
    transport: "http",
    clientInfo: { ide: "fieldwork", version: "1.0.0" },
  });
}

function expectUnrelatedHeaders(headers: Record<string, string>) {
  expect(headers["X-Context7-Source"]).toBe("mcp-server");
  expect(headers["mcp-session-id"]).toBe("session-default-policy");
  expect(headers["Authorization"]).toBe("Bearer test-api-key");
  expect(headers["X-Context7-Transport"]).toBe("http");
  expect(headers["X-Context7-Client-IDE"]).toBe("fieldwork");
  expect(headers["X-Context7-Client-Version"]).toBe("1.0.0");
}

afterEach(() => {
  delete process.env.CLIENT_IP_ENCRYPTION_KEY;
  vi.restoreAllMocks();
  vi.resetModules();
});

describe.sequential("Context7 client-IP default-key policy", () => {
  test("classifies absent and empty configuration exactly", async () => {
    const selected = candidate();

    for (const configuredKey of [undefined, ""] as const) {
      const diagnostic = vi.spyOn(console, "error").mockImplementation(() => {});
      const generateHeaders = await loadGenerateHeaders(configuredKey);
      const headers = generate(generateHeaders);
      expectUnrelatedHeaders(headers);

      if (selected === "compatibility-retained") {
        expect(headers["mcp-client-ip"]).toMatch(
          /^[0-9a-f]{32}:[0-9a-f]+$/,
        );
        expect(
          decryptClientIp(headers["mcp-client-ip"], PUBLIC_DEFAULT_KEY),
        ).toBe(CLIENT_IP);
        expect(diagnostic).not.toHaveBeenCalled();
      } else {
        expect(headers).not.toHaveProperty("mcp-client-ip");
        expect(diagnostic).toHaveBeenCalledWith(MISSING_KEY_MESSAGE);
        expect(diagnostic.mock.calls.flat().join(" ")).not.toContain(CLIENT_IP);
      }

      diagnostic.mockRestore();
    }
  });

  test("preserves metadata with an explicit valid non-public key", async () => {
    const diagnostic = vi.spyOn(console, "error").mockImplementation(() => {});
    const generateHeaders = await loadGenerateHeaders(EXPLICIT_TEST_KEY);
    const headers = generate(generateHeaders);

    expectUnrelatedHeaders(headers);
    expect(headers["mcp-client-ip"]).toMatch(/^[0-9a-f]{32}:[0-9a-f]+$/);
    expect(headers["mcp-client-ip"]).not.toContain(CLIENT_IP);
    expect(decryptClientIp(headers["mcp-client-ip"], EXPLICIT_TEST_KEY)).toBe(
      CLIENT_IP,
    );
    expect(diagnostic).not.toHaveBeenCalled();
  });
});
