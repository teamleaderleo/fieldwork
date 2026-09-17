import assert from 'node:assert/strict'

function epochWithoutProjectionFence() {
  const backend = { epoch: 2, status: 'busy' }
  const ui = { status: 'busy' }

  // The superseded backend writer cannot mutate the durable run record.
  const staleWriterEpoch = 1
  if (staleWriterEpoch === backend.epoch) backend.status = 'idle'

  // But the visible status event does not carry the epoch and is accepted.
  ui.status = 'idle'

  return { backend, ui }
}

function epochPropagatedToProjection() {
  const backend = { epoch: 2, status: 'busy' }
  const ui = { epoch: 2, status: 'busy' }
  const staleEvent = { epoch: 1, status: 'idle' }

  if (staleEvent.epoch === ui.epoch) ui.status = staleEvent.status

  return { backend, ui }
}

function replayWithoutAlignment() {
  const delivered = ['hello ']
  const replayedJournal = ['hello ', 'world']
  delivered.push(...replayedJournal)
  return delivered.join('')
}

function replayWithAlignment() {
  const delivered = ['hello ']
  const replayedJournal = ['hello ', 'world']

  let prefix = 0
  while (
    prefix < delivered.length &&
    prefix < replayedJournal.length &&
    delivered[prefix] === replayedJournal[prefix]
  ) {
    prefix += 1
  }
  delivered.push(...replayedJournal.slice(prefix))
  return delivered.join('')
}

function deadlineWithoutProjectionFence() {
  const operation = { settlement: 'timeout' }
  const ui = { status: 'timed_out' }

  // The remote provider job completes after the local wait has timed out.
  const remoteEvent = { status: 'completed' }
  ui.status = remoteEvent.status

  return { operation, ui }
}

function deadlinePropagatedToProjection() {
  const operation = { settlement: 'timeout' }
  const ui = { settlement: 'timeout', status: 'timed_out' }
  const remoteEvent = { settlement: 'success', status: 'completed' }

  if (ui.settlement === 'pending') {
    ui.settlement = remoteEvent.settlement
    ui.status = remoteEvent.status
  }

  return { operation, ui }
}

function durableIntentWithoutOutcomeProjection() {
  const interruptSequence = 10
  const oldWake = { admittedAt: 9 }
  const newPrompt = { admittedAt: 11 }

  const coordinator = {
    oldWakeAccepted: oldWake.admittedAt > interruptSequence,
    newPromptAccepted: newPrompt.admittedAt > interruptSequence,
  }

  // The durable interrupt request protects new intent, but the UI has no
  // durable activity outcome to project and remains on its prior live state.
  const ui = { status: 'busy', durableOutcome: undefined }

  return { coordinator, ui }
}

const result = {
  epochWithoutProjectionFence: epochWithoutProjectionFence(),
  epochPropagatedToProjection: epochPropagatedToProjection(),
  replayWithoutAlignment: replayWithoutAlignment(),
  replayWithAlignment: replayWithAlignment(),
  deadlineWithoutProjectionFence: deadlineWithoutProjectionFence(),
  deadlinePropagatedToProjection: deadlinePropagatedToProjection(),
  durableIntentWithoutOutcomeProjection:
    durableIntentWithoutOutcomeProjection(),
}

assert.equal(result.epochWithoutProjectionFence.backend.status, 'busy')
assert.equal(result.epochWithoutProjectionFence.ui.status, 'idle')
assert.equal(result.epochPropagatedToProjection.ui.status, 'busy')
assert.equal(result.replayWithoutAlignment, 'hello hello world')
assert.equal(result.replayWithAlignment, 'hello world')
assert.equal(result.deadlineWithoutProjectionFence.operation.settlement, 'timeout')
assert.equal(result.deadlineWithoutProjectionFence.ui.status, 'completed')
assert.equal(result.deadlinePropagatedToProjection.ui.status, 'timed_out')
assert.equal(
  result.durableIntentWithoutOutcomeProjection.coordinator.oldWakeAccepted,
  false,
)
assert.equal(
  result.durableIntentWithoutOutcomeProjection.coordinator.newPromptAccepted,
  true,
)
assert.equal(
  result.durableIntentWithoutOutcomeProjection.ui.durableOutcome,
  undefined,
)

console.log(JSON.stringify(result, null, 2))
