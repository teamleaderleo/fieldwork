function asAsyncIterableStream(stream) {
  stream[Symbol.asyncIterator] = function () {
    const reader = this.getReader();
    let finished = false;

    async function cleanup(cancelStream) {
      if (finished) return;
      finished = true;
      try {
        if (cancelStream) await reader.cancel?.();
      } finally {
        try {
          reader.releaseLock();
        } catch {}
      }
    }

    return {
      async next() {
        if (finished) return { done: true, value: undefined };
        try {
          const { done, value } = await reader.read();
          if (done) {
            await cleanup(true);
            return { done: true, value: undefined };
          }
          return { done: false, value };
        } catch (error) {
          await cleanup(false);
          throw error;
        }
      },
      async return() {
        await cleanup(true);
        return { done: true, value: undefined };
      },
      async throw(error) {
        await cleanup(true);
        throw error;
      },
    };
  };
  return stream;
}

function createAsyncIterableStream(source) {
  return asAsyncIterableStream(source.pipeThrough(new TransformStream()));
}

const implementations = [
  ['createAsyncIterableStream', createAsyncIterableStream],
  ['asAsyncIterableStream', asAsyncIterableStream],
];

async function runExactReasonCase(name, create) {
  const sourceError = { type: 'source-error' };
  let controller;
  let cancelCalls = 0;
  const source = new ReadableStream({
    start(value) {
      controller = value;
      value.enqueue('chunk1');
    },
    cancel() {
      cancelCalls++;
    },
  });

  const stream = create(source);
  const iterator = stream[Symbol.asyncIterator]();
  const first = await iterator.next();
  const failedRead = iterator.next();
  controller.error(sourceError);

  let observedReason;
  try {
    await failedRead;
  } catch (error) {
    observedReason = error;
  }

  const nextAfterError = await iterator.next();
  const returnAfterError = await iterator.return();
  const reader = stream.getReader();
  let reacquiredReason;
  try {
    await reader.read();
  } catch (error) {
    reacquiredReason = error;
  } finally {
    reader.releaseLock();
  }

  return {
    implementation: name,
    first,
    exactReasonPreserved: observedReason === sourceError,
    unlockedAfterError: stream.locked === false,
    cancelCalls,
    nextAfterError,
    returnAfterError,
    reacquiredReasonPreserved: reacquiredReason === sourceError,
  };
}

async function runConcurrentCase(name, create) {
  const sourceError = new Error('source failed');
  let controller;
  let cancelCalls = 0;
  const source = new ReadableStream({
    start(value) {
      controller = value;
    },
    cancel() {
      cancelCalls++;
    },
  });

  const stream = create(source);
  const iterator = stream[Symbol.asyncIterator]();
  const reads = [iterator.next(), iterator.next()];
  controller.error(sourceError);
  const outcomes = await Promise.allSettled(reads);

  return {
    implementation: name,
    reasonsPreserved: outcomes.every(
      outcome => outcome.status === 'rejected' && outcome.reason === sourceError,
    ),
    statuses: outcomes.map(outcome => outcome.status),
    unlockedAfterError: stream.locked === false,
    cancelCalls,
    nextAfterError: await iterator.next(),
  };
}

const result = {
  node: process.version,
  platform: process.platform,
  exactReasonCases: [],
  concurrentCases: [],
};

for (const [name, create] of implementations) {
  result.exactReasonCases.push(await runExactReasonCase(name, create));
  result.concurrentCases.push(await runConcurrentCase(name, create));
}

console.log(JSON.stringify(result, null, 2));
