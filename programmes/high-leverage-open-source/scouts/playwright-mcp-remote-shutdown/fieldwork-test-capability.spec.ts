/** Fieldwork reversing controls for Playwright MCP shutdown candidate B. */

import os from 'os';

import { ChildProcess, spawn } from 'child_process';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { test as baseTest, expect, mcpServerPath, formatLog } from './fixtures';
import { inheritAndCleanEnv } from '../config/utils';

type ExitReceipt = { code: number | null, signal: NodeJS.Signals | null };
type Endpoint = {
  child: ChildProcess;
  remoteBaseUrl: URL;
  remoteMcpUrl: URL;
  stderr: () => string;
  waitForExit: () => Promise<ExitReceipt>;
};

function nonLoopbackIpv4(): string {
  for (const addresses of Object.values(os.networkInterfaces())) {
    for (const address of addresses || []) {
      if (address.family === 'IPv4' && !address.internal)
        return address.address;
    }
  }
  throw new Error('No non-loopback IPv4 address is available');
}

function withTimeout<T>(promise: Promise<T>, message: string): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) => setTimeout(() => reject(new Error(message)), 15_000)),
  ]);
}

const test = baseTest.extend<{
  shutdownServer: (enabled: boolean) => Promise<Endpoint>;
}>({
  shutdownServer: async ({ mcpHeadless }, use, testInfo) => {
    let endpoint: Endpoint | undefined;
    await use(async (enabled: boolean) => {
      if (endpoint)
        throw new Error('Process already running');
      const child = spawn('node', [
        ...mcpServerPath,
        '--port=0',
        '--host=0.0.0.0',
        '--allowed-hosts=*',
        '--isolated',
        ...(mcpHeadless ? ['--headless'] : []),
      ], {
        stdio: 'pipe',
        env: inheritAndCleanEnv({
          DEBUG: 'pw:mcp:test',
          DEBUG_COLORS: '0',
          DEBUG_HIDE_DATE: '1',
          ...(enabled ? { PLAYWRIGHT_MCP_ALLOW_PROCESS_SHUTDOWN: '1' } : {}),
        }),
        cwd: testInfo.outputPath(),
      });
      let stderr = '';
      const exitPromise = new Promise<ExitReceipt>(resolve => child.once('exit', (code, signal) => resolve({ code, signal })));
      const presentedUrl = await withTimeout(new Promise<string>((resolve, reject) => {
        child.once('error', reject);
        child.once('exit', (code, signal) => reject(new Error(`server exited before readiness: ${code}/${signal}\n${stderr}`)));
        child.stderr?.on('data', data => {
          stderr += data.toString();
          const match = stderr.match(/Listening on (http:\/\/.*)/);
          if (match)
            resolve(match[1]);
        });
      }), 'Playwright MCP did not report a listener');
      const remoteBaseUrl = new URL(presentedUrl);
      remoteBaseUrl.hostname = nonLoopbackIpv4();
      endpoint = {
        child,
        remoteBaseUrl,
        remoteMcpUrl: new URL('/mcp', remoteBaseUrl),
        stderr: () => stderr,
        waitForExit: () => withTimeout(exitPromise, 'server did not exit'),
      };
      return endpoint;
    });
    if (endpoint && endpoint.child.exitCode === null && endpoint.child.signalCode === null) {
      endpoint.child.kill('SIGTERM');
      await endpoint.waitForExit();
    }
  },
});

async function connectClient(url: URL) {
  const transport = new StreamableHTTPClientTransport(url);
  const client = new Client({ name: 'fieldwork-test-capability', version: '1.0.0' });
  await client.connect(transport);
  return client;
}

test('ordinary server hides shutdown route even for an accepted remote Host', async ({ shutdownServer, server }) => {
  const endpoint = await shutdownServer(false);
  const client = await connectClient(endpoint.remoteMcpUrl);
  await client.callTool({ name: 'browser_navigate', arguments: { url: server.HELLO_WORLD } });

  const response = await fetch(new URL('/killkillkill', endpoint.remoteBaseUrl), {
    method: 'POST',
    headers: { 'x-pw-mcp-kill': '1' },
  });
  expect(response.status).toBe(404);
  await client.ping();
  expect(endpoint.child.exitCode).toBeNull();
});

test('explicit capability retains method/header controls and graceful shutdown', async ({ shutdownServer }) => {
  const endpoint = await shutdownServer(true);
  const shutdownUrl = new URL('/killkillkill', endpoint.remoteBaseUrl);

  expect((await fetch(shutdownUrl, { method: 'GET', headers: { 'x-pw-mcp-kill': '1' } })).status).toBe(405);
  expect((await fetch(shutdownUrl, { method: 'POST' })).status).toBe(405);
  expect((await fetch(shutdownUrl, { method: 'POST', headers: { 'x-pw-mcp-kill': '0' } })).status).toBe(405);

  const accepted = await fetch(shutdownUrl, { method: 'POST', headers: { 'x-pw-mcp-kill': '1' } });
  expect(accepted.status).toBe(200);
  expect(await accepted.text()).toBe('Killing process');
  expect(await endpoint.waitForExit()).toEqual({ code: 0, signal: null });
  expect(formatLog(endpoint.stderr())['gracefully closing 0']).toBe(1);
});
