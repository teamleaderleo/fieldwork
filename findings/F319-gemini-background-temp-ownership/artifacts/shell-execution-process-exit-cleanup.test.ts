/**
 * @license
 * Copyright 2026 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

import { afterEach, describe, expect, it, vi } from 'vitest';

import { ExecutionLifecycleService } from './executionLifecycleService.js';
import { NoopSandboxManager } from './sandboxManager.js';
import { ShellExecutionService } from './shellExecutionService.js';

const executeChild = async (onProcessExit: () => void | Promise<void>) => {
  const handle = await ShellExecutionService.execute(
    'true',
    process.cwd(),
    vi.fn(),
    new AbortController().signal,
    false,
    {
      sanitizationConfig: {},
      sandboxManager: new NoopSandboxManager(),
      sessionId: 'fieldwork-process-exit-cleanup',
      onProcessExit,
    },
  );
  return handle.result;
};

describe('ShellExecutionService process-exit cleanup', () => {
  afterEach(() => {
    ExecutionLifecycleService.resetForTest();
  });

  it('preflights and acknowledges background ownership exactly once', async () => {
    const handle = ExecutionLifecycleService.createExecution(
      '',
      undefined,
      'child_process',
    );
    const executionId = handle.pid!;

    expect(ExecutionLifecycleService.canBackground(executionId)).toBe(true);
    expect(ExecutionLifecycleService.background(executionId)).toBe(true);
    expect(ExecutionLifecycleService.canBackground(executionId)).toBe(false);
    expect(ExecutionLifecycleService.background(executionId)).toBe(false);
    await expect(handle.result).resolves.toMatchObject({
      pid: executionId,
      backgrounded: true,
    });

    ExecutionLifecycleService.completeExecution(executionId, { exitCode: 0 });
  });

  it('invokes transferred cleanup after child-process exit', async () => {
    const cleanup = vi.fn().mockResolvedValue(undefined);

    const result = await executeChild(cleanup);

    expect(result.exitCode).toBe(0);
    await vi.waitFor(() => {
      expect(cleanup).toHaveBeenCalledTimes(1);
    });
  });

  it('preserves the execution result when transferred cleanup rejects', async () => {
    const cleanup = vi.fn().mockRejectedValue(new Error('cleanup failed'));

    const result = await executeChild(cleanup);

    expect(result.exitCode).toBe(0);
    expect(result.error).toBeNull();
    await vi.waitFor(() => {
      expect(cleanup).toHaveBeenCalledTimes(1);
    });
  });
});
