import { execFile } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

if (process.platform === "win32") {
  console.error("This discriminator uses SIGUSR1 and requires a POSIX platform.");
  process.exit(2);
}

const dir = mkdtempSync(join(tmpdir(), "fieldwork-bun-execfile-timeout-"));
const receipt = join(dir, "signals.bin");
const start = performance.now();

const childSource = String.raw`
  const { appendFileSync, writeFileSync } = require("node:fs");
  const receipt = process.argv[1];
  writeFileSync(receipt, "");
  process.on("SIGUSR1", () => appendFileSync(receipt, "1"));
  setInterval(() => {}, 1000);
`;

let child;
let callbackError = null;
let callbackStdout = "";
let callbackStderr = "";
const killCalls = [];

try {
  await new Promise(resolve => {
    child = execFile(
      process.execPath,
      ["-e", childSource, receipt],
      {
        timeout: 1000,
        killSignal: "SIGUSR1",
        encoding: "utf8",
      },
      (error, stdout, stderr) => {
        callbackError = error;
        callbackStdout = stdout ?? "";
        callbackStderr = stderr ?? "";
        resolve();
      },
    );

    // Both Node and Bun implement timeout by calling the public ChildProcess
    // kill() method. Wrap that method after execFile() returns so the probe can
    // count timeout attempts even if the OS coalesces identical pending
    // standard signals before the child runs its SIGUSR1 handler.
    const originalKill = child.kill.bind(child);
    child.kill = signal => {
      killCalls.push({
        signal: signal ?? "SIGTERM",
        atMs: Math.round(performance.now() - start),
      });
      return originalKill(signal);
    };

    // Use the original method so probe cleanup is excluded from killCallCount.
    const cleanup = setTimeout(() => originalKill("SIGKILL"), 1600);
    child.once("close", () => clearTimeout(cleanup));
  });

  let signalCount = null;
  try {
    signalCount = readFileSync(receipt).length;
  } catch {
    // A missing receipt means the child never reached its ready write. Keep
    // this distinct from a valid zero-signal observation.
  }

  const result = {
    runtime: process.versions.bun ? `bun ${process.versions.bun}` : `node ${process.versions.node}`,
    killCallCount: killCalls.length,
    killCalls,
    signalCount,
    callbackError: callbackError
      ? {
          name: callbackError.name,
          code: callbackError.code,
          signal: callbackError.signal,
          killed: callbackError.killed,
        }
      : null,
    callbackStdout,
    callbackStderr,
  };

  console.log(JSON.stringify(result, null, 2));

  for (const [envName, actual] of [
    ["EXPECT_KILL_CALLS", result.killCallCount],
    ["EXPECT_SIGNALS", result.signalCount],
  ]) {
    const expected = process.env[envName];
    if (expected === undefined) continue;

    const n = Number(expected);
    if (!Number.isInteger(n) || n < 0) {
      console.error(`${envName} must be a non-negative integer, got ${JSON.stringify(expected)}`);
      process.exitCode = 2;
    } else if (actual !== n) {
      console.error(`${envName}: expected ${n}, observed ${String(actual)}.`);
      process.exitCode = 1;
    }
  }
} finally {
  try {
    child?.kill("SIGKILL");
  } catch {}
  rmSync(dir, { recursive: true, force: true });
}
