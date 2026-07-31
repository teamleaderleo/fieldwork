#!/usr/bin/env python3
"""Apply the Context7 explicit-key-only client-IP metadata candidate."""

from __future__ import annotations

import argparse
from pathlib import Path


SOURCE = Path("packages/mcp/src/lib/encryption.ts")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one source match, found {count}")
    return text.replace(old, new, 1)


def apply(root: Path) -> None:
    source = root / SOURCE
    text = source.read_text(encoding="utf-8")

    text = replace_once(
        text,
        '''const DEFAULT_ENCRYPTION_KEY = "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f";
const ENCRYPTION_KEY = process.env.CLIENT_IP_ENCRYPTION_KEY || DEFAULT_ENCRYPTION_KEY;
const ALGORITHM = "aes-256-cbc";

function validateEncryptionKey(key: string): boolean {
  // Must be exactly 64 hex characters (32 bytes)
  return /^[0-9a-fA-F]{64}$/.test(key);
}
''',
        '''const ENCRYPTION_KEY = process.env.CLIENT_IP_ENCRYPTION_KEY;
const ALGORITHM = "aes-256-cbc";

function validateEncryptionKey(key: string): boolean {
  // Must be exactly 64 hex characters (32 bytes)
  return /^[0-9a-fA-F]{64}$/.test(key);
}
''',
        "encryption-key constants",
    )

    text = replace_once(
        text,
        '''function encryptClientIp(clientIp: string): string {
  if (!validateEncryptionKey(ENCRYPTION_KEY)) {
    console.error("Invalid encryption key format. Must be 64 hex characters.");
    return clientIp; // Fallback to unencrypted
  }

  try {
    const iv = randomBytes(16);
    const cipher = createCipheriv(ALGORITHM, Buffer.from(ENCRYPTION_KEY, "hex"), iv);
    let encrypted = cipher.update(clientIp, "utf8", "hex");
    encrypted += cipher.final("hex");
    return iv.toString("hex") + ":" + encrypted;
  } catch (error) {
    console.error("Error encrypting client IP:", error);
    return clientIp; // Fallback to unencrypted
  }
}
''',
        '''function encryptClientIp(clientIp: string): string | undefined {
  if (!ENCRYPTION_KEY) {
    console.error(
      "CLIENT_IP_ENCRYPTION_KEY is not configured; omitting mcp-client-ip metadata.",
    );
    return undefined;
  }
  if (!validateEncryptionKey(ENCRYPTION_KEY)) {
    console.error("Invalid encryption key format; omitting mcp-client-ip metadata.");
    return undefined;
  }

  try {
    const iv = randomBytes(16);
    const cipher = createCipheriv(ALGORITHM, Buffer.from(ENCRYPTION_KEY, "hex"), iv);
    let encrypted = cipher.update(clientIp, "utf8", "hex");
    encrypted += cipher.final("hex");
    return iv.toString("hex") + ":" + encrypted;
  } catch {
    console.error("Unable to encrypt client IP; omitting mcp-client-ip metadata.");
    return undefined;
  }
}
''',
        "client-IP encryption implementation",
    )

    text = replace_once(
        text,
        '''  if (context.clientIp) {
    headers["mcp-client-ip"] = encryptClientIp(context.clientIp);
  }
''',
        '''  if (context.clientIp) {
    const encryptedClientIp = encryptClientIp(context.clientIp);
    if (encryptedClientIp) {
      headers["mcp-client-ip"] = encryptedClientIp;
    }
  }
''',
        "client-IP header publication",
    )

    source.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    apply(args.root.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
