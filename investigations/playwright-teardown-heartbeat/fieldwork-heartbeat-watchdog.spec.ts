import { test, expect } from './playwright-test-fixtures';

const mode = process.env.FIELDWORK_HEARTBEAT_MODE;

test('finite unlimited teardown keeps the worker alive only until completion', async ({ runInlineTest }) => {
  test.skip(mode !== 'finite', 'finite control only');

  const result = await runInlineTest({
    'a.spec.ts': `
      import { test as base } from '@playwright/test';
      const test = base.extend<{}, { slowTeardown: void }>({
        slowTeardown: [async ({}, use) => {
          await use();
          await new Promise(f => setTimeout(f, 4000));
          console.log('FIELDWORK_FINITE_TEARDOWN_COMPLETE');
        }, { scope: 'worker', timeout: 0 }],
      });
      test('passes', async ({ slowTeardown }) => {});
    `,
  }, undefined, {
    PWTEST_CHILD_PROCESS_TIMEOUT: '2000',
    PWTEST_FORCE_EXIT_TIMEOUT: '3000',
  });

  expect(result.exitCode).toBe(0);
  expect(result.passed).toBe(1);
  expect(result.output).toContain('FIELDWORK_FINITE_TEARDOWN_COMPLETE');
  expect(result.output).not.toContain('force-killed');
});

test('responsive never-settling teardown outlives both internal watchdog settings', async ({ runInlineTest }) => {
  test.skip(mode !== 'stuck', 'stuck discriminator only');
  test.setTimeout(0);

  await runInlineTest({
    'a.spec.ts': `
      import { test as base } from '@playwright/test';
      const test = base.extend<{}, { stuckTeardown: void }>({
        stuckTeardown: [async ({}, use) => {
          await use();
          console.log('FIELDWORK_STUCK_TEARDOWN_STARTED');
          await new Promise(() => {});
        }, { scope: 'worker', timeout: 0 }],
      });
      test('passes', async ({ stuckTeardown }) => {});
    `,
  }, undefined, {
    PWTEST_CHILD_PROCESS_TIMEOUT: '2000',
    PWTEST_FORCE_EXIT_TIMEOUT: '3000',
  });

  throw new Error('never-settling teardown unexpectedly returned');
});
