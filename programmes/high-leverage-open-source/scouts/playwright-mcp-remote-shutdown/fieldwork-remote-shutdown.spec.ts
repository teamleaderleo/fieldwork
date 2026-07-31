/**
 * Fieldwork controls for issue #404.
 *
 * This file is copied into exact Playwright source and executed through the
 * target repository's MCP fixtures. It uses runner-local networking and a
 * disposable local page only.
 */

import * as http from 'http';
import os from 'os';

import { ChildProcess, spawn } from 'child_process';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { test as baseTest, expect, mcpServerPath, formatLog } from './fixtures';
import { inheritAndCleanEnv } from '../config/utils';

type ExitReceipt = { code: number | null, signal: NodeJS.Signals | null };
type Endpoint = {
  child: ChildProcess;
  loopbackBaseUrl: URL;
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
  throw new Error('No non-loopback IPv4 address is available for the remote shutdown control');
}

function withTimeout<T>(promise: Promise<T>, message: string): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((_, reject) => setTimeout(() => reject(new Error(message)), 15_000)),
  ]);
}

async function request(url: URL, method: string, headers: Record<string, string> = {}): Promise<{ status: number, body: string }> {
  return await new Promise((resolve, reject) => {
    const request = http.request(url, { method, headers }, response => {
      let body = '';
      response.setEncoding('utf8');
      response.on('data', chunk => body += chunk);
      response.on('end', () => resolve({ status: response.statusCode || 0, body }));
    });
    request.on('error', reject);
    request.end();
  });
}

const test = baseTest.extend<{
  shutdownServer: (allowAnyHost: boolean) => Promise<Endpoint>;
}>({
  shutdownServer: async ({ mcpHeadless }, use, testInfo) => {
    let endpoint: Endpoint | undefined;

    await use(async (allowAnyHost: boolean) => {
      if (endpoint)
        throw new Error('Process already running');

      const child = spawn('node', [
        ...mcpServerPath,
        '--port=0',
        '--host=0.0.0.0',
        ...(allowAnyHost ? ['--allowed-hosts=*'] : []),
        '--isolated',
        ...(mcpHeadless ? ['--headless'] : []),
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
      const exitPromise = new Promise<ExitReceipt>(resolve => {
        child.once('exit', (code, signal) => resolve({ code, signal }));
      });
      const presentedUrl = await withTimeout(new Promise<string>((resolve, reject) => {
        child.once('error', reject);
        child.once('exit', (code, signal) => reject(new Error(
            `Playwright MCP exited before readiness: code=${code} signal=${signal}\n${stderr}`
        )));
        child.stderr?.on('data', data => {
          stderr += data.toString();
          const match = stderr.match(/Listening on (http:\/\/.*)/);
          if (match)
            resolve(match[1]);
        });
      }), 'Playwright MCP did not report a listener');

      const loopbackBaseUrl = new URL(presentedUrl);
      const remoteBaseUrl = new URL(presentedUrl);
      remoteBaseUrl.hostname = nonLoopbackIpv4();
      endpoint = {
        child,
        loopbackBaseUrl,
        remoteBaseUrl,
        remoteMcpUrl: new URL('/mcp', remoteBaseUrl),
        stderr: () => stderr,
        waitForExit: () => withTimeout(exitPromise, 'Playwright MCP did not exit after shutdown request'),
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
  const client = new Client({ name: 'fieldwork-remote-shutdown', version: '1.0.0' });
  await client.connect(transport);
  return { client, transport };
}

test('non-loopback accepted shutdown header owns process termination', async ({ shutdownServer, server }) => {
  const endpoint = await shutdownServer(true);
  expect(endpoint.remoteBaseUrl.hostname).toBe(nonLoopbackIpv4());

  const { client } = await connectClient(endpoint.remoteMcpUrl);
  await client.callTool({
    name: 'browser_navigate',
    arguments: { url: server.HELLO_WORLD },
  });

  const shutdownUrl = new URL('/killkillkill', endpoint.remoteBaseUrl);
  const wrongMethod = await request(shutdownUrl, 'GET', { 'x-pw-mcp-kill': '1' });
  expect(wrongMethod.status).toBe(405);
  await client.ping();

  const missingHeader = await request(shutdownUrl, 'POST');
  expect(missingHeader.status).toBe(405);
  await client.ping();

  const wrongHeader = await request(shutdownUrl, 'POST', { 'x-pw-mcp-kill': '0' });
  expect(wrongHeader.status).toBe(405);
  await client.ping();

  const accepted = await request(shutdownUrl, 'POST', { 'x-pw-mcp-kill': '1' });
  expect(accepted).toEqual({ status: 200, body: 'Killing process' });

  const exit = await endpoint.waitForExit();
  expect(exit).toEqual({ code: 0, signal: null });
  const log = formatLog(endpoint.stderr());
  expect(log['create http session']).toBe(1);
  expect(log['create browser (isolated)']).toBe(1);
  expect(log['gracefully closing 1']).toBe(1);
});

test('Host rejection happens before shutdown handling', async ({ shutdownServer }) => {
  const endpoint = await shutdownServer(false);
  const response = await request(
      new URL('/killkillkill', endpoint.remoteBaseUrl),
      'POST',
      { 'x-pw-mcp-kill': '1' },
  );
  expect(response.status).toBe(403);
  expect(response.body).toContain('Access is only allowed at');

  const stillAlive = await request(
      new URL('/killkillkill', endpoint.loopbackBaseUrl),
      'POST',
      { 'x-pw-mcp-kill': '0' },
  );
  expect(stillAlive.status).toBe(405);
  expect(endpoint.child.exitCode).toBeNull();
});

test('loopback accepted shutdown uses the same ordinary route', async ({ shutdownServer }) => {
  const endpoint = await shutdownServer(false);
  const response = await request(
      new URL('/killkillkill', endpoint.loopbackBaseUrl),
      'POST',
      { 'x-pw-mcp-kill': '1' },
  );
  expect(response).toEqual({ status: 200, body: 'Killing process' });
  expect(await endpoint.waitForExit()).toEqual({ code: 0, signal: null });
  expect(formatLog(endpoint.stderr())['gracefully closing 0']).toBe(1);
});
