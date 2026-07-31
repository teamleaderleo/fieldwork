import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { mkdir, writeFile } from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const exactTarget = "594a73133e14631af8c915a1b4f2c8039c964fe1";
const selectedIp = "198.51.100.77";
const socketIp = "203.0.113.9";
const packageRoot = process.cwd();
const fieldworkHead = process.env.FIELDWORK_HEAD;
const outputPath = process.env.FIELDWORK_CONTEXT7_COMPOSED_RECEIPT;

assert.match(fieldworkHead ?? "", /^[0-9a-f]{40}$/, "FIELDWORK_HEAD must be a full Git SHA");
assert.ok(outputPath, "FIELDWORK_CONTEXT7_COMPOSED_RECEIPT is required");

const clientIpUrl = pathToFileURL(path.join(packageRoot, "dist", "lib", "client-ip.js")).href;
const encryptionUrl = pathToFileURL(path.join(packageRoot, "dist", "lib", "encryption.js")).href;

function execute(key) {
  const program = `
    const { getClientIp } = await import(${JSON.stringify(clientIpUrl)});
    const { generateHeaders } = await import(${JSON.stringify(encryptionUrl)});
    const selected = getClientIp({
      headers: { "x-forwarded-for": ${JSON.stringify(selectedIp)} },
      socket: { remoteAddress: ${JSON.stringify(socketIp)} },
    });
    process.stdout.write(JSON.stringify({
      selected,
      metadata: generateHeaders({ clientIp: selected, transport: "http" })["mcp-client-ip"],
    }));
  `;
  const env = { ...process.env };
  if (key === undefined) delete env.CLIENT_IP_ENCRYPTION_KEY;
  else env.CLIENT_IP_ENCRYPTION_KEY = key;

  const result = spawnSync(process.execPath, ["--input-type=module", "--eval", program], {
    cwd: packageRoot,
    env,
    encoding: "utf8",
  });
  assert.equal(result.status, 0, result.stderr);
  return { value: JSON.parse(result.stdout), stderr: result.stderr };
}

const repositoryDefault = execute(undefined);
assert.equal(repositoryDefault.value.selected, selectedIp);
assert.notEqual(repositoryDefault.value.metadata, selectedIp);
assert.match(repositoryDefault.value.metadata, /^[0-9a-f]{32}:[0-9a-f]+$/);

const malformedConfiguredKey = ["not", "a", "64", "character", "hex", "key"].join("-");
const malformed = execute(malformedConfiguredKey);
assert.equal(malformed.value.selected, selectedIp);
assert.equal(malformed.value.metadata, selectedIp);
assert.match(malformed.stderr, /Invalid encryption key format/);

const receipt = {
  schemaVersion: 1,
  evidenceClass: "target-executed-local-helper",
  fieldworkHead,
  exactTarget,
  sourcePath: "packages/mcp/src/lib/encryption.ts",
  selectedIp,
  socketIp,
  outcomes: {
    forwardedIdentitySelected: true,
    repositoryDefaultKeyProducesCiphertextShapedMetadata: true,
    malformedConfiguredKeyEmitsPlaintextSelectedIp: true,
    rejectOrOmitPlaintextRepairPresent: false,
  },
  claimClasses: {
    parserToDefaultMetadata: "target-executed-local-helper",
    parserToMalformedConfigFallback: "target-executed-local-helper",
    hostedContext7ApiReceipt: "not-executed",
  },
  boundaries: {
    mcpSessionCreated: false,
    hostedContext7ApiCalled: false,
    redisOperationCalled: false,
    credentialUsed: false,
  },
};

await mkdir(path.dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(receipt, null, 2)}\n`, "utf8");
console.log(JSON.stringify(receipt));
console.log("FIELDWORK_CONTEXT7_METADATA_FALLBACK_EXACT=3/3");
