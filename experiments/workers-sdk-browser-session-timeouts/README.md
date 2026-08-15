# Workers SDK Browser Rendering timeout experiments

Status: evidence complete; owned-fork candidates ready for review decision

Coordination: issue #907

Target: `cloudflare/workers-sdk`, Miniflare Browser Rendering

Pinned/current upstream revision: `49f73de207124171b3f8e9ffb182facb48727388`

No upstream writes are part of this experiment. Third-party GitHub references use redirect.GitHub.

## Trigger

The Browser Rendering test `it creates a browser session` failed on Windows four times in the `packages-and-tools` job for [workers-sdk PR #15143](https://redirect.github.com/cloudflare/workers-sdk/pull/15143) with the generic message `Test timed out in 20000ms`. The same revision later passed the same Windows job on the owned fork.

The investigation found two distinct ownership gaps:

- Candidate A: the test owns a bounded acquisition deadline and a larger outer watchdog so the acquisition phase can fail before Vitest's generic watchdog.
- Candidate B: BrowserSession owns a bounded persistent DevTools connection attempt; acquisition checks registration failure and releases launched-browser registry ownership when registration fails.

These should remain separate review units.

## Historical controls and design lineage

[workers-sdk PR #14708](https://redirect.github.com/cloudflare/workers-sdk/pull/14708) tried broader timeout/retry changes: browser test timeout 20s -> 120s, a longer Windows readiness window, and broader transient retry matching. It closed unmerged after the author reported that it did not help much. This is the main negative control against another blanket timeout increase.

[workers-sdk PR #13971](https://redirect.github.com/cloudflare/workers-sdk/pull/13971) merged a Browser Run diagnostic change motivated by recurring Windows `packages-and-tools` flakes. It established the existing direction of preserving upstream status/body/cause rather than replacing a useful Browser Run error with an opaque parse failure. Candidate B's `/session-info` response check follows that diagnostic model.

[workers-sdk PR #13734](https://redirect.github.com/cloudflare/workers-sdk/pull/13734) was a closed draft/prototype around the Windows Chrome-readiness/connect race. Current source contains the readiness/retry design discussed there, but the PR itself is design lineage rather than the authority for landed code.

Current Chrome readiness policy gives a useful scale reference: after the DevTools URL appears, Miniflare allows a 5s readiness window and caps each `/json/version` readiness request at 500ms. Candidate B's 2s persistent-WebSocket attempt deadline is four times that per-request readiness budget on the same DevTools listener.

## Candidate A — test-owned acquisition deadline

Clean owned-fork branch: `fieldwork/browser-session-timeout-current`

Commit: `d93625eed59148442a96ca0925d1e62269753ac7`

Shape:

- suite-level 20s timeout unchanged;
- only `it creates a browser session` gets a 60s acquisition deadline and 75s outer timeout;
- acquisition uses `AbortSignal.timeout()` around `mf.dispatchFetch()`;
- named error: `Browser session acquisition timed out after 60000ms`;
- target retry condition uses named Chrome readiness/acquisition failures rather than generic `Test timed out`.

Exact-diff Windows validation: run `31891360605`, job `95027999575`. The normal path passed, and a deterministic 65s browser-launch stall produced the named 60s acquisition timeout before the 75s outer watchdog.

Earlier warm focused samples were about 1.6-1.9s of test-body acquisition and 7.67-7.92s command wall time. Browser installation/setup is a separate slower phase.

## Candidate B discovery history

### v1 — timeout without registration ownership

A first product-side prototype added per-attempt timeouts to `fetchWithConnectRetry()`. Normal Browser Rendering tests passed. Under a deterministic stalled connection, acquisition still appeared successful because `BrowserRenderingRouter.#acquireSession()` ignored the `/session-info` response status.

Finding: bounding the inner connect is insufficient if the acquisition owner discards registration failure.

### v2 — registration error still masked by the test harness

Owned-fork branch: `fieldwork/browser-connect-timeout-proof-v2`.

Normal typecheck/build/full Browser Rendering spec passed. Under deterministic connect stall, the target test failed after retry-scale elapsed time, but Vitest showed only `expected false to be true`.

The Browser Rendering test worker reads the binding response body and creates a new default-200 `Response`, then the test checks only whether the text contains `sessionId`. This is a separate test-harness observability boundary: a useful product-side error body can still be reduced to a boolean assertion in the suite.

This finding remains relevant after Candidate B. It belongs with Candidate A / test-side observability rather than expanding the product-side B patch again.

### v3 narrowing — avoid side-effect replay and own failed registration cleanup

`fetchWithConnectRetry()` is also used by DevTools JSON proxy operations, including side-effecting `PUT /json/new`. Making timeout retries the helper default could replay a timed-out side-effecting operation.

Candidate B was therefore narrowed so `perAttemptTimeoutMs` is opt-in and only BrowserSession's persistent Chrome DevTools health WebSocket opts into the deadline. Raw page/browser WebSockets and JSON proxy requests retain their existing timeout behavior.

A second lifecycle invariant emerged: `/browser/launch` registers a Chrome process before BrowserSession registration. If registration fails, acquisition must release that module-level ownership through the existing `/browser/close` path.

The surviving-state oracle is `/browser/status`: 410 means the session is no longer registered. This proves registry ownership release. It does **not** prove OS-process termination, because the existing `/browser/close` path removes the registry entry before process close and suppresses process-close errors.

### v3 core proof

Owned-fork branch: `fieldwork/browser-connect-timeout-proof-v3`.

Invalid harness attempt: run `31893035391`, job `95032053906`. The injection script had an escaping error and failed before candidate source was exercised. Retained as harness history, not product evidence.

Successful repaired run: `31893274327`, job `95032621710`, Windows Server 2025 / Vitest 4.1.0.

Observed:

- candidate typecheck/build passed;
- full Browser Rendering spec passed: 20 passed, 1 skipped;
- deterministic stalled persistent DevTools connect made exactly 5 attempts;
- final named error was `Chrome DevTools connection attempt timed out after 2000ms (attempt 5/5)`;
- acquisition-level `Failed to establish Chrome DevTools connection for browser session ...` attribution survived;
- focused stalled test body completed in about 11.4s, before the 20s Vitest watchdog;
- `/browser/status` returned 410 after failed registration;
- injected non-retryable connect failure made exactly 1 attempt and released registry ownership;
- a BrowserSession-local cancellation injection won over the per-attempt timeout on the first attempt.

The last cancellation check is local to BrowserSession. It does not establish end-to-end user-worker signal propagation.

## Caller-cancellation boundary

workerd's request-signal passthrough tests explicitly enable `enable_request_signal`, `request_signal_passthrough`, and `enable_abortsignal_rpc`. The Miniflare Browser Rendering internal service uses compatibility date `2025-05-01` with `nodejs_compat` and does not explicitly enable those request-signal flags. `enable_request_signal` has no default activation date in the inspected workerd compatibility source.

Three attempted end-to-end caller-abort probes were invalid harnesses rather than product evidence:

- run `31893720300`, job `95033700813`: faulted build ran without the dependency-build prerequisite;
- run `31893851018`, job `95034015132`: typecheck was placed after synthetic fault injection;
- run `31893967509`, job `95034289131`: healthy candidate typecheck/build and a warm browser acquisition passed, but the generated inline test-worker template had an escaping error before the cancellation assertion ran.

Route-level caller-signal propagation is excluded from the clean Candidate B. It is a separate compatibility/runtime question unless later evidence makes it necessary.

## Final Candidate B

Canonical owned-fork branch: `fieldwork/browser-connect-timeout-current`

Final commit: `37334286de10040e62abc500f6fe0d8834bad60f`

Parent: exact current upstream `49f73de207124171b3f8e9ffb182facb48727388`.

Proposal shape: one commit, two files:

- `.changeset/bound-browser-rendering-devtools-connect.md` — `miniflare: patch`;
- `packages/miniflare/src/workers/browser-rendering/binding.worker.ts` — 85 additions, 14 deletions.

Production-file behavior:

- adds a 2s optional per-attempt deadline to `fetchWithConnectRetry()`;
- only BrowserSession's persistent DevTools health WebSocket opts into that deadline;
- timed-out connection attempts retry within the existing five-attempt/backoff policy;
- unrelated non-retryable errors do not become retryable;
- failed persistent connection clears BrowserSession state and rethrows;
- acquisition checks `/session-info` status/body instead of discarding it;
- failed registration calls the existing module-level `/browser/close` path to release the launched browser's registry ownership;
- the registration failure remains primary if the cleanup fetch itself throws;
- no route-level caller-signal compatibility change is included.

The final production blob is `37f207680f451eb98cedb4a7622644d1c4fa7590`.

### Exact/final validation receipts

Initial exact-clean commit `9d9f32771622eb72a61173321efde4d1f28ba88a` was the semantically identical pre-format version of the production patch.

Run `31894196383`, job `95034841700`:

- exact source identity passed;
- Miniflare typecheck passed;
- Miniflare build passed;
- full Windows Browser Rendering spec passed: 20 passed, 1 skipped; `it creates a browser session` took about 8.1s on that run;
- exact stalled-connect proof passed: attempts 1-5, final named `2000ms (attempt 5/5)` timeout, acquisition-level registration attribution, registry status 410, and response elapsed about 11.4s before the 20s watchdog;
- the job later turned red only while preparing the non-retryable control because the probe generator emitted trailing whitespace. That control did not run in this job and the failure is retained as harness history.

Standalone repaired non-retryable control: run `31895665386`, job `95038494797`, success.

Observed:

- exactly one `FIELDWORK_CONNECT_ATTEMPT`;
- registry status 410;
- 500 response preserved `Failed to establish Chrome DevTools connection ...` plus `Injected non-retryable DevTools connection failure`;
- no connection-timeout attribution and no generic 20s Vitest timeout;
- focused test completed in about 8.0s.

The production patch was then formatted with repository `oxfmt` into commit `9d8c9a7d92dbc1f66d2bd7956c04bb3903a5ebb6`; formatting changed layout only. The final `37334286...` commit reuses that exact production blob and adds the patch changeset.

Formatted-code validation: run `31895781122`.

- quality job `95038779062`: exact source identity, `oxfmt --check`, and type-aware `oxlint` all passed;
- Windows job `95038779079`: exact source identity, Miniflare typecheck/build, and full Browser Rendering spec all passed.

Final two-file proposal validation: run `31896065634`, job `95039456653`, success.

- final commit parent and two-file diff shape verified;
- `git diff --check` passed;
- both final changed files passed `oxfmt --check`;
- `changeset status --since=49f73de207124171b3f8e9ffb182facb48727388` passed.

An earlier changeset-status attempt, run `31895974542`, failed because the command defaulted to the fork's stale `main` and also printed unrelated workspace catalog-version diagnostics. The pinned-base rerun above is the applicable receipt.

## Budget and interpretation

Five 2s connect attempts plus current backoff are roughly 10.4s before cleanup. `closeBrowserProcess()` itself allows up to 5s graceful close and then up to 5s after force-kill. A pathological failed-registration path can therefore approach or exceed the existing 20s test watchdog.

This is another reason Candidate B does not replace Candidate A. If A lands first, its 60s acquisition budget leaves ample room for B's bounded connect failure and cleanup to report before the 75s outer watchdog. B alone improves product ownership and normally fails well inside 20s, but pathological cleanup can still let the old outer test watchdog become relevant.

The current Browser Rendering test harness has one additional presentation issue: it can turn a useful non-2xx binding body into `expected false to be true`. That should be addressed in the test-side proposal rather than folded into B.

## Recommendation

Candidate B is now ready as a separate product-hardening proposal on the owned fork. Keep the upstream submission decision separate from Candidate A and do not bundle caller-signal compatibility work.

Recommended order remains:

1. Candidate A first: smallest change, directly repairs CI test timeout ownership and retry attribution.
2. Candidate B second: bounds the persistent BrowserSession DevTools connection, preserves registration failure, and releases registry ownership on failed registration.
3. Before upstreamizing the test-side work, consider a tiny harness refinement so non-2xx Browser binding response bodies are preserved in assertion output instead of collapsing to the `sessionId` boolean check.

Do not claim registry status 410 proves Chrome process termination. No upstream issue, PR, comment, reaction, review, rerun, or message has been created by this investigation.