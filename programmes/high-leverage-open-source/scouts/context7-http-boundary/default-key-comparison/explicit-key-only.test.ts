import { createDecipheriv } from "crypto";
import { afterEach, describe, expect, test, vi } from "vitest";
import { SERVER_VERSION } from "../src/lib/constants.js";

const CLIENT_IP = "198.51.100.77";
const PUBLIC_DEFAULT_KEY =
  "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f";
const EXPLICIT_TEST_KEY =
  "f1e2d3c4b5a69788776655443322110000112233445566778899aabbccddeeff";
const MISSING_KEY_MESSAGE =
  "CLIENT_IP_ENCRYPTION_KEY is not configured; omitting mcp-client-ip metadata.";
const INVALID_KEY_MESSAGE =
  "Invalid encryption key format; omitting mcp-client-ip metadata.";
const CIPHER_FAILURE_MESSAGE =
  "Unable to encrypt client IP; omitting mcp-client-ip metadata.";

type CryptoModule = typeof import("crypto");

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
  const [ivHex, ciphertextHex] = value.split(":");
  if (!ivHex || !ciphertextHex) throw new Error("missing ciphertext fields");
  const decipher = createDecipheriv(
    "aes-256-cbc",
    Buffer.from(key, "hex"),
    Buffer.from(ivHex, "hex"),
  );
  let plaintext = decipher.update(ciphertextHex, "hex", "utf8");
  plaintext += decipher.final("utf8");
  return plaintext;
}

function expectBaseHeaders(headers: Record<string, string>) {
  expect(headers["X-Context7-Source"]).toBe("mcp-server");
  expect(headers["X-Context7-Server-Version"]).toBe(SERVER_VERSION);
}

afterEach(() => {
  delete process.env.CLIENT_IP_ENCRYPTION_KEY;
  vi.doUnmock("crypto");
  vi.restoreAllMocks();
  vi.resetModules();
});

describe.sequential("explicit-key-only client-IP metadata", () => {
  test.each([
    ["absent", undefined],
    ["empty", ""],
  ])("omits metadata for %s configuration", async (_, key) => {
    const diagnostic = vi.spyOn(console, "error").mockImplementation(() => {});
    const generateHeaders = await loadGenerateHeaders(key);
    const headers = generateHeaders({
      clientIp: CLIENT_IP,
      sessionId: "session-1",
      apiKey: "test-api-key",
      transport: "http",
    });

    expectBaseHeaders(headers);
    expect(headers).not.toHaveProperty("mcp-client-ip");
    expect(headers["mcp-session-id"]).toBe("session-1");
    expect(headers["Authorization"]).toBe("Bearer test-api-key");
    expect(headers["X-Context7-Transport"]).toBe("http");
    expect(diagnostic).toHaveBeenCalledWith(MISSING_KEY_MESSAGE);
    expect(diagnostic.mock.calls.flat().join(" ")).not.toContain(CLIENT_IP);
  });

  test("retains ciphertext only for an explicit valid key", async () => {
    const diagnostic = vi.spyOn(console, "error").mockImplementation(() => {});
    const generateHeaders = await loadGenerateHeaders(EXPLICIT_TEST_KEY);
    const headers = generateHeaders({
      clientIp: CLIENT_IP,
      sessionId: "session-2",
      apiKey: "test-api-key",
      transport: "stdio",
      clientInfo: { ide: "test-ide", version: "1.2.3" },
    });

    expectBaseHeaders(headers);
    expect(headers["mcp-client-ip"]).toMatch(/^[0-9a-f]{32}:[0-9a-f]+$/);
    expect(decryptClientIp(headers["mcp-client-ip"], EXPLICIT_TEST_KEY)).toBe(
      CLIENT_IP,
    );
    expect(() =>
      decryptClientIp(headers["mcp-client-ip"], PUBLIC_DEFAULT_KEY),
    ).toThrow();
    expect(headers["mcp-session-id"]).toBe("session-2");
    expect(headers["Authorization"]).toBe("Bearer test-api-key");
    expect(headers["X-Context7-Transport"]).toBe("stdio");
    expect(headers["X-Context7-Client-IDE"]).toBe("test-ide");
    expect(headers["X-Context7-Client-Version"]).toBe("1.2.3");
    expect(diagnostic).not.toHaveBeenCalled();
  });

  test("omits metadata for an explicitly malformed key", async () => {
    const invalidKey = "not-a-valid-key";
    const diagnostic = vi.spyOn(console, "error").mockImplementation(() => {});
    const generateHeaders = await loadGenerateHeaders(invalidKey);
    const headers = generateHeaders({ clientIp: CLIENT_IP, transport: "http" });

    expectBaseHeaders(headers);
    expect(headers).not.toHaveProperty("mcp-client-ip");
    expect(headers["X-Context7-Transport"]).toBe("http");
    expect(diagnostic).toHaveBeenCalledWith(INVALID_KEY_MESSAGE);
    const retained = diagnostic.mock.calls.flat().join(" ");
    expect(retained).not.toContain(CLIENT_IP);
    expect(retained).not.toContain(invalidKey);
  });

  test("omits metadata after a runtime cipher failure", async () => {
    const failureText = `failure for ${CLIENT_IP} using ${EXPLICIT_TEST_KEY}`;
    vi.doMock("crypto", async () => {
      const actual = await vi.importActual<CryptoModule>("crypto");
      return {
        ...actual,
        randomBytes: vi.fn(() => {
          throw new Error(failureText);
        }),
      };
    });
    const diagnostic = vi.spyOn(console, "error").mockImplementation(() => {});
    const generateHeaders = await loadGenerateHeaders(EXPLICIT_TEST_KEY);
    const headers = generateHeaders({
      clientIp: CLIENT_IP,
      sessionId: "session-3",
      transport: "http",
    });

    expectBaseHeaders(headers);
    expect(headers).not.toHaveProperty("mcp-client-ip");
    expect(headers["mcp-session-id"]).toBe("session-3");
    expect(diagnostic).toHaveBeenCalledWith(CIPHER_FAILURE_MESSAGE);
    const retained = diagnostic.mock.calls.flat().join(" ");
    expect(retained).not.toContain(CLIENT_IP);
    expect(retained).not.toContain(EXPLICIT_TEST_KEY);
    expect(retained).not.toContain(failureText);
  });

  test("does not require an encryption key when no client IP is present", async () => {
    const diagnostic = vi.spyOn(console, "error").mockImplementation(() => {});
    const generateHeaders = await loadGenerateHeaders(undefined);
    const headers = generateHeaders({
      sessionId: "session-4",
      apiKey: "test-api-key",
      transport: "stdio",
    });

    expectBaseHeaders(headers);
    expect(headers).not.toHaveProperty("mcp-client-ip");
    expect(headers["mcp-session-id"]).toBe("session-4");
    expect(headers["Authorization"]).toBe("Bearer test-api-key");
    expect(headers["X-Context7-Transport"]).toBe("stdio");
    expect(diagnostic).not.toHaveBeenCalled();
  });
});
