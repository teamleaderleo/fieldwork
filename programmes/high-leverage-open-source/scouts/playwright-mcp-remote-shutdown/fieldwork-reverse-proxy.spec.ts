/**
 * Copyright (c) Microsoft Corporation.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/** Fieldwork discriminator for shutdown authority through a local proxy. */

import http from 'http';
import os from 'os';

import { ChildProcess, spawn } from 'child_process';
import { StreamableHTTPClientTransport } from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { test as baseTest, expect, mcpServerPath, formatLog } from './fixtures';
import { inheritAndCleanEnv } from '../config/utils';

type Candidate = 'loopback-only' | 'test-capability';
type ExitReceipt = { code: number | null, signal: NodeJS.Signals | null };
type Endpoint = {
  child: ChildProcess;
  loopbackBaseUrl: URL;
  stderr: () => string;
  waitForExit: () => Promise<ExitReceipt>;
};

function candidate(): Candidate {
  const value = process.env.FIELDWORK_CANDIDATE;
  if (value !== 'loopback-only' && value !== 'test-capability')
    throw new Error('FIELDWORK_CANDIDATE must name one exact comparison candidate');
  return value;
}

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

async function listen(server: http.Server): Promise<number> {
  await new Promise<void>((resolve, reject) => {
    server.once('error', reject);
    server.listen(0, '0.0.0.0', () => resolve());
  });
  const address = server.address();
  if (!address || typeof address === 'string')
    throw new Error('Proxy did not expose one TCP listener');
  return address.port;
}

async function closeServer(server: http.Server): Promise<void> {
  await new Promise<void>((resolve, reject) => {
    server.close(error => error ? reject(error) : resolve());
  });
}

function createProxy(upstream: URL): http.Server {
  return http.createServer((request, response) => {
    const upstreamRequest = http.request({
      protocol: upstream.protocol,
      hostname: upstream.hostname,
      port: upstream.port,
      method: request.method,
      path: request.url,
      headers: request.headers,
    }, upstreamResponse => {
      response.writeHead(upstreamResponse.statusCode || 500, upstreamResponse.headers);
      upstreamResponse.pipe(response);
    });
    upstreamRequest.once('error', error => {
      if (!response.headersSent)
        response.writeHead(502, { 'content-type': 'text/plain' });
      response.end(`proxy failure: ${error.name}`);
    });
    request.pipe(upstreamRequest);
  });
}

const test = baseTest.extend<{
  shutdownServer: () => Promise<Endpoint>;
}>({
  shutdownServer: async ({ mcpHeadless }, use, testInfo) => {
    let endpoint: Endpoint | undefined;
    await use(async () => {
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
      endpoint = {
        child,
        loopbackBaseUrl: new URL(presentedUrl),
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

async function connectClient(url: URL): Promise<Client> {
  const transport = new StreamableHTTPClientTransport(url);
  const client = new Client({ name: 'fieldwork-reverse-proxy', version: '1.0.0' });
  await client.connect(transport);
  return client;
}

test('local proxy reveals the candidate shutdown authority boundary', async ({ shutdownServer }) => {
  const selected = candidate();
  const endpoint = await shutdownServer();
  const client = await connectClient(new URL('/mcp', endpoint.loopbackBaseUrl));
  const proxy = createProxy(endpoint.loopbackBaseUrl);
  const proxyPort = await listen(proxy);

  try {
    const response = await fetch(
      new URL(`http://${nonLoopbackIpv4()}:${proxyPort}/killkillkill`),
      {
        method: 'POST',
        headers: { 'x-pw-mcp-kill': '1' },
      },
    );

    if (selected === 'loopback-only') {
      expect(response.status).toBe(200);
      expect(await response.text()).toBe('Killing process');
      expect(await endpoint.waitForExit()).toEqual({ code: 0, signal: null });
      expect(formatLog(endpoint.stderr())['gracefully closing 1']).toBe(1);
    } else {
      expect(response.status).toBe(404);
      expect(await response.text()).toBe('');
      await client.ping();
      expect(endpoint.child.exitCode).toBeNull();
      await client.close();
    }
  } finally {
    await closeServer(proxy);
  }
});
