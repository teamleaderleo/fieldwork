function legacyCheckSleepPoll({ timeoutMs, intervalMs, pollMs = 0 }) {
  let elapsed = 0
  if (elapsed > timeoutMs) throw new Error('timeout')
  elapsed += intervalMs
  elapsed += pollMs
  return { outcome: 'success', elapsed }
}

function newerSleepCheckPoll({ timeoutMs, intervalMs, pollMs }) {
  let elapsed = 0
  elapsed += intervalMs
  if (elapsed > timeoutMs) return { outcome: 'timeout', elapsed }
  elapsed += pollMs
  return { outcome: 'success', elapsed }
}

function deadlineOwnedPoll({ timeoutMs, intervalMs, pollMs }) {
  let elapsed = 0
  const sleepMs = Math.min(intervalMs, Math.max(0, timeoutMs - elapsed))
  elapsed += sleepMs
  if (elapsed >= timeoutMs) return { outcome: 'timeout', elapsed }
  elapsed += pollMs
  if (elapsed >= timeoutMs) return { outcome: 'timeout', elapsed }
  return { outcome: 'success', elapsed }
}

const result = {
  legacyIntervalOvershoot: legacyCheckSleepPoll({
    timeoutMs: 5,
    intervalMs: 30,
  }),
  newerRequestOvershoot: newerSleepCheckPoll({
    timeoutMs: 20,
    intervalMs: 5,
    pollMs: 30,
  }),
  deadlineOwnedIntervalCase: deadlineOwnedPoll({
    timeoutMs: 5,
    intervalMs: 30,
    pollMs: 0,
  }),
  deadlineOwnedRequestCase: deadlineOwnedPoll({
    timeoutMs: 20,
    intervalMs: 5,
    pollMs: 30,
  }),
}

console.log(JSON.stringify(result, null, 2))
