# NativeSSH control-master ownership negative result

## In simple words

`NativeSSHConnectionBroker.retainWorkspace` looks dangerous in isolation: for an exact cmux-owned ControlPath it asks the cross-process ownership registry to retain a shared lease, discards the returned Boolean, and then records the workspace in its in-process owner maps anyway.

On the current production path that bookkeeping mismatch does **not** authorize a stale operation. Foreground authentication has a checked temporary-to-durable handoff; restore/reconnect/fork paths that lack that handoff are checked again by `RemoteSessionCoordinator` before daemon bootstrap, proxy, or reverse-relay work; last-owner cleanup obtains a fresh exclusive authorization before issuing `ssh -O exit`. The only startup side effect that precedes the recheck removes PPID-1 orphaned relay/stdio children and does not classify the shared ControlMaster process itself.

Disposition: **negative result for stale-generation mutation at the traced source boundary**. The ignored retain result is misleading internal state, but every consequence-producing use found in production is separately fenced.

Target: `manaflow-ai/cmux`  
Traced revision: `6044a8b3f43152d2e6fc17f771fd4b277b393118`  
Latest upstream checked: `594eb0461e0ae4d57a99180e19097cea5e5091e0`  
Continuity: the two intervening upstream commits do not touch the macOS RemoteSession / NativeSSH ownership paths.  
Evidence class: `source-read` / interface trace  
Upstream contact authorized: `false`

## Candidate sequence examined

```text
process A holds exclusive ControlMaster recovery/cleanup authority
B configures/restores the same exact cmux-owned ControlPath
B retainWorkspace mints generation G
cross-process registry retain(G) -> false
B nevertheless records G in ownerLeases / ownersByControlMaster
B starts a RemoteSessionCoordinator
```

The disputed question was whether B can now use or destroy the master as though G were authoritative.

## Foreground-authenticated start is fenced at the handoff

`Workspace.notifyRemoteForegroundAuthenticationReady` calls `beginControlMasterAdoption` for the exact resolved path. That method creates a temporary lease and returns `nil` if the registry cannot retain it.

`Workspace.configureRemoteConnection` then:

1. scopes the configuration to the workspace;
2. carries the pending adoption's resolved path into the configuration;
3. calls `nativeSSHConnectionBroker.retainWorkspace`, which mints the durable generation;
4. calls `completeControlMasterAdoption`;
5. if durable retain fails, cancels the handoff, releases the local lease, publishes `controlMasterOwnershipUnavailable`, and returns `false`.

`completeControlMasterAdoption` itself requires the registry to retain the durable lease before releasing the temporary handoff, so there is no unowned gap between foreground authentication and the durable owner.

## Restore/reconnect/fork start is fenced before remote use

Paths without a foreground adoption can reach the isolated mismatch: `retainWorkspace` can return a generated configuration after registry retain returned `false`.

However, `RemoteSessionCoordinator.beginConnectionAttemptLocked` calls `prepareControlMasterOwnershipLocked()` before daemon bootstrap, proxy startup, or reverse-relay startup. For an exact cmux-owned path, that flows through `resolvedControlMasterSSHOptionsLocked()` to `retainResolvedControlMasterLease(...)` and requires the registry's Boolean result. A busy/exclusive owner therefore causes the connection attempt to fail before the shared master is reused.

The startup helper `killOrphanedRemoteSSHProcesses` runs immediately before that check. Its command classifier is limited to PPID-1 cmux reverse-relay transports (`ssh -N -R ...`) and `cmuxd-remote serve --stdio` transports. It does not classify an OpenSSH ControlMaster process, and live sibling-process children are not PPID 1.

## Cleanup is independently re-authorized

When the local owner map reaches zero, `removeLease` builds a last-owner cleanup request. Production `launchCleanup` still calls `controlMasterOwnershipRegistry.beginCleanup(controlPath:)` before spawning `ssh -O exit`.

If another process retains or exclusively owns the master, cleanup gets no authorization and enters bounded retry. The local bookkeeping entry therefore cannot directly destroy the shared master.

## Why this is a negative control

The source contains two plausible ideas of ownership:

- `ownerLeases` / `ownersByControlMaster` inside one broker process;
- advisory-file-lock ownership across cmux processes.

They can briefly disagree because `retainWorkspace` discards one Boolean. Yet the later effect boundaries do not trust the local map alone. Both remote reuse and destructive cleanup ask the cross-process owner again.

That makes this a useful negative control for the scout harness: suspicious split bookkeeping exists, while stale work still cannot cross the side-effect boundary under the traced production paths.

## Reopen trigger

Reopen if any production path is introduced or found that:

- consumes an exact cmux-owned ControlPath after `retainWorkspace` without `prepareControlMasterOwnershipLocked` / `retainResolvedControlMasterLease`;
- issues destructive ControlMaster cleanup without `beginCleanup` authorization;
- broadens the pre-ownership orphan killer to include the ControlMaster process or another live sibling-owned resource;
- treats local `ownerLeases` as authoritative for a cross-process side effect.

No fork patch is justified by the current stale-generation claim. A future refactor could make the failed-retain state less misleading, but that would need its own demonstrated consequence before promotion.

Third-party upstream remained read-only.
