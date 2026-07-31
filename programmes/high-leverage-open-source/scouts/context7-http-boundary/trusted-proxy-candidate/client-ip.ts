import type express from "express";
import { BlockList, isIP } from "node:net";

export type ClientIpPolicy = {
  trustedProxies: BlockList;
};

function stripIpv4MappedPrefix(ip: string): string {
  return ip.replace(/^::ffff:/i, "");
}

function normalizeIp(ip: string | undefined): string | undefined {
  if (!ip) return undefined;
  const normalized = stripIpv4MappedPrefix(ip.trim()).toLowerCase();
  return isIP(normalized) ? normalized : undefined;
}

function invalidTrustedProxyConfiguration(): never {
  throw new Error("Invalid CONTEXT7_TRUSTED_PROXY_CIDRS configuration");
}

/**
 * Build an explicit trusted-proxy policy from comma-separated addresses/CIDRs.
 * An empty value trusts no proxy and therefore ignores all forwarded headers.
 */
export function createClientIpPolicy(value: string | undefined): ClientIpPolicy {
  const trustedProxies = new BlockList();
  if (!value?.trim()) return { trustedProxies };

  for (const rawEntry of value.split(",")) {
    const entry = rawEntry.trim();
    if (!entry) invalidTrustedProxyConfiguration();

    const parts = entry.split("/");
    if (parts.length > 2) invalidTrustedProxyConfiguration();

    const address = normalizeIp(parts[0]);
    if (!address) invalidTrustedProxyConfiguration();

    const familyNumber = isIP(address);
    const family = familyNumber === 4 ? "ipv4" : "ipv6";
    if (parts.length === 1) {
      trustedProxies.addAddress(address, family);
      continue;
    }

    if (!/^\d+$/.test(parts[1])) invalidTrustedProxyConfiguration();
    const prefix = Number(parts[1]);
    const maximumPrefix = familyNumber === 4 ? 32 : 128;
    if (prefix < 0 || prefix > maximumPrefix) invalidTrustedProxyConfiguration();
    trustedProxies.addSubnet(address, prefix, family);
  }

  return { trustedProxies };
}

function isTrustedProxy(policy: ClientIpPolicy, ip: string): boolean {
  const family = isIP(ip);
  if (family === 4) return policy.trustedProxies.check(ip, "ipv4");
  if (family === 6) return policy.trustedProxies.check(ip, "ipv6");
  return false;
}

function parseForwardedChain(
  value: string | string[] | undefined
): string[] | undefined {
  if (!value) return undefined;
  if (Array.isArray(value)) {
    if (value.length !== 1) return undefined;
    value = value[0];
  }

  const rawEntries = value.split(",");
  if (!rawEntries.length) return undefined;

  const chain: string[] = [];
  for (const rawEntry of rawEntries) {
    const normalized = normalizeIp(rawEntry);
    if (!normalized) return undefined;
    chain.push(normalized);
  }
  return chain.length ? chain : undefined;
}

/**
 * Returns true for RFC1918, CGNAT, loopback, link-local, and IPv6 private ranges.
 */
export function isPrivateOrLocalIp(ip: string): boolean {
  const plainIp = stripIpv4MappedPrefix(ip).toLowerCase();

  if (plainIp.includes(".")) {
    return (
      plainIp.startsWith("10.") ||
      plainIp.startsWith("192.168.") ||
      /^172\.(1[6-9]|2[0-9]|3[0-1])\./.test(plainIp) ||
      /^100\.(6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\./.test(plainIp) ||
      plainIp.startsWith("127.") ||
      plainIp.startsWith("169.254.")
    );
  }

  if (/^[0:]+1$/.test(plainIp)) {
    return true;
  }

  if (/^fe[89ab][0-9a-f]:/.test(plainIp)) {
    return true;
  }

  if (/^f[cd][0-9a-f]{2}:/.test(plainIp)) {
    return true;
  }

  return false;
}

/**
 * Resolve the client address from one immutable request.
 *
 * Forwarding is ignored unless the direct socket belongs to an explicitly
 * configured trusted proxy. A trusted chain is walked from the socket side
 * toward the client, skipping trusted proxy hops and returning the first
 * untrusted address. Any malformed or duplicate forwarding input fails closed
 * to the direct socket address.
 */
export function getClientIp(
  req: express.Request,
  policy: ClientIpPolicy = createClientIpPolicy(undefined)
): string | undefined {
  const socketIp = normalizeIp(req.socket?.remoteAddress);
  if (!socketIp) return undefined;
  if (!isTrustedProxy(policy, socketIp)) return socketIp;

  const forwardedFor =
    req.headers["x-forwarded-for"] || req.headers["X-Forwarded-For"];
  const chain = parseForwardedChain(forwardedFor);
  if (!chain) return socketIp;

  for (let index = chain.length - 1; index >= 0; index--) {
    const candidate = chain[index];
    if (!isTrustedProxy(policy, candidate)) return candidate;
  }

  return socketIp;
}
