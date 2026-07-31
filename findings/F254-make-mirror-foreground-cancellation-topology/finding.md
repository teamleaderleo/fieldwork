# F254-make-mirror-foreground-cancellation-topology: prompt PID-only cancellation is not justified yet

Finding state: `stopped`

Workstream: `G`  
Canonical Fieldwork issue: `#254`  
Canonical finding path: `findings/F254-make-mirror-foreground-cancellation-topology/finding.md`  
Canonical implementation: `none`; retained Linux Fieldwork research PR `#264`  
Exact implementation or evidence head: `4e9deb179eb8a175d3108affa5a907eb22af9c07`  
Exact base or source revision: stacked on worker carrier `d270f558fa7c32569ea380fd614c34edaf60b3b3`; imported `make_mirror.sh` blob `6c4be092edcf23b56b63a3befe238c099c45f590`  
Strongest evidence class: `model-executed`  
Reviewed input generation: current Fieldwork/Linux protocols; merged #224; worker #231/#267; Linux #263/#264 complete ten-file research fence  
Current review disposition: `HOLD` source expansion  
Desk routing: `not-entered`; durable stopped finding  
Upstream contact authorized: `no`

## In simple words

The accepted `make_mirror.sh` repairs eventually report cancellation correctly and clean the right state. A signal sent only to the top-level shell or only to the `update_cache()` worker can still wait while an unowned foreground command finishes.

The investigation compared ways to make every such cancellation prompt. A technically complete source repair is possible, but it is not a small change: the parent must own each pipeline worker, the worker must own simple and fallback commands, and a separate mechanism must own every stage of output-capturing pipelines.

That machinery adds process-group or supervisor dependencies for a latency path whose frequency and real impact have not been measured. The investigation therefore stops without a source patch. The accepted #224/#267 lifecycle remains the current answer.

## Why we care

A long APT command may continue after a PID-only stop request even though the final status is eventually 143. Parent-only delivery can also allow later worker commands to run before the top-level trap executes.

This is an operational latency issue. It is separate from the correctness defects already addressed by the accepted lifecycle work: false success, duplicate cleanup, cross-owner proxy termination, leaked proxy state, and continuation after the worker trap itself runs.

## What happens if we leave it alone

Under selected PID-only delivery topologies:

- worker-only TERM can remain pending until a foreground child returns;
- owner-only TERM can remain pending until the complete pipeline worker returns;
- the eventual result and cleanup remain correct under the accepted candidates;
- actual delay depends on the foreground command and caller topology.

The repository currently documents direct `./make_mirror.sh` invocation and does not guarantee an isolated caller process group.

## Current finding

Do not add broad prompt-cancellation machinery without evidence that the remaining delay is materially harmful or an explicit contract that makes process-group supervision supported.

Retain the comparative evidence and reopen only on named triggers.

### Claim table

| Claim | Evidence class | Exact support | Limit |
| --- | --- | --- | --- |
| Worker-only TERM can remain pending behind a foreground child, then finish 143 without worker later work. | `model-executed` | topology matrix in Linux PR #264 | Held synthetic child, no APT |
| Owner-only TERM can remain pending through the worker and permit worker later work before final 143. | `model-executed` | topology matrix | Reduced owner/worker chain |
| Isolated process-group TERM is prompt. | `model-executed` | topology matrix | Requires safe isolated group |
| Background one-line and heredoc pipelines expose the final worker PID through `$!` and preserve input/status. | `model-executed` | parent pipeline identity matrix | Target `/bin/sh` model |
| Tracking only the final PID of an internal pipeline is insufficient. | `model-executed` | output-pipeline negative control | Three-stage held pipeline |
| Isolated groups preserve tested output, final-stage status, partial-output rejection, cancellation, and rerun contracts. | `model-executed` | output-capture contract | Requires `setsid` and group-aware kill |
| Fallback ownership can preserve ordinary/fallback results and distinguish cancellation. | `model-executed` | seven-case fallback matrix | Reduced commands, no APT |
| Broad source expansion is proportionate to demonstrated impact. | `none` | no measured real latency evidence | This absence supports stopping, not a performance claim |

## System and ownership map

- Top-level owner: `make_mirror.sh`, proxy PID, cache publication, top-level result.
- Pipeline worker: parenthesized `update_cache()`, worker APT root and worker result.
- Foreground descendants: APT commands, fallback attempts, filters, and output-capturing pipelines.
- Current accepted propagation: worker nonzero result reaches top-level `set -e`; parent cleanup retires proxy.
- Promptness gap: neither accepted repair tracks every active worker/descendant PID or process group.
- Caller boundary: direct invocation is documented; safe group isolation is not.

## Historical precedent

### Top-level proxy lifecycle

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/224
- Revision: merge `386f5c8dbb01e5de1af45ac0eb325ee8567722e3`
- Principle supported: child and cleanup resources require one owner; signal cleanup must terminate.
- Important difference: this finding asks whether cancellation must be prompt through all descendant layers.

### Worker-local cleanup ownership

- Source: https://github.com/teamleaderleo/linux-fieldwork/pull/267
- Revision: `c066db4046626cbed0b1c186cb52b9dffa72554a`
- Principle supported: the worker owns APT state and result, not the parent proxy.
- Important difference: the focused repair guarantees eventual result/cleanup, not prompt foreground-child interruption.

## Approaches considered

### Declined as repository answer: rely on caller process groups

Group delivery is prompt in the model, but the repository does not guarantee that direct invocations run in a safe isolated group. It remains operational guidance for controlled wrappers, not a source contract.

### Rejected as incomplete: worker owns only foreground child

This makes worker-only delivery prompt but leaves owner-only delivery deferred and does not own the output pipeline.

### Rejected by execution: track final pipeline PID only

Killing the final stage leaves upstream stages alive and the shell waiting on the pipeline job.

### Technically viable but not retained: internal isolated process groups

This covers full pipelines and preserves tested semantics, but requires several ownership primitives, first-signal/registration logic at multiple levels, and `setsid`/group-aware kill dependencies not explicitly declared in the primary test dependency block.

### Not justified: dedicated all-stage supervisor

A Python or other helper could make ownership explicit, but it adds a source, packaging, and API surface. No measured impact currently justifies that expansion.

### Selected: retain eventual correctness and stop

The accepted lifecycle repairs remove the demonstrated correctness failures. The remaining unmeasured latency path does not justify the broader mechanism now.

## Edge cases covered

| Case | Evidence | Result |
| --- | --- | --- |
| Worker-only TERM while child held | topology matrix | pending until release; final 143; no worker later work |
| Owner-only TERM while child held | topology matrix | pending until release; worker later work; final 143 |
| Isolated group TERM | topology matrix | prompt 143; no later work |
| Worker-child ownership | topology matrix | worker-only prompt |
| Composed parent-worker/worker-child ownership | topology matrix | owner-only prompt |
| One-line background worker pipeline | identity matrix | final PID/input/status preserved |
| Heredoc background worker pipeline | identity matrix | final PID/input/status preserved |
| Final-stage-only output ownership | negative matrix | upstream survives; wait blocks |
| Isolated output group | output contract | all stages stop; partial capture rejected |
| Fallback ordinary and signal paths | seven-case fallback matrix | result precedence preserved; cancellation omits fallback |

## Edge cases deferred or outside scope

| Edge case | Why outside scope | Reopening trigger |
| --- | --- | --- |
| Real APT latency distribution | no real workload executed | measured harmful delay |
| Full mirror/QEMU/network execution | high-cost integration | contradictory or deployment evidence |
| Group-tool availability across hosts | dependency contract absent | explicit dependency acceptance |
| Competing first signals and registration windows in proposed supervisors | no implementation selected | implementation becomes justified |
| Timeout and TERM-to-KILL escalation | separate policy | uncooperative real child evidence |

## Exact execution and receipts

| Repository/head | Command or workflow | Result | Evidence class |
| --- | --- | --- | --- |
| Linux PR #264 retained local records | topology/source matrix | 6 controls passed | `model-executed` |
| same | parent pipeline identity | 2 controls passed | `model-executed` |
| same | output ownership negative/group | 2 controls passed | `model-executed` |
| same | output-capture contract | 4 controls passed | `model-executed` |
| same | fallback ownership/precedence/cancellation | 7 controls passed | `model-executed` |
| `linux-fieldwork#264@4e9deb17…` | exact-head review `4824675356` | STOP / HOLD source expansion | `source-read` |

Total retained local controls: 21.

A fresh assistant-container rerun could not begin because the container could not resolve GitHub. This is a retrieval/setup failure, not contradictory product evidence. Hosted exact-head CI remains additive validation.

## Complete-diff and compatibility review

- Complete fence: five investigation records and five executable matrices.
- No retained product patch is included.
- Concurrent output-capture and fallback work was reconciled into the stopped conclusion.
- The exact review confirms that final-PID-only ownership is disproved and isolated groups are technically viable but disproportionate without impact/dependency evidence.
- The stopped result does not demote or block the focused #267 worker repair.

## Current disposition and desk routing

- Finding state: `stopped`
- Review disposition: `HOLD` source expansion
- Review Queue entry: none required; stopped result retained in Linux PR #264
- Delivery lane: `not-entered`
- Exact next transition: none
- Clearing condition: none
- Required subgates: none
- User decision requested: none

## Reopening triggers

Reopen only when at least one occurs:

1. a real or faithful APT workload demonstrates materially harmful PID-only cancellation latency;
2. a supported caller or supervisor contract guarantees a safe isolated group;
3. the project explicitly accepts required group-management dependencies;
4. another change already introduces an all-stage supervisor and lowers marginal complexity;
5. contradictory evidence appears against the accepted #224/#267 lifecycle.

## Changes to the canonical conclusion

| Date | Record | Change |
| --- | --- | --- |
| 2026-07-31 | Linux #263 / early PR #264 | Began comparative evaluation of caller groups and explicit ownership chains |
| 2026-07-31 | output/fallback matrices | Disproved final-PID-only ownership and proved isolated-group feasibility/semantic cost |
| 2026-07-31 | PR #264 `4e9deb17…` | Stopped source expansion with 21 retained controls and explicit reopening triggers |

## References

- https://github.com/teamleaderleo/linux-fieldwork/issues/263
- https://github.com/teamleaderleo/linux-fieldwork/pull/264
- https://github.com/teamleaderleo/linux-fieldwork/pull/224
- https://github.com/teamleaderleo/linux-fieldwork/pull/267
- https://github.com/teamleaderleo/linux-fieldwork/issues/231
- https://github.com/teamleaderleo/fieldwork/issues/254
