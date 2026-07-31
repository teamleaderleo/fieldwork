import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { Run } from "../client.js";
import { createTestBox, mockResponse } from "./helpers.js";

function deferred<T>(): {
  promise: Promise<T>;
  resolve: (value: T) => void;
} {
  let resolve!: (value: T) => void;
  const promise = new Promise<T>((settle) => {
    resolve = settle;
  });
  return { promise, resolve };
}

describe("Fieldwork shared cancellation receipt repair", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => vi.restoreAllMocks());

  it("shares one accepted request and one immutable receipt", async () => {
    const { box, fetchMock } = await createTestBox();
    const response = deferred<Response>();
    fetchMock.mockReturnValueOnce(response.promise);

    const abortController = new AbortController();
    const run = new Run(box, "agent", "run-accepted");
    Run._update(run, { abortController });

    const first = run.requestCancel();
    const second = run.requestCancel();

    expect(first).toBe(second);
    await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(abortController.signal.aborted).toBe(true);
    expect(run.status).toBe("running");

    response.resolve(mockResponse({}));
    const [firstReceipt, secondReceipt] = await Promise.all([first, second]);

    expect(firstReceipt).toBe(secondReceipt);
    expect(firstReceipt).toEqual({
      requestState: "accepted",
      outcomeState: "unknown",
    });
    expect(Object.isFrozen(firstReceipt)).toBe(true);
    expect(run.status).toBe("running");

    const laterReceipt = await run.requestCancel();
    expect(laterReceipt).toBe(firstReceipt);
    expect(fetchMock).toHaveBeenCalledTimes(2);

    Run._update(run, { status: "completed", result: "natural completion" });
    expect(run.status).toBe("completed");
    expect(await run.requestCancel()).toBe(firstReceipt);
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("publishes fixed failure prose without claiming a terminal outcome", async () => {
    const { box, fetchMock } = await createTestBox();
    fetchMock.mockResolvedValueOnce(
      mockResponse({ error: "raw provider detail must not escape" }, 503),
    );

    const run = new Run(box, "command", "run-failed");
    const receipt = await run.requestCancel();

    expect(receipt).toEqual({
      requestState: "failed",
      outcomeState: "unknown",
      diagnostic: "cancellation request failed",
    });
    expect(JSON.stringify(receipt)).not.toContain("raw provider detail");
    expect(Object.isFrozen(receipt)).toBe(true);
    expect(run.status).toBe("running");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("preserves the legacy void return and shares its request", async () => {
    const { box, fetchMock } = await createTestBox();
    fetchMock.mockResolvedValueOnce(mockResponse({}));

    const run = new Run(box, "code", "run-legacy");
    const legacy = run.cancel();
    const receipt = run.requestCancel();

    await expect(legacy).resolves.toBeUndefined();
    await expect(receipt).resolves.toEqual({
      requestState: "accepted",
      outcomeState: "unknown",
    });
    expect(run.status).toBe("running");
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });
});
