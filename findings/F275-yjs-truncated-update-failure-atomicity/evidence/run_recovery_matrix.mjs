import assert from "node:assert/strict"
import crypto from "node:crypto"
import fs from "node:fs"
import path from "node:path"
import { createRequire } from "node:module"
import * as Y13 from "yjs"
import * as Y14 from "@y/y"

const require = createRequire(import.meta.url)
const versionOf = packageName => require(`${packageName}/package.json`).version

assert.equal(versionOf("yjs"), "13.6.31")
assert.equal(versionOf("@y/y"), "14.0.0-rc.24")

const sha256 = bytes =>
  crypto.createHash("sha256").update(Buffer.from(bytes)).digest("hex")
const hex = bytes => Buffer.from(bytes).toString("hex")
const base64 = bytes => Buffer.from(bytes).toString("base64")
const errorText = error => `${error?.name ?? "Error"}: ${error?.message ?? error}`

const variants = [
  {
    name: "yjs-13-v1",
    packageName: "yjs",
    version: versionOf("yjs"),
    Y: Y13,
    encode: doc => Y13.encodeStateAsUpdate(doc),
    apply: (doc, update, origin) => Y13.applyUpdate(doc, update, origin),
  },
  {
    name: "yjs-13-v2",
    packageName: "yjs",
    version: versionOf("yjs"),
    Y: Y13,
    encode: doc => Y13.encodeStateAsUpdateV2(doc),
    apply: (doc, update, origin) => Y13.applyUpdateV2(doc, update, origin),
  },
  {
    name: "yjs-14-v1",
    packageName: "@y/y",
    version: versionOf("@y/y"),
    Y: Y14,
    encode: doc => Y14.encodeStateAsUpdate(doc),
    apply: (doc, update, origin) => Y14.applyUpdate(doc, update, origin),
  },
  {
    name: "yjs-14-v2",
    packageName: "@y/y",
    version: versionOf("@y/y"),
    Y: Y14,
    encode: doc => Y14.encodeStateAsUpdateV2(doc),
    apply: (doc, update, origin) => Y14.applyUpdateV2(doc, update, origin),
  },
]

for (const variant of variants) {
  for (const [name, value] of Object.entries({
    Doc: variant.Y.Doc,
    encodeStateVector: variant.Y.encodeStateVector,
    encode: variant.encode,
    apply: variant.apply,
  })) {
    assert.equal(typeof value, "function", `${variant.name} missing ${name}`)
  }
}

const pendingSummary = doc => {
  const store = doc.store
  const pendingStructs = store?.pendingStructs
  return {
    pendingStructsBytes: pendingStructs?.update?.length ?? 0,
    pendingMissing:
      pendingStructs?.missing == null
        ? []
        : [...pendingStructs.missing.entries()].sort((a, b) => a[0] - b[0]),
    pendingDeleteSetBytes: store?.pendingDs?.length ?? 0,
  }
}

const attachObservers = (doc, text) => {
  const counts = {
    beforeTransaction: 0,
    afterTransaction: 0,
    update: 0,
    updateV2: 0,
    text: 0,
  }
  doc.on("beforeTransaction", () => {
    counts.beforeTransaction += 1
  })
  doc.on("afterTransaction", () => {
    counts.afterTransaction += 1
  })
  doc.on("update", () => {
    counts.update += 1
  })
  doc.on("updateV2", () => {
    counts.updateV2 += 1
  })
  text.observe(() => {
    counts.text += 1
  })
  return counts
}

const snapshot = (variant, doc, observers) => {
  const vector = variant.Y.encodeStateVector(doc)
  return {
    visible: doc.getText("text").toString(),
    stateVectorBytes: vector.length,
    stateVectorHex: hex(vector),
    pending: pendingSummary(doc),
    observers: { ...observers },
  }
}

const stateChanged = (before, after) =>
  before.visible !== after.visible ||
  before.stateVectorHex !== after.stateVectorHex ||
  JSON.stringify(before.pending) !== JSON.stringify(after.pending) ||
  JSON.stringify(before.observers) !== JSON.stringify(after.observers)

const makeFullUpdate = variant => {
  const source = new variant.Y.Doc()
  const text = source.getText("text")
  text.insert(0, "abcdef")
  text.delete(2, 2)
  const update = variant.encode(source)
  return { source, update }
}

const applyCleanControl = (variant, update) => {
  const target = new variant.Y.Doc()
  const text = target.getText("text")
  const observers = attachObservers(target, text)
  variant.apply(target, update, "clean-full")
  const state = snapshot(variant, target, observers)
  assert.equal(state.visible, "abef", `${variant.name} full update control`)
  return { target, state }
}

const exerciseRecovery = (variant, update, cut) => {
  const target = new variant.Y.Doc()
  const text = target.getText("text")
  const observers = attachObservers(target, text)
  const truncated = update.slice(0, cut)
  let truncatedError = null
  try {
    variant.apply(target, truncated, "truncated")
  } catch (error) {
    truncatedError = errorText(error)
  }
  assert.notEqual(truncatedError, null, `${variant.name} minimized prefix must throw`)
  const afterThrow = snapshot(variant, target, observers)

  let persisted = null
  try {
    const encoded = variant.encode(target)
    const restored = new variant.Y.Doc()
    variant.apply(restored, encoded, "restore-after-throw")
    persisted = {
      encodedBytes: encoded.length,
      encodedSha256: sha256(encoded),
      restoredVisible: restored.getText("text").toString(),
      restoredStateVectorHex: hex(variant.Y.encodeStateVector(restored)),
      restoredPending: pendingSummary(restored),
    }
  } catch (error) {
    persisted = { error: errorText(error) }
  }

  let retry = null
  try {
    variant.apply(target, update, "retry-full")
    retry = snapshot(variant, target, observers)
  } catch (error) {
    retry = { error: errorText(error) }
  }

  let independentRemote = null
  try {
    const peer = new variant.Y.Doc()
    peer.getMap("peer").set("afterThrow", true)
    variant.apply(target, variant.encode(peer), "independent-remote")
    independentRemote = {
      value: target.getMap("peer").get("afterThrow"),
      state: snapshot(variant, target, observers),
    }
  } catch (error) {
    independentRemote = { error: errorText(error) }
  }

  let localWrite = null
  try {
    target.transact(() => {
      target.getMap("local").set("afterThrow", true)
    }, "local-after-throw")
    localWrite = {
      value: target.getMap("local").get("afterThrow"),
      state: snapshot(variant, target, observers),
    }
  } catch (error) {
    localWrite = { error: errorText(error) }
  }

  return {
    cut,
    prefixBytes: truncated.length,
    prefixHex: hex(truncated),
    prefixBase64: base64(truncated),
    prefixSha256: sha256(truncated),
    error: truncatedError,
    afterThrow,
    persisted,
    retry,
    independentRemote,
    localWrite,
  }
}

const results = {}

for (const variant of variants) {
  const { update } = makeFullUpdate(variant)
  const clean = applyCleanControl(variant, update)
  const baselineDoc = new variant.Y.Doc()
  const baselineText = baselineDoc.getText("text")
  const baselineObservers = attachObservers(baselineDoc, baselineText)
  const baseline = snapshot(variant, baselineDoc, baselineObservers)

  const thrown = []
  const silent = []
  const mutatedAfterThrow = []

  for (let cut = 1; cut < update.length; cut += 1) {
    const target = new variant.Y.Doc()
    const text = target.getText("text")
    const observers = attachObservers(target, text)
    const before = snapshot(variant, target, observers)
    let error = null
    try {
      variant.apply(target, update.slice(0, cut), `cut-${cut}`)
    } catch (caught) {
      error = errorText(caught)
    }
    const after = snapshot(variant, target, observers)
    const changed = stateChanged(before, after)
    if (error !== null) {
      thrown.push({ cut, changed, error, after })
      if (changed) {
        mutatedAfterThrow.push({ cut, error, after })
      }
    } else if (changed && after.visible !== clean.state.visible) {
      silent.push({ cut, after })
    }
  }

  const firstMutated = mutatedAfterThrow[0]
  const recovery =
    firstMutated == null ? null : exerciseRecovery(variant, update, firstMutated.cut)

  if (variant.name === "yjs-13-v1") {
    assert.ok(mutatedAfterThrow.length > 0, "stable Yjs V1 reproduction disappeared")
  }

  if (recovery?.retry?.error == null) {
    assert.equal(recovery.retry.visible, clean.state.visible)
    assert.equal(recovery.retry.stateVectorHex, clean.state.stateVectorHex)
  }

  results[variant.name] = {
    package: variant.packageName,
    version: variant.version,
    updateBytes: update.length,
    updateHex: hex(update),
    updateSha256: sha256(update),
    baseline,
    clean: clean.state,
    thrownCuts: thrown.length,
    silentPartialCuts: silent,
    mutationAfterThrowCount: mutatedAfterThrow.length,
    mutationCuts: mutatedAfterThrow.map(item => item.cut),
    firstMutation: firstMutated ?? null,
    recovery,
  }
}

const record = {
  schemaVersion: 1,
  node: process.version,
  generatedAt: new Date().toISOString(),
  results,
}

const outputDir = process.env.RESULTS_DIR
if (outputDir) {
  fs.mkdirSync(outputDir, { recursive: true })
  fs.writeFileSync(
    path.join(outputDir, `yjs-recovery-${process.version}.json`),
    `${JSON.stringify(record, null, 2)}\n`,
  )
}

console.log(JSON.stringify(record, null, 2))
