import { execFile } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

if (process.platform === "win32") {
  console.error("This discriminator uses SIGUSR1 and requires a POSIX platform.");
  process.exit(2);
}

const dir = mkdtempSync(join(tmpdir(), "fieldwork-bun-execfile-timeout-"));
const receipt = join(dir, "signals.txt");

const childSource = String.raw`
  const { appendFileSync, writeFileSync } = require("node:fs");
  const receipt = process.argv[1];
  writeFileSync(receipt, "");
  process.on("SIGUSR1", () => {
    appendFileSync(receipt, "x");
  });
  setInterval(() => {}, 1000);
`;

let child;
let callbackError = null;
let callbackStdout = "";
let callbackStderr = "";

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

    // The timeout signal is deliberately handled by the child, so ensure the
    // probe always reaches a terminal state after the observation window.
    const cleanup = setTimeout(() => {
      child.kill("SIGKILL");
    }, 1600);

    child.once("close", () => clearTimeout(cleanup));
  });

  let receiptText = null;
  try {
    receiptText = readFileSync(receipt, "utf8");
  } catch {
    // A missing receipt means the child never reached its ready write. Report
    // that directly so a slow-start harness failure cannot look like zero signals.
  }

  const result = {
    runtime: process.versions.bun ? `bun ${process.versions.bun}` : `node ${process.versions.node}`,
    signalCount: receiptText === null ? null : receiptText.length,
    receiptBytes: receiptText,
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

  const expected = process.env.EXPECT_SIGNALS;
  if (expected !== undefined) {
    const n = Number(expected);
    if (!Number.isInteger(n) || n < 0) {
      console.error(`EXPECT_SIGNALS must be a non-negative integer, got ${JSON.stringify(expected)}`);
      process.exitCode = 2;
    } else if (result.signalCount !== n) {
      console.error(`Expected ${n} SIGUSR1 deliveries, observed ${String(result.signalCount)}.`);
      process.exitCode = 1;
    }
  }
} finally {
  try {
    child?.kill("SIGKILL");
  } catch {}
  rmSync(dir, { recursive: true, force: true });
}
