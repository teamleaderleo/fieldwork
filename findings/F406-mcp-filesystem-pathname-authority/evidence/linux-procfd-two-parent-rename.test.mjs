import assert from "node:assert/strict";
import { constants } from "node:fs";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const DIRECTORY_FLAGS =
  constants.O_RDONLY | constants.O_DIRECTORY | constants.O_NOFOLLOW;

function procPath(handle, name) {
  assert.equal(name.includes("/"), false);
  assert.equal(name.includes("\\"), false);
  assert.notEqual(name, "");
  assert.notEqual(name, ".");
  assert.notEqual(name, "..");
  return `/proc/self/fd/${handle.fd}/${name}`;
}

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
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "fieldwork-procfd-rename-"));
  const allowed = path.join(root, "allowed");
  const outsideSource = path.join(root, "outside-source");
  const outsideDestination = path.join(root, "outside-destination");
  const sourceParent = path.join(allowed, "source");
  const destinationParent = path.join(allowed, "destination");
  await fs.mkdir(sourceParent, { recursive: true });
  await fs.mkdir(destinationParent);
  await fs.mkdir(outsideSource);
  await fs.mkdir(outsideDestination);
  return {
    root,
    allowed,
    outsideSource,
    outsideDestination,
    sourceParent,
    destinationParent,
  };
}

test("two retained parents keep rename inside after both visible parents are replaced", async () => {
  const state = await fixture();
  let sourceHandle;
  let destinationHandle;
  try {
    await fs.writeFile(path.join(state.sourceParent, "item.txt"), "inside-item");
    sourceHandle = await fs.open(state.sourceParent, DIRECTORY_FLAGS);
    destinationHandle = await fs.open(state.destinationParent, DIRECTORY_FLAGS);

    const parkedSource = path.join(state.allowed, "source-before-swap");
    const parkedDestination = path.join(
      state.allowed,
      "destination-before-swap",
    );
    await fs.rename(state.sourceParent, parkedSource);
    await fs.rename(state.destinationParent, parkedDestination);
    await fs.symlink(state.outsideSource, state.sourceParent, "dir");
    await fs.symlink(
      state.outsideDestination,
      state.destinationParent,
      "dir",
    );

    await fs.rename(
      procPath(sourceHandle, "item.txt"),
      procPath(destinationHandle, "moved.txt"),
    );

    assert.equal(await exists(path.join(parkedSource, "item.txt")), false);
    assert.equal(
      await fs.readFile(path.join(parkedDestination, "moved.txt"), "utf8"),
      "inside-item",
    );
    assert.equal(
      await exists(path.join(state.outsideSource, "item.txt")),
      false,
    );
    assert.equal(
      await exists(path.join(state.outsideDestination, "moved.txt")),
      false,
    );
  } finally {
    await sourceHandle?.close();
    await destinationHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});

test("same-parent temporary replacement remains inside after visible parent replacement", async () => {
  const state = await fixture();
  let destinationHandle;
  try {
    await fs.writeFile(path.join(state.destinationParent, "target.txt"), "old");
    destinationHandle = await fs.open(state.destinationParent, DIRECTORY_FLAGS);

    const parkedDestination = path.join(
      state.allowed,
      "destination-before-swap",
    );
    await fs.rename(state.destinationParent, parkedDestination);
    await fs.symlink(
      state.outsideDestination,
      state.destinationParent,
      "dir",
    );

    const temporary = await fs.open(
      procPath(destinationHandle, ".target.txt.tmp"),
      constants.O_WRONLY |
        constants.O_CREAT |
        constants.O_EXCL |
        constants.O_NOFOLLOW,
    );
    await temporary.writeFile("new");
    await temporary.close();
    await fs.rename(
      procPath(destinationHandle, ".target.txt.tmp"),
      procPath(destinationHandle, "target.txt"),
    );

    assert.equal(
      await fs.readFile(path.join(parkedDestination, "target.txt"), "utf8"),
      "new",
    );
    assert.equal(
      await exists(path.join(state.outsideDestination, "target.txt")),
      false,
    );
  } finally {
    await destinationHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});

test("retained parent authority does not preserve the originally observed final entry identity", async () => {
  const state = await fixture();
  let sourceHandle;
  let destinationHandle;
  try {
    const original = path.join(state.sourceParent, "item.txt");
    const parkedOriginal = path.join(state.sourceParent, "item-before-swap.txt");
    const outsideObject = path.join(state.outsideSource, "outside.txt");
    await fs.writeFile(original, "inside-original");
    await fs.writeFile(outsideObject, "outside-object");
    sourceHandle = await fs.open(state.sourceParent, DIRECTORY_FLAGS);
    destinationHandle = await fs.open(state.destinationParent, DIRECTORY_FLAGS);

    // Model an entry replacement after policy admitted the original path but
    // before rename uses the retained source parent and final component name.
    await fs.rename(original, parkedOriginal);
    await fs.symlink(outsideObject, original);

    await fs.rename(
      procPath(sourceHandle, "item.txt"),
      procPath(destinationHandle, "moved.txt"),
    );

    const movedStat = await fs.lstat(
      path.join(state.destinationParent, "moved.txt"),
    );
    assert.equal(movedStat.isSymbolicLink(), true);
    assert.equal(
      await fs.readFile(parkedOriginal, "utf8"),
      "inside-original",
    );
    assert.equal(await fs.readFile(outsideObject, "utf8"), "outside-object");
  } finally {
    await sourceHandle?.close();
    await destinationHandle?.close();
    await fs.rm(state.root, { recursive: true, force: true });
  }
});
