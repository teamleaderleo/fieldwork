import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { once } from 'node:events';

import { StreamableHTTPClientTransport } from '@modelcontextprotocol/client';

const reconnectionOptions = {
  initialReconnectionDelay: 1,
  maxReconnectionDelay: 10,
  reconnectionDelayGrowFactor: 2,
  maxRetries: 2,
};

async function waitFor(predicate, description) {
  const deadline = Date.now() + 5000;
  while (Date.now() < deadline) {
    if (predicate()) return;
    await new Promise((resolve) => setTimeout(resolve, 10));
  }
  throw new Error(`Timed out waiting for ${description}`);
}

async function listen(server) {
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  const address = server.address();
  if (!address || typeof address === 'string') throw new Error('Expected TCP address');
  return new URL(`http://127.0.0.1:${address.port}/mcp`);
}

async function closeServer(server) {
  await new Promise((resolve, reject) => server.close((error) => (error ? reject(error) : resolve())));
}

function respondAfterBody(req, callback) {
  req.on('error', () => {});
  req.on('data', () => {});
  req.on('end', callback);
}

async function successfulReopenDropCycles() {
  let getCount = 0;
  const receivedLastEventIds = [];
  const server = createServer((req, res) => {
    if (req.method === 'POST') {
      respondAfterBody(req, () => {
        res.writeHead(200, { 'content-type': 'text/event-stream' });
        res.end('retry: 1\nid: event-0\ndata:\n\n');
      });
      return;
    }
    if (req.method === 'GET') {
      getCount += 1;
      receivedLastEventIds.push(req.headers['last-event-id']);
      res.writeHead(200, { 'content-type': 'text/event-stream' });
      res.end(`retry: 1\nid: event-${getCount}\ndata:\n\n`);
      return;
    }
    res.writeHead(405).end();
  });

  const url = await listen(server);
  const scheduled = [];
  let streamEndCount = 0;
  const errors = [];
  const tokens = [];
  const transport = new StreamableHTTPClientTransport(url, {
    reconnectionOptions,
    reconnectionScheduler(reconnect, delay, attempt) {
      scheduled.push({ reconnect, delay, attempt });
      return () => {};
    },
  });
  transport.onerror = (error) => errors.push(error.message);

  try {
    await transport.start();
    await transport.send(
      { jsonrpc: '2.0', id: 'request-cycles', method: 'tools/call', params: { name: 'slow' } },
      {
        onresumptiontoken: (token) => tokens.push(token),
        onRequestStreamEnd: () => {
          streamEndCount += 1;
        },
      },
    );
    await waitFor(() => scheduled.length >= 1, 'initial reconnect schedule');

    const cycles = reconnectionOptions.maxRetries + 4;
    const attempts = [];
    for (let i = 0; i < cycles; i += 1) {
      const next = scheduled.shift();
      assert(next, `missing reconnect callback for cycle ${i}`);
      attempts.push(next.attempt);
      next.reconnect();
      await waitFor(() => scheduled.length >= 1, `reconnect schedule after cycle ${i}`);
    }

    assert.deepEqual(attempts, Array(cycles).fill(0));
    assert.equal(getCount, cycles);
    assert.deepEqual(receivedLastEventIds, ['event-0', 'event-1', 'event-2', 'event-3', 'event-4', 'event-5']);
    assert.deepEqual(tokens, ['event-0', 'event-1', 'event-2', 'event-3', 'event-4', 'event-5', 'event-6']);
    assert.equal(streamEndCount, 0);
    assert.deepEqual(errors, []);

    return { attempts, getCount, receivedLastEventIds, tokens, streamEndCount, errors };
  } finally {
    await transport.close();
    await closeServer(server);
  }
}

async function failedOpenExhaustion() {
  let postCount = 0;
  let getCount = 0;
  const server = createServer((req, res) => {
    if (req.method === 'POST') {
      let body = '';
      req.on('data', (chunk) => {
        body += String(chunk);
      });
      req.on('end', () => {
        postCount += 1;
        const message = JSON.parse(body);
        if (postCount === 1) {
          res.writeHead(200, { 'content-type': 'text/event-stream' });
          res.end('retry: 1\nid: failed-0\ndata:\n\n');
        } else {
          res.writeHead(200, { 'content-type': 'application/json' });
          res.end(JSON.stringify({ jsonrpc: '2.0', id: message.id, result: { recovered: true } }));
        }
      });
      return;
    }
    if (req.method === 'GET') {
      getCount += 1;
      res.writeHead(503, { 'content-type': 'text/plain' });
      res.end('still unavailable');
      return;
    }
    res.writeHead(405).end();
  });

  const url = await listen(server);
  const scheduled = [];
  const errors = [];
  const messages = [];
  let streamEndCount = 0;
  const transport = new StreamableHTTPClientTransport(url, {
    reconnectionOptions,
    reconnectionScheduler(reconnect, delay, attempt) {
      scheduled.push({ reconnect, delay, attempt });
      return () => {};
    },
  });
  transport.onerror = (error) => errors.push(error.message);
  transport.onmessage = (message) => messages.push(message);

  try {
    await transport.start();
    await transport.send(
      { jsonrpc: '2.0', id: 'request-fails', method: 'tools/call', params: { name: 'slow' } },
      {
        onRequestStreamEnd: () => {
          streamEndCount += 1;
        },
      },
    );
    await waitFor(() => scheduled.length >= 1, 'first failed-open callback');

    const first = scheduled.shift();
    assert.equal(first.attempt, 0);
    first.reconnect();
    await waitFor(() => scheduled.length >= 1, 'second failed-open callback');

    const second = scheduled.shift();
    assert.equal(second.attempt, 1);
    second.reconnect();
    await waitFor(() => streamEndCount === 1, 'failed-open stream end');

    assert.equal(getCount, 2);
    assert(errors.some((message) => message.includes('Maximum reconnection attempts (2) exceeded')));

    await transport.send({ jsonrpc: '2.0', id: 'request-after', method: 'tools/call', params: { name: 'after' } });
    await waitFor(() => messages.length >= 1, 'later independent response');
    assert.deepEqual(messages, [{ jsonrpc: '2.0', id: 'request-after', result: { recovered: true } }]);

    return { getCount, postCount, streamEndCount, errors, messages };
  } finally {
    await transport.close();
    await closeServer(server);
  }
}

async function usefulResumeCompletes() {
  let getCount = 0;
  const server = createServer((req, res) => {
    if (req.method === 'POST') {
      respondAfterBody(req, () => {
        res.writeHead(200, { 'content-type': 'text/event-stream' });
        res.end('retry: 1\nid: result-0\ndata:\n\n');
      });
      return;
    }
    if (req.method === 'GET') {
      getCount += 1;
      res.writeHead(200, { 'content-type': 'text/event-stream' });
      res.end(`id: result-1\ndata: ${JSON.stringify({ jsonrpc: '2.0', id: 'request-result', result: { ok: true } })}\n\n`);
      return;
    }
    res.writeHead(405).end();
  });

  const url = await listen(server);
  const scheduled = [];
  const messages = [];
  let streamEndCount = 0;
  const transport = new StreamableHTTPClientTransport(url, {
    reconnectionOptions,
    reconnectionScheduler(reconnect, delay, attempt) {
      scheduled.push({ reconnect, delay, attempt });
      return () => {};
    },
  });
  transport.onmessage = (message) => messages.push(message);

  try {
    await transport.start();
    await transport.send(
      { jsonrpc: '2.0', id: 'request-result', method: 'tools/call', params: { name: 'slow' } },
      {
        onRequestStreamEnd: () => {
          streamEndCount += 1;
        },
      },
    );
    await waitFor(() => scheduled.length >= 1, 'useful resume callback');
    scheduled.shift().reconnect();
    await waitFor(() => messages.length === 1 && streamEndCount === 1, 'resumed result completion');

    assert.equal(getCount, 1);
    assert.deepEqual(messages, [{ jsonrpc: '2.0', id: 'request-result', result: { ok: true } }]);
    assert.equal(scheduled.length, 0);

    return { getCount, streamEndCount, messages };
  } finally {
    await transport.close();
    await closeServer(server);
  }
}

const output = {
  package: '@modelcontextprotocol/client@2.0.0',
  node: process.version,
  successfulReopenDropCycles: await successfulReopenDropCycles(),
  failedOpenExhaustion: await failedOpenExhaustion(),
  usefulResumeCompletes: await usefulResumeCompletes(),
};

console.log(JSON.stringify(output, null, 2));
