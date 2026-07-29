import assert from 'node:assert/strict';
import process from 'node:process';
import {setTimeout as delay} from 'node:timers/promises';
import {execa} from 'execa';

const isAlive = pid => {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
};

const waitFor = async (predicate, description, timeoutMs = 5000) => {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (predicate()) return;
    await delay(25);
  }
  throw new Error(`Timed out waiting for ${description}`);
};

const child = execa(
  process.execPath,
  ['-e', 'setInterval(() => {}, 1000)'],
  {
    killDescendants: true,
    reject: false,
    stdio: 'ignore',
  },
);

const pid = child.pid;
assert.equal(typeof pid, 'number');
await waitFor(() => isAlive(pid), 'child to become live');

const aliveBefore = isAlive(pid);
const killReturn = child.kill(0);

// The Windows adapter launches taskkill asynchronously. Give it enough time to
// terminate the process while keeping the Unix control bounded.
await delay(1500);
const aliveAfter = isAlive(pid);

const result = {
  platform: process.platform,
  node: process.version,
  execa: '10.0.0',
  pid,
  aliveBefore,
  killReturn,
  aliveAfter,
  observed: aliveAfter ? 'non_destructive_check' : 'process_terminated',
};

try {
  assert.equal(aliveBefore, true);
  assert.equal(killReturn, true);
  if (process.platform === 'win32') {
    assert.equal(
      aliveAfter,
      false,
      'current Execa 10.0.0 Windows adapter is expected to terminate on kill(0)',
    );
  } else {
    assert.equal(
      aliveAfter,
      true,
      'signal 0 must remain non-destructive on Unix process groups',
    );
  }
} finally {
  if (isAlive(pid)) {
    child.kill('SIGKILL');
  }
  await Promise.race([child, delay(5000)]);
}

console.log(JSON.stringify(result));
