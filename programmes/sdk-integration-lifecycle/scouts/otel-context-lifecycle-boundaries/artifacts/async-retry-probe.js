'use strict';

const assert = require('node:assert/strict');
const { AsyncLocalStorage } = require('node:async_hooks');

const als = new AsyncLocalStorage();
const events = [];
const activeOperation = () => als.getStore()?.operationId ?? 'ROOT';

class RetryingTransportModel {
  constructor(transport, retryDelayMillis = 10) {
    this.transport = transport;
    this.retryDelayMillis = retryDelayMillis;
  }

  retry(data, timeoutMillis, inMillis) {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        this.transport.send(data, timeoutMillis).then(resolve, reject);
      }, inMillis);
    });
  }

  async send(data, timeoutMillis) {
    let attempts = 1;
    const deadline = Date.now() + timeoutMillis;
    let result = await this.transport.send(data, timeoutMillis);

    while (result.status === 'retryable' && attempts > 0) {
      attempts -= 1;
      const remaining = deadline - Date.now();
      if (this.retryDelayMillis > remaining) return result;
      result = await this.retry(data, remaining, this.retryDelayMillis);
    }

    return result;
  }

  shutdown() {
    return this.transport.shutdown();
  }
}

async function main() {
  // A pre-existing consumer resolves outside the operation's async resource.
  let releaseDetached;
  const detached = new Promise(resolve => {
    releaseDetached = resolve;
  });
  const detachedSeen = detached.then(() => activeOperation());

  await als.run({ operationId: 'logical-op-19' }, async () => {
    releaseDetached();
  });

  assert.equal(await detachedSeen, 'ROOT');
  events.push(['pre-existing-consumer', 'ROOT']);

  // Explicit capture repairs the application-owned queue boundary.
  const captured = { operationId: 'logical-op-19' };
  const reboundSeen = await new Promise(resolve => {
    setImmediate(() => als.run(captured, () => resolve(activeOperation())));
  });

  assert.equal(reboundSeen, 'logical-op-19');
  events.push(['explicit-capture', reboundSeen]);

  // A retry scheduled inside an active operation retains that operation.
  // The source-equivalent direct transport model has no retry-timer cancellation
  // in shutdown, so its second send can run after shutdown is called.
  let sends = 0;
  const underlying = {
    async send() {
      sends += 1;
      events.push([`send-${sends}`, activeOperation()]);
      return sends === 1 ? { status: 'retryable' } : { status: 'success' };
    },
    shutdown() {
      events.push(['shutdown', activeOperation()]);
    },
  };

  const retrying = new RetryingTransportModel(underlying);

  await als.run({ operationId: 'logical-op-19' }, async () => {
    const pending = retrying.send(Uint8Array.from([19]), 1000);
    await Promise.resolve();
    retrying.shutdown();
    const result = await pending;
    assert.equal(result.status, 'success');
  });

  assert.deepEqual(events, [
    ['pre-existing-consumer', 'ROOT'],
    ['explicit-capture', 'logical-op-19'],
    ['send-1', 'logical-op-19'],
    ['shutdown', 'logical-op-19'],
    ['send-2', 'logical-op-19'],
  ]);

  console.log(JSON.stringify({ status: 'pass', events }, null, 2));
}

main().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
