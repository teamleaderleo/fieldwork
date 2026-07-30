import assert from 'node:assert/strict';

const WATCHDOG_MS = 25;

class OneShotProvider {
  #called = false;
  #invocationActive = false;
  #promise;

  constructor(name, child) {
    this.name = name;
    this.child = child;
  }

  shutdown() {
    if (this.#invocationActive) {
      return Promise.resolve(`${this.name}:direct-reentry-contained`);
    }
    if (this.#called) {
      return this.#promise;
    }

    this.#called = true;
    let resolveOwner;
    let rejectOwner;
    this.#promise = new Promise((resolve, reject) => {
      resolveOwner = resolve;
      rejectOwner = reject;
    });

    this.#invocationActive = true;
    try {
      Promise.resolve(this.child.shutdown()).then(resolveOwner, rejectOwner);
    } catch (error) {
      rejectOwner(error);
    } finally {
      this.#invocationActive = false;
    }

    return this.#promise;
  }

  forceFlush() {
    if (this.#invocationActive) {
      return Promise.resolve(`${this.name}:direct-force-flush-contained`);
    }
    if (this.#called) {
      return this.#promise;
    }
    return Promise.resolve(`${this.name}:force-flush`);
  }
}

async function observe(promise, timeoutMs = WATCHDOG_MS) {
  const timeout = new Promise(resolve => {
    setTimeout(() => resolve({ state: 'watchdog-timeout' }), timeoutMs);
  });
  return Promise.race([
    Promise.resolve(promise).then(
      value => ({ state: 'fulfilled', value }),
      error => ({ state: 'rejected', error: String(error?.message ?? error) })
    ),
    timeout,
  ]);
}

async function directSyncSelfReentry() {
  let provider;
  const child = {
    shutdown() {
      return provider.shutdown();
    },
  };
  provider = new OneShotProvider('direct', child);
  return observe(provider.shutdown());
}

async function delayedSelfReentry() {
  let provider;
  const child = {
    async shutdown() {
      await Promise.resolve();
      return provider.shutdown();
    },
  };
  provider = new OneShotProvider('delayed', child);
  return observe(provider.shutdown());
}

async function delayedForceFlushSelfReentry() {
  let provider;
  const child = {
    async shutdown() {
      await Promise.resolve();
      return provider.forceFlush();
    },
  };
  provider = new OneShotProvider('delayed-force-flush', child);
  return observe(provider.shutdown());
}

async function healthyConcurrentJoin() {
  let release;
  const child = {
    shutdown() {
      return new Promise(resolve => {
        release = resolve;
      });
    },
  };
  const provider = new OneShotProvider('healthy-join', child);
  const owner = provider.shutdown();
  await Promise.resolve();
  const joiner = provider.shutdown();
  const samePromise = owner === joiner;
  release('child-finished');
  const [ownerResult, joinerResult] = await Promise.all([
    observe(owner),
    observe(joiner),
  ]);
  return { samePromise, ownerResult, joinerResult };
}

async function concurrentJoinDuringSelfCycle() {
  let provider;
  const child = {
    async shutdown() {
      await Promise.resolve();
      return provider.shutdown();
    },
  };
  provider = new OneShotProvider('cycle-join', child);
  const owner = provider.shutdown();
  await Promise.resolve();
  const joiner = provider.shutdown();
  const samePromise = owner === joiner;
  const [ownerResult, joinerResult] = await Promise.all([
    observe(owner),
    observe(joiner),
  ]);
  return { samePromise, ownerResult, joinerResult };
}

async function crossOwnerNestedShutdown() {
  const childB = { shutdown: () => Promise.resolve('provider-b-finished') };
  const providerB = new OneShotProvider('provider-b', childB);
  const childA = {
    async shutdown() {
      await Promise.resolve();
      return providerB.shutdown();
    },
  };
  const providerA = new OneShotProvider('provider-a', childA);
  return observe(providerA.shutdown());
}

const results = {
  model: 'one-shot provider with synchronous invocation guard',
  watchdogMs: WATCHDOG_MS,
  cases: {
    directSyncSelfReentry: await directSyncSelfReentry(),
    delayedSelfReentry: await delayedSelfReentry(),
    delayedForceFlushSelfReentry: await delayedForceFlushSelfReentry(),
    healthyConcurrentJoin: await healthyConcurrentJoin(),
    concurrentJoinDuringSelfCycle: await concurrentJoinDuringSelfCycle(),
    crossOwnerNestedShutdown: await crossOwnerNestedShutdown(),
  },
};

assert.equal(results.cases.directSyncSelfReentry.state, 'fulfilled');
assert.equal(results.cases.delayedSelfReentry.state, 'watchdog-timeout');
assert.equal(results.cases.delayedForceFlushSelfReentry.state, 'watchdog-timeout');
assert.equal(results.cases.healthyConcurrentJoin.samePromise, true);
assert.equal(results.cases.healthyConcurrentJoin.ownerResult.state, 'fulfilled');
assert.equal(results.cases.healthyConcurrentJoin.joinerResult.state, 'fulfilled');
assert.equal(results.cases.concurrentJoinDuringSelfCycle.samePromise, true);
assert.equal(
  results.cases.concurrentJoinDuringSelfCycle.ownerResult.state,
  'watchdog-timeout'
);
assert.equal(
  results.cases.concurrentJoinDuringSelfCycle.joinerResult.state,
  'watchdog-timeout'
);
assert.equal(results.cases.crossOwnerNestedShutdown.state, 'fulfilled');

process.stdout.write(`${JSON.stringify(results, null, 2)}\n`);
