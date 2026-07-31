import test from "node:test";
import assert from "node:assert/strict";
import fs, { constants } from "node:fs/promises";
import os from "node:os";
import path from "node:path";

async function exists(target) {
  try {
    await fs.lstat(target);
    return true;
  } catch (error) {
    if (error?.code === "ENOENT") return false;
    throw error;
  }
}

async function fixture() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "fieldwork-procfd-authority-"));
  const allowed = path.join(root, "allowed");
  const outside = path.join(root, "outside");
  const parent = path.join(allowed, "pivot");
  const parked = path.join(allowed, "pivot-before-swap");
  await fs.mkdir(parent, { recursive: true });
  await fs.mkdir(outside);
  return { root, allowed, outside, parent, parked };
}

async function swapParent({ parent, parked, outside }) {
  await fs.rename(parent, parked);
  await fs.symlink(outside, parent, "dir");
}

test("pathname baseline follows the swapped ancestor", async () => {
  const state = await fixture();
  try {
    const requested = path.join(state.parent, "created.txt");
    await swapParent(state);
    await fs.writeFile(requested, "pathname-outside", { flag: "wx" });

    assert.equal(
      await fs.readFile(path.join(state.outside, "created.txt"), "utf8"),
      "pathname-outside",
    );
    assert.equal(await exists(path.join(state.parked, "created.txt")), false);
  } finally {
    await fs.rm(state.root, { recursive: true, force: true });
  }
});

test("an open directory fd retains the validated parent after rename", async () => {
  const state = await fixture();
  let parentHandle;
  try {
    parentHandle = await fs.open(
      state.parent,
      constants.O_RDONLY | constants.O_DIRECTORY,
    );
    const fdPath = `/proc/self/fd/${parentHandle.fd}/created.txt`;

    await swapParent(state);
    await fs.writeFile(fdPath, "descriptor-inside", { flag: "wx" });

    assert.equal(
      await fs.readFile(path.join(state.parked, "created.txt"), "utf8"),
      "descriptor-inside",
    );
    assert.equal(await exists(path.join(state.outside, "created.txt")), false);
  } finally {
    await parentHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});

test("procfd sibling temp plus rename retains the opened parent", async () => {
  const state = await fixture();
  let parentHandle;
  try {
    await fs.writeFile(path.join(state.parent, "existing.txt"), "before");
    parentHandle = await fs.open(
      state.parent,
      constants.O_RDONLY | constants.O_DIRECTORY,
    );
    const fdRoot = `/proc/self/fd/${parentHandle.fd}`;
    const tempPath = path.join(fdRoot, ".fieldwork.tmp");
    const destinationPath = path.join(fdRoot, "existing.txt");

    await swapParent(state);
    await fs.writeFile(tempPath, "after", { flag: "wx" });
    await fs.rename(tempPath, destinationPath);

    assert.equal(
      await fs.readFile(path.join(state.parked, "existing.txt"), "utf8"),
      "after",
    );
    assert.equal(await exists(path.join(state.outside, "existing.txt")), false);
    assert.equal(await exists(path.join(state.outside, ".fieldwork.tmp")), false);
  } finally {
    await parentHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});
