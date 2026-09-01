# cmux raw-RPC target-alias fail-closed scout

Date: 2026-09-01  
Programme: high-leverage-open-source  
Upstream contact authorized: `false`

## Verdict

**Active golden candidate:** raw v2 RPC target-selector aliases can be silently ignored, widening an explicitly targeted request into focused-surface fallback.

The upstream report proves the read-side failure on released cmux: `surfaceId` is ignored by `surface.read_text` / `terminal.replay`, and the request returns `ok:true` with the human's focused terminal contents. Current `main` still has the same selector and dispatch seams. Source inspection also shows mutating terminal methods (`terminal.input`, `terminal.paste`, scroll, mouse) traverse the same raw parameter dictionary without a method-level unknown-key gate.

A current-main red regression is prepared on the owned fork to answer the high-consequence discriminator directly and safely: does `terminal.input` with bogus camelCase `surfaceId` inject a marker into an isolated focused `/bin/cat` terminal? The macOS verifier is queued. Until that executes, the write-side cross-target consequence remains `Unknown`; the read-side cross-target consequence is established by the upstream runtime report plus current-source continuity.

## Exact upstream state

Repository: `manaflow-ai/cmux`  
Issue: https://redirect.github.com/manaflow-ai/cmux/issues/10910  
Current-main revision: `eaa899cb20bd411019744fbd2bdedeb397f3070b`

The immediately preceding revision was `6b425641ae4d474e77854da535442af2a0d0a475`. The move to `eaa899cb20bd411019744fbd2bdedeb397f3070b` changes cmux-tui socket-start-lock handling; the selected raw-RPC owners and regression owner remain unchanged.

## Scores

Consequence: **5/5 for the established read leak; write-side escalation pending executable proof.** A misspelled explicit target can return a different human-focused terminal while claiming success. If the red mutation test executes as source inspection predicts, arbitrary text can also be delivered to the focused terminal under the same caller mistake.

Proofability: **5/5.** The discriminator is a single malformed selector and a marker in an isolated `/bin/cat` surface: pre-fix either the request succeeds and the marker appears in the focused surface, or it fails closed before terminal input executes.

## Current-source evidence

### Common selector vocabulary

`ControlCommandCoordinator.routingSelectors(_:)` recognizes only exact snake_case routing keys, including:

- `window_id`;
- `group_id`;
- `workspace_id`;
- `surface_id` / `terminal_id` / `tab_id`;
- `pane_id`.

A camelCase target such as `surfaceId` is therefore absent from the routing-selector view.

### Terminal mutation dispatcher

`ControlCommandCoordinator+MobileHost.swift` forwards `request.params` directly for raw terminal methods including:

- `terminal.input`;
- `terminal.replay`;
- `terminal.viewport`;
- `terminal.scroll`;
- `terminal.mouse`;
- `terminal.paste`.

There is no method-level unknown-key rejection at that dispatcher boundary.

### Socket execution-policy boundary

`TerminalController+ControlSocketAsync.swift` parses the v2 envelope, authorizes remote relay, selects worker/main execution policy, then dispatches the parsed request. `surface.read_text` has a worker-policy path, while `terminal.input` reaches the main path. A selector-alias gate placed immediately after strict envelope parsing can protect both lanes before either worker/main execution path sees the request.

### Existing project precedent

`MobileHostService+TicketAuthorization.swift` already rejects ignored alias parameters `workspaceID` and `terminalID` as unsafe. That is direct project precedent for the selected repair policy. `surfaceId` and `tabId` are absent from that narrow legacy list.

The repo does not currently expose a single method→allowed-parameter schema suitable for generic rejection of every unknown key. Therefore the selected candidate is deliberately narrower than the full upstream issue request: **fail closed on aliases of known target selectors**. Arbitrary unrelated unknown keys such as `totally_bogus_key` remain outside this slice unless a reusable schema owner is found.

## Overlap

At the scout check:

- issue 10910 was open with zero comments;
- no open PR was found claiming issue 10910 or the raw-RPC selector-alias rejection lane;
- neighboring targeting work reinforces the fail-closed policy but does not occupy this exact seam.

Severe claimed lane retained for triage: deep recursive process-tree crash https://redirect.github.com/manaflow-ai/cmux/issues/7848 scores approximately 5/5 consequence and 5/5 proofability, but serious implementations are already active, including https://redirect.github.com/manaflow-ai/cmux/pull/8802 and another current cap-based repair. Do not start a competing implementation without a new discriminator.

## Owned-fork state

Owned repo: `teamleaderleo/cmux`  
Exact-base branch: `fieldwork/upstream-main-eaa899cb`  
Candidate branch: `fieldwork/rpc-target-keys-10910`

Red commit: https://github.com/teamleaderleo/cmux/commit/702784686141f453454fea2afcda15c9b9573753

The red commit changes only the already-wired `cmuxTests/SocketTerminalBindingRegressionTests.swift`.

The regression creates an isolated live replacement `TerminalSurface` with `/bin/cat`, then sends an actual async socket-execution-policy request:

- method: `terminal.input`;
- params: bogus `surfaceId` plus a unique marker.

Desired behavior is `invalid_params` and marker absence. Pre-fix source inspection predicts `ok:true` plus marker delivery to the focused terminal; the test records that as an explicit failure if observed.

Fork-owned verifier workflow: https://github.com/teamleaderleo/cmux/blob/main/.github/workflows/fieldwork-rpc-target-verifier.yml  
Current red verifier run: https://github.com/teamleaderleo/cmux/actions/runs/33540062202

The workflow checks out the candidate directly on `macos-15`, selects the repo's CI Xcode, installs the same toolchain/dependencies used by cmux CI, resolves Swift packages, runs only `SocketTerminalBindingRegressionTests/camelCaseSurfaceAliasCannotInjectIntoFocusedTerminal`, then runs narrow repository guards.

## Candidate repair

Proposed repair owner: `Sources/TerminalController+ControlSocketAsync.swift`, immediately after strict v2 parsing and before relay authorization/execution-policy selection.

Proposed policy:

1. normalize incoming parameter keys by removing `_` and lowercasing;
2. compare against the canonical target-selector vocabulary;
3. when a noncanonical spelling normalizes to a known selector, return `invalid_params` naming the supplied and canonical keys;
4. preserve focus fallback when the caller truly supplies no targeting selector;
5. preserve unrelated method parameters and future extension keys.

This would catch `surfaceId`, `surfaceID`, `workspaceId`, `workspaceID`, `terminalId`, `terminalID`, `tabId`, `paneId`, and corresponding capitalization variants while keeping exact canonical snake_case unchanged.

## Evidence labels

- current upstream SHA: `source-read`;
- released read-side cross-target behavior: `upstream-runtime-report`;
- current selector/dispatcher continuity: `source-read`;
- write-side focused-terminal injection: **Unknown / executable red test queued**;
- candidate regression: `fork-authored`;
- repair: **prepared conceptually; production commit intentionally withheld until red execution**;
- upstream overlap: `github-search`;
- upstream mutation/contact: absent.

## Stop condition

Do not promote or submit the production fix until the red discriminator either executes and proves the mutation path, or the lane is rescoped with the failed/blocked proof retained. Upstream contact remains unauthorized.
