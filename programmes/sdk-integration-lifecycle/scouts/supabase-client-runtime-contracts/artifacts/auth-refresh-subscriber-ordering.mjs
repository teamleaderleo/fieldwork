// Synthetic mechanism probe derived from supabase-js auth-js control flow at
// 63318987365bbcea2c31a00b62cbb95b21083ad5.
// Preserves: Deferred semantics, refresh single-flight, save-before-notify,
// awaited async subscribers, and single-flight settlement after notification.

const unhandledRejections = [];
process.on('unhandledRejection', (reason) => {
  unhandledRejections.push(reason instanceof Error ? reason.message : String(reason));
});

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

function deferred() {
  let resolve;
  let reject;
  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });
  return { promise, resolve, reject };
}

class RefreshModel {
  constructor() {
    this.refreshingDeferred = null;
    this.listeners = [];
    this.storage = null;
    this.fetchCount = 0;
    this.trace = [];
  }

  onAuthStateChange(callback) {
    this.listeners.push(callback);
  }

  async notify(event, session) {
    this.trace.push(`notify:${event}:begin`);
    const errors = [];
    await Promise.all(
      this.listeners.map(async (listener) => {
        try {
          await listener(event, session);
        } catch (error) {
          errors.push(error);
        }
      })
    );
    this.trace.push(`notify:${event}:end`);
    if (errors.length > 0) throw errors[0];
  }

  async refreshAccessToken() {
    this.fetchCount += 1;
    this.trace.push('service:refresh');
    await Promise.resolve();
    return { access_token: 'A2', refresh_token: 'R2' };
  }

  async callRefreshToken() {
    if (this.refreshingDeferred) {
      this.trace.push('refresh:join-inflight');
      return this.refreshingDeferred.promise;
    }

    this.trace.push('refresh:begin');
    this.refreshingDeferred = deferred();
    try {
      const session = await this.refreshAccessToken();
      this.storage = session;
      this.trace.push('storage:saved');
      await this.notify('TOKEN_REFRESHED', session);
      const result = { data: session, error: null };
      this.refreshingDeferred.resolve(result);
      this.trace.push('refresh:resolved');
      return result;
    } catch (error) {
      this.refreshingDeferred.reject(error);
      this.trace.push(`refresh:rejected:${error.message}`);
      throw error;
    } finally {
      this.refreshingDeferred = null;
      this.trace.push('refresh:end');
    }
  }
}

async function raceWithTimeout(promise, timeoutMs = 100) {
  return Promise.race([
    promise.then(
      (value) => ({ outcome: 'resolved', value }),
      (error) => ({ outcome: 'rejected', error: error.message })
    ),
    sleep(timeoutMs).then(() => ({ outcome: 'timeout' })),
  ]);
}

async function nestedRefreshScenario() {
  const client = new RefreshModel();
  client.onAuthStateChange(async (event) => {
    if (event === 'TOKEN_REFRESHED') {
      client.trace.push('listener:nested-refresh:begin');
      await client.callRefreshToken();
      client.trace.push('listener:nested-refresh:end');
    }
  });
  const outcome = await raceWithTimeout(client.callRefreshToken());
  return {
    scenario: 'nested refresh inside TOKEN_REFRESHED subscriber',
    outcome,
    fetchCount: client.fetchCount,
    persistedRefreshToken: client.storage?.refresh_token ?? null,
    trace: client.trace,
  };
}

async function throwingSubscriberScenario() {
  const client = new RefreshModel();
  client.onAuthStateChange(async (event) => {
    if (event === 'TOKEN_REFRESHED') {
      client.trace.push('listener:throw');
      throw new Error('application subscriber failed');
    }
  });
  const outcome = await raceWithTimeout(client.callRefreshToken());
  await sleep(0); // let the rejected internal Deferred reach unhandledRejection
  return {
    scenario: 'subscriber throws after rotated session is saved',
    outcome,
    fetchCount: client.fetchCount,
    persistedRefreshToken: client.storage?.refresh_token ?? null,
    trace: client.trace,
  };
}

async function readOnlySubscriberControl() {
  const client = new RefreshModel();
  client.onAuthStateChange(async (event, session) => {
    if (event === 'TOKEN_REFRESHED') {
      client.trace.push(`listener:read:${session.refresh_token}`);
    }
  });
  const outcome = await raceWithTimeout(client.callRefreshToken());
  return {
    scenario: 'read-only TOKEN_REFRESHED subscriber control',
    outcome,
    fetchCount: client.fetchCount,
    persistedRefreshToken: client.storage?.refresh_token ?? null,
    trace: client.trace,
  };
}

const scenarios = [
  await nestedRefreshScenario(),
  await throwingSubscriberScenario(),
  await readOnlySubscriberControl(),
];

const result = {
  probe: 'supabase-auth-refresh-subscriber-ordering',
  sourceRevision: 'supabase/supabase-js@63318987365bbcea2c31a00b62cbb95b21083ad5',
  claimScope: 'mechanism',
  modelPreserves: [
    'Deferred implementation semantics',
    'refresh single-flight promise',
    'session save before TOKEN_REFRESHED notification',
    'awaited asynchronous subscribers',
    'single-flight settlement after subscriber completion',
  ],
  modelOmits: [
    'HTTP implementation',
    'JWT contents',
    'storage adapters',
    'BroadcastChannel',
    'auth service database state',
  ],
  scenarios,
  unhandledRejections,
};

console.log(JSON.stringify(result, null, 2));
