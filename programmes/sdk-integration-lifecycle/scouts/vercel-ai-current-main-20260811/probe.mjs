import assert from 'node:assert/strict';
import { createHmac } from 'node:crypto';

// Model the exact current branch in
// packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.ts.
function convertOpenAICompatibleChatUsage(usage) {
  const promptTokens = usage.prompt_tokens ?? 0;
  const completionTokens = usage.completion_tokens ?? 0;
  const cacheReadTokens = usage.prompt_tokens_details?.cached_tokens ?? 0;
  const reasoningTokens = usage.completion_tokens_details?.reasoning_tokens ?? 0;

  return {
    inputTokens: {
      total: promptTokens,
      noCache: promptTokens - cacheReadTokens,
      cacheRead: cacheReadTokens,
      cacheWrite: undefined,
    },
    outputTokens: {
      total: completionTokens,
      text: Math.max(0, completionTokens - reasoningTokens),
      reasoning: reasoningTokens,
    },
    raw: usage,
  };
}

// Model the current public projection in packages/ai/src/types/usage.ts.
function asLanguageModelUsage(usage) {
  const add = (a, b) =>
    a == null && b == null ? undefined : (a ?? 0) + (b ?? 0);
  return {
    inputTokens: usage.inputTokens.total,
    outputTokens: usage.outputTokens.total,
    outputTokenDetails: {
      textTokens: usage.outputTokens.text,
      reasoningTokens: usage.outputTokens.reasoning,
    },
    totalTokens: add(usage.inputTokens.total, usage.outputTokens.total),
    raw: usage.raw,
  };
}

const incident = {
  prompt_tokens: 951,
  completion_tokens: 6000,
  total_tokens: 6952,
  prompt_tokens_details: { cached_tokens: 60 },
  completion_tokens_details: { reasoning_tokens: 6001 },
};

const internal = convertOpenAICompatibleChatUsage(incident);
const publicUsage = asLanguageModelUsage(internal);
assert.equal(internal.outputTokens.text, 0);
assert.equal(internal.outputTokens.total, 6000);
assert.equal(internal.outputTokens.reasoning, 6001);
assert.equal(publicUsage.totalTokens, 6951);
console.log(
  'usage-invariant:',
  JSON.stringify({
    internal: internal.outputTokens,
    publicTotalTokens: publicUsage.totalTokens,
    rawTotalTokens: incident.total_tokens,
    delta: incident.total_tokens - publicUsage.totalTokens,
  }),
);

// Model the bridge-token contract visible in the current lifecycle schema and
// attach branch: deterministic derivation exists, while live attach consumes
// the token materialized in bridge coordinates.
const secret = 'fieldwork-example-secret';
const sandboxId = 'sandbox-123';
const derivedToken = createHmac('sha256', secret)
  .update(sandboxId)
  .digest('hex');
const persistedBridgeState = {
  port: 4319,
  token: derivedToken,
  lastSeenEventId: 7,
};
const redacted = { ...persistedBridgeState };
delete redacted.token;
assert.equal(typeof persistedBridgeState.token, 'string');
assert.equal('token' in redacted, false);
console.log(
  'bridge-secret-redaction:',
  JSON.stringify({
    attachUsesPersistedToken: true,
    redactedStateValidation: 'bridge.token required by lifecycle state schema',
    derivationAvailableOutsideState: derivedToken.length === 64,
  }),
);

// Model current xAI self-managed history conversion for a provider-executed
// image-generation call/result: both are skipped by convertToXaiResponsesInput.
const imageHistory = [
  { type: 'tool-call', providerExecuted: true, toolName: 'image_generation' },
  { type: 'tool-result', toolName: 'image_generation' },
];
const converted = imageHistory.filter(part => {
  if (part.type === 'tool-call' && part.providerExecuted) return false;
  if (part.type === 'tool-result') return false;
  return true;
});
assert.equal(converted.length, 0);
console.log(
  'xai-image-history:',
  JSON.stringify({
    convertedItems: converted.length,
    requiresPreviousResponseIdForRoundTrip: true,
  }),
);
