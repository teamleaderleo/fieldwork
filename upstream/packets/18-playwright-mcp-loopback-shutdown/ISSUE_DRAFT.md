# Submitted upstream issue record

## Issue

[MCP HTTP clients can terminate the server through `/killkillkill`](https://redirect.github.com/microsoft/playwright/issues/42129)

Status when recorded: open, awaiting maintainer response.

## Filed title

`[Bug]: MCP HTTP clients can terminate the server through /killkillkill`

## Reported behavior

A programmatic HTTP client that can reach an accepted MCP host can send:

```http
POST /killkillkill
x-pw-mcp-kill: 1
```

The server returns success and emits `SIGINT`. The fixed header reduces browser-CSRF exposure, but it doesn't authenticate the caller or show process ownership.

## Expected behavior

Ordinary MCP HTTP clients shouldn't be able to terminate the server process. The spawning parent or an authorized supervisor should own lifecycle control.

## Proposed direction

Remove the HTTP route. In HTTP test mode, translate EOF on the child stdin pipe owned by the spawning test parent into the existing `SIGINT` cleanup path. Return from stdio mode before installing that listener.

## Evidence included

- route history and current in-tree use;
- self-contained command-line reproduction;
- current-main source reference;
- Ubuntu 24.04 environment;
- completed implementation and three-platform focused validation.

The upstream PR remains blocked on explicit maintainer approval or assignment.
