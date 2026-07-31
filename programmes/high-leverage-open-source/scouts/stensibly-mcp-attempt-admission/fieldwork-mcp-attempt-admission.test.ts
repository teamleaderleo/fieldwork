import { describe, expect, test } from "bun:test";
import {
  createMcpAttemptObservation,
  projectMcpAttemptObservations,
  type McpAttemptObservationInput,
  type McpAttemptObservationV1,
} from "../src/mcp-attempt-observation.ts";

const manifestFingerprint = `sha256:${"a".repeat(64)}`;
const occurredAt = "2026-07-31T02:00:00.000Z";

function accepted(
  overrides: Partial<McpAttemptObservationInput> = {},
): McpAttemptObservationV1 {
  return createMcpAttemptObservation({
    attemptId: "attempt-490-fieldwork",
    requestId: "request-490-fieldwork",
    sessionClassification: "streamable_http_stateless",
    manifestFingerprint,
    transition: "request_accepted",
    occurredAt,
    settlement: "unsettled",
    delivery: "unknown",
    ...overrides,
  });
}

const secretShapedIds = [
  "attempt:github_pat_private",
  "request.ghp_private",
  "run:stn.tok_private",
  "trace:sk-proj-private",
  "grant-xoxb-private",
  "receipt:env://PRIVATE_TOKEN",
  "receipt:secret://github-token",
] as const;

describe("Fieldwork MCP attempt admission repair", () => {
  test("rejects out-of-range numeric-looking data without changing array length", () => {
    const history = [accepted()];
    Object.defineProperty(history, "4294967295", {
      enumerable: true,
      configurable: true,
      value: "unbound-content",
    });

    expect(history).toHaveLength(1);
    expect(() => projectMcpAttemptObservations(history)).toThrow(
      "MCP attempt observations contains unsupported fields",
    );
  });

  test("rejects out-of-range accessor without invoking it", () => {
    const history = [accepted()];
    let reads = 0;
    Object.defineProperty(history, "4294967295", {
      enumerable: true,
      configurable: true,
      get() {
        reads += 1;
        return "unbound-content";
      },
    });

    expect(() => projectMcpAttemptObservations(history)).toThrow(
      "MCP attempt observations contains unsupported fields",
    );
    expect(reads).toBe(0);
  });

  test("rejects symbol array fields with fixed prose and zero getter invocation", () => {
    const history = [accepted()];
    const privateSymbol = Symbol("github_pat_private");
    let reads = 0;
    Object.defineProperty(history, privateSymbol, {
      enumerable: true,
      configurable: true,
      get() {
        reads += 1;
        return "private";
      },
    });

    let message = "";
    try {
      projectMcpAttemptObservations(history);
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
    }
    expect(message).toBe(
      "MCP attempt observations contains unsupported fields",
    );
    expect(message).not.toContain("github_pat_private");
    expect(reads).toBe(0);
  });

  test("rejects namespaced credentials during creation", () => {
    for (const identity of secretShapedIds) {
      expect(() => accepted({ attemptId: identity })).toThrow(
        "MCP attempt ID is invalid",
      );
      expect(() => accepted({ requestId: identity })).toThrow(
        "MCP request ID is invalid",
      );
    }
  });

  test("rejects namespaced credentials during re-admission", () => {
    const observation = accepted();
    for (const identity of secretShapedIds) {
      expect(() => projectMcpAttemptObservations([{
        ...observation,
        attemptId: identity,
      }])).toThrow("MCP attempt ID is invalid");
      expect(() => projectMcpAttemptObservations([{
        ...observation,
        requestId: identity,
      }])).toThrow("MCP request ID is invalid");
    }
  });

  test("unknown credential-shaped field uses fixed prose without getter invocation", () => {
    let reads = 0;
    const input = {
      attemptId: "attempt-490-fieldwork",
      requestId: "request-490-fieldwork",
      sessionClassification: "streamable_http_stateless",
      manifestFingerprint,
      transition: "request_accepted",
      occurredAt,
      settlement: "unsettled",
      delivery: "unknown",
    } as unknown as McpAttemptObservationInput;
    Object.defineProperty(input, "github_pat_private_field", {
      enumerable: true,
      configurable: true,
      get() {
        reads += 1;
        return "private";
      },
    });

    let message = "";
    try {
      createMcpAttemptObservation(input);
    } catch (error) {
      message = error instanceof Error ? error.message : String(error);
    }
    expect(message).toBe(
      "MCP attempt observation input contains unsupported fields",
    );
    expect(message).not.toContain("github_pat_private_field");
    expect(reads).toBe(0);
  });

  test("failure stage vocabulary is derived from the exhaustive window table", async () => {
    const source = await Bun.file(
      new URL("../src/mcp-attempt-observation.ts", import.meta.url),
    ).text();
    expect(source).toContain("const failureStages = Object.freeze(");
    expect(source).toContain("Object.keys(failureStageWindows)");
    expect(source).not.toContain("const failureStages = [");
    expect(source).not.toContain("export const mcpAttemptFailureStages");
  });
});
