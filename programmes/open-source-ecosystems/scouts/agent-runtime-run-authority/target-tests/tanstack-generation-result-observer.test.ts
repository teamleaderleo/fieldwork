import { describe, expect, it, vi } from 'vitest'
import {
  generateImage,
  type GenerationMiddleware,
  type ImageAdapter,
} from '../../src/index'
import { observeGenerationResult } from '../../src/adapter-internals'

function imageAdapter(url: string): ImageAdapter<string> {
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
      images: [{ url }],
      usage: {
        promptTokens: 0,
        completionTokens: 0,
        totalTokens: 0,
        unitsBilled: 1,
      },
    })),
  }
}

describe('generation final-result observers', () => {
  it('observes the result only after every registered transform', async () => {
    const observed: Array<unknown> = []

    const observer: GenerationMiddleware = {
      name: 'fieldwork-observer',
      onStart: (ctx) => {
        observeGenerationResult(ctx, (result) => {
          observed.push(result)
        })
      },
    }

    const laterTransform: GenerationMiddleware = {
      name: 'fieldwork-later-transform',
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

    const result = await generateImage({
      adapter: imageAdapter('https://provider.test/original.png'),
      prompt: 'final-result observer',
      middleware: [observer, laterTransform],
    })

    expect(result.images[0]?.url).toBe('https://app.test/final.png')
    expect(observed).toHaveLength(1)
    expect(
      (observed[0] as { images?: Array<{ url?: string }> }).images?.[0]?.url,
    ).toBe('https://app.test/final.png')
  })

  it('does not leak observers between activity contexts', async () => {
    let observations = 0
    const observer: GenerationMiddleware = {
      name: 'fieldwork-once-per-context',
      onStart: (ctx) => {
        observeGenerationResult(ctx, () => {
          observations += 1
        })
      },
    }

    await generateImage({
      adapter: imageAdapter('https://provider.test/first.png'),
      prompt: 'first observer call',
      middleware: [observer],
    })
    await generateImage({
      adapter: imageAdapter('https://provider.test/second.png'),
      prompt: 'second observer call',
      middleware: [],
    })

    expect(observations).toBe(1)
  })
})
