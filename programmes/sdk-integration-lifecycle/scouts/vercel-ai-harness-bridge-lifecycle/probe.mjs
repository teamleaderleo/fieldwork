import assert from 'node:assert/strict';

function bridgeAuthAccepted({ configuredToken, envToken, url }) {
  // Mirrors packages/harness/src/bridge/index.ts at the pinned revision.
  const expectedToken = configuredToken ?? envToken ?? '';
  const parsed = new URL(url, 'http://localhost');
  return parsed.searchParams.get('agent_bridge_token') === expectedToken;
}

const auth = {
  missingParam: bridgeAuthAccepted({ url: '/' }),
  emptyParam: bridgeAuthAccepted({ url: '/?agent_bridge_token=' }),
  wrongParam: bridgeAuthAccepted({ url: '/?agent_bridge_token=wrong' }),
  explicitTokenCorrect: bridgeAuthAccepted({
    configuredToken: 'secret',
    url: '/?agent_bridge_token=secret',
  }),
  explicitTokenEmptyParam: bridgeAuthAccepted({
    configuredToken: 'secret',
    url: '/?agent_bridge_token=',
  }),
};

assert.deepEqual(auth, {
  missingParam: false,
  emptyParam: true,
  wrongParam: false,
  explicitTokenCorrect: true,
  explicitTokenEmptyParam: false,
});

const pendingToolResults = new Map();
const turnAbort = new AbortController();

function requestToolResult(toolCallId) {
  return new Promise(resolve => {
    pendingToolResults.set(toolCallId, resolve);
  });
}

async function currentAbortBehavior() {
  const onStart = requestToolResult('tc-1').then(() => 'settled');

  // Mirrors the shared bridge's inbound `abort` branch: abort the signal only.
  turnAbort.abort();

  const outcome = await Promise.race([
    onStart,
    new Promise(resolve => setTimeout(() => resolve('still-pending'), 30)),
  ]);

  return {
    signalAborted: turnAbort.signal.aborted,
    onStartOutcomeAfterAbort: outcome,
    retainedPendingResolver: pendingToolResults.has('tc-1'),
  };
}

const abort = await currentAbortBehavior();

assert.deepEqual(abort, {
  signalAborted: true,
  onStartOutcomeAfterAbort: 'still-pending',
  retainedPendingResolver: true,
});

console.log(JSON.stringify({ auth, abort }, null, 2));
