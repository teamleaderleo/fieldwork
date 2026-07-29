#!/usr/bin/env node

/**
 * Synthetic MCP transport/session lifecycle probe.
 *
 * This zero-dependency model transcribes the state seams observed at
 * modelcontextprotocol/typescript-sdk@cc4b41617ce3601b1290d67216ea0b194a3cd9ac.
 * It does not import or modify upstream code. Its purpose is to distinguish
 * protocol-owned request state from transport-owned reconnect/session state.
 */

class SyntheticProtocol {
  constructor() {
    this.nextId = 0;
    this.pending = new Map();
    this.progress = new Map();
    this.inbound = new Map();
    this.errors = [];
    this.sessionId = undefined;
  }

  request(onProgress) {
    const id = this.nextId++;
    let resolve;
    let reject;
    const promise = new Promise((res, rej) => {
      resolve = res;
      reject = rej;
    });
    this.pending.set(id, { resolve, reject });
    if (onProgress) this.progress.set(id, onProgress);
    return { id, promise };
  }

  startInbound(id) {
    const controller = new AbortController();
    this.inbound.set(id, controller);
    return controller;
  }

  cancelInbound(id, reason) {
    this.inbound.get(id)?.abort(reason);
  }

  receiveProgress(id, value) {
    const callback = this.progress.get(id);
    if (!callback) {
      this.errors.push(`unknown progress token ${id}`);
      return;
    }
    callback(value);
  }

  receiveResponse(id, value) {
    const pending = this.pending.get(id);
    if (!pending) {
      this.errors.push(`unknown response id ${id}`);
      return;
    }
    this.pending.delete(id);
    this.progress.delete(id);
    pending.resolve(value);
  }

  close() {
    const error = new Error('Connection closed');
    for (const { reject } of this.pending.values()) reject(error);
    this.pending.clear();
    this.progress.clear();
    for (const controller of this.inbound.values()) controller.abort(error);
    this.inbound.clear();
  }
}

class SyntheticReconnectTransport {
  constructor({ maxRetries = 2 } = {}) {
    this.maxRetries = maxRetries;
    this.serverRetryMs = undefined;
    this.cancelReconnection = undefined;
    this.scheduled = [];
  }

  observeRetry(ms) {
    this.serverRetryMs = ms;
  }

  delayFor(attempt) {
    return this.serverRetryMs ?? Math.min(1000 * 1.5 ** attempt, 30_000);
  }

  schedule(stream, attempt = 0) {
    if (attempt >= this.maxRetries) return false;
    const timer = { stream, attempt, delay: this.delayFor(attempt), cancelled: false };
    this.scheduled.push(timer);
    this.cancelReconnection = () => {
      timer.cancelled = true;
    };
    return true;
  }

  close() {
    this.cancelReconnection?.();
  }
}

async function run() {
  const protocol = new SyntheticProtocol();
  const progress = [];
  const outbound = protocol.request(value => progress.push(value));
  const inbound = protocol.startInbound(outbound.id);

  protocol.receiveProgress(outbound.id, 1);
  protocol.cancelInbound(outbound.id, 'caller cancelled');
  protocol.pending.delete(outbound.id);
  protocol.progress.delete(outbound.id);
  protocol.receiveResponse(outbound.id, { ok: true });

  const reconnectProtocol = new SyntheticProtocol();
  reconnectProtocol.sessionId = 'session-2';
  const old = reconnectProtocol.request();
  reconnectProtocol.close();
  await old.promise.catch(() => undefined);
  const oldPromiseRevived = reconnectProtocol.pending.has(old.id);

  const sharedRetry = new SyntheticReconnectTransport();
  sharedRetry.observeRetry(50);
  const streamADelayBeforeStreamB = sharedRetry.delayFor(0);
  sharedRetry.observeRetry(5000);
  const streamADelayAfterStreamB = sharedRetry.delayFor(0);

  const cancelHandle = new SyntheticReconnectTransport();
  cancelHandle.schedule('A', 0);
  cancelHandle.schedule('B', 0);
  cancelHandle.close();

  const resetBudget = new SyntheticReconnectTransport({ maxRetries: 2 });
  const scheduledAttempts = [];
  for (let cycle = 0; cycle < 5; cycle += 1) {
    // A successful reopen creates a fresh stream handler. When that stream
    // closes again, the SDK source schedules the next reconnect at attempt 0.
    resetBudget.schedule(`cycle-${cycle}`, 0);
    scheduledAttempts.push(0);
  }

  const output = {
    sourceModel: 'synthetic transcription of SDK lifecycle seams',
    scenarios: {
      cancelLateResponse: {
        requestId: outbound.id,
        progress,
        handlerAborted: inbound.signal.aborted,
        clientErrors: protocol.errors
      },
      sessionReconnectBoundary: {
        preservedSessionId: reconnectProtocol.sessionId,
        oldRequestId: old.id,
        oldPromiseRevived
      },
      sharedRetryDelay: {
        streamADelayBeforeStreamB,
        streamADelayAfterStreamB,
        coupled: streamADelayBeforeStreamB !== streamADelayAfterStreamB
      },
      singleCancelHandle: {
        scheduled: cancelHandle.scheduled,
        onlyLatestCancelled:
          cancelHandle.scheduled.length === 2 &&
          cancelHandle.scheduled[0].cancelled === false &&
          cancelHandle.scheduled[1].cancelled === true
      },
      retryBudgetReset: {
        maxRetries: resetBudget.maxRetries,
        reconnectCyclesObserved: scheduledAttempts.length,
        scheduledAttempts,
        terminalReached: scheduledAttempts.some(attempt => attempt >= resetBudget.maxRetries)
      }
    }
  };

  process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
}

run().catch(error => {
  console.error(error);
  process.exitCode = 1;
});
