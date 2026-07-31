#!/usr/bin/env python3
"""Apply the bounded MCP attempt admission/privacy repair to exact Stensibly source."""

from __future__ import annotations

from pathlib import Path
import sys


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one exact source block, observed {count}")
    return text.replace(old, new, 1)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: apply_repair.py <stensibly-root>")

    root = Path(sys.argv[1]).resolve()
    source_path = root / "src" / "mcp-attempt-observation.ts"
    test_path = root / "test" / "mcp-attempt-observation.test.ts"

    source = source_path.read_text(encoding="utf-8")
    source = replace_once(
        source,
        '''const failureStages = [
  "method_validation",
  "origin_validation",
  "host_validation",
  "token_authority",
  "authentication",
  "payload_parse",
  "authorization",
  "server_construction",
  "transport_connection",
  "request_execution",
  "request_validation",
] as const satisfies readonly McpFailureStage[];
''',
        "",
        "remove duplicated failure-stage list",
    )
    source = replace_once(
        source,
        '''} as const satisfies Record<McpFailureStage, McpFailureStageWindow>;
const singletonTransitions = new Set<McpAttemptTransitionKind>(
''',
        '''} as const satisfies Record<McpFailureStage, McpFailureStageWindow>;
export const mcpAttemptFailureStages = Object.freeze(
  Object.keys(failureStageWindows) as McpFailureStage[],
);
const singletonTransitions = new Set<McpAttemptTransitionKind>(
''',
        "derive failure-stage admission",
    )
    source = replace_once(
        source,
        '''const credentialPattern = /^(?:stn\\.tok_|github_pat_|gh[pousr]_|sk-(?:proj-)?)/iu;
''',
        '''const secretShapedIdentityPattern = /(?:^|[._:/-])(?:(?:env|secret):\\/\\/|github_pat_|gh[pousr]_|stn\\.tok_|sk-|xox[baprs]-)/iu;
''',
        "replace credential identity detector",
    )
    source = replace_once(
        source,
        '''      optionalEnumValue(record.failureStage, "MCP failure stage", failureStages),
''',
        '''      optionalEnumValue(
        record.failureStage,
        "MCP failure stage",
        mcpAttemptFailureStages,
      ),
''',
        "bind failure-stage admission",
    )
    source = replace_once(
        source,
        '''  const descriptors = Object.getOwnPropertyDescriptors(value);
  for (const key of Reflect.ownKeys(value)) {
    if (typeof key !== "string") {
      throw new TypeError(`${label} cannot contain symbol fields`);
    }
    if (key !== "length" && !/^(0|[1-9][0-9]*)$/u.test(key)) {
      throw new TypeError(`${label} contains unsupported field ${key}`);
    }
  }
  const result: unknown[] = [];
''',
        '''  const descriptors = Object.getOwnPropertyDescriptors(value);
  const allowedKeys = new Set<string>(["length"]);
  for (let index = 0; index < length; index += 1) {
    allowedKeys.add(String(index));
  }
  for (const key of Reflect.ownKeys(value)) {
    if (typeof key !== "string" || !allowedKeys.has(key)) {
      throw new TypeError(`${label} contains unsupported fields`);
    }
  }
  const result: unknown[] = [];
''',
        "close dense-array key admission",
    )
    source = replace_once(
        source,
        '''  for (const key of Reflect.ownKeys(value)) {
    if (typeof key !== "string") {
      throw new TypeError(`${label} cannot contain symbol fields`);
    }
    if (!allowedKeys.includes(key)) {
      throw new TypeError(`${label} contains unknown field ${key}`);
    }
    const descriptor = descriptors[key]!;
''',
        '''  for (const key of Reflect.ownKeys(value)) {
    if (typeof key !== "string" || !allowedKeys.includes(key)) {
      throw new TypeError(`${label} contains unsupported fields`);
    }
    const descriptor = descriptors[key]!;
''',
        "fix record-field diagnostics",
    )
    source = replace_once(
        source,
        '''    || credentialPattern.test(value)
''',
        '''    || secretShapedIdentityPattern.test(value)
''',
        "bind namespaced secret detector",
    )
    source_path.write_text(source, encoding="utf-8")

    tests = test_path.read_text(encoding="utf-8")
    tests = replace_once(
        tests,
        ''').toThrow("unknown field token");
''',
        ''').toThrow("contains unsupported fields");
''',
        "update fixed unknown-field expectation",
    )
    test_path.write_text(tests, encoding="utf-8")


if __name__ == "__main__":
    main()
