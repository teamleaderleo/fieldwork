# Approaches — Playwright MCP remote and shared-browser authority

## In simple words

The runtime behavior is deliberate and coherent: HTTP is opt-in, localhost is the default, and shared browser context is explicit. The selected contribution leaves that behavior intact and improves the CLI help at the exact point where an operator chooses broader network reach or shared browser state.

## Selected approach

### A. Three-string CLI help clarification

Change only `packages/playwright-core/src/tools/mcp/program.ts`:

1. clarify that `--allowed-hosts` protects against DNS rebinding and does not authenticate clients;
2. tell `--host` users to protect non-loopback HTTP with an authenticated reverse proxy or equivalently access-controlled trusted network boundary;
3. tell `--shared-browser-context` users that every accepted client shares and can control the same browser context, including tabs, cookies, storage, and page state.

Why selected:

- matches the runtime direction stated in upstream issue #41915;
- addresses the operator confusion found by source reading and execution;
- preserves all defaults and behavior;
- costs one file and three descriptions;
- can be validated through build, generated help, lint, and the existing HTTP suite;
- keeps adjacent shutdown-route repair separate.

Current source: `teamleaderleo/playwright@745b4dea96ac64eeb1e92d9ce4525b995e64909f`.

## Considered alternatives

### B. Add built-in bearer-token authentication

Status: `rejected for this unit`

A public report proposed random bearer-token authentication for HTTP/SSE. Upstream issue #41915 was closed as working as intended: HTTP is opt-in, localhost-bound by default, and broader binding is deliberate.

A token design would introduce secret generation, display, transport, configuration, rotation, compatibility, and proxy-composition decisions. The retained evidence establishes an operator-visible authority boundary, not a requirement for a new authentication protocol.

Reopening trigger: upstream explicitly requests built-in authentication or a separate campaign establishes a target-supported protocol and compatibility model.

### C. Reject non-loopback HTTP without an authentication option

Status: `rejected`

This would change existing deliberate remote behavior and create a new fail-closed composition rule. It conflicts with the current maintainer statement that non-loopback binding is an intentional local-development-server trust decision.

Reopening trigger: upstream changes the contract or documents non-loopback HTTP as unsupported without an integrated credential mechanism.

### D. Ban `--shared-browser-context` with non-loopback HTTP

Status: `rejected`

The retained matrix shows coherent shared behavior and bounded cleanup after explicit operator choices. A prohibition would remove a supported composition without evidence that documentation and deployment access control are insufficient.

Reopening trigger: target execution reveals cross-session behavior outside the documented shared BrowserContext contract or upstream declares the combination unsupported.

### E. Add only an `--allowed-hosts` authentication warning

Status: `rejected as incomplete`

This would separate Host validation from authentication but leave the deliberate non-loopback deployment boundary and shared-context authority implicit. All three option descriptions participate in the operator decision.

### F. Add a README security section instead of CLI help

Status: `rejected as the sole change`

A guide could provide richer deployment examples, yet `--help` is generated from `program.ts` and sits directly beside the flags. The one-file CLI change reaches operators at configuration time and remains synchronized with the option surface.

A future guide update could complement this patch if maintainers request it.

### G. Open a new upstream issue first

Status: `available policy route; not selected in the draft`

Playwright requires issues for most contributions and exempts minor documentation fixes. Existing issue #41915 already records the authentication question and maintainer direction. The packet therefore prepares a direct documentation PR while flagging the unsolicited-PR policy for human judgment.

Reopening trigger: a human reviewer judges the wording consequential enough to seek explicit approval before submission.

### H. Reuse the historical wording unchanged

Status: `rejected after review`

Historical wording:

```text
Non-loopback HTTP should be protected by a trusted authenticated network boundary or reverse proxy.
```

A plain reverse proxy could satisfy the final phrase grammatically. The current candidate makes authentication or equivalent access control apply to the deployment boundary in either form.

The historical finding also used a whole-record `target-executed` label and promoted cookies/storage/page-state to direct execution. The packet now keeps evidence class per claim.

## Approach history

### Source-map phase

Fieldwork issue #371 and PR #374 separated bind authority, Host validation, client authentication, session identity, and browser-context sharing. Early review corrected a plan that combined socket reachability with Host-header rejection.

### Behavior carrier phase

PR #375 ran the complete upstream HTTP suite plus two Fieldwork controls. Its first run, `30633035608`, stopped before target installation because the workflow checked a synthetic merge ref while expecting the branch head. The repaired exact-head run `30633739476` passed 19/19.

### Historical help carrier phase

PR #377 had two bounded carrier failures:

1. run `30634283260`: zero-context patch rejected by ordinary `git apply` before target installation;
2. run `30634703157`: patch applied and target built, but line-wrapped Commander output defeated literal line-based `grep`.

The final run `30634831167` used contextual hunks and whitespace-normalized semantic assertions and passed.

### Claim-calibration review

Review `4830037719` found four repairs:

- remove the whole-record evidence maximum;
- classify cookies/storage/general page control as source-backed unless directly executed;
- replace broad “safe local defaults” wording with precise network-reach claims;
- remove ambiguity from the reverse-proxy recommendation.

The current source branch incorporates the wording repairs. This packet incorporates the evidence repairs.

### Current-source materialization

The source branch was created directly from current public head `15b1aec478d90f0293dae7b7b6dafd494d9f0154`. Commit `745b4dea96ac64eeb1e92d9ce4525b995e64909f` changes one file and three descriptions. Owned-fork PR #38 carries temporary validation only.

## Negative results

- No equivalent open issue or PR implementing the three help clarifications surfaced on 2026-08-01.
- Current public source still contains the original three descriptions.
- The retained evidence provides no basis for a vulnerability label, public-exploitability claim, deployment-frequency claim, or built-in-authentication requirement.
- The retained matrix directly exercises tabs/session continuity/cleanup; it does not directly exercise cookie or origin-storage readback.
- Adjacent shutdown-route authority is a separate behavior change owned by Fieldwork #404 and upstream unit 18.

## Decision

Keep approach A as the sole candidate for unit 25. A failed current build, generated-help assertion, lint check, or HTTP suite moves the unit to `REPAIR`. A green exact-source receipt moves it to `READY` for independent review, with public submission still requiring separate authority.
