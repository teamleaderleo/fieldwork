# Adjacent research — Unit 18

## Selected design

Mode-aware parent stdin EOF is now the preferred implementation:

- source: `teamleaderleo/playwright#48@10e28dfdd7758d92aeed50922fd9c7ce9596c21c`
- execution: run `30855503566`
- result: 21/21 plus all declared gates on Ubuntu 24.04, macOS 15, and Windows Server 2025.

The important placement rule is that stdin is consumed only after the stdio transport branch returns. That avoids competing with `StdioServerTransport` for MCP protocol bytes.

## How the stdin design developed

The first experiment closed the parent side of the pipe but listened for readable `close`; it failed on all three platforms. Ordinary parent EOF is observed as `end`, and the stream must be consumed for that event to arrive.

A repaired global experiment listened for `end` and resumed stdin. It proved the mechanism worked, but its placement before transport selection could race stdio input. The final source moved the listener into the HTTP-only branch and added an immediate stdio startup control.

## Executed fallback

Strict parent IPC remains available at:

```text
teamleaderleo/playwright#40
e99e97da2acfc6c1a67749bc749e1d0cb71b5607
run 30690674059
```

It passed its complete focused matrix on Ubuntu, macOS, and Windows. It isn't selected because parent stdin already expresses child lifetime without a private message schema, version, parser, or extra IPC descriptor.

## Separate leads

The following remain separate investigations, not part of this issue:

- other Playwright foreground servers that listen for stdin `close`;
- MCP signal exit-code policy;
- orphan cleanup when a parent dies through an intermediary or without closing the child pipe.

They shouldn't be added to the upstream issue unless a maintainer asks to widen the scope.
