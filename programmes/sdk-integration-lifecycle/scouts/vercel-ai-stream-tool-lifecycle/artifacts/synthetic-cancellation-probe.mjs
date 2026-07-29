const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));

async function runScenario(mode) {
  const events = [];
  const controller = new AbortController();
  let sourceCancelled = false;

  const source = new ReadableStream({
    start(streamController) {
      streamController.enqueue({ type: 'tool-call' });
      streamController.enqueue({ type: 'model-call-end' });
    },
    cancel(reason) {
      sourceCancelled = true;
      events.push(`source-cancel:${String(reason)}`);
    },
  });

  const pipeline = source.pipeThrough(
    new TransformStream({
      async transform(chunk, streamController) {
        streamController.enqueue(chunk);
        if (chunk.type !== 'model-call-end') return;

        events.push('tool-start');
        try {
          await new Promise((resolve, reject) => {
            const timer = setTimeout(resolve, 60);
            controller.signal.addEventListener(
              'abort',
              () => {
                clearTimeout(timer);
                reject(controller.signal.reason);
              },
              { once: true },
            );
          });
          events.push('tool-complete');
          try {
            streamController.enqueue({ type: 'tool-result' });
            events.push('result-delivered');
          } catch (error) {
            events.push(`result-delivery-error:${error?.name ?? String(error)}`);
          }
        } catch (error) {
          events.push(`tool-abort:${error?.name ?? String(error)}`);
        }
      },
    }),
  );

  const reader = pipeline.getReader();
  await reader.read(); // tool-call
  const pendingRead = reader.read(); // starts model-call-end transform + tool execution

  while (!events.includes('tool-start')) await sleep(0);

  if (mode === 'reader-cancel') {
    const cancelPromise = reader.cancel('consumer-stopped');
    await sleep(90);
    await cancelPromise;
  } else {
    controller.abort(new DOMException('explicit abort', 'AbortError'));
    await pendingRead.catch(() => undefined);
    await sleep(10);
    await reader.cancel('cleanup').catch(() => undefined);
  }

  return {
    mode,
    events,
    sourceCancelled,
    sharedAbortSignalAborted: controller.signal.aborted,
  };
}

const results = [
  await runScenario('reader-cancel'),
  await runScenario('explicit-abort'),
];

console.log(JSON.stringify(results, null, 2));

const readerCancel = results[0];
const explicitAbort = results[1];

if (!readerCancel.events.includes('tool-complete')) {
  throw new Error('Expected reader cancellation to leave tool-like work running to completion.');
}
if (readerCancel.sharedAbortSignalAborted) {
  throw new Error('Reader cancellation unexpectedly aborted the separate signal.');
}
if (!explicitAbort.events.some(event => event.startsWith('tool-abort:AbortError'))) {
  throw new Error('Expected explicit abort to stop tool-like work.');
}
