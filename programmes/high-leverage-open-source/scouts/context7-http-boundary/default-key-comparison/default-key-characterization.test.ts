import { createDecipheriv } from "crypto";
import { afterEach, describe, expect, test, vi } from "vitest";

const CLIENT_IP = "198.51.100.77";
const PUBLIC_DEFAULT_KEY =
  "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f";

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

afterEach(() => {
  delete process.env.CLIENT_IP_ENCRYPTION_KEY;
  vi.restoreAllMocks();
  vi.resetModules();
});

describe.sequential("public default client-IP encryption key", () => {
  test.each([
    ["absent", undefined],
    ["empty", ""],
  ])("%s configuration is decryptable with the source constant", async (_, key) => {
    const diagnostic = vi.spyOn(console, "error").mockImplementation(() => {});
    const generateHeaders = await loadGenerateHeaders(key);
    const headers = generateHeaders({
      clientIp: CLIENT_IP,
      sessionId: "session-1",
      transport: "http",
    });

    expect(headers["mcp-client-ip"]).toMatch(/^[0-9a-f]{32}:[0-9a-f]+$/);
    expect(decryptClientIp(headers["mcp-client-ip"], PUBLIC_DEFAULT_KEY)).toBe(
      CLIENT_IP,
    );
    expect(headers["mcp-session-id"]).toBe("session-1");
    expect(headers["X-Context7-Transport"]).toBe("http");
    expect(diagnostic).not.toHaveBeenCalled();
  });
});
