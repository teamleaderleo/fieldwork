#!/usr/bin/env node
import assert from 'node:assert/strict';

const tick = () => Promise.resolve();
const sleep = milliseconds =>
  new Promise(resolve => setTimeout(resolve, milliseconds));

class Deferred {
  constructor() {
    this.promise = new Promise((resolve, reject) => {
      this.resolve = resolve;
      this.reject = reject;
    });
  }
}

class BindOnceOwner {
  constructor(child, { containDirect = true } = {}) {
    this.child = child;
    this.containDirect = containDirect;
    this.called = false;
    this.invoking = false;
    this.deferred = new Deferred();
  }

  shutdown() {
    if (this.containDirect && this.invoking) {
      return Promise.resolve('direct-contained');
    }
    if (this.called) {
      return this.deferred.promise;
    }

    this.called = true;
    this.invoking = true;
    try {
      Promise.resolve(this.child()).then(
        this.deferred.resolve,
        this.deferred.reject
      );
    } catch (error) {
      this.deferred.reject(error);
    } finally {
      this.invoking = false;
    }
    return this.deferred.promise;
  }
}

async function observe(promise, milliseconds = 25) {
  const pending = Symbol('pending');
  const result = await Promise.race([
    promise.then(
      value => ({ state: 'fulfilled', value }),
      error => ({ state: 'rejected', error: String(error) })
    ),
    sleep(milliseconds).then(() => pending),
  ]);
  return result === pending ? { state: 'pending' } : result;
}

async function directRecursion() {
  let owner;
  let nested;
  owner = new BindOnceOwner(() => {
    nested = owner.shutdown();
    return nested;
  });
  const outer = owner.shutdown();
  return {
    outer: await observe(outer),
    nested: await observe(nested),
    samePromise: outer === nested,
  };
}

async function delayedSelfRecursion() {
  let owner;
  let nested;
  let childResult;
  owner = new BindOnceOwner(async () => {
    await tick();
    nested = owner.shutdown();
    childResult = nested;
    return nested;
  });
  const outer = owner.shutdown();
  await tick();
  return {
    outer: await observe(outer),
    nested: await observe(nested),
    childResultSameAsOuter: childResult === outer,
    nestedSameAsOuter: nested === outer,
  };
}

async function externalJoin() {
  const release = new Deferred();
  const owner = new BindOnceOwner(async () => {
    await tick();
    await release.promise;
    return 'done';
  });
  const first = owner.shutdown();
  await tick();
  const second = owner.shutdown();
  release.resolve();
  return {
    samePromise: first === second,
    first: await observe(first),
    second: await observe(second),
  };
}

async function crossOwner() {
  const secondOwner = new BindOnceOwner(async () => {
    await tick();
    return 'second-owner-done';
  });
  const firstOwner = new BindOnceOwner(async () => {
    await tick();
    await secondOwner.shutdown();
    return 'first-owner-done';
  });
  return {
    first: await observe(firstOwner.shutdown()),
    second: await observe(secondOwner.shutdown()),
  };
}

async function identityCheckFails() {
  let owner;
  let returnedFromChild;
  owner = new BindOnceOwner(() => {
    returnedFromChild = (async () => {
      await tick();
      return owner.shutdown();
    })();
    return returnedFromChild;
  });
  const outer = owner.shutdown();
  await tick();
  return {
    childPromiseSameAsOuter: returnedFromChild === outer,
    outer: await observe(outer),
    child: await observe(returnedFromChild),
  };
}

async function callerDeadlineDoesNotBreakCycle() {
  let owner;
  owner = new BindOnceOwner(async () => {
    await tick();
    return owner.shutdown();
  });
  const outer = owner.shutdown();
  const caller = await Promise.race([
    outer.then(() => 'settled'),
    sleep(5).then(() => 'caller-timeout'),
  ]);
  return { caller, ownerAfterTimeout: await observe(outer) };
}

async function operationWideWatchdog() {
  let owner;
  owner = new BindOnceOwner(async () => {
    await tick();
    return owner.shutdown();
  });

  const originalChild = owner.child;
  owner.child = () =>
    Promise.race([
      originalChild(),
      sleep(5).then(() => {
        throw new Error('operation-timeout');
      }),
    ]);

  const first = owner.shutdown();
  await tick();
  const second = owner.shutdown();
  return {
    samePromise: first === second,
    first: await observe(first),
    second: await observe(second),
  };
}

async function explicitOwnerToken() {
  const lifecycleToken = Symbol('owner-lifecycle');
  class TokenOwner extends BindOnceOwner {
    shutdown(token) {
      if (token === lifecycleToken) {
        return Promise.reject(new Error('same-owner-lifecycle-reentry'));
      }
      return super.shutdown();
    }
  }

  let owner;
  owner = new TokenOwner(async () => {
    await tick();
    return owner.shutdown(lifecycleToken);
  });
  const first = owner.shutdown();
  await tick();
  const external = owner.shutdown();
  return {
    samePromise: first === external,
    first: await observe(first),
    external: await observe(external),
  };
}

async function suppressAllInflightCalls() {
  class SuppressingOwner extends BindOnceOwner {
    shutdown() {
      if (this.called) {
        return Promise.resolve('inflight-suppressed');
      }
      return super.shutdown();
    }
  }

  const release = new Deferred();
  const owner = new SuppressingOwner(async () => {
    await tick();
    await release.promise;
    return 'done';
  });
  const outer = owner.shutdown();
  await tick();
  const external = owner.shutdown();
  release.resolve();
  return {
    outer: await observe(outer),
    external: await observe(external),
    samePromise: outer === external,
  };
}

const results = {
  direct_recursion: await directRecursion(),
  delayed_same_owner_recursion: await delayedSelfRecursion(),
  unrelated_external_join: await externalJoin(),
  cross_owner_nesting: await crossOwner(),
  promise_identity_check: await identityCheckFails(),
  caller_local_deadline: await callerDeadlineDoesNotBreakCycle(),
  operation_wide_watchdog: await operationWideWatchdog(),
  explicit_owner_token: await explicitOwnerToken(),
  suppress_all_inflight_calls: await suppressAllInflightCalls(),
};

assert.equal(results.direct_recursion.outer.state, 'fulfilled');
assert.equal(results.delayed_same_owner_recursion.outer.state, 'pending');
assert.equal(results.unrelated_external_join.samePromise, true);
assert.equal(results.unrelated_external_join.first.state, 'fulfilled');
assert.equal(results.cross_owner_nesting.first.state, 'fulfilled');
assert.equal(results.promise_identity_check.childPromiseSameAsOuter, false);
assert.equal(results.promise_identity_check.outer.state, 'pending');
assert.equal(results.caller_local_deadline.caller, 'caller-timeout');
assert.equal(results.caller_local_deadline.ownerAfterTimeout.state, 'pending');
assert.equal(results.operation_wide_watchdog.samePromise, true);
assert.equal(results.operation_wide_watchdog.first.state, 'rejected');
assert.equal(results.explicit_owner_token.samePromise, true);
assert.equal(results.explicit_owner_token.first.state, 'rejected');
assert.equal(results.suppress_all_inflight_calls.external.state, 'fulfilled');
assert.equal(results.suppress_all_inflight_calls.samePromise, false);

console.log(JSON.stringify(results, null, 2));
