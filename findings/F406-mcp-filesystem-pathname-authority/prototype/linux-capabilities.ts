import { randomBytes } from 'crypto';
import { constants } from 'fs';
import fs, { type FileHandle } from 'fs/promises';
import path from 'path';

type RootCapability = {
  configuredPath: string;
  handle: FileHandle;
};

function assertComponent(component: string): void {
  if (
    !component ||
    component === '.' ||
    component === '..' ||
    component.includes('/') ||
    component.includes('\\')
  ) {
    throw new Error(`Invalid path component: ${component}`);
  }
}

function isWithinRoot(candidate: string, root: string): boolean {
  return candidate === root || candidate.startsWith(`${root}${path.sep}`);
}

async function closeHandles(handles: FileHandle[]): Promise<void> {
  let firstError: unknown;
  for (const handle of [...handles].reverse()) {
    try {
      await handle.close();
    } catch (error) {
      firstError ??= error;
    }
  }
  if (firstError)
    throw firstError;
}

export class LinuxParentCapability {
  private closed = false;

  constructor(
    private readonly parentHandle: FileHandle,
    private readonly finalName: string,
    private readonly ownedTraversalHandles: FileHandle[],
    private readonly procFdRoot: string,
  ) {}

  private assertOpen(): void {
    if (this.closed)
      throw new Error('Filesystem parent capability is closed');
  }

  private entryPath(name: string = this.finalName): string {
    this.assertOpen();
    assertComponent(name);
    return path.join(this.procFdRoot, String(this.parentHandle.fd), name);
  }

  async readFile(encoding: BufferEncoding = 'utf-8'): Promise<string> {
    const handle = await fs.open(
      this.entryPath(),
      constants.O_RDONLY | constants.O_NOFOLLOW,
    );
    try {
      return await handle.readFile({ encoding });
    } finally {
      await handle.close();
    }
  }

  async writeFile(content: string): Promise<void> {
    const finalPath = this.entryPath();
    try {
      const created = await fs.open(
        finalPath,
        constants.O_WRONLY |
          constants.O_CREAT |
          constants.O_EXCL |
          constants.O_NOFOLLOW,
        0o666,
      );
      try {
        await created.writeFile(content, 'utf-8');
      } finally {
        await created.close();
      }
      return;
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code !== 'EEXIST')
        throw error;
    }

    const temporaryName = `.${this.finalName}.${randomBytes(16).toString('hex')}.tmp`;
    const temporaryPath = this.entryPath(temporaryName);
    let temporary: FileHandle | undefined;
    try {
      temporary = await fs.open(
        temporaryPath,
        constants.O_WRONLY |
          constants.O_CREAT |
          constants.O_EXCL |
          constants.O_NOFOLLOW,
        0o666,
      );
      await temporary.writeFile(content, 'utf-8');
      await temporary.close();
      temporary = undefined;
      await fs.rename(temporaryPath, finalPath);
    } catch (error) {
      await temporary?.close().catch(() => {});
      await fs.unlink(temporaryPath).catch(() => {});
      throw error;
    }
  }

  async renameTo(destination: LinuxParentCapability): Promise<void> {
    await fs.rename(this.entryPath(), destination.entryPath());
  }

  async close(): Promise<void> {
    if (this.closed)
      return;
    this.closed = true;
    await closeHandles(this.ownedTraversalHandles);
  }
}

export class LinuxFilesystemCapabilities {
  private closed = false;

  private constructor(
    private readonly roots: RootCapability[],
    private readonly procFdRoot: string,
  ) {}

  static async create(
    allowedDirectories: string[],
    procFdRoot: string = '/proc/self/fd',
  ): Promise<LinuxFilesystemCapabilities> {
    if (process.platform !== 'linux')
      throw new Error('Linux filesystem capabilities require Linux');
    await fs.access(procFdRoot);

    const roots: RootCapability[] = [];
    try {
      const realRoots = [...new Set(
        await Promise.all(
          allowedDirectories.map(directory => fs.realpath(path.resolve(directory))),
        ),
      )].sort((left, right) => right.length - left.length);

      for (const configuredPath of realRoots) {
        const handle = await fs.open(
          configuredPath,
          constants.O_RDONLY | constants.O_DIRECTORY | constants.O_NOFOLLOW,
        );
        const openedPath = await fs.realpath(
          path.join(procFdRoot, String(handle.fd)),
        );
        if (path.resolve(openedPath) !== configuredPath) {
          await handle.close();
          throw new Error(
            `Allowed root changed while opening: ${configuredPath} -> ${openedPath}`,
          );
        }
        roots.push({ configuredPath, handle });
      }

      if (!roots.length)
        throw new Error('At least one allowed directory is required');
      return new LinuxFilesystemCapabilities(roots, procFdRoot);
    } catch (error) {
      await closeHandles(roots.map(root => root.handle)).catch(() => {});
      throw error;
    }
  }

  private assertOpen(): void {
    if (this.closed)
      throw new Error('Filesystem capabilities are closed');
  }

  async openParent(requestedPath: string): Promise<LinuxParentCapability> {
    this.assertOpen();
    const absolute = path.resolve(requestedPath);
    const root = this.roots.find(candidate =>
      isWithinRoot(absolute, candidate.configuredPath),
    );
    if (!root)
      throw new Error(`Access denied - path outside retained allowed roots: ${absolute}`);

    const relative = path.relative(root.configuredPath, absolute);
    const components = relative.split(path.sep);
    if (!relative || !components.length)
      throw new Error('Operation requires a final path component');
    components.forEach(assertComponent);

    const finalName = components.pop()!;
    const opened: FileHandle[] = [];
    let current = root.handle;
    try {
      for (const component of components) {
        const next = await fs.open(
          path.join(this.procFdRoot, String(current.fd), component),
          constants.O_RDONLY |
            constants.O_DIRECTORY |
            constants.O_NOFOLLOW,
        );
        opened.push(next);
        current = next;
      }
      return new LinuxParentCapability(
        current,
        finalName,
        opened,
        this.procFdRoot,
      );
    } catch (error) {
      await closeHandles(opened).catch(() => {});
      throw error;
    }
  }

  async close(): Promise<void> {
    if (this.closed)
      return;
    this.closed = true;
    await closeHandles(this.roots.map(root => root.handle));
  }
}
