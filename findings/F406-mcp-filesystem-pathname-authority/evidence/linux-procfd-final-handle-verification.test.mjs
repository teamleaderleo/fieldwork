import assert from 'node:assert/strict';
import { constants } from 'node:fs';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import test from 'node:test';

const DIRECTORY_FLAGS =
  constants.O_RDONLY | constants.O_DIRECTORY | constants.O_NOFOLLOW;

function stripDeletedSuffix(value) {
  return value.endsWith(' (deleted)')
    ? value.slice(0, -' (deleted)'.length)
    : value;
}

function isWithin(candidate, root) {
  const normalizedCandidate = path.resolve(stripDeletedSuffix(candidate));
  const normalizedRoot = path.resolve(stripDeletedSuffix(root));
  return normalizedCandidate === normalizedRoot ||
    normalizedCandidate.startsWith(`${normalizedRoot}${path.sep}`);
}

async function descriptorPath(handle, procFdRoot = '/proc/self/fd') {
  return fs.realpath(path.join(procFdRoot, String(handle.fd)));
}

async function openFinalFollowingSymlink(parentHandle, name, procFdRoot = '/proc/self/fd') {
  assert.equal(name.includes('/'), false);
  assert.equal(name.includes('\\'), false);
  return fs.open(
    path.join(procFdRoot, String(parentHandle.fd), name),
    constants.O_RDONLY,
  );
}

async function verifyOpenedHandleBeneathRoot(
  rootHandle,
  openedHandle,
  procFdRoot = '/proc/self/fd',
) {
  const [rootPath, openedPath] = await Promise.all([
    descriptorPath(rootHandle, procFdRoot),
    descriptorPath(openedHandle, procFdRoot),
  ]);
  if (!isWithin(openedPath, rootPath)) {
    throw new Error(
      `Opened descriptor escaped retained root: ${openedPath} outside ${rootPath}`,
    );
  }
  return { rootPath, openedPath };
}

async function fixture() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'fieldwork-procfd-final-'));
  const allowed = path.join(root, 'allowed');
  const outside = path.join(root, 'outside');
  await fs.mkdir(allowed);
  await fs.mkdir(outside);
  await fs.writeFile(path.join(allowed, 'inside.txt'), 'inside-value');
  await fs.writeFile(path.join(outside, 'outside.txt'), 'outside-value');
  return { root, allowed, outside };
}

test('an inside final symlink is verified and read through the stable opened handle', async () => {
  const state = await fixture();
  let rootHandle;
  let fileHandle;
  try {
    await fs.symlink('inside.txt', path.join(state.allowed, 'link.txt'));
    rootHandle = await fs.open(state.allowed, DIRECTORY_FLAGS);
    fileHandle = await openFinalFollowingSymlink(rootHandle, 'link.txt');
    await verifyOpenedHandleBeneathRoot(rootHandle, fileHandle);
    assert.equal(await fileHandle.readFile('utf8'), 'inside-value');
  } finally {
    await fileHandle?.close();
    await rootHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});

test('an outside final symlink is rejected before content is read', async () => {
  const state = await fixture();
  let rootHandle;
  let fileHandle;
  try {
    await fs.symlink(
      path.join(state.outside, 'outside.txt'),
      path.join(state.allowed, 'link.txt'),
    );
    rootHandle = await fs.open(state.allowed, DIRECTORY_FLAGS);
    fileHandle = await openFinalFollowingSymlink(rootHandle, 'link.txt');
    await assert.rejects(
      verifyOpenedHandleBeneathRoot(rootHandle, fileHandle),
      /escaped retained root/,
    );
  } finally {
    await fileHandle?.close();
    await rootHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});

test('swapping an admitted inside link to outside before open is rejected', async () => {
  const state = await fixture();
  let rootHandle;
  let fileHandle;
  try {
    const link = path.join(state.allowed, 'link.txt');
    await fs.symlink('inside.txt', link);
    rootHandle = await fs.open(state.allowed, DIRECTORY_FLAGS);

    await fs.unlink(link);
    await fs.symlink(path.join(state.outside, 'outside.txt'), link);

    fileHandle = await openFinalFollowingSymlink(rootHandle, 'link.txt');
    await assert.rejects(
      verifyOpenedHandleBeneathRoot(rootHandle, fileHandle),
      /escaped retained root/,
    );
  } finally {
    await fileHandle?.close();
    await rootHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});

test('swapping the link after open cannot redirect the stable descriptor', async () => {
  const state = await fixture();
  let rootHandle;
  let fileHandle;
  try {
    const link = path.join(state.allowed, 'link.txt');
    await fs.symlink('inside.txt', link);
    rootHandle = await fs.open(state.allowed, DIRECTORY_FLAGS);
    fileHandle = await openFinalFollowingSymlink(rootHandle, 'link.txt');

    await fs.unlink(link);
    await fs.symlink(path.join(state.outside, 'outside.txt'), link);

    await verifyOpenedHandleBeneathRoot(rootHandle, fileHandle);
    assert.equal(await fileHandle.readFile('utf8'), 'inside-value');
  } finally {
    await fileHandle?.close();
    await rootHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});

test('visible allowed-root replacement does not invalidate retained-root verification', async () => {
  const state = await fixture();
  let rootHandle;
  let fileHandle;
  try {
    await fs.symlink('inside.txt', path.join(state.allowed, 'link.txt'));
    rootHandle = await fs.open(state.allowed, DIRECTORY_FLAGS);

    const parkedAllowed = path.join(state.root, 'allowed-before-swap');
    await fs.rename(state.allowed, parkedAllowed);
    await fs.symlink(state.outside, state.allowed, 'dir');

    fileHandle = await openFinalFollowingSymlink(rootHandle, 'link.txt');
    const verified = await verifyOpenedHandleBeneathRoot(rootHandle, fileHandle);
    assert.equal(isWithin(verified.openedPath, verified.rootPath), true);
    assert.equal(await fileHandle.readFile('utf8'), 'inside-value');
  } finally {
    await fileHandle?.close();
    await rootHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});

test('deleted retained roots fail verification closed even though an already-open file remains readable', async () => {
  const state = await fixture();
  let rootHandle;
  let fileHandle;
  try {
    rootHandle = await fs.open(state.allowed, DIRECTORY_FLAGS);
    fileHandle = await openFinalFollowingSymlink(rootHandle, 'inside.txt');

    await fs.unlink(path.join(state.allowed, 'inside.txt'));
    await fs.rmdir(state.allowed);

    await assert.rejects(
      verifyOpenedHandleBeneathRoot(rootHandle, fileHandle),
      error => error?.code === 'ENOENT',
    );
    assert.equal(await fileHandle.readFile('utf8'), 'inside-value');
  } finally {
    await fileHandle?.close();
    await rootHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});
