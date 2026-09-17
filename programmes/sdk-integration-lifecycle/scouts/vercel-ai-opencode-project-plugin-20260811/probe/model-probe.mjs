import { mkdtemp, mkdir, writeFile, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const SENTINEL_ENV = 'fieldwork-fake-openai-key';
const SENTINEL_CONFIG = 'fieldwork-fake-config-key';
const root = await mkdtemp(path.join(tmpdir(), 'fieldwork-opencode-plugin-'));
const pluginDir = path.join(root, '.opencode', 'plugin');
const output = path.join(root, 'presence.json');

await mkdir(pluginDir, { recursive: true });
await writeFile(
  path.join(pluginDir, 'presence.mjs'),
  `
import { writeFile } from 'node:fs/promises';
export async function server() {
  await writeFile(${JSON.stringify(output)}, JSON.stringify({
    pluginLoaded: true,
    openaiApiKeyPresent: process.env.OPENAI_API_KEY === ${JSON.stringify(SENTINEL_ENV)},
    configContainsSentinel: (process.env.OPENCODE_CONFIG_CONTENT || '').includes(${JSON.stringify(SENTINEL_CONFIG)}),
  }));
  return {};
}
`,
);

async function run(disableProjectConfig) {
  process.env.OPENAI_API_KEY = SENTINEL_ENV;
  process.env.OPENCODE_CONFIG_CONTENT = JSON.stringify({
    provider: { openai: { options: { apiKey: SENTINEL_CONFIG } } },
  });

  if (disableProjectConfig) {
    process.env.OPENCODE_DISABLE_PROJECT_CONFIG = '1';
  } else {
    delete process.env.OPENCODE_DISABLE_PROJECT_CONFIG;
  }

  await rm(output, { force: true });

  // This is deliberately a model of the discovery gate, not an OpenCode run.
  if (!process.env.OPENCODE_DISABLE_PROJECT_CONFIG) {
    const mod = await import(
      pathToFileURL(path.join(pluginDir, 'presence.mjs')).href +
        `?run=${disableProjectConfig}`
    );
    await mod.server();
  }

  try {
    return JSON.parse(await readFile(output, 'utf8'));
  } catch {
    return {
      pluginLoaded: false,
      openaiApiKeyPresent: false,
      configContainsSentinel: false,
    };
  }
}

const baseline = await run(false);
const disabled = await run(true);
console.log(JSON.stringify({ baseline, disabled }, null, 2));

await rm(root, { recursive: true, force: true });
