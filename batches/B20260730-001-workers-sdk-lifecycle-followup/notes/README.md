# Adjacent Vite follow-up notes

- `vite-container-cleanup-ownership.md` — candidate #165; per-instance container cleanup callbacks, early tag ownership, restart retry ownership, and preview close cleanup.
- `vite-shared-context-ownership.md` — candidate #179; logical server ownership for restart state, Miniflare, tunnels, export maps, warnings, and tunnel hostnames.
- `vite-build-marker-scope.md` — candidate #183; operation-scoped build intent and entry-versus-prerender preview selection without sticky process environment.
- `vite-remote-proxy-session-ownership.md` — candidate #186; live remote-binding session lifecycle, connection identity, disposed-entry reuse, and session-owned logging.
- `vite-container-registry-auth-scope.md` — candidate #187; per-operation account and bearer-token authority for container registry credential generation.

All five candidates are separate from the first Miniflare runtime-first patch and remain blocked on package, mocked integration, or multi-operation execution appropriate to their evidence class.
