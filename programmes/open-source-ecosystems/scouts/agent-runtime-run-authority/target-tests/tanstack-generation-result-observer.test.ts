import { describe, expect, it, vi } from 'vitest'
import { generateImage } from '../../src/index'
import { observeGenerationResult } from '../../src/adapter-internals'
import type { GenerationMiddleware } from '../../src/activities/middleware'

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

    const adapter = {
      kind: 'image' as const,
      name: 'fieldwork-image-provider',
      model: 'fieldwork-image-model',
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

    const result = await generateImage({
      adapter: adapter as any,
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
    const adapter = {
      kind: 'image' as const,
      name: 'fieldwork-image-provider',
      model: 'fieldwork-image-model',
      generateImages: vi.fn(async () => ({
        images: [{ url: 'https://provider.test/image.png' }],
        usage: {
          promptTokens: 0,
          completionTokens: 0,
          totalTokens: 0,
          unitsBilled: 1,
        },
      })),
    }

    await generateImage({
      adapter: adapter as any,
      prompt: 'first observer call',
      middleware: [observer],
    })
    await generateImage({
      adapter: adapter as any,
      prompt: 'second observer call',
      middleware: [],
    })

    expect(observations).toBe(1)
  })
})
