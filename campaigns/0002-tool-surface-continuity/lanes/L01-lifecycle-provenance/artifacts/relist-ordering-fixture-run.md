# Relist ordering fixture run

Date: 2026-07-30  
Command:

```bash
python3 campaigns/0002-tool-surface-continuity/lanes/L01-lifecycle-provenance/artifacts/relist_ordering_fixture.py
```

Result: exit code `0`; every assertion passed.

```json
{
  "codex_late_binding": {
    "removed": {
      "advertised_catalogue": "A",
      "diagnostic": "advertisement_execution_revision_mismatch",
      "live_catalogue": "B-removed",
      "outcome": "unavailable_after_startup_wait"
    },
    "same_digest": {
      "diagnostic": "verified_equal_catalogue",
      "outcome": "execute_live_binding",
      "tool_revision": "schema-v1/approval-prompt"
    },
    "same_name_changed": {
      "advertised_tool_revision": "schema-v1/approval-prompt",
      "diagnostic": "advertisement_execution_revision_mismatch",
      "live_tool_revision": "schema-v2/approval-auto",
      "outcome": "execute_live_binding"
    }
  },
  "sdk_relist_ordering": {
    "cache_catalogue": "C",
    "late_application_publish_accepted": false,
    "late_cache_write_accepted": false,
    "naive_application_catalogue": "B",
    "ticketed_application_catalogue": "C"
  }
}
```

## Interpretation

The fixture models source-derived invariants rather than executing the full Codex or Rust SDK binaries.

- The SDK cache generation prevents a late relist response from replacing the newer cached catalogue.
- The current raw result API can still give that late response to application code, allowing a naive publisher to roll its own catalogue back.
- A public generation/ticket check prevents the application rollback.
- Codex cached advertisement followed by live call-time binding is acceptable only when catalogue equality is verified or a typed mismatch policy governs the rebind.

The next evidentiary step is a compiled Rust fixture using the real SDK receive loop and a controlled Codex MCP server. Public upstream remained read-only.