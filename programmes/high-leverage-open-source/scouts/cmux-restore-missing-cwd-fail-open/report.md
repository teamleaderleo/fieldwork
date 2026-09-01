# cmux restore missing-CWD fail-open candidate

Date: 2026-09-01  
Programme: high-leverage-open-source  
Worker: ChatGPT  
Claim scope: interface  
Upstream contact authorized: `false`

## In simple words

cmux currently builds agent restore commands so that a saved working directory which no longer exists is treated as permission to launch the agent anyway. The agent then starts in whatever directory the terminal already happens to occupy.

That is a dangerous restore default. A restored agent can appear to come back successfully while operating in an unrelated repository or directory. The broader upstream incident already documents agents and ordinary terminals appearing under plausible tabs while their real CWD/TTY belonged elsewhere; this scout isolates one current-main mechanism that is much smaller and independently provable.

## Question

Can the current restore command builder be made to fail closed when a persisted agent working directory is unavailable, without regressing the shell-compatibility work that removed POSIX brace grouping?

## Assignment boundary

Expected deliverable: current-head overlap check, deterministic shell discriminator, exact source/test map, narrow owned-fork candidate if the lane remains free, fork CI, and recommendation.  
Owned output path: `programmes/high-leverage-open-source/scouts/cmux-restore-missing-cwd-fail-open/report.md`  
Dependencies: public cmux source/issues/PRs; owned `teamleaderleo/cmux` fork; GitHub-hosted macOS Actions for an eventual app-host test.  
Target revision: `manaflow-ai/cmux` `244adb38efdb8dea6fde624b079a0083738049d5`.  
Stop condition: the missing-directory behavior is reduced to a deterministic red/green discriminator and either an isolated candidate is executed on the owned fork or overlap/current-head evidence shows the lane should be left alone; upstream remains read-only.

## Upstream evidence

Primary incident: https://redirect.github.com/manaflow-ai/cmux/issues/8720

The issue documents a recurring restore integrity failure where ordinary terminal surfaces appeared under plausible workspace/tab names while their live foreground-process CWDs and TTY ownership belonged to unrelated surfaces. One audited restore had 27 terminals with confirmed wrong CWDs and 18 TTYs shared across multiple surfaces. A later reproduction reported 52 of 58 restored surfaces at the wrong directory and captured the generated resume command live from `ps`.

The same issue identified this command family:

```sh
cd -- '<saved-directory>' 2>/dev/null || [ ! -d '<saved-directory>' ] && <agent-command>
```

For POSIX AND-OR lists this is evaluated left-to-right as `(cd || test) && command`. When the saved directory is absent, `cd` fails, `[ ! -d ... ]` succeeds, and the agent command executes in the caller's existing CWD.

## Current-main source state

Pinned current main: `244adb38efdb8dea6fde624b079a0083738049d5`.

Production owner: `Sources/RestorableAgentSession.swift`, `TerminalStartupWorkingDirectoryPrefix.optionalChangeDirectoryPrefix(for:)`.

Current source deliberately emits:

```swift
return "cd -- \(quoted) 2>/dev/null || [ ! -d \(quoted) ] && "
```

The nearby comment explicitly records the left-associative semantics. The helper feeds agent resume/relaunch command construction through `TerminalStartupWorkingDirectoryPrefix.prefix(...)`.

A second copy of the same shell policy exists in `CLI/CMUXCLI+SessionsListForkStartupInput.swift` for session-list/fork startup input.

## Deterministic discriminator

A local shell control was executed against a guaranteed-missing path using the exact current-main logic:

```sh
/bin/sh -c "cd -- '/definitely/cmux-missing-dir' 2>/dev/null || [ ! -d '/definitely/cmux-missing-dir' ] && printf 'LAUNCHED:%s\n' \"\$PWD\""
```

Observed result:

```text
LAUNCHED:/tmp/<unrelated-current-directory>
```

This proves the narrow defect without launching cmux, an agent, or touching user data. The desired discriminator is equally crisp: with an unavailable persisted restore CWD, the agent payload must remain unexecuted and the shell command must return failure; with an existing persisted CWD, the payload must execute there.

## Overlap check

No PR directly claiming https://redirect.github.com/manaflow-ai/cmux/issues/8720 was found.

Two active restore-related PRs were inspected for overlap:

- https://redirect.github.com/manaflow-ai/cmux/pull/9855 changes working-directory trust and sanitization for remote restores and touches `RestorableAgentSession.swift`, but its patch leaves `optionalChangeDirectoryPrefix(for:)` and the missing-directory execute-anyway policy unchanged.
- https://redirect.github.com/manaflow-ai/cmux/pull/11312 centralizes Vault restore planning but does not change `RestorableAgentSession.swift` or this prefix helper.

This means the exact local missing-CWD fail-open slice is currently unclaimed, while a later rebase may need to account for the broader remote-CWD PR.

## Proofability / consequence

**Proofability: 5/5.** The behavior is one shell expression, current source emits it directly, the failure can be shown with a guaranteed-missing path, and the negative control is an existing temporary directory.

**Consequence: 5/5 at interface scope.** A restored coding agent can execute in an unrelated working directory while the restore path appears successful. The upstream incident documents this class reaching real agents and wrong repositories. This report does not claim that this single missing-directory branch explains the separate per-panel path-collapse or TTY-aliasing mechanisms in the full incident.

**Cross score: exceptional.** The dangerous outcome is large and the isolated proof is tiny.

## Candidate design

The smallest safe policy is to separate two concepts that current code combines:

1. optional placement, where a best-effort directory change may legitimately fall back;
2. persisted restore placement, where a recorded working directory is part of the restored execution identity and must fail closed when unavailable.

The candidate should preserve fish compatibility (the reason brace grouping was removed) while making the restore form equivalent to `cd <saved-dir> && <agent-command>` or another cross-supported form that cannot execute the payload after a failed `cd`.

Regression coverage should execute the rendered command with:

- an existing temporary directory: payload runs and reports that exact CWD;
- a missing directory: payload does not run and the command fails;
- a path containing spaces/shell-sensitive characters: quoting remains intact;
- the existing fish/no-brace expectation remains satisfied.

## Adjacent severe lanes checked

### Deep process-tree crash

https://redirect.github.com/manaflow-ai/cmux/issues/7848 remains severe and current source still contains the recursive process-tree walk, but the lane is already claimed by active fixes including https://redirect.github.com/manaflow-ai/cmux/pull/8802 and https://redirect.github.com/manaflow-ai/cmux/pull/10952. No duplicate implementation recommended.

### Launch rewrite drops socket password

https://redirect.github.com/manaflow-ai/cmux/issues/8372 is severe on release `0.64.22`: a reported relaunch stripped the saved socket password while preserving password mode and left 39 of 51 auto-resumed agent panes unable to authenticate. Current main has since added a dedicated password store plus plaintext-secret migration that saves the secret before scrubbing the JSON and leaves the original file intact if secret persistence fails. Treat the tracker issue as release evidence; current-main duplication is unwarranted without a fresh reproduction against `244adb38`.

## Evidence labels

- Wrong-CWD / shared-TTY restore incidents: **Documented** in the upstream issue.
- Current shell prefix and left-associative semantics: **Observed** on pinned current source.
- Missing-directory payload executes in unrelated current CWD: **Observed** by deterministic local shell execution.
- Exact local missing-CWD overlap status: **Observed** from current PR search and relevant PR patches.
- Claim that this one expression causes all path collapse or TTY cross-linking in the larger incident: **Unknown** and explicitly outside this scout's supported scope.
- Owned-fork red/green app-host execution: **Pending**.

## Recommendation

Promote this slice to an owned-fork candidate. It meets the high-consequence/high-proofability bar independently of the unresolved broader restore corruption report. Implement the fail-closed restore invariant, keep the diff narrow, exercise the rendered command directly plus the existing restore test seam, and carry any fork-only verifier outside the upstream-facing candidate diff. Keep upstream read-only until a fresh bounded greenlight.