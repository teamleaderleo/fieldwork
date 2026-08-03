# Fieldwork — current owner map

Observed: `2026-08-03 14:58 +08:00`  
Fieldwork base: `d82277ce8b170faeeeb3e74809f5ab8bf902d232`  
Linux Fieldwork base: `6cc74d846c50b9bbb88247e8a128b67e8c174c1e`

## In simple words

There is substantially more active work than the Human Review Desk shows. That is intentional: the desk should contain only decisions that genuinely need the repository owner. The wider portfolio includes a 27-unit upstream-convergence backlog, several near-finished contribution packets, active SDK and runtime investigations, coordination infrastructure, and a large Linux workbench.

The problem is not lack of work. It is that the useful work is spread across many issues, packet pull requests, source forks, execution carriers, and historical stacks.

This page is a dated owner snapshot. It is not a second state machine and grants no authority. Live issue, pull-request, workflow, review, source, and desk records win whenever they move.

## One place for owner decisions

Pin or bookmark [Human Review Desk #387](https://github.com/teamleaderleo/fieldwork/issues/387).

At this observation it contains two genuine behavior decisions:

1. **Playwright Python shared asynchronous shutdown** — `teamleaderleo/playwright-python#8@4cfc6a9e3e3a5c6dcab04015a1210ce6924d4c27`, packet [#442](https://github.com/teamleaderleo/fieldwork/pull/442).
2. **HTTPX terminal asynchronous response close** — `teamleaderleo/httpx#6@d5f9e3dffce3342d8c02ec2c1d3ed9588a83b803`.

Everything below remains assistant- or peer-owned until one current, concise, non-delegable decision is ready.

## Immediate technical review

[Peer Review Queue #213](https://github.com/teamleaderleo/fieldwork/issues/213) currently carries one exact review generation:

- **Gemini CLI confirmation call affinity — unit 16**
  - source: `teamleaderleo/gemini-cli#24@b6d8e8bb6160aec16555647d81d46a694e44b58b`;
  - packet: [#443](https://github.com/teamleaderleo/fieldwork/pull/443) at `0693e3dace1b41e52baa4bc90f4524106153a0af`;
  - result: 15/15 focused and scheduler tests, build, typecheck, formatting, changed-file lint, clean publication, and passing packet integrity;
  - remaining transition: eligible independent exact-diff disposition, then filing preparation through #160.

## Next owner bench

These are technically close enough to deserve active servicing. They should reach #387 one at a time, only after exact currentness and technical review are settled.

### Vite watch-change failure isolation — unit 01

- packet [#438](https://github.com/teamleaderleo/fieldwork/pull/438);
- source `teamleaderleo/vite#4@ba8ac979ee91c77fdd91304ccde38942e9752133`;
- substantive Linux, macOS, Windows, and Node-version jobs passed at the retained generation;
- remaining work is final aggregate/current-state classification and exact review routing.

### Nixpkgs gomarkdoc checks — unit 22

- packet [#564](https://github.com/teamleaderleo/fieldwork/pull/564);
- source `teamleaderleo/nixpkgs@e8d97d5d8c67a9473a7aaad3961c0630583aa34b`;
- one source file and one commit;
- Linux and Darwin checks passed, checks-enabled and checks-disabled binaries were byte-identical, and independent review passed;
- technically complete packet awaiting orderly owner presentation.

### Playwright MCP remote-authority help — unit 25

- packet [#448](https://github.com/teamleaderleo/fieldwork/pull/448);
- source `teamleaderleo/playwright#39@745b4dea96ac64eeb1e92d9ce4525b995e64909f`;
- one documentation source file;
- build, generated-help assertions, ESLint, and the complete MCP HTTP suite passed;
- exact-diff review found no source defect.

### Jotai stale asynchronous read generation — unit 21

- packet [#450](https://github.com/teamleaderleo/fieldwork/pull/450);
- source `teamleaderleo/jotai#3@dfe607d7637fbcf61ae41c39f4f470f61fa7c531` stacked on the key-cache prerequisite;
- test, multiple-version, old-TypeScript, multiple-build, and compressed-size gates passed;
- duplicate, policy, and disclosure checks must be refreshed before any filing.

## Assistant finishing lanes

[Internal Delivery Desk #160](https://github.com/teamleaderleo/fieldwork/issues/160) owns the exact current routing. The important near-finish work includes:

- **node-lru-cache background fetch size — unit 07**, packet [#440](https://github.com/teamleaderleo/fieldwork/pull/440): focused 95/95 assertions and core hygiene passed; the remaining Windows lane is separating a base TAP-plugin setup defect from source behavior.
- **Playwright MCP shutdown authority — unit 18**, packet [#451](https://github.com/teamleaderleo/fieldwork/pull/451): strict parent IPC is the fully executed canonical candidate; mode-aware stdin comparison [#563](https://github.com/teamleaderleo/fieldwork/pull/563) is the current alternative matrix.
- **Miniflare runtime-first disposal — unit 15**, packet [#456](https://github.com/teamleaderleo/fieldwork/pull/456): clean source repaired; exact-head workflows and final classification remain.
- **OpenTelemetry lifecycle fanout — unit 11**, packet [#445](https://github.com/teamleaderleo/fieldwork/pull/445): one clean six-file source commit; exact-head target workflows remain the active evidence boundary.
- **DuckDB Hive default marker — unit 04**, packet [#446](https://github.com/teamleaderleo/fieldwork/pull/446): accepted source implementation with bounded exact-head execution remaining.
- **DuckDB ROWS FOLLOWING overflow — unit 03**, packet [#452](https://github.com/teamleaderleo/fieldwork/pull/452): focused current-main regression passed; ordinary regular window-suite settlement remains.
- **Gemini background shell ownership — unit 05**, packet [#447](https://github.com/teamleaderleo/fieldwork/pull/447): source and packet review accepted; exact-head carrier and platform/cancellation boundaries remain.
- **Jotai key-scoped JSON cache — unit 20**, packet [#441](https://github.com/teamleaderleo/fieldwork/pull/441): selected source exists; current workflows, sequencing with unit 21, carrier retirement, and independent review remain.
- **Codex durable append acknowledgement — unit 23**, packet [#449](https://github.com/teamleaderleo/fieldwork/pull/449): selected semantics and historical evidence exist; current-main direct materialization remains.
- **Workerd receiver-aware declarations — unit 10**, execution carrier [#475](https://github.com/teamleaderleo/fieldwork/pull/475): generated-declaration validation remains an execution concern, not a clean-source identity.

The complete numbered inventory remains [P0 backlog #435](https://github.com/teamleaderleo/fieldwork/issues/435). A packet being open does not mean it belongs on the owner desk.

## High-value active research

### SDK and application lifecycle

- **Vercel AI SDK async-iterator read-error cleanup**, Fieldwork [#532](https://github.com/teamleaderleo/fieldwork/pull/532), source `teamleaderleo/ai#14`: target-native candidate and focused/current CI are the promotion boundary.
- **Workers SDK authority boundaries**, Fieldwork [#473](https://github.com/teamleaderleo/fieldwork/pull/473): account-cache identity, module-global deploy context, profile authority, Access-cache lifetime, and session log-level ownership have source maps and controlled carriers.
- **Cloudflare Vite project-environment authority**, Fieldwork [#467](https://github.com/teamleaderleo/fieldwork/pull/467): process-global environment leakage is source-confirmed and model-executed; target reproduction remains.
- **Authoritative run state across agent runtimes**, Fieldwork [#535](https://github.com/teamleaderleo/fieldwork/pull/535): retains Vercel provider polling, TanStack transformation order, OpenCode stale-idle publication, and resumed-message adoption candidates.
- **TanStack async throttle acknowledgement**, Fieldwork [#533](https://github.com/teamleaderleo/fieldwork/pull/533): corrected model candidate exists; target execution remains the evidence gap.
- **Zustand storage and hydration authority**, Fieldwork [#531](https://github.com/teamleaderleo/fieldwork/pull/531) and [#476](https://github.com/teamleaderleo/fieldwork/pull/476): clean one-line directions exist, but exact target workflows and distinct policy boundaries remain.

### Tooling, package, and runtime systems

- **uv first-contribution review**, Fieldwork [#534](https://github.com/teamleaderleo/fieldwork/pull/534): BusyBox-compatible relocatable launcher remains the leading contribution; Linux source gates passed while macOS, Fish, and publication evidence were still being settled.
- **uv self-update recovery audit**, Fieldwork [#491](https://github.com/teamleaderleo/fieldwork/pull/491): useful evidence exists, but the branch contains many experiments and must be reduced to bounded owner decisions rather than presented whole.
- **curl HSTS pre-truncation**, Fieldwork [#474](https://github.com/teamleaderleo/fieldwork/pull/474): local installed-curl experiment retained; no current-master repair claim.

## Non-Debian Linux Fieldwork

The active Linux work worth keeping in the foreground is not the old mmdebstrap pile.

### Foundational systems deep dive

- parent [linux-fieldwork#419](https://github.com/teamleaderleo/linux-fieldwork/issues/419);
- research carrier [linux-fieldwork#420](https://github.com/teamleaderleo/linux-fieldwork/pull/420);
- strongest current result: the curl/Ceph-style hang is reproduced when an Asio one-shot wait is not re-armed while curl retains unchanged input interest; the generation-safe re-arm control completes;
- adjacent lanes: systemd vmspawn user-namespace bind handling, BuildKit lazy context consumption, BuildKit cancellation/process ownership, and systemd VT release ordering.

### systemd-oomd reporter ownership

- [linux-fieldwork#245](https://github.com/teamleaderleo/linux-fieldwork/pull/245);
- current systemd VM behavior is reproduced: a later user-manager `auto` report removes an earlier system-manager pressure policy for the same path;
- source-precedence prototype, snapshot lifecycle model, and typed C reducer are under exact validation.

### kmod recursive configuration identity

- [linux-fieldwork#412](https://github.com/teamleaderleo/linux-fieldwork/pull/412);
- deterministic package-level reproduction shows a recursive `modprobe` loses a requested configuration path containing whitespace through flattened `MODPROBE_OPTIONS` serialization;
- current upstream build and native fake-root tests are the next evidence boundary.

### fsck and udev lock identity

- [linux-fieldwork#413](https://github.com/teamleaderleo/linux-fieldwork/pull/413);
- privileged probe passed and proved current `fsck -l` and udev whole-device flock use independent lock objects;
- a synchronized disposable ext4/udev lifecycle fixture is the next step.

### jq, systemd, UV, and WGPU cross-ecosystem round

- [linux-fieldwork#414](https://github.com/teamleaderleo/linux-fieldwork/pull/414);
- jq destructuring inside `path()` has an active controlled source-order matrix;
- systemd bind-path whitespace is an overlap review because a public implementation already exists;
- WGPU/Naga bitcast work is retired after current source accepted the controlled cases;
- the UV lockfile diagnostic is held because complete review exposed a valid-requirements-file false positive.

### util-linux cpuset parse ownership

- historical packet [linux-fieldwork#404](https://github.com/teamleaderleo/linux-fieldwork/pull/404), closed without merge after the Debian package gate was cancelled;
- installed util-linux 2.41-5 reproducibly aborted in text and JSON modes on malformed CPU-online input;
- the canonical repair applied cleanly, the exact actual-binary baseline/candidate matrix passed, and controlled fork head `95ebc67e521195741040ffebb58756b259fb69b2` passed the focused native regression;
- retain as upstream util-linux evidence and require fresh current-source review before any future proposal.

### DuckDB secondary ART persisted wrong result

- [linux-fieldwork#334](https://github.com/teamleaderleo/linux-fieldwork/pull/334);
- exact release-artifact matrix retained a high-consequence false-negative index-scan result while sequential reads retained the row;
- the one-file evidence restack passed repository CI and needs eligible independent review before promotion.

### Reusable repository integrity

- [linux-fieldwork#418](https://github.com/teamleaderleo/linux-fieldwork/pull/418): broadened relative-executable/cwd inventory coverage and hardened untrusted-input handling.
- [linux-fieldwork#328](https://github.com/teamleaderleo/linux-fieldwork/pull/328): executed repair for fenced-example parsing in carrier-state audit; technically review-ready.

## Debian and mmdebstrap direction

Owner direction on `2026-08-03`: **deprioritize Debian and mmdebstrap work**.

Therefore:

- no new Debian/mmdebstrap investigation, packaging matrix, packet repair, Salsa refresh, or public-submission preparation should begin;
- queued or historical receipts remain valid at their exact generations;
- branches and artifacts remain preserved for future reopening;
- Debian-only and mmdebstrap-only carriers should leave active owner, review, and delivery routing and may close without merge after their preservation boundary is explicit;
- technically reusable non-Debian findings may continue only after being separated from the Debian carrier that discovered them;
- util-linux, systemd, BuildKit, curl, kmod, jq, DuckDB, Nixpkgs, and other upstream-system work is not automatically retired merely because a Debian package was used as one control.

The old Linux last-mile push [linux-fieldwork#194](https://github.com/teamleaderleo/linux-fieldwork/issues/194) is closed `not planned` with its full history preserved. Linux Fieldwork PRs #399, #400, #402, #405, #408, #410, and #415 were closed without merge as parked packet/carrier history. PR #404's Debian wrapper was also closed after its util-linux result was separated into the active non-Debian map.

## Consolidation debt

Several families have too many simultaneously open surfaces:

1. **Playwright MCP shutdown** — route restriction, explicit capability, strict IPC, global stdin, and mode-aware stdin histories overlap. Preserve the comparisons, select one canonical current source, and close superseded carriers.
2. **MCP filesystem pathname authority** — the canonical finding, procfd primitive, platform matrices, and multiple stacked prototype PRs need one selected architecture and a compact successor map.
3. **Linux mmdebstrap** — many evidence, package, harness, tarfilter, and execution PRs remain open after owner deprioritization. Retain exact evidence, remove them from active routing, and close temporary carriers instead of continuing them.
4. **Fieldwork coordination protocol** — cockpit, typed state, lease, review routing, and protocol compositions contain valuable rules but should not delay a simple owner snapshot or ordinary technical servicing.
5. **uv self-update** — split finalizer, recovery, process-tree, and package-routing experiments into bounded conclusions before requesting owner attention.

## Current autonomous order

1. Keep #387 limited to the two current behavior decisions and process their replies.
2. Obtain eligible technical review for Gemini unit 16 through #213.
3. Finish exact bounded D1/D2 gates already near completion before opening more broad research.
4. Advance the Vite, Nixpkgs, Playwright-help, and Jotai packets to concise owner cards one at a time.
5. Consolidate overlapping Playwright MCP and MCP-filesystem histories.
6. Service the non-Debian Linux core: curl/Asio, systemd-oomd, kmod, fsck/udev, jq/systemd, util-linux, and DuckDB ART.
7. Park and close Debian/mmdebstrap-only routing surfaces while preserving branches, receipts, and reopening triggers.
8. Keep public upstream contact separately unauthorized unless the repository owner grants exact authority for one interaction.

## Authority

This snapshot does not authorize merge, release, deployment, spending, credentials, private-data access, or public upstream contact. It identifies what should be serviced and where a future owner decision may arise.
