# Upstream pull-request draft — fix(mcp): scope HTTP test shutdown to parent stdin

Draft status: `waiting for issue approval or assignment`

Upstream issue: [MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

Proposed source: `teamleaderleo/playwright:fix/mcp-http-parent-stdin-review@10e28dfdd7758d92aeed50922fd9c7ce9596c21c`

Proposed base: `microsoft/playwright:main`, refreshed from `2cc9f3ee7fdd82feb87edb7f24af77442bdc10e2` before submission.

## Summary

- remove the test-only `/killkillkill` HTTP shutdown route;
- in HTTP test mode, translate the owning parent's stdin EOF into the existing `SIGINT` cleanup path;
- leave MCP stdio input ownership unchanged;
- replace the route-driven lifecycle test and add production-scope and stdio-startup controls.

## Why

The fixed method and public header reduce browser-CSRF exposure, but they don't authenticate a programmatic HTTP caller or establish process ownership. The spawning test parent already owns the child's stdin pipe.

## Tests

Run `30855503566` passed the full 21-test MCP HTTP file, complete build, focused ESLint, clean tree, and exact three-file diff on Ubuntu 24.04, macOS 15 ARM64, and Windows Server 2025.

## Submission steps

1. Wait for explicit maintainer approval or assignment on the upstream issue.
2. Obtain separate user authorization to open the PR.
3. Refresh the branch against current `main` and rerun any gate affected by the refresh.
4. Use the body in `PR_DRAFT.md` and include:

```text
Fixes #42129
```

5. Confirm that the upstream diff contains only the three intended files.

No upstream pull request has been opened.
