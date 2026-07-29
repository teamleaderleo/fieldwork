#!/usr/bin/env node
import assert from 'node:assert/strict';

async function probeAbortDuringPreparation() {
  let spawned = false;
  let releasePreparation;
  const preparation = new Promise((resolve) => {
    releasePreparation = resolve;
  });
  const controller = new AbortController();

  const currentFlow = (async () => {
    await preparation;
    // Current discovered-tool execution does not re-check the signal before spawn.
    spawned = true;
  })();

  controller.abort();
  releasePreparation();
  await currentFlow;
  assert.equal(controller.signal.aborted, true);
  assert.equal(spawned, true);

  return {
    abortedDuringPreparation: true,
    spawnedAfterAbort: spawned,
    consequence:
      'a repair that only checks before asynchronous sandbox preparation still permits post-abort spawn',
  };
}

function probeParallelWaitingBoolean() {
  let waiting = false;
  let pending = 0;
  const transitions = [];
  const setWaiting = (value) => {
    waiting = value;
    transitions.push(value);
  };

  pending += 1;
  setWaiting(true);
  pending += 1;
  setWaiting(true);

  pending -= 1;
  setWaiting(false);

  assert.equal(pending, 1);
  assert.equal(waiting, false);

  return {
    transitions,
    pendingApprovalsAfterFirstResolution: pending,
    reportedWaiting: waiting,
    consequence:
      'try/finally balances each call but a shared boolean can report idle while another approval remains pending',
  };
}

function probeLateExitAfterSyntheticAbort() {
  const active = new Map([[4323, { state: 'running' }]]);
  let retainedResult;

  retainedResult = { aborted: true, exitCode: 130, signal: null };
  active.delete(4323);

  const realExit = { aborted: false, exitCode: null, signal: 15 };
  if (active.has(4323)) {
    retainedResult = realExit;
  }

  assert.deepEqual(retainedResult, {
    aborted: true,
    exitCode: 130,
    signal: null,
  });

  return {
    syntheticResult: retainedResult,
    laterRealExit: realExit,
    laterExitRetained: false,
    consequence:
      'immediate lifecycle settlement prevents later OS exit details from replacing the synthetic cancellation result',
  };
}

async function probeDetachedMcpCompletion() {
  let sideEffectCompleted = false;
  let releaseRemote;
  const remote = new Promise((resolve) => {
    releaseRemote = () => {
      sideEffectCompleted = true;
      resolve(['remote-result']);
    };
  });

  const controller = new AbortController();
  const local = new Promise((resolve, reject) => {
    const onAbort = () => {
      const error = new Error('Tool call aborted');
      error.name = 'AbortError';
      reject(error);
    };
    controller.signal.addEventListener('abort', onAbort, { once: true });
    remote.then(resolve, reject);
  });

  controller.abort();
  await assert.rejects(local, { name: 'AbortError' });
  assert.equal(sideEffectCompleted, false);

  releaseRemote();
  await remote;
  assert.equal(sideEffectCompleted, true);

  return {
    localRejectedOnAbort: true,
    remoteCompletedLater: sideEffectCompleted,
    consequence:
      'local promise cancellation does not establish cancellation of remote MCP work',
  };
}

function probeUnboundedDiscoveredOutput() {
  let stdout = '';
  const chunk = 'x'.repeat(1024);
  const chunks = 4096;
  for (let index = 0; index < chunks; index += 1) {
    stdout += chunk;
  }
  assert.equal(stdout.length, 4 * 1024 * 1024);

  return {
    simulatedChunks: chunks,
    retainedBytes: stdout.length,
    configuredExecutionLimitObserved: false,
    consequence:
      'project-discovered execution retains all output in memory until close; a threshold and truncation contract remain undefined',
  };
}

const result = {
  probe: 'Gemini CLI expanded deterministic lifecycle exploration',
  targetRevision: '3499c84f7b8e70c86600e7cd2c67a7c65a667f5e',
  generatedAt: '2026-07-30',
  cases: {
    abortDuringPreparation: await probeAbortDuringPreparation(),
    parallelWaitingBoolean: probeParallelWaitingBoolean(),
    lateExitAfterSyntheticAbort: probeLateExitAfterSyntheticAbort(),
    detachedMcpCompletion: await probeDetachedMcpCompletion(),
    unboundedDiscoveredOutput: probeUnboundedDiscoveredOutput(),
  },
};

process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
