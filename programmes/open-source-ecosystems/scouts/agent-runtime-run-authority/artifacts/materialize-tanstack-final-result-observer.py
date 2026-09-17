from __future__ import annotations

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text()
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected one occurrence in {path}, found {count}: {old[:120]!r}")
    file.write_text(text.replace(old, new, 1))


replace_once(
    "packages/ai/src/activities/middleware/run.ts",
    """} from './types'\n\n/**\n * Build the stable context for a single media-activity call.\n""",
    """} from './types'\n\ntype GenerationResultObserver = (\n  result: unknown,\n  ctx: GenerationResultTransformContext,\n) => void | Promise<void>\n\nconst generationResultObservers = new WeakMap<\n  GenerationMiddlewareContext,\n  Array<GenerationResultObserver>\n>()\n\n/**\n * Register a side-effecting observer that runs after every result transform has\n * completed. Observers cannot replace the result; they receive the same final\n * value that the activity returns or streams.\n *\n * Stored outside the public context shape so custom context builders remain\n * source-compatible. The WeakMap entry is removed after the transform phase.\n */\nexport function observeGenerationResult(\n  ctx: GenerationMiddlewareContext,\n  observer: GenerationResultObserver,\n): void {\n  const existing = generationResultObservers.get(ctx)\n  if (existing) {\n    existing.push(observer)\n  } else {\n    generationResultObservers.set(ctx, [observer])\n  }\n}\n\n/**\n * Build the stable context for a single media-activity call.\n""",
)

replace_once(
    "packages/ai/src/activities/middleware/run.ts",
    """  for (const transform of ctx.resultTransforms ?? []) {\n    const transformed = await transform(current, transformCtx)\n    if (transformed !== undefined) {\n      current = transformed as TResult\n    }\n  }\n\n  return current\n}\n""",
    """  try {\n    for (const transform of ctx.resultTransforms ?? []) {\n      const transformed = await transform(current, transformCtx)\n      if (transformed !== undefined) {\n        current = transformed as TResult\n      }\n    }\n\n    for (const observer of generationResultObservers.get(ctx) ?? []) {\n      await observer(current, transformCtx)\n    }\n\n    return current\n  } finally {\n    generationResultObservers.delete(ctx)\n  }\n}\n""",
)

replace_once(
    "packages/ai/src/adapter-internals.ts",
    """export {\n  getPendingTurn,\n  PendingTurnCapability,\n  providePendingTurn,\n} from './activities/chat/middleware/pending-turn'\n""",
    """export {\n  getPendingTurn,\n  PendingTurnCapability,\n  providePendingTurn,\n} from './activities/chat/middleware/pending-turn'\nexport { observeGenerationResult } from './activities/middleware/run'\n""",
)

replace_once(
    "packages/ai-persistence/src/middleware.ts",
    """import { providePendingTurn } from '@tanstack/ai/adapter-internals'\n""",
    """import {\n  observeGenerationResult,\n  providePendingTurn,\n} from '@tanstack/ai/adapter-internals'\n""",
)

replace_once(
    "packages/ai-persistence/src/middleware.ts",
    """      // Always capture the terminal result metadata + any artifact refs onto the\n      // run record. Registered AFTER the artifact transform so it observes the\n      // fully-merged result (with the artifact refs attached). `result` is\n      // metadata/urls only — the media bytes already live in the blob store.\n      ctx.resultTransforms?.push(async (result) => {\n        const rawArtifacts = objectValue(result)?.artifacts\n        const artifacts = Array.isArray(rawArtifacts)\n          ? rawArtifacts.filter(isArtifactRef)\n          : []\n        await generationRuns.update(runId, {\n          result,\n          ...(artifacts.length > 0 ? { artifacts } : {}),\n        })\n        return undefined\n      })\n""",
    """      // Capture terminal metadata only after the complete transform chain.\n      // Artifact persistence remains a transform because it rewrites the live\n      // result; durable capture is an observer because it must see the exact\n      // value the activity will return or stream, independent of middleware\n      // registration order.\n      observeGenerationResult(ctx, async (result) => {\n        const rawArtifacts = objectValue(result)?.artifacts\n        const artifacts = Array.isArray(rawArtifacts)\n          ? rawArtifacts.filter(isArtifactRef)\n          : []\n        await generationRuns.update(runId, {\n          result,\n          ...(artifacts.length > 0 ? { artifacts } : {}),\n        })\n      })\n""",
)

changeset = Path(".changeset/quiet-maps-rest.md")
changeset.write_text(
    """---\n'@tanstack/ai': patch\n'@tanstack/ai-persistence': patch\n---\n\nCapture generation persistence after the complete result-transform chain so\nthe durable run record matches the result returned or streamed to the caller.\n"""
)
