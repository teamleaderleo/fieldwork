# cmux terminal input owner acknowledgement — current-head verification

## In simple words

The local hosted-terminal input bug has a current-upstream owned-fork repair that matches the tested bytes exactly.

CMUX used to be able to durably say a receipted terminal input succeeded after putting an `Input` frame into the terminal-host socket but before the terminal host actually wrote the bytes into the PTY. The retained crash probe proved a durable success receipt and successful idempotent replay could coexist with an independent oracle proving the PTY effect never happened.

The owned-fork candidate now waits for an authoritative terminal-host acknowledgement issued only after PTY `write_all` + `flush`. Interactive typing remains fire-and-forget. A surviving older host without the additive ACK capability rejects receipted input before any bytes are sent.

This current-head pass rebuilt the candidate on exact upstream `9e2dd50957936153ca0da61d2f079937674f9375`, ran the full current-head comparison gate, reconstructed the Git trees independently from reviewed blobs, and then required the canonical refiners to regenerate those exact tree hashes before the draft PR was moved.

## Scope and ownership

- Target: `manaflow-ai/cmux`
- Upstream interaction: read-only only
- Exact upstream SHA: `9e2dd50957936153ca0da61d2f079937674f9375`
- Exact upstream tree: `8506d08895c5f59b7b0c1ac47b65bf4a3fa1ca49`
- Owned fork: `teamleaderleo/cmux`
- Owned draft PR: `teamleaderleo/cmux#16`
- PR base branch: `fieldwork/upstream-main-9e2dd509`
- PR head branch: `fix/terminal-input-owner-ack`
- Claim scope: mechanism + interface correctness on local hosted terminal input
- Upstream contact authorization: `false`

## Exact candidate

The canonical current-head candidate is intentionally two commits:

1. `e652c92bfc8298435b8e5199fecf10ff5b30c0b6` — synchronous owner acknowledgement
   - tree: `300ed73dd3d49872b67041dfd28462b3d8d6c934`
2. `22c287b42de69e42d1915c24e11c73ce867679dc` — split submission from ACK waiting
   - tree: `a56a8e828a906b87df9169790b2beb053373648f`

The final PR delta is exactly eight files:

- `cmux-tui/crates/cmux-tui-core/src/resource_router/content.rs`
- `cmux-tui/crates/cmux-tui-core/src/surface.rs`
- `cmux-tui/crates/cmux-tui-core/src/terminal_host_protocol.rs`
- `cmux-tui/crates/cmux-tui-core/src/terminal_host_runtime.rs`
- `cmux-tui/crates/cmux-tui-core/src/workspace_registry/tests.rs`
- `cmux-tui/crates/cmux-tui/tests/cli.rs`
- `cmux-tui/spec/inventory.json`
- `cmux-tui/spec/terminal-host.md`

No workflow or Fieldwork carrier file is present in the PR diff.

## Current-head source continuity

The prior canonical base was `61bc1e4a6d1c882d552199f4b2785ea45c177ae2`. Exact upstream `9e2dd509…` is 15 commits ahead of that base. A bounded compare established that none of the eight repair owner/test/spec files changed in those 15 commits.

That made a deterministic restack appropriate: the known first commit could be replayed directly and the canonical split-phase refiners could be applied without resolving owner-file conflicts.

## Target-executed verification

GitHub Actions run `33575479868`, job `100078394641`, completed successfully on Ubuntu 24.04 using the repository-pinned Rust toolchain and Zig.

The job executed these gates:

- exact source continuity against `9e2dd509…`;
- direct reconstruction of the synchronous owner-ACK commit on current upstream;
- full `cmux-tui-core` characterization for the synchronous baseline;
- application of the canonical split-phase refiners;
- exact four-file refinement-delta check;
- `cargo fmt` check;
- spec inventory checks;
- resource API boundary checks;
- binding generation check;
- focused receipted-input/owner-ACK tests;
- focused `resource_router::content` tests;
- a second full `cmux-tui-core` run requiring zero candidate-only failures compared with the characterized current-head synchronous baseline.

Every workflow step completed successfully.

## Byte-identity publication gate

The Actions verifier was deliberately read-only. Publication therefore used a separate independent tree reconstruction through the owned repository Git data API.

Starting from upstream tree `8506d088…`, the reviewed first-commit blobs produced tree `300ed73d…`. Replacing only the four split-phase refinement blobs produced tree `a56a8e82…`.

A separate read-only identity run, `33576673292`, job `100082049016`, then:

1. checked out exact upstream `9e2dd509…`;
2. cherry-picked the canonical synchronous first commit;
3. required `HEAD^{tree}` to equal `300ed73dd3d49872b67041dfd28462b3d8d6c934`;
4. reran all six canonical split-phase refinement scripts;
5. staged only the four refinement files;
6. required `git write-tree` to equal `a56a8e828a906b87df9169790b2beb053373648f`.

That identity job completed successfully. Only after this exact hash equality was established were the owned fork refs moved to the reconstructed commits.

## Repair semantics

The terminal-host protocol has additive `InputAck = 23` support. Current host discovery records advertise `supports_input_ack`; missing/false means receipted input is rejected before send.

For a supported hosted terminal, the confirmed path registers a targeted request, submits the input, releases the terminal runtime lock, and waits for the corresponding owner response. Pending requests and aggregate pending input bytes are bounded. The host publishes the ACK only after PTY `write_all` + `flush` succeeds.

The result classes are intentionally conservative:

- known pre-effect: no supported live owner, legacy host without ACK capability, bounded request-window exhaustion, request-id exhaustion/collision;
- indeterminate: partial/local PTY write, possible partial host-socket write, timeout/disconnect after a send may have occurred;
- success: authoritative terminal host confirmed the PTY write/flush boundary.

A crash after owner ACK but before the SQLite effect receipt commits can still recover as `mutation.indeterminate`. The candidate fixes false authoritative success; it does not claim exactly-once fate recovery without retained owner-side logical request identity.

## Controls retained

The original audit retained these controls:

- normal committed input: one PTY effect, exact-key replay returns the committed result without duplication;
- hosted terminal creation after mux crash: replacement adopts the same terminal host and converges to one committed creation;
- responsive terminal close with surviving host: replacement converges after the host resumes;
- interrupted input twins: effect-happened and effect-never-happened cases were deliberately indistinguishable after restart under the generic indeterminate contract.

Those controls keep the claim narrow: the defect was the success boundary for receipted hosted input, not the existence of generic `mutation.indeterminate` itself.

## Disposition

**Current-head repair candidate verified and retained as owned draft PR #16.**

The remaining decision is product/architecture judgment about accepting the additive owner-ACK protocol. No third-party upstream write has been made.
