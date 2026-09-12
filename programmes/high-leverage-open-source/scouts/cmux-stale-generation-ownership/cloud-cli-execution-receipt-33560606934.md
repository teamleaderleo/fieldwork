# Hardened cloud CLI socket ownership execution receipt

## In simple words

The rewritten cloud CLI candidate now proves both layers of the ownership contract: live bridge A excludes successor B until A has removed its socket name, and the lock object used for that exclusion cannot silently be a symlink, FIFO, hard-linked inode, or non-private owned file. The test-only commit fails every disputed assertion; the hardened commit passes repeatedly and cross-builds for every released daemon platform.

Evidence class: `target-executed`  
Target: `manaflow-ai/cmux`  
Exact upstream base: `6044a8b3f43152d2e6fc17f771fd4b277b393118`  
Owned-fork PR: `teamleaderleo/cmux#10`  
RED: `3fcfdc334a2459ea353dc6316d5325be48a20e40`  
GREEN: `2df7cd900dd038bdd18b4c7c35dcd809878f1344`  
Execution carrier: `teamleaderleo/cmux#30`  
Workflow run: `33560606934`  
Job: `100031891608`  
Upstream contact authorized: `false`

## Environment

GitHub-hosted Ubuntu 24.04.4 (`ubuntu-24.04` image), Go `1.24.13 linux/amd64`.

The repository release builder supports `darwin/arm64`, `darwin/amd64`, `linux/arm64`, and `linux/amd64`, so the verifier also cross-built the daemon for all four targets and cross-compiled the Darwin arm64 Go test target.

## RED discriminators

The verifier first proved ancestry and required RED to differ from base only by:

`daemon/remote/cmd/cmuxd-remote/cloud_cli_bridge_generation_test.go`

It then ran each regression separately and required both non-zero exit and the exact distinguishing marker:

1. `TestCloudCLIBridgeRejectsOverlappingSocketOwner`
   - `second bridge took over the socket while the first owner was still alive`
2. `TestCloudCLIBridgeRejectsSymlinkedSocketLock`
   - `symlinked cloud CLI socket lock was accepted`
3. `TestCloudCLIBridgeRejectsFIFOSocketLockWithoutBlocking`
   - `FIFO cloud CLI socket lock was accepted`
4. `TestCloudCLIBridgeRejectsHardLinkedSocketLockWithoutChmod`
   - `hard-linked cloud CLI socket lock was accepted`
5. `TestCloudCLIBridgeMigratesOwnedSocketLockToPrivateMode`
   - `owned lock mode = 644, want 600`

All five red discriminators passed the verifier by failing for those intended reasons.

## GREEN checks

The combined five-test hardened regression set passed with `-count=25`.

The verifier then:

- built `cmuxd-remote` for Darwin arm64;
- built `cmuxd-remote` for Darwin amd64;
- built `cmuxd-remote` for Linux arm64;
- built `cmuxd-remote` for Linux amd64;
- cross-compiled the Darwin arm64 `cmd/cmuxd-remote` test binary;
- passed full `daemon/remote` `go test ./...`.

## Repair contract

GREEN opens `<socket>.lock` with `O_CREAT|O_RDWR|O_CLOEXEC|O_NOFOLLOW|O_NONBLOCK`, validates the opened descriptor as a single-link regular file owned by the effective UID, migrates/rechecks private mode `0600`, then acquires nonblocking exclusive `flock`.

The lock descriptor remains owned by the bridge until the listener accept loop exits. Deferred socket-path removal runs before deferred lock release, preventing a successor from acquiring the lock between old-listener close and old-path cleanup.

## Consequence and limit

The underlying bug supports **2. stale destructive effect**: A can remove B's stable pathname after B becomes authoritative. A B listener FD may survive while new clients see `ENOENT`, giving a bounded **4. leaked surviving resource** characteristic until B exits.

This receipt proves target-native behavior on Linux and compilation across every released Darwin/Linux architecture. It does not establish ecosystem prevalence or upstream acceptance. Fresh read-only issue/PR searches found no exact-mechanism upstream work.

Third-party upstream remained read-only.
