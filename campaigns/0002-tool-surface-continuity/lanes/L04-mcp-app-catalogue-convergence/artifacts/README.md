# L04 catalogue transition fixture

This directory contains a dependency-free, harmless MCP-shaped stdio fixture for Fieldwork issue #39.

## Run

```bash
python3 catalogue_transition_probe.py --output results/latest.json
python3 -W error::ResourceWarning -m unittest -v test_catalogue_transition.py
```

## Files

- `stub_real_mcp.py` — minimal JSON-RPC stdio server implementing `initialize`, `tools/list`, `tools/call`, and `shutdown`.
- `catalogue_transition_probe.py` — orchestrates stub-to-real, refresh, reconnect, fresh-thread, restart, identity-only, catalogue-only, and connection-config controls.
- `test_catalogue_transition.py` — seven regression checks.
- `results/latest.json` — full inventory and digest checkpoints.
- `results/probe-output.txt` — top-level assertions from the retained run.
- `results/test-output.txt` — retained unittest output.

## Scope

The fixture preserves the public Codex lifecycle seam found at revision `3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`: a ready client captures server information and tools at startup; ordinary refresh can reuse that client when connection configuration matches; each sampling step freezes a binding and builds its router and model-visible tools from that binding.

It is an owned local reproduction of the interface contract. A compiled Codex end-to-end test remains a separate follow-up.
