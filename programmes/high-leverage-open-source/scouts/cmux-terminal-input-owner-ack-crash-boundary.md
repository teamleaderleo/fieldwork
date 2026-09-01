# cmux: local terminal input can commit success before PTY delivery

## In simple words

cmux could durably remember “I typed this” when it had only handed the bytes to another process and that process had not yet delivered them to the terminal. A crash in that gap can leave a permanent success receipt for input that provably never reached the PTY.

The repaired candidate moves the success boundary to the component that actually owns the PTY: receipted terminal input now carries a request id, the terminal host writes and flushes the bytes to the PTY, and only then returns `InputAck`. Ordinary interactive typing stays fire-and-forget. The current-main candidate is target-executed and independently diff-reviewed; the remaining human question is whether this demonstrated crash-boundary trust failure is consequential enough to justify the additive owner-ack protocol upstream.

## Target

- Upstream: `manaflow-ai/cmux`
- Audited revision: `eaa899cb20bd411019744fbd2bdedeb397f3070b`
- Current upstream relation checked through: `61bc1e4a6d1c882d552199f4b2785ea45c177ae2`
- Audit date: 2026-09-01
- Runtime artifact: upstream GitHub Actions Linux artifact for the exact audited revision
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

The final current-main restack verified that the owner paths used by this repair were unchanged between the prior current-main patch base `6044a8b3f43152d2e6fc17f771fd4b277b393118` and upstream `61bc1e4a6d1c882d552199f4b2785ea45c177ae2`; the intervening upstream commit touched only `cmux-tui/crates/cmux-remote/src/client.rs`.

## Patch direction

The smallest compatible correction is to make **receipted API input** wait for an acknowledgement from the local terminal host after its PTY write/flush has succeeded. Ordinary interactive input remains on the current low-latency fire-and-forget path.

Compatibility uses an explicit additive capability so a new daemon never sends a targeted input request to an old surviving host that only understands fire-and-forget input. The implementation uses `supports_input_ack` in the durable terminal-host discovery record; missing/false causes receipted API input to fail closed before sending bytes while legacy interactive input remains available.

The confirmed path covers the durable terminal operations that emit PTY bytes: `terminal.input.write`, `terminal.input.keys`, `terminal.input.mouse`, and `terminal.input.focus`.

The split-phase refinement registers and writes the targeted request under the short terminal runtime lock, then releases that lock before waiting for `InputAck`. Multiple receipted callers can therefore be outstanding without turning the runtime lock into a stop-and-wait serialization point. Outstanding requests and aggregate payload are bounded; one maximum legal terminal-host input frame remains admissible.

### Failure classification

- **Known pre-effect:** legacy host without `supports_input_ack`, exited/no live hosted owner, bounded acknowledgement window exhausted, request-id exhaustion/collision.
- **Indeterminate:** local partial/write failure, possible partial terminal-host socket frame, acknowledgement timeout/disconnect after a possible send.
- **Success:** only after the authoritative terminal host has successfully written/flushed the bytes to the PTY and returned the matching acknowledgement.

This removes the demonstrated false-success window. It does not by itself make a crash after host ACK but before SQLite completion exactly reconcilable; that stronger property would require owner-side retained logical request identity or another fate query.

## Repair verification

Canonical owned implementation PR: `teamleaderleo/cmux#16`.

Exact current-main generation:

- upstream base: `61bc1e4a6d1c882d552199f4b2785ea45c177ae2`
- synchronous owner-ACK baseline: `9057c2f0d876565c94a98482e35d70519b414223`
- split-phase candidate/head: `a7fba4766f359963a375b67c6c62818240f53dda`
- two commits; eight product/test/spec files total
- canonical branch contains no Fieldwork helper/workflow machinery

Target-executed current-main restack: owned-fork workflow run `33561858997`, job `100035981383`, Ubuntu 24.04 with pinned Rust/Zig. The run completed successfully and:

1. proved source continuity into current upstream;
2. rebuilt the synchronous owner-ACK commit directly on current upstream;
3. characterized the synchronous baseline's full `cmux-tui-core` failures;
4. applied only the four-file split-phase delta;
5. passed Rust formatting;
6. passed protocol/spec inventory, resource API boundary, and binding generation checks;
7. passed focused receipted-input and owner-ACK tests, including pipelining, bounded outstanding work, legacy-host no-send, PTY-before-ACK, exited-host pre-effect failure, local partial-write ambiguity, and interactive fire-and-forget preservation;
8. passed focused resource-router tests;
9. reran the full core suite and required the candidate to introduce **no failing test absent from the synchronous baseline**;
10. published the exact candidate only after that comparison passed.

Independent complete-diff review checked request-id registration and cleanup, waiter/reservation cleanup on success/error/drop, runtime-lock release before ACK wait, socket poisoning after ambiguous transport failure, legacy/exited-host pre-effect fencing, host ACK ordering after PTY delivery, request-id-zero compatibility, additive discovery semantics, and product-only branch contents. No blocking defect was found.

## Remaining boundary

The repair deliberately does **not** claim shell/application execution. `InputAck` proves the authoritative PTY owner accepted and flushed the terminal input bytes; it does not prove that a command represented by those bytes later succeeded.

A harder crash window also remains:

```text
PTY receives input
→ terminal host sends InputAck
→ mux receives InputAck
→ mux crashes
→ durable success receipt was not yet committed
```

Recovery may truthfully report `mutation.indeterminate` here. Eliminating that ambiguity would require the owner to retain logical request fate across daemon replacement. That is a separate protocol/architecture step and is not necessary to remove the demonstrated false-success claim.

## Disposition

**REPAIRED CANDIDATE / HUMAN JUDGMENT.** Consequence is very high and provability is high: the false-success behavior is deterministic, the repair is target-executed on current upstream, and the complete candidate delta has been independently reviewed. The remaining decision is whether this narrow crash-boundary trust failure is important enough to justify upstream protocol complexity and maintainer attention.

Third-party upstream remains read-only; no upstream issue, PR, comment, review, or contact has been created.
