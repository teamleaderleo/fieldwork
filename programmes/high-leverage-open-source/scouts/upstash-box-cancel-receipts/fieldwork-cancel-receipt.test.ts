import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Run } from "../client.js";
import { createTestBox, mockResponse } from "./helpers.js";

describe("Fieldwork cancellation receipt characterization", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => vi.restoreAllMocks());

  it("reports cancelled after the remote cancellation request fails", async () => {
    const { box, fetchMock } = await createTestBox();
    fetchMock.mockResolvedValueOnce(mockResponse({ error: "cancel unavailable" }, 500));

    const controller = new AbortController();
    const run = new Run(box, "agent", "run-1");
    Run._update(run, { abortController: controller });

    await expect(run.cancel()).resolves.toBeUndefined();

    expect(controller.signal.aborted).toBe(true);
    expect(run.status).toBe("cancelled");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("sends duplicate remote cancellation requests for concurrent callers", async () => {
    const { box, fetchMock } = await createTestBox();
    fetchMock.mockResolvedValue(mockResponse({ error: "cancel unavailable" }, 503));

    const run = new Run(box, "command", "run-2");
    await Promise.all([run.cancel(), run.cancel()]);

    // One initial Box.get() request plus one cancellation request per caller.
    expect(fetchMock).toHaveBeenCalledTimes(3);
    expect(run.status).toBe("cancelled");
  });

  it("allows a later server event to replace the local cancelled status", async () => {
    const { box, fetchMock } = await createTestBox();
    fetchMock.mockResolvedValueOnce(mockResponse({ error: "cancel unavailable" }, 500));

    const run = new Run(box, "code", "run-3");
    await run.cancel();
    expect(run.status).toBe("cancelled");

    Run._update(run, { status: "completed", result: "natural completion" });
    expect(run.status).toBe("completed");
    expect(run.result).toBe("natural completion");
  });

  it.fails("repair control: request failure must not claim confirmed cancellation", async () => {
    const { box, fetchMock } = await createTestBox();
    fetchMock.mockResolvedValueOnce(mockResponse({ error: "cancel unavailable" }, 500));

    const run = new Run(box, "agent", "run-4");
    await run.cancel();

    // Selected receipt families may use `running`, `cancelling`, or an explicit
    // outcome-unknown receipt. The current terminal `cancelled` classification
    // is deliberately incompatible with this reversing control.
    expect(run.status).toBe("running");
  });

  it.fails("repair control: concurrent callers must share one cancellation operation", async () => {
    const { box, fetchMock } = await createTestBox();
    fetchMock.mockResolvedValue(mockResponse({}, 200));

    const run = new Run(box, "agent", "run-5");
    await Promise.all([run.cancel(), run.cancel()]);

    // One initial Box.get() request plus one shared cancellation request.
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
