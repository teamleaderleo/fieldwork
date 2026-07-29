# Execution update: bundled-development plugin hot-update browser trial

Date: 2026-07-30

Fieldwork lane: #25

Pinned Vite revision: `8a245726944ed29225920d49be77c33c6e03afc8`

Owned reproduction: `teamleaderleo/vite#3`

Upstream contact: none

## Result

The third scout candidate now has a browser-visible reproduction in Vite's own playground harness.

The same fixture ran under ordinary dev and under the serve suite with bundled development force-enabled.

A plugin exposes virtual state initially read as `alpha` from an external text file. The file is registered with Vite's filesystem watcher but intentionally omitted from the module and bundle dependency graph. The plugin owns its browser update path through custom HMR events:

- `watchChange` sends a watcher marker;
- `hotUpdate` reads the changed value and sends the state update;
- the browser changes visible text when the state event arrives.

After the backing file changes to `beta`:

### Ordinary dev control

- watcher marker received;
- plugin `hotUpdate` event received;
- visible state changed to `beta`;
- custom update count became `1`.

### Bundled development

- the same watcher marker was received, proving Vite observed the filesystem event;
- plugin `hotUpdate` event was absent;
- visible state remained stale at `alpha`;
- custom update count remained `0`.

Focused workflow `Fieldwork bundled hotUpdate browser probe`, run `30478771510`, passed Vite build, classic browser control, and bundled browser comparison.

## Interpretation

The early return before `hotUpdate`/`handleHotUpdate` is not only an internal hook difference. It can preserve stale browser state for a plugin that deliberately owns updates to external or virtual data.

Bundled development is experimental and its third-party plugin limits are documented. The candidate should therefore be presented upstream as a reproduced compatibility gap, with the project deciding between:

- supporting plugin hot-update hooks in the bundled pipeline; or
- rejecting or diagnosing plugins that rely on unsupported custom HMR handling.

## Trial location decision

The original scout proposed Renderprove as the owned integration gate. During execution, Vite's existing Playwright playground harness proved stronger and narrower: it runs the identical fixture in ordinary and bundled modes without adding framework-specific dependencies to another repository. Renderprove was therefore left unchanged.

## Handoff

All three Fieldwork #25 candidates now have owned runtime evidence:

1. `teamleaderleo/vite#1` — rejected `watchChange` preserves stale transform cache;
2. `teamleaderleo/vite#2` — post-order transform escapes dev import/HMR graph analysis;
3. `teamleaderleo/vite#3` — bundled dev skips plugin hot-update handling and leaves browser state stale.

Each Vite draft PR contains a portable upstream issue draft. None has been submitted upstream.
