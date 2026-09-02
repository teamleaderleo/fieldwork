# Cloud CLI socket ownership lock review

## In simple words

The cloud CLI stale-unlink bug is real, and serializing the stable socket name is a plausible repair. The first implementation still left the new lock pathname under-specified: plain `os.OpenFile` followed symlinks and did not prove that the opened object was a private, single-link regular file owned by this daemon user. That candidate was therefore repaired before promotion.

Target: `manaflow-ai/cmux`  
Exact current upstream base: `6044a8b3f43152d2e6fc17f771fd4b277b393118`  
Canonical owned-fork PR: `teamleaderleo/cmux#10`  
Current RED: `3fcfdc334a2459ea353dc6316d5325be48a20e40`  
Current GREEN: `2df7cd900dd038bdd18b4c7c35dcd809878f1344`  
Upstream contact authorized: `false`

## Review finding

The superseded lock implementation used a predictable `<socket>.lock` pathname opened with `os.OpenFile(..., O_CREATE|O_RDWR, 0600)` before `flock`.

That creates several ownership ambiguities in a world-writable parent such as `/tmp`:

- a symlink can redirect the descriptor to another object;
- a FIFO can make acquisition depend on special-file open semantics before type validation;
- a hard-linked inode can make mode changes or locking affect a shared object;
- an existing foreign-owned or overly-permissive file has no explicit descriptor-level ownership contract.

The original source pin itself contains a hardened start-lock pattern elsewhere, so accepting a weaker adjacent lock boundary would be inconsistent with the target's current defensive posture.

Disposition on the superseded head: **REPAIR**.

## Rewritten regression contract

The new test-only RED commit requires all of these:

1. live A excludes overlapping B while A remains dialable;
2. a symlinked lock pathname is rejected and its target bytes/mode stay unchanged;
3. a FIFO lock is rejected without blocking before type validation;
4. a hard-linked lock is rejected without chmod side effects;
5. an owned single-link regular lock can migrate from `0644` to `0600`.

These checks intentionally make the lock object part of the ownership invariant instead of treating `flock` success as sufficient proof.

## Rewritten implementation

GREEN opens the lock using the existing `golang.org/x/sys/unix` dependency with:

`O_CREAT | O_RDWR | O_CLOEXEC | O_NOFOLLOW | O_NONBLOCK`

It then validates the opened descriptor with `fstat` before locking:

- regular file;
- link count exactly one;
- UID equals the effective UID;
- mode migrated to and rechecked as private (`0600`).

Only then does it take nonblocking exclusive `flock`. The descriptor stays alive until the listener accept loop exits; socket pathname cleanup runs before lock release, so a successor cannot acquire ownership between old-listener close and old-path removal.

## Portability boundary

The release builder targets `darwin/arm64`, `darwin/amd64`, `linux/arm64`, and `linux/amd64`. The fresh execution carrier therefore includes normal Linux tests, four daemon cross-builds, and a Darwin test-target cross-compile.

## Evidence state

`target-test-prepared` for the rewritten head until the fresh execution carrier completes. Earlier ownership-only runs remain valid evidence for the stale-unlink mechanism and for the singleton handoff model, but they do not accept this changed head.

Third-party upstream remained read-only.
