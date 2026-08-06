import { describe, expect, it, vi } from 'vitest'
import { generateImage } from '@tanstack/ai'
import type {
  GenerationMiddleware,
  ImageAdapter,
} from '@tanstack/ai'
import { memoryPersistence } from '../src/memory'
import { withGenerationPersistence } from '../src/middleware'

function imageAdapter(): ImageAdapter<string> {
  return {
    kind: 'image',
    name: 'fieldwork-image-provider',
    model: 'fieldwork-image-model',
    '~types': {
      providerOptions: {},
      modelProviderOptionsByName: {},
      modelSizeByName: {},
      modelInputModalitiesByName: {},
    },
    generateImages: vi.fn(async () => ({
      images: [{ url: 'https://provider.test/original.png' }],
      usage: {
        promptTokens: 0,
        completionTokens: 0,
        totalTokens: 0,
        unitsBilled: 1,
      },
    })),
  }
}

describe('generation persistence result authority', () => {
  it('persists the same final result returned after every middleware transform', async () => {
    const persistence = memoryPersistence()
    let requestId = ''

    const captureRequestId: GenerationMiddleware = {
      name: 'capture-request-id',
      onStart: (ctx) => {
        requestId = ctx.requestId
      },
    }

    const laterTransform: GenerationMiddleware = {
      name: 'later-transform',
      onStart: (ctx) => {
        ctx.resultTransforms.push((result) => {
          const current = result as {
            images: Array<{ url?: string }>
          }
          return {
            ...current,
            images: current.images.map((image, index) =>
              index === 0
                ? { ...image, url: 'https://app.test/final.png' }
                : image,
            ),
          }
        })
      },
    }

    const live = await generateImage({
      adapter: imageAdapter(),
      prompt: 'a final result',
      middleware: [
        captureRequestId,
        withGenerationPersistence(persistence, {
          threadId: 'fieldwork:result-authority',
          // This regression concerns final-result metadata ordering, not
          // artifact-byte persistence. Disable extraction so the synthetic
          // provider URL never becomes a network dependency.
          extractArtifacts: () => [],
        }),
        laterTransform,
      ],
    })

    const persisted = await persistence.stores.generationRuns.get(requestId)
    const persistedResult = persisted?.result as
      | { images?: Array<{ url?: string }> }
      | undefined

    expect(live.images[0]?.url).toBe('https://app.test/final.png')
    expect(persistedResult?.images?.[0]?.url).toBe(
      'https://app.test/final.png',
    )
  })
})
