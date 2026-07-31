import { afterEach, describe, expect, test, vi } from "vitest";

const CLIENT_IP = "198.51.100.77";
const VALID_KEY =
  "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f";
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

afterEach(() => {
  delete process.env.CLIENT_IP_ENCRYPTION_KEY;
  vi.doUnmock("crypto");
  vi.restoreAllMocks();
  vi.resetModules();
});

describe.sequential("generateHeaders client IP encryption", () => {
  test("keeps ciphertext and unrelated headers", async () => {
    const generateHeaders = await loadGenerateHeaders(VALID_KEY);
    const headers = generateHeaders({
      clientIp: CLIENT_IP,
      sessionId: "session-1",
      apiKey: "test-api-key",
      transport: "http",
      clientInfo: { ide: "test-ide", version: "1.2.3" },
    });

    expect(headers["mcp-client-ip"]).toMatch(/^[0-9a-f]{32}:[0-9a-f]+$/);
    expect(headers["mcp-client-ip"]).not.toBe(CLIENT_IP);
    expect(headers["mcp-session-id"]).toBe("session-1");
    expect(headers["Authorization"]).toBe("Bearer test-api-key");
    expect(headers["X-Context7-Client-IDE"]).toBe("test-ide");
    expect(headers["X-Context7-Client-Version"]).toBe("1.2.3");
    expect(headers["X-Context7-Transport"]).toBe("http");
  });

  test("omits metadata for an invalid key", async () => {
    const diagnostic = vi.spyOn(console, "error");
    diagnostic.mockImplementation(() => {});
    const invalidKey = ["not", "hex"].join("-");
    const generateHeaders = await loadGenerateHeaders(invalidKey);
    const headers = generateHeaders({
      clientIp: CLIENT_IP,
      sessionId: "session-2",
      transport: "http",
    });

    expect(headers).not.toHaveProperty("mcp-client-ip");
    expect(headers["mcp-session-id"]).toBe("session-2");
    expect(headers["X-Context7-Transport"]).toBe("http");
    expect(diagnostic).toHaveBeenCalledWith(INVALID_KEY_MESSAGE);

    const retainedDiagnostic = diagnostic.mock.calls.flat().join(" ");
    expect(retainedDiagnostic).not.toContain(CLIENT_IP);
    expect(retainedDiagnostic).not.toContain(invalidKey);
  });

  test("omits metadata after cipher failure", async () => {
    const failureText = `sensitive cipher failure for ${CLIENT_IP}`;
    vi.doMock("crypto", async () => {
      const actual = await vi.importActual<CryptoModule>("crypto");
      return {
        ...actual,
        randomBytes: vi.fn(() => {
          throw new Error(failureText);
        }),
      };
    });

    const diagnostic = vi.spyOn(console, "error");
    diagnostic.mockImplementation(() => {});
    const generateHeaders = await loadGenerateHeaders(VALID_KEY);
    const headers = generateHeaders({
      clientIp: CLIENT_IP,
      apiKey: "test-api-key",
      transport: "stdio",
    });

    expect(headers).not.toHaveProperty("mcp-client-ip");
    expect(headers["Authorization"]).toBe("Bearer test-api-key");
    expect(headers["X-Context7-Transport"]).toBe("stdio");
    expect(diagnostic).toHaveBeenCalledWith(CIPHER_FAILURE_MESSAGE);

    const retainedDiagnostic = diagnostic.mock.calls.flat().join(" ");
    expect(retainedDiagnostic).not.toContain(CLIENT_IP);
    expect(retainedDiagnostic).not.toContain(failureText);
  });
});
