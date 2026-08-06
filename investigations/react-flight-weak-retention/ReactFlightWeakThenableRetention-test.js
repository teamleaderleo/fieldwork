/**
 * Focused Fieldwork characterization for React Flight weak-thenable ownership.
 * Injected into React's existing react-server-dom-webpack test directory.
 *
 * @jest-environment ./scripts/jest/ReactDOMServerIntegrationEnvironment
 */

'use strict';

global.AsyncLocalStorage = require('async_hooks').AsyncLocalStorage;

let ReactServerDOMServer;
let webpackMap;

function createNeverSettlingWeakThenable() {
  const listeners = [];
  return {
    status: 'pending_weak',
    listeners,
    then(resolve, reject) {
      listeners.push(resolve, reject);
    },
  };
}

async function drain(stream) {
  const reader = stream.getReader();
  for (;;) {
    const {done} = await reader.read();
    if (done) {
      return;
    }
  }
}

function createUnretainedWeakRef() {
  const value = {kind: 'unretained-control'};
  return new WeakRef(value);
}

async function eventuallyCollected(ref) {
  for (let attempt = 0; attempt < 80; attempt++) {
    global.gc();
    // Add bounded allocation pressure and move to a new task so a value
    // returned by WeakRef.deref() in the previous iteration cannot be kept
    // alive until the end of the same JavaScript job.
    const pressure = new Array(4096);
    for (let i = 0; i < pressure.length; i++) {
      pressure[i] = {attempt, i};
    }
    await new Promise(resolve => setImmediate(resolve));
    if (ref.deref() === undefined) {
      return true;
    }
  }
  return false;
}

async function renderCompletedWeakRequest() {
  const weakThenable = createNeverSettlingWeakThenable();
  const perRequestWebpackMap = Object.assign({}, webpackMap, {
    __fieldworkSentinel: {identity: 'weak-request-map'},
  });
  const mapRef = new WeakRef(perRequestWebpackMap);

  const stream = ReactServerDOMServer.renderToReadableStream(
    {weak: weakThenable},
    perRequestWebpackMap,
  );
  await drain(stream);

  return {weakThenable, mapRef};
}

describe('React Flight weak thenable request retention', () => {
  beforeEach(() => {
    jest.resetModules();
    jest.mock('react', () => require('react/react.react-server'));
    jest.mock('react-server-dom-webpack/server', () =>
      require('react-server-dom-webpack/server.edge'),
    );

    const WebpackMock = require('./utils/WebpackMock');
    webpackMap = WebpackMock.webpackMap;
    ReactServerDOMServer = require('react-server-dom-webpack/server');
  });

  test('listener callbacks retain a completed request until cleared', async () => {
    expect(typeof global.gc).toBe('function');

    const controlRef = createUnretainedWeakRef();
    expect(await eventuallyCollected(controlRef)).toBe(true);

    const {weakThenable, mapRef} = await renderCompletedWeakRequest();
    expect(weakThenable.listeners).toHaveLength(2);

    // Current source expectation: the callbacks close over Request, whose
    // bundlerConfig is this per-request map.
    expect(await eventuallyCollected(mapRef)).toBe(false);

    weakThenable.listeners.length = 0;
    expect(await eventuallyCollected(mapRef)).toBe(true);
  });
});
