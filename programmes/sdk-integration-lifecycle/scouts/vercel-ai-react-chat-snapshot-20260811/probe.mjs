import { performance } from 'node:perf_hooks';

function boundedSnapshot(value) {
  if (value == null || typeof value !== 'object') return value;
  if (Array.isArray(value)) return [...value];

  const copied = { ...value };

  if (Array.isArray(value.parts)) {
    copied.parts = value.parts.map(part =>
      part != null && typeof part === 'object' ? { ...part } : part,
    );
  }

  if (
    value.metadata != null &&
    typeof value.metadata === 'object' &&
    !Array.isArray(value.metadata)
  ) {
    copied.metadata = { ...value.metadata };
  }

  return copied;
}

function outerSnapshot(value) {
  if (value == null || typeof value !== 'object') return value;
  const copied = { ...value };
  if (Array.isArray(value.parts)) copied.parts = [...value.parts];
  return copied;
}

function makeMessage(toolCount = 3) {
  return {
    id: 'assistant-1',
    role: 'assistant',
    metadata: { phase: 'streaming', nested: { counter: 1 } },
    parts: [
      {
        type: 'text',
        text: 'hel',
        state: 'streaming',
        providerMetadata: { provider: { trace: 'a' } },
      },
      ...Array.from({ length: toolCount }, (_, index) => ({
        type: 'tool-demo',
        toolCallId: `tool-${index}`,
        state: 'input-available',
        input: { index },
        output: undefined,
        approval: { id: `approval-${index}` },
      })),
      {
        type: 'data-demo',
        id: 'data-1',
        data: { rows: [{ value: 'old' }] },
      },
    ],
  };
}

function mutateLikeCurrentStream(message) {
  const text = message.parts[0];
  text.text += 'lo';
  text.state = 'done';
  text.providerMetadata = { provider: { trace: 'b' } };

  const tool = message.parts[1];
  tool.state = 'output-available';
  tool.output = { rows: [{ value: 'new-output' }] };
  tool.approval = { ...tool.approval, approved: true };

  const data = message.parts.at(-1);
  data.data = { rows: [{ value: 'new-data' }] };

  message.metadata = {
    ...message.metadata,
    nested: { ...message.metadata.nested, counter: 2 },
  };
}

function checkSnapshot(name, snapshot) {
  const working = makeMessage();
  const before = snapshot(working);
  mutateLikeCurrentStream(working);
  const after = snapshot(working);

  return {
    name,
    priorTextStable: before.parts[0].text === 'hel',
    priorToolStateStable: before.parts[1].state === 'input-available',
    priorToolOutputStable: before.parts[1].output === undefined,
    priorApprovalStable: before.parts[1].approval.approved === undefined,
    priorDataStable: before.parts.at(-1).data.rows[0].value === 'old',
    priorMetadataStable: before.metadata.nested.counter === 1,
    newMessageIdentity: before !== after,
    newPartsArrayIdentity: before.parts !== after.parts,
    everyPartGetsNewIdentity: before.parts.every(
      (part, index) => part !== after.parts[index],
    ),
    newMetadataRootIdentity: before.metadata !== after.metadata,
  };
}

function nestedMutationLimit() {
  const working = makeMessage();
  working.parts[1].output = { rows: [{ value: 'before' }] };
  const before = boundedSnapshot(working);

  // Deliberately outside the sampled current stream contract: mutate inside
  // a retained payload instead of replacing the top-level part.output field.
  working.parts[1].output.rows[0].value = 'after';

  return {
    candidateSharesNestedPayload:
      before.parts[1].output === working.parts[1].output,
    nestedInPlaceMutationLeaksAcrossSnapshot:
      before.parts[1].output.rows[0].value === 'after',
  };
}

function makeBenchmarkMessage(toolCount, rowsPerOutput) {
  return {
    id: 'bench',
    role: 'assistant',
    metadata: { phase: 'streaming' },
    parts: [
      { type: 'text', text: '', state: 'streaming' },
      ...Array.from({ length: toolCount }, (_, index) => ({
        type: 'tool-demo',
        toolCallId: `tool-${index}`,
        state: 'output-available',
        output: {
          index,
          rows: Array.from({ length: rowsPerOutput }, (_, row) => ({
            row,
            text: 'x'.repeat(64),
          })),
        },
      })),
    ],
  };
}

function benchmarkOne(snapshot, toolCount, rowsPerOutput = 100, writes = 30) {
  const working = makeBenchmarkMessage(toolCount, rowsPerOutput);
  const start = performance.now();
  let sink = 0;

  for (let write = 0; write < writes; write++) {
    working.parts[0].text += 'x';
    const snap = snapshot(working);
    sink += snap.parts.length;
  }

  return { ms: performance.now() - start, sink };
}

function median(values) {
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.floor(sorted.length / 2)];
}

function benchmark() {
  const sizes = [10, 25, 50, 100];
  const rounds = 5;
  const rowsPerOutput = 100;
  const writes = 30;

  return sizes.map(toolCount => {
    const deep = [];
    const bounded = [];

    for (let round = 0; round < rounds; round++) {
      deep.push(
        benchmarkOne(structuredClone, toolCount, rowsPerOutput, writes).ms,
      );
      bounded.push(
        benchmarkOne(boundedSnapshot, toolCount, rowsPerOutput, writes).ms,
      );
    }

    const deepMedianMs = median(deep);
    const boundedMedianMs = median(bounded);

    return {
      toolCount,
      rowsPerOutput,
      writes,
      rounds,
      deepMedianMs: Number(deepMedianMs.toFixed(3)),
      boundedMedianMs: Number(boundedMedianMs.toFixed(3)),
      medianSpeedup: Number((deepMedianMs / boundedMedianMs).toFixed(1)),
    };
  });
}

const result = {
  environment: {
    node: process.version,
    platform: `${process.platform}/${process.arch}`,
  },
  correctness: {
    deep: checkSnapshot('structuredClone', structuredClone),
    outerOnlyNegativeControl: checkSnapshot('outer-only', outerSnapshot),
    bounded: checkSnapshot(
      'bounded-message-parts-metadata',
      boundedSnapshot,
    ),
    explicitBoundary: nestedMutationLimit(),
  },
  benchmark: benchmark(),
};

console.log(JSON.stringify(result, null, 2));
