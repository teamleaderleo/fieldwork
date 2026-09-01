# cmux: local terminal input can commit success before PTY delivery

## Target

- Upstream: `manaflow-ai/cmux`
- Audited revision: `eaa899cb20bd411019744fbd2bdedeb397f3070b`
- Audit date: 2026-09-01
- Runtime artifact: upstream GitHub Actions Linux artifact for the exact revision
- Artifact SHA-256: `5777f0684b90fee55bf4b4ea7d142ec3c3aee9d33d0275076e8c29cc63ba0ab4`

## Finding

`terminal.input.write` can return and durably record success after the mux has written an `Input` frame into the terminal-host Unix socket but before the terminal host has delivered those bytes to the PTY.

That makes the mux receipt stronger than the owner evidence that backs it. The terminal host owns the PTY master and is the smallest component that can establish whether the input crossed the owner boundary.

## Deterministic false-success reproduction

The test terminal child entered raw mode, blocked on one byte from stdin, and wrote the received byte to a separate effect file. The effect file was the independent oracle.

1. Create a hosted terminal and wait for the child to block on input.
2. Discover the terminal-host PID/incarnation from its durable host record.
3. `SIGSTOP` the terminal host.
4. Issue `terminal.input.write` with payload `X` and idempotency key `input-key`.
5. The mux returns success and commits the effect receipt at revision 2.
6. The journal contains `terminal.input.write.effect.succeeded` with correlation `input-key`.
7. While the terminal host is still stopped, the independent effect file is absent: the PTY child has received zero bytes.
8. `SIGKILL` the mux.
9. `SIGKILL` the still-frozen terminal host before it can consume queued socket data.
10. Restart the session and replay the exact same mutation key/payload.

Observed replay:

```json
{
  "replayed": true,
  "revision": "2",
  "value": {}
}
```

Final oracle state:

| Oracle | Result |
| --- | --- |
| Effect receipt | committed success, revision 2 |
| Journal | `terminal.input.write.effect.succeeded` |
| Exact replay | success, `replayed:true` |
| PTY-child effect file | absent |
| Original terminal host | dead |

Classification: **false authoritative completion**. The durable system says the effect succeeded while external reality proves it never occurred.

## Interrupted-execution twins

A second fault-injection pair used a 2 MiB write to hold the effect receipt in `executing` while controlling the terminal host independently.

### Twin A: effect happened

- receipt: `executing`
- completion journal record: absent
- host resumed before mux death
- child effect file: `X`
- mux killed before receipt completion
- host and child survived

After restart, exact replay returned non-retryable `mutation.indeterminate`; the effect remained present.

### Twin B: effect never happened

- receipt: `executing`
- completion journal record: absent
- host remained stopped through mux death
- child effect file: absent

After restart, exact replay returned the same non-retryable `mutation.indeterminate` state.

The durable post-recovery state cannot distinguish “owner definitely applied the input” from “owner definitely never applied the input.” That is consistent with the generic fail-closed external-effect contract, but it leaves terminal input unreconcilable after an interrupted owner handoff.

## Controls

### Clean committed input

A normal input mutation applied once. After mux `SIGKILL`, exact replay returned the original revision with `replayed:true` and no second external effect. Classification: **A**.

### Terminal creation

`workspace.run` was crashed after the independent terminal host and shell existed while creation/effect receipts remained executing. Restart adopted the same host, settled creation once, emitted one journal event, and exact replay returned the original resource identity. Classification: **A**.

This is the useful counterexample: cmux already has a working owner-reconciliation model when the surviving owner exposes durable identity and adoption evidence.

### Terminal close

The terminal host was frozen after the close became durable but before owner termination. After mux crash, restart waited for the surviving host; once resumed, it terminated and exact close replay converged to the original revision with one close event. Classification: **A** for a responsive survivor.

## Source boundary

At the audited revision:

- hosted `Surface::write_bytes` delegates to `HostAttachment::send(MessageKind::Input, bytes)`;
- `HostAttachment::send` completes when a CMTH frame is written to the Unix socket;
- the terminal-host client loop later handles `MessageKind::Input` by `write_all` + `flush` to the PTY;
- CMTH has targeted acknowledgements for resize, clear-history, cell-pixel size, Kitty limits, terminate, and detach;
- CMTH has no targeted input acknowledgement.

The remote PTY implementation is a useful contrast: it carries sequenced input and emits cumulative `pty.input_ack` events.

## Patch direction

The smallest compatible correction is to make **receipted API input** wait for an acknowledgement from the local terminal host after its PTY write/flush has succeeded. Ordinary interactive input can remain on the current low-latency fire-and-forget path.

Compatibility needs an explicit capability boundary so a new daemon never sends an unknown targeted input request to an old surviving host. A terminal-host record version bump is a compact discriminator because host records survive mux replacement and already represent additive host capabilities.

This removes the demonstrated false-success window. It does not by itself make a crash after host ACK but before SQLite completion exactly reconcilable; that stronger property would require owner-side retained logical request identity or another fate query.

## Patch status

Implementation work lives on the user fork `teamleaderleo/cmux`, based directly on audited upstream commit `eaa899cb20bd411019744fbd2bdedeb397f3070b` so the fork's older divergent `main` history does not contaminate the patch.
