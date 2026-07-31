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
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "fieldwork-procfd-nested-"));
  const allowed = path.join(root, "allowed");
  const outside = path.join(root, "outside");
  const parent = path.join(allowed, "pivot");
  const nested = path.join(parent, "nested");
  const parkedNested = path.join(parent, "nested-before-swap");
  await fs.mkdir(nested, { recursive: true });
  await fs.mkdir(outside);
  return { root, allowed, outside, parent, nested, parkedNested };
}

async function swapNested({ nested, parkedNested, outside }) {
  await fs.rename(nested, parkedNested);
  await fs.symlink(outside, nested, "dir");
}

test("top-parent procfd still follows a swapped unresolved nested component", async () => {
  const state = await fixture();
  let parentHandle;
  try {
    parentHandle = await fs.open(
      state.parent,
      constants.O_RDONLY | constants.O_DIRECTORY,
    );
    const requested = `/proc/self/fd/${parentHandle.fd}/nested/escaped.txt`;

    await swapNested(state);
    await fs.writeFile(requested, "nested-outside", { flag: "wx" });

    assert.equal(
      await fs.readFile(path.join(state.outside, "escaped.txt"), "utf8"),
      "nested-outside",
    );
    assert.equal(await exists(path.join(state.parkedNested, "escaped.txt")), false);
  } finally {
    await parentHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});

test("pre-opened immediate nested parent retains authority after nested swap", async () => {
  const state = await fixture();
  let nestedHandle;
  try {
    nestedHandle = await fs.open(
      state.nested,
      constants.O_RDONLY | constants.O_DIRECTORY,
    );
    const requested = `/proc/self/fd/${nestedHandle.fd}/inside.txt`;

    await swapNested(state);
    await fs.writeFile(requested, "nested-inside", { flag: "wx" });

    assert.equal(
      await fs.readFile(path.join(state.parkedNested, "inside.txt"), "utf8"),
      "nested-inside",
    );
    assert.equal(await exists(path.join(state.outside, "inside.txt")), false);
  } finally {
    await nestedHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});
