# Playwright MCP shutdown-authority repair comparison

Owning issue: #404  
Parent characterization: PR #405  
Exact target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`  
State: `target-test-prepared`  
Upstream contact authorized: `no`

## Governing invariant

An accepted HTTP Host is not automatically authorized to terminate the MCP process. The repair should preserve the existing graceful SIGINT cleanup test and ordinary local shutdown behavior without introducing a broad credential protocol merely for a test route.

## Ordered criteria

1. deny ordinary non-loopback process shutdown after Host acceptance;
2. preserve the existing cross-platform graceful SIGINT lifecycle control;
3. keep safe local behavior simple and deterministic;
4. avoid adding a production secret or public authentication contract solely for test cleanup;
5. minimize production and test-harness changes;
6. remain easy to explain, test, and remove;
7. preserve Host-validation and method/header controls as separate layers.

## Candidate A — loopback-only route

Retained patch: `candidate-loopback-only.patch`

- production changes: one file;
- test-harness changes: none;
- mechanism: classify the direct socket peer as IPv6 loopback, IPv4 loopback, or IPv4-mapped loopback before method/header processing;
- remote accepted Host: HTTP 403, process remains live;
- loopback: existing POST/header path remains available;
- expected advantage: smallest source change and no hidden capability;
- expected risk: local address classification becomes a target-owned helper and must cover mapped IPv4 correctly.

Discriminator: `fieldwork-loopback-only.spec.ts`.

## Candidate B — explicit test capability

Retained patch: `candidate-test-capability.patch`

- production changes: one file;
- test-harness changes: the existing SIGINT test opts in through `PLAYWRIGHT_MCP_ALLOW_PROCESS_SHUTDOWN=1`;
- mechanism: ordinary servers hide the route with HTTP 404; an explicitly enabled process retains the existing method/header route for accepted clients;
- expected advantage: no address-classification logic and a fail-closed ordinary server;
- expected risk: introduces a hidden production environment switch, changes the test harness, and can deliberately re-enable remote shutdown.

Discriminator: `fieldwork-test-capability.spec.ts`.

## Shared execution gate

For each candidate, the exact workflow must:

1. verify Fieldwork and target heads;
2. apply the retained patch with zero fuzz;
3. copy only the matching Fieldwork control;
4. install exact dependencies and build exact target source;
5. install Chromium and runner dependencies;
6. run the complete upstream `tests/mcp/http.spec.ts` plus the candidate control;
7. run focused ESLint on changed and copied TypeScript files;
8. run `git diff --check` and retain the exact applied diff;
9. emit one candidate-specific receipt whose reusable result requires every named step to succeed.

## Selection rule

Candidate A is the provisional leader because it preserves the upstream test unchanged and grants shutdown only to the direct local peer. Candidate B wins only if address classification fails a compatibility control or if target precedent strongly prefers explicit hidden test capabilities.

No candidate is accepted until exact execution and complete-diff review. Documentation-only, authenticated remote shutdown, and route removal remain retained alternatives but need no prototype unless A and B both fail or new compatibility evidence appears.