async function applyTransforms(raw, transforms) {
  let current = raw
  for (const transform of transforms) {
    const next = await transform(current)
    if (next !== undefined) current = next
  }
  return current
}

let persisted
const transforms = []

// Persistence middleware registers a transform during onStart.
transforms.push(async (result) => {
  persisted = structuredClone(result)
  return result
})

// A later middleware registers another valid result transform.
transforms.push(async (result) => ({ ...result, url: 'durable://final' }))

const live = await applyTransforms(
  { url: 'provider://temporary' },
  transforms,
)

console.log(
  JSON.stringify(
    {
      persisted,
      live,
      restoredMatchesLive: JSON.stringify(persisted) === JSON.stringify(live),
    },
    null,
    2,
  ),
)
