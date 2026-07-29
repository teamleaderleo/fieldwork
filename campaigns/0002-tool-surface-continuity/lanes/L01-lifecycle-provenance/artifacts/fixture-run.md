# Lifecycle provenance fixture run

Command:

```bash
python3 campaigns/0002-tool-surface-continuity/lanes/L01-lifecycle-provenance/artifacts/lifecycle_provenance_fixture.py
```

Execution environment:

- Python `3.13.5`
- Linux `6.12.13-x86_64`
- public source pin `openai/codex@3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`
- owned comparison pin `teamleaderleo/codex@2b7b93081361b77f8ddaceaf362a09765b4153bf`

Result:

```text
exit code: 0
assertions: all passed
```

Observed transition summary:

| transition | effective dynamic set | root-a winner | additive root-b | outcome |
|---|---|---|---|---|
| start | `host_new` | `/host/root-a` | yes | current host declarations accepted |
| live reconnect | `host_live` | `/live/root-a` | yes | existing session preserved |
| cold resume | `host_old` | `/saved/root-a` | yes | saved dynamic set preserved; roots merged saved-first |
| fork | `host_old` | `/saved/root-a` | yes | copied dynamic set preserved; roots merged saved-first |
| restart | `host_old` | `/saved/root-a` | yes | cold-resume composition |
| upgrade | `host_old` | `/saved/root-a` | yes | cold-resume composition under current runtime |

Every cold reconstruction reports both diagnostics encoded by the source branches:

```text
current host thread capability set has no public resume/fork input
conflicting root root-a: kept /saved/root-a; ignored /current/root-a
```

Controls held current native tools and current MCP tools constant so the fixture isolates thread-scoped host provenance.
