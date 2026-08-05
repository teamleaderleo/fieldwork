# Upstream issue record

Status: `submitted / open / waiting for maintainer response`

Issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

Filed title:

```text
[Bug]: MCP HTTP clients can terminate the server through /killkillkill
```

## Report contents

- version: `1.63.0-next` at public base `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2`, with the route also present in 1.62.0;
- reproduction: start `@playwright/mcp` in HTTP mode and send the fixed `POST` and header;
- expected: ordinary HTTP clients can't terminate the server process;
- actual: the request returns success and emits `SIGINT`;
- context: route introduction, later POST/header change, current in-tree test use, and the parent-stdin replacement;
- environment: Ubuntu 24.04.4, Node 22.23.1, npm 10.9.8.

The report stays narrow. Orphan-process and failed-cleanup issues weren't included because they concern a different failure mode.

## Next gate

Wait for an explicit maintainer approval for community contribution or assignment. Don't open an upstream PR based only on elapsed time.
