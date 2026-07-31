import assert from "node:assert/strict"
import fs from "node:fs/promises"
import path from "node:path"

const delay = milliseconds =>
  new Promise(resolve => setTimeout(resolve, milliseconds))

const CANCELLATION_ACKNOWLEDGEMENT = Symbol("cancellation-acknowledgement")

function acknowledgeCancellation() {
  return Object.freeze({ [CANCELLATION_ACKNOWLEDGEMENT]: true })
}

function isCancellationAcknowledgement(value) {
  return Boolean(
    value
      && typeof value === "object"
      && value[CANCELLATION_ACKNOWLEDGEMENT] === true,
  )
}

function minimizedFailure(error) {
  return Object.freeze({
    code: "runtime_failed",
    errorType: error instanceof Error ? error.name : "NonError",
  })
}

function minimizedControlFailure(error) {
  return Object.freeze({
    code: "control_failed",
    errorType: error instanceof Error ? error.name : "NonError",
  })
}

function consumeResponseEvents(events) {
  const assistantText = []
  const argumentBuffers = new Map()
  const dispatchedCalls = []
  const dispatchedIds = new Set()
  const errors = []
  let responseCompleted = false

  for (const event of events) {
    switch (event.type) {
      case "assistant_text.delta":
        assistantText.push(event.delta)
        break

      case "function_call.arguments.delta":
        argumentBuffers.set(
          event.callId,
          `${argumentBuffers.get(event.callId) ?? ""}${event.delta}`,
        )
        break

      case "function_call.completed": {
        if (dispatchedIds.has(event.callId)) {
          errors.push({
            code: "duplicate_call_completion",
            callId: event.callId,
          })
          break
        }

        dispatchedIds.add(event.callId)
        dispatchedCalls.push({
          callId: event.callId,
          name: event.name,
          arguments:
            event.arguments ?? argumentBuffers.get(event.callId) ?? "",
        })
        break
      }

      case "response.completed":
        responseCompleted = true
        break

      default:
        errors.push({
          code: "unsupported_event",
          eventType: event.type,
        })
        break
    }
  }

  const terminal = !responseCompleted
    ? { kind: "error", code: "stream_incomplete" }
    : errors.length > 0
      ? { kind: "error", code: errors[0].code }
      : { kind: "success" }

  return {
    assistantText: assistantText.join(""),
    dispatchedCalls,
    errors,
    terminal,
  }
}

async function superviseRuntime(
  startRuntime,
  { timeoutMs = 20, cancellationGraceMs = 20 } = {},
) {
  const controller = new AbortController()
  const runtimeResult = Promise.resolve()
    .then(() => startRuntime(controller.signal))
    .then(
      value => ({ kind: "settled", value }),
      error => ({ kind: "failed", failure: minimizedFailure(error) }),
    )

  const beforeDeadline = await Promise.race([
    runtimeResult,
    delay(timeoutMs).then(() => ({ kind: "deadline" })),
  ])

  if (beforeDeadline.kind === "settled") {
    return Object.freeze({ kind: "completed" })
  }

  if (beforeDeadline.kind === "failed") {
    return Object.freeze({
      kind: "failed",
      ...beforeDeadline.failure,
    })
  }

  controller.abort(new Error("runtime deadline exceeded"))

  const afterCancellationRequest = await Promise.race([
    runtimeResult,
    delay(cancellationGraceMs).then(() => ({ kind: "grace_expired" })),
  ])

  if (afterCancellationRequest.kind === "settled") {
    if (isCancellationAcknowledgement(afterCancellationRequest.value)) {
      return Object.freeze({
        kind: "cancelled",
        code: "runtime_acknowledged_cancellation",
      })
    }

    return Object.freeze({
      kind: "settled_after_cancel_request",
      code: "cancellation_causality_unconfirmed",
    })
  }

  if (afterCancellationRequest.kind === "failed") {
    return Object.freeze({
      kind: "failed_after_cancel_request",
      code: "cancellation_causality_unconfirmed",
      errorType: afterCancellationRequest.failure.errorType,
    })
  }

  return Object.freeze({
    kind: "outcome_unknown",
    code: "runtime_did_not_settle_after_cancel_request",
  })
}

const cases = []

function recordCase(name, run) {
  cases.push({ name, run })
}

recordCase("partial arguments never render or dispatch", async () => {
  const result = consumeResponseEvents([
    {
      type: "function_call.arguments.delta",
      callId: "call-1",
      delta: "{\"secret\":",
    },
  ])

  assert.equal(result.assistantText, "")
  assert.deepEqual(result.dispatchedCalls, [])
  assert.deepEqual(result.terminal, {
    kind: "error",
    code: "stream_incomplete",
  })

  return result
})

recordCase("unknown internal event is quarantined", async () => {
  const result = consumeResponseEvents([
    {
      type: "connector.internal.partial",
      payload: "synthetic-sensitive-value",
    },
    { type: "response.completed" },
  ])

  assert.equal(result.assistantText, "")
  assert.deepEqual(result.dispatchedCalls, [])
  assert.deepEqual(result.errors, [
    {
      code: "unsupported_event",
      eventType: "connector.internal.partial",
    },
  ])
  assert.deepEqual(result.terminal, {
    kind: "error",
    code: "unsupported_event",
  })
  assert.equal(JSON.stringify(result).includes("synthetic-sensitive-value"), false)

  return result
})

recordCase("completed call dispatches exactly once", async () => {
  const result = consumeResponseEvents([
    {
      type: "function_call.arguments.delta",
      callId: "call-2",
      delta: "{\"query\":",
    },
    {
      type: "function_call.arguments.delta",
      callId: "call-2",
      delta: "\"status\"}",
    },
    {
      type: "function_call.completed",
      callId: "call-2",
      name: "search",
    },
    {
      type: "function_call.completed",
      callId: "call-2",
      name: "search",
    },
    { type: "response.completed" },
  ])

  assert.equal(result.assistantText, "")
  assert.deepEqual(result.dispatchedCalls, [
    {
      callId: "call-2",
      name: "search",
      arguments: "{\"query\":\"status\"}",
    },
  ])
  assert.equal(result.errors[0]?.code, "duplicate_call_completion")

  return result
})

recordCase("cooperative runtime explicitly acknowledges cancellation", async () => {
  const receipt = await superviseRuntime(
    signal =>
      new Promise(resolve => {
        signal.addEventListener(
          "abort",
          () => resolve(acknowledgeCancellation()),
          { once: true },
        )
      }),
  )

  assert.deepEqual(receipt, {
    kind: "cancelled",
    code: "runtime_acknowledged_cancellation",
  })

  return receipt
})

recordCase("natural late completion does not become cancelled", async () => {
  const receipt = await superviseRuntime(
    () => delay(40).then(() => "natural-success"),
    { timeoutMs: 10, cancellationGraceMs: 100 },
  )

  assert.deepEqual(receipt, {
    kind: "settled_after_cancel_request",
    code: "cancellation_causality_unconfirmed",
  })

  return receipt
})

recordCase("late failure stays causal-unknown and content-minimized", async () => {
  const secretShapedValue = "sk-proj-fieldwork-secret-shaped-value"
  const receipt = await superviseRuntime(
    () =>
      delay(40).then(() => {
        throw new Error(`provider failure ${secretShapedValue}`)
      }),
    { timeoutMs: 10, cancellationGraceMs: 100 },
  )

  assert.deepEqual(receipt, {
    kind: "failed_after_cancel_request",
    code: "cancellation_causality_unconfirmed",
    errorType: "Error",
  })
  assert.equal(JSON.stringify(receipt).includes(secretShapedValue), false)

  return receipt
})

recordCase("non-settling runtime returns bounded outcome-unknown", async () => {
  const startedAt = Date.now()
  const receipt = await superviseRuntime(() => new Promise(() => {}))
  const elapsedMs = Date.now() - startedAt

  assert.deepEqual(receipt, {
    kind: "outcome_unknown",
    code: "runtime_did_not_settle_after_cancel_request",
  })
  assert.ok(elapsedMs < 1000, `expected bounded settlement, got ${elapsedMs} ms`)

  return { receipt, elapsedMs }
})

recordCase("late completion cannot rewrite emitted terminal receipt", async () => {
  let finishRuntime
  const runtime = new Promise(resolve => {
    finishRuntime = resolve
  })

  const receipt = await superviseRuntime(() => runtime)
  const serializedReceipt = JSON.stringify(receipt)

  finishRuntime("late-success")
  await delay(10)

  assert.equal(JSON.stringify(receipt), serializedReceipt)
  assert.deepEqual(receipt, {
    kind: "outcome_unknown",
    code: "runtime_did_not_settle_after_cancel_request",
  })
  assert.equal(Object.isFrozen(receipt), true)

  return receipt
})

recordCase("failed-control diagnostics omit source text", async () => {
  const secretShapedValue = "ghp_fieldwork_secret_shaped_value"
  const diagnostic = minimizedControlFailure(
    new Error(`assertion contained ${secretShapedValue}`),
  )

  assert.deepEqual(diagnostic, {
    code: "control_failed",
    errorType: "Error",
  })
  assert.equal(JSON.stringify(diagnostic).includes(secretShapedValue), false)

  return diagnostic
})

const results = []

for (const testCase of cases) {
  try {
    results.push({
      name: testCase.name,
      status: "passed",
      detail: await testCase.run(),
    })
  } catch (error) {
    const diagnostic = minimizedControlFailure(error)
    results.push({
      name: testCase.name,
      status: "failed",
      diagnostic,
    })
    process.stderr.write(`${testCase.name}: ${diagnostic.code}\n`)
  }
}

const report = {
  schemaVersion: 2,
  evidenceClass: "model-executed",
  claimLimit:
    "Synthetic contract model only. It does not execute the ChatGPT host, connector runtime, mobile client, or public Codex source.",
  node: process.version,
  cases: results,
}

const output = `${JSON.stringify(report, null, 2)}\n`
process.stdout.write(output)

if (process.env.RESULTS_DIR) {
  await fs.mkdir(process.env.RESULTS_DIR, { recursive: true })
  await fs.writeFile(
    path.join(process.env.RESULTS_DIR, "boundary-matrix.json"),
    output,
  )
}

if (results.some(result => result.status !== "passed")) {
  process.exitCode = 1
}
