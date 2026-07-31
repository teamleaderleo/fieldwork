import { afterEach, describe, expect, it } from 'vitest';
import fs from 'fs/promises';
import os from 'os';
import path from 'path';

import { LinuxFilesystemCapabilities } from '../linux-capabilities.js';

type Fixture = {
  root: string;
  allowed: string;
  outside: string;
};

const cleanupRoots = new Set<string>();

async function fixture(): Promise<Fixture> {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'fieldwork-linux-capability-'));
  cleanupRoots.add(root);
  const allowed = path.join(root, 'allowed');
  const outside = path.join(root, 'outside');
  await fs.mkdir(allowed);
  await fs.mkdir(outside);
  return { root, allowed, outside };
}

async function exists(target: string): Promise<boolean> {
  try {
    await fs.lstat(target);
    return true;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === 'ENOENT')
      return false;
    throw error;
  }
}

async function countFixtureDescriptors(root: string): Promise<number> {
  const entries = await fs.readdir('/proc/self/fd');
  let count = 0;
  for (const entry of entries) {
    try {
      const target = await fs.readlink(path.join('/proc/self/fd', entry));
      if (target.startsWith(root))
        count++;
    } catch {}
  }
  return count;
}

afterEach(async () => {
  for (const root of cleanupRoots)
    await fs.rm(root, { recursive: true, force: true });
  cleanupRoots.clear();
});

describe('Linux retained filesystem capabilities', () => {
  it('reads from the retained allowed root after its visible pathname is replaced', async () => {
    const { root, allowed, outside } = await fixture();
    const insideParent = path.join(allowed, 'nested');
    await fs.mkdir(insideParent);
    await fs.mkdir(path.join(outside, 'nested'));
    await fs.writeFile(path.join(insideParent, 'value.txt'), 'inside-value');
    await fs.writeFile(path.join(outside, 'nested', 'value.txt'), 'outside-value');

    const capabilities = await LinuxFilesystemCapabilities.create([allowed]);
    try {
      const parkedAllowed = path.join(root, 'allowed-before-swap');
      await fs.rename(allowed, parkedAllowed);
      await fs.symlink(outside, allowed, 'dir');

      const parent = await capabilities.openParent(
        path.join(allowed, 'nested', 'value.txt'),
      );
      try {
        await expect(parent.readFile()).resolves.toBe('inside-value');
      } finally {
        await parent.close();
      }
    } finally {
      await capabilities.close();
    }
  });

  it('creates through an acquired exact parent after the visible parent is replaced', async () => {
    const { allowed, outside } = await fixture();
    const parentPath = path.join(allowed, 'pivot', 'nested');
    await fs.mkdir(parentPath, { recursive: true });

    const capabilities = await LinuxFilesystemCapabilities.create([allowed]);
    try {
      const parent = await capabilities.openParent(
        path.join(parentPath, 'created.txt'),
      );
      try {
        const parkedParent = path.join(allowed, 'pivot', 'nested-before-swap');
        await fs.rename(parentPath, parkedParent);
        await fs.symlink(outside, parentPath, 'dir');

        await parent.writeFile('retained-create');
        await expect(
          fs.readFile(path.join(parkedParent, 'created.txt'), 'utf8'),
        ).resolves.toBe('retained-create');
        expect(await exists(path.join(outside, 'created.txt'))).toBe(false);
      } finally {
        await parent.close();
      }
    } finally {
      await capabilities.close();
    }
  });

  it('atomically replaces inside the retained parent rather than following a final symlink', async () => {
    const { allowed, outside } = await fixture();
    const parentPath = path.join(allowed, 'replace');
    await fs.mkdir(parentPath);
    await fs.writeFile(path.join(outside, 'outside.txt'), 'outside-original');
    await fs.symlink(
      path.join(outside, 'outside.txt'),
      path.join(parentPath, 'target.txt'),
    );

    const capabilities = await LinuxFilesystemCapabilities.create([allowed]);
    try {
      const parent = await capabilities.openParent(
        path.join(parentPath, 'target.txt'),
      );
      try {
        await parent.writeFile('inside-replacement');
        const replaced = await fs.lstat(path.join(parentPath, 'target.txt'));
        expect(replaced.isSymbolicLink()).toBe(false);
        await expect(
          fs.readFile(path.join(parentPath, 'target.txt'), 'utf8'),
        ).resolves.toBe('inside-replacement');
        await expect(
          fs.readFile(path.join(outside, 'outside.txt'), 'utf8'),
        ).resolves.toBe('outside-original');
      } finally {
        await parent.close();
      }
    } finally {
      await capabilities.close();
    }
  });

  it('moves between two retained parents after both visible parents are replaced', async () => {
    const { allowed, outside } = await fixture();
    const sourcePath = path.join(allowed, 'source');
    const destinationPath = path.join(allowed, 'destination');
    const outsideSource = path.join(outside, 'source');
    const outsideDestination = path.join(outside, 'destination');
    await fs.mkdir(sourcePath);
    await fs.mkdir(destinationPath);
    await fs.mkdir(outsideSource);
    await fs.mkdir(outsideDestination);
    await fs.writeFile(path.join(sourcePath, 'item.txt'), 'inside-item');

    const capabilities = await LinuxFilesystemCapabilities.create([allowed]);
    try {
      const source = await capabilities.openParent(
        path.join(sourcePath, 'item.txt'),
      );
      const destination = await capabilities.openParent(
        path.join(destinationPath, 'moved.txt'),
      );
      try {
        const parkedSource = path.join(allowed, 'source-before-swap');
        const parkedDestination = path.join(
          allowed,
          'destination-before-swap',
        );
        await fs.rename(sourcePath, parkedSource);
        await fs.rename(destinationPath, parkedDestination);
        await fs.symlink(outsideSource, sourcePath, 'dir');
        await fs.symlink(outsideDestination, destinationPath, 'dir');

        await source.renameTo(destination);
        expect(await exists(path.join(parkedSource, 'item.txt'))).toBe(false);
        await expect(
          fs.readFile(path.join(parkedDestination, 'moved.txt'), 'utf8'),
        ).resolves.toBe('inside-item');
        expect(await exists(path.join(outsideDestination, 'moved.txt'))).toBe(false);
      } finally {
        await destination.close();
        await source.close();
      }
    } finally {
      await capabilities.close();
    }
  });

  it('rejects an intermediate symlink and closes partial traversal handles', async () => {
    const { root, allowed, outside } = await fixture();
    const good = path.join(allowed, 'good');
    await fs.mkdir(good);
    await fs.symlink(outside, path.join(good, 'bad'), 'dir');

    const capabilities = await LinuxFilesystemCapabilities.create([allowed]);
    try {
      const before = await countFixtureDescriptors(root);
      for (let attempt = 0; attempt < 10; attempt++) {
        await expect(
          capabilities.openParent(path.join(good, 'bad', 'value.txt')),
        ).rejects.toMatchObject({ code: expect.stringMatching(/ELOOP|ENOTDIR/) });
      }
      const after = await countFixtureDescriptors(root);
      expect(after).toBe(before);
    } finally {
      await capabilities.close();
    }
  });

  it('fails closed without procfs and rejects use after closure', async () => {
    const { root, allowed } = await fixture();
    await expect(
      LinuxFilesystemCapabilities.create(
        [allowed],
        path.join(root, 'missing-proc-self-fd'),
      ),
    ).rejects.toMatchObject({ code: 'ENOENT' });

    const capabilities = await LinuxFilesystemCapabilities.create([allowed]);
    await capabilities.close();
    await expect(
      capabilities.openParent(path.join(allowed, 'value.txt')),
    ).rejects.toThrow('Filesystem capabilities are closed');
  });
});
