# cmux raw-RPC target-alias fail-closed scout

Date: 2026-09-01  
Programme: high-leverage-open-source  
Upstream contact authorized: `false`

## Verdict

**Active golden candidate:** raw v2 RPC target-selector aliases can be silently ignored, widening an explicitly targeted request into focused-surface fallback.

The upstream report proves the read-side failure on released cmux: `surfaceId` is ignored by `surface.read_text` / `terminal.replay`, and the request returns `ok:true` with the human's focused terminal contents. Current `main` retains the same selector and dispatch behavior. Source inspection also shows mutating terminal methods (`terminal.input`, `terminal.paste`, scroll, mouse) traverse the same raw parameter dictionary.

The owned fork now carries a three-commit candidate on exact current upstream: an isolated app-host mutation regression, a pure parser regression, then a parser-level fail-closed repair. Portable red→green proof is wired against immutable commit SHAs; an app-host red→green lane separately attempts to prove the wrong-terminal write consequence.

Until the app-host lane executes through the current app target, the write-side cross-target consequence remains `Unknown`; the read-side cross-target consequence is established by the upstream runtime report plus current-source continuity.

## Exact upstream state

Repository: `manaflow-ai/cmux`  
Issue: https://redirect.github.com/manaflow-ai/cmux/issues/10910  
Current-main revision: `eaa899cb20bd411019744fbd2bdedeb397f3070b`

The immediately preceding revision was `6b425641ae4d474e77854da535442af2a0d0a475`. The move to `eaa899cb20bd411019744fbd2bdedeb397f3070b` changes cmux-tui socket-start-lock handling; the selected raw-RPC owners and regression owners remain unchanged.

## Scores

Consequence: **5/5 for the established read leak; write-side escalation pending executable proof.** A misspelled explicit target can return a different human-focused terminal while claiming success. If the mutation regression executes as source inspection predicts, arbitrary text can also be delivered to the focused terminal under the same caller mistake.

Proofability: **5/5.** The parser defect has an exact one-request discriminator, and the write-side discriminator is a unique marker in an isolated `/bin/cat` surface.

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

### Common parser choke point

`ControlRequestParser` is shared by the v2 control path before worker/main execution selection. Its pre-fix behavior accepts an arbitrary params dictionary and therefore loses the distinction between “no target supplied” and “caller supplied a target under an ignored spelling.”

The candidate repair now lives here rather than in the app dispatcher. That protects sync/async and worker/main paths before focus fallback can occur.

### Existing project precedent

`MobileHostService+TicketAuthorization.swift` already rejects ignored alias parameters `workspaceID` and `terminalID` as unsafe. That is direct project precedent for the selected repair policy. `surfaceId` and `tabId` were absent from that narrow legacy list.

The repo does not currently expose a single method→allowed-parameter schema suitable for generic rejection of every unknown key. Therefore this candidate is deliberately narrower than the full upstream issue request: **fail closed on aliases of known target selectors**. Arbitrary unrelated unknown keys such as `totally_bogus_key` remain outside this slice.

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
Owned draft PR: https://github.com/teamleaderleo/cmux/pull/5

Exact three-commit sequence:

1. app-host red regression: https://github.com/teamleaderleo/cmux/commit/702784686141f453454fea2afcda15c9b9573753
2. parser red regression: https://github.com/teamleaderleo/cmux/commit/0f4e0144398cfda3efd096bc68a560f7b9f2e220
3. production repair: https://github.com/teamleaderleo/cmux/commit/a36ffbe0b8c3acedeb7ab82454ae6cec65ec5d06

The candidate is exactly three commits ahead of upstream and changes five files. Fork-only CI remains on the fork default branch and is absent from the candidate diff.

### App-host discriminator

The first red commit changes only the already-wired `cmuxTests/SocketTerminalBindingRegressionTests.swift`.

The regression creates an isolated live replacement `TerminalSurface` with `/bin/cat`, then sends an actual async socket-execution-policy request:

- method: `terminal.input`;
- params: bogus `surfaceId` plus a unique marker.

Desired behavior is `invalid_params` and marker absence. Pre-fix source inspection predicts `ok:true` plus marker delivery to the focused terminal; the test records that exact observation as an explicit failure if it occurs.

### Pure parser discriminator

The second red commit adds a package test proving `terminal.input` with `surfaceId` must fail strict request parsing. Pre-fix `ControlRequestParser` accepts that request.

This provides a portable exact discriminator independent of the current app-target compilation state.

## Implemented repair

Production owner: `Packages/macOS/CmuxControlSocket/Sources/CmuxControlSocket/Wire/ControlRequestParser.swift`, with matching parse-error and response-encoder additions.

Implemented policy:

1. normalize incoming parameter keys by removing `_` and lowercasing;
2. compare against the canonical target-selector vocabulary;
3. when a noncanonical spelling normalizes to a known selector, reject the v2 request before domain dispatch;
4. strict parsing reports an `unsupportedTargetAlias` parse/validation error carrying request id, supplied key, and canonical key;
5. wire encoding returns `invalid_params` and names the canonical snake_case spelling;
6. lenient parsing also refuses target aliases so the worker-style lenient path cannot silently widen them;
7. true no-target focus fallback remains available;
8. unrelated extension keys remain accepted.

Covered canonical selector families:

- `window_id`;
- `group_id`;
- `workspace_id`;
- `surface_id`;
- `terminal_id`;
- `tab_id`;
- `pane_id`.

Examples rejected by normalization include `surfaceId`, `surfaceID`, `workspaceId`, `workspaceID`, `terminalId`, `terminalID`, `tabId`, and `paneId`.

## Fork-owned verification

Workflow: https://github.com/teamleaderleo/cmux/blob/main/.github/workflows/fieldwork-rpc-target-verifier.yml  
Current immutable-SHA verifier run: https://github.com/teamleaderleo/cmux/actions/runs/33541421261

The workflow now pins all evidence revisions explicitly:

- upstream base `eaa899cb20bd411019744fbd2bdedeb397f3070b`;
- app red `702784686141f453454fea2afcda15c9b9573753`;
- parser red `0f4e0144398cfda3efd096bc68a560f7b9f2e220`;
- green `a36ffbe0b8c3acedeb7ab82454ae6cec65ec5d06`.

Portable Ubuntu lane compiles the real `JSONValue`, `ControlRequest`, parse-error, parser, call-result, and response-encoder sources directly. Required red→green observations are:

- red parser: `surfaceId` accepted;
- green parser: same request rejected;
- green wire response: `invalid_params`;
- green canonical `surface_id`: accepted;
- green unrelated `totally_bogus_key`: accepted.

Separate macOS app-host jobs pin the red app commit and green candidate. The red job succeeds only if the focused-terminal injection regression fails for its intended marker-injection reason; a compile blocker is therefore retained as blocked evidence rather than misclassified as a reproduced mutation. The green job requires the focused regression to pass.

Current run state at this record update: queued.

## Evidence labels

- current upstream SHA: `source-read`;
- released read-side cross-target behavior: `upstream-runtime-report`;
- current selector/dispatcher continuity: `source-read`;
- parser red: `fork-authored / execution queued`;
- app-host write-side injection: `Unknown / execution queued`;
- production repair: `fork-authored`;
- candidate diff/ancestry: `github-compare`;
- upstream overlap: `github-search`;
- upstream mutation/contact: absent.

## Stop condition

Keep upstream untouched until the portable red→green discriminator executes successfully. Treat write-side focused-terminal injection as `Unknown` unless the app-host red lane reaches the regression and fails for the exact marker-injection reason. Upstream contact remains unauthorized.
