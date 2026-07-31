import assert from 'node:assert/strict';
import test from 'node:test';

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((resolvePromise, rejectPromise) => {
    resolve = resolvePromise;
    reject = rejectPromise;
  });
  return { promise, resolve, reject };
}

class FakeGeneration {
  closeCount = 0;
  closed = false;

  constructor(id) {
    this.id = id;
  }

  async close() {
    this.closeCount++;
    assert.equal(this.closeCount, 1, `generation ${this.id} closed twice`);
    this.closed = true;
  }
}

class GenerationEntry {
  leases = 0;
  retired = false;
  closePromise = undefined;
  drained = deferred();

  constructor(generation) {
    this.generation = generation;
  }
}

class CapabilityGenerationManager {
  #current;
  #entries = new Map();
  #requestEpoch = 0;
  #pending = new Set();
  #shutdown = false;
  #shutdownPromise;

  constructor(initialGeneration) {
    const initial = new GenerationEntry(initialGeneration);
    this.#entries.set(initialGeneration, initial);
    this.#current = initial;
  }

  currentId() {
    return this.#current.generation.id;
  }

  acquire() {
    if (this.#shutdown)
      throw new Error('Capability generation manager is shut down');

    const entry = this.#current;
    entry.leases++;
    let released = false;
    return {
      id: entry.generation.id,
      generation: entry.generation,
      release: async () => {
        if (released)
          return;
        released = true;
        entry.leases--;
        assert.ok(entry.leases >= 0);
        await this.#maybeClose(entry);
      },
    };
  }

  replace(builder) {
    if (this.#shutdown)
      return Promise.reject(new Error('Capability generation manager is shut down'));

    const requestEpoch = ++this.#requestEpoch;
    const task = this.#performReplace(requestEpoch, builder);
    this.#pending.add(task);
    return task.finally(() => this.#pending.delete(task));
  }

  async #performReplace(requestEpoch, builder) {
    let candidate;
    try {
      candidate = await builder();
    } catch (error) {
      return {
        applied: false,
        reason:
          this.#shutdown || requestEpoch !== this.#requestEpoch
            ? 'stale-build-failed'
            : 'build-failed',
        error,
      };
    }

    if (this.#shutdown || requestEpoch !== this.#requestEpoch) {
      await candidate.close();
      return {
        applied: false,
        reason: this.#shutdown ? 'shutdown' : 'stale',
      };
    }

    const candidateEntry = new GenerationEntry(candidate);
    this.#entries.set(candidate, candidateEntry);
    const previous = this.#current;
    this.#current = candidateEntry;
    previous.retired = true;
    await this.#maybeClose(previous);
    return { applied: true, generation: candidate };
  }

  async #maybeClose(entry) {
    if (!entry.retired || entry.leases !== 0)
      return;
    if (!entry.closePromise) {
      entry.closePromise = entry.generation.close().finally(() => {
        this.#entries.delete(entry.generation);
        entry.drained.resolve();
      });
    }
    await entry.closePromise;
  }

  shutdown() {
    if (this.#shutdownPromise)
      return this.#shutdownPromise;

    this.#shutdown = true;
    this.#requestEpoch++;
    this.#current.retired = true;
    const currentClose = this.#maybeClose(this.#current);
    this.#shutdownPromise = (async () => {
      await currentClose;
      await Promise.all([...this.#pending]);
      await Promise.all([...this.#entries.values()].map(entry => entry.drained.promise));
    })();
    return this.#shutdownPromise;
  }
}

test('a current-generation lease survives replacement and delays descriptor closure', async () => {
  const initial = new FakeGeneration('A');
  const next = new FakeGeneration('B');
  const manager = new CapabilityGenerationManager(initial);

  const oldLease = manager.acquire();
  const result = await manager.replace(async () => next);
  assert.equal(result.applied, true);
  assert.equal(manager.currentId(), 'B');
  assert.equal(initial.closeCount, 0);

  const newLease = manager.acquire();
  assert.equal(oldLease.id, 'A');
  assert.equal(newLease.id, 'B');

  await oldLease.release();
  await oldLease.release();
  assert.equal(initial.closeCount, 1);

  await newLease.release();
  await manager.shutdown();
  assert.equal(next.closeCount, 1);
});

test('a replacement without active leases closes the old generation immediately', async () => {
  const initial = new FakeGeneration('A');
  const next = new FakeGeneration('B');
  const manager = new CapabilityGenerationManager(initial);

  const result = await manager.replace(async () => next);
  assert.equal(result.applied, true);
  assert.equal(initial.closeCount, 1);
  assert.equal(manager.currentId(), 'B');

  await manager.shutdown();
  assert.equal(next.closeCount, 1);
});

test('a newer replacement request wins even when an older build finishes later', async () => {
  const initial = new FakeGeneration('A');
  const older = new FakeGeneration('B');
  const newer = new FakeGeneration('C');
  const olderBuild = deferred();
  const newerBuild = deferred();
  const manager = new CapabilityGenerationManager(initial);

  const olderRequest = manager.replace(() => olderBuild.promise);
  const newerRequest = manager.replace(() => newerBuild.promise);

  newerBuild.resolve(newer);
  assert.deepEqual(await newerRequest, { applied: true, generation: newer });
  assert.equal(manager.currentId(), 'C');
  assert.equal(initial.closeCount, 1);

  olderBuild.resolve(older);
  assert.deepEqual(await olderRequest, { applied: false, reason: 'stale' });
  assert.equal(older.closeCount, 1);
  assert.equal(manager.currentId(), 'C');

  await manager.shutdown();
  assert.equal(newer.closeCount, 1);
});

test('a failed newest replacement preserves the old current generation and expires older builds', async () => {
  const initial = new FakeGeneration('A');
  const staleCandidate = new FakeGeneration('B');
  const olderBuild = deferred();
  const manager = new CapabilityGenerationManager(initial);

  const olderRequest = manager.replace(() => olderBuild.promise);
  const failure = new Error('new roots could not be opened');
  const newestResult = await manager.replace(async () => {
    throw failure;
  });

  assert.equal(newestResult.applied, false);
  assert.equal(newestResult.reason, 'build-failed');
  assert.equal(newestResult.error, failure);
  assert.equal(manager.currentId(), 'A');
  assert.equal(initial.closeCount, 0);

  olderBuild.resolve(staleCandidate);
  assert.deepEqual(await olderRequest, { applied: false, reason: 'stale' });
  assert.equal(staleCandidate.closeCount, 1);
  assert.equal(manager.currentId(), 'A');

  await manager.shutdown();
  assert.equal(initial.closeCount, 1);
});

test('shutdown rejects new leases, closes pending candidates, and drains current leases once', async () => {
  const initial = new FakeGeneration('A');
  const pendingCandidate = new FakeGeneration('B');
  const pendingBuild = deferred();
  const manager = new CapabilityGenerationManager(initial);
  const lease = manager.acquire();
  const replacement = manager.replace(() => pendingBuild.promise);

  const shutdown = manager.shutdown();
  assert.throws(() => manager.acquire(), /shut down/);
  await assert.rejects(
    manager.replace(async () => new FakeGeneration('C')),
    /shut down/,
  );
  assert.equal(initial.closeCount, 0);

  pendingBuild.resolve(pendingCandidate);
  assert.deepEqual(await replacement, { applied: false, reason: 'shutdown' });
  assert.equal(pendingCandidate.closeCount, 1);

  let shutdownFinished = false;
  void shutdown.then(() => {
    shutdownFinished = true;
  });
  await Promise.resolve();
  assert.equal(shutdownFinished, false);

  await lease.release();
  await lease.release();
  await shutdown;
  await manager.shutdown();
  assert.equal(initial.closeCount, 1);
});
