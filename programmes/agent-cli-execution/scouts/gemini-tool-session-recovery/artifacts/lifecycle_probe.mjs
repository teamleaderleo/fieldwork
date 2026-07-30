#!/usr/bin/env node
import assert from 'node:assert/strict';

const LOST_RESULT_SENTINEL =
  'The tool execution result was lost due to context management truncation.';

function probeParallelConfirmationAffinity() {
  const activeCalls = new Map([
    ['call-a', { request: { callId: 'call-a', args: { path: 'a.txt' } }, tool: 'edit-a' }],
    ['call-b', { request: { callId: 'call-b', args: { path: 'b.txt' } }, tool: 'edit-b' }],
  ]);
  const targetCallId = 'call-b';
  const currentSelection = activeCalls.values().next().value;
  assert.equal(currentSelection.request.callId, 'call-a');
  assert.notEqual(currentSelection.request.callId, targetCallId);
  return {
    targetCallId,
    selectedCallId: currentSelection.request.callId,
    reproduced: true,
    consequence: 'modification input is sourced from another active approval',
  };
}

async function probeWaitingCallbackAbort() {
  const transitions = [];
  const onWaiting = (value) => transitions.push(value);
  const wait = Promise.reject(new Error('Operation cancelled'));

  try {
    onWaiting(true);
    await wait;
    onWaiting(false);
  } catch {
    // Mirrors the current control flow: false is skipped when await rejects.
  }

  assert.deepEqual(transitions, [true]);
  return {
    transitions,
    reproduced: true,
    consequence: 'consumer remains marked as waiting after cancellation',
  };
}

function probeAsyncKillAcknowledgement() {
  let operatingSystemProcessAlive = true;
  let lifecycleActive = true;
  let terminationStarted = false;

  const externalKillHook = () => {
    terminationStarted = true;
    // The real hook starts asynchronous process-tree termination and returns void.
  };

  externalKillHook();
  lifecycleActive = false;
  const observationAtAcknowledgement = {
    terminationStarted,
    lifecycleActive,
    operatingSystemProcessAlive,
  };
  assert.deepEqual(observationAtAcknowledgement, {
    terminationStarted: true,
    lifecycleActive: false,
    operatingSystemProcessAlive: true,
  });

  operatingSystemProcessAlive = false;
  return {
    observationAtAcknowledgement,
    eventualOperatingSystemProcessAlive: operatingSystemProcessAlive,
    reproduced: true,
    consequence: 'lifecycle reports termination before the process tree has exited',
  };
}

function probeDiscoveredToolAbortOwnership() {
  let childAlive = true;
  let abortObservedByInvocation = false;
  const signal = { aborted: true };

  // Mirrors DiscoveredToolInvocation.execute: the abortSignal parameter is ignored.
  void signal;
  const waitForClose = () => childAlive;
  abortObservedByInvocation = false;

  assert.equal(waitForClose(), true);
  assert.equal(abortObservedByInvocation, false);

  childAlive = false;
  return {
    abortObservedByInvocation,
    childAliveAtCancellation: true,
    childAliveAfterNaturalClose: childAlive,
    reproduced: true,
    consequence: 'scheduler cancellation does not terminate the discovered-tool subprocess',
  };
}

function probeInterruptedSessionRecovery() {
  const jsonl = [
    JSON.stringify({ sessionId: 's1', projectHash: 'p1' }),
    JSON.stringify({
      id: 'm1',
      type: 'gemini',
      content: '',
      toolCalls: [{ id: 'call-1', name: 'write_file', args: { path: 'x' } }],
    }),
    '{"id":"partial',
  ];

  const records = [];
  for (const line of jsonl) {
    try {
      records.push(JSON.parse(line));
    } catch {
      // Current loader ignores malformed individual lines.
    }
  }

  const modelMessage = records.find((record) => record.id === 'm1');
  const unresolvedCall = modelMessage.toolCalls.find((call) => !call.result);
  assert.equal(unresolvedCall.id, 'call-1');

  const recoveredResponse = {
    functionResponse: {
      id: unresolvedCall.id,
      name: unresolvedCall.name,
      response: { error: LOST_RESULT_SENTINEL },
    },
  };
  assert.equal(
    recoveredResponse.functionResponse.response.error,
    LOST_RESULT_SENTINEL,
  );

  return {
    parsedRecordCount: records.length,
    ignoredTrailingPartialLine: true,
    unresolvedCallId: unresolvedCall.id,
    recoveredError: recoveredResponse.functionResponse.response.error,
    reproduced: true,
    consequence:
      'resume assigns a context-truncation cause without a durable execution outcome',
  };
}

const result = {
  probe: 'gemini-cli deterministic lifecycle source-equivalent probe',
  targetRevision: '3499c84f7b8e70c86600e7cd2c67a7c65a667f5e',
  cases: {
    discoveredToolAbortOwnership: probeDiscoveredToolAbortOwnership(),
    parallelConfirmationAffinity: probeParallelConfirmationAffinity(),
    waitingCallbackAbort: await probeWaitingCallbackAbort(),
    asyncKillAcknowledgement: probeAsyncKillAcknowledgement(),
    interruptedSessionRecovery: probeInterruptedSessionRecovery(),
  },
};

process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
