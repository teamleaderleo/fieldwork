# Playwright MCP shutdown-authority repair comparison

Owning issue: #404  
Parent characterization: PR #405  
Comparison PR: #410  
Exact target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`  
Exact target-executed comparison head: `f40f316224ebb526150fc87fc336486dfdf9f9bd`  
State: `target-executed / provisional-selection`  
Selected direction: candidate A — loopback-only route  
Upstream contact authorized: `no`

## Governing invariant

An accepted HTTP Host is not automatically authorized to terminate the MCP process. The repair should preserve the existing graceful SIGINT cleanup test and ordinary local shutdown behavior without introducing a broad credential or hidden process-capability protocol merely for a test route.

## Ordered criteria

1. deny ordinary non-loopback process shutdown after Host acceptance;
2. preserve the existing cross-platform graceful SIGINT lifecycle control;
3. keep safe local behavior simple and deterministic;
4. avoid adding a production secret or public authentication contract solely for test cleanup;
5. minimize production and test-harness changes;
6. remain easy to explain, test, and remove;
7. preserve Host-validation and method/header controls as separate layers.

## Exact shared execution

Both candidates executed against the same exact Fieldwork and Playwright generations.

- Fieldwork head: `f40f316224ebb526150fc87fc336486dfdf9f9bd`;
- target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`;
- workflow: `30651626301`;
- runner: Ubuntu 24.04;
- Node: 22.23.1;
- project: Chromium;
- Fieldwork integrity: `30651622950`, success.

For each candidate the matrix passed:

- exact-head verification;
- zero-fuzz `git apply --check` and apply;
- `npm ci` with 638 packages;
- complete Playwright build;
- Chromium and runner dependency installation;
- complete upstream HTTP suite plus candidate-specific reversing controls;
- focused ESLint;
- `git diff --check`;
- receipt assembly and artifact upload.

Both receipts record every named step as `success` and `reusableCandidateEvidence: true`.

## Candidate A — loopback-only route

Retained patch: `candidate-loopback-only.patch`  
Control: `fieldwork-loopback-only.spec.ts`  
Job: `91226004779`  
Artifact: `8801633779`  
Artifact digest: `sha256:11c19ee26756e11167dc9a0567ce73f975dd0de01e02ee4a19e2bd1c3c9b4c7d`

### Mechanism

- production changes: one file;
- test-harness changes: none;
- classify the direct socket peer as IPv6 loopback, IPv4 loopback, or IPv4-mapped loopback before method/header processing;
- accepted non-loopback Host receives HTTP 403 and the process remains live;
- loopback retains the current POST/header path and graceful SIGINT cleanup.

### Exact result

```text
Running 19 tests using 1 worker
19 passed (30.6s)
```

The 17 existing upstream HTTP tests passed unchanged. The two Fieldwork controls proved:

1. an accepted remote Host cannot use the shutdown route; it receives 403, the MCP client still answers ping, and the process remains live;
2. loopback retains GET/missing-header/wrong-header 405 controls, exact POST/header 200 `Killing process`, clean exit code 0, and `gracefully closing 0`.

### Cost and uncertainty

- adds one local address classifier;
- exact controls cover IPv4 non-loopback and loopback behavior on Linux;
- source explicitly handles `::1`, `127/8`, and IPv4-mapped loopback;
- Windows and macOS execution remain unmeasured in this Fieldwork matrix;
- Unix-domain or non-TCP peers are outside the current HTTP server path and not claimed.

## Candidate B — explicit process capability

Retained patch: `candidate-test-capability.patch`  
Control: `fieldwork-test-capability.spec.ts`  
Job: `91226004861`  
Artifact: `8801643332`  
Artifact digest: `sha256:0dcc2345a6d3198bfe205961aa6d8fac0c58f90243ad8700e3c11365fd90dba5`

### Mechanism

- production changes: one file;
- ordinary processes hide the route with HTTP 404;
- `PLAYWRIGHT_MCP_ALLOW_PROCESS_SHUTDOWN=1` restores the route for a deliberately enabled process;
- method/header controls remain after capability admission;
- the complete upstream HTTP suite executes under the explicit capability, while the Fieldwork control separately exercises the ordinary disabled process.

### Exact result

```text
Upstream HTTP suite: 17 passed (23.4s)
Fieldwork capability controls: 2 passed (2.8s)
```

The Fieldwork controls proved:

1. an ordinary all-interface process hides the route with 404, remains live, and continues answering MCP ping;
2. an explicitly enabled process retains GET/missing-header/wrong-header 405 controls, exact POST/header 200 `Killing process`, clean exit code 0, and `gracefully closing 0`.

### Cost and uncertainty

- adds a hidden production environment capability;
- a deliberately enabled non-loopback process can still grant shutdown to any accepted Host that knows the fixed route/header;
- introduces a second admission axis beside Host and method/header checks;
- the capability name and lifecycle would become another contract to document, test, and avoid inheriting accidentally;
- no target precedent was found for a general MCP test-mode capability.

## Provisional selection

**Candidate A — loopback-only route wins.**

Both candidates meet the primary behavioral invariant and pass the same technical gates. Candidate A ranks higher under criteria 2–7 because:

- it binds authority to the direct local peer rather than a process-wide switch;
- it preserves ordinary local shutdown without an opt-in;
- it leaves the upstream SIGINT test unchanged;
- it cannot be re-enabled remotely through inherited environment alone;
- it adds no hidden production capability or new documentation obligation;
- it keeps Host validation, peer locality, and method/header checks as distinct layers.

Candidate B is retained as a technically valid losing alternative. It would become preferable only if cross-platform execution disproves the address classifier or if target-owned precedent explicitly favors a hidden shutdown capability.

## Alternatives not prototyped

- authenticated/secret remote shutdown: broader credential and lifecycle contract than the current test route justifies;
- remove the route and invent another cross-platform child-signal fixture: larger harness change while candidate A preserves the current fixture;
- documentation-only: does not repair the demonstrated authority inheritance;
- public remote shutdown as intentional behavior: no target contract was found that identifies accepted Host as an authorized shutdown principal.

## Exact next transition

1. retain this execution receipt and remove the temporary comparison workflow;
2. run Fieldwork integrity on the workflow-free comparison head;
3. complete-review the retained patch, controls, criteria, receipts, and losing reason;
4. materialize candidate A on one directly owned Playwright source branch when available;
5. run the target repository's declared gates plus Windows and macOS focused controls if the owned runner matrix is available, or state the platform limit explicitly;
6. compare against current target source before any public-upstream packet is drafted.

No source merge, release, deployment, external site, account, credential, private browser state, spending, or public-upstream interaction is included or authorized.