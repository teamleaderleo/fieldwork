import { afterEach, describe, expect, it } from "vitest";
import fs from "fs/promises";
import os from "os";
import path from "path";

import {
  setAllowedDirectories,
  validatePath,
  writeFileContent,
} from "../lib.js";

async function exists(target: string): Promise<boolean> {
  try {
    await fs.lstat(target);
    return true;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return false;
    throw error;
  }
}

async function fixture(): Promise<{
  root: string;
  allowed: string;
  outside: string;
}> {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "fieldwork-fs-authority-"));
  const allowed = path.join(root, "allowed");
  const outside = path.join(root, "outside");
  await fs.mkdir(allowed);
  await fs.mkdir(outside);
  setAllowedDirectories([await fs.realpath(allowed)]);
  return { root, allowed, outside };
}

afterEach(() => {
  setAllowedDirectories([]);
});

describe("Fieldwork pathname authority after validation", () => {
  it("writes inside the allowed root while the validated parent remains stable", async () => {
    const { root, allowed, outside } = await fixture();
    try {
      const parent = path.join(allowed, "stable");
      const requested = path.join(parent, "created.txt");
      await fs.mkdir(parent);

      const validated = await validatePath(requested);
      await writeFileContent(validated, "inside");

      await expect(fs.readFile(requested, "utf8")).resolves.toBe("inside");
      expect(await exists(path.join(outside, "created.txt"))).toBe(false);
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });

  it("rejects a parent that already resolves outside the allowed root", async () => {
    const { root, allowed, outside } = await fixture();
    try {
      const linkedParent = path.join(allowed, "linked");
      await fs.symlink(outside, linkedParent, "dir");

      await expect(
        validatePath(path.join(linkedParent, "blocked.txt")),
      ).rejects.toThrow();
      expect(await exists(path.join(outside, "blocked.txt"))).toBe(false);
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });

  it("follows a parent symlink installed after validation", async () => {
    const { root, allowed, outside } = await fixture();
    try {
      const parent = path.join(allowed, "pivot");
      const parkedParent = path.join(allowed, "pivot-before-swap");
      const requested = path.join(parent, "escaped.txt");
      await fs.mkdir(parent);

      const validated = await validatePath(requested);

      await fs.rename(parent, parkedParent);
      await fs.symlink(outside, parent, "dir");
      await writeFileContent(validated, "outside-after-validation");

      await expect(
        fs.readFile(path.join(outside, "escaped.txt"), "utf8"),
      ).resolves.toBe("outside-after-validation");
      expect(await exists(path.join(parkedParent, "escaped.txt"))).toBe(false);
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });
});
