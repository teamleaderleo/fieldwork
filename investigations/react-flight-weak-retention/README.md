# React Flight weak-thenable request retention

Tracks Fieldwork issue #652.

## Exact source

- React fork/head: `teamleaderleo/react@11eddecd916843f31d88630e4d6f8ab7f52b3a8c`
- feature commit: `9b5b4d51e5be870d396a9568701259e5eb053668`
- server implementation: `packages/react-server/src/ReactFlightServer.js`
- Edge entrypoint: `packages/react-server-dom-webpack/src/server/ReactFlightDOMServerEdge.js`

## Question

Does a never-settling externally retained `pending_weak` thenable retain an otherwise completed Flight server `Request` through the fulfillment/rejection callbacks registered by `serializeThenable()`?

## Probe

The hosted workflow injects one focused test into the existing `ReactFlightDOMEdge` harness and runs the actual Jest child with `node --expose-gc`.

The test:

1. creates an ordinary unretained object and requires it to become unreachable under the same GC loop;
2. creates a per-request webpack map and tracks it with `WeakRef`;
3. renders a model containing a never-settling `pending_weak` thenable;
4. fully drains and closes the stream;
5. retains only the thenable and its listener callbacks;
6. requires the webpack map to remain reachable;
7. clears the thenable's callback array;
8. requires the webpack map to become unreachable.

The final transition distinguishes callback ownership from unrelated Jest, stream, or module retention.

## Interpretation

- control collects, request remains, request collects after listener clear: confirmed callback-owned request retention;
- control does not collect: GC fixture is inconclusive;
- request collects before listener clear: source inference disproved or callbacks do not retain the request graph as expected;
- request remains after listener clear: another owner exists and must be identified before selecting a correction.

No upstream interaction is authorized or made.
