# Held upstream issue draft

Do not file without explicit authorization.

## Suggested title

`killDescendants: true` makes `subprocess.kill(0)` destructive on Windows

## Description

Execa 10.0.0 added `killDescendants` process-tree termination. With that option enabled, the Windows kill adapter ignores the requested signal and always launches:

```text
taskkill /pid <pid> /T /F
```

Execa explicitly accepts integer signal `0` in `subprocess.kill(0)`. Node documents signal `0` as a platform-independent existence check that must not terminate the process.

The result is that a caller using the standard liveness check can forcefully terminate the process tree on Windows when `killDescendants: true`.

## Minimal reproduction

```js
import process from 'node:process';
import {setTimeout as delay} from 'node:timers/promises';
import {execa} from 'execa';

const child = execa(
  process.execPath,
  ['-e', 'setInterval(() => {}, 1000)'],
  {killDescendants: true, reject: false, stdio: 'ignore'},
);

console.log(process.kill(child.pid, 0)); // true; non-destructive Node control
console.log(child.kill(0));              // true
await delay(1000);
console.log(process.kill(child.pid, 0)); // throws on affected Windows path
```

## Expected result

`subprocess.kill(0)` should only check whether the direct subprocess/process group exists. It should not launch `taskkill`, terminate the child or descendants, schedule forceful escalation, or mark cancellation state.

## Suggested narrow correction

Handle signal `0` before platform-specific process-tree termination:

```js
if (signal === 0) {
  return subprocess.kill(0)
}
```

Add a Windows regression pairing the non-destructive signal-zero case with a normal descendant-termination control.

## Scope

- release: `execa@10.0.0`;
- source: `e389369f3cd82ae59a8635781ecb9fb20f7cb201`;
- feature commit: `84fa0ecb3f7ca5f73f2dcbd4d4ec0c65fb6b1146`;
- separate from documented best-effort descendant escape and Unix terminal-detachment behavior.
