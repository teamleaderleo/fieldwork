/**
 * Fieldwork controls for issue #371.
 *
 * This file is copied into exact Playwright source and executed through the
 * target repository's MCP fixtures. It uses disposable local pages only.
 */

import os from 'os';

import { ChildProcess, spawn } from 'child_process';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { test as baseTest, expect, mcpServerPath, formatLog } from './fixtures';
import { inheritAndCleanEnv } from '../config/utils';

function nonLoopbackIpv4(): string {
  for (const addresses of Object.values(os.networkInterfaces())) {
    for (const address of addresses || []) {
      if (address.family === 'IPv4' && !address.internal)
        return address.address;
    }
  }
  throw new Error('No non-loopback IPv4 address is available for the remote-equivalent control');
}

const test = baseTest.extend<{
  remoteServerEndpoint: (args: string[]) => Promise<{ url: URL, stderr: () => string }>;
}>({
  remoteServerEndpoint: async ({ mcpHeadless }, use, testInfo) => {
    let cp: ChildProcess | undefined;
    const userDataDir = testInfo.outputPath('user-data-dir');

    await use(async (args: string[]) => {
      if (cp)
        throw new Error('Process already running');

      cp = spawn('node', [
        ...mcpServerPath,
        '--port=0',
        '--host=0.0.0.0',
        '--allowed-hosts=*',
        ...(!args.includes('--isolated') ? ['--user-data-dir=' + userDataDir] : []),
        ...(mcpHeadless ? ['--headless'] : []),
        ...args,
      ], {
        stdio: 'pipe',
        env: inheritAndCleanEnv({
          DEBUG: 'pw:mcp:test',
          DEBUG_COLORS: '0',
          DEBUG_HIDE_DATE: '1',
        }),
        cwd: testInfo.outputPath(),
      });

      let stderr = '';
      const presentedUrl = await new Promise<string>((resolve, reject) => {
        const timeout = setTimeout(() => reject(new Error('Playwright MCP did not report a listener')), 15_000);
        cp!.once('exit', code => reject(new Error(`Playwright MCP exited before readiness: ${code}\n${stderr}`)));
        cp!.stderr?.on('data', data => {
          stderr += data.toString();
          const match = stderr.match(/Listening on (http:\/\/.*)/);
          if (match) {
            clearTimeout(timeout);
            resolve(match[1]);
          }
        });
      });

      const url = new URL(presentedUrl);
      url.hostname = nonLoopbackIpv4();
      url.pathname = '/mcp';
      return { url, stderr: () => stderr };
    });

    if (cp && cp.exitCode === null) {
      cp.kill('SIGTERM');
      await new Promise<void>(resolve => cp!.once('exit', () => resolve()));
    }
  },
});

async function connectClient(name: string, url: URL) {
  const transport = new StreamableHTTPClientTransport(url);
  const client = new Client({ name, version: '1.0.0' });
  await client.connect(transport);
  return { client, transport };
}

async function closeClient(client: Client, transport: StreamableHTTPClientTransport) {
  await transport.terminateSession();
  await client.close();
}

test('explicit remote-equivalent transport keeps isolated clients separate', async ({ remoteServerEndpoint, server }) => {
  const { url, stderr } = await remoteServerEndpoint(['--isolated']);
  expect(url.hostname).toBe(nonLoopbackIpv4());

  const first = await connectClient('fieldwork-isolated-1', url);
  const second = await connectClient('fieldwork-isolated-2', url);
  try {
    await first.client.callTool({
      name: 'browser_navigate',
      arguments: { url: server.HELLO_WORLD },
    });

    const secondTabs = await second.client.callTool({
      name: 'browser_tabs',
      arguments: { action: 'list' },
    });
    expect(secondTabs.content[0]?.text).not.toContain(server.HELLO_WORLD);
  } finally {
    await closeClient(first.client, first.transport);
    await closeClient(second.client, second.transport);
  }

  await expect.poll(() => formatLog(stderr())['delete http session']).toBe(2);
  await expect.poll(() => formatLog(stderr())['close browser']).toBe(1);
});

test('explicit remote-equivalent transport shares browser authority only in shared mode', async ({ remoteServerEndpoint, server }) => {
  const { url, stderr } = await remoteServerEndpoint(['--shared-browser-context']);
  expect(url.hostname).toBe(nonLoopbackIpv4());

  const first = await connectClient('fieldwork-shared-1', url);
  const second = await connectClient('fieldwork-shared-2', url);
  try {
    await first.client.callTool({
      name: 'browser_navigate',
      arguments: { url: server.HELLO_WORLD },
    });

    const secondTabs = await second.client.callTool({
      name: 'browser_tabs',
      arguments: { action: 'list' },
    });
    expect(secondTabs.content[0]?.text).toContain(server.HELLO_WORLD);

    await closeClient(first.client, first.transport);

    const snapshot = await second.client.callTool({
      name: 'browser_snapshot',
      arguments: {},
    });
    expect(snapshot.isError).not.toBe(true);
  } finally {
    if (first.client.getServerCapabilities())
      await first.client.close().catch(() => {});
    await closeClient(second.client, second.transport);
  }

  await expect.poll(() => formatLog(stderr())['create http session']).toBe(2);
  await expect.poll(() => formatLog(stderr())['delete http session']).toBe(2);
  await expect.poll(() => formatLog(stderr())['close browser']).toBe(1);
});
