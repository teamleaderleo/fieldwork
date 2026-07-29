# ChatGPT Connector and Developer-MCP Coexistence Field Trial

## In simple words

- **What is this?** A controlled ChatGPT journey alternating the official GitHub connector with the Stensibly developer MCP.
- **Where does it sit?** It tests the live boundary among ChatGPT catalogue selection, policy, executable routing, Stensibly server completion, and result delivery to the conversation.
- **What was tested?** Two complete reversible mutation lifecycles, repeated connector reads and writes, a host context-summary boundary, and catalogue rediscovery.
- **Why could anyone care?** The active incident can strand work or leave a mutation outcome unclear when one tool family disappears during a long conversation.
- **Current answer:** Both tool families stayed executable throughout this trial. Every mutation returned a visible typed result and was confirmed by a separate read. No first divergence appeared. Disconnect/reconnect and application restart remain separate interactive controls.

State: `ready-for-synthesis`

Worker: Aster (`agent:gpt-5.6-thinking-fw46`)

Programme: #14

Campaign: #31

Lane issue: #46

Target hub: #8 for shared comparison vocabulary

Owned testbed: `teamleaderleo/stensibly`

Claim scope: `integration`

Upstream contact authorized: `false`

Retrieval boundary: 2026-07-29 through 2026-07-30 +08:00

Durable receipt: [`artifacts/checkpoints.json`](artifacts/checkpoints.json)

## Assignment and ownership

The lane was claimed on issue #46 before the test journey began. The claim used operation identity `fw46-claim-20260730T0050+0800-a1` and fenced writes to:

```text
campaigns/0002-tool-surface-continuity/lanes/L08-chatgpt-coexistence-field-trial/
```

This branch began from draft campaign PR #51 at commit `aa72bd513f6664dc67517dabd9b03b4f051d8460`.

The exercised Stensibly source boundary was `teamleaderleo/stensibly@20241e668fb493b7f389df8b9df7f229bcadff68`. The pure effective-tool-surface contract referenced by issue #544 was pinned at `7690ca0022048443fae9ec9d9eb3fd17ac1c58b6`.

## Question

During repeated alternating use of an official GitHub connector and the Stensibly developer MCP, which observable layer changes first, which recovery restores capability, and which symptoms resemble public Codex lifecycle failures without treating normal ChatGPT private implementation as established?

## Environment

| Field | Value |
| --- | --- |
| Product | ChatGPT |
| Model | GPT-5.6 Thinking |
| Product build | Host field unavailable |
| Profile | Host field unavailable |
| Transport | Host field unavailable |
| Official connector | GitHub |
| Developer MCP | Stensibly |
| Initial discovered function count | GitHub 89; Stensibly 25 |
| Test project | `oauth-dogfood` |
| Mutation policy | Unique idempotency identity for every write |
| Ambiguity policy | Stop and reconcile by read before any replay |

The host exposed callable tool declarations and typed results. It did not expose the raw per-turn model advertisement, internal router-registration table, policy snapshot, transport session, or request/prewarm identifiers. Those fields remain `Unknown` in this report.

## Safety and privacy boundary

The trial used owned public repositories and dedicated bounded test records. Every test item was completed after verification. Retained evidence contains owned repository identifiers, stable operation identities, item/event/artifact/comment identities, versions, claim generations, class counts, typed states, and workspace fingerprints.

Credentials, access tokens, private prompts, provider payloads, account identities, opaque internal policy data, and secret values were excluded.

## Controlled journey

The journey alternated between these surfaces:

```text
GitHub read
→ Stensibly survey
→ Stensibly create
→ read-after-write
→ GitHub read
→ Stensibly claim
→ read-after-write
→ GitHub read
→ Stensibly event
→ read-after-write
→ GitHub read or write
→ Stensibly artifact attachment
→ read-after-write
→ Stensibly complete
→ final reread
→ catalogue rediscovery
→ GitHub read
→ Stensibly survey
```

Every mutation had a fresh logical identity. A second mutation waited for the prior mutation's separate read receipt.

## Baseline

**Observed:** The initial Stensibly workspace survey succeeded with fingerprint:

```text
sha256:9091d5ebc7a6045c0f5b2d7162b073bf40a853377cca34ea5c00af1b6e5419fe
```

The survey returned 20 total records across three projects, including three earlier fresh- or same-conversation coexistence lifecycle completions in `oauth-dogfood`.

**Observed:** The official GitHub connector read Fieldwork and Stensibly repository files, issues, comments, and PR metadata before the first Stensibly mutation.

**Observed:** Initial tool discovery exposed 89 GitHub connector functions and 25 Stensibly developer-MCP functions to the current conversation.

## Lifecycle A — sustained same-conversation use

Run identity: `fw46-chatgpt-20260730T0054+0800-a`

Stensibly item: `item_js795cyshevj1e2nnkr7dp8hks8be4pb`

| Step | Operation identity | Typed result | Read-after-write receipt |
| --- | --- | --- | --- |
| Create | `fw46-a-create-20260730T0054+0800` | Success | Ready, version 1 |
| Claim | `fw46-a-claim-20260730T0055+0800` | Success | Active, claim generation 1, version 2 |
| Event | `fw46-a-event-20260730T0056+0800` | Success, event `evt_jn73gyfy1202ky5839wz8fmsa58bf6d1` | Event present, version 3 |
| Artifact | `fw46-a-artifact-20260730T0057+0800` | Success, artifact `art_jd7cjkw6p6v6eym6xq690x79c18bephg` | Artifact list contained the owned Fieldwork issue |
| Complete | `fw46-a-complete-20260730T0058+0800` | Success | Done, claim generation 2, version 6 |

GitHub repository and issue reads succeeded between Stensibly segments. The item reached terminal `done` state and preserved the exact event and artifact identities.

First divergence: **none observed**.

## Lifecycle B — context-summary boundary

Run identity: `fw46-chatgpt-20260730T0059+0800-b`

Stensibly item: `item_js7accmdtt789d9s6rydsezypd8bfr4e`

A host context-summary boundary occurred during this lifecycle. The retained conversation state continued with the prior item identities and exact next action. The first operations after the boundary tested both tool families.

| Step | Operation identity | Typed result | Read-after-write receipt |
| --- | --- | --- | --- |
| Create | `fw46-b-create-20260730T0059+0800` | Success | Ready, version 1 after the boundary |
| GitHub read | direct namespace invocation | Success | Stensibly README returned from current source |
| Claim | `fw46-b-claim-20260730T0100+0800` | Success | Active, claim generation 1, version 2 |
| GitHub issue-history read | direct namespace invocation | Success | Current issue #544 comments returned |
| Event | `fw46-b-event-20260730T0101+0800` | Success, event `evt_jn73e4d9y8z98jcm5185sqsn718bf75q` | Event present, version 3 |
| GitHub comment | `fw46-b-github-comment-20260730T0102+0800` | Success, comment `5120954375` | Issue comment reread returned the exact body |
| Artifact | `fw46-b-artifact-20260730T0103+0800` | Success, artifact `art_jd7dc5mf8kaend3mgjb5c5nr058bfk3m` | Artifact list contained the GitHub comment receipt |
| Complete | `fw46-b-complete-20260730T0104+0800` | Success | Done, claim generation 2, version 5 |

First divergence: **none observed**.

## Refresh and rediscovery control

The available GitHub and Stensibly resources were rediscovered after both lifecycles. The next GitHub issue read succeeded. The next Stensibly survey succeeded with project-scoped fingerprint:

```text
sha256:f694997636579d76fcda780a59668c07ee55690d73dbb930193d44c319003571
```

The final `oauth-dogfood` survey showed six total items, all six in `done`, with zero ready, active, or blocked items. Both current lifecycle items appeared in `recentDone` with their terminal summaries.

Control result: **passed**.

## Layer-by-layer result

| Layer | Observable in this host? | Result | Evidence boundary |
| --- | --- | --- | --- |
| Catalogue | Partly | Healthy before and after rediscovery | Function counts and callable namespaces were visible; raw host catalogue snapshot was unavailable |
| Policy | Partly | No rejection during the journey | Calls avoided the earlier `developer MCPs` restriction; opaque policy state was unavailable |
| Binding | Indirectly | Executable for every tested call | Successful dispatch proves a current binding for that operation only |
| Router registration | Indirectly | Executable for every tested call | Internal registration inventory was unavailable |
| Model advertisement | Partly | Tool declarations remained usable | Exact serialized per-turn advertisement was unavailable |
| Execution | Yes | All tested reads and writes executed | Typed tool results were visible |
| Server completion | Yes for Stensibly receipts | Every Stensibly write returned stable item/event/artifact state | Provider-internal traces were unavailable |
| Client result delivery | Yes | Every result reached the conversation | Separate reads confirmed the durable outcome |

The first failing layer could not be located because this run produced no failure.

## Controls and limitations

| Control | Status | Interpretation |
| --- | --- | --- |
| Repeated same-conversation lifecycle | Passed twice | Both tool families remained executable |
| Safe long-context/context-summary boundary | Passed | Reads and mutations succeeded after the boundary |
| Catalogue refresh and rediscovery | Passed | Both namespaces remained executable after rediscovery |
| Fresh conversation | Corroborated by prior owned records | The current conversation cannot spawn a second independent ChatGPT conversation |
| Disconnect/reconnect | Unexercised | The available control plane exposes no reconnect command |
| Application restart | Unexercised | The current conversation cannot restart its host application |
| Stensibly first-party GitHub provider | Unexercised | This trial used the official ChatGPT GitHub connector |

The prior owned fresh-conversation records are:

- `item_js7fqx6zkm5a30zjxhsdjyzpvn8bfyx5`
- `item_js7fm47hgdh39mgfq7yaa4dfrh8bffqc`
- `item_js7drd7jabgr27cjwdehfw0dds8be4qs`

They support recovery and repeatability context. The current lane keeps their evidence separate from its own two lifecycles.

## Strongest finding

**Observed:** An official ChatGPT GitHub connector and the Stensibly developer MCP coexisted through two complete mutation journeys, sustained alternating use, one host context-summary boundary, post-boundary mutation on both sides, and catalogue rediscovery. Every mutation returned a visible typed success and a stable operation or result identity. A separate read confirmed every durable effect.

**Observed negative result:** This trial did not reproduce connector eviction, a developer-MCP-only policy transition, schema-without-execution behavior, silent mutation disappearance, or client-delivery loss.

**Inferred:** The active incident is intermittent or depends on a lifecycle trigger absent from this journey, with disconnect/reconnect and restart still carrying the highest remaining information value.

## Competing hypotheses after the negative result

1. **Conversation policy transition after reconnect.** A real disconnect/reconnect could recreate the earlier official-connector restriction while the developer MCP remains present.
2. **Stale host catalogue after application restart or version change.** Restart could rebuild one tool family from a newer catalogue while retaining affected conversation state.
3. **Intermittent result delivery failure.** Server completion could succeed while the client loses the visible result; unique identities and immediate reconciliation remain the decisive guard.
4. **Earlier incident repaired by subsequent deployment.** The current Stensibly revision includes newer release-manifest, effective-surface persistence, and idempotency work. This trial alone cannot attribute recovery to any one change.
5. **Load-, timing-, or auth-refresh-dependent failure.** The current run stayed within bounded test load and did not observe token-refresh internals.

## Change thesis

**Current behaviour:** In this controlled run, ChatGPT kept the official GitHub connector and Stensibly developer MCP executable together, including after a context-summary boundary and rediscovery.

**Consequence:** The sustained-use journey can complete safely when every mutation has a unique identity and a read reconciliation step. The earlier incident still lacks a deterministic trigger.

**Proposed improvement:** Retain the effective-surface checkpoint and operation-reconciliation contract as the diagnostic baseline. Run disconnect/reconnect and restart as explicit host controls. Add code only after one control produces a failing receipt with an attributable owning boundary.

**Evidence:** Two completed items, typed operation identities, separate read receipts, one post-boundary GitHub mutation, Stensibly event/artifact histories, and before/after workspace fingerprints.

**Boundary:** The evidence establishes one owned ChatGPT/Stensibly integration journey. It does not establish normal ChatGPT internals, Codex implementation identity, ecosystem prevalence, or reconnect/restart behavior.

## Recovery packet for a future affected conversation

A fresh conversation can continue without replaying an ambiguous mutation by carrying:

```text
Fieldwork issue: teamleaderleo/fieldwork#46
Campaign: teamleaderleo/fieldwork#31
Last confirmed run and item identity
Last confirmed operation/idempotency identity
Last confirmed item version and claim generation
Last confirmed GitHub comment/issue/commit receipt
Pending exact next action
Current Fieldwork and Stensibly revisions
Required tool classes: official GitHub connector + Stensibly developer MCP
First action: rediscover both namespaces and run benign reads
Mutation rule: reconcile the prior identity before any retry
Privacy rule: retain counts, digests, typed states, and owned references only
```

## Ranked branch candidates

1. **Accept this lane as a healthy negative result.** Feed the receipt vocabulary and boundary into campaign synthesis and diagnostics lane #43.
2. **Run an interactive disconnect/reconnect continuation.** Use a fresh run identity, benign reads first, then one bounded lifecycle. This is the strongest remaining control for the symptom recorded in [Stensibly sustained-use incident #490](https://redirect.github.com/teamleaderleo/stensibly/issues/490).
3. **Run an application restart continuation.** Preserve the affected conversation reference and compare the first post-restart catalogue and executable smoke tests.
4. **Instrument only after a failing control.** Capture catalogue, policy result, executable dispatch, server receipt, and client delivery under one logical operation identity.

## Negative results and dead ends

- Repeated same-conversation use produced no tool-family loss.
- The context-summary boundary produced no capability loss.
- Catalogue rediscovery produced no capability loss.
- The current connector control plane offered no disconnect/reconnect or application-restart operation.
- Exact model-advertised and router-registered inventories were unavailable from the host.
- No code repair is justified by this run alone.

## Cleanup and rollback

Both created Stensibly items reached terminal `done` state. No active claims, blocked work, or pending test mutations remained in `oauth-dogfood`. The final survey reported zero ready, active, and blocked records.

The Fieldwork changes are research records on a dedicated branch. Rollback is branch deletion or PR closure.

## Disposition

State: `ready-for-synthesis`

Recommendation: retain the result as an integration-scope healthy negative result. Schedule reconnect and restart only through a host surface that exposes those controls. Preserve the current issue and item identities as the clean baseline for the first future divergence.

Evidence labels used: `Observed`, `Documented`, `Inferred`, `Unknown`.

Upstream contact remains unauthorized.
