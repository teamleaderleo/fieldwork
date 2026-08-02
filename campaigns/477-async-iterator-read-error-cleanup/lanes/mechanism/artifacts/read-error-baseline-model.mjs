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

        const { done, value } = await reader.read();
        if (done) {
          await cleanup(true);
          return { done: true, value: undefined };
        }

        return { done: false, value };
      },
      async return() {
        await cleanup(true);
        return { done: true, value: undefined };
      },
    };
  };
  return stream;
}

function createAsyncIterableStream(source) {
  return asAsyncIterableStream(source.pipeThrough(new TransformStream()));
}

async function observe(name, create) {
  const sourceError = { type: 'source-error' };
  let controller;
  const source = new ReadableStream({
    start(value) {
      controller = value;
      value.enqueue('chunk1');
    },
  });

  const stream = create(source);
  const iterator = stream[Symbol.asyncIterator]();
  await iterator.next();
  const failedRead = iterator.next();
  controller.error(sourceError);

  let observedReason;
  try {
    await failedRead;
  } catch (error) {
    observedReason = error;
  }

  let reacquireResult;
  try {
    stream.getReader();
    reacquireResult = 'acquired';
  } catch (error) {
    reacquireResult = `${error.name}: ${error.message}`;
  }

  let nextAfterError;
  try {
    nextAfterError = await iterator.next();
  } catch (error) {
    nextAfterError = error === sourceError ? 'same-error' : String(error);
  }

  return {
    implementation: name,
    exactReasonPreserved: observedReason === sourceError,
    lockedAfterError: stream.locked,
    reacquireResult,
    nextAfterError,
  };
}

console.log(
  JSON.stringify(
    {
      node: process.version,
      platform: process.platform,
      cases: [
        await observe('createAsyncIterableStream', createAsyncIterableStream),
        await observe('asAsyncIterableStream', asAsyncIterableStream),
      ],
    },
    null,
    2,
  ),
);
