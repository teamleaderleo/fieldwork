# Supabase campaign review refresh — 2026-07-30

State: `ready-for-review`

Campaign: #78

Central candidate: #148

Parent scout: #21

Fieldwork PR: #91

Owned experiment: `teamleaderleo/supabase-js#1`

Review date: `2026-07-30`

Upstream contact authorized: `false`

Upstream contact performed: `false`

## In simple words

Fieldwork now has a dedicated central candidate issue for the Supabase refresh result. Reviewers can begin at #148, see the exact evidence heads and decision request, and then follow the durable campaign documents or owned experiment.

A fresh public-source check found no new Supabase JS commit after the campaign's pinned source. Two open auth lifecycle proposals remain important rebase constraints, and one additional mobile-session report was narrowed to an application cookie-write problem rather than a client defect.

## Coordination update

### Central candidate

Candidate #148 now represents the preferred reviewable contract:

> During `TOKEN_REFRESHED` notification, allow a call carrying the rotated event token to consume the committed event result, keep the initiating operation waiting for all listeners, preserve old-token joined-caller timing, isolate listener exceptions from committed refresh success, and continue propagating notification-transport failures.

The candidate records:

- campaign #78 and parent scout #21;
- canonical Fieldwork evidence PR #91;
- owned experiment `teamleaderleo/supabase-js#1`;
- exact evidence heads;
- `target-executed` focused evidence;
- `full-gate` ordinary repository pull-request CI;
- the absent production branch;
- an exact review ask and production-branch gate;
- upstream contact as unauthorized.

This follows the candidate-node convention now visible in recent Fieldwork issues: one consequential proposal, one independent disposition, and a narrow next transition.

### Coordination graph dogfood

The current campaign can be represented as:

```text
scout #21
  -> campaign #78
     -> Fieldwork evidence PR #91 @ exact head
        -> owned experiment PR teamleaderleo/supabase-js#1 @ f589f012...
           -> focused auth-js workflow 30485952998
           -> SDK Compliance 30485953401
           -> ordinary repository PR CI 30485953213
              -> central candidate #148
```

Candidate #148 requires an exact-head technical disposition. A later production branch, merge decision, or upstream-contact decision must remain a separate node.

Issue #138 should treat the experiment PR as upstream-fork research rather than a production merge candidate. The Fieldwork branch is the canonical durable evidence surface; the owned Supabase PR is a two-variant design lab.

## Exact-head self-review

### Work class

- Fieldwork PR #91: evidence and documentation.
- Owned Supabase PR #1: upstream-fork research.
- Candidate #148: candidate contract and review request.
- Production implementation: absent.

### Canonical surfaces

- Durable evidence branch: `campaign/0008-supabase-auth-refresh-settlement`.
- Experiment branch: `fieldwork/auth-refresh-settlement-lab`.
- Central review surface: #148.

### Evidence class

- Source and history audit: `source-read`.
- Dependency-free settlement model: `model-executed`.
- Focused real auth-js matrix: `target-executed`.
- Ordinary Supabase repository pull-request workflow at the exact experiment head: `full-gate` for the checks declared by that workflow.
- Live Auth service, hosted project, real SSR framework, browser BroadcastChannel, and React Native behavior: unexecuted integration gates.

### Current disposition

**Self-review disposition: ACCEPT as a review-ready candidate contract; HOLD production promotion for an independent exact-head review and the named integration gates.**

The strongest supported conclusion is the relative contract ranking, not a completed production correction.

### Staleness and merge boundary

- Supabase source pin remains current at this refresh.
- Fieldwork PR #91 has accumulated evidence commits and must be reviewed at its final head rather than through an earlier disposition.
- The branch may require a current-main rebase before merge; rebasing would expire exact-head review receipts unless the reviewer records semantic identity across the new fence.
- Candidate #148 must be updated when the canonical Fieldwork head changes.

## Supabase source freshness check

The current Supabase JS master head remains [`63318987365bbcea2c31a00b62cbb95b21083ad5`](https://redirect.github.com/supabase/supabase-js/commit/63318987365bbcea2c31a00b62cbb95b21083ad5), the source revision already used by the campaign.

No later merged commit changes auth refresh notification settlement. The current client ordering and residual reentry note therefore remain the correct source baseline for candidate #148.

## Open auth lifecycle proposals

### Offline fail-fast and reconnect

The [offline refresh and reconnect proposal](https://redirect.github.com/supabase/supabase-js/pull/2568) remains open at `ed238764a11889551d3c1a34c30174135b317af0`.

Its current scope includes:

- stopping retry/backoff after one failed default-transport probe when the browser affirmatively reports offline;
- preserving custom transport and loopback behavior;
- clearing refresh-failure cooldown on reconnect;
- restarting an active auto-refresh tick;
- guarding listener and timer setup against disposal races.

Interaction with candidate #148:

- it changes retry, reconnect, cooldown, ticker, initialization, and disposal paths;
- it does not change the ordering between session commit, `TOKEN_REFRESHED` listener completion, and shared refresh settlement;
- a production settlement branch must preserve its disposal and reconnect guards if it lands;
- the settlement tests should add an offline/reconnect control only after rebasing, rather than absorbing this proposal into the first patch.

### Bounded automatic refresh failures

The [automatic refresh failure-limit proposal](https://redirect.github.com/supabase/supabase-js/pull/2573) remains open at `420df5f3b9d009816ab8ba4abecb987a1aa1362e`.

It proposes:

- an opt-in `maxAutoRefreshFailures` setting;
- a new `TOKEN_REFRESH_FAILED` event;
- stopping the ticker after the configured count;
- resetting the count after successful refresh.

Interaction with candidate #148:

- a new auth event expands the subscriber matrix and should retain the existing non-refresh listener-error behavior;
- success-path listener-error isolation for `TOKEN_REFRESHED` must not silently apply to `TOKEN_REFRESH_FAILED`;
- a production branch should include a control proving failure-count reset still occurs after a committed refresh whose application listener throws;
- the candidate should avoid changing default retry policy or adopting the new public event before upstream decides that proposal.

Neither open proposal has current maintainer acceptance recorded. They remain rebase and compatibility inputs, not dependencies that block review of the settlement contract.

## Newly narrowed public report

The [iOS intermittent null-session report](https://redirect.github.com/supabase/supabase-js/issues/1560) initially appeared adjacent to mobile refresh recovery.

Maintainer review identified an empty cookie `setAll()` implementation, so refreshed server cookies were not persisted. The reporter later supplied a writable cookie adapter and confirmed the problem was resolved.

Assessment:

**Reject as evidence of a current auth-js settlement defect.**

Useful lesson:

- successful refresh in one client instance does not establish that a server framework persisted response cookies;
- SSR integration trials must inspect the adapter's write path and final response, not only the auth result;
- a real campaign integration test should pair one correct writable-cookie control with one intentionally non-writing negative control.

This result strengthens the production gate without expanding candidate #148.

## Adjacent issue-map corrections

The earlier adjacent map remains accurate with these additions:

1. add the resolved cookie-write report as a narrowed application/adapter case;
2. keep the React Native Realtime persisted-session report as the highest-value current-version runtime characterization;
3. keep `getSession()` performance as a remeasurement candidate after lockless coordination;
4. retain generated-types and Bigint work outside auth settlement;
5. treat both open refresh lifecycle proposals as rebase constraints;
6. retain successful-response refresh headers as a separate observability design.

## Review recommendations

### Candidate #148

Request one independent exact-head review with:

- complete current diff of Fieldwork PR #91;
- complete current diff of the owned experiment PR;
- workflow receipts bound to the experiment head;
- verification that ordinary PR CI actually ran the claimed package and compatibility checks;
- confirmation that the experiment PR is research rather than the production branch;
- one explicit `ACCEPT`, `REPAIR`, `HOLD`, `EXECUTE`, or `REJECT` disposition.

### Fieldwork process PR #143

The proposed evidence classes and exact-head expiry rules fit this campaign. One useful wording refinement for the manual contract is to distinguish:

- `full-gate` for the repository's declared gate at one exact head;
- integration properties that the repository gate does not exercise.

Candidate #148 is a clean dogfood case: it has full repository PR CI and still requires real SSR, browser, and React Native integration evidence.

### Coordination issue #138

Add this candidate graph as another first-slice case. It demonstrates:

- one campaign producing one preferred candidate after a two-variant experiment;
- evidence PR and experiment PR having different work classes;
- exact-head target and full-gate receipts;
- a production branch absent despite green experiment CI;
- integration gates remaining open;
- later upstream authorization remaining independent.

## Next useful work

1. obtain an independent exact-head disposition on #148;
2. rebase only when a clean production branch is authorized;
3. add the Realtime token-handoff regression to the production branch, not the two-variant lab;
4. run one real writable-cookie SSR trial and one non-writing negative control;
5. run the current React Native persisted-session characterization separately;
6. update #148, #78, PR #91, and this file whenever an evidence head or lifecycle proposal changes.

## Boundary

No public Supabase issue, pull request, comment, review, reaction, branch, or message was created or changed during this refresh.
