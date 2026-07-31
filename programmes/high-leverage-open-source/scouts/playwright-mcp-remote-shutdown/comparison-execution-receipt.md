# Playwright MCP shutdown repair comparison execution receipt

Owning issue: #404  
Parent characterization: PR #405  
Comparison carrier: PR #410  
Evidence class: `target-executed` for the named candidate controls  
Selected direction: candidate A — loopback-only route  
Upstream contact authorized: `no`

## Exact identities

- Fieldwork comparison head: `f40f316224ebb526150fc87fc336486dfdf9f9bd`;
- exact target: `microsoft/playwright@368941457a82da112aa8610107e25f4bde94339a`;
- workflow: `30651626301`;
- Fieldwork integrity: `30651622950`, success;
- runner: Ubuntu 24.04;
- Node: 22.23.1;
- project: Chromium.

## Candidate A — loopback-only route

- job: `91226004779`;
- artifact: `8801633779`;
- artifact digest: `sha256:11c19ee26756e11167dc9a0567ce73f975dd0de01e02ee4a19e2bd1c3c9b4c7d`;
- artifact files: applied diff, combined target log, JSON receipt;
- exact result: 19/19 passed in 30.6 seconds;
- upstream HTTP suite: 17/17 passed unchanged;
- candidate controls: 2/2 passed;
- focused ESLint: success;
- diff hygiene: success;
- receipt: every named step `success`, `reusableCandidateEvidence: true`.

Executed candidate controls:

1. accepted non-loopback Host plus exact shutdown POST/header returns 403, MCP ping remains live, and process remains running;
2. loopback GET/missing-header/wrong-header remain 405;
3. loopback exact POST/header returns 200 `Killing process`, exits code 0, and logs `gracefully closing 0`.

## Candidate B — explicit process capability

- job: `91226004861`;
- artifact: `8801643332`;
- artifact digest: `sha256:0dcc2345a6d3198bfe205961aa6d8fac0c58f90243ad8700e3c11365fd90dba5`;
- artifact files: applied diff, upstream HTTP log, Fieldwork control log, JSON receipt;
- upstream HTTP suite under explicit capability: 17/17 passed in 23.4 seconds;
- candidate controls: 2/2 passed in 2.8 seconds;
- focused ESLint: success;
- diff hygiene: success;
- receipt: every named step `success`, `reusableCandidateEvidence: true`.

Executed candidate controls:

1. ordinary process without capability returns 404 for the exact shutdown route, MCP ping remains live, and process remains running;
2. explicitly enabled process preserves GET/missing-header/wrong-header 405 controls;
3. enabled exact POST/header returns 200 `Killing process`, exits code 0, and logs `gracefully closing 0`.

## Comparative conclusion

Both candidates are technically viable within the exact Linux target matrix. Candidate A wins under the criteria recorded before execution because it:

- binds shutdown to the direct local peer;
- preserves ordinary local use and the upstream SIGINT test unchanged;
- introduces no process-wide hidden capability;
- cannot be remotely re-enabled merely through inherited environment;
- keeps Host validation, peer locality, and method/header checks independently testable.

Candidate B is retained as a losing alternative, not rejected as broken. It reopens remote shutdown for any accepted Host whenever the environment capability is set and creates a new process-level contract with no close target precedent found.

## Limits

- one Linux runner only;
- no Windows or macOS candidate execution;
- no reverse proxy, container network, IPv6 non-loopback, or production deployment;
- no frequency, exploitability, or harmful-impact claim;
- no target full repository suite beyond complete build, complete MCP HTTP suite, focused candidate controls, lint, and diff hygiene;
- no source merge or public upstream acceptance.

The later workflow-free comparison head transfers this receipt and does not claim another target run.