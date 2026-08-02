const messages = [
  {
    id: 'turn-0',
    role: 'user',
    parts: [{ type: 'text', text: 'first question' }],
  },
  {
    id: 'turn-0:reply',
    role: 'assistant',
    parts: [{ type: 'text', text: 'first answer' }],
  },
]

const lastMessage = structuredClone(messages.at(-1))
const streamingState = {
  message:
    lastMessage?.role === 'assistant'
      ? lastMessage
      : { id: 'generated', role: 'assistant', parts: [] },
}

// The resumed stream reveals its identity only after state creation.
streamingState.message.id = 'turn-1:reply'
streamingState.message.parts.push({ type: 'text', text: 'RESUMED-TEXT' })
messages.push(streamingState.message)

console.log(
  JSON.stringify(
    {
      messages,
      duplicatedText: messages.filter((message) =>
        message.parts.some((part) => part.text === 'first answer'),
      ).length,
    },
    null,
    2,
  ),
)
