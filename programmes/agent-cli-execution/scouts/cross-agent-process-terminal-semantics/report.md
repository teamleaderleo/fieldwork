# Cross-agent process and terminal semantics

State: `ready-for-synthesis`

Programme: `agent-cli-execution` (#14)

Targets:

- `google-gemini/gemini-cli@3499c84f7b8e70c86600e7cd2c67a7c65a667f5e`
- `openai/codex@3725f02cf38d856bc82bb46dd68ab61bb96ec6fc`

Fieldwork base: `teamleaderleo/fieldwork@09fe47ac92ec9c0c333b4979011f6321795deff2`

Claim scope supported: mechanism and interface

Upstream contact authorized: `false`

## In simple words

Gemini CLI and Codex each have more than one process contract. Both can run ordinary commands through pipes and interactive commands through a terminal-like transport, yet they preserve different information and use different completion rules.

Gemini CLI's pipe path folds stdout and stderr into one text stream in callback arrival order. Its PTY path feeds bytes into a headless terminal and emits rendered screen snapshots. Codex's one-shot path keeps stdout and stderr separate and tags live chunks by stream, while its final aggregate places retained stdout before retained stderr. Codex unified exec merges interactive output into one transcript and manages a resumable process session.

These differences are coherent product choices. They also create reusable failure boundaries: final output can disagree with live output, direct child exit can arrive before output closes, a result can settle before process-tree cleanup finishes, and a raw transcript can be mistaken for a rendered terminal screen.

The strongest campaign lead is Codex one-shot output drainage. Its source gives each pipe reader two seconds to finish after the process outcome. When that deadline expires, the reader task is aborted and an empty stream result is returned, which can discard bytes already retained by that reader even though live delta events already carried them. A target adapter should confirm the full tool behavior before a wider claim.

A second strong lead is Gemini CLI's explicit lifecycle kill route. The lifecycle service invokes the backend kill callback and then immediately resolves a synthetic aborted result. The backend process-group kill is asynchronous in the shell adapter. A target adapter should measure result settlement and process-tree death as separate events.

## Question and exclusions

Scout question: which process and terminal properties should remain stable across agent CLIs, where do Gemini CLI and Codex implement them differently, and which differences produce concrete risk or opportunity?

The comparison excludes model quality, wording, terminal styling preferences, approval-policy quality, and broad architectural replacement. It also excludes upstream contact, public issue filing, and target code changes.

## Method

1. Read Fieldwork coordination, evidence, experiment, testbed, and integration-context protocols.
2. Pin both targets before source analysis.
3. Trace process creation, output handling, cancellation, completion, background continuation, and terminal state through implementation and tests.
4. Build a neutral POSIX case pack independent of either target.
5. Separate documented source behavior, locally observed operating-system behavior, inference, and open questions.
6. Rank target-specific campaign branches under each repository's contribution rules.

No owned-repository testbed was selected. A local deterministic runner answered the mechanism questions with less unrelated code and fewer assumptions.

## Common vocabulary

The report uses these events as separate observations:

- **spawned** — a direct child or session handle exists;
- **stdout/stderr/PTY bytes** — bytes became readable at a declared observation point;
- **display snapshot** — terminal control sequences have been applied to a screen buffer;
- **direct process exited** — the immediate child reported an exit status;
- **output closed** — the relevant pipe or PTY output handle reached EOF or closure;
- **termination requested** — a signal or backend kill request was issued;
- **process tree gone** — the direct process and relevant descendants have exited;
- **result settled** — the caller received the final tool or lifecycle result.

A comparison that compresses these events into one word, “finished,” loses the boundary where many failures occur.

## Source and test map

### Gemini CLI

Implementation:

- `packages/core/src/services/shellExecutionService.ts`
- `packages/core/src/services/executionLifecycleService.ts`
- `packages/core/src/tools/shell.ts`
- `packages/core/src/utils/process-utils.ts`
- `packages/core/src/utils/getPty.ts`
- `packages/core/src/utils/terminalSerializer.ts`

Tests and adjacent coverage:

- `packages/core/src/services/shellExecutionService.test.ts`
- `packages/core/src/services/shellExecutionService.windows.integration.test.ts`
- `packages/core/src/tools/shell.test.ts`
- `packages/core/src/tools/shellBackgroundTools.test.ts`
- `packages/core/src/tools/shellBackgroundTools.integration.test.ts`
- `packages/cli/src/ui/hooks/useExecutionLifecycle.test.tsx`
- `packages/cli/src/ui/components/BackgroundTaskDisplay.test.tsx`

Contribution boundary:

- `CONTRIBUTING.md` requires an existing reviewed issue for a pull request, reserves self-assignment for eligible `help wanted` issues, and asks contributors to wait for maintainer feedback before coding. Any Gemini implementation campaign therefore requires a separate approval gate. [Documented]

### Codex

Implementation:

- `codex-rs/core/src/exec.rs`
- `codex-rs/core/src/unified_exec/mod.rs`
- `codex-rs/core/src/unified_exec/process.rs`
- `codex-rs/core/src/unified_exec/process_manager.rs`
- `codex-rs/core/src/unified_exec/async_watcher.rs`
- `codex-rs/utils/pty/src/lib.rs`
- `codex-rs/utils/pty/src/process.rs`

Tests and adjacent coverage:

- `codex-rs/core/src/exec_tests.rs`
- `codex-rs/core/src/unified_exec/process_tests.rs`
- `codex-rs/core/src/unified_exec/mod_tests.rs`
- `codex-rs/core/tests/suite/unified_exec.rs`
- `codex-rs/core/tests/suite/user_shell_cmd.rs`
- `codex-rs/utils/pty/src/tests.rs`

Contribution boundary:

- `docs/contributing.md` says external code contributions are invitation-only and unsolicited pull requests are closed without review. Fieldwork can retain analysis, reproductions, and candidate designs. Implementation remains gated by an explicit invitation and separate upstream authorization. [Documented]

## Neutral comparison

| Dimension | Gemini CLI pipe fallback | Gemini CLI PTY | Codex one-shot exec | Codex unified exec |
|---|---|---|---|---|
| Effective transport | independent stdout/stderr pipes; stdin ignored | PTY plus headless xterm buffer | independent stdout/stderr pipes | PTY or pipe-backed managed session, selected by `tty` |
| Child terminal identity | no TTY | TTY, configured dimensions, `TERM=xterm-256color` | no TTY in the one-shot shell path | managed terminal when `tty=true`; environment sets `TERM=dumb` and `NO_COLOR=1` |
| Live channel provenance | absent; both callbacks emit `data` text | one PTY stream rendered as screen snapshots | present through `ExecOutputStream::{Stdout,Stderr}` | local sources merge; protocol deltas are emitted as stdout |
| Cross-channel order | callback arrival order in one buffer | PTY delivery order | live observation order per emitted delta; final aggregate is stdout then stderr | merged receiver order in one transcript |
| Final representation | ANSI-stripped, trimmed text | terminal-buffer text plus optional ANSI token snapshot | separate stdout/stderr and aggregate | merged transcript in stdout; empty stderr on successful completion |
| Raw bytes | final `rawOutput` is empty in the traced shell paths | final `rawOutput` is empty | retained as bytes until final lossy UTF-8 conversion | retained in a head/tail byte buffer, then lossy conversion for final text |
| Output cap | 16 MiB tail retention in pipe path | scrollback and serialized-line limits | 1 MiB retained cap for shell calls; live event count cap | 1 MiB head/tail transcript cap and token formatting limits |
| Timeout basis | configured inactivity timeout at the shell-tool layer; resets on output events | same shell-tool inactivity rule | wall-clock timeout, default 10 seconds | yield deadlines and managed background-session limits |
| Cancellation | shell abort awaits process-group kill path; explicit lifecycle kill settles immediately after invoking backend kill | same distinction | group TERM on cancellation, 50 ms grace, then kill escalation; timeout and Ctrl+C have separate paths | distinct interrupt and terminate operations; process/session watcher coordinates exit and output drain |
| Completion boundary | Node `close` path after output handles close | PTY exit followed by queued terminal writes and final render | process outcome followed by up to two seconds per pipe reader | process exit token, trailing-output handling, output-drained notification, then end event |
| Background continuation | explicit background transition, session history, log, completion inject/notify/silent | same, with PTY input/resize/scroll | one-shot result | process ID, yield/poll/write input, later end event |
| Late observation | lifecycle subscriber receives current snapshot; recent exit cache lasts five minutes | rendered terminal snapshot | live delta stream plus final result | shared transcript for polling; remote exec-server path adds sequence recovery |

### Transport and terminal state

Gemini CLI explicitly tries a PTY when interactive execution is enabled and falls back to `child_process` when the outer PTY attempt throws. The PTY helper handles some errors internally, so fallback behavior depends on the failure path; `posix_spawnp failed` is rethrown for fallback, while other caught PTY errors can return an execution failure with method `none`. [Documented]

Gemini's PTY is also a terminal renderer. Output bytes are decoded, written into an xterm headless terminal, serialized, and emitted as a screen snapshot on a throttled cadence. Carriage returns, erase commands, wrapping, cursor location, resizing, and scrollback all influence that snapshot. [Documented]

Codex unified exec can open a managed process with `tty=true` and exposes input, interrupt, termination, and resize through its PTY utility. Its default unified-exec environment sets `TERM=dumb`, disables color, normalizes locale to UTF-8, and disables pagers. This chooses a transcript-friendly child environment while retaining interactive transport capabilities. [Documented]

These are different contracts. Gemini asks, “what does the terminal screen currently display?” Codex unified exec asks, “what bytes entered the managed transcript?” A cross-agent regression oracle needs both fields when a case contains carriage returns or ANSI control sequences. [Inferred]

### stdout, stderr, and ordering

Gemini's pipe fallback maintains separate UTF-8 decoders for stdout and stderr, yet both feed one `state.output` and one untagged `data` event type. The resulting order reflects callback delivery. The final consumer cannot recover channel provenance. [Documented]

Codex one-shot exec reads the channels concurrently, emits stream-tagged live deltas, retains each channel separately, and constructs the final aggregate from retained stdout followed by retained stderr. Under output-cap contention, the aggregate reserves space across the two channels. The final aggregate therefore serves as a two-channel summary, rather than a replay of live interleaving. [Documented]

Codex unified exec combines local stdout and stderr receivers through `tokio::select!` into one broadcast stream. The async watcher emits those merged chunks with the protocol stream field set to stdout, and successful final output contains the merged transcript in stdout with empty stderr. [Documented]

A useful shared rule follows: per-channel order can be asserted for pipe transports. Cross-channel order needs a named observation point, such as child instrumentation, kernel pipe readiness, callback delivery, or protocol event delivery. [Inferred]

### Completion and trailing output

The neutral inherited-pipe cases demonstrate that direct child exit and output closure can be separated by a descendant holding the inherited file descriptor. On the retained Linux run, a 350 ms descendant hold produced a 346.807 ms gap, and a 2.25 second hold produced a 2247.620 ms gap. [Observed]

Gemini's child-process result is finalized from the Node `close` handler, so its normal completion follows output-handle closure. Its shell-tool timeout is based on inactivity and resets on output events. A quiet inherited descriptor can therefore delay completion until the configured inactivity timeout causes cancellation. A descendant that keeps producing output can extend the run. [Documented, Inferred]

Codex one-shot explicitly bounds post-outcome pipe drainage at two seconds. This avoids an unbounded hang when descendants inherit output descriptors. The current `await_output` timeout branch aborts the reader task and returns a new empty stream value. Bytes already accumulated inside that task are then absent from the final stream, even when live deltas already exposed them. [Documented]

Codex unified exec uses another contract. Its streaming watcher starts a 100 ms trailing-output grace after process exit, performs a final drain when the output producer has closed, and notifies the exit watcher only after output drainage. Polling/yield collection also has a 50 ms post-exit close-wait cap. [Documented]

These choices trade unbounded waiting, retained output, and prompt completion differently. The reusable invariant is narrower: a bounded drain should retain bytes already read, report incomplete output, and distinguish direct exit from output closure. [Inferred]

### Cancellation and process trees

Both targets include process-group cleanup. The visible timing differs.

Gemini's shell abort handler awaits `killProcessGroup` with escalation before the ordinary close path produces the final shell result. Its separate `ExecutionLifecycleService.kill` method invokes the registered backend kill callback and immediately settles a synthetic aborted result with exit code 130. The shell callback starts an asynchronous group kill. This explicit lifecycle route can report settlement before operating-system cleanup has completed. [Documented, Inferred]

Codex one-shot cancellation sends a group termination request, waits 50 ms for the child, and escalates to group kill when needed. Timeout and process-level Ctrl+C use distinct synthetic status paths. [Documented]

Codex unified exec separates interrupt from terminate. Interrupt forwards a terminal/process interrupt signal. Terminate kills the child and aborts helper tasks. Dropping a process handle also terminates it. [Documented]

The neutral cancellation case gives a parent and descendant TERM handlers longer than the runner's 100 ms grace. The runner escalated to SIGKILL, returned exit code `-9`, and found the descendant gone. Cleanup text from the TERM handlers was absent because escalation cut the handlers short. [Observed]

The reusable test therefore records five outputs: requested signal, grace duration, escalation, final bytes, and descendant survival. A single exit code cannot describe the whole cancellation result. [Inferred]

### Background and resumable sessions

Gemini backgrounding resolves the original execution promise with `backgrounded: true`, leaves the process registered, creates a session-scoped history record and log, and later supports completion behavior of inject, notify, or silent. The PTY path keeps input, resize, scroll, and rendered snapshots available. [Documented]

Codex unified exec yields a process ID when a command remains active, stores the managed process, accepts later input or polling, and emits a final end event after process and output completion. It caps the process store and can prune old entries. [Documented]

Both expose a continuation after the initiating tool call returns. Their public state machines use different names and representations. A shared case should ask whether the process remains controllable, whether output remains recoverable, and what event closes the continuation. [Inferred]

### Bytes, text, and binary output

The neutral invalid-UTF-8 child emits two invalid bytes between valid text. The baseline retains the original bytes in base64 and shows two replacement characters in its lossy text view. [Observed]

Gemini shell execution detects probable binary output during an initial sniff window and switches to binary progress events. Its traced final `rawOutput` fields are empty, so the shell result does not preserve the original byte sequence. [Documented]

Codex one-shot retains bytes separately and converts final streams with lossy UTF-8. Codex unified exec splits live chunks on UTF-8 boundaries where possible; when no valid prefix exists, it emits one byte to keep the stream moving, and final transcript conversion is lossy. [Documented]

Reusable adapters should record raw bytes, text decoding policy, binary classification, and live-event payload rules separately. [Inferred]

### Local and remote execution

Codex unified exec has a local managed-process path and an exec-server-backed path. The remote path attaches sequence numbers to output and repairs gaps by reading from the last known sequence. The local path uses broadcast channels and skips lagged receiver errors. Its retained head/tail buffer remains a separate source for final and polled output. [Documented]

The comparison found no equivalent shell-level remote path in the Gemini files traced for this scout. `ExecutionMethod` includes `remote_agent`, but the analyzed shell service covers local PTY and child-process execution. [Documented]

A future Codex campaign can compare local and remote event continuity under a deliberately slow consumer. Any ecosystem claim stays provisional until both adapters run. [Inferred]

## Runnable case pack

Durable artifacts:

- `artifacts/run_process_terminal_cases.py`
- `artifacts/case-pack.json`
- `artifacts/results-linux-python-3.13.5.json`
- `artifacts/README.md`

Run:

```bash
python3 artifacts/run_process_terminal_cases.py --pretty
```

Retained environment:

- Linux `6.12.13`, x86_64, glibc `2.41`
- Python `3.13.5`
- no network access

Retained observations:

| Case | Observation |
|---|---|
| pipe interleave | live channel sequence was stdout, stderr, stdout, stderr; per-channel content stayed ordered |
| PTY interleave | all bytes arrived through one PTY stream; line endings became CRLF |
| pipe identity | stdin, stdout, and stderr reported no TTY; no terminal size was available |
| PTY identity | all three descriptors reported TTY; configured size was 72 columns × 19 rows |
| inherited pipe, 350 ms | output EOF followed direct child exit by 346.807 ms |
| inherited pipe, 2.25 s | output EOF followed direct child exit by 2247.620 ms |
| invalid UTF-8 | raw bytes were retained in base64; lossy text used replacement characters |
| final marker | `FINAL-MARKER` appeared in final stdout |
| cancellation | TERM was followed by SIGKILL after 100 ms; direct process and descendant exited |

The baseline is an operating-system reference. It is not an expected byte-for-byte target result because each target intentionally transforms transport, terminal state, and final output.

## Reusable failure cases

1. **Live/final disagreement** — live chunks preserve one order or content set while the final aggregate reorders, truncates, or loses retained bytes.
2. **Direct exit before output closure** — descendants keep output handles open after the immediate child exits.
3. **Result settlement before tree cleanup** — lifecycle result resolves while an asynchronous group kill continues.
4. **PTY requested, pipe delivered** — fallback changes TTY identity, stdin behavior, output provenance, and control-sequence handling.
5. **Raw transcript treated as screen state** — carriage returns and erase sequences produce different visible output than append-only text.
6. **Merged output mislabeled as stdout** — source channels merge before a protocol field identifies the chunk as stdout.
7. **Bounded drain drops retained bytes** — timeout protection avoids a hang while erasing bytes already read.
8. **Cancellation grace hides cleanup output** — escalation interrupts signal handlers and removes expected final diagnostics.
9. **Invalid UTF-8 loses byte identity** — lossy text remains readable while exact bytes disappear.
10. **Slow consumer misses live events** — broadcast lag drops event chunks even when the final retained buffer remains usable.
11. **Background completion disappears across session boundaries** — the initiating turn returns while later output, control, and completion depend on process-store lifetime.
12. **Resize or terminal identity races with exit** — resize, input, or active checks run while the process is closing.

## Ranked campaign opportunities

### 1. Shared target-adapter event trace

Build thin Fieldwork adapters that translate each target into a shared trace vocabulary while preserving target-native fields. Run the existing case pack against Gemini pipe, Gemini PTY, Codex one-shot, and Codex unified exec.

Success evidence:

- exact target revision and command;
- raw target events;
- normalized events with explicit observation point;
- final result and process-tree state;
- differences classified as intended, unsupported, or failure candidates.

This is the best next campaign because it turns source-level differences into repeatable target evidence without presuming a preferred design.

### 2. Codex one-shot inherited-pipe retention

Create a target-specific test where a descendant holds stdout open longer than two seconds after the direct child exits, while the direct child emits an early marker.

Question: does the final tool result retain bytes read before the drain deadline, and does it identify output incompleteness?

Candidate branch stays in Fieldwork until the Codex team explicitly invites a contribution. [Source-supported lead]

### 3. Gemini lifecycle kill settlement

Drive `ShellExecutionService.kill` or the user path that reaches it with a TERM-aware parent and descendant. Measure backend kill request, result settlement, direct exit, descendant exit, and final output.

Question: does the public lifecycle promise mean “termination requested” or “process tree settled,” and does the UI/model receive enough information to distinguish them?

Candidate implementation work requires an approved Gemini issue and separate upstream authorization. [Source-supported lead]

### 4. Live/final transcript consistency

For each execution mode, declare whether the final aggregate is a replay, rendered screen, channel summary, or head/tail digest. Add assertions that match that declared role.

Focus cases:

- interleaved stdout/stderr;
- final marker immediately before exit;
- output-cap contention;
- binary and invalid UTF-8;
- cancellation during output.

### 5. Effective transport disclosure

Test requested PTY, effective PTY, fallback to pipes, and spawn failure. Preserve `executionMethod` or equivalent, TTY identity, and terminal dimensions in the trace.

Gemini has the clearest lead because its PTY helper contains multiple error paths with different fallback outcomes. Codex can use the same case for local, Windows, and remote backends.

### 6. Codex unified local/remote continuity

Feed output faster than a live consumer reads it. Compare local broadcast lag behavior with remote sequence-gap repair, and compare both live streams with final retained output.

This campaign supports an interface claim only. Operational consequence needs a realistic client and separate integration context.

### 7. Background/session closeout

Start a command, return from the initiating call, then exercise input, resize, polling, cancellation, natural exit, application shutdown, and process-store pruning.

Compare the lifecycle questions shared by both products while preserving their different background models.

### 8. Cross-platform terminal matrix

Run terminal identity, Unicode, resize, signal, and fallback cases on Linux, macOS, and Windows/ConPTY. Pin shell, locale, runtime, terminal dimensions, and target revision.

The current Linux run supplies a case definition, not cross-platform evidence.

## Negative results and stopped paths

- UI wording and styling produced no correctness claim and were excluded.
- Model-generated command choice was excluded because it would add nondeterminism to process evidence.
- A universal expected final string failed as a useful oracle: rendered-screen, raw-transcript, merged-stream, and split-stream contracts intentionally differ.
- Cross-stream program order cannot be reconstructed from independent pipes without child instrumentation or a declared observer.
- An owned integration testbed added no evidence for the first pass; the local runner preserved the relevant process boundaries directly.
- End-to-end target builds were not available through the connected repository interface. This report therefore keeps implementation observations source-level and retains target adapter runs as the next campaign.
- Windows and remote behavior remain source-level because the retained runner executed on Linux only.
- No upstream issues, comments, pull requests, discussions, emails, or other contacts were created.

## Uncertainty and alternative interpretations

- Gemini's configured inactivity timeout value varies by configuration; this report compares timeout basis, not a fixed duration.
- Gemini's ordinary abort path and explicit lifecycle kill path settle at different points. A target adapter must identify which user actions reach each route.
- Codex one-shot reader-timeout output loss is directly visible in the helper function. Full tool behavior still needs a pinned end-to-end reproduction, including live protocol events and final result formatting.
- Codex unified exec supports both `tty=true` and `tty=false`; terminal claims apply to the effective mode recorded by the adapter.
- Broadcast lag in Codex local unified exec can affect a live subscriber while the retained buffer remains complete within its head/tail cap. The user-visible consequence depends on the consuming surface.
- Terminal emulators can transform bytes according to terminal mode and platform. The neutral PTY baseline captures one POSIX environment.

## Recommendation

Accept this scout as `ready-for-synthesis` at mechanism/interface scope. Open the shared target-adapter campaign first. Promote the Codex inherited-pipe retention case and Gemini lifecycle-kill settlement case as independent target lanes after the adapters reproduce them at the pinned revisions.

Keep upstream contact unauthorized. Gemini implementation requires a reviewed issue and maintainer direction; Codex implementation requires an explicit invitation. Fieldwork can continue producing source maps, adapters, case results, and candidate designs without crossing either boundary.

## Evidence register

| Claim | Label | Primary source or artifact | Limitation |
|---|---|---|---|
| Gemini pipe merges decoded stdout/stderr into one untagged output buffer | Documented | `google-gemini/gemini-cli@3499c84...:packages/core/src/services/shellExecutionService.ts` | source-level |
| Gemini PTY emits serialized terminal snapshots | Documented | same file plus `terminalSerializer.ts` | UI consumption beyond traced call remains outside scope |
| Gemini lifecycle kill settles synthetic abort after invoking backend kill | Documented | `...:packages/core/src/services/executionLifecycleService.ts` | user-route mapping needs adapter |
| Gemini timeout is inactivity-based at shell-tool layer | Documented | `...:packages/core/src/tools/shell.ts` | configured duration omitted |
| Codex one-shot live deltas retain stream tags | Documented | `openai/codex@3725f02...:codex-rs/core/src/exec.rs` | final consumer can reformat |
| Codex final aggregate is stdout followed by stderr | Documented | same file | represents summary, not live replay |
| Codex drain timeout aborts reader and returns empty stream | Documented | same file | end-to-end result needs adapter |
| Codex unified exec merges local output into one transcript | Documented | `...:codex-rs/core/src/unified_exec/process.rs`, `async_watcher.rs` | remote path differs |
| Direct exit and output EOF can differ by descendant hold time | Observed | `artifacts/results-linux-python-3.13.5.json` | Linux/Python baseline |
| Cancellation grace can suppress cleanup output | Observed | same artifact | one 100 ms grace case |
| Shared event vocabulary will reduce ambiguous comparisons | Inferred | source comparison plus case pack | value needs campaign use |
| Codex one-shot may show live bytes absent from final result under long inherited pipes | Inferred from documented mechanism | `exec.rs` plus inherited-pipe baseline | target adapter required |
| Gemini explicit lifecycle kill may settle before tree cleanup | Inferred from documented mechanism | lifecycle service and shell adapter | target adapter required |
