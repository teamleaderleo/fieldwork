import { afterEach, describe, expect, it } from "vitest";
import fs from "fs/promises";
import os from "os";
import path from "path";

import {
  applyFileEdits,
  setAllowedDirectories,
  validatePath,
} from "../lib.js";

type Fixture = {
  root: string;
  allowed: string;
  outside: string;
};

async function fixture(): Promise<Fixture> {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "fieldwork-fs-operations-"));
  const allowed = path.join(root, "allowed");
  const outside = path.join(root, "outside");
  await fs.mkdir(allowed);
  await fs.mkdir(outside);
  setAllowedDirectories([await fs.realpath(allowed)]);
  return { root, allowed, outside };
}

async function replaceParentWithOutsideSymlink(
  allowed: string,
  outside: string,
  name: string,
): Promise<string> {
  const parent = path.join(allowed, name);
  const parked = path.join(allowed, `${name}-before-swap`);
  await fs.rename(parent, parked);
  await fs.symlink(outside, parent, "dir");
  return parked;
}

async function exists(target: string): Promise<boolean> {
  try {
    await fs.lstat(target);
    return true;
  } catch (error) {
    if ((error as NodeJS.ErrnoException).code === "ENOENT") return false;
    throw error;
  }
}

afterEach(() => {
  setAllowedDirectories([]);
});

describe("Fieldwork operation authority after pathname validation", () => {
  it("redirects a validated read to outside content after an ancestor swap", async () => {
    const { root, allowed, outside } = await fixture();
    try {
      const parent = path.join(allowed, "read-pivot");
      await fs.mkdir(parent);
      await fs.writeFile(path.join(parent, "value.txt"), "inside-value");
      await fs.writeFile(path.join(outside, "value.txt"), "outside-value");

      const validated = await validatePath(path.join(parent, "value.txt"));
      const parked = await replaceParentWithOutsideSymlink(
        allowed,
        outside,
        "read-pivot",
      );

      await expect(fs.readFile(validated, "utf8")).resolves.toBe(
        "outside-value",
      );
      await expect(
        fs.readFile(path.join(parked, "value.txt"), "utf8"),
      ).resolves.toBe("inside-value");
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });

  it("redirects a validated edit to an outside file after an ancestor swap", async () => {
    const { root, allowed, outside } = await fixture();
    try {
      const parent = path.join(allowed, "edit-pivot");
      await fs.mkdir(parent);
      await fs.writeFile(path.join(parent, "note.txt"), "inside-original");
      await fs.writeFile(path.join(outside, "note.txt"), "outside-original");

      const validated = await validatePath(path.join(parent, "note.txt"));
      const parked = await replaceParentWithOutsideSymlink(
        allowed,
        outside,
        "edit-pivot",
      );

      await applyFileEdits(
        validated,
        [{ oldText: "outside-original", newText: "outside-edited" }],
        false,
      );

      await expect(
        fs.readFile(path.join(outside, "note.txt"), "utf8"),
      ).resolves.toBe("outside-edited");
      await expect(
        fs.readFile(path.join(parked, "note.txt"), "utf8"),
      ).resolves.toBe("inside-original");
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });

  it("redirects final directory creation after validating the missing child", async () => {
    const { root, allowed, outside } = await fixture();
    try {
      const parent = path.join(allowed, "mkdir-pivot");
      await fs.mkdir(parent);
      const requested = path.join(parent, "new");

      const validated = await validatePath(requested);
      const parked = await replaceParentWithOutsideSymlink(
        allowed,
        outside,
        "mkdir-pivot",
      );
      await fs.mkdir(validated, { recursive: true });

      expect(await exists(path.join(outside, "new"))).toBe(true);
      expect(await exists(path.join(parked, "new"))).toBe(false);
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });

  it("exports an allowed source through a swapped destination parent", async () => {
    const { root, allowed, outside } = await fixture();
    try {
      const source = path.join(allowed, "source.txt");
      const destinationParent = path.join(allowed, "destination-pivot");
      const destination = path.join(destinationParent, "exported.txt");
      await fs.writeFile(source, "inside-source");
      await fs.mkdir(destinationParent);

      const validatedSource = await validatePath(source);
      const validatedDestination = await validatePath(destination);
      const parked = await replaceParentWithOutsideSymlink(
        allowed,
        outside,
        "destination-pivot",
      );
      await fs.rename(validatedSource, validatedDestination);

      await expect(
        fs.readFile(path.join(outside, "exported.txt"), "utf8"),
      ).resolves.toBe("inside-source");
      expect(await exists(path.join(parked, "exported.txt"))).toBe(false);
      expect(await exists(source)).toBe(false);
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });

  it("imports an outside source through a swapped validated source parent", async () => {
    const { root, allowed, outside } = await fixture();
    try {
      const sourceParent = path.join(allowed, "source-pivot");
      const source = path.join(sourceParent, "import.txt");
      const destination = path.join(allowed, "imported.txt");
      await fs.mkdir(sourceParent);
      await fs.writeFile(source, "inside-source");
      await fs.writeFile(path.join(outside, "import.txt"), "outside-source");

      const validatedSource = await validatePath(source);
      const validatedDestination = await validatePath(destination);
      const parked = await replaceParentWithOutsideSymlink(
        allowed,
        outside,
        "source-pivot",
      );
      await fs.rename(validatedSource, validatedDestination);

      await expect(fs.readFile(destination, "utf8")).resolves.toBe(
        "outside-source",
      );
      await expect(
        fs.readFile(path.join(parked, "import.txt"), "utf8"),
      ).resolves.toBe("inside-source");
      expect(await exists(path.join(outside, "import.txt"))).toBe(false);
    } finally {
      await fs.rm(root, { recursive: true, force: true });
    }
  });
});
