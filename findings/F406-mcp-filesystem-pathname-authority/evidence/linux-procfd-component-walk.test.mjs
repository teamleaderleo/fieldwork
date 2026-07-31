import assert from "node:assert/strict";
import { constants } from "node:fs";
import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";

const DIRECTORY_FLAGS =
  constants.O_RDONLY | constants.O_DIRECTORY | constants.O_NOFOLLOW;

function assertSingleComponent(component) {
  assert.equal(typeof component, "string");
  assert.notEqual(component, "");
  assert.notEqual(component, ".");
  assert.notEqual(component, "..");
  assert.equal(component.includes("/"), false);
  assert.equal(component.includes("\\"), false);
}

async function openDirectoryComponent(
  parentHandle,
  component,
  procFdRoot = "/proc/self/fd",
) {
  assertSingleComponent(component);
  return fs.open(
    path.join(procFdRoot, String(parentHandle.fd), component),
    DIRECTORY_FLAGS,
  );
}

async function openFinalNoFollow(
  parentHandle,
  component,
  flags,
  procFdRoot = "/proc/self/fd",
) {
  assertSingleComponent(component);
  return fs.open(
    path.join(procFdRoot, String(parentHandle.fd), component),
    flags | constants.O_NOFOLLOW,
  );
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

async function makeFixture() {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), "fieldwork-procfd-walk-"));
  const allowed = path.join(root, "allowed");
  const outside = path.join(root, "outside");
  await fs.mkdir(path.join(allowed, "pivot", "nested"), { recursive: true });
  await fs.mkdir(outside);
  return { root, allowed, outside };
}

test("component-wise directory acquisition retains nested authority across ancestor swaps", async () => {
  const { root, allowed, outside } = await makeFixture();
  let allowedHandle;
  let pivotHandle;
  let nestedHandle;
  try {
    allowedHandle = await fs.open(allowed, DIRECTORY_FLAGS);
    pivotHandle = await openDirectoryComponent(allowedHandle, "pivot");

    const parkedPivot = path.join(allowed, "pivot-before-swap");
    await fs.rename(path.join(allowed, "pivot"), parkedPivot);
    await fs.symlink(outside, path.join(allowed, "pivot"), "dir");

    nestedHandle = await openDirectoryComponent(pivotHandle, "nested");

    const parkedNested = path.join(parkedPivot, "nested-before-swap");
    await fs.rename(path.join(parkedPivot, "nested"), parkedNested);
    await fs.symlink(outside, path.join(parkedPivot, "nested"), "dir");

    const outputHandle = await openFinalNoFollow(
      nestedHandle,
      "inside.txt",
      constants.O_WRONLY | constants.O_CREAT | constants.O_EXCL,
    );
    await outputHandle.writeFile("retained-inside");
    await outputHandle.close();

    await assert.doesNotReject(
      fs.readFile(path.join(parkedNested, "inside.txt"), "utf8"),
    );
    assert.equal(
      await fs.readFile(path.join(parkedNested, "inside.txt"), "utf8"),
      "retained-inside",
    );
    assert.equal(await exists(path.join(outside, "inside.txt")), false);
  } finally {
    await nestedHandle?.close();
    await pivotHandle?.close();
    await allowedHandle?.close();
    await fs.rm(root, { recursive: true, force: true });
  }
});

test("a symlink present before component acquisition is rejected", async () => {
  const { root, allowed, outside } = await makeFixture();
  let allowedHandle;
  try {
    await fs.rm(path.join(allowed, "pivot"), { recursive: true, force: true });
    await fs.symlink(outside, path.join(allowed, "pivot"), "dir");
    allowedHandle = await fs.open(allowed, DIRECTORY_FLAGS);

    await assert.rejects(
      openDirectoryComponent(allowedHandle, "pivot"),
      error => ["ELOOP", "ENOTDIR"].includes(error?.code),
    );
  } finally {
    await allowedHandle?.close();
    await fs.rm(root, { recursive: true, force: true });
  }
});

test("a final symlink is rejected rather than followed", async () => {
  const { root, allowed, outside } = await makeFixture();
  let nestedHandle;
  try {
    await fs.writeFile(path.join(outside, "secret.txt"), "outside-secret");
    await fs.symlink(
      path.join(outside, "secret.txt"),
      path.join(allowed, "pivot", "nested", "secret.txt"),
    );
    nestedHandle = await fs.open(
      path.join(allowed, "pivot", "nested"),
      DIRECTORY_FLAGS,
    );

    await assert.rejects(
      openFinalNoFollow(nestedHandle, "secret.txt", constants.O_RDONLY),
      error => error?.code === "ELOOP",
    );
  } finally {
    await nestedHandle?.close();
    await fs.rm(root, { recursive: true, force: true });
  }
});

test("missing procfs fails closed before a component is acquired", async () => {
  const { root, allowed } = await makeFixture();
  let allowedHandle;
  try {
    allowedHandle = await fs.open(allowed, DIRECTORY_FLAGS);
    await assert.rejects(
      openDirectoryComponent(
        allowedHandle,
        "pivot",
        path.join(root, "missing-proc-self-fd"),
      ),
      error => error?.code === "ENOENT",
    );
  } finally {
    await allowedHandle?.close();
    await fs.rm(root, { recursive: true, force: true });
  }
});

test("component validation rejects traversal syntax before filesystem access", async () => {
  const { root, allowed } = await makeFixture();
  let allowedHandle;
  try {
    allowedHandle = await fs.open(allowed, DIRECTORY_FLAGS);
    for (const component of ["", ".", "..", "a/b", "a\\b"]) {
      await assert.rejects(
        openDirectoryComponent(allowedHandle, component),
        assert.AssertionError,
      );
    }
  } finally {
    await allowedHandle?.close();
    await fs.rm(root, { recursive: true, force: true });
  }
});
