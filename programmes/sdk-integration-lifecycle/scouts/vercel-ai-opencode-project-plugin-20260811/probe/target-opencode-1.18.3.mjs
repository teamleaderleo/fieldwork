import { mkdtemp, mkdir, readFile, rm, writeFile } from 'node:fs/promises';
import { createRequire } from 'node:module';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const EXPECTED_RUNTIME = '1.18.3';
const ENV_SENTINEL = 'fieldwork-openai-sentinel';
const CONFIG_SENTINEL = 'fieldwork-config-sentinel';

const bridgePackagePath = path.join(process.cwd(), 'package.json');
const bridgePackage = JSON.parse(await readFile(bridgePackagePath, 'utf8'));
const sdkVersion = bridgePackage.dependencies?.['@opencode-ai/sdk'];
const runtimeVersion = bridgePackage.dependencies?.['opencode-ai'];

if (sdkVersion !== EXPECTED_RUNTIME || runtimeVersion !== EXPECTED_RUNTIME) {
  throw new Error(
    `Run from the pinned Vercel bridge directory with @opencode-ai/sdk and opencode-ai ${EXPECTED_RUNTIME}; got sdk=${sdkVersion} runtime=${runtimeVersion}`,
  );
}

const requireFromBridge = createRequire(bridgePackagePath);
const sdkEntry = requireFromBridge.resolve('@opencode-ai/sdk/v2');
const { createOpencodeClient, createOpencodeServer } = await import(
  pathToFileURL(sdkEntry).href
);

function restoreEnv(name, value) {
  if (value === undefined) delete process.env[name];
  else process.env[name] = value;
}

async function readMarker(markerPath) {
  try {
    return JSON.parse(await readFile(markerPath, 'utf8'));
  } catch {
    return {
      pluginLoaded: false,
      openaiApiKeyPresent: false,
      configContainsSentinel: false,
    };
  }
}

async function runCase({ disableProjectConfig }) {
  const root = await mkdtemp(
    path.join(tmpdir(), 'fieldwork-opencode-target-plugin-'),
  );
  const pluginDir = path.join(root, '.opencode', 'plugins');
  const markerPath = path.join(root, 'fieldwork-presence.json');
  await mkdir(pluginDir, { recursive: true });

  await writeFile(
    path.join(pluginDir, 'fieldwork-presence.js'),
    `
import { writeFile } from 'node:fs/promises';

export const FieldworkPresence = async () => {
  await writeFile(${JSON.stringify(markerPath)}, JSON.stringify({
    pluginLoaded: true,
    openaiApiKeyPresent: process.env.OPENAI_API_KEY === ${JSON.stringify(ENV_SENTINEL)},
    configContainsSentinel: (process.env.OPENCODE_CONFIG_CONTENT || '').includes(${JSON.stringify(CONFIG_SENTINEL)}),
  }));
  return {};
};
`,
  );

  const previousOpenAI = process.env.OPENAI_API_KEY;
  const previousDisable = process.env.OPENCODE_DISABLE_PROJECT_CONFIG;
  process.env.OPENAI_API_KEY = ENV_SENTINEL;
  if (disableProjectConfig) {
    process.env.OPENCODE_DISABLE_PROJECT_CONFIG = '1';
  } else {
    delete process.env.OPENCODE_DISABLE_PROJECT_CONFIG;
  }

  let server;
  try {
    server = await createOpencodeServer({
      hostname: '127.0.0.1',
      port: 0,
      timeout: 30_000,
      config: {
        share: 'disabled',
        autoupdate: false,
        provider: {
          openai: {
            options: {
              apiKey: CONFIG_SENTINEL,
            },
          },
        },
      },
    });

    const client = createOpencodeClient({
      baseUrl: server.url,
      directory: root,
    });

    // This is the same first directory-scoped call used by Vercel's
    // harness-opencode ensureRuntime() path. No session or prompt is created.
    const status = await client.mcp.status();
    const marker = await readMarker(markerPath);

    return {
      disableProjectConfig,
      marker,
      mcpStatusReturned: status != null,
      sessionOrPromptCreated: false,
    };
  } finally {
    server?.close();
    restoreEnv('OPENAI_API_KEY', previousOpenAI);
    restoreEnv('OPENCODE_DISABLE_PROJECT_CONFIG', previousDisable);
    await rm(root, { recursive: true, force: true });
  }
}

const baseline = await runCase({ disableProjectConfig: false });
const disabled = await runCase({ disableProjectConfig: true });

const receipt = {
  runtime: EXPECTED_RUNTIME,
  sentinelsOnly: true,
  baseline,
  disabled,
};

console.log(JSON.stringify(receipt, null, 2));

if (
  !baseline.marker.pluginLoaded ||
  !baseline.marker.openaiApiKeyPresent ||
  !baseline.marker.configContainsSentinel
) {
  process.exitCode = 2;
}

if (disabled.marker.pluginLoaded) {
  process.exitCode = 3;
}
