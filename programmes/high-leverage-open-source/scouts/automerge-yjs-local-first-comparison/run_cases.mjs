import assert from "node:assert/strict"
import fs from "node:fs"
import * as Automerge from "@automerge/automerge"
import * as Y from "yjs"

const readPackageVersion = packagePath =>
  JSON.parse(fs.readFileSync(new URL(packagePath, import.meta.url), "utf8")).version

const versions = {
  automerge: readPackageVersion(
    "../../../../node_modules/@automerge/automerge/package.json",
  ),
  yjs: readPackageVersion("../../../../node_modules/yjs/package.json"),
  node: process.version,
}

assert.equal(versions.automerge, "3.3.2")
assert.equal(versions.yjs, "13.6.31")

const cloneY = doc => {
  const clone = new Y.Doc()
  Y.applyUpdate(clone, Y.encodeStateAsUpdate(doc))
  return clone
}

const errorText = error => `${error?.name ?? "Error"}: ${error?.message ?? error}`

const results = {}

// Duplicate and reordered delivery must remain idempotent for distinct writers.
{
  const base = Automerge.from({ values: { base: true } })
  let left = Automerge.clone(base)
  let right = Automerge.clone(base)
  left = Automerge.change(left, doc => {
    doc.values.left = 1
  })
  right = Automerge.change(right, doc => {
    doc.values.right = 2
  })
  const leftChanges = Automerge.getChanges(base, left)
  const rightChanges = Automerge.getChanges(base, right)
  let replay = Automerge.clone(base)
  ;[replay] = Automerge.applyChanges(replay, rightChanges)
  ;[replay] = Automerge.applyChanges(replay, leftChanges)
  ;[replay] = Automerge.applyChanges(replay, leftChanges)
  assert.deepEqual(replay.values, { base: true, left: 1, right: 2 })
  results.automergeReorderedDuplicate = replay.values
}

{
  const base = new Y.Doc()
  base.getMap("values").set("base", true)
  const stateVector = Y.encodeStateVector(base)
  const left = cloneY(base)
  const right = cloneY(base)
  left.getMap("values").set("left", 1)
  right.getMap("values").set("right", 2)
  const leftUpdate = Y.encodeStateAsUpdate(left, stateVector)
  const rightUpdate = Y.encodeStateAsUpdate(right, stateVector)
  const replay = cloneY(base)
  Y.applyUpdate(replay, rightUpdate)
  Y.applyUpdate(replay, leftUpdate)
  Y.applyUpdate(replay, leftUpdate)
  assert.deepEqual(replay.getMap("values").toJSON(), {
    base: true,
    left: 1,
    right: 2,
  })
  results.yjsReorderedDuplicate = replay.getMap("values").toJSON()
}

// Convergence keeps both locally distinct records even when provider identity collides.
{
  const base = Automerge.from({ events: [] })
  let left = Automerge.clone(base)
  let right = Automerge.clone(base)
  left = Automerge.change(left, doc => {
    doc.events.push({ localId: "left", providerId: "provider-42" })
  })
  right = Automerge.change(right, doc => {
    doc.events.push({ localId: "right", providerId: "provider-42" })
  })
  const merged = Automerge.merge(left, right)
  assert.equal(merged.events.length, 2)
  assert.equal(new Set(merged.events.map(event => event.providerId)).size, 1)
  results.automergeDuplicateProviderIdentity = merged.events
}

{
  const base = new Y.Doc()
  base.getArray("events")
  const stateVector = Y.encodeStateVector(base)
  const left = cloneY(base)
  const right = cloneY(base)
  left
    .getArray("events")
    .insert(0, [{ localId: "left", providerId: "provider-42" }])
  right
    .getArray("events")
    .insert(0, [{ localId: "right", providerId: "provider-42" }])
  const merged = cloneY(base)
  Y.applyUpdate(merged, Y.encodeStateAsUpdate(left, stateVector))
  Y.applyUpdate(merged, Y.encodeStateAsUpdate(right, stateVector))
  const events = merged.getArray("events").toArray()
  assert.equal(events.length, 2)
  assert.equal(new Set(events.map(event => event.providerId)).size, 1)
  results.yjsDuplicateProviderIdentity = events
}

// Delete and edit can converge together; the application still owns the policy.
{
  const base = Automerge.from({
    event: {
      id: "event-1",
      providerId: "provider-42",
      deleted: false,
      start: "09:00",
    },
  })
  let deleting = Automerge.clone(base)
  let editing = Automerge.clone(base)
  deleting = Automerge.change(deleting, doc => {
    doc.event.deleted = true
  })
  editing = Automerge.change(editing, doc => {
    doc.event.start = "10:00"
  })
  const merged = Automerge.merge(deleting, editing)
  assert.equal(merged.event.deleted, true)
  assert.equal(merged.event.start, "10:00")
  results.automergeDeleteVersusEdit = merged.event
}

{
  const base = new Y.Doc()
  const event = new Y.Map()
  event.set("id", "event-1")
  event.set("providerId", "provider-42")
  event.set("deleted", false)
  event.set("start", "09:00")
  base.getMap("calendar").set("event", event)
  const stateVector = Y.encodeStateVector(base)
  const deleting = cloneY(base)
  const editing = cloneY(base)
  deleting.getMap("calendar").get("event").set("deleted", true)
  editing.getMap("calendar").get("event").set("start", "10:00")
  const merged = cloneY(base)
  Y.applyUpdate(merged, Y.encodeStateAsUpdate(deleting, stateVector))
  Y.applyUpdate(merged, Y.encodeStateAsUpdate(editing, stateVector))
  const mergedEvent = merged.getMap("calendar").get("event").toJSON()
  assert.equal(mergedEvent.deleted, true)
  assert.equal(mergedEvent.start, "10:00")
  results.yjsDeleteVersusEdit = mergedEvent
}

// Stable text positions survive a leading insertion and a full save/load restart.
{
  let doc = Automerge.from({ text: "abcde" })
  const cursor = Automerge.getCursor(doc, ["text"], 2)
  doc = Automerge.change(doc, draft => {
    Automerge.splice(draft, ["text"], 0, 0, "XX")
  })
  const restarted = Automerge.load(Automerge.save(doc))
  const position = Automerge.getCursorPosition(restarted, ["text"], cursor)
  assert.equal(restarted.text, "XXabcde")
  assert.equal(position, 4)
  results.automergeStablePositionAfterRestart = { cursor, position }
}

{
  const doc = new Y.Doc()
  const text = doc.getText("text")
  text.insert(0, "abcde")
  const relative = Y.createRelativePositionFromTypeIndex(text, 2)
  const encodedRelative = Y.encodeRelativePosition(relative)
  text.insert(0, "XX")
  const restarted = new Y.Doc()
  Y.applyUpdate(restarted, Y.encodeStateAsUpdate(doc))
  const decodedRelative = Y.decodeRelativePosition(encodedRelative)
  const absolute = Y.createAbsolutePositionFromRelativePosition(
    decodedRelative,
    restarted,
  )
  assert.equal(restarted.getText("text").toString(), "XXabcde")
  assert.equal(absolute?.index, 4)
  results.yjsStablePositionAfterRestart = {
    encodedBytes: encodedRelative.length,
    position: absolute?.index,
  }
}

// Compare failure atomicity for a truncated second change/update.
{
  const base = Automerge.from({ text: "" })
  let source = Automerge.clone(base)
  source = Automerge.change(source, doc => {
    Automerge.splice(doc, ["text"], 0, 0, "abcdef")
  })
  source = Automerge.change(source, doc => {
    Automerge.splice(doc, ["text"], 2, 2, "")
  })
  const changes = Automerge.getChanges(base, source)
  assert.equal(changes.length, 2)
  let mutationAfterThrow = null
  let thrownCuts = 0
  for (let cut = 1; cut < changes[1].length; cut += 1) {
    let target = Automerge.clone(base)
    ;[target] = Automerge.applyChanges(target, [changes[0]])
    const before = target.text
    try {
      ;[target] = Automerge.applyChanges(target, [changes[1].slice(0, cut)])
    } catch (error) {
      thrownCuts += 1
      if (target.text !== before && mutationAfterThrow === null) {
        mutationAfterThrow = {
          cut,
          before,
          after: target.text,
          error: errorText(error),
        }
      }
    }
  }
  assert.equal(thrownCuts, changes[1].length - 1)
  assert.equal(mutationAfterThrow, null)

  let full = Automerge.clone(base)
  ;[full] = Automerge.applyChanges(full, changes)
  assert.equal(full.text, "abef")
  results.automergeTruncatedChange = {
    bytes: changes[1].length,
    thrownCuts,
    mutationAfterThrow,
    fullText: full.text,
  }
}

{
  const source = new Y.Doc()
  const text = source.getText("text")
  text.insert(0, "abcdef")
  text.delete(2, 2)
  const update = Y.encodeStateAsUpdate(source)
  const mutationAfterThrow = []
  let thrownCuts = 0
  let silentPartialCuts = 0
  for (let cut = 1; cut < update.length; cut += 1) {
    const target = new Y.Doc()
    let threw = null
    try {
      Y.applyUpdate(target, update.slice(0, cut))
    } catch (error) {
      threw = errorText(error)
      thrownCuts += 1
    }
    const visible = target.getText("text").toString()
    const stateVectorBytes = Y.encodeStateVector(target).length
    if (threw !== null && (visible !== "" || stateVectorBytes > 1)) {
      mutationAfterThrow.push({ cut, visible, stateVectorBytes, error: threw })
    }
    if (threw === null && (visible !== "" || stateVectorBytes > 1)) {
      silentPartialCuts += 1
    }
  }
  assert.equal(thrownCuts, update.length - 1)
  assert.equal(silentPartialCuts, 0)
  assert.ok(mutationAfterThrow.length > 0)
  assert.deepEqual(
    mutationAfterThrow.map(receipt => receipt.cut),
    [36, 37, 38, 39, 40, 41, 42, 43, 44],
  )
  assert.ok(mutationAfterThrow.every(receipt => receipt.visible === "abef"))
  assert.ok(mutationAfterThrow.every(receipt => receipt.stateVectorBytes === 7))

  const full = new Y.Doc()
  Y.applyUpdate(full, update)
  assert.equal(full.getText("text").toString(), "abef")
  results.yjsTruncatedUpdate = {
    bytes: update.length,
    thrownCuts,
    silentPartialCuts,
    mutationAfterThrow: mutationAfterThrow.slice(0, 12),
    mutationAfterThrowCount: mutationAfterThrow.length,
    fullText: full.getText("text").toString(),
  }
}

// Reusing one writer identity across independent writers is a recovery hazard.
{
  const actor = "00000000000000000000000000000001"
  let left = Automerge.init(actor)
  let right = Automerge.init(actor)
  left = Automerge.change(left, doc => {
    doc.left = true
  })
  right = Automerge.change(right, doc => {
    doc.right = true
  })
  const runOrder = (first, second) => {
    let target = Automerge.init()
    let error = null
    try {
      ;[target] = Automerge.applyChanges(target, Automerge.getAllChanges(first))
      ;[target] = Automerge.applyChanges(target, Automerge.getAllChanges(second))
    } catch (caught) {
      error = errorText(caught)
    }
    return { value: { ...target }, error }
  }
  const leftThenRight = runOrder(left, right)
  const rightThenLeft = runOrder(right, left)
  assert.deepEqual(leftThenRight.value, { left: true })
  assert.deepEqual(rightThenLeft.value, { right: true })
  assert.match(leftThenRight.error ?? "", /duplicate seq 1/)
  assert.match(rightThenLeft.error ?? "", /duplicate seq 1/)
  results.automergeDuplicateWriterIdentity = { leftThenRight, rightThenLeft }
}

{
  const makeWriter = key => {
    const doc = new Y.Doc()
    doc.clientID = 424242
    doc.getMap("values").set(key, true)
    return Y.encodeStateAsUpdate(doc)
  }
  const leftUpdate = makeWriter("left")
  const rightUpdate = makeWriter("right")
  const runOrder = updates => {
    const target = new Y.Doc()
    for (const update of updates) {
      Y.applyUpdate(target, update)
    }
    return target.getMap("values").toJSON()
  }
  const leftThenRight = runOrder([leftUpdate, rightUpdate])
  const rightThenLeft = runOrder([rightUpdate, leftUpdate])
  assert.deepEqual(leftThenRight, { left: true })
  assert.deepEqual(rightThenLeft, { right: true })
  results.yjsDuplicateWriterIdentity = { leftThenRight, rightThenLeft }
}

console.log(JSON.stringify({ versions, results }, null, 2))
