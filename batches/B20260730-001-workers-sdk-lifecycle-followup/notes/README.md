# Adjacent Vite follow-up notes

- `vite-container-cleanup-ownership.md` — candidate #165; per-instance container cleanup callbacks, early tag ownership, restart retry ownership, and preview close cleanup.
- `vite-shared-context-ownership.md` — candidate #179; logical server ownership for restart state, Miniflare, tunnels, export maps, warnings, and tunnel hostnames.
- `vite-build-marker-scope.md` — candidate #183; operation-scoped build intent and entry-versus-prerender preview selection without sticky process environment.

All three candidates are separate from the first Miniflare runtime-first patch and remain blocked on Vite package/integration execution.
