# Handoff — Unit 02: uv BusyBox `realpath` compatibility

Updated: `2026-08-07`

State: `RETIRED — PUBLIC PR CLOSED UNMERGED — UPSTREAM BUSYBOX FIX PREFERRED`

## Terminal public state

- Public issue: [astral-sh/uv#16209](https://redirect.github.com/astral-sh/uv/issues/16209)
- Public pull request: [astral-sh/uv#20943](https://redirect.github.com/astral-sh/uv/pull/20943)
- Preferred upstream repair: [vda-linux/busybox_mirror#26](https://redirect.github.com/vda-linux/busybox_mirror/issues/26)
- Final public head: `28b00fc950c7eb924ab243418d44ce16ac5bee5a`
- Final canonical CI: run `31059965759` — success
- Public PR state: closed without merge
- Final diff: four files, 207 additions, 16 deletions

The final uv candidate passed its full visible CI. Closure was a project-level design decision: uv maintainers did not want a runtime capability probe in generated launchers and chose to pursue POSIX-compatible `--` handling in BusyBox instead.

## Canonical internal locations

- Routing issue: `teamleaderleo/fieldwork#435`, unit 02
- Completed investigation: `teamleaderleo/linux-fieldwork#307`
- Packet branch: `teamleaderleo/fieldwork:upstream/02-uv-busybox-realpath-packet`
- Packet path: `upstream/packets/02-uv-busybox-realpath/`
- Final fork branch: `teamleaderleo/uv:upstream/02-busybox-realpath`

## Final downstream behavior

The submitted PR evolved from unconditional `realpath` delimiter removal into a runtime capability check:

- probe `realpath -- /`;
- require both success and output equal to `/`;
- retain `realpath -- "$0"` when supported;
- use `realpath "$0"` for BusyBox-style implementations;
- apply equivalent behavior to POSIX and Fish activation scripts;
- recognize current and historical `python` / `python3` launchers in `uv run`.

## Retained evidence

The final candidate covered:

- compliant and BusyBox-style `realpath` behavior;
- a bare `-foo` operand;
- a literal file named `--`;
- current and historical relocatable shebangs;
- POSIX and Fish generation;
- Linux, macOS, and Windows ordinary CI.

The investigation also preserved the failure modes of retry fallback, `./$0`, `command -v`, generation-time detection, and BusyBox fingerprinting. See `APPROACHES.md`.

## Process closeout

The initial maintainer instruction to identify and specialize for BusyBox was reasonably read as permitting a runtime capability probe. The later clarification added an unstated constraint: per-launcher probing was itself unacceptable.

Future upstream work should ask the smallest architectural question before expanding an ambiguous review direction. Private research may retain the full option tree, while maintainer-facing discussion should lead with the most relevant finding and requested decision. Target contribution and AI policies must be checked before public replies.

## Next action

No further downstream uv action is active.

Do not:

- reopen the closed PR;
- publish a replacement runtime-probe PR;
- add another uv issue or PR comment without a concrete maintainer event;
- compete with the announced BusyBox patch unless the user deliberately chooses that work after checking current ownership.

Retain this packet as a negative result, portability reference, and continuation record. Continue unrelated uv work in separate lanes.
