## In simple words

Three independent source surfaces line up on the same compatibility mismatch: Together documents top-level reasoning usage, SGLang emits it, and AI SDK's generic OpenAI-compatible normalization ignores it while retaining it in raw usage.

## Evidence map

### AI SDK — current target source

Pin: `8e9028317de6a72973971356283271aff44bba74`

- `packages/openai-compatible/src/chat/openai-compatible-chat-language-model.ts`
  - usage schema is `z.looseObject`;
  - explicitly models nested `completion_tokens_details.reasoning_tokens`;
  - top-level provider fields survive loose parsing.
- `packages/openai-compatible/src/chat/convert-openai-compatible-chat-usage.ts`
  - normalized reasoning reads nested reasoning only;
  - absent nested reasoning becomes zero.
- `packages/togetherai/src/togetherai-provider.ts`
  - chat model is `OpenAICompatibleChatLanguageModel`;
  - `includeUsage: true`;
  - no provider-specific `convertUsage`.

Classification: `source-read`.

### TogetherAI — provider contract

Current OpenAI-compatibility documentation states:

- standard usage fields are prompt/completion/total;
- Together-specific fields such as cached and reasoning token counts may appear on supporting models;
- these fields may differ in placement from OpenAI's nested detail objects.

Current reasoning documentation states that `max_tokens` needs to accommodate reasoning plus answer output.

A recent direct Kimi-K3 verification retained in Vercel AI records provider-specific cached/reasoning fields accompanying completion usage once streaming usage is requested.

Classification: `documented` plus retained `observed` Vercel verification.

### SGLang — independent compatible implementation

Pin: `b3bffef70aa17733b48af91e4b529e72c913bc6e`

- `UsageInfo` declares top-level `reasoning_tokens`.
- `UsageProcessor.calculate_token_usage` emits top-level reasoning and computes total as prompt + completion.
- scheduler output records completion from the full generated output-id sequence and reasoning separately.

Classification: `source-read` primary implementation evidence.

## Supported claim

The alternate top-level reasoning field is a real OpenAI-compatible dialect used by at least one documented hosted provider and one independent serving implementation. Current AI SDK generic parsing retains the field in raw usage but omits it from normalized reasoning details.

## Limitation

No new live provider request was executed in this lane. The Together contract and prior Vercel live verification establish the response dialect; source-native target execution remains the next evidence step.
